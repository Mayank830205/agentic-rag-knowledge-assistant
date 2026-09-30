"""
AgentRAG - Enterprise Knowledge Assistant
Streamlit Frontend Application.

Supports two operational modes:
1. Standard Decoupled Mode (Recommended): Communicates via HTTP with FastAPI backend.
2. Resilient Cloud Standalone Mode: Executes in-process when deployed directly to Streamlit Community Cloud.
"""
import os
import tempfile
import requests
import streamlit as st

# Application Configuration: Read from environment or Streamlit secrets
BACKEND_URL = os.getenv("BACKEND_URL")
if not BACKEND_URL and hasattr(st, "secrets") and "BACKEND_URL" in st.secrets:
    BACKEND_URL = str(st.secrets["BACKEND_URL"])
if not BACKEND_URL:
    BACKEND_URL = "http://localhost:8000"
BACKEND_URL = BACKEND_URL.rstrip("/")

# Get Gemini API key if present in secrets
if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
    os.environ["GEMINI_API_KEY"] = str(st.secrets["GEMINI_API_KEY"])

st.set_page_config(
    page_title="AgentRAG – Enterprise Knowledge Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1A365D;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4A5568;
        margin-bottom: 20px;
    }
    .badge-rag {
        background-color: #EBF8FF;
        color: #2B6CB0;
        padding: 5px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid #BEE3F8;
    }
    .badge-sql {
        background-color: #FEFCBF;
        color: #975A16;
        padding: 5px 12px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid #FAF089;
    }
    .answer-box {
        background-color: #F7FAFC;
        border-left: 4px solid #3182CE;
        padding: 16px;
        border-radius: 6px;
        font-size: 1.05rem;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .source-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Helper: Fetch Backend Health
def get_backend_health():
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=2)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None

# Check if direct in-process execution is available as cloud fallback
def is_standalone_ready():
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        api_key = str(st.secrets["GEMINI_API_KEY"])
    return bool(api_key)

