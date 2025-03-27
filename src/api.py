"""
FastAPI REST API for the DPRG Archive Agent.
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any, Union
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .config import get_api_settings, validate_config
from .schema.models import (
    SearchQuery, SearchResponse, SearchError, ArchiveDocument,
    ChatMessage, ChatCompletionRequest, ChatCompletionResponse, ChatCompletionError
)
from .agent.archive_agent import archive_agent

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
    yield
    # Shutdown logic can be added here if needed

# Initialize FastAPI app
app = FastAPI(
    title="DPRG Archive Agent API",
    description="API for querying the DPRG archive using vector search",
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


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "DPRG Archive Agent API",
        "description": "Search the DPRG archive using vector search",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Validate configuration
    config_status = validate_config()
    
    return {
        "status": "healthy" if config_status["valid"] else "unhealthy",
        "config_valid": config_status["valid"],
        "message": config_status.get("message", "All systems operational")
    }


@app.get("/search", response_model=Union[SearchResponse, SearchError])
async def search(
    query: str = Query(..., description="Search query text"),
    top_k: int = Query(10, description="Number of results to return"),
    author: Optional[str] = Query(None, description="Filter by author"),
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month"),
    day: Optional[int] = Query(None, description="Filter by day"),
    keywords: Optional[str] = Query(None, description="Comma-separated keywords to filter by"),
    min_score: Optional[float] = Query(None, description="Minimum score threshold"),
    search_type: str = Query("dense", description="Search type: dense, sparse, or hybrid"),
):
    """
    Search the DPRG archive.
    
    Args:
        query: The search query
        top_k: Number of results to return
        author: Filter by author
        year: Filter by year
        month: Filter by month
        day: Filter by day
        keywords: Comma-separated keywords to filter by
        min_score: Minimum score threshold
        search_type: Search type (dense, sparse, or hybrid)
        
    Returns:
        SearchResponse with results or SearchError if an error occurred
    """
    try:
        # Parse keywords if provided
        keyword_list = None
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
            
        # Create search query
        search_query = SearchQuery(
            query=query,
            top_k=top_k,
            author=author,
            year=year,
            month=month,
            day=day,
            keywords=keyword_list,
            min_score=min_score,
            use_dense=search_type == "dense",
            use_sparse=search_type == "sparse",
            use_hybrid=search_type == "hybrid",
        )
        
        # Execute search
        if search_type == "hybrid":
            result = await archive_agent.search_hybrid(
                query=query,
                top_k=top_k,
                author=author,
                year=year,
                month=month,
                day=day,
                keywords=keyword_list,
                min_score=min_score,
            )
        elif search_type == "sparse":
            result = await archive_agent.search_sparse(
                query=query,
                top_k=top_k,
                author=author,
                year=year,
                month=month,
                day=day,
                keywords=keyword_list,
                min_score=min_score,
            )
        else:  # dense
            result = await archive_agent.search_dense(
                query=query,
                top_k=top_k,
                author=author,
                year=year,
                month=month,
                day=day,
                keywords=keyword_list,
                min_score=min_score,
            )
        
        # Check for error response
        if isinstance(result, SearchError):
            raise HTTPException(status_code=500, detail=result.error)
        
        return result
    
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/metadata", response_model=Union[SearchResponse, SearchError])
async def search_by_metadata(
    author: Optional[str] = Query(None, description="Filter by author"),
    year: Optional[int] = Query(None, description="Filter by year"),
    month: Optional[int] = Query(None, description="Filter by month"),
    day: Optional[int] = Query(None, description="Filter by day"),
    keywords: Optional[str] = Query(None, description="Comma-separated keywords to filter by"),
    top_k: int = Query(10, description="Number of results to return"),
):
    """
    Search the DPRG archive by metadata only.
    
    Args:
        author: Filter by author
        year: Filter by year
        month: Filter by month
        day: Filter by day
        keywords: Comma-separated keywords to filter by
        top_k: Number of results to return
        
    Returns:
        SearchResponse with results or SearchError if an error occurred
    """
    try:
        # Parse keywords if provided
        keyword_list = None
        if keywords:
            keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
            
        # At least one metadata field must be provided
        if not any([author, year, month, day, keyword_list]):
            raise HTTPException(
                status_code=400, 
                detail="At least one metadata filter must be provided"
            )
            
        # Execute search
        result = await archive_agent.search_by_metadata(
            author=author,
            year=year,
            month=month,
            day=day,
            keywords=keyword_list,
            top_k=top_k,
        )
        
        # Check for error response
        if isinstance(result, SearchError):
            raise HTTPException(status_code=500, detail=result.error)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in metadata search endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Metadata search failed: {str(e)}")


@app.post("/chat", response_model=Union[ChatCompletionResponse, ChatCompletionError])
async def chat_completion(
    request: ChatCompletionRequest = Body(..., description="Chat completion request")
):
    """
    Generate a chat completion based on the conversation history,
    using relevant documents from the DPRG archive.
    
    Args:
        request: Chat completion request with messages and parameters
        
    Returns:
        ChatCompletionResponse with generated message or ChatCompletionError
    """
    try:
        logger.info("Received chat completion request")
        
        # Validate the request
        if not request.messages:
            raise HTTPException(status_code=400, detail="No messages provided in the request")
        
        # Process the chat request
        result = await archive_agent.chat(request)
        
        # Check for error response
        if isinstance(result, ChatCompletionError):
            raise HTTPException(status_code=500, detail=result.error)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat completion endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat completion failed: {str(e)}")


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
