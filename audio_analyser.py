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


def do_message(system, user=None):
    messages = [
        {
            "role": "system",
            "content": f"{system}"
        }
    ]
    if user is not None:
        messages.append({
            "role": "system",
            "content": f"{user}"
        })

    response = client.chat.completions.create(
        model="gpt-4",
        temperature=0,
        messages=messages
    )
    return response.choices[0].message.content


def complexity(transcription):
    return do_message("Please explain what reading level and typical age is needed to understand the text",
                      transcription)


def goodexpl(subject, input2):
    return do_message(f"Please explain if this is a good explanation for {subject}. Don't suggest an alternative "
                      f"explanation", input2)


def alternative(subject):
    return do_message(f"Please provide a brief explanation of {subject} suitable for a 7 year old ")


# Main function for Streamlit app
def main():
    st.set_page_config(page_title="Am I  understandable?")

    with st.expander("Instructions"):
        st.write(
            """
            - Record a short  audio file (e.g. 30 seconds) of you describing a complicated topic
            - Upload it here (must be m4a, mp3, mp4, mpeg format)
            - App will transcribe to text and comment on the reading-age needed to understand the text
            - App will also comment on whether the explanation is a good one 
            - Powered by OpenAI's Whisper
        """
        )
    uploaded_file = st.file_uploader("Please upload an audio file of your speech",
                                     type=['flac', 'm4a', 'mp3', 'mp4', 'mpeg', 'mpga', 'oga', 'ogg', 'wav', 'webm'])
    if uploaded_file is not None:
        st.session_state.file_bytes = uploaded_file

    subject = st.text_input('What are you trying to talk about?')
    if st.button("Analyse"):
        with st.spinner("Analysing..."):
            text = transcribe(st.session_state.file_bytes)
            st.header("Transcription")
            st.write(text)
            st.header("Complexity analysis")
            analysis = complexity(text)
            st.write(analysis)
            st.header("Relevance")
            rel = goodexpl(subject, text)
            st.write(rel)
            st.header("Alternative suitable for 7 year old")
            alt = alternative(subject)
            st.write(alt)

    # Create a button with label 'Clear Input'
    if st.button("Clear Input"):
        # Clear the text area
        st.session_state.file_bytes = None
        st.experimental_rerun()


if __name__ == "__main__":
    main()
