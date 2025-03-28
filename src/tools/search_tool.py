"""
Search tool for the DPRG Archive Agent.
"""
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Union

from ..config import DEFAULT_TOP_K, MIN_SCORE_THRESHOLD
from ..schema.models import SearchQuery, ArchiveDocument, SearchResponse, SearchError
from ..utils.vector_store import DenseVectorClient, SparseVectorClient, HybridSearchClient

# Set up logger
logger = logging.getLogger(__name__)


class SearchTool:
    """Tool for searching the DPRG archive."""
    
    def __init__(self):
        """Initialize the search tool."""
        # Initialize vector clients
        self.dense_client = DenseVectorClient()
        self.sparse_client = SparseVectorClient()
        self.hybrid_client = HybridSearchClient()
        logger.info("Search tool initialized")
    
    async def search(self, query: SearchQuery) -> Union[SearchResponse, SearchError]:
        """
        Search the DPRG archive using the specified query parameters.
        
        Args:
            query: The search query parameters
            
        Returns:
            SearchResponse with results or SearchError if an error occurred
        """
        start_time = time.time()
        
        try:
            # Log the actual query for debugging
            logger.info(f"Search query: '{query.query}', Search type: {query.use_dense=}, {query.use_sparse=}, {query.use_hybrid=}")
            if query.title:
                logger.info(f"Searching with title filter: '{query.title}'")
                
            # More filter logging
            if query.author or query.year or query.month or query.day or query.keywords:
                logger.info("Additional filters: " + 
                           (f"author='{query.author}' " if query.author else "") +
                           (f"year={query.year} " if query.year else "") +
                           (f"month={query.month} " if query.month else "") +
                           (f"day={query.day} " if query.day else "") +
                           (f"keywords={query.keywords} " if query.keywords else ""))
            
            # Determine search type and execute search
            if query.use_hybrid:
                search_type = "hybrid"
                results = await self.hybrid_client.search(
                    query.query,
                    top_k=query.top_k,
                    filter=self._build_filter(query),
                    min_score=query.min_score
                )
            elif query.use_sparse:
                search_type = "sparse"
                results = await self.sparse_client.search(
                    query.query,
                    top_k=query.top_k,
                    filter=self._build_filter(query),
                    min_score=query.min_score
                )
            else:
                search_type = "dense"
                results = await self.dense_client.search(
                    query.query,
                    top_k=query.top_k,
                    filter=self._build_filter(query),
                    min_score=query.min_score
                )
            
            # Convert results to ArchiveDocument objects
            documents = [
                ArchiveDocument(
                    id=result['id'],
                    text_excerpt=result['metadata'].get('text_excerpt', ''),
                    metadata=result['metadata'],
                    score=result['score']
                )
                for result in results
            ]
            
            # Filter by metadata if needed
            if any([query.author, query.year, query.month, query.day, query.keywords, query.title]):
                documents = await self.filter_by_metadata(
                    documents,
                    author=query.author,
                    year=query.year,
                    month=query.month,
                    day=query.day,
                    keywords=query.keywords,
                    title=query.title
                )
            
            # Create and return response
            return SearchResponse(
                results=documents,
                total=len(documents),
                query=query.query,
                search_type=search_type,
                elapsed_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return SearchError(error=f"Search failed: {str(e)}")
    
    def _build_filter(self, query: SearchQuery) -> Optional[Dict[str, Any]]:
        """Build a filter dictionary from query parameters."""
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
            if keywords and not all(k in result.metadata.keywords for k in keywords):
                continue
            if title and title.lower() not in result.metadata.title.lower():
                continue
                
            filtered_results.append(result)
            
        return filtered_results


# Create singleton instance
search_tool = SearchTool() 