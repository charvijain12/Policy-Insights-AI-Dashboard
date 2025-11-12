import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from datetime import datetime
from groq import Groq
import PyPDF2

# Load API key
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=groq_api_key)

# CSV for storing queries
QUERY_FILE = "queries.csv"
if not os.path.exists(QUERY_FILE):
    pd.DataFrame(columns=["timestamp", "question", "answer"]).to_csv(QUERY_FILE, index=False)

# Streamlit setup
st.set_page_config(page_title="Policy Insights AI Dashboard", layout="wide", page_icon="🧠")

# Sidebar Navigation
st.sidebar.title("🧭 Dashboard Navigation")
page = st.sidebar.radio(
    "Choose a tab:",
    ["💬 Chat & Upload", "📊 Analytics", "🔥 Policy Summary", "💡 Insights & Recommendations", "📞 Contacts"]
)

# --- Helper Functions ---
def save_query(question, answer):
    df = pd.read_csv(QUERY_FILE)
    new_row = pd.DataFrame([[datetime.now(), question, answer]], columns=["timestamp", "question", "answer"])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(QUERY_FILE, index=False)

def load_queries():
    return pd.read_csv(QUERY_FILE)

def ask_ai(prompt):
    """Use Groq free model for responses"""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Groq’s free & fast model
            messages=[
                {"role": "system", "content": "You are a helpful and knowledgeable HR policy assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --- TAB 1: Chat & Upload ---
if page == "💬 Chat & Upload":
    st.title("💬 Policy Chat Assistant")
    st.write("Upload a company policy document (PDF or TXT) and ask HR or compliance-related questions.")

    uploaded_file = st.file_uploader("📄 Upload Policy Document", type=["txt", "pdf"])
    policy_text = ""

    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            policy_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        else:
            policy_text = uploaded_file.read().decode("utf-8")
        st.success("✅ Document uploaded successfully!")

    question = st.text_input("Ask a policy-related question:")
    if st.button("Ask"):
        if uploaded_file and question.strip():
            with st.spinner("Thinking..."):
                answer = ask_ai(f"Policy Document:\n{policy_text[:4000]}\n\nQuestion:\n{question}")
                st.markdown(f"**Answer:** {answer}")
                save_query(question, answer)
        elif not uploaded_file:
            st.warning("Please upload a policy document first.")
        else:
            st.warning("Please enter a question.")

# --- TAB 2: Analytics ---
elif page == "📊 Analytics":
    st.title("📊 Policy Query Analytics")

    df = load_queries()
    if not df.empty:
        st.write(f"Total Queries: {len(df)}")

        # --- Hot Questions Detection ---
        question_counts = df["question"].value_counts().reset_index()
        question_counts.columns = ["question", "count"]

        if not question_counts.empty:
            st.subheader("🔥 Hot & Frequently Asked Questions")
            st.table(question_counts.head(5))

            fig = px.bar(question_counts.head(10), x="question", y="count",
                         title="Top 10 Most Asked Questions", text_auto=True)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("🕓 Recent Questions")
        st.dataframe(df.sort_values("timestamp", ascending=False).head(10))
    else:
        st.info("No queries found yet. Ask something in the Chat tab first!")

# --- TAB 3: Policy Summary ---
elif page == "🔥 Policy Summary":
    st.title("🔥 AI Policy Summary")
    st.write("Upload your policy and get a short summary to understand it better.")

    upload_summary = st.file_uploader("📄 Upload Policy (PDF or TXT)", type=["pdf", "txt"], key="summary_upload")
    if upload_summary:
        if upload_summary.type == "application/pdf":
            reader = PyPDF2.PdfReader(upload_summary)
            policy_text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        else:
            policy_text = upload_summary.read().decode("utf-8")

        with st.spinner("Summarizing your document..."):
            summary = ask_ai(f"Summarize the following company policy in 5 bullet points:\n{policy_text[:4000]}")
        st.markdown("### 🧾 Summary:")
        st.write(summary)

# --- TAB 4: Insights & Recommendations ---
elif page == "💡 Insights & Recommendations":
    st.title("💡 HR Insights & Recommendations")
    df = load_queries()

    if not df.empty:
        with st.spinner("Generating insights from employee queries..."):
            combined_queries = "\n".join(df['question'].tolist())
            insights = ask_ai(
                f"Based on these employee questions about HR policies:\n{combined_queries}\n\n"
                f"Provide insights and actionable recommendations for management to improve clarity or communication."
            )
        st.markdown("### 📈 AI-Generated Insights:")
        st.write(insights)
    else:
        st.info("No queries yet — ask questions in the Chat tab to generate insights!")

# --- TAB 5: Contacts ---
elif page == "📞 Contacts":
    st.title("📞 Department Contacts")
    st.write("Reach out to departments for further clarifications.")

    contact_data = {
        "Department": ["HR", "Finance", "Legal", "IT Support", "Admin"],
        "Email": [
            "hr@company.in",
            "finance@company.in",
            "legal@company.in",
            "itsupport@company.in",
            "admin@company.in"
        ],
        "Phone": ["+91 9876543210", "+91 9823456789", "+91 9812345678", "+91 9800011223", "+91 9700044455"]
    }

    st.table(pd.DataFrame(contact_data))
    st.success("For urgent policy-related issues, contact the HR department.")