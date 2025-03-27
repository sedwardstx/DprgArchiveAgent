"""
Configuration settings for the DprgArchiveAgent.
"""
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Pinecone settings
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "dprg-archive")

# Vector index URLs
DENSE_INDEX_URL = os.getenv(
    "DENSE_INDEX_URL", 
    "https://dprg-list-archive-dense-4p4f7lg.svc.aped-4627-b74a.pinecone.io"
)
SPARSE_INDEX_URL = os.getenv(
    "SPARSE_INDEX_URL", 
    "https://dprg-list-archive-sparse-4p4f7lg.svc.aped-4627-b74a.pinecone.io"
)

# OpenAI settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_WORKERS = int(os.getenv("API_WORKERS", "4"))

# Search settings
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "10"))
MIN_SCORE_THRESHOLD = float(os.getenv("MIN_SCORE_THRESHOLD", "0.7"))

# Hybrid search weights
DENSE_WEIGHT = float(os.getenv("DENSE_WEIGHT", "0.7"))
SPARSE_WEIGHT = float(os.getenv("SPARSE_WEIGHT", "0.3"))

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
        "dense_index_url": DENSE_INDEX_URL,
        "sparse_index_url": SPARSE_INDEX_URL,
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
