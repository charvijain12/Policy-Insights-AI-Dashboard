import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
import PyPDF2

# --- Load API Key ---
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

# --- File Setup ---
QUERY_FILE = "queries.csv"
POLICY_DIR = "policies"
os.makedirs(POLICY_DIR, exist_ok=True)

if not os.path.exists(QUERY_FILE):
    pd.DataFrame(columns=["timestamp", "policy", "question", "answer"]).to_csv(QUERY_FILE, index=False)

# --- Streamlit Page Config ---
st.set_page_config(page_title="Policy Insights Dashboard", page_icon="🏢", layout="wide")

# --- Helper Functions ---
def save_query(policy, question, answer):
    df = pd.read_csv(QUERY_FILE)
    new_row = pd.DataFrame([[datetime.now(), policy, question, answer]], columns=["timestamp", "policy", "question", "answer"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(QUERY_FILE, index=False)

def load_queries():
    return pd.read_csv(QUERY_FILE)

def ask_ai(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an HR policy assistant that helps employees understand company policies clearly and politely."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def display_pdf_download_button(file_path, label):
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{os.path.basename(file_path)}">📥 {label}</a>'
        st.markdown(href, unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.title("🏢 Policy Insights AI Dashboard")
st.sidebar.caption("For Employees")

page = st.sidebar.radio(
    "Navigate:",
    ["📚 All Policies", "📤 Upload or Choose Policy", "💬 Ask Policy AI", "📊 My Analytics", "❓ My FAQs", "🎨 Settings"]
)

# --- KPI Cards (Top) ---
def kpi_cards():
    st.markdown("### 📈 Dashboard Overview")
    df = load_queries()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Questions Asked", len(df))
    unique_policies = len(df["policy"].unique()) if not df.empty else 0
    col2.metric("Policies Referenced", unique_policies)
    col3.metric("Last Query", df['timestamp'].max() if not df.empty else "—")

# --- TAB 1: All Policies ---
if page == "📚 All Policies":
    st.title("📚 All Company Policies")
    st.write("View and download the latest company policies below:")

    if not os.listdir(POLICY_DIR):
        st.info("No policy files found. Please upload some first.")
    else:
        for file in os.listdir(POLICY_DIR):
            if file.endswith(".pdf"):
                st.write(f"📄 **{file.replace('_', ' ').title()}**")
                display_pdf_download_button(os.path.join(POLICY_DIR, file), "Download Policy")

# --- TAB 2: Upload or Choose Policy ---
elif page == "📤 Upload or Choose Policy":
    st.title("📤 Upload or Choose Policy")
    st.write("Upload a new policy or pick one from the knowledge base below.")

    uploaded_file = st.file_uploader("Upload new policy PDF", type=["pdf"])
    if uploaded_file:
        save_path = os.path.join(POLICY_DIR, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ Policy '{uploaded_file.name}' uploaded successfully!")

    st.subheader("📚 Choose from Existing Policies:")
    files = [f for f in os.listdir(POLICY_DIR) if f.endswith(".pdf")]
    if files:
        selected_policy = st.selectbox("Select a Policy", files)
        st.info(f"You selected: **{selected_policy}**")
    else:
        st.warning("No policies found yet. Upload one above.")

# --- TAB 3: Ask Policy AI ---
elif page == "💬 Ask Policy AI":
    st.title("💬 Ask a Question About a Policy")
    files = [f for f in os.listdir(POLICY_DIR) if f.endswith(".pdf")]
    selected_policy = st.selectbox("Select Policy Document", files if files else ["(No files available)"])

    if selected_policy and selected_policy != "(No files available)":
        path = os.path.join(POLICY_DIR, selected_policy)
        reader = PyPDF2.PdfReader(path)
        policy_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

        question = st.text_input("What would you like to know?")
        if st.button("Ask AI"):
            if question.strip():
                with st.spinner("Thinking..."):
                    answer = ask_ai(f"Policy: {selected_policy}\nContent:\n{policy_text[:4000]}\nQuestion:\n{question}")
                    st.markdown(f"**Answer:** {answer}")
                    save_query(selected_policy, question, answer)
            else:
                st.warning("Please enter a question.")

# --- TAB 4: My Analytics ---
elif page == "📊 My Analytics":
    st.title("📊 My Policy Insights")
    kpi_cards()
    df = load_queries()

    if not df.empty:
        question_counts = df["question"].value_counts().reset_index()
        question_counts.columns = ["Question", "Count"]

        fig = px.bar(question_counts.head(10), x="Question", y="Count", title="🔥 Most Common Questions")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("You haven't asked any questions yet.")

# --- TAB 5: My FAQs ---
elif page == "❓ My FAQs":
    st.title("❓ Frequently Asked Questions")
    df = load_queries()
    if not df.empty:
        st.write("Based on what employees often ask:")
        questions = "\n".join(df["question"].tolist())
        with st.spinner("Generating FAQs..."):
            faqs = ask_ai(f"From these employee questions, generate 5 clear FAQ Q&A pairs:\n{questions}")
        st.markdown(f"### FAQs:\n{faqs}")
    else:
        st.info("No questions asked yet — start in the Ask tab.")

# --- TAB 6: Settings / UI Enhancements ---
elif page == "🎨 Settings":
    st.title("🎨 UI & Dashboard Settings")
    st.write("Toggle theme or personalize your dashboard.")
    dark_mode = st.toggle("🌙 Dark Mode", value=False)
    if dark_mode:
        st.success("Dark Mode activated!")
    else:
        st.info("Light Mode active.")
    st.caption("More personalization options coming soon ✨")