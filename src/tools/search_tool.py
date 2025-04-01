"""
Search tool for the DPRG Archive Agent.
"""
import time
import logging
import re
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
    
    def find_excerpt_with_terms(self, full_text: str, search_terms: List[str], max_length: int = 250) -> str:
        """
        Find an excerpt from the full text that contains at least one of the search terms.
        
        Args:
            full_text: The full document text
            search_terms: List of search terms to look for
            max_length: Maximum length of the excerpt
            
        Returns:
            An excerpt containing at least one search term, or a default excerpt if no terms found
        """
        if not full_text or not search_terms:
            return full_text[:max_length] if full_text else ""
        
        # Normalize text and search terms for case-insensitive matching
        full_text_lower = full_text.lower()
        
        # Process search terms - for short terms, only do exact matches
        # For longer terms (like keywords), allow partial matches
        search_terms_patterns = []
        for term in search_terms:
            if not term:
                continue
            term = term.lower()
            # For short terms (less than 5 chars), only match whole words
            if len(term) < 5:
                search_terms_patterns.append(rf'\b{re.escape(term)}\b')
            else:
                # For longer terms, also match partial words
                search_terms_patterns.append(re.escape(term))
        
        # Create a regex pattern with all search terms for efficient searching
        if not search_terms_patterns:
            return full_text[:max_length]
        
        pattern = r'|'.join(search_terms_patterns)
        
        # Find all matches
        matches = list(re.finditer(pattern, full_text_lower))
        if not matches:
            logger.debug(f"No matches found for terms {search_terms} in text: {full_text[:100]}...")
            # No match found, return beginning of text
            return full_text[:max_length]
        
        logger.debug(f"Found {len(matches)} matches for search terms in document")
        
        # Find the best match to use as center of excerpt
        best_match = matches[0]  # Start with first match
        best_term_count = 1
        
        # Try to find an excerpt that includes multiple search terms if possible
        for i, match in enumerate(matches):
            start_pos = max(0, match.start() - max_length // 2)
            end_pos = min(len(full_text), match.end() + max_length // 2)
            excerpt_lower = full_text_lower[start_pos:end_pos]
            
            # Count how many different search terms appear in this excerpt
            term_count = 0
            for term in search_terms:
                if term and term.lower() in excerpt_lower:
                    term_count += 1
            
            # If this excerpt contains more search terms than our current best, use it instead
            if term_count > best_term_count:
                best_match = match
                best_term_count = term_count
                # If we found an excerpt with all terms, no need to check further
                if term_count == len([t for t in search_terms if t]):
                    break
        
        # Create excerpt around the best match
        start_pos = max(0, best_match.start() - max_length // 2)
        end_pos = min(len(full_text), best_match.end() + max_length // 2)
        
        # Adjust to avoid cutting words
        if start_pos > 0:
            # Find the next space before the start position
            space_before = full_text.rfind(" ", 0, start_pos)
            if space_before >= 0:
                start_pos = space_before + 1
        
        if end_pos < len(full_text):
            # Find the next space after the end position
            space_after = full_text.find(" ", end_pos)
            if space_after >= 0:
                end_pos = space_after
        
        # Get the excerpt with the matched term
        excerpt = full_text[start_pos:end_pos]
        
        # Add ellipsis if needed
        if start_pos > 0:
            excerpt = "..." + excerpt
        if end_pos < len(full_text):
            excerpt = excerpt + "..."
        
        return excerpt
    
    async def search(self, query: SearchQuery) -> Union[SearchResponse, SearchError]:
        """
        Search for documents matching the query.
        """
        try:
            # Validate query - special case for metadata searches that might use "*" wildcard
            is_metadata_search = False
            if query.query == "*":
                is_metadata_search = True
                logger.info("Detected metadata search with wildcard query")
            elif not query.query:
                return SearchError(error="Query cannot be empty")
            elif len(query.query) > 1000:
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

            # Build filters from query fields, but save title for client-side filtering
            filters = query.metadata_filters or {}
            title_filter = None
            
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
                # Save title for client-side filtering
                title_filter = query.title
                # Don't add title to filters sent to Pinecone

            # Log actual query and filters for debugging
            logger.debug(f"Executing search with query: {query.query}")
            if filters:
                logger.debug(f"Using filters: {filters}")
            if title_filter:
                logger.debug(f"Will apply title filter client-side: {title_filter}")

            # Determine search type - explicit search_type parameter takes precedence
            search_type = "dense"
            if query.search_type:
                search_type = query.search_type
            elif query.use_hybrid:
                search_type = "hybrid"
            elif query.use_sparse:
                search_type = "sparse"
            elif query.use_dense:
                search_type = "dense"

            # Set default min_score if not provided
            min_score = query.min_score if query.min_score is not None else 0.7
            top_k = query.top_k if query.top_k else 10

            # If we have a title filter, increase top_k for initial search to ensure
            # we get enough results after client-side filtering
            server_top_k = top_k
            if title_filter:
                server_top_k = max(50, top_k * 3)  # Get more results to filter

            # Execute search based on type
            start_time = time.time()
            if search_type == "dense":
                results = await self.dense_search(query.query, filters=filters, top_k=server_top_k, min_score=min_score)
            elif search_type == "sparse":
                results = await self.sparse_search(query.query, filters=filters, top_k=server_top_k, min_score=min_score)
            else:  # hybrid
                results = await self.hybrid_search(query.query, filters=filters, top_k=server_top_k, min_score=min_score)
            elapsed_time = time.time() - start_time

            # Convert results to ArchiveDocument objects if necessary
            docs = []
            # Collect search terms from the query and keywords for excerpt highlighting
            search_terms = []
            
            if is_metadata_search:
                # For metadata search, prioritize the keywords/filters as search terms
                if query.keywords:
                    search_terms.extend(query.keywords)
                if title_filter:
                    search_terms.append(title_filter)
                # Add any other filter values that might be useful
                if query.author:
                    # Don't include author email as a search term normally
                    pass
            else:
                # Add the main query terms (split by spaces)
                search_terms.extend([term.strip() for term in query.query.split() if len(term.strip()) > 2])
                # Add keywords if provided
                if query.keywords:
                    search_terms.extend(query.keywords)
            
            # Log the search terms we'll be using for excerpts
            logger.debug(f"Using search terms for excerpts: {search_terms}")
                
            for result in results:
                try:
                    # Check if result is already an ArchiveDocument
                    if isinstance(result, ArchiveDocument):
                        doc = result
                    else:
                        # Convert dictionary to ArchiveDocument
                        doc = ArchiveDocument.from_pinecone_match(result)
                    
                    # Find a better excerpt that contains search terms
                    if doc.metadata and doc.metadata.text:
                        doc.text_excerpt = self.find_excerpt_with_terms(
                            doc.metadata.text, 
                            search_terms
                        )
                    
                    docs.append(doc)
                except Exception as e:
                    logger.error(f"Error converting result to ArchiveDocument: {e}")
                    continue

            # Apply title filter client-side if needed
            if title_filter and docs:
                filtered_docs = []
                for doc in docs:
                    if doc.metadata and doc.metadata.title and title_filter.lower() in doc.metadata.title.lower():
                        filtered_docs.append(doc)
                docs = filtered_docs
                
                # Ensure we only return top_k after filtering
                if len(docs) > top_k:
                    docs = docs[:top_k]

            # Return response
            response = SearchResponse(
                results=docs,
                total=len(docs),
                query=query.query,
                search_type=search_type,
                elapsed_time=elapsed_time
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
                # Get the ID based on whether it's an ArchiveDocument or dict
                result_id = result.id if isinstance(result, ArchiveDocument) else result.get('id')
                if result_id and result_id not in seen_ids:
                    seen_ids.add(result_id)
                    combined_results.append(result)
            
            # Sort by score and take top_k
            combined_results.sort(
                key=lambda x: x.score if isinstance(x, ArchiveDocument) else x.get('score', 0), 
                reverse=True
            )
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
            if title and result.metadata.title and title.lower() not in result.metadata.title.lower():
                continue
                
            filtered_results.append(result)
            
        return filtered_results


# Create singleton instance
search_tool = SearchTool() 
