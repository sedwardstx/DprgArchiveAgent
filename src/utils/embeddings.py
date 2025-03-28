"""
Utility functions for generating embeddings.
"""
import time
import re
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import math

import numpy as np
import openai
from openai import OpenAI
from openai import AsyncOpenAI

from ..config import OPENAI_API_KEY, EMBEDDING_MODEL


# Initialize the OpenAI clients
client = OpenAI(api_key=OPENAI_API_KEY)
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# nltk stopwords (common English words to ignore)
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
    "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't",
    "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
    "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves"
}


def tokenize_text(text: str) -> List[str]:
    """
    Tokenization function for text that preserves technical terms.
    
    Args:
        text: The text to tokenize
        
    Returns:
        List of tokens
    """
    # Split on whitespace while preserving case
    tokens = text.split()
    
    # Remove stopwords but keep technical terms
    tokens = [t for t in tokens if t not in STOPWORDS]
    
    return tokens


def compute_idf(corpus_tokens: List[List[str]]) -> Dict[str, float]:
    """
    Compute Inverse Document Frequency (IDF) values.
    
    Args:
        corpus_tokens: A list of tokenized documents
        
    Returns:
        Dictionary mapping tokens to IDF values
    """
    # Number of documents
    N = len(corpus_tokens)
    
    # Count documents containing each token
    doc_freq = {}
    for doc_tokens in corpus_tokens:
        for token in set(doc_tokens):  # Use set to count each token only once per document
            doc_freq[token] = doc_freq.get(token, 0) + 1
    
    # Compute IDF value for each token
    idf = {}
    for token, freq in doc_freq.items():
        idf[token] = math.log((N + 1) / (freq + 1)) + 1  # Smoothed IDF
    
    return idf


async def generate_sparse_vector(text: str) -> Tuple[List[int], List[float]]:
    """
    Generate a sparse vector for text using a consistent hashing approach.
    
    Args:
        text: The text to convert to a sparse vector
        
    Returns:
        A tuple of (indices, values) representing the sparse vector
    """
    # Step 1: Tokenize the text while preserving case
    tokens = tokenize_text(text)
    
    # Step 2: Count term frequencies
    term_freq = Counter(tokens)
    
    # Step 3: Generate consistent indices and values
    indices = []
    values = []
    
    for token, count in term_freq.items():
        # Use a consistent hashing approach
        # Convert token to bytes and use first 4 bytes as index
        token_bytes = token.encode('utf-8')
        if len(token_bytes) >= 4:
            # Use first 4 bytes to generate index
            index = int.from_bytes(token_bytes[:4], byteorder='big') % 1000
        else:
            # For short tokens, pad with zeros
            padded_bytes = token_bytes + b'\x00' * (4 - len(token_bytes))
            index = int.from_bytes(padded_bytes, byteorder='big') % 1000
        
        # Calculate value using term frequency
        value = 1.0 + math.log(count)
        
        indices.append(index)
        values.append(value)
    
    return indices, values


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