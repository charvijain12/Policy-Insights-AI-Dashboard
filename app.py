import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime
from groq import Groq
from pypdf import PdfReader
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ---------- FORCE LIGHT MODE (Fixes UI issue on other systems) ----------
st.markdown("""
<style>
:root {
    color-scheme: light !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- FIXED WIDTH CONTAINER ----------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    max-width: 1100px;
    margin: auto;
}
</style>
""", unsafe_allow_html=True)

# ---------- FIX FILE UPLOADER WIDTH ----------
st.markdown("""
<style>
[data-testid="stFileUploader"] {
    width: 75% !important;
    margin-left: auto;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)

# ---------- SETUP ----------
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

POLICY_DIR = "policies"
os.makedirs(POLICY_DIR, exist_ok=True)

QUERY_FILE = "queries.csv"
if not os.path.exists(QUERY_FILE):
    pd.DataFrame(columns=["timestamp", "context", "question", "answer"]).to_csv(QUERY_FILE, index=False)

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Escobar Consultancy - Policy Insights", page_icon="💼", layout="wide")

# ---------- CSS THEME ----------
st.markdown("""
<style>

[data-testid="stSidebarContent"] {
    background: linear-gradient(180deg, #E6E6FA, #FFF8E1) !important;
    padding-top: 25px !important;
    border-right: 1px solid #e0e0e0;
}

.menu-item {
    padding: 12px 16px;
    border-radius: 10px;
    margin-bottom: 10px;
    cursor: pointer;
    display: block;
    font-size: 16px;
    color: black;
    background: rgba(255,255,255,0.45);
}
.menu-item:hover {
    background: rgba(255,255,255,0.7);
}

.card {
    background: white;
    padding: 22px;
    border-radius: 14px;
    border: 1px solid #e8e8e8;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

.chat-bubble-user {
    background-color: #E8DAEF;
    padding: 12px;
    border-radius: 10px;
    margin-top: 10px;
}

.chat-bubble-bot {
    background-color: #F3E5F5;
    padding: 12px;
    border-radius: 10px;
    border-left: 4px solid #C39BD3;
    margin-top: 10px;
}

div.stButton > button {
    background: linear-gradient(90deg, #F3E5F5, #E6E6FA);
    border: 1px solid #C39BD3;
    border-radius: 8px;
    color: black;
    padding: 8px 20px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
def show_header():
    st.markdown("""
        <div style="background: linear-gradient(90deg, #E6E6FA, #FFF8E1);
        padding:20px; border-radius:10px; text-align:center;
        box-shadow:0px 3px 10px rgba(0,0,0,0.08);">
            <h1>💼 Escobar Consultancy — Policy Insights Dashboard</h1>
            <p>Your AI-powered policy assistance platform.</p>
        </div>
    """, unsafe_allow_html=True)

# ---------- AI HELPER ----------
def ask_ai(prompt):
    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful HR assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {e}"

def save_query(context, q, a):
    df = pd.read_csv(QUERY_FILE)
    df.loc[len(df)] = [datetime.now(), context, q, a]
    df.to_csv(QUERY_FILE, index=False)

# ---------- SIDEBAR ----------
page = st.sidebar.radio(
    "",
    ["Home", "All Policies", "Upload or Choose & Ask", "Ask Policy AI", "My Analytics", "My FAQs", "Contact & Support"],
    label_visibility="collapsed"
)

# ----------------------------- HOME -----------------------------
if page == "Home":
    show_header()
    st.title("🏠 Welcome to Escobar Consultancy’s Policy Portal")
    st.markdown("""
    <div class='card'>
        <h3>About This Dashboard</h3>
        This dashboard allows employees to easily:
        <ul>
            <li>Browse and download company policies</li>
            <li>Upload a policy and ask questions</li>
            <li>Use AI for general HR questions</li>
            <li>View personal analytics and usage insights</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------- ALL POLICIES -----------------------------
elif page == "All Policies":
    st.title("📚 All Policies")
    files = [f for f in os.listdir(POLICY_DIR) if f.endswith(".pdf")]

    if not files:
        st.info("No policies found. Upload them to the GitHub 'policies' folder.")
    else:
        selected = st.selectbox("Select a policy", files)
        path = os.path.join(POLICY_DIR, selected)
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        st.markdown(
            f"<div class='card'><b>📄 {selected}</b><br>"
            f"<a href='data:application/pdf;base64,{b64}' download='{selected}'>📥 Download</a></div>",
            unsafe_allow_html=True
        )

# ------------------------ UPLOAD OR CHOOSE & ASK ------------------------
elif page == "Upload or Choose & Ask":
    st.title("📤 Upload or Choose a Policy")

    col1, col2 = st.columns(2)
    uploaded = col1.file_uploader("Upload policy (temporary)", type=["pdf"])

    files = [f for f in os.listdir(POLICY_DIR) if f.endswith(".pdf")]
    selected = col2.selectbox("Choose existing policy", files if files else ["None"])

    chosen = uploaded if uploaded else (selected if selected != "None" else None)

    if chosen:
        try:
            reader = PdfReader(uploaded if uploaded else open(os.path.join(POLICY_DIR, selected), "rb"))
            content = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        except:
            st.error("Could not read PDF.")

        st.markdown("## 💬 Ask about this policy")
        q = st.text_input("Your question")

        if st.button("Ask AI"):
            ans = ask_ai(f"Policy Document:\n{content[:5000]}\n\nQuestion: {q}")
            st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {q}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='chat-bubble-bot'><b>AI:</b> {ans}</div>", unsafe_allow_html=True)
            save_query(selected if not uploaded else uploaded.name, q, ans)

# ----------------------------- ASK POLICY AI -----------------------------
elif page == "Ask Policy AI":
    st.title("💬 General Policy AI Assistant")
    q = st.text_area("Ask any HR / policy question")

    if st.button("Ask"):
        ans = ask_ai(q)
        st.markdown(f"<div class='chat-bubble-user'>{q}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-bubble-bot'>{ans}</div>", unsafe_allow_html=True)
        save_query("General", q, ans)

# ----------------------------- MY ANALYTICS -----------------------------
elif page == "My Analytics":
    st.title("📊 My Analytics")

    df = pd.read_csv(QUERY_FILE)
    if df.empty:
        st.info("You haven't asked anything yet.")
    else:
        st.metric("Total Questions", len(df))
        st.metric("Unique Policies", df["context"].nunique())

        st.markdown("### 🔥 Word Cloud of Topics")
        text = " ".join(df["question"])
        wc = WordCloud(width=800, height=300, background_color="white", colormap="Purples").generate(text)

        fig, ax = plt.subplots()
        ax.imshow(wc)
        ax.axis("off")
        st.pyplot(fig)

# ----------------------------- FAQs -----------------------------
elif page == "My FAQs":
    st.title("❓ My FAQs")

    df = pd.read_csv(QUERY_FILE)
    if df.empty:
        st.info("No questions asked yet.")
    else:
        faqs = ask_ai("Create 5 FAQs from:\n" + "\n".join(df["question"]))
        st.markdown(f"<div class='card'>{faqs}</div>", unsafe_allow_html=True)

# ----------------------------- CONTACT -----------------------------
elif page == "Contact & Support":
    st.title("📞 Contact & Support")

    departments = {
        "HR": ("hr@escobarconsultancy.in", "98234xxxxx"),
        "Finance": ("finance@escobarconsultancy.in", "98188xxxxx"),
        "IT Support": ("itsupport@escobarconsultancy.in", "99777xxxxx"),
        "Admin": ("admin@escobarconsultancy.in", "91234xxxxx"),
    }

    for dept, info in departments.items():
        st.markdown(
            f"<div class='card'><h4>{dept}</h4>Email: {info[0]}<br>Phone: {info[1]}</div>",
            unsafe_allow_html=True
        )