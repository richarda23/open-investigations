# Import necessary libraries
import collections
import re

import streamlit as st
from langchain.schema import Document
from rspace_client.eln import eln
from jupyter_notebooks.rspace_loader import RSpaceLoader;
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
import textwrap
from typing import List
from callback_handlers import MyStreamLitHandler


def show_help():
    st.write('## Instructions')
    st.write("First of all set up your RSpace key and URL. These will persist as long as you don't refresh the page.")
    st.write("Now enter a folder or notebook ID. Up to 20 documents will be uploaded. This is not recursive - only top"
             "level documents are uploaded")
    st.write("Once the docs are loaded, they will be sent to the LLM (OpenAI's gpt-3.5-turbo) for summarising. You "
             "can follow progress in the Logs tab.")
    st.write("In general, one new 'chain' is started per document. ")
    st.write("Depending on length of the docs, this might take some time. Documents are summarised recursively.")
    st.write("No content is created or altered  in your RSpace account - data is only read.")


def run_summary(docs: List[Document], handler) -> str:
    chat_llm = ChatOpenAI(temperature=0.0)
    prompt = """
       Write a concise summary of the input text. Tell jokes as well. 
       Use bullet points and terse sentences. 
    
        Extract a maximum of 10 keywords and list these at the end in a section called 'Keywords'.
    
        The text:
    
        {text}
    
        Your summary:
    
        Your keywords (maximum 10):
        """
    prompt_t = PromptTemplate(input_variables=['text'], template=prompt)

    chain = load_summarize_chain(llm=chat_llm, verbose=True, chain_type="map_reduce", map_prompt=prompt_t)
    output_summary = chain.run(docs, callbacks=[handler])
    wrapped_text = textwrap.fill(output_summary, width=60)
    return wrapped_text


def form_callback():
    st.session_state.eln_cli = eln.ELNClient(
        st.session_state.rspace_url, st.session_state.rspace_apikey
    )
    st.sidebar.write(st.session_state.eln_cli.get_status())


# Main function for Streamlit app
def main():
    st.set_page_config(page_title="RSpace summarise content")

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

    importer_tab, logger_tab, help_tab = st.tabs(["Import Docs & summarise", "Logs", "Instructions"])
    imported_rspace_docs = []
    if 'loaded_docs' not in st.session_state:
        st.session_state.loaded_docs = []
    with logger_tab:
        log_ct = st.container()
    with help_tab:
        show_help()

    with importer_tab:
        folder_to_import = st.text_input(
            "Set up your RSpace URL and key, then enter a folder or notebook ID, eg. FL12344, NB182183",
            ""
        )
        if st.button("Import"):
            with st.spinner(f"importing documents from  {folder_to_import}"):
                if re.match(r'^[A-Z]{2}\d+', folder_to_import):
                    folder_to_import = folder_to_import[2:]
                loader = RSpaceLoader(api_key=st.session_state.rspace_apikey, url=st.session_state.rspace_url,
                                      folder_id=folder_to_import)
                for d in loader.lazy_load():
                    st.write(f"read doc {d.metadata['source']}")
                    imported_rspace_docs.append(d)
                st.write(f"Finished importing {len(imported_rspace_docs)} docs")
                st.session_state.loaded_docs = imported_rspace_docs
        if len(st.session_state.loaded_docs) > 0:
            if st.button("Summarise"):
                with st.spinner("Summarizing..."):
                    log_ct.empty()
                    writer = MyStreamLitHandler(log_ct)
                    result = run_summary(st.session_state.loaded_docs, writer)
                    st.code(result, language=None, line_numbers=False)


if __name__ == "__main__":
    main()
