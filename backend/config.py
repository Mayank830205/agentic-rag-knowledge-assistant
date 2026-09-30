"""
Application Configuration Module.
Loads environment variables and provides centralized settings for the application.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # Gemini Configuration
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    LLM_MODEL: str = Field(default="gemini-2.5-flash", description="Gemini Chat Model Name")
    EMBEDDING_MODEL: str = Field(default="gemini-embedding-001", description="Gemini Text Embedding Model Name")
    
    # MySQL Database Configuration
    MYSQL_HOST: str = Field(default="localhost", description="MySQL Hostname")
    MYSQL_PORT: int = Field(default=3306, description="MySQL Port")
    MYSQL_DATABASE: str = Field(default="agentrag_db", description="MySQL Database Name")
    MYSQL_USER: str = Field(default="root", description="MySQL Username")
    MYSQL_PASSWORD: str = Field(default="root", description="MySQL Password")
    
    # Storage Paths
    CHROMA_PERSIST_DIRECTORY: str = Field(default="./chroma_data", description="Local ChromaDB storage path")
    DATA_DOCUMENTS_DIRECTORY: str = Field(default="./data/documents", description="Uploaded documents directory")
    
    # Networking & Logging
    BACKEND_URL: str = Field(default="http://localhost:8000", description="Backend URL for Streamlit")
    LOG_LEVEL: str = Field(default="INFO", description="Logging Level")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_gemini_api_key(self) -> str:
        """Helper to ensure API key is retrieved from GEMINI_API_KEY, GOOGLE_API_KEY, or Streamlit secrets."""
        key = self.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
        if not key:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                    key = str(st.secrets["GEMINI_API_KEY"])
            except Exception:
                pass
        return key

    def get_mysql_connection_url(self) -> str:
        """Constructs a PyMySQL SQLAlchemy connection string."""
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

# Global singleton settings instance
settings = Settings()
