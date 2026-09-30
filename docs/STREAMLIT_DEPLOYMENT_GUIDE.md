# Streamlit Deployment Guide — AgentRAG

This step-by-step guide explains how to deploy **AgentRAG** to **Streamlit Community Cloud** (100% free hosting with public URL).

The project is built with dual-mode flexibility:
- **Method 1: Instant 2-Minute Deployment (Zero External Infrastructure)** — Runs Streamlit with the embedded LangGraph + ChromaDB engine and resilient relational database.
- **Method 2: Full Decoupled Enterprise Deployment** — Hosts FastAPI on Render (free) and Streamlit on Streamlit Cloud communicating via HTTP REST APIs.

---

## 🚀 Method 1: Instant 2-Minute Streamlit Cloud Deployment (Recommended)

This method lets you deploy the entire application to Streamlit Cloud immediately without needing to set up an external server or database.

### Step 1: Push Code to GitHub
Your code is already on GitHub:
👉 `https://github.com/Mayank830205/agentic-rag-knowledge-assistant`

### Step 2: Sign in to Streamlit Community Cloud
1. Open your browser and go to: **[share.streamlit.io](https://share.streamlit.io/)**
2. Click **Continue with GitHub** and authorize Streamlit.

### Step 3: Create a New App
1. On your Streamlit dashboard, click the blue **"Create app"** button.
2. Select **"I already have an app"** (or pick repository from GitHub).
3. Fill in the repository details:
   - **Repository:** `Mayank830205/agentic-rag-knowledge-assistant`
   - **Branch:** `main`
   - **Main file path:** `frontend/app.py`
   - **App URL:** (Optional: customize your custom subdomain, e.g. `agentrag-assistant.streamlit.app`)

### Step 4: Add Your Secrets (Crucial Step!)
1. Before clicking Deploy, click **"Advanced settings"** at the bottom of the form (or go to App Settings ➔ **Secrets** after creating).
2. In the **Secrets** text box, paste:
   ```toml
   GEMINI_API_KEY = "your_actual_gemini_api_key_here"
   ```
   *(Replace with your Google Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey))*
3. Click **Save**.

### Step 5: Click "Deploy!"
1. Click the **"Deploy"** button.
2. Streamlit Cloud will automatically:
   - Provision a Linux container.
   - Install dependencies from `requirements.txt`.
   - Start the Streamlit application.
3. Within 1–2 minutes, your app is live at `https://<your-app-name>.streamlit.app`! 🎉

---

## 🌐 Method 2: Full Decoupled Enterprise Deployment (FastAPI on Render + Streamlit Cloud)

If you want to demonstrate the full decoupled REST architecture live in an interview (Streamlit ➔ HTTP ➔ FastAPI ➔ LangGraph):

### Step 1: Deploy FastAPI Backend on Render.com (Free)
1. Go to **[Render.com](https://render.com/)** and sign up with GitHub.
2. Click **New +** ➔ **Web Service**.
3. Connect your repository: `Mayank830205/agentic-rag-knowledge-assistant`.
4. Configure the settings:
   - **Name:** `agentrag-backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** `Free`
5. Under **Environment Variables**, add:
   - `GEMINI_API_KEY` = `your_gemini_api_key`
   - `LLM_MODEL` = `gemini-2.5-flash`
   - `EMBEDDING_MODEL` = `gemini-embedding-001`
   - *(Optional: If using Cloud MySQL like Aiven/TiDB, add `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`)*
6. Click **Deploy Web Service**.
7. Once deployed, copy your backend URL (e.g., `https://agentrag-backend.onrender.com`).
8. Verify it works by opening: `https://agentrag-backend.onrender.com/health` in your browser.

### Step 2: Connect Streamlit Cloud to Your Render Backend
1. Go to your Streamlit Cloud app dashboard: **[share.streamlit.io](https://share.streamlit.io/)**.
2. Click the three dots (⋮) next to your app ➔ **Settings** ➔ **Secrets**.
3. Add the `BACKEND_URL` secret:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key"
   BACKEND_URL = "https://agentrag-backend.onrender.com"
   ```
4. Click **Save**.
5. Streamlit will instantly refresh. In the sidebar, you will see:
   `Mode: DECOUPLED (HTTP)`
   `Backend: HEALTHY`

---

## 🧪 Testing Your Live Streamlit Cloud Deployment

Once deployed, test both paths live:

### 1. Document RAG Test:
1. In the sidebar, upload the provided sample PDF:  
   `data/documents/sample_company_policies.pdf`
2. Click **"2. Process Document"**.
3. Ask in the query box:
   - *"What is the company leave policy?"* ➔ Verifies RAG answer with page citations.
   - *"What are the core working hours?"* ➔ Verifies working hours retrieval.
   - *"What is the pet insurance policy?"* ➔ Verifies anti-hallucination guardrail (`"I could not find this information in the available documents."`).

### 2. Database Text-to-SQL Test:
1. Ask in the query box:
   - *"How many employees are in Engineering?"* ➔ Verifies SQL routing (`Route: SQL`) and counts 8 employees.
   - *"What is the average salary?"* ➔ Verifies SQL average aggregation (`102400.00`).
   - *"How many employees joined in 2025?"* ➔ Verifies date filter (`5 employees`).
2. Expand the **"🔍 Inspected SQL Query"** box to show interviewers the generated SELECT query!

---

## 🛠️ Troubleshooting & FAQs

### Q1: My Streamlit app shows "Backend offline at http://localhost:8000"
**Fix:** In Streamlit Cloud, `localhost` does not exist. Open your app's **Settings ➔ Secrets** and make sure you have added:
```toml
GEMINI_API_KEY = "your_actual_key"
```
Once `GEMINI_API_KEY` is present in Secrets, the app automatically runs in direct Standalone Cloud Mode!

### Q2: How do I change secrets after deploying?
**Fix:** On [share.streamlit.io](https://share.streamlit.io/), click the **⋮ (three dots)** menu next to your running app ➔ **Settings** ➔ **Secrets**, edit the text, and click **Save**. The app restarts automatically with the new secrets.

### Q3: Why does Render backend take 30-50 seconds on the first request?
**Fix:** Free instances on Render spin down after 15 minutes of inactivity (cold start). The first request wakes the server up; subsequent requests respond in under 1 second.
