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
    ) -> ChatResponse:
        """
        Process a chat request.
        
        Args:
            request: The chat request
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            search_type: Optional search type override
            search_top_k: Optional search top_k override
            
        Returns:
            Chat response
            
        Raises:
            Exception: If there's an error during processing
        """
        start_time = time.time()
        logger.info(f"Processing chat request with {len(request.messages)} messages")
        
        try:
            # Get completion
            completion = await self.get_completion(
                messages=request.messages,
                temperature=temperature or request.temperature,
                max_tokens=max_tokens or request.max_tokens,
                model=request.model
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
        model: str = "gpt-4"
    ) -> Any:
        """
        Get chat completion from OpenAI.
        
        Args:
            messages: List of messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            model: Model to use
            
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
                
                # Get completion using provided client
                response = await self.openai_client.chat.completions.create(
                    model=model,
                    messages=formatted_messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                return response
            else:
                # Use the default client
                return await get_chat_completion(
                    messages=[
                        {"role": msg.role, "content": msg.content}
                        for msg in messages
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    model=model
                )
                
        except Exception as e:
            logger.error(f"Error getting chat completion: {str(e)}")
            raise 
