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
st.set_page_config(page_title="Escobar Consultancy - Policy Insights", page_icon="💼", layout="wide")

# ---------- CSS ----------
st.markdown("""
<style>

[data-testid="stSidebarContent"] {
    background: linear-gradient(180deg, #E6E6FA, #FFF8E1) !important;
    padding-top: 25px !important;
    border-right: 1px solid #e0e0e0;
}

section[data-testid="stSidebar"] div[role="radiogroup"] {
    background: transparent !important;
    border: none !important;
}
section[data-testid="stSidebar"] input[type="radio"] { display: none !important; }
section[data-testid="stSidebar"] label { background: transparent !important; }

.menu-item {
    padding: 10px 16px;
    border-radius: 10px;
    margin-bottom: 10px;
    cursor: pointer;
    display: block;
    font-size: 16px;
    font-weight: 500;
    color: black;
    background: rgba(255,255,255,0.45);
    text-decoration: none;
    transition: 0.2s ease;
}
.menu-item:hover {
    background: rgba(255,255,255,0.7);
    transform: translateX(5px);
}
.menu-active {
    background: white !important;
    border-left: 4px solid #C39BD3 !important;
    font-weight: 600 !important;
}

/******** HEADER ********/
.header {
    background: linear-gradient(90deg, #E6E6FA, #FFF8E1);
    padding: 20px;
    border-radius: 10px;
    color: black;
    text-align: center;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
    margin-bottom: 30px;
}

/******** CARDS ********/
.card {
    background: white;
    border: 1px solid #e8e8e8;
    padding: 22px;
    border-radius: 14px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

/******** CHAT ********/
.chat-bubble-user {
    background-color: #E8DAEF;
    padding: 12px;
    border-radius: 10px;
    margin: 10px 0;
}
.chat-bubble-bot {
    background-color: #F3E5F5;
    padding: 12px;
    border-radius: 10px;
    border-left: 4px solid #C39BD3;
    margin: 10px 0;
}

/******** BUTTONS ********/
div.stButton > button {
    background: linear-gradient(90deg, #F3E5F5, #E6E6FA);
    border: 1px solid #C39BD3;
    border-radius: 8px;
    color: black;
    padding: 8px 20px;
    font-weight: 600;
}
div.stButton > button:hover {
    background: linear-gradient(90deg, #E6E6FA, #F3E5F5);
}

body, [data-testid="stAppViewContainer"] {
    background-color: #FAFAFA;
    font-family: "Segoe UI", sans-serif;
}

</style>
""", unsafe_allow_html=True)

# ---------- HEADER (only for Home page) ----------
def show_header():
    st.markdown("""
    <div class='header'>
        <h1>💼 Escobar Consultancy — Policy Insights Dashboard</h1>
        <p>Your AI-powered company policy assistant.</p>
    </div>
    """, unsafe_allow_html=True)

# ---------- HELPERS ----------
def ask_ai(prompt):
    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role":"system","content":"You are a friendly HR assistant."},
                {"role":"user","content":prompt}
            ],
            temperature=0.2,
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {e}"

def save_query(context, q, a):
    df = pd.read_csv(QUERY_FILE)
    new = pd.DataFrame([[datetime.now(), context, q, a]],columns=["timestamp","context","question","answer"])
    df = pd.concat([df,new], ignore_index=True)
    df.to_csv(QUERY_FILE,index=False)

def category_of(question):
    q = question.lower()
    if any(x in q for x in ["leave","holiday","vacation"]): return "Leave & Attendance"
    if any(x in q for x in ["salary","pay","compensation"]): return "Payroll & Compensation"
    if any(x in q for x in ["policy","rules"]): return "Policy Clarification"
    if any(x in q for x in ["approval","form","hr"]): return "HR Processes"
    return "General"

def show_policy_card(path):
    name = os.path.basename(path)
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f"<div class='card'><b>📄 {name}</b><br>"
        f"<a style='color:#6C35A3;' href='data:application/octet-stream;base64,{b64}' download='{name}'>📥 Download</a></div>",
        unsafe_allow_html=True
    )

# ---------- SIDEBAR NAV ----------
st.sidebar.markdown("### 🧭 Navigation")

page = st.sidebar.radio(
    "",
    [
        "Home",
        "All Policies",
        "Upload or Choose & Ask",
        "Ask Policy AI",
        "My Analytics",
        "My FAQs",
        "Contact & Support"
    ],
    label_visibility="collapsed"
)

