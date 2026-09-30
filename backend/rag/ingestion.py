"""
PDF Document Ingestion Pipeline.
Handles PDF extraction, recursive chunking, metadata enrichment, and vector storage.
"""
import os
import logging
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from backend.rag.vectorstore import get_vectorstore

logger = logging.getLogger(__name__)

def load_and_chunk_pdf(file_path: str) -> List[Document]:
    """
    Loads a PDF file and splits it into semantic chunks with 1-indexed page metadata.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    logger.info(f"Loading PDF: {file_path}")
    loader = PyPDFLoader(file_path)
    raw_pages = loader.load()

    if not raw_pages:
        raise ValueError(f"No readable text extracted from {file_path}")

    # Text splitter configured with sensible chunking for enterprise documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
        separators=["\n\n", "\n", "• ", ". ", " ", ""]
    )

    chunks = text_splitter.split_documents(raw_pages)
    filename = os.path.basename(file_path)

    # Standardize metadata across chunks
    for chunk in chunks:
        # PyPDFLoader returns 0-indexed page in metadata 'page'
        raw_page = chunk.metadata.get("page", 0)
        chunk.metadata["page"] = int(raw_page) + 1  # 1-indexed for user readability
        chunk.metadata["source"] = filename

    logger.info(f"Processed {len(raw_pages)} pages into {len(chunks)} chunks for {filename}")
    return chunks

def ingest_pdf_to_vectorstore(file_path: str) -> Dict[str, Any]:
    """
    Ingests PDF chunks into persistent ChromaDB.
    Returns ingestion summary metrics.
    """
    chunks = load_and_chunk_pdf(file_path)
    if not chunks:
        return {"filename": os.path.basename(file_path), "chunks_added": 0, "pages": 0}

    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)

    # Derive unique page count from chunks
    pages = len(set(c.metadata.get("page", 1) for c in chunks))

    return {
        "filename": os.path.basename(file_path),
        "chunks_added": len(chunks),
        "pages": pages
    }
