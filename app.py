import os

import streamlit as st
from google import genai


st.set_page_config(
    page_title="Cognivolt AI",
    page_icon="✦",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stTextArea textarea {
        padding-top: 10px;
        padding-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_answer(question: str) -> str:
    """Ask Gemini for an answer using the server-side secret."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "The GEMINI_API_KEY secret is not configured. Add it in the app's Secrets panel."
        )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=question,
    )

    answer = getattr(response, "text", None)
    if not answer:
        raise RuntimeError(
            "Gemini returned an empty response. Please try another question."
        )
    return answer


st.title("Cognivolt AI")
st.write("Ask a question and get a thoughtful answer powered by Cognivolt AI.")

with st.form("question_form"):
    question = st.text_area(
        "Your question",
        placeholder="What would you like to know?",
        height=140,
    )
    submitted = st.form_submit_button("Get answer", type="primary")

if submitted:
    question = question.strip()
    if not question:
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Thinking..."):
            try:
                answer = get_answer(question)
            except Exception as error:
                st.error(f"Unable to get an answer: {error}")
            else:
                st.subheader("Answer")
                st.markdown(answer)
