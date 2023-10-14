# Import necessary libraries
import collections
import re

import streamlit as st
from langchain.schema import Document
from rspace_client.eln import eln
from langchain.document_loaders.rspace import RSpaceLoader
from langchain.llms import OpenAI
from langchain.chat_models.openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
import textwrap
from typing import List
from callback_handlers import MyStreamLitHandler
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.callbacks import OpenAICallbackHandler
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA


## rob_nb=SD1932261


def show_help():
    st.write('## Instructions')
    st.write("First of all set up your RSpace key and URL. These will persist as long as you don't refresh the page.")
    st.write("Now enter a  global ID - this can be a folder (FLXXXX), notebook (NBXXXX), document (SDXXXX) "
             "or a PDF document in the gallery (GLXXXXX). "
             "A maximum of  20 documents will be uploaded from a folder or notebook. This is not recursive - only top-"
             "level documents are uploaded.")
    st.write("Once the docs are loaded, choose a model and a summary strategy. The default settings are likely to "
             "produce the highest quality output.")
    st.write("Once the docs are loaded, they will be sent to the LLM (OpenAI gpt3.5) for summarising. You "
             "can follow progress in the Logs tab.")
    st.write("In general, one new 'chain' is started per document. ")
    st.write("Depending on length of the docs, this might take some time. Documents are summarised recursively.")
    st.write("No content is created or altered  in your RSpace account - data is only read.")


def run_summary(docs: List[Document], log_tab_writer: MyStreamLitHandler, model_choice: str,
                summary_method: str) -> str:
    if "instruct" in model_choice:
        chat_llm = OpenAI(temperature=0.0, batch_size=20)
    else:
        chat_llm = ChatOpenAI(temperature=0.0, model_name=model_choice)

    prompt = """
     Write a concise  summary of the input text. Convey as wide a  range of information as possible.
     The summary must reduce the word count to less than 50% of the wordcount of the text, and must be less than 250 words.
     
     Think! Count the number of words in the input text
     
     Write the concise  summary of the input text and then write a maximum 10 keywords at the end on a newline.
     
     Think! Is the summary less than 50% of the wordcount of the original text, and less than 250 words?
     
    START OF INPUT
    
    {text}
    
    END OF INPUT
    Your summary:
    
    Keywords:
        """
    prompt_t = PromptTemplate(input_variables=['text'], template=prompt)
    chain = None
    if summary_method == "refine":
        chain = load_summarize_chain(llm=chat_llm, verbose=True, chain_type=summary_method)
    else:
        chain = load_summarize_chain(llm=chat_llm, verbose=True, chain_type=summary_method, combine_prompt=prompt_t)

    splitter = RecursiveCharacterTextSplitter(chunk_size=3500, chunk_overlap=200)
    split_docs = splitter.split_documents(docs)

    # collects usage and billing info
    openai_cb = OpenAICallbackHandler()

    output_summary = chain.run(split_docs, callbacks=[log_tab_writer, openai_cb])
    wrapped_text = textwrap.fill(output_summary, width=60)
    log_tab_writer.container.write(openai_cb)
    return wrapped_text


def form_callback():
    st.session_state.eln_cli = eln.ELNClient(
        st.session_state.rspace_url, st.session_state.rspace_apikey
    )
    st.sidebar.write(st.session_state.eln_cli.get_status())


