"""
OpenAI client utilities for the DPRG Archive Agent.
"""
import logging
import time
from typing import List, Dict, Any, Optional, Union

from openai import OpenAI
from openai.types.chat import ChatCompletion

from ..config import OPENAI_API_KEY, EMBEDDING_MODEL, CHAT_MODEL, CHAT_MAX_TOKENS, CHAT_TEMPERATURE

__all__ = ['openai_client', 'get_embedding', 'get_chat_completion']

# Set up logger
logger = logging.getLogger(__name__)

# Initialize the OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)


async def get_embedding(text: str) -> List[float]:
    """
    Get an embedding for a text string.
    
    Args:
        text: The text to embed
        
    Returns:
        Embedding vector as a list of floats
    """
    try:
        embedding_response = openai_client.embeddings.create(
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
    fallback_model: Optional[str] = None,
) -> ChatCompletion:
    """
    Get a chat completion from OpenAI.
    
    Args:
        messages: List of message objects with role and content
        model: Model to use for completion
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        fallback_model: Model to try if the primary model fails
        
    Returns:
        OpenAI ChatCompletion object
    """
    # Use provided parameters or fall back to defaults
    model_name = model or CHAT_MODEL
    tokens = max_tokens or CHAT_MAX_TOKENS
    temp = temperature if temperature is not None else CHAT_TEMPERATURE
    fb_model = fallback_model or "gpt-3.5-turbo"
    
    start_time = time.time()
    logger.info(f"Getting chat completion with model={model_name}, max_tokens={tokens}, temperature={temp}")
    
    # Run the synchronous call in a separate thread to avoid blocking
    from asyncio import get_event_loop
    loop = get_event_loop()
    
    try:
        response = await loop.run_in_executor(None, lambda: openai_client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=tokens,
            temperature=temp
        ))
        
        elapsed = time.time() - start_time
        logger.info(f"Chat completion completed in {elapsed:.2f}s with model {model_name}")
        
        return response
    except Exception as primary_error:
        logger.warning(f"Error with primary model {model_name}: {str(primary_error)}")
        
        if fb_model and fb_model != model_name:
            logger.info(f"Trying fallback model: {fb_model}")
            try:
                fallback_start_time = time.time()
                
                response = await loop.run_in_executor(None, lambda: openai_client.chat.completions.create(
                    model=fb_model,
                    messages=messages,
                    max_tokens=tokens,
                    temperature=temp
                ))
                
                elapsed = time.time() - fallback_start_time
                total_elapsed = time.time() - start_time
                logger.info(f"Fallback chat completion completed in {elapsed:.2f}s with model {fb_model} (total: {total_elapsed:.2f}s)")
                
                return response
            except Exception as fallback_error:
                logger.error(f"Error with fallback model {fb_model}: {str(fallback_error)}")
                raise fallback_error
        else:
            logger.error(f"No fallback model available or fallback is same as primary: {str(primary_error)}")
            raise primary_error 