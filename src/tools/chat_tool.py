"""
Chat tool for the DPRG Archive Agent.
"""
import logging
import time
from typing import List, Dict, Any, Optional
import asyncio

from src.schema.models import ChatRequest, ChatResponse, Message, Document
from src.utils.openai_client import get_chat_completion
from src.config import get_settings

# Set up logger
logger = logging.getLogger(__name__)

class ChatTool:
    """Tool for handling chat interactions."""
    
    def __init__(self):
        """Initialize the chat tool."""
        self.settings = get_settings()
    
    async def process(
        self,
        request: ChatRequest,
        search_type: Optional[str] = None,
        search_top_k: Optional[int] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> ChatResponse:
        """
        Process a chat request.
        
        Args:
            request: The chat request containing messages
            search_type: Type of search to perform (dense, sparse, hybrid)
            search_top_k: Number of top results to return
            temperature: Sampling temperature for response generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            ChatResponse containing the assistant's message
        """
        try:
            start_time = time.time()
            
            # Convert messages to OpenAI format
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in request.messages
            ]
            
            # Get chat completion using the synchronous client
            response = await get_chat_completion(
                messages=messages,
                model=self.settings.CHAT_MODEL,
                max_tokens=max_tokens or self.settings.CHAT_MAX_TOKENS,
                temperature=temperature or self.settings.CHAT_TEMPERATURE
            )
            
            # Extract assistant's message
            assistant_message = response.choices[0].message.content
            
            # Calculate elapsed time
            elapsed_time = time.time() - start_time
            
            # Return chat response
            return ChatResponse(
                message=Message(
                    role="assistant",
                    content=assistant_message
                ),
                referenced_documents=[],  # Empty list since we're not implementing document references yet
                elapsed_time=elapsed_time
            )
            
        except Exception as e:
            logger.error(f"Error processing chat request: {str(e)}")
            raise Exception(f"Error processing chat request: {str(e)}") 