"""
Tests for /chat and /documents/upload API endpoints.
Verifies payload validation, error codes, and successful responses.
"""
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_chat_empty_question_rejected():
    response = client.post("/chat", json={"question": "   "})
    assert response.status_code == 422 or response.status_code == 400

def test_chat_successful_rag_response():
    mock_state = {
        "question": "What is the leave policy?",
        "route": "rag",
        "context": "Sample context",
        "sql_query": "",
        "sql_result": "",
        "answer": "Employees receive 20 days paid leave.",
        "sources": [{"source": "sample.pdf", "page": 1, "content": "20 days leave"}]
    }

    with patch("backend.api.routes.run_agent_workflow", return_value=mock_state):
        response = client.post("/chat", json={"question": "What is the leave policy?"})
        assert response.status_code == 200
        data = response.json()
        assert data["route"] == "rag"
        assert "20 days" in data["answer"]
        assert len(data["sources"]) == 1
        assert data["sources"][0]["source"] == "sample.pdf"

def test_chat_successful_sql_response():
    mock_state = {
        "question": "How many employees are in Engineering?",
        "route": "sql",
        "context": "",
        "sql_query": "SELECT COUNT(*) FROM employees WHERE department_id = 1",
        "sql_result": "[{'COUNT(*)': 8}]",
        "answer": "There are 8 employees in Engineering.",
        "sources": []
    }

    with patch("backend.api.routes.run_agent_workflow", return_value=mock_state):
        response = client.post("/chat", json={"question": "How many employees are in Engineering?"})
        assert response.status_code == 200
        data = response.json()
        assert data["route"] == "sql"
        assert "8 employees" in data["answer"]
        assert data["sql_query"] == "SELECT COUNT(*) FROM employees WHERE department_id = 1"
        assert data["sources"] == []

def test_upload_non_pdf_rejected():
    files = {"file": ("test.txt", b"This is not a PDF", "text/plain")}
    response = client.post("/documents/upload", files=files)
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]

def test_upload_valid_pdf():
    mock_ingest = {
        "filename": "mock_policy.pdf",
        "chunks_added": 6,
        "pages": 2
    }
    with patch("backend.api.routes.ingest_pdf_to_vectorstore", return_value=mock_ingest):
        files = {"file": ("mock_policy.pdf", b"%PDF-1.4 mock pdf content", "application/pdf")}
        response = client.post("/documents/upload", files=files)
        assert response.status_code == 201
        data = response.json()
        assert data["filename"] == "mock_policy.pdf"
        assert data["chunks_ingested"] == 6
        assert data["total_pages"] == 2
