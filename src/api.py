"""
FastAPI REST API for the DPRG Archive Agent.
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, HTTPException, Depends, Body, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config import get_settings, get_api_settings, validate_config
from .schema.models import (
    SearchQuery, SearchResponse, SearchError, ArchiveDocument,
    ChatMessage, ChatCompletionRequest, ChatCompletionResponse, ChatCompletionError,
    ChatRequest, ChatResponse
)
from .agent.archive_agent import ArchiveAgent
from .tools.search_tool import SearchTool
from .tools.chat_tool import ChatTool
from .utils.vector_store import DenseVectorClient, SparseVectorClient

# Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with lifespan handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for application startup and shutdown events."""
    # Validate configuration
    config_status = validate_config()
    if not config_status["valid"]:
        logger.error(f"Invalid configuration: {config_status['message']}")
        # We'll continue, but log the error
    # Initialize tools
    settings = get_settings()
    dense_vector_client = DenseVectorClient()
    sparse_vector_client = SparseVectorClient()
    search_tool = SearchTool(dense_vector_client, sparse_vector_client)
    chat_tool = ChatTool()
    archive_agent = ArchiveAgent(search_tool, chat_tool)
    yield
    # Shutdown logic can be added here if needed

# Initialize FastAPI app
app = FastAPI(
    title="DPRG Archive Search API",
    description="Search the DPRG archive using vector search",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients and tools
settings = get_settings()
dense_vector_client = DenseVectorClient()
sparse_vector_client = SparseVectorClient()
search_tool = SearchTool(dense_vector_client, sparse_vector_client)
chat_tool = ChatTool()
archive_agent = ArchiveAgent(search_tool, chat_tool)
api_settings = get_api_settings()

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the DPRG Archive Search API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.post("/search")
async def search(query: SearchQuery) -> SearchResponse:
    """Search endpoint."""
    try:
        return await search_tool.search(query)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """Chat endpoint."""
    try:
        return await chat_tool.process(request)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/metadata")
async def metadata(query: SearchQuery) -> Dict[str, Any]:
    """Metadata endpoint."""
    try:
        response = await search_tool.search(query)
        return {
            "metadata": [doc.metadata for doc in response.results],
            "total": response.total
        }
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start():
    """Start the API server."""
    # Get API settings
    settings = get_api_settings()
    
    # Start the server
    uvicorn.run(
        "src.api:app",
        host=settings["host"],
        port=settings["port"],
        workers=settings["workers"],
        reload=True,
    )

if __name__ == "__main__":
    start()
