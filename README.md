# Internal Project 1 for EY GDS AIML Training

## Escobar Consultancy - Policy Insights AI Dashboard 

An AI-powered internal policy portal designed for employees to easily access, understand, and navigate company policies.  
Built using **Streamlit**, **Groq Llama 3.1 (free model)**, this dashboard provides:

- 📚 A central policy library  
- 🤖 AI-based policy Q&A  
- 📤 Upload-your-own policy chat  
- 📊 Personal analytics  
- ❓ Smart FAQ generation  
- 📞 Department & regional contact details  

This project is created for academic and demonstration purposes using the fictional company **Escobar Consultancy**.

---

## 🚀 Features

### **1. Home Dashboard**
- Overview of all features  
- Easy navigation  

### **2. All Policies**
- Displays all official policy PDFs  
- Downloadable directly  
- Pulled from the `/policies` folder  

### **3. Upload or Choose & Ask**
- Upload any PDF temporarily  
- OR choose a policy from library  
- AI answers based on **that document’s content**  
- Fast & accurate thanks to **Groq’s Llama 3.1 model**

### **4. Ask Policy AI**
- Ask general HR or policy-related questions  
- AI gives conversational, HR-safe responses  

### **5. My Analytics**
- Total questions asked  
- Unique policy usage  
- Word cloud of topics  
- Visual insights  

### **6. My FAQs**
- AI-generated FAQs based on your own queries  

### **7. Contact & Support**
- Department-wise support  
- Region-wise POCs  
- Masked phone numbers  
- Fictional email domain  

---

## 🤖 AI Model Used

This dashboard uses:

### **Model:**  
`llama-3.1-8b-instant` (Groq API - Free)

### **Why Groq?**
- Lightning fast inference  
- Free tier available  
- Perfect for real-time Q&A  
- Lightweight 8B model with strong accuracy  

### **How AI Works**
There are two modes:

#### **1️⃣ General Assistant Mode**
For HR queries, general policy help.

#### **2️⃣ Policy-Aware Mode (RAG-lite)**
- PDF is read using `pypdf`  
- Extracted text is injected into the AI prompt  
- AI answers based on that document  

Not full RAG, but efficient, fast, and accurate for policies.

---

## 📂 Project Structure
project_root/ 
  ├─ app.py 
  ├─ policies/           # stored PDFs 
  ├─ queries.csv         # auto-created 
  ├─ .env                # contains GROQ_API_KEY 
  └─ requirements.txt
