# Import necessary libraries
import streamlit as st
import json
import openai
import requests
import os
from rspace_client.eln import eln
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
from open_ai_functions import pretty_print_conversation2, chat_completion_request

GPT_MODEL = "gpt-4"
eln_cli = eln.ELNClient(os.getenv("RSPACE_URL"), os.getenv("RSPACE_API_KEY"))
print(eln_cli.get_status())


def search_rspace_eln(luceneQuery, sort_order="lastModified desc"):
    q = "l: " + luceneQuery
    docs = eln_cli.get_documents(query=q, order_by=sort_order)["documents"]
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
    resp = chat_completion_request(messages, functions, {"name": "lucene"})
    active_messages = messages.copy()
    response_message = resp.json()["choices"][0]["message"]
    active_messages.append(response_message)

    if response_message["function_call"] is not None:
        f_name = response_message["function_call"]["name"]
        f_args = json.loads(response_message["function_call"]["arguments"])
        rspace_search_result = available_functions[f_name](**f_args)
    return (active_messages, rspace_search_result)


# Main function for Streamlit app
def main():
    ##unsafe_allow_html(bool)

    # Create text area with label 'Input data'
    user_input = st.text_area("Input data", "")

    # Create a button with label 'submit'
    if st.button("Search for content in RSpace in your own words"):
        result = process(user_input)  # Process the input using the process method
        st.text_area(
            "Output", key="output_area", height=800, value=result, disabled=True
        )  # Displa

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
    (conversation, results) = do_conversation(messages, functions)

    print("-----------------------------------")

    conversation = pretty_print_conversation2(conversation)
    conversation = "\n".join(conversation)
    conversation += json.dumps(results, indent=2)
    return conversation


if __name__ == "__main__":
    main()
