"""
ChromaDB Vector Store Module.
Manages persistent Chroma vector database initialization and retriever creation.
"""
import os
import logging
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from backend.config import settings

logger = logging.getLogger(__name__)

_vectorstore = None
_embeddings = None

def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Returns singleton Gemini embeddings client."""
    global _embeddings
    if _embeddings is None:
        api_key = settings.get_gemini_api_key()
        _embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            google_api_key=api_key
        )
    return _embeddings

def get_vectorstore() -> Chroma:
    """Returns singleton Chroma vector store instance."""
    global _vectorstore
    if _vectorstore is None:
        persist_dir = os.path.abspath(settings.CHROMA_PERSIST_DIRECTORY)
        os.makedirs(persist_dir, exist_ok=True)
        embeddings = get_embeddings()
        _vectorstore = Chroma(
            collection_name="agentrag_documents",
            embedding_function=embeddings,
            persist_directory=persist_dir
        )
    return _vectorstore

def get_retriever(k: int = 4):
    """Returns retriever with top-k similarity search."""
    vs = get_vectorstore()
    return vs.as_retriever(search_kwargs={"k": k})

def get_vectorstore_doc_count() -> int:
    """Returns number of document chunks currently indexed in Chroma."""
    try:
        vs = get_vectorstore()
        collection = vs._collection
        return collection.count() if collection else 0
    except Exception as e:
        logger.warning(f"Could not retrieve Chroma document count: {e}")
        return 0
