"""
Configuration settings for the DprgArchiveAgent.
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    # Pinecone settings
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENVIRONMENT: str = os.getenv("PINECONE_ENVIRONMENT", "")
    DENSE_INDEX_NAME: str = os.getenv("DENSE_INDEX_NAME", "dense-test")
    SPARSE_INDEX_NAME: str = os.getenv("SPARSE_INDEX_NAME", "sparse-test")
    DENSE_INDEX_URL: str = os.getenv("DENSE_INDEX_URL", "")
    SPARSE_INDEX_URL: str = os.getenv("SPARSE_INDEX_URL", "")
    PINECONE_NAMESPACE: str = os.getenv("PINECONE_NAMESPACE", "default")
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
    CHAT_MODEL: str = os.getenv("CHAT_MODEL", "gpt-4")
    CHAT_MAX_TOKENS: int = int(os.getenv("CHAT_MAX_TOKENS", "1024"))
    CHAT_TEMPERATURE: float = float(os.getenv("CHAT_TEMPERATURE", "0.7"))
    
    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_WORKERS: int = int(os.getenv("API_WORKERS", "4"))
    
    # Search settings
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "10"))
    MIN_SCORE_THRESHOLD: float = float(os.getenv("MIN_SCORE_THRESHOLD", "0.7"))
    DENSE_WEIGHT: float = float(os.getenv("DENSE_WEIGHT", "0.7"))
    SPARSE_WEIGHT: float = float(os.getenv("SPARSE_WEIGHT", "0.3"))
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = True

_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Export settings for backward compatibility
settings = get_settings()
PINECONE_API_KEY = settings.PINECONE_API_KEY
PINECONE_ENVIRONMENT = settings.PINECONE_ENVIRONMENT
OPENAI_API_KEY = settings.OPENAI_API_KEY
DENSE_INDEX_NAME = settings.DENSE_INDEX_NAME
SPARSE_INDEX_NAME = settings.SPARSE_INDEX_NAME
DENSE_INDEX_URL = settings.DENSE_INDEX_URL
SPARSE_INDEX_URL = settings.SPARSE_INDEX_URL
PINECONE_NAMESPACE = settings.PINECONE_NAMESPACE

# Model settings
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
CHAT_MODEL = settings.CHAT_MODEL
CHAT_MAX_TOKENS = settings.CHAT_MAX_TOKENS
CHAT_TEMPERATURE = settings.CHAT_TEMPERATURE

# API settings
API_HOST = settings.API_HOST
API_PORT = settings.API_PORT
API_WORKERS = settings.API_WORKERS

# Search settings
DEFAULT_TOP_K = settings.DEFAULT_TOP_K
MIN_SCORE_THRESHOLD = settings.MIN_SCORE_THRESHOLD
DENSE_WEIGHT = settings.DENSE_WEIGHT
SPARSE_WEIGHT = settings.SPARSE_WEIGHT

# Pinecone settings
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "dprg-archive")

# Vector index URLs
DENSE_INDEX_URL = os.getenv("DENSE_INDEX_URL", "https://dprg-list-archive-dense-4p4f7lg.svc.aped-4627-b74a.pinecone.io")
SPARSE_INDEX_URL = os.getenv("SPARSE_INDEX_URL", "https://dprg-list-archive-sparse-4p4f7lg.svc.aped-4627-b74a.pinecone.io")

# Vector index names (from available indices)
DENSE_INDEX_NAME = "dprg-list-archive-dense"
SPARSE_INDEX_NAME = "dprg-list-archive-sparse"

# OpenAI settings
CHAT_SYSTEM_PROMPT = os.getenv(
    "CHAT_SYSTEM_PROMPT", 
    "You are an expert on the DPRG (Dallas Personal Robotics Group) archive. "
    "Answer questions using only the specific information provided in the retrieved documents. "
    "If you don't have enough information to answer, say so clearly rather than making up information. "
    "When referencing information, cite the source document titles. "
    "You should focus on providing accurate, helpful information about robotics, DPRG history, and related topics."
)

def validate_config() -> Dict[str, Any]:
    """Validate that required configuration settings are present."""
    missing = []
    
    if not PINECONE_API_KEY:
        missing.append("PINECONE_API_KEY")
    
    # Pinecone SDK v6+ no longer requires environment parameter
    # Kept for backward compatibility but not enforced
    
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    
    if missing:
        return {
            "valid": False,
            "missing": missing,
            "message": f"Missing required configuration: {', '.join(missing)}"
        }
    
    return {"valid": True}

def get_vector_index_settings() -> Dict[str, Any]:
    """Return settings related to vector indexes."""
    return {
        "dense_index_name": DENSE_INDEX_NAME,
        "sparse_index_name": SPARSE_INDEX_NAME,
        "namespace": PINECONE_NAMESPACE,
        "api_key": PINECONE_API_KEY,
        "environment": PINECONE_ENVIRONMENT,
    }

def get_api_settings() -> Dict[str, Any]:
    """Return settings related to the API server."""
    return {
        "host": API_HOST,
        "port": API_PORT,
        "workers": API_WORKERS,
    }

def get_search_settings() -> Dict[str, Any]:
    """Return settings related to search operations."""
    return {
        "top_k": DEFAULT_TOP_K,
        "min_score": MIN_SCORE_THRESHOLD,
        "dense_weight": DENSE_WEIGHT,
        "sparse_weight": SPARSE_WEIGHT,
    }

def get_chat_settings() -> Dict[str, Any]:
    """Return settings related to chat completions."""
    return {
        "model": CHAT_MODEL,
        "max_tokens": CHAT_MAX_TOKENS,
        "temperature": CHAT_TEMPERATURE,
        "system_prompt": CHAT_SYSTEM_PROMPT,
    }
