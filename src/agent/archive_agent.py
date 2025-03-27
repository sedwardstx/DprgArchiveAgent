"""
Main agent for the DPRG Archive.
"""
import logging
import time
from typing import Dict, List, Any, Optional, Union

from ..schema.models import (
    SearchQuery, SearchResponse, SearchError, ArchiveDocument,
    ChatMessage, ChatCompletionRequest, ChatCompletionResponse, ChatCompletionError
)
from ..tools.search_tool import search_tool
from ..utils.openai_client import get_chat_completion
from ..config import CHAT_SYSTEM_PROMPT

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
        request: ChatCompletionRequest
    ) -> Union[ChatCompletionResponse, ChatCompletionError]:
        """
        Process a chat request using RAG (Retrieval Augmented Generation).
        
        Args:
            request: Chat completion request with messages and parameters
            
        Returns:
            ChatCompletionResponse with generated message or ChatCompletionError
        """
        start_time = time.time()
        
        try:
            logger.info("Processing chat completion request")
            
            # Extract the last user message as the search query
            user_messages = [msg for msg in request.messages if msg.role == "user"]
            if not user_messages:
                return ChatCompletionError(error="No user messages found in the request")
                
            last_user_message = user_messages[-1].content
            
            # Perform search using the last user message
            logger.info(f"Searching for relevant documents using: '{last_user_message}'")
            search_query = SearchQuery(
                query=last_user_message,
                top_k=request.search_top_k or 5,
                use_dense=request.use_search_type == "dense",
                use_sparse=request.use_search_type == "sparse",
                use_hybrid=request.use_search_type == "hybrid",
            )
            
            search_result = await self.search(search_query)
            
            if isinstance(search_result, SearchError):
                logger.error(f"Search error: {search_result.error}")
                return ChatCompletionError(
                    error="Failed to retrieve relevant documents",
                    details={"search_error": search_result.error}
                )
                
            # Get the relevant documents from the search results
            retrieved_documents = search_result.results
            
            if not retrieved_documents:
                logger.warning("No relevant documents found in the archive")
            else:
                logger.info(f"Retrieved {len(retrieved_documents)} relevant documents")
                
            # Prepare system message with instructions and context
            system_message = {
                "role": "system",
                "content": self._build_system_prompt(retrieved_documents)
            }
            
            # Prepare chat messages for the completion request
            chat_messages = [system_message]
            
            # Include user conversation history
            for msg in request.messages:
                chat_messages.append({"role": msg.role, "content": msg.content})
                
            # Get completion from OpenAI
            completion = await get_chat_completion(
                messages=chat_messages,
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
            
            # Extract the response
            assistant_response = completion.choices[0].message.content
            
            # Create and return the response
            response = ChatCompletionResponse(
                message=ChatMessage(role="assistant", content=assistant_response),
                referenced_documents=retrieved_documents,
                elapsed_time=time.time() - start_time,
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error during chat completion: {str(e)}")
            return ChatCompletionError(error=f"Chat completion failed: {str(e)}")
    
    def _build_system_prompt(self, documents: List[ArchiveDocument]) -> str:
        """
        Build a system prompt with context from retrieved documents.
        
        Args:
            documents: List of retrieved documents to include as context
            
        Returns:
            System prompt with document context
        """
        # Start with the base system prompt
        prompt = CHAT_SYSTEM_PROMPT + "\n\n"
        
        # Add context from retrieved documents
        if documents:
            prompt += "Here are relevant documents from the DPRG archive that may help answer the user's question:\n\n"
            
            for i, doc in enumerate(documents, 1):
                title = doc.metadata.title or "Untitled Document"
                author = doc.metadata.author or "Unknown Author"
                date_info = ""
                
                if doc.metadata.year:
                    date_info = f"{doc.metadata.year}"
                    if doc.metadata.month:
                        date_info += f"-{doc.metadata.month}"
                        if doc.metadata.day:
                            date_info += f"-{doc.metadata.day}"
                
                prompt += f"Document {i}: {title}\n"
                prompt += f"Author: {author}\n"
                if date_info:
                    prompt += f"Date: {date_info}\n"
                prompt += f"Content: {doc.text_excerpt}\n\n"
        else:
            prompt += "No relevant documents were found in the DPRG archive for this query. " \
                      "Please inform the user that you don't have enough information to provide a specific answer " \
                      "based on the DPRG archive contents."
        
        return prompt


# Create singleton instance
archive_agent = ArchiveAgent() 