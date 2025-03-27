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


class SearchResponse(BaseModel):
    """Response model for search queries."""
    results: List[ArchiveDocument]
    total: int = Field(..., description="Total number of results")
    query: str = Field(..., description="The original query")
    search_type: str = Field(..., description="The type of search performed")
    elapsed_time: float = Field(..., description="Time taken to perform the search in seconds")


class SearchError(BaseModel):
    """Error response for search queries."""
    error: str
    details: Optional[Dict[str, Any]] = None 