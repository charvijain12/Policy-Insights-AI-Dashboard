import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ---------- SETUP ----------
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

POLICY_DIR = "policies"
os.makedirs(POLICY_DIR, exist_ok=True)

QUERY_FILE = "queries.csv"
if not os.path.exists(QUERY_FILE):
    pd.DataFrame(columns=["timestamp", "context", "question", "answer"]).to_csv(QUERY_FILE, index=False)

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Policy Insights Dashboard", page_icon="💼", layout="wide")

# ---------- HEADER / STYLING ----------
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #23395d, #406080);
    color: white;
}
.chat-bubble-user {
    background-color: #004080;
    color: white;
    padding: 12px;
    border-radius: 10px;
    margin: 8px 0;
}
.chat-bubble-bot {
    background-color: #f8f9fa;
    color: black;
    padding: 12px;
    border-radius: 10px;
    border-left: 4px solid #004080;
    margin: 8px 0;
}
.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.08);
    margin-bottom: 15px;
}
.header {
    background: linear-gradient(90deg, #004080, #0077b6);
    padding: 15px;
    border-radius: 10px;
    color: white;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'><h2>🏢 Policy Insights AI Dashboard</h2><p>Empowering Employees to Understand Company Policies</p></div>", unsafe_allow_html=True)

# ---------- HELPER FUNCTIONS ----------
def ask_ai(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional HR policy assistant who explains company policies clearly and politely."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"

def save_query(context, question, answer):
    df = pd.read_csv(QUERY_FILE)
    new_row = pd.DataFrame([[datetime.now(), context, question, answer]], columns=["timestamp", "context", "question", "answer"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(QUERY_FILE, index=False)

def show_policy_card(file_path):
    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        download_link = f"<a href='data:application/octet-stream;base64,{b64}' download='{file_name}'>📥 Download</a>"
    st.markdown(f"<div class='card'><b>📄 {file_name.replace('_', ' ').title()}</b><br>{download_link}</div>", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("", ["📚 All Policies", "📤 Upload or Choose & Ask", "💬 Ask Policy AI", "📊 My Analytics", "❓ My FAQs"])
st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Upload a PDF temporarily or pick one from the library to ask questions.")

# ---------- MAIN CONTENT ----------

# ---- TAB 1: All Policies ----
if page == "📚 All Policies":
    st.title("📚 Company Policy Library")
    st.markdown("Browse and download all available company policies from below:")

    company_policies = [os.path.join(POLICY_DIR, f) for f in os.listdir(POLICY_DIR) if f.endswith(".pdf")]
    if not company_policies:
        st.info("No policies found in the 'policies/' folder.")
    else:
        selected_policy = st.selectbox("Select a Policy", [os.path.basename(f) for f in company_policies])
        show_policy_card(os.path.join(POLICY_DIR, selected_policy))

# ---- TAB 2: Upload or Choose & Ask ----
elif page == "📤 Upload or Choose & Ask":
    st.title("📤 Upload or Choose a Policy to Chat About")

    col1, col2 = st.columns(2)

    with col1:
        uploaded = st.file_uploader("Upload a Policy PDF (temporary, not saved)", type=["pdf"])

    with col2:
        company_files = [f for f in os.listdir(POLICY_DIR) if f.endswith(".pdf")]
        selected = st.selectbox("Or Choose from Existing Policies", company_files if company_files else ["No company files yet"])

    chosen_file = uploaded if uploaded else (selected if selected != "No company files yet" else None)
    file_content = None

    if uploaded:
        try:
            reader = PdfReader(uploaded, strict=False)
            file_content = "\n".join(p.extract_text() for p in reader.pages if p.extract_text())
        except PdfReadError:
            st.error("⚠️ Could not read the uploaded file. Please upload a valid PDF.")
    elif selected and selected != "No company files yet":
        with open(os.path.join(POLICY_DIR, selected), "rb") as f:
            reader = PdfReader(f, strict=False)
            file_content = "\n".join(p.extract_text() for p in reader.pages if p.extract_text())

    if file_content:
        st.markdown("### 💬 Chat About This Policy")
        user_q = st.text_input("Ask a question about this policy:")
        colA, colB = st.columns(2)
        with colA:
            ask_button = st.button("Ask AI")
        with colB:
            summary_button = st.button("📝 Summarize Policy")

        if ask_button and user_q.strip():
            with st.spinner("Analyzing and generating answer..."):
                answer = ask_ai(f"Policy Content:\n{file_content[:6000]}\n\nQuestion: {user_q}")
                st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {user_q}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='chat-bubble-bot'><b>AI:</b> {answer}</div>", unsafe_allow_html=True)
                save_query(uploaded.name if uploaded else selected, user_q, answer)

        elif summary_button:
            with st.spinner("Summarizing policy..."):
                summary = ask_ai(f"Summarize this policy in 5 bullet points:\n{file_content[:6000]}")
                st.markdown(f"<div class='chat-bubble-bot'><b>Summary:</b><br>{summary}</div>", unsafe_allow_html=True)

# ---- TAB 3: Ask Policy AI ----
elif page == "💬 Ask Policy AI":
    st.title("💬 General Policy AI Assistant")
    question = st.text_area("Ask any question about company policies or HR practices:")
    if st.button("Ask"):
        if question.strip():
            with st.spinner("Thinking..."):
                answer = ask_ai(f"Employee Question: {question}")
                st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {question}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='chat-bubble-bot'><b>AI:</b> {answer}</div>", unsafe_allow_html=True)
                save_query("General", question, answer)
        else:
            st.warning("Please enter a question.")

# ---- TAB 4: Analytics ----
elif page == "📊 My Analytics":
    st.title("📊 My Analytics")
    df = pd.read_csv(QUERY_FILE)
    if df.empty:
        st.info("You haven’t asked any questions yet.")
    else:
        st.metric("Total Questions", len(df))
        st.metric("Unique Policies", df['context'].nunique())

        # Word cloud for top topics
        text_data = " ".join(df["question"].tolist())
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text_data)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

        st.dataframe(df.sort_values("timestamp", ascending=False).head(10))

# ---- TAB 5: FAQs ----
elif page == "❓ My FAQs":
    st.title("❓ Common Employee FAQs")
    df = pd.read_csv(QUERY_FILE)
    if df.empty:
        st.info("No questions yet — start asking in the other tabs.")
    else:
        questions = "\n".join(df["question"].tolist())
        with st.spinner("Generating FAQs..."):
            faqs = ask_ai(f"From these employee questions, create 5 helpful FAQ-style Q&A pairs:\n{questions}")
        st.markdown(f"<div class='card'>{faqs}</div>", unsafe_allow_html=True)