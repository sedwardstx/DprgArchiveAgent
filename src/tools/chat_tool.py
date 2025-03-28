"""
Chat tool for interacting with the archive.
"""
from typing import List, Dict, Any, Optional, Union
import logging
import time
import openai
from openai import OpenAI

from ..config import OPENAI_API_KEY, CHAT_MODEL
from ..schema.models import (
    ChatMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionError,
    ArchiveDocument
)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Setup logging
logger = logging.getLogger(__name__)

class ChatTool:
    """Tool for chatting with the archive using OpenAI's chat models."""
    
    def __init__(self, model: str = CHAT_MODEL):
        """Initialize the chat tool.
        
        Args:
            model: The OpenAI model to use for chat
        """
        self.model = model
    
    async def chat(
        self,
        request: ChatCompletionRequest,
    ) -> Union[ChatCompletionResponse, ChatCompletionError]:
        """Generate a chat response based on the request.
        
        Args:
            request: The chat completion request
            
        Returns:
            ChatCompletionResponse with the response or ChatCompletionError if an error occurred
        """
        try:
            start_time = time.time()
            
            # Generate response
            response = client.chat.completions.create(
                model=request.model or self.model,
                messages=[msg.dict() for msg in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            # Create chat message from response
            message = ChatMessage(
                role="assistant",
                content=response.choices[0].message.content.strip()
            )
            
            # Create and return response
            return ChatCompletionResponse(
                message=message,
                referenced_documents=[],  # We'll add this functionality later
                elapsed_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            return ChatCompletionError(
                error=f"Chat failed: {str(e)}"
            ) 