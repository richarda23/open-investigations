# Import necessary libraries
import collections
import re

import streamlit as st
from langchain.schema import Document
from rspace_client.eln import eln
from jupyter_notebooks.rspace_loader import RSpaceLoader;
from langchain.llms import OpenAI
from langchain.chat_models.openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
import textwrap
from typing import List
from callback_handlers import MyStreamLitHandler
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.callbacks import OpenAICallbackHandler


def show_help():
    st.write('## Instructions')
    st.write("First of all set up your RSpace key and URL. These will persist as long as you don't refresh the page.")
    st.write("Now enter a folder or notebook ID. Up to 20 documents will be uploaded. This is not recursive - only top-"
             "level documents are uploaded.")
    st.write("Once the docs are loaded, choose a model and a summary strategy. The default settings are likely to "
             "produce "
             "the highest quality output.")
    st.write("Once the docs are loaded, they will be sent to the LLM (OpenAI gpt3.5) for summarising. You "
             "can follow progress in the Logs tab.")
    st.write("In general, one new 'chain' is started per document. ")
    st.write("Depending on length of the docs, this might take some time. Documents are summarised recursively.")
    st.write("No content is created or altered  in your RSpace account - data is only read.")


def run_summary(docs: List[Document], handler, model_choice, summary_method) -> str:
    if "instruct" in model_choice:
        chat_llm = OpenAI(temperature=0.0, model=model_choice)
    else:
        chat_llm = ChatOpenAI(temperature=0.0, model=model_choice)

    prompt = """
     Write a concise summary of the input text.
     The summary must be at most half the length of the input text, but can be up to 250 words. 
    
    The text:
    
    {text}
    
    Your summary:
    
    Keywords:
        """
    prompt_t = PromptTemplate(input_variables=['text'], template=prompt)

    chain = load_summarize_chain(llm=chat_llm, verbose=True, chain_type=summary_method, combine_prompt=prompt_t)
    splitter = RecursiveCharacterTextSplitter(chunk_size=3500, chunk_overlap=200)
    split_docs = splitter.split_documents(docs)

    # collects usage and billing info
    openai_cb = OpenAICallbackHandler()

    output_summary = chain.run(split_docs, callbacks=[handler, openai_cb])
    wrapped_text = textwrap.fill(output_summary, width=60)
    handler.container.write(openai_cb)
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
        if st.button("Clear existing data"):
            st.session_state.loaded_docs = []
        if st.button("Import"):
            with st.spinner(f"importing documents from  {folder_to_import}"):
                loader = RSpaceLoader(api_key=st.session_state.rspace_apikey, url=st.session_state.rspace_url,
                                      global_id=folder_to_import)
                for d in loader.lazy_load():
                    st.write(f"read doc {d.metadata['source']}")
                    imported_rspace_docs.append(d)
                st.write(f"Finished importing {len(imported_rspace_docs)} docs")
                st.session_state.loaded_docs = imported_rspace_docs
        if len(st.session_state.loaded_docs) > 0:
            model_choice = st.radio(label="Choose a language model", options=["gpt-3.5-turbo",
                                                                              "gpt-3.5-turbo-instruct"],
                                    help="'gpt-3.5-turbo-instruct' variant is faster, but tends to produce text that "
                                         "is more "
                                         "unstructured. 'gpt-3.5-turbo' is slower but produces better quality, "
                                         "more natural prose.")
            summary_method = st.radio(label="Summarization strategy", options=["map_reduce",
                                                                               "refine"],
                                      help="""       
                                           - map_reduce summarizes all documents, then summarizes the summaries 
                                            until a single summary remains. It is faster as all the documents can be 
                                            processed in parallel.
                                           - refine progressively edits an initial summary, as more documents are processed.
                                           """)
            if st.button("Summarise"):
                with st.spinner("Summarizing..."):
                    log_ct.empty()
                    writer = MyStreamLitHandler(log_ct)
                    result = run_summary(st.session_state.loaded_docs, writer, model_choice, summary_method)
                    st.code(result, language=None, line_numbers=False)


if __name__ == "__main__":
    main()
