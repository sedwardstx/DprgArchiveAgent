"""
Main agent for the DPRG Archive.
"""
import logging
import time
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
                # Search for relevant documents
                search_results = await self.search(query)
                
                if isinstance(search_results, SearchError):
                    return ChatCompletionError(
                        error=f"Search failed: {search_results.error}"
                    )
                
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
                request = query
            
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
                referenced_documents=[
                    ArchiveDocument(
                        id=doc.id,
                        text_excerpt=doc.text_excerpt,
                        metadata=ArchiveMetadata(
                            author=doc.metadata.get("author"),
                            title=doc.metadata.get("title"),
                            keywords=doc.metadata.get("keywords", [])
                        )
                    ) for doc in chat_response.referenced_documents
                ],
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
        # Format context into a string
        context_str = "\n\n".join([
            f"Document {i+1}:\n{doc.text_excerpt}"
            for i, doc in enumerate(documents)
        ])
        
        # Create system message with context
        return f"""You are a helpful assistant for the DPRG (Dallas Personal Robotics Group) archive.
        Answer questions based on the following context from the archive:
        
        {context_str}
        
        If you cannot find relevant information in the context, say so.
        Keep responses focused on the provided context."""


# Create singleton instance
archive_agent = ArchiveAgent() 