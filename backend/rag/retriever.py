"""
RAG Retrieval and Grounded Answer Generation Module.
Enforces strict anti-hallucination guardrails and extracts document source citations.
"""
import logging
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import settings
from backend.rag.vectorstore import get_retriever

logger = logging.getLogger(__name__)

NOT_FOUND_MESSAGE = "I could not find this information in the available documents."

RAG_PROMPT_TEMPLATE = """You are an enterprise knowledge assistant answering questions based strictly on the provided company documents.

STRICT INSTRUCTIONS:
1. Answer the question relying ONLY on the provided context excerpts below.
2. If the answer cannot be determined directly from the provided context, respond EXACTLY with:
"I could not find this information in the available documents."
3. Do NOT guess, extrapolate, or bring in outside knowledge.
4. Keep your answer factual, professional, and directly grounded in the text.

Context:
{context}

Question:
{question}

Answer:"""

prompt = PromptTemplate(
    template=RAG_PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)

def format_docs_context(docs: List[Document]) -> str:
    """Formats retrieved chunks into clean delimited text for LLM prompt."""
    parts = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown Document")
        page = doc.metadata.get("page", 1)
        parts.append(f"[Excerpt {i} | Source: {source}, Page: {page}]\n{doc.page_content.strip()}")
    return "\n\n".join(parts)

def extract_sources(docs: List[Document]) -> List[Dict[str, Any]]:
    """Extracts structured source citations for API response and UI display."""
    sources = []
    seen = set()
    for doc in docs:
        src = doc.metadata.get("source", "Unknown Document")
        page = doc.metadata.get("page", 1)
        key = (src, page, doc.page_content[:60])
        if key not in seen:
            seen.add(key)
            sources.append({
                "source": src,
                "page": page,
                "content": doc.page_content.strip()
            })
    return sources

def query_rag_pipeline(question: str) -> Tuple[str, str, List[Dict[str, Any]]]:
    """
    Retrieves document chunks from ChromaDB and generates a grounded response.
    Returns:
        (answer: str, context_str: str, sources: List[dict])
    """
    retriever = get_retriever(k=4)
    docs = retriever.invoke(question)

    if not docs:
        return NOT_FOUND_MESSAGE, "", []

    context_str = format_docs_context(docs)
    sources = extract_sources(docs)

    api_key = settings.get_gemini_api_key()
    llm = ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        temperature=0.0,
        google_api_key=api_key
    )

    formatted_prompt = prompt.format(context=context_str, question=question)
    response = llm.invoke(formatted_prompt)
    answer = response.content.strip()

    return answer, context_str, sources
