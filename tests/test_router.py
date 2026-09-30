"""
Tests for Query Routing and LangGraph Decision Logic.
Verifies routing decisions between 'rag' and 'sql'.
"""
from unittest.mock import MagicMock, patch
from backend.agent.router import classify_query_route
from backend.agent.graph import route_decision, AgentState

def test_classify_query_route_sql_mock():
    with patch("backend.agent.router.ChatGoogleGenerativeAI") as mock_llm_cls:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(content="sql")
        mock_llm_cls.return_value = mock_instance

        decision = classify_query_route("How many employees are in Engineering?")
        assert decision == "sql"

def test_classify_query_route_rag_mock():
    with patch("backend.agent.router.ChatGoogleGenerativeAI") as mock_llm_cls:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(content="rag")
        mock_llm_cls.return_value = mock_instance

        decision = classify_query_route("What is the company leave policy?")
        assert decision == "rag"

def test_classify_query_fallback_keywords():
    # If the LLM returns ambiguous text, rule-based fallback detects SQL keywords
    with patch("backend.agent.router.ChatGoogleGenerativeAI") as mock_llm_cls:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(content="I think this is a database question.")
        mock_llm_cls.return_value = mock_instance

        decision = classify_query_route("What is the average employee salary?")
        assert decision == "sql"

def test_langgraph_route_decision_edge():
    rag_state: AgentState = {
        "question": "leave policy",
        "route": "rag",
        "context": "",
        "sql_query": "",
        "sql_result": "",
        "answer": "",
        "sources": []
    }
    assert route_decision(rag_state) == "rag"

    sql_state: AgentState = {
        "question": "how many employees",
        "route": "sql",
        "context": "",
        "sql_query": "",
        "sql_result": "",
        "answer": "",
        "sources": []
    }
    assert route_decision(sql_state) == "sql"