def import_content_into_session(global_id: str):
    loader = RSpaceLoader(api_key=st.session_state.rspace_apikey, url=st.session_state.rspace_url,
                          global_id=global_id.strip())
    imported_rspace_docs = []
    for d in loader.lazy_load():
        st.write(f"read doc {d.metadata['source']}")
        imported_rspace_docs.append(d)
    st.write(f"Finished importing {len(imported_rspace_docs)} docs")
    st.session_state.loaded_docs = imported_rspace_docs
    if len(imported_rspace_docs) == 0:
        st.write("No documents were retrieved. If you were importing a folder, maybe it's empty. If you "
                 "were importing a Gallery file, it has to be a PDF file with a '.pdf' file extension.")


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

    importer_tab, qandatab, logger_tab, help_tab = st.tabs(["Import Docs & summarise", "QandA", "Logs", "Instructions"])
    imported_rspace_docs = []
    if 'loaded_docs' not in st.session_state:
        st.session_state.loaded_docs = []
    if 'vstores' not in st.session_state:
        st.session_state.vstores = {}
    with logger_tab:
        log_ct = st.container()
    with help_tab:
        show_help()

    with qandatab:
        chat_llm = OpenAI(temperature=0.0, batch_size=20)
        current_state = st.container()
        with current_state:
            for k in st.session_state.vstores.keys():
                current_state.write(f"Store exists for {k}")

        item_to_import = st.text_input(
            "First, enter your RSpace URL and key in the sidebar. Then enter a folder, document or  notebook "
            "globalID. A search index will be created from the imported data, and you can question it",
        )
        st.write("First of all import your RSpace documents")
        if st.button("Create vector DB"):
            global_id = item_to_import.strip()
            st.session_state.global_id = global_id
            with st.spinner(f"importing documents from  {global_id}"):
                import_content_into_session(global_id)
            with st.spinner("Creating vector DB"):
                docs: List[Document] = st.session_state.loaded_docs
                splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                split_docs = splitter.split_documents(docs)
                st.write(f"Split into {len(split_docs)} fragments ")
                v_stores = st.session_state.vstores
                if v_stores is None:
                    st.session_state.vstores={}
                if v_stores is None or global_id not in v_stores.keys():
                    st.write(f"regenerating vector db for {global_id}")
                    st.session_state.vstores[global_id] = Chroma.from_documents(documents=split_docs,
                                                                               embedding=OpenAIEmbeddings())

        if st.button("Clear All", help="Removes all database created from your imported documents"):
            st.session_state.vstores = {}
        with st.form("query the docs"):
            st.write("Enter a question in plain text about the content of the data")
            query = st.text_input("Query")
            bt = st.form_submit_button("Go")

            if bt:
                global_id = st.session_state.global_id
                v_stores = st.session_state.vstores
                if v_stores is None or global_id not in v_stores.keys():
                    st.write(f"no data in vector store for global_id {global_id}")
                else:
                    st.write (f"Querying db from {global_id} ")
                    v_store = v_stores[global_id]
                    retriever = v_store.as_retriever(search_kwargs={'k': 4, 'score_threshold': 0.8})
                    qa_chain = RetrievalQA.from_chain_type(chat_llm, chain_type='stuff', retriever=retriever, verbose=True)
                    result = qa_chain({"query": query})
                    st.write(result)

    with importer_tab:
        item_to_import = st.text_input(
            "First, enter your RSpace URL and key in the sidebar. Then enter a folder, document or  notebook "
            "globalID. You can also  import a PDF from the Gallery using its global ID (e.g GL12345)",
        )

        if st.button("Import"):
            with st.spinner(f"importing documents from  {item_to_import.strip()}"):
                import_content_into_session((item_to_import.strip()))

        if len(st.session_state.loaded_docs) > 0:
            if st.button("Clear existing data"):
                st.session_state.loaded_docs = []
            model_choice = st.radio(label="Choose a  model", options=["gpt-3.5-turbo-instruct", "gpt-3.5-turbo"],
                                    help="'gpt-3.5-turbo-instruct' variant is faster, but tends to produce text that "
                                         "is more "
                                         "unstructured. 'gpt-3.5-turbo' is slower but produces better quality, "
                                         "more natural prose.")
            summary_method = st.radio(label="Summarization strategy", options=["map_reduce",
                                                                               "refine"],
                                      help="""       
                                           - map_reduce summarizes all documents, then summarizes the summaries 
                                            until a single summary remains. It is faster as many documents can be 
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
