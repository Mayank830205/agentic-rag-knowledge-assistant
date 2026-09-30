"""
Tests for RAG Ingestion, Chunking, Retrieval, and Grounded Generation.
"""
from unittest.mock import MagicMock, patch
from langchain_core.documents import Document
from backend.rag.retriever import format_docs_context, extract_sources, query_rag_pipeline, NOT_FOUND_MESSAGE

def test_format_docs_context():
    docs = [
        Document(page_content="Policy line 1", metadata={"source": "policy.pdf", "page": 1}),
        Document(page_content="Policy line 2", metadata={"source": "policy.pdf", "page": 2}),
    ]
    ctx = format_docs_context(docs)
    assert "[Excerpt 1 | Source: policy.pdf, Page: 1]" in ctx
    assert "Policy line 1" in ctx
    assert "[Excerpt 2 | Source: policy.pdf, Page: 2]" in ctx
    assert "Policy line 2" in ctx

def test_extract_sources_deduplication():
    docs = [
        Document(page_content="Sample text chunk A", metadata={"source": "doc1.pdf", "page": 1}),
        Document(page_content="Sample text chunk A", metadata={"source": "doc1.pdf", "page": 1}),
        Document(page_content="Sample text chunk B", metadata={"source": "doc1.pdf", "page": 2}),
    ]
    sources = extract_sources(docs)
    assert len(sources) == 2
    assert sources[0]["source"] == "doc1.pdf"
    assert sources[0]["page"] == 1
    assert sources[1]["page"] == 2

def test_query_rag_pipeline_not_found():
    with patch("backend.rag.retriever.get_retriever") as mock_retriever_getter:
        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = []
        mock_retriever_getter.return_value = mock_retriever

        answer, ctx, sources = query_rag_pipeline("Question with no matching docs")
        assert answer == NOT_FOUND_MESSAGE
        assert ctx == ""
        assert sources == []

def test_query_rag_pipeline_grounded_answer():
    mock_docs = [
        Document(page_content="All employees receive 20 days paid leave.", metadata={"source": "handbook.pdf", "page": 1})
    ]
    with patch("backend.rag.retriever.get_retriever") as mock_retriever_getter:
        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = mock_docs
        mock_retriever_getter.return_value = mock_retriever

        with patch("backend.rag.retriever.ChatGoogleGenerativeAI") as mock_llm_cls:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content="Employees get 20 days of paid leave.")
            mock_llm_cls.return_value = mock_llm

            answer, ctx, sources = query_rag_pipeline("What is the leave allowance?")
            assert "20 days" in answer
            assert len(sources) == 1
            assert sources[0]["source"] == "handbook.pdf"
            assert sources[0]["page"] == 1
