"""
Pydantic models for DprgArchiveAgent.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator


class ArchiveMetadata(BaseModel):
    """Metadata for an archive document."""
    author: Optional[str] = None
    date: Optional[datetime] = None
    day: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None
    has_url: Optional[bool] = None
    keywords: Optional[List[str]] = None
    title: Optional[str] = None
    text: Optional[str] = None  # Full document text for excerpt generation


class ArchiveDocument(BaseModel):
    """A document from the DPRG archive."""
    id: str
    text_excerpt: str
    metadata: ArchiveMetadata
    score: Optional[float] = None
    search_terms: Optional[List[str]] = None  # Terms used for searching and highlighting
    
    @classmethod
    def from_pinecone_match(cls, match: Dict[str, Any]) -> "ArchiveDocument":
        """Create an ArchiveDocument from a Pinecone match."""
        # Extract the metadata - handle both old and new Pinecone SDK response formats
        metadata = match.get("metadata", {})
        
        # Create metadata object
        archive_metadata = ArchiveMetadata(
            author=metadata.get("author"),
            date=metadata.get("date"),
            day=metadata.get("day"),
            month=metadata.get("month"),
            year=metadata.get("year"),
            has_url=metadata.get("has_url"),
            keywords=metadata.get("keywords"),
            title=metadata.get("title"),
            text=metadata.get("text_excerpt"),  # Store full text in metadata if available
        )
        
        # Create and return document
        return cls(
            id=match.get("id"),
            text_excerpt=metadata.get("text_excerpt", ""),
            metadata=archive_metadata,
            score=match.get("score"),
        )


class SearchQuery(BaseModel):
    """A search query for the DPRG archive."""
    query: str = Field(..., description="The search query text")
    top_k: int = Field(10, description="Number of results to return")
    author: Optional[str] = Field(None, description="Filter by author")
    year: Optional[int] = Field(None, description="Filter by year")
    month: Optional[int] = Field(None, description="Filter by month")
    day: Optional[int] = Field(None, description="Filter by day")
    keywords: Optional[List[str]] = Field(None, description="Filter by keywords")
    min_score: Optional[float] = Field(None, description="Minimum score threshold")
    use_dense: Optional[bool] = Field(True, description="Use dense vector search")
    use_sparse: Optional[bool] = Field(False, description="Use sparse vector search")
    use_hybrid: Optional[bool] = Field(False, description="Use hybrid search approach")
    title: Optional[str] = Field(None, description="Filter by title")
    metadata_filters: Optional[Dict[str, Any]] = Field(None, alias="filters", description="Metadata filters")
    search_type: Optional[str] = Field(None, description="Type of search to perform")


class SearchResponse(BaseModel):
    """Response model for search queries."""
    results: List[ArchiveDocument]
    total: int = Field(..., description="Total number of results")
    query: str = Field(..., description="The original query")
    search_type: str = Field(..., description="The type of search performed")
    elapsed_time: float = Field(..., description="Time taken to perform the search in seconds")


class SearchError(Exception):
    """Error response for search queries."""
    def __init__(self, error: str, details: Optional[Dict[str, Any]] = None):
        self.error = error
        self.details = details
        super().__init__(error)


class Message(BaseModel):
    """Message for chat completion."""
    role: str
    content: str


class ChatMessage(BaseModel):
    """Message for chat completion."""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Request model for chat API."""
    messages: List[Message]
    model: Optional[str] = "gpt-4"
    max_tokens: Optional[int] = 500
    temperature: Optional[float] = 0.7
    search_top_k: Optional[int] = 5
    use_search_type: Optional[str] = "dense"


class ChatCompletionRequest(BaseModel):
    """Request model for chat completion API."""
    messages: List[ChatMessage]
    model: Optional[str] = "gpt-4"
    max_tokens: Optional[int] = 500
    temperature: Optional[float] = 0.7
    search_top_k: Optional[int] = 5
    use_search_type: Optional[str] = "dense"
    min_score: Optional[float] = None


class ChatResponse(BaseModel):
    """Response model for chat API."""
    message: Message
    elapsed_time: float
    referenced_documents: Optional[List[ArchiveDocument]] = []


class ChatCompletionResponse(BaseModel):
    """Response model for chat completion API."""
    message: ChatMessage
    referenced_documents: List[ArchiveDocument] = []
    elapsed_time: float


class ChatCompletionError(BaseModel):
    """Error response for chat completion API."""
    error: str
    details: Optional[Dict[str, Any]] = None 