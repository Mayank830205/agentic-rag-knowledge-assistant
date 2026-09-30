"""
Tests for /health endpoint.
Verifies API status response and handles both connected and degraded states.
"""
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint_success():
    with patch("backend.api.routes.check_database_connection", return_value=(True, "Operational")):
        with patch("backend.api.routes.get_vectorstore_doc_count", return_value=12):
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"
            assert data["vector_store"] == "ready"
            assert data["documents_count"] == 12

def test_health_endpoint_db_failure():
    with patch("backend.api.routes.check_database_connection", return_value=(False, "Connection refused")):
        with patch("backend.api.routes.get_vectorstore_doc_count", return_value=0):
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert "disconnected" in data["database"]
