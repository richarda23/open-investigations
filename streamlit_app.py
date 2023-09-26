# Import necessary libraries
import streamlit as st
import json
import openai
import requests
import os
    from rspace_client.eln import eln
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
from jupyter_notebooks.open_ai_functions import (
    pretty_print_conversation2,
    chat_completion_request,
)

GPT_MODEL = "gpt-4"

def search_rspace_eln(luceneQuery, sort_order="lastModified desc"):
    q = "l: " + luceneQuery
    docs = st.session_state.eln_cli.get_documents(query=q, order_by=sort_order)[
        "documents"
    ]
    wanted_keys = ["globalId", "name", "tags", "created"]  # The keys we want
    summarised = list(
        map(lambda d: dict((k, d[k]) for k in wanted_keys if k in d), docs)
    )
    return summarised


available_functions = {"lucene": search_rspace_eln}

functions = [
    {
        "name": "lucene",
        "description": """
    A valid Lucene Query Language string generated from user input.
    Document fields are name, docTag, fields.fieldData, and username.
    Don't use wildcards.
    """,
        "parameters": {
            "type": "object",
            "properties": {
                "luceneQuery": {
                    "type": "string",
                    "description": "Valid Lucene Query Language as plain text",
                },
                "sort_order": {
                    "type": "string",
                    "description": "How results should be sorted",
                    "enum": ["name asc", "name desc", "created asc", "created desc"],
                },
            },
        },
    }
]


def do_conversation(messages, functions):
    resp = chat_completion_request(
        messages,
        functions,
        function_call={"name": "lucene"},
        key=st.secrets.OPENAI_API_KEY,
    )
    active_messages = messages.copy()
    response_message = resp.json()["choices"][0]["message"]
    active_messages.append(response_message)

    if response_message["function_call"] is not None:
        f_name = response_message["function_call"]["name"]
        f_args = json.loads(response_message["function_call"]["arguments"])
        rspace_search_result = available_functions[f_name](**f_args)
    return (active_messages, rspace_search_result)


def card(item):
    return f"""
    <div style="border: 1px solid #ccc; border-radius: 5px; padding: 20px; width: 300px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); position: relative;">
    <div style="font-size: 20px; font-weight: bold;">Card Title</div>
    <div style="position: absolute; bottom: 20px; width: 100%; display: flex; justify-content: space-between;">
        <span style="font-size: 14px;">20/09/2023</span>
        <span style="font-size: 14px;">Additional Info</span>
    </div>
</div>
"""


def form_callback():
    st.session_state.eln_cli = eln.ELNClient(
        st.session_state.rspace_url, st.session_state.rspace_apikey
    )
    st.sidebar.write(st.session_state.eln_cli.get_status())


# Main function for Streamlit app
def main():
    st.set_page_config(page_title="RSpace query with GPT")

    # Create text area with label 'Input data'
    with st.sidebar:
        with st.form(key="my_form"):
            apikey = st.text_input(
                "Your RSpace API key", key="rspace_apikey", type="password"
            )
            url = st.text_input(
                "Your RSpace URL",
                key="rspace_url",
                placeholder="https://community.researchspace.com",
            )
            submit_button = st.form_submit_button(
                label="Submit", on_click=form_callback
            )
    user_input = st.text_area(
        "Set up your RSpace URL and key, then enter a search query  for RSpace in your own words",
        "",
    )

    with st.expander("Examples"):
        st.write(
            """
            - tagged with polyclonal
            - tagged with polyclonal and PCR but not ECL newest first
            - tagged with polyclonal and ECL but not PCR sort alpha 
            - with 'dna polymerase' in the text
        """
        )

    if st.button("Search"):
        with st.spinner("searching..."):
            (conversation, results) = process(
                user_input
            )  # Process the input using the process method

            conversation = pretty_print_conversation2(conversation)
            st.subheader("Conversation history")
            c = '<div style ="border: 2px solid blue; padding:1em;">'
            for m in conversation:
                c += f'<p style="color:{m["c"]}">{m["m"]}</p>'
            c += "</div>"
            st.markdown(c, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
            # conversation = "\n".join(conversation)
            jsonout = json.dumps(results, indent=2)
            st.subheader("Search results")
            st.text_area("", key="output_area", height=800, value=jsonout)

    # Create a button with label 'Clear Input'
    if st.button("Clear Input"):
        # Clear the text area
        st.experimental_rerun()  # Rerun the app to clear the text area
        st.text_area(
            "Output", key="output_area", height=800, value="", disabled=True
        )  # Displa


def process(data):
    # Placeholder for processing logic. In this example, just return the data with a prefix.
    # Modify this method as per your specific processing requirements.
    messages = [
        {"role": "system", "content": "Extract user input into structured data"}
    ]
    messages.append({"role": "user", "content": data})
    return do_conversation(messages, functions)


if __name__ == "__main__":
    main()
