"""
Main agent for the DPRG Archive. 
"""
import logging
import time
import re
from typing import Dict, List, Any, Optional, Union

from ..schema.models import (
    SearchQuery, SearchResponse, SearchError, ArchiveDocument,
    ChatMessage, ChatCompletionRequest, ChatCompletionResponse, ChatCompletionError,
    ChatRequest, Message
)
from ..tools.search_tool import SearchTool
from ..tools.chat_tool import ChatTool
from ..utils.openai_client import get_chat_completion
from ..config import CHAT_SYSTEM_PROMPT

# Set up logger
logger = logging.getLogger(__name__)


class ArchiveAgent:
    """
    Agent for searching and querying the DPRG archive.
    """
    
    def __init__(self, search_tool: Optional[SearchTool] = None, chat_tool: Optional[ChatTool] = None):
        """
        Initialize the archive agent.
        
        Args:
            search_tool: Optional SearchTool instance
            chat_tool: Optional ChatTool instance
        """
        self.search_tool = search_tool or SearchTool()
        self.chat_tool = chat_tool or ChatTool()
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
        min_score: Optional[float] = 0.0,  # Use a default of 0.0 for metadata searches
    ) -> Union[SearchResponse, SearchError]:
        """
        Search the DPRG archive by metadata only.
        
        This function allows searching documents based solely on their metadata attributes
        without requiring a text query. Unlike semantic searches, metadata searches use
        a default min_score of 0.0 to ensure that all documents matching the metadata
        criteria are returned, regardless of their semantic relevance scores.
        
        Args:
            author: Filter by author (email address preferred)
            year: Filter by year
            month: Filter by month
            day: Filter by day
            keywords: Filter by keywords
            title: Filter by title (partial match)
            top_k: Number of results to return
            min_score: Minimum score threshold (defaults to 0.0 for metadata searches)
            
        Returns:
            SearchResponse with results or SearchError if an error occurred
        """
        # If we're searching by title, use it as the query to get better semantic matches
        query_text = title if title else "*"
        
        # For title searches, we want to use a regular query as it will work better
        # than the metadata filter
        if title:
            logger.info(f"Metadata search with title as query: {title}")
        else:
            logger.info("Metadata search with wildcard query")
        
        # Construct a query with metadata filters
        search_query = SearchQuery(
            query=query_text,  # Use title as query if available
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
        
        return await self.search(search_query)
    
    async def chat(
        self,
        query: Union[str, ChatCompletionRequest],
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Union[ChatCompletionResponse, ChatCompletionError]:
        """
        Generate a chat response.
        
        Args:
            query: The query string or chat request
            temperature: Sampling temperature for response generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            The chat response
        """
        try:
            # If query is a string, perform search and build context
            if isinstance(query, str):
                # Extract possible metadata filters from the query
                author_filter = None
                title_filter = None
                year_filter = None
                keyword_filters = []
                
                # Extract author information if present
                if "by " in query.lower() and "@" in query:
                    # Find email addresses which are likely author identifiers
                    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', query)
                    if email_match:
                        author_filter = email_match.group(0)
                        logger.info(f"Extracted author filter: {author_filter}")
                
                # Extract title information if mentioned
                title_indicators = ["titled", "with title", "title", "called", "name", '"', "'"]
                for indicator in title_indicators:
                    if indicator in query.lower():
                        # Extract text in quotes if present
                        quote_match = re.search(r'["\'](.+?)["\']', query)
                        if quote_match:
                            title_filter = quote_match.group(1)
                            logger.info(f"Extracted title filter from quotes: {title_filter}")
                            break
                        
                        # Try to find title after the indicator
                        parts = query.lower().split(indicator, 1)
                        if len(parts) > 1 and len(parts[1].strip()) > 3:
                            # Use the next few words as a potential title
                            potential_title = parts[1].strip().split()[:4]
                            title_filter = " ".join(potential_title)
                            logger.info(f"Extracted potential title filter: {title_filter}")
                            break
                
                # Check for specific keywords that might be important
                important_keywords = ["robotic", "presentation", "meeting", "contest", "competition"]
                for keyword in important_keywords:
                    if keyword.lower() in query.lower():
                        keyword_filters.append(keyword)
                        logger.info(f"Added keyword filter: {keyword}")
                
                # Extract year if present (4 digits that could be a year)
                year_match = re.search(r'\b(19\d{2}|20\d{2})\b', query)
                if year_match:
                    year_filter = int(year_match.group(1))
                    logger.info(f"Extracted year filter: {year_filter}")
                
                # Now create a search query with these filters for better context
                search_query = SearchQuery(
                    query=query,
                    search_type="hybrid",
                    min_score=0.3,  # Lower threshold for chat context
                    top_k=10,       # Retrieve more documents for better context
                    author=author_filter,
                    title=title_filter,
                    year=year_filter,
                    keywords=keyword_filters if keyword_filters else None
                )
                
                # If we have specific metadata filters but no good query text,
                # consider doing a metadata search instead
                if (author_filter or title_filter or keyword_filters) and len(query.split()) > 10:
                    logger.info("Using extracted metadata for searching instead of full query")
                    # Create a shortened, more focused query from the metadata
                    focused_query = " ".join([k for k in keyword_filters])
                    if title_filter:
                        focused_query = f"{focused_query} {title_filter}"
                    search_query.query = focused_query if focused_query.strip() else query
                
                # Perform the search with the enhanced filters
                logger.info(f"Searching with query: {search_query.query} and filters: author={search_query.author}, title={search_query.title}, keywords={search_query.keywords}")
                search_results = await self.search(search_query)
                
                if isinstance(search_results, SearchError):
                    return ChatCompletionError(
                        error=f"Search failed: {search_results.error}"
                    )
                
                # Check if any documents were found
                if not search_results.results:
                    logger.warning(f"No relevant documents found for query: {query}")
                    
                    # Try a fallback search with just the metadata if we have specific filters
                    if author_filter or title_filter or year_filter or keyword_filters:
                        logger.info("Trying metadata-only search as fallback")
                        metadata_results = await self.search_by_metadata(
                            author=author_filter,
                            title=title_filter,
                            year=year_filter,
                            keywords=keyword_filters if keyword_filters else None,
                            top_k=10,
                            min_score=0.0  # No threshold for metadata search
                        )
                        
                        if not isinstance(metadata_results, SearchError) and metadata_results.results:
                            logger.info(f"Fallback metadata search found {len(metadata_results.results)} results")
                            search_results = metadata_results
                
                # Build system prompt with context
                system_prompt = self._build_system_prompt(search_results.results)
                
                # Create chat request
                request = ChatCompletionRequest(
                    messages=[
                        ChatMessage(role="system", content=system_prompt),
                        ChatMessage(role="user", content=query)
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                # Use the request as provided but search with its parameters
                request = query
                
                # Extract the user's query from the messages
                user_query = ""
                for msg in request.messages:
                    if msg.role == "user":
                        user_query = msg.content
                        break
                
                if user_query:
                    # Extract possible metadata filters from the query (same as above)
                    author_filter = None
                    title_filter = None
                    year_filter = None
                    keyword_filters = []
                    
                    # Extract author information if present
                    if "by " in user_query.lower() and "@" in user_query:
                        # Find email addresses which are likely author identifiers
                        email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', user_query)
                        if email_match:
                            author_filter = email_match.group(0)
                            logger.info(f"Extracted author filter: {author_filter}")
                    
                    # Extract title information if mentioned
                    title_indicators = ["titled", "with title", "title", "called", "name", '"', "'"]
                    for indicator in title_indicators:
                        if indicator in user_query.lower():
                            # Extract text in quotes if present
                            quote_match = re.search(r'["\'](.+?)["\']', user_query)
                            if quote_match:
                                title_filter = quote_match.group(1)
                                logger.info(f"Extracted title filter from quotes: {title_filter}")
                                break
                            
                            # Try to find title after the indicator
                            parts = user_query.lower().split(indicator, 1)
                            if len(parts) > 1 and len(parts[1].strip()) > 3:
                                # Use the next few words as a potential title
                                potential_title = parts[1].strip().split()[:4]
                                title_filter = " ".join(potential_title)
                                logger.info(f"Extracted potential title filter: {title_filter}")
                                break
                    
                    # Check for specific keywords that might be important
                    important_keywords = ["robotic", "presentation", "meeting", "contest", "competition"]
                    for keyword in important_keywords:
                        if keyword.lower() in user_query.lower():
                            keyword_filters.append(keyword)
                            logger.info(f"Added keyword filter: {keyword}")
                    
                    # Extract year if present (4 digits that could be a year)
                    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', user_query)
                    if year_match:
                        year_filter = int(year_match.group(1))
                        logger.info(f"Extracted year filter: {year_filter}")
                    
                    # Use min_score from the request or default to 0.3
                    min_score_value = request.min_score if hasattr(request, 'min_score') and request.min_score is not None else 0.3
                    
                    # Create a search query with these filters for better context
                    search_query = SearchQuery(
                        query=user_query,
                        search_type=request.use_search_type or "hybrid",
                        min_score=min_score_value,
                        top_k=request.search_top_k or 10,
                        author=author_filter,
                        title=title_filter,
                        year=year_filter,
                        keywords=keyword_filters if keyword_filters else None
                    )
                    
                    # Perform the search with enhanced filters
                    logger.info(f"Searching with query: {search_query.query} and filters: author={search_query.author}, title={search_query.title}, keywords={search_query.keywords}")
                    search_results = await self.search(search_query)
                    
                    if isinstance(search_results, SearchError):
                        return ChatCompletionError(
                            error=f"Search failed: {search_results.error}"
                        )
                    
                    # Check if any documents were found
                    if not search_results.results:
                        logger.warning(f"No relevant documents found for query: {user_query}")
                        
                        # Try a fallback search with just the metadata if we have specific filters
                        if author_filter or title_filter or year_filter or keyword_filters:
                            logger.info("Trying metadata-only search as fallback")
                            metadata_results = await self.search_by_metadata(
                                author=author_filter,
                                title=title_filter,
                                year=year_filter,
                                keywords=keyword_filters if keyword_filters else None,
                                top_k=10,
                                min_score=0.0  # No threshold for metadata search
                            )
                            
                            if not isinstance(metadata_results, SearchError) and metadata_results.results:
                                logger.info(f"Fallback metadata search found {len(metadata_results.results)} results")
                                search_results = metadata_results
                    
                    # Build system prompt with context
                    system_prompt = self._build_system_prompt(search_results.results)
                    
                    # Replace the system message if it exists, or add it if it doesn't
                    has_system_message = False
                    for i, msg in enumerate(request.messages):
                        if msg.role == "system":
                            request.messages[i] = ChatMessage(role="system", content=system_prompt)
                            has_system_message = True
                            break
                    
                    if not has_system_message:
                        # Add the system message at the beginning
                        request.messages.insert(0, ChatMessage(role="system", content=system_prompt))
                else:
                    # No user message found, use a default system prompt
                    search_results = SearchResponse(query="", search_type="", results=[], total=0, elapsed_time=0)
            
            # Convert ChatCompletionRequest to ChatRequest for ChatTool
            chat_request = ChatRequest(
                messages=[Message(role=msg.role, content=msg.content) for msg in request.messages],
                model=request.model or "gpt-4",
                max_tokens=request.max_tokens or max_tokens,
                temperature=request.temperature or temperature,
                search_top_k=request.search_top_k or 5,
                use_search_type=request.use_search_type or "dense"
            )
            
            # Generate chat response using the process method
            chat_response = await self.chat_tool.process(
                request=chat_request,
                temperature=chat_request.temperature,
                max_tokens=chat_request.max_tokens,
                search_type=chat_request.use_search_type,
                search_top_k=chat_request.search_top_k
            )
            
            # Convert ChatResponse to ChatCompletionResponse
            return ChatCompletionResponse(
                message=ChatMessage(
                    role=chat_response.message.role,
                    content=chat_response.message.content
                ),
                referenced_documents=search_results.results if 'search_results' in locals() else [],
                elapsed_time=chat_response.elapsed_time
            )
            
        except Exception as e:
            logger.error(f"Error during chat: {str(e)}")
            return ChatCompletionError(
                error=f"Chat failed: {str(e)}"
            )
    
    def _build_system_prompt(self, documents: List[ArchiveDocument]) -> str:
        """
        Build a system prompt with context from retrieved documents.
        
        Args:
            documents: List of relevant documents from the archive
            
        Returns:
            System prompt with context
        """
        if not documents:
            # No documents found, provide a general instruction
            return """You are a helpful assistant for the DPRG (Dallas Personal Robotics Group) archive.
            
            I could not find any specific information in the archive that matches your query.
            If you're asking about a specific topic, I may not have access to that information.
            
            However, I can provide general information about DPRG, robotics concepts, or suggest related topics.
            Please let me know if you'd like to ask about something else."""
        
        # Format context into a string
        context_str = "\n\n".join([
            f"Document {i+1}:\nTitle: {doc.metadata.title if hasattr(doc.metadata, 'title') else 'Unknown'}\n" +
            f"Author: {doc.metadata.author if hasattr(doc.metadata, 'author') else 'Unknown'}\n" +
            f"Content: {doc.text_excerpt}"
            for i, doc in enumerate(documents)
        ])
        
        # Create system message with context
        return f"""You are a helpful assistant for the DPRG (Dallas Personal Robotics Group) archive.
        Answer questions based on the following context from the archive:
        
        {context_str}
        
        If you cannot find the specific information requested in the context, say so clearly, but try to provide the most relevant information from what's available.
        Focus on information from the provided documents, and be specific about what document contains which information."""


# Create singleton instance
archive_agent = ArchiveAgent() 