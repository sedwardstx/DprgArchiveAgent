"""
Search tool for the DPRG Archive Agent.
"""
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Union

from ..config import DEFAULT_TOP_K, MIN_SCORE_THRESHOLD
from ..schema.models import SearchQuery, ArchiveDocument, SearchResponse, SearchError, ArchiveMetadata
from ..utils.vector_store import DenseVectorClient, SparseVectorClient, HybridSearchClient

# Set up logger
logger = logging.getLogger(__name__)


class SearchTool:
    """Tool for searching the DPRG archive."""
    
    def __init__(self, dense_client: Optional[DenseVectorClient] = None, sparse_client: Optional[SparseVectorClient] = None, hybrid_client: Optional[HybridSearchClient] = None):
        """
        Initialize the search tool.
        
        Args:
            dense_client: Optional DenseVectorClient instance
            sparse_client: Optional SparseVectorClient instance
            hybrid_client: Optional HybridSearchClient instance
        """
        # Initialize vector clients
        self.dense_client = dense_client or DenseVectorClient()
        self.sparse_client = sparse_client or SparseVectorClient()
        self.hybrid_client = hybrid_client or HybridSearchClient()
        logger.info("Search tool initialized")
    
    async def search(self, query: SearchQuery) -> Union[SearchResponse, SearchError]:
        """
        Search for documents matching the query.
        """
        try:
            # Validate query
            if not query.query:
                return SearchError(error="Query cannot be empty")
            if len(query.query) > 1000:
                return SearchError(error="Query is too long (max 1000 characters)")
            
            # Validate dates
            if query.year and (query.year < 1900 or query.year > 2100):
                return SearchError(error="Year must be between 1900 and 2100")
            if query.month and (query.month < 1 or query.month > 12):
                return SearchError(error="Month must be between 1 and 12")
            if query.day and (query.day < 1 or query.day > 31):
                return SearchError(error="Day must be between 1 and 31")

            # Validate search type
            if query.search_type and query.search_type not in ["dense", "sparse", "hybrid"]:
                return SearchError(error="Invalid search type. Must be one of: dense, sparse, hybrid")

            # Build filters from query fields
            filters = {}
            if query.author:
                filters["author"] = query.author
            if query.year:
                filters["year"] = query.year
            if query.month:
                filters["month"] = query.month
            if query.day:
                filters["day"] = query.day
            if query.keywords:
                filters["keywords"] = query.keywords
            if query.title:
                filters["title"] = query.title

            # Log actual query and filters for debugging
            logger.debug(f"Executing search with query: {query.query}")
            if filters:
                logger.debug(f"Using filters: {filters}")

            # Execute search based on type
            search_type = query.search_type or "dense"
            if search_type == "dense":
                results = await self.dense_search(query.query, filters=filters, top_k=query.top_k, min_score=query.min_score)
            elif search_type == "sparse":
                results = await self.sparse_search(query.query, filters=filters, top_k=query.top_k, min_score=query.min_score)
            else:  # hybrid
                results = await self.hybrid_search(query.query, filters=filters, top_k=query.top_k, min_score=query.min_score)

            # Convert results to ArchiveDocument objects
            docs = []
            for result in results:
                try:
                    doc = ArchiveDocument.from_pinecone_match(result)
                    docs.append(doc)
                except Exception as e:
                    logger.error(f"Error converting result to ArchiveDocument: {e}")
                    continue

            # Return response
            response = SearchResponse(
                results=docs,
                total=len(docs),
                query=query.query,
                search_type=search_type,
                elapsed_time=0.0  # TODO: Implement timing
            )
            return response

        except Exception as e:
            logger.error(f"Error executing search: {e}")
            return SearchError(error=str(e))

    async def dense_search(self, query: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 10, min_score: float = 0.7) -> List[Dict[str, Any]]:
        """Execute a dense vector search."""
        try:
            return await self.dense_client.search(query, top_k=top_k, filter=filters, min_score=min_score)
        except Exception as e:
            logger.error(f"Error in dense search: {e}")
            return []

    async def sparse_search(self, query: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 10, min_score: float = 0.7) -> List[Dict[str, Any]]:
        """Execute a sparse vector search."""
        try:
            return await self.sparse_client.search(query, top_k=top_k, filter=filters, min_score=min_score)
        except Exception as e:
            logger.error(f"Error in sparse search: {e}")
            return []

    async def hybrid_search(self, query: str, filters: Optional[Dict[str, Any]] = None, top_k: int = 10, min_score: float = 0.7) -> List[Dict[str, Any]]:
        """Execute a hybrid search combining dense and sparse results."""
        try:
            dense_results = await self.dense_search(query, filters=filters, top_k=top_k, min_score=min_score)
            sparse_results = await self.sparse_search(query, filters=filters, top_k=top_k, min_score=min_score)
            
            # Combine and deduplicate results
            seen_ids = set()
            combined_results = []
            for result in dense_results + sparse_results:
                result_id = result.get('id')
                if result_id not in seen_ids:
                    seen_ids.add(result_id)
                    combined_results.append(result)
            
            # Sort by score and take top_k
            combined_results.sort(key=lambda x: x.get('score', 0), reverse=True)
            return combined_results[:top_k]
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    def _build_filter(self, query: SearchQuery) -> Optional[Dict[str, Any]]:
        """
        Build a filter dictionary for the search query.
        
        Args:
            query: The search query parameters
            
        Returns:
            Optional filter dictionary
        """
        filter_dict = {}
        
        if query.author:
            filter_dict['author'] = query.author
        if query.year:
            filter_dict['year'] = query.year
        if query.month:
            filter_dict['month'] = query.month
        if query.day:
            filter_dict['day'] = query.day
        if query.keywords:
            filter_dict['keywords'] = query.keywords
        if query.title:
            filter_dict['title'] = query.title
            
        return filter_dict if filter_dict else None
    
    async def filter_by_metadata(
        self,
        results: List[ArchiveDocument],
        author: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        keywords: Optional[List[str]] = None,
        title: Optional[str] = None,
    ) -> List[ArchiveDocument]:
        """
        Filter results by metadata criteria.
        
        Args:
            results: List of results to filter
            author: Filter by author
            year: Filter by year
            month: Filter by month
            day: Filter by day
            keywords: Filter by keywords
            title: Filter by title
            
        Returns:
            Filtered list of results
        """
        filtered_results = []
        
        for result in results:
            # Check each filter criterion
            if author and result.metadata.author != author:
                continue
            if year and result.metadata.year != year:
                continue
            if month and result.metadata.month != month:
                continue
            if day and result.metadata.day != day:
                continue
            if keywords and not all(k in (result.metadata.keywords or []) for k in keywords):
                continue
            if title and result.metadata.title != title:
                continue
                
            filtered_results.append(result)
            
        return filtered_results


# Create singleton instance
search_tool = SearchTool() 