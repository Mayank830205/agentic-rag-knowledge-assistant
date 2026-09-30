"""
Pydantic Request and Response Schemas.
Enforces strict input validation and clean typed API responses.
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator

class ChatRequest(BaseModel):
    """Incoming user chat query."""
    question: str = Field(..., description="The user question to process")

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Question cannot be empty or solely whitespace.")
        return cleaned

class DocumentSource(BaseModel):
    """Source reference for RAG document retrieval."""
    source: str = Field(..., description="Filename of the source document")
    page: Optional[int] = Field(None, description="Page number of the retrieved chunk if applicable")
    content: str = Field(..., description="Relevant text excerpt retrieved from the document")

class ChatResponse(BaseModel):
    """Structured response returned by /chat endpoint."""
    answer: str = Field(..., description="Natural language answer to the user query")
    route: Literal["rag", "sql"] = Field(..., description="Routing path chosen by LangGraph ('rag' or 'sql')")
    sources: List[DocumentSource] = Field(default_factory=list, description="Retrieved document citations for RAG")
    sql_query: Optional[str] = Field(None, description="Generated and executed SELECT query (SQL route only)")

class HealthResponse(BaseModel):
    """Application health status response."""
    status: str
    database: str
    vector_store: str
    documents_count: int

class UploadResponse(BaseModel):
    """Response returned upon uploading and processing a PDF."""
    message: str
    filename: str
    chunks_ingested: int
    total_pages: int