# ===========================================
#                HOME PAGE
# ===========================================
if page == "Home":
    show_header()
    st.title("🏠 Welcome to Escobar Consultancy’s Policy Portal")

    st.markdown("""
    <div class='card'>
        <h3>About This Dashboard</h3>
        <p>
        This platform helps employees easily access, understand, and navigate company policies using AI-powered support.
        </p>

        <ul style="margin-left:20px;">
            <li>Browse official company policies</li>
            <li>Upload a policy temporarily and ask questions</li>
            <li>Use the AI assistant for HR and policy queries</li>
            <li>View your personal insights and FAQs</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ===========================================
#                ALL POLICIES
# ===========================================
elif page == "All Policies":
    st.title("📚 All Company Policies")
    files = [f for f in os.listdir(POLICY_DIR) if f.endswith(".pdf")]

    if not files:
        st.info("No policy files found.")
    else:
        selected = st.selectbox("Select a policy:", files)
        show_policy_card(os.path.join(POLICY_DIR, selected))

# ===========================================
#             UPLOAD OR CHOOSE
# ===========================================
elif page == "Upload or Choose & Ask":
    st.title("📤 Upload or Choose a Policy")

    col1, col2 = st.columns(2)
    with col1:
        uploaded = st.file_uploader("Upload Policy (Temporary)", type=["pdf"])
    with col2:
        files = [f for f in os.listdir(POLICY_DIR) if f.endswith(".pdf")]
        selected = st.selectbox("Choose Existing Policy", files if files else ["None"])

    chosen = uploaded if uploaded else (selected if selected!="None" else None)

    content = None
    if chosen:
        try:
            reader = PdfReader(chosen if uploaded else open(os.path.join(POLICY_DIR, selected),"rb"), strict=False)
            content = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        except:
            st.error("Could not read policy file.")

    if content:
        st.markdown("## 💬 Ask Questions About This Policy")
        q = st.text_input("Your question:")
        c1,c2 = st.columns(2)
        with c1: ask_btn = st.button("Ask AI")
        with c2: sum_btn = st.button("Summarize Policy")

        if ask_btn:
            ans = ask_ai(f"Policy:\n{content[:6000]}\n\nQuestion: {q}")
            st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {q}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='chat-bubble-bot'><b>AI:</b> {ans}</div>", unsafe_allow_html=True)
            save_query(selected if not uploaded else uploaded.name, q, ans)

        if sum_btn:
            sm = ask_ai(f"Summarize this policy in 5 points:\n{content}")
            st.markdown(f"<div class='chat-bubble-bot'><b>Summary:</b><br>{sm}</div>", unsafe_allow_html=True)

# ===========================================
#            ASK POLICY AI
# ===========================================
elif page == "Ask Policy AI":
    st.title("💬 General Policy AI Assistant")
    q = st.text_area("Ask your question:")
    if st.button("Ask"):
        ans = ask_ai(q)
        st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {q}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='chat-bubble-bot'><b>AI:</b> {ans}</div>", unsafe_allow_html=True)
        save_query("General", q, ans)

# ===========================================
#               ANALYTICS
# ===========================================
elif page == "My Analytics":
    st.title("📊 Your Policy Insights")
    df = pd.read_csv(QUERY_FILE)

    if df.empty:
        st.info("You haven’t asked any questions yet.")
    else:
        col1,col2 = st.columns(2)
        with col1: st.metric("Total Questions", len(df))
        with col2: st.metric("Unique Policies", df["context"].nunique())

        df["category"] = df["question"].apply(category_of)
        st.markdown("### 📌 Question Categories")
        st.bar_chart(df["category"].value_counts())

        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        st.markdown("### ⏰ When You Ask Questions")
        st.line_chart(df["hour"].value_counts().sort_index())

        st.markdown("### 🔥 Frequent Topics")
        wc = WordCloud(width=800, height=300, background_color="white", colormap="Purples") \
            .generate(" ".join(df["question"]))
        fig, ax = plt.subplots()
        ax.imshow(wc)
        ax.axis("off")
        st.pyplot(fig)

# ===========================================
#                    FAQ
# ===========================================
elif page == "My FAQs":
    st.title("❓ Frequently Asked Questions")
    df = pd.read_csv(QUERY_FILE)
    if df.empty:
        st.info("Ask some questions first!")
    else:
        bundle = "\n".join(df["question"])
        faqs = ask_ai(f"Create 5 short FAQs from:\n{bundle}")
        st.markdown(f"<div class='card'>{faqs}</div>", unsafe_allow_html=True)

# ===========================================
#             CONTACT & SUPPORT
# ===========================================
elif page == "Contact & Support":
    st.title("📞 Contact & Support – Escobar Consultancy")

    st.markdown("""
    <div class='card'>
        <h3>We're here to help!</h3>
        <p>If you need assistance regarding any policy or HR process, please reach out to the relevant department or regional POC below.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 🏢 Department-wise Contacts")

    departments = {
        "Human Resources (HR)": {"email": "hr@escobarconsultancy.in", "phone": "98234xxxxx"},
        "Finance & Payroll": {"email": "finance@escobarconsultancy.in", "phone": "98188xxxxx"},
        "IT Support": {"email": "itsupport@escobarconsultancy.in", "phone": "99777xxxxx"},
        "Admin & Facilities": {"email": "admin@escobarconsultancy.in", "phone": "91234xxxxx"},
        "Compliance & Legal": {"email": "compliance@escobarconsultancy.in", "phone": "99876xxxxx"},
    }

    for dept, info in departments.items():
        st.markdown(
            f"""
            <div class='card'>
                <h4>{dept}</h4>
                📧 Email: <b>{info['email']}</b><br>
                📞 Phone: <b>{info['phone']}</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("## 🌍 Region-wise Points of Contact (POCs)")

    regional_pocs = {
        "Maharashtra": {"name": "Rahul Deshmukh", "phone": "99345xxxxx", "email": "rahul.d@escobarconsultancy.in"},
        "Karnataka": {"name": "Sneha Ramesh", "phone": "99822xxxxx", "email": "sneha.r@escobarconsultancy.in"},
        "Tamil Nadu": {"name": "Arun Prakash", "phone": "98455xxxxx", "email": "arun.p@escobarconsultancy.in"},
        "Delhi NCR": {"name": "Priya Malhotra", "phone": "98760xxxxx", "email": "priya.m@escobarconsultancy.in"},
        "Telangana": {"name": "Varun Reddy", "phone": "99001xxxxx", "email": "varun.r@escobarconsultancy.in"}
    }

    for region, info in regional_pocs.items():
        st.markdown(
            f"""
            <div class='card'>
                <h4>📍 {region}</h4>
                <b>{info['name']}</b><br>
                📞 {info['phone']}<br>
                📧 {info['email']}
            </div>
            """,
            unsafe_allow_html=True
        )