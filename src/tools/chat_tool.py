"""
Chat tool for interacting with the DPRG archive.
"""
import logging
import time
from typing import List, Dict, Any, Optional

from src.schema.models import ChatRequest, ChatResponse, Message, ArchiveDocument
from src.utils.openai_client import get_chat_completion

# Set up logger
logger = logging.getLogger(__name__)

class ChatTool:
    """Tool for chat completion."""
    
    def __init__(self, openai_client=None):
        """
        Initialize the chat tool.
        
        Args:
            openai_client: Optional OpenAI client to use instead of the default
        """
        self.openai_client = openai_client
        logger.info("Chat tool initialized")
    
    async def process(
        self, 
        request: ChatRequest,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        search_type: Optional[str] = None,
        search_top_k: Optional[int] = None,
        model: Optional[str] = None,
        fallback_model: Optional[str] = None,
        log_level: Optional[str] = None
    ) -> ChatResponse:
        """
        Process a chat request.
        
        Args:
            request: The chat request
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            search_type: Optional search type override
            search_top_k: Optional search top_k override
            model: Optional model override
            fallback_model: Optional fallback model override
            log_level: Optional logging level override
            
        Returns:
            Chat response
            
        Raises:
            Exception: If there's an error during processing
        """
        start_time = time.time()
        
        # Set logging level if provided
        if log_level:
            log_level_value = getattr(logging, log_level.upper(), None)
            if log_level_value:
                logger.setLevel(log_level_value)
                logging.getLogger("src").setLevel(log_level_value)
                logger.debug(f"Set logging level to {log_level.upper()}")
        
        logger.info(f"Processing chat request with {len(request.messages)} messages")
        
        try:
            # Get completion
            completion = await self.get_completion(
                messages=request.messages,
                temperature=temperature or request.temperature,
                max_tokens=max_tokens or request.max_tokens,
                model=model or request.model,
                fallback_model=fallback_model or request.fallback_model
            )
            
            # Create response
            response = ChatResponse(
                message=Message(
                    role="assistant",
                    content=completion.choices[0].message.content
                ),
                elapsed_time=time.time() - start_time,
                referenced_documents=[]  # No documents referenced by default
            )
            
            logger.info(f"Chat completed in {response.elapsed_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error in chat process: {str(e)}")
            # Re-raise the exception with a more descriptive message
            raise Exception(f"Error processing chat request: {str(e)}")
    
    async def get_completion(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 500,
        model: str = "gpt-4",
        fallback_model: str = "gpt-3.5-turbo"
    ) -> Any:
        """
        Get chat completion from OpenAI.
        
        Args:
            messages: List of messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            model: Model to use
            fallback_model: Model to try if the primary model fails
            
        Returns:
            OpenAI chat completion
        """
        try:
            # If using provided client
            if self.openai_client:
                # Prepare messages in the format expected by OpenAI
                formatted_messages = [
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ]
                
                try:
                    # Get completion using provided client with primary model
                    response = await self.openai_client.chat.completions.create(
                        model=model,
                        messages=formatted_messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    
                    return response
                except Exception as primary_error:
                    logger.warning(f"Error with primary model {model}: {str(primary_error)}")
                    
                    if fallback_model and fallback_model != model:
                        logger.info(f"Trying fallback model: {fallback_model}")
                        # Try the fallback model
                        response = await self.openai_client.chat.completions.create(
                            model=fallback_model,
                            messages=formatted_messages,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                        
                        return response
                    else:
                        # Re-raise the original error
                        raise primary_error
            else:
                # Use the default client with fallback support
                return await get_chat_completion(
                    messages=[
                        {"role": msg.role, "content": msg.content}
                        for msg in messages
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    model=model,
                    fallback_model=fallback_model
                )
                
        except Exception as e:
            logger.error(f"Error getting chat completion: {str(e)}")
            raise 
