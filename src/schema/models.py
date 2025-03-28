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
        else:
            # Dictionary response or older format
            metadata = match.get("metadata", {})
            match_id = match.get("id", "")
            score = match.get("score")
        
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
        )
        
        # Create and return document
        return cls(
            id=match_id,
            text_excerpt=metadata.get("text_excerpt", ""),
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