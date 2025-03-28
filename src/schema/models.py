"""
Pydantic models for DprgArchiveAgent.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union, Literal
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
    text_excerpt: Optional[str] = None


class ArchiveDocument(BaseModel):
    """A document from the DPRG archive."""
    id: str
    text_excerpt: str
    metadata: ArchiveMetadata
    score: Optional[float] = None
    
    @classmethod
    def from_pinecone_match(cls, match: Dict[str, Any]) -> "ArchiveDocument":
        """Create an ArchiveDocument from a Pinecone match."""
        # Extract the metadata - handle both old and new Pinecone SDK response formats
        if hasattr(match, "metadata"):
            # New Pinecone SDK v6+ object response
            metadata = match.metadata
            match_id = match.id
            score = match.score
            # Try to get text_excerpt from both root and metadata
            text_excerpt = getattr(match, "text_excerpt", "") or getattr(metadata, "text_excerpt", "")
        else:
            # Dictionary response or older format
            metadata = match.get("metadata", {})
            match_id = match.get("id", "")
            score = match.get("score")
            # Try to get text_excerpt from both root and metadata
            text_excerpt = match.get("text_excerpt", "") or metadata.get("text_excerpt", "")
        
        # Handle metadata that might be a dictionary or an object
        if isinstance(metadata, dict):
            metadata_dict = metadata
        else:
            metadata_dict = {
                "author": getattr(metadata, "author", None),
                "date": getattr(metadata, "date", None),
                "day": getattr(metadata, "day", None),
                "month": getattr(metadata, "month", None),
                "year": getattr(metadata, "year", None),
                "has_url": getattr(metadata, "has_url", None),
                "keywords": getattr(metadata, "keywords", None),
                "title": getattr(metadata, "title", None),
                "text_excerpt": text_excerpt  # Include text_excerpt in metadata
            }
        
        # Create metadata object
        archive_metadata = ArchiveMetadata(
            author=metadata_dict.get("author"),
            date=metadata_dict.get("date"),
            day=metadata_dict.get("day"),
            month=metadata_dict.get("month"),
            year=metadata_dict.get("year"),
            has_url=metadata_dict.get("has_url"),
            keywords=metadata_dict.get("keywords"),
            title=metadata_dict.get("title"),
            text_excerpt=text_excerpt  # Include text_excerpt in metadata
        )
        
        # Create and return document
        return cls(
            id=match_id,
            text_excerpt=text_excerpt,
            metadata=archive_metadata,
            score=score,
        )


class SearchQuery(BaseModel):
    """Search query model."""
    query: str
    author: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[int] = None
    keywords: Optional[List[str]] = None
    title: Optional[str] = None
    min_score: float = 0.7
    top_k: int = 10
    search_type: str = "dense"
    no_filter: bool = False
    use_dense: bool = True
    use_sparse: bool = False
    use_hybrid: bool = False


class SearchResponse(BaseModel):
    """Search response model."""
    results: List[ArchiveDocument]
    total: int
    query: str
    search_type: str
    elapsed_time: float


class SearchError(BaseModel):
    """Search error model."""
    error: str


# Chat completion models
class ChatMessage(BaseModel):
    """A message in a chat conversation."""
    role: Literal["system", "user", "assistant"] = Field(..., description="The role of the message sender")
    content: str = Field(..., description="The content of the message")


class ChatCompletionRequest(BaseModel):
    """Request model for chat completions."""
    messages: List[ChatMessage] = Field(..., description="The messages in the conversation so far")
    model: Optional[str] = Field(None, description="The model to use for chat completion")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate")
    temperature: Optional[float] = Field(0.7, description="Sampling temperature")
    search_top_k: Optional[int] = Field(5, description="Number of archive documents to retrieve")
    use_search_type: Optional[str] = Field("dense", description="Search type to use: dense, sparse, or hybrid")


class ChatCompletionResponse(BaseModel):
    """Response model for chat completions."""
    message: ChatMessage = Field(..., description="The generated assistant message")
    referenced_documents: List[ArchiveDocument] = Field([], description="Documents referenced in the response")
    elapsed_time: float = Field(..., description="Time taken to generate the response in seconds")


class ChatCompletionError(BaseModel):
    """Error response for chat completions."""
    error: str
    details: Optional[Dict[str, Any]] = None


class Metadata(BaseModel):
    """Document metadata model."""
    author: str
    year: int
    month: int
    day: int
    keywords: List[str]
    title: str
    has_url: bool = False


class Document(BaseModel):
    """Document model."""
    id: str
    text_excerpt: str
    metadata: Metadata
    score: float


class Message(BaseModel):
    """Chat message model."""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""
    messages: List[Message]
    model: str = "gpt-4"
    max_tokens: int = 1024
    temperature: float = 0.7
    search_top_k: int = 5
    use_search_type: str = "dense"


class ChatResponse(BaseModel):
    """Chat response model."""
    message: Message
    referenced_documents: List[Document]
    elapsed_time: float


class ChatError(BaseModel):
    """Chat error model."""
    error: str


class SearchResult(BaseModel):
    """A search result."""
    id: str = Field(..., description="The document ID")
    score: float = Field(..., description="The similarity score")
    content: str = Field(..., description="The document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")


class MetadataFilter(BaseModel):
    """A metadata filter."""
    author: Optional[str] = Field(default=None, description="Filter by author")
    title: Optional[str] = Field(default=None, description="Filter by title")
    keywords: Optional[List[str]] = Field(default=None, description="Filter by keywords")
    start_date: Optional[datetime] = Field(default=None, description="Filter by start date")
    end_date: Optional[datetime] = Field(default=None, description="Filter by end date")


class ErrorResponse(BaseModel):
    """An error response."""
    error: str = Field(..., description="The error message") 