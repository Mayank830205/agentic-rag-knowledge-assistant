"""
LangGraph Routing Workflow.
Orchestrates State, Nodes, and Conditional Routing between RAG and SQL subsystems:

START -> Router -> (RAG Node | SQL Node) -> Final Response -> END
"""
import logging
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END

from backend.agent.router import classify_query_route
from backend.rag.retriever import query_rag_pipeline
from backend.agent.sql_node import generate_and_execute_sql

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """LangGraph execution state."""
    question: str
    route: str
    context: str
    sql_query: str
    sql_result: str
    answer: str
    sources: List[Dict[str, Any]]

# Node 1: Router Node
def router_node(state: AgentState) -> Dict[str, Any]:
    """Inspects the user question and decides between RAG and SQL routes."""
    question = state["question"]
    route = classify_query_route(question)
    logger.info(f"Router classified question: '{question}' -> route: {route}")
    return {"route": route}

# Conditional routing edge function
def route_decision(state: AgentState) -> str:
    """Evaluates the state route field to choose next branch."""
    return state.get("route", "rag")

# Node 2A: RAG Retrieval Node
def rag_node(state: AgentState) -> Dict[str, Any]:
    """Retrieves document context from ChromaDB and generates grounded answer."""
    question = state["question"]
    logger.info(f"Executing RAG Node for question: '{question}'")
    answer, context, sources = query_rag_pipeline(question)
    return {
        "context": context,
        "answer": answer,
        "sources": sources,
        "sql_query": "",
        "sql_result": ""
    }

# Node 2B: SQL Execution Node
def sql_node(state: AgentState) -> Dict[str, Any]:
    """Generates SELECT query, validates against destructive operations, and queries MySQL."""
    question = state["question"]
    logger.info(f"Executing SQL Node for question: '{question}'")
    answer, clean_query, raw_results = generate_and_execute_sql(question)
    return {
        "context": "",
        "answer": answer,
        "sources": [],
        "sql_query": clean_query,
        "sql_result": str(raw_results)
    }

# Node 3: Final Response Formatting Node
def finalize_response_node(state: AgentState) -> Dict[str, Any]:
    """Prepares and validates the final response payload."""
    logger.info(f"Finalizing response for route: {state.get('route')}")
    return {}

def build_agent_graph():
    """Constructs and compiles the LangGraph workflow."""
    workflow = StateGraph(AgentState)

    # Register Nodes
    workflow.add_node("router", router_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("sql_node", sql_node)
    workflow.add_node("finalize_response", finalize_response_node)

    # Define Edges
    workflow.add_edge(START, "router")
    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "rag": "rag_node",
            "sql": "sql_node"
        }
    )
    workflow.add_edge("rag_node", "finalize_response")
    workflow.add_edge("sql_node", "finalize_response")
    workflow.add_edge("finalize_response", END)

    app = workflow.compile()
    return app

# Singleton compiled graph
agent_graph = build_agent_graph()

def run_agent_workflow(question: str) -> AgentState:
    """Executes the compiled LangGraph workflow for an input question."""
    initial_state: AgentState = {
        "question": question,
        "route": "",
        "context": "",
        "sql_query": "",
        "sql_result": "",
        "answer": "",
        "sources": []
    }
    final_state = agent_graph.invoke(initial_state)
    return final_state
