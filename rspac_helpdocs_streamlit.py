# Import necessary libraries
import collections
import os
import re

import boto3
from dotenv import load_dotenv

from langchain.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
import streamlit as st

download_dir = "rspac-helpdocs"


def set_vector_store_in_session(vs):
    st.session_state.vs=vs


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


if st.button("Import ChromaDB from S3"):
    list_s3()
    vs = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory=download_dir)


form = st.form("Search RSpace Helpocs")
search_term =form.text("Enter a search term")

if st.form_submit_button:
    resp = st.session_state.vs.similarity_search(search_term)
    st.write(resp)


if __name__ == '__main__':
    # list_s3()
    vs = Chroma(embedding_function=OpenAIEmbeddings(), persist_directory=download_dir)
    resp = vs.similarity_search("how do I create a notebook")
    print(resp[0])
