"""
Search tool for the DPRG Archive Agent.
"""
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Union

from ..config import DEFAULT_TOP_K, MIN_SCORE_THRESHOLD
from ..schema.models import SearchQuery, ArchiveDocument, SearchResponse, SearchError
from ..utils.vector_store import dense_client, sparse_client, hybrid_client

# Set up logger
logger = logging.getLogger(__name__)


class SearchTool:
    """Tool for searching the DPRG archive."""
    
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
            # Determine search type
            if query.use_hybrid:
                search_type = "hybrid"
            elif query.use_sparse:
                search_type = "sparse"
            else:
                search_type = "dense"
                
            # Create filter based on metadata parameters
            filter_dict = {}
            
            if query.author:
                filter_dict["author"] = {"$eq": query.author}
                
            if query.year:
                filter_dict["year"] = {"$eq": query.year}
                
            if query.month:
                filter_dict["month"] = {"$eq": query.month}
                
            if query.day:
                filter_dict["day"] = {"$eq": query.day}
                
            if query.keywords and len(query.keywords) > 0:
                # Filter for documents that contain ALL specified keywords
                filter_dict["keywords"] = {"$all": query.keywords}
            
            # Set minimum score
            min_score = query.min_score or MIN_SCORE_THRESHOLD
            
            # Execute search based on type
            if search_type == "hybrid":
                results = await hybrid_client.search(
                    query=query.query,
                    top_k=query.top_k,
                    filter=filter_dict if filter_dict else None,
                    min_score=min_score,
                )
            elif search_type == "sparse":
                results = await sparse_client.search(
                    query=query.query,
                    top_k=query.top_k,
                    filter=filter_dict if filter_dict else None,
                )
            else:  # dense
                results = await dense_client.search(
                    query=query.query,
                    top_k=query.top_k,
                    filter=filter_dict if filter_dict else None,
                )
            
            # Convert results to ArchiveDocument objects
            documents = [ArchiveDocument.from_pinecone_match(match) for match in results]
            
            # Filter by minimum score if necessary
            if min_score > 0 and search_type != "hybrid":  # hybrid already filters
                documents = [doc for doc in documents if doc.score and doc.score >= min_score]
            
            # Create response
            response = SearchResponse(
                results=documents,
                total=len(documents),
                query=query.query,
                search_type=search_type,
                elapsed_time=time.time() - start_time,
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return SearchError(error=f"Search failed: {str(e)}")
    
    
    async def filter_by_metadata(
        self,
        results: List[ArchiveDocument],
        author: Optional[str] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        keywords: Optional[List[str]] = None,
    ) -> List[ArchiveDocument]:
        """
        Filter search results by metadata.
        
        Args:
            results: The search results to filter
            author: Filter by author
            year: Filter by year
            month: Filter by month
            day: Filter by day
            keywords: Filter by keywords (must contain all specified keywords)
            
        Returns:
            Filtered results
        """
        filtered = results
        
        if author:
            filtered = [doc for doc in filtered if doc.metadata.author == author]
            
        if year:
            filtered = [doc for doc in filtered if doc.metadata.year == year]
            
        if month:
            filtered = [doc for doc in filtered if doc.metadata.month == month]
            
        if day:
            filtered = [doc for doc in filtered if doc.metadata.day == day]
            
        if keywords and len(keywords) > 0:
            filtered = [
                doc for doc in filtered 
                if doc.metadata.keywords and all(kw in doc.metadata.keywords for kw in keywords)
            ]
            
        return filtered


# Create singleton instance
search_tool = SearchTool() 