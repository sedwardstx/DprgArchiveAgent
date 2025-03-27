"""
OpenAI client utilities for the DPRG Archive Agent.
"""
import logging
import time
from typing import List, Dict, Any, Optional, Union

from openai import OpenAI
from openai.types.chat import ChatCompletion

from ..config import OPENAI_API_KEY, EMBEDDING_MODEL, CHAT_MODEL, CHAT_MAX_TOKENS, CHAT_TEMPERATURE

# Set up logger
logger = logging.getLogger(__name__)

# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


async def get_embedding(text: str) -> List[float]:
    """
    Get an embedding for a text string.
    
    Args:
        text: The text to embed
        
    Returns:
        Embedding vector as a list of floats
    """
    try:
        embedding_response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return embedding_response.data[0].embedding
    except Exception as e:
        logger.error(f"Error getting embedding: {str(e)}")
        raise


async def get_chat_completion(
    messages: List[Dict[str, str]], 
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
) -> ChatCompletion:
    """
    Get a chat completion from OpenAI.
    
    Args:
        messages: List of message objects with role and content
        model: Model to use for completion
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        
    Returns:
        OpenAI ChatCompletion object
    """
    try:
        start_time = time.time()
        
        # Use provided parameters or fall back to defaults
        model_name = model or CHAT_MODEL
        tokens = max_tokens or CHAT_MAX_TOKENS
        temp = temperature if temperature is not None else CHAT_TEMPERATURE
        
        logger.info(f"Getting chat completion with model={model_name}, max_tokens={tokens}, temperature={temp}")
        
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=tokens,
            temperature=temp
        )
        
        elapsed = time.time() - start_time
        logger.info(f"Chat completion completed in {elapsed:.2f}s")
        
        return response
    except Exception as e:
        logger.error(f"Error getting chat completion: {str(e)}")
        raise 