# Import necessary libraries
import collections
import os
import re

import boto3
from dotenv import load_dotenv
from langchain.chains import QAWithSourcesChain, RetrievalQAWithSourcesChain
from langchain.chains.retrieval_qa.base import BaseRetrievalQA

from langchain.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.retrievers import ParentDocumentRetriever
import streamlit as st

download_dir = "rspac-helpdocs"


def set_vector_store_in_session(vs):
    st.session_state.vs = vs


def get_vector_store_from_session():
    return st.session_state.vs


def list_s3():
    s3 = boto3.resource(
        's3',
        # aws_access_key_id=st.secrets['AWS_ACCESS_KEY_ID'],
        # aws_secret_access_key=st.secrets['AWS_SECRET_ACCESS_KEY'],
    )
    bucket_name = 'chroma-databases'
    bucket = s3.Bucket(bucket_name)
    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)
    for obj in bucket.objects.all():
        f_name = obj.key.split('/')[-1]
        print(f_name, obj.key)
        bucket.download_file(obj.key, f"{download_dir}/{f_name}")


def load_db_into_session():
    vs = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory=download_dir)
    set_vector_store_in_session(vs)
    st.write("helpdocs db stored in session")


if st.button("Import ChromaDB from S3"):
    list_s3()
    load_db_into_session()

if st.button("Load vector DB"):
    load_db_into_session()


with st.form("Search RSpace Helpdocs"):
    search_term = st.text_input("Enter a search term")

    if st.form_submit_button("Submit query"):
        resp = st.session_state.vs.similarity_search(search_term)
        chat_llm = ChatOpenAI(temperature=0.0)
        vs = get_vector_store_from_session()
        chain = RetrievalQAWithSourcesChain.from_chain_type(chain_type="stuff",
                                                            retriever=vs.as_retriever(),
                                                            return_source_documents=True,
                                                            llm=chat_llm, verbose=True)
        output = chain({"question": search_term})
        srcs = [o.metadata['source'] for o in output['source_documents']]
        st.write(output['answer'])
        st.header("Sources")
        for s in srcs:
            st.markdown(f"[{s}]({s})")

if __name__ == '__main__':
    # list_s3()


    st.write(output)
