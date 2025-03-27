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
                
            if query.title:
                # For title, we want a partial match (containment)
                filter_dict["title"] = {"$eq": query.title}
                # Note: Pinecone doesn't support partial matching with $contains
                # We'll need to post-filter for partial matches
                need_title_post_filter = True
            else:
                need_title_post_filter = False
                
            if query.keywords and len(query.keywords) > 0:
                # Pinecone v6+ doesn't support $all, use $in instead and implement post-filtering
                # $in will match ANY of the keywords, then we'll filter for ALL later
                filter_dict["keywords"] = {"$in": query.keywords}
                # Remember that we need to post-filter results for ALL keywords
                need_post_keyword_filter = len(query.keywords) > 1
            else:
                need_post_keyword_filter = False
            
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
            
            # Post-process to enforce ALL keywords if needed
            if need_post_keyword_filter and query.keywords and len(query.keywords) > 1:
                logger.info(f"Post-filtering for ALL keywords: {query.keywords}")
                pre_keyword_filter_count = len(documents)
                documents = [
                    doc for doc in documents 
                    if doc.metadata.keywords and all(kw in doc.metadata.keywords for kw in query.keywords)
                ]
                post_keyword_filter_count = len(documents)
                logger.info(f"Keyword post-filtering: {pre_keyword_filter_count} -> {post_keyword_filter_count} documents")
            
            # Post-process for title partial matching if needed
            if need_title_post_filter and query.title:
                logger.info(f"Post-filtering for title containing: {query.title}")
                pre_title_filter_count = len(documents)
                documents = [
                    doc for doc in documents 
                    if doc.metadata.title and query.title.lower() in doc.metadata.title.lower()
                ]
                post_title_filter_count = len(documents)
                logger.info(f"Title post-filtering: {pre_title_filter_count} -> {post_title_filter_count} documents")
            
            # Filter by minimum score if necessary
            filtered_docs = documents
            if min_score > 0 and search_type != "hybrid":  # hybrid already filters
                pre_filter_count = len(documents)
                filtered_docs = [doc for doc in documents if doc.score and doc.score >= min_score]
                post_filter_count = len(filtered_docs)
                
                if pre_filter_count > 0 and post_filter_count == 0:
                    logger.warning(
                        f"All {pre_filter_count} results were filtered out by min_score={min_score}. "
                        f"Score range: {min([doc.score for doc in documents if doc.score]):.2f} - "
                        f"{max([doc.score for doc in documents if doc.score]):.2f}"
                    )
                    # Use original results but warn in logs
                    filtered_docs = documents
            
            # Create response
            response = SearchResponse(
                results=filtered_docs,
                total=len(filtered_docs),
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
        title: Optional[str] = None,
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
            title: Filter by title (partial match)
            
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

        if title:
            filtered = [
                doc for doc in filtered 
                if doc.metadata.title and title.lower() in doc.metadata.title.lower()
            ]
            
        return filtered


# Create singleton instance
search_tool = SearchTool() 