# Helper: Upload PDF (HTTP or Standalone fallback)
def upload_pdf_document(uploaded_file, use_standalone=False):
    if not use_standalone:
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            resp = requests.post(f"{BACKEND_URL}/documents/upload", files=files, timeout=60)
            return resp.status_code, resp.json()
        except Exception as e:
            return 500, {"detail": str(e)}
    else:
        # In-process standalone execution
        try:
            from backend.rag.ingestion import ingest_pdf_to_vectorstore
            os.makedirs("data/documents", exist_ok=True)
            save_path = os.path.join("data", "documents", uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            res = ingest_pdf_to_vectorstore(save_path)
            return 201, {
                "message": "Document indexed successfully in standalone mode.",
                "filename": res["filename"],
                "chunks_ingested": res["chunks_added"],
                "total_pages": res["pages"]
            }
        except Exception as e:
            return 500, {"detail": f"Standalone ingestion error: {str(e)}"}

# Helper: Send Chat Query (HTTP or Standalone fallback)
def send_chat_query(question_text, use_standalone=False):
    if not use_standalone:
        try:
            resp = requests.post(
                f"{BACKEND_URL}/chat",
                json={"question": question_text},
                timeout=60
            )
            return resp.status_code, resp.json()
        except Exception as e:
            return 500, {"detail": str(e)}
    else:
        # In-process standalone execution
        try:
            from backend.agent.graph import run_agent_workflow
            final_state = run_agent_workflow(question_text)
            return 200, {
                "answer": final_state.get("answer", "No answer generated."),
                "route": final_state.get("route", "rag"),
                "sources": final_state.get("sources", []),
                "sql_query": final_state.get("sql_query") or None
            }
        except Exception as e:
            return 500, {"detail": f"Standalone processing error: {str(e)}"}

# Determine active execution mode
health_data = get_backend_health()
has_standalone = is_standalone_ready()
is_standalone_mode = (health_data is None) and has_standalone

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    
    # System Status Monitor
    st.subheader("System Health")
    if health_data:
        st.success(f"Mode: DECOUPLED (HTTP)")
        st.write(f"• **Backend**: `{health_data.get('status', 'online').upper()}`")
        st.write(f"• **Database**: `{health_data.get('database')}`")
        st.write(f"• **ChromaDB**: `{health_data.get('vector_store')}`")
        st.write(f"• **Indexed Chunks**: `{health_data.get('documents_count', 0)}`")
    elif is_standalone_mode:
        st.info("Mode: STANDALONE CLOUD")
        st.caption("Running in-process on Streamlit Cloud with embedded LangGraph & ChromaDB.")
        st.write("• **Backend**: `In-Process Engine`")
        st.write("• **Database**: `Resilient Relational Fallback`")
        st.write("• **Gemini API**: `Configured & Ready`")
    else:
        st.error(f"Backend offline at `{BACKEND_URL}`.")
        st.warning("Please configure `GEMINI_API_KEY` in Streamlit Cloud Secrets (or start local FastAPI).")

    st.divider()

    # Step 1 & 2: PDF Upload & Processing
    st.subheader("1. Document Ingestion")
    uploaded_pdf = st.file_uploader(
        "Upload Company Policy PDF",
        type=["pdf"],
        help="Upload an enterprise policy or handbook in PDF format."
    )

    if st.button("2. Process Document", type="primary", use_container_width=True):
        if uploaded_pdf is not None:
            with st.spinner("Chunking, embedding, and indexing into ChromaDB..."):
                status_code, upload_res = upload_pdf_document(uploaded_pdf, use_standalone=is_standalone_mode)
                if status_code in (200, 201):
                    st.success(f"Indexed **{upload_res.get('chunks_ingested')}** chunks from **{upload_res.get('total_pages')}** pages!")
                    st.rerun()
                else:
                    st.error(f"Upload failed: {upload_res.get('detail', 'Unknown error')}")
        else:
            st.warning("Please select a PDF file first.")

    st.divider()

    # Sample Questions Helper
    st.subheader("💡 Example Questions")
    st.caption("Click any question to prefill the query box:")
    
    sample_questions = [
        "What is the company's leave policy?",
        "What are the working hours?",
        "What is the refund policy?",
        "How many employees are in Engineering?",
        "What is the average salary?",
        "How many employees joined in 2025?"
    ]

    for sq in sample_questions:
        if st.button(sq, key=f"btn_{sq}", use_container_width=True):
            st.session_state["prefill_query"] = sq

# --- MAIN PAGE CONTENT ---
st.markdown('<div class="main-title">AgentRAG</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Enterprise Knowledge Assistant & Intelligent Query Router</div>', unsafe_allow_html=True)

# Step 3: Ask Question
prefilled_val = st.session_state.get("prefill_query", "")

with st.form("query_form"):
    user_question = st.text_input(
        "3. Ask Question:",
        value=prefilled_val,
        placeholder="e.g., 'What is the leave policy?' or 'What is the average salary?'"
    )
    submit_btn = st.form_submit_button("Submit Question", type="primary", use_container_width=False)

if submit_btn and user_question:
    if "prefill_query" in st.session_state:
        del st.session_state["prefill_query"]

    with st.spinner("Routing through LangGraph and generating response..."):
        status_code, chat_res = send_chat_query(user_question, use_standalone=is_standalone_mode)

    if status_code == 200:
        route = chat_res.get("route", "rag").lower()
        answer = chat_res.get("answer", "")
        sources = chat_res.get("sources", [])
        sql_query = chat_res.get("sql_query")

        st.markdown("---")
        
        # 5. Display Route
        col_route, col_meta = st.columns([1, 3])
        with col_route:
            if route == "rag":
                st.markdown('<span class="badge-rag">📄 Route: RAG (Unstructured Document)</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge-sql">🗄️ Route: SQL (MySQL / Relational Database)</span>', unsafe_allow_html=True)

        # 4. Display Answer
        st.subheader("4. Generated Answer")
        st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)

        # SQL Query Inspection
        if route == "sql" and sql_query:
            with st.expander("🔍 Inspected SQL Query (Validated SELECT)", expanded=False):
                st.code(sql_query, language="sql")

        # 6. Display Sources (for RAG)
        if route == "rag":
            st.subheader("6. Source Documents")
            if sources:
                for idx, src in enumerate(sources, 1):
                    doc_name = src.get("source", "Document")
                    page_num = src.get("page", "N/A")
                    content_excerpt = src.get("content", "")

                    with st.container():
                        st.markdown(f"""
                        <div class="source-card">
                            <strong>Source #{idx}:</strong> <code>{doc_name}</code> (Page: <b>{page_num}</b>)<br/>
                            <div style="margin-top: 6px; color: #4A5568; font-size: 0.95rem;">
                                <em>"{content_excerpt}"</em>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No document sources cited.")

    else:
        err_msg = chat_res.get("detail", "Failed to retrieve response from backend.")
        st.error(f"Error ({status_code}): {err_msg}")
elif submit_btn and not user_question:
    st.warning("Please enter a question before submitting.")
