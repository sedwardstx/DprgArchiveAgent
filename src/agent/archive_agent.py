"""
Main agent for the DPRG Archive.
"""
import logging
from typing import Dict, List, Any, Optional, Union

from ..schema.models import SearchQuery, SearchResponse, SearchError, ArchiveDocument
from ..tools.search_tool import search_tool

# Set up logger
logger = logging.getLogger(__name__)


class ArchiveAgent:
    """
    Agent for searching and querying the DPRG archive.
    """
    
    def __init__(self):
        """Initialize the archive agent."""
        self.search_tool = search_tool
        logger.info("Archive agent initialized")
    
    async def search(self, query: Union[str, SearchQuery]) -> Union[SearchResponse, SearchError]:
        """
        Search the DPRG archive.
        
        Args:
            query: Either a string query or a SearchQuery object
            
        Returns:
            SearchResponse with results or SearchError if an error occurred
        """
        # Convert string query to SearchQuery if needed
        if isinstance(query, str):
            search_query = SearchQuery(query=query)
        else:
            search_query = query
            
        logger.info(f"Searching for: {search_query.query}")
        
        try:
            # Execute search
            result = await self.search_tool.search(search_query)
            return result
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return SearchError(error=f"Search failed: {str(e)}")
    
    async def search_hybrid(
        self, 
        query: str, 
        top_k: int = 10,
        **kwargs
    ) -> Union[SearchResponse, SearchError]:
        """
        Perform a hybrid search using both dense and sparse indexes.
        
        Args:
            query: The search query
            top_k: Number of results to return
            **kwargs: Additional filter parameters
            
        Returns:
            SearchResponse with results or SearchError if an error occurred
        """
        search_query = SearchQuery(
            query=query,
            top_k=top_k,
            use_hybrid=True,
            use_dense=False,
            use_sparse=False,
            **kwargs
        )
        
        logger.info(f"Hybrid search for: {search_query.query}")
        return await self.search(search_query)
    
    async def search_dense(
        self, 
        query: str, 
        top_k: int = 10,
        **kwargs
    ) -> Union[SearchResponse, SearchError]:
        """
        Perform a search using the dense vector index.
        
        Args:
            query: The search query
            top_k: Number of results to return
            **kwargs: Additional filter parameters
            
        Returns:
            SearchResponse with results or SearchError if an error occurred
        """
        search_query = SearchQuery(
            query=query,
            top_k=top_k,
            use_hybrid=False,
            use_dense=True,
            use_sparse=False,
            **kwargs
        )
        
        logger.info(f"Dense search for: {search_query.query}")
        return await self.search(search_query)
    
    async def search_sparse(
        self, 
        query: str, 
        top_k: int = 10,
        **kwargs
    ) -> Union[SearchResponse, SearchError]:
        """
        Perform a search using the sparse vector index.
        
        Args:
            query: The search query
            top_k: Number of results to return
            **kwargs: Additional filter parameters
            
        Returns:
            SearchResponse with results or SearchError if an error occurred
        """
        search_query = SearchQuery(
            query=query,
            top_k=top_k,
            use_hybrid=False,
            use_dense=False,
            use_sparse=True,
            **kwargs
        )
        
        logger.info(f"Sparse search for: {search_query.query}")
        return await self.search(search_query)
    
    async def search_by_metadata(
        self,
        author: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        keywords: Optional[List[str]] = None,
        title: Optional[str] = None,
        top_k: int = 10,
        min_score: Optional[float] = None,
    ) -> Union[SearchResponse, SearchError]:
        """
        Search the DPRG archive by metadata only.
        
        Args:
            author: Filter by author
            year: Filter by year
            month: Filter by month
            day: Filter by day
            keywords: Filter by keywords
            title: Filter by title (partial match)
            top_k: Number of results to return
            min_score: Minimum score threshold
            
        Returns:
            SearchResponse with results or SearchError if an error occurred
        """
        # Construct a dummy query just to search by metadata
        search_query = SearchQuery(
            query="*",  # Wildcard query
            top_k=top_k,
            author=author,
            year=year,
            month=month,
            day=day,
            keywords=keywords,
            title=title,
            min_score=min_score,
            use_dense=True,  # Using dense by default
        )
        
        logger.info(f"Metadata search")
        return await self.search(search_query)


# Create singleton instance
archive_agent = ArchiveAgent() 