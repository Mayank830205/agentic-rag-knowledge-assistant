"""
FastAPI Application Entry Point.
Configures FastAPI app, CORS middleware, structured logging, and lifecycle events.
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.api.routes import router
from backend.rag.vectorstore import get_vectorstore_doc_count
from backend.rag.ingestion import ingest_pdf_to_vectorstore

# Configure standard logging
logging.basicConfig(
    level=settings.LOG_LEVEL.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("agentrag.backend")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle management."""
    logger.info("Initializing AgentRAG Enterprise Knowledge Assistant Backend...")
    
    # Ensure necessary storage directories exist
    os.makedirs(os.path.abspath(settings.DATA_DOCUMENTS_DIRECTORY), exist_ok=True)
    os.makedirs(os.path.abspath(settings.CHROMA_PERSIST_DIRECTORY), exist_ok=True)

    # Auto-index sample company policy document if vectorstore is empty
    doc_count = get_vectorstore_doc_count()
    sample_pdf = os.path.join(settings.DATA_DOCUMENTS_DIRECTORY, "sample_company_policies.pdf")

    if doc_count == 0 and os.path.exists(sample_pdf):
        logger.info(f"Vector store is empty. Auto-indexing initial sample document: {sample_pdf}")
        try:
            res = ingest_pdf_to_vectorstore(sample_pdf)
            logger.info(f"Auto-indexed sample document: {res}")
        except Exception as e:
            logger.warning(f"Failed to auto-index sample document on startup: {e}")
    else:
        logger.info(f"Vector store ready with {doc_count} document chunks.")

    yield
    logger.info("Shutting down AgentRAG Backend.")

app = FastAPI(
    title="AgentRAG – Enterprise Knowledge Assistant",
    description="Intelligent enterprise assistant routing queries between Document RAG and MySQL Database using LangGraph and Gemini.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local Streamlit frontend and external consumers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
