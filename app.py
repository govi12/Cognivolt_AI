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

BIS_CONTEXT = """
You are an assistant that helps people understand BIS (Bureau of Indian Standards)
certification and Indian Standards. Use the reference information below to answer
questions. If the answer isn't covered by this information, say you don't have
information on that specific topic, and suggest checking bis.gov.in — don't make
up an answer.

Reference information:

1. BIS Certification: The Bureau of Indian Standards (BIS) is India's national
   standards body. Products carrying the ISI mark have been tested and certified
   to meet BIS quality and safety standards.

2. How to apply: Manufacturers submit an application to BIS with test reports from
   a BIS-recognized lab, pay the applicable fee, and undergo a factory inspection
   before certification is granted.

3. Products requiring mandatory BIS certification include electrical appliances,
   LPG cylinders, helmets, toys, pressure cookers, and cement, under the Compulsory
   Registration Scheme (CRS).

4. Hallmarking: BIS's certification for gold and silver jewellery, confirming
   purity. A hallmark includes the BIS logo, purity grade (e.g. 916 for 22K gold),
   and a unique HUID number.

5. Helmet standards: Two-wheeler helmets must comply with IS 4151, covering impact
   resistance, strap strength, and visibility.

6. LPG cylinder standards: Must comply with IS 3196, covering material strength,
   valve safety, and periodic testing.
"""


def get_answer(question: str) -> str:
    """Ask Gemini for an answer using the server-side secret."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "The GEMINI_API_KEY secret is not configured. Add it in the app's Secrets panel."
        )

    client = genai.Client(api_key=api_key)
    prompt = (
        f"{BIS_CONTEXT}\n\nUser's question: {question}\n\nAnswer clearly and concisely."
    )
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    answer = getattr(response, "text", None)
    if not answer:
        raise RuntimeError(
            "Gemini returned an empty response. Please try another question."
        )
    return answer


st.title("Cognivolt AI")
st.write("Ask about BIS certifications, ISI marks, and Indian Standards.")

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
