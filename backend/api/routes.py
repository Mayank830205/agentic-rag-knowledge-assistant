"""
FastAPI Route Handlers.
Exposes endpoints for Health Check, Document Upload, and LangGraph Chat Querying.
"""
import os
import shutil
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from backend.config import settings
from backend.models.schemas import ChatRequest, ChatResponse, HealthResponse, UploadResponse, DocumentSource
from backend.database.connection import check_database_connection
from backend.rag.vectorstore import get_vectorstore_doc_count
from backend.rag.ingestion import ingest_pdf_to_vectorstore
from backend.agent.graph import run_agent_workflow

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the operational status of the API, MySQL database, and ChromaDB vector store."
)
async def health_check():
    """Verifies MySQL database and ChromaDB availability."""
    db_ok, db_msg = check_database_connection()
    doc_count = get_vectorstore_doc_count()

    db_status = "connected" if db_ok else f"disconnected ({db_msg})"
    vector_status = "ready" if os.path.exists(settings.CHROMA_PERSIST_DIRECTORY) else "initializing"
    overall_status = "healthy" if db_ok else "degraded"

    return HealthResponse(
        status=overall_status,
        database=db_status,
        vector_store=vector_status,
        documents_count=doc_count
    )

@router.post(
    "/documents/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and process PDF",
    description="Uploads a PDF, extracts text, chunks it, generates embeddings, and saves into ChromaDB."
)
async def upload_document(file: UploadFile = File(...)):
    """Uploads and ingests a PDF file into the vector store."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents (.pdf) are supported."
        )

    storage_dir = os.path.abspath(settings.DATA_DOCUMENTS_DIRECTORY)
    os.makedirs(storage_dir, exist_ok=True)
    file_path = os.path.join(storage_dir, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Saved uploaded file to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save file {file.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}"
        )

    try:
        ingestion_result = ingest_pdf_to_vectorstore(file_path)
    except Exception as e:
        logger.error(f"Ingestion failed for {file.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and index PDF: {str(e)}"
        )

    return UploadResponse(
        message="Document successfully processed and indexed into vector database.",
        filename=ingestion_result["filename"],
        chunks_ingested=ingestion_result["chunks_added"],
        total_pages=ingestion_result["pages"]
    )

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat query",
    description="Processes user questions through LangGraph, routing to either RAG or SQL."
)
async def chat_endpoint(request: ChatRequest):
    """Processes user queries via LangGraph routing."""
    question = request.question.strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty."
        )

    try:
        result_state = run_agent_workflow(question)
    except Exception as e:
        logger.error(f"Error processing question '{question}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

    sources = [
        DocumentSource(
            source=s.get("source", "Unknown"),
            page=s.get("page"),
            content=s.get("content", "")
        )
        for s in result_state.get("sources", [])
    ]

    return ChatResponse(
        answer=result_state.get("answer", "No answer could be generated."),
        route=result_state.get("route", "rag"),
        sources=sources,
        sql_query=result_state.get("sql_query") or None
    )
