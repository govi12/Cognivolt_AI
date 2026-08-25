import os
import random
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
certification and Indian Standards. Provide thorough, well-explained answers — include
context, practical steps, and examples where helpful, not just a one-line answer.

Treat the reference information below as your source of truth for specific facts,
standard numbers, and figures — don't contradict it. You may also draw on your
general knowledge of India's regulatory and certification landscape to explain
concepts more fully, as long as it stays consistent with the reference information.
If a question is genuinely unrelated to BIS/Indian Standards, say so honestly rather
than guessing.

Reference information:

1. About BIS: The Bureau of Indian Standards (BIS) is India's National Standards
   Body, responsible for standardisation, marking, and quality certification of
   goods. Originally established as the Indian Standards Institution (ISI) on
   January 7, 1947, it was formally reconstituted as BIS under the BIS Act 1986
   (effective April 1, 1987) and now operates under the BIS Act 2016. It functions
   under the Ministry of Consumer Affairs, Food & Public Distribution, headquartered
   in New Delhi with 5 regional offices.

2. BIS Certification: An official mark proving a product meets Indian Standards for
   quality, performance, and safety. Required before many goods can be legally sold,
   manufactured, or imported into India. Main schemes:
   - ISI Mark Scheme (Scheme-I): industrial/consumer goods (cement, steel, LPG
     cylinders, electrical appliances) — requires factory inspection.
   - Compulsory Registration Scheme (CRS): electronics and IT products (mobile
     phones, laptops, LED TVs, Bluetooth devices like speakers/headphones/
     smartwatches) — based on self-declaration and lab testing.
   - Foreign Manufacturers Certification Scheme (FMCS): for imported products,
     requires an Indian representative.
   Over 300 product categories require mandatory BIS certification under government
   Quality Control Orders (QCOs).

3. How to apply for an ISI mark: Identify the applicable Indian Standard (IS code)
   for your product, get preliminary testing done at a BIS-recognized lab, register
   and apply through the BIS Manak Online Portal (manakonline.in) with required
   documents (business proof, factory layout, quality control manual, test reports,
   raw material/supplier details) and fees, undergo a factory inspection, and
   receive the license upon approval.

4. License validity: As of a February 2026 BIS regulation update, a Standard Mark
   license is now valid for up to 5 years on first grant, renewable for further
   5-year terms with annual fee payment — a significant increase from the earlier
   1-2 year validity period.

5. Fee concessions for MSMEs: BIS offers concessions on marking fees — 80% for
   Micro Scale units and Startups, 50% for Small Scale, and 20% for Medium Scale
   enterprises. An additional 10% concession applies to Women Entrepreneurs and
   enterprises located in North-East India.

6. Hallmarking (gold/silver): BIS's certification confirming precious metal purity.
   Since the HUID (Hallmark Unique Identification) system was introduced on
   July 1, 2021, a valid hallmark consists of exactly 3 marks: the BIS logo, the
   purity/fineness grade (e.g. 916 for 22K gold, 750 for 18K, 585 for 14K), and a
   unique 6-digit alphanumeric HUID code. Older pre-2021 items may show additional
   separate assaying-centre and jeweller marks — that 5-mark format is no longer
   used for new hallmarks.

7. Helmet standards: Two-wheeler helmets must comply with IS 4151:2015, covering
   impact absorption, penetration resistance, and chin strap/retention strength.
   Related: IS 2925:1984 (industrial safety helmets), IS 2745:1983 (firefighter
   helmets).

8. LPG cylinder standards: IS 3196 (Part 1):2006 covers welded steel LPG cylinders
   above 5-litre capacity; IS 7142 covers smaller cylinders under 5 litres; IS 8737
   covers valve fittings for cylinders above 5-litre capacity, requiring impact,
   pneumatic, torque, and hydrostatic testing.

9. Toy safety standards: Under the Toys (Quality Control) Order, IS 9873 covers
   mechanical/physical safety (Part 1), flammability (Part 2), and chemical safety
   restricting heavy metals like lead, mercury, and cadmium (Parts 3 & 9).

10. Food, water & infant product standards: IS 14543 (packaged drinking water),
    IS 13428 (packaged natural mineral water), IS 1165 (milk powder), IS 14433
    (infant milk substitutes), IS 4984 (HDPE pipes for potable water).

11. PVC material standards: IS 10151 (PVC for food/pharma/drinking water contact,
    limiting residual vinyl chloride monomer), IS 4985 (UPVC pipes for water
    supply), IS 15778 (CPVC pipes for hot/cold water), IS 6719 (PVC soles and
    heels for footwear), IS 13592 (UPVC soil/waste pipes), IS 9537 (PVC electrical
    conduits).

12. Stainless steel standards: IS 6911 (plate/sheet/strip), IS 1570 (grade
    classification, e.g. 304, 316), IS 3444 (bars and flats), IS 7283 (tubes),
    IS 6529 (wire), IS 6603 (forgings).

13. Automotive component standards: IS 15633 (tubeless tyres for passenger cars),
    IS 15636 (tyres for trucks/commercial vehicles), IS 2573 (brake linings),
    IS 2553 Part 1 (safety glass for windscreens/windows).
"""
def get_answer(question: str) -> str:  
        """Ask Gemini for an answer using a randomly chosen server-side key."""
        keys = [
            os.getenv("GEMINI_API_KEY_1"),
            os.getenv("GEMINI_API_KEY_2"),
            os.getenv("GEMINI_API_KEY_3"),
            os.getenv("GEMINI_API_KEY_4"),
            os.getenv("GEMINI_API_KEY_5"),
            os.getenv("GEMINI_API_KEY_6"),
        ]
        keys = [k for k in keys if k]  # drop any unset ones
        if not keys:
            raise RuntimeError(
                "No Gemini API keys configured. Add them in the app's Secrets panel."
            )
        api_key = random.choice(keys)
        client = genai.Client(api_key=api_key)
prompt = f"{BIS_CONTEXT}\n\nUser's question: {question}\n\nProvide a detailed, well-explained answer with relevant context or examples. When your answer references a specific fact from the reference information, mention the relevant IS standard number or scheme name (e.g., 'as per IS 4151:2015') so the user knows exactly which standard applies."
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


with st.sidebar:
    st.markdown("### Try asking:")
    sample_questions = [
        "What is an ISI mark?",
        "How do I apply for BIS certification?",
        "What standard applies to two-wheeler helmets?",
        "What does hallmarking mean for gold?",
    ]
    for q in sample_questions:
        if st.button(q, use_container_width=True):
            st.session_state.pending_question = q

    st.markdown("---")
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
st.title("Cognivolt AI")
st.write("Ask about BIS certifications, ISI marks, and Indian Standards.")

# Keep track of the conversation across questions
if "messages" not in st.session_state:
    st.session_state.messages = []

# Redraw all previous messages every time the page updates
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box, pinned to the bottom like Grok/ChatGPT
question = st.chat_input("What would you like to know?")

if "pending_question" in st.session_state:
    question = st.session_state.pending_question
    del st.session_state.pending_question

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = get_answer(question)
            except Exception as error:
                answer = f"Unable to get an answer: {error}"
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

st.markdown("---")
st.caption("Built for Smart India Hackathon 2026 — Team Cognivolt")
