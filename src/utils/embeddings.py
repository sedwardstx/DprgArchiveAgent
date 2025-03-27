"""
Utility functions for generating embeddings.
"""
import time
from typing import List, Dict, Any, Optional

import openai
from openai import OpenAI
from openai import AsyncOpenAI

from ..config import OPENAI_API_KEY, EMBEDDING_MODEL


# Initialize the OpenAI clients
client = OpenAI(api_key=OPENAI_API_KEY)
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def get_embedding(text: str, model: str = EMBEDDING_MODEL) -> List[float]:
    """
    Generate an embedding for the given text using the specified model.
    
    Args:
        text: The text to generate an embedding for
        model: The embedding model to use
        
    Returns:
        A list of floats representing the embedding
    """
    # Ensure the text is not empty
    if not text.strip():
        raise ValueError("Cannot generate embedding for empty text")
    
    # Truncate text if it's too long (text-embedding-3-large has a 8191 token limit)
    if len(text) > 32000:  # Approximation, not exact token counting
        text = text[:32000]
    
    try:
        response = await async_client.embeddings.create(
            model=model,
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding
    except Exception as e:
        raise Exception(f"Error generating embedding: {str(e)}")


async def get_embeddings(texts: List[str], model: str = EMBEDDING_MODEL) -> List[List[float]]:
    """
    Generate embeddings for multiple texts.
    
    Args:
        texts: List of texts to generate embeddings for
        model: The embedding model to use
        
    Returns:
        A list of embeddings, where each embedding is a list of floats
    """
    if not texts:
        return []
    
    # Filter out empty texts
    valid_texts = [t for t in texts if t.strip()]
    
    if not valid_texts:
        return []
    
    try:
        response = await async_client.embeddings.create(
            model=model,
            input=valid_texts,
            encoding_format="float"
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        raise Exception(f"Error generating embeddings: {str(e)}")


def calculate_embedding_cost(num_tokens: int, model: str = EMBEDDING_MODEL) -> float:
    """
    Calculate the cost of generating embeddings.
    
    Args:
        num_tokens: The number of tokens to embed
        model: The embedding model
        
    Returns:
        The cost in USD
    """
    # text-embedding-3-large price per 1K tokens (May 2024)
    if model == "text-embedding-3-large":
        return (num_tokens / 1000) * 0.00013
    # text-embedding-3-small price per 1K tokens
    elif model == "text-embedding-3-small":
        return (num_tokens / 1000) * 0.00002
    # Default to ada v2 pricing
    else:
        return (num_tokens / 1000) * 0.0001 