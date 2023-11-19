# Import necessary libraries
import streamlit as st
import json
from openai import OpenAI

GPT_MODEL = "gpt-4"

client = OpenAI()


def transcribe(audio_file):

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text",
        language="en"
    )
    return transcript


def complexity(transcription):
    response = client.chat.completions.create(
        model="gpt-4",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": f"Please explain what reading level and typical age is needed to understand the text"
            },
            {
                "role": "user",
                "content": transcription
            }
        ]
    )
    return response.choices[0].message.content


# Main function for Streamlit app
def main():
    st.set_page_config(page_title="Am I  understandable?")

    with st.expander("Instructions"):
        st.write(
            """
            - Record a short  audio file (e.g. 30 seconds) of you describing a complicated topic
            - Upload it here (must be m4a, mp3, mp4, mpeg format)
            - App will transcribe to text and comment on the reading-age needed to understand the text
            - Powered by OpenAI's Whisper
        """
        )
    uploaded_file = st.file_uploader("Please upload an audio file of your speech", type=['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm'])
    if uploaded_file is not None:
        st.session_state.file_bytes = uploaded_file

    if st.button("Analyse"):
        with st.spinner("Analysing..."):
            text = transcribe(st.session_state.file_bytes)
            st.header("Transcription")
            st.write(text)
            st.header("Complexity analysis")
            analysis = complexity(text)
            st.write(analysis)

    # Create a button with label 'Clear Input'
    if st.button("Clear Input"):
        # Clear the text area
        st.experimental_rerun()
        st.session_state.file_bytes = None


if __name__ == "__main__":
    main()
