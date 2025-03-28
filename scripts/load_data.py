"""
Script to load data into Pinecone vector indices.
"""
import os
import json
import logging
import asyncio
from typing import List, Dict, Any
from tqdm import tqdm

from pinecone import Pinecone
from openai import OpenAI

from src.config import (
    PINECONE_API_KEY,
    OPENAI_API_KEY,
    DENSE_INDEX_NAME,
    SPARSE_INDEX_NAME,
    DENSE_INDEX_URL,
    SPARSE_INDEX_URL,
    PINECONE_NAMESPACE,
    EMBEDDING_MODEL
)
from src.utils.embeddings import get_embedding, generate_sparse_vector

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_documents(file_path: str) -> List[Dict[str, Any]]:
    """
    Load documents from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing documents
        
    Returns:
        List of documents
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def deduplicate_sparse_vector(indices: List[int], values: List[float]) -> tuple[List[int], List[float]]:
    """
    Deduplicate indices in a sparse vector by summing values for duplicate indices.
    
    Args:
        indices: List of indices
        values: List of values
        
    Returns:
        Tuple of (deduplicated indices, deduplicated values)
    """
    # Create a dictionary to store values for each index
    index_values = {}
    for idx, val in zip(indices, values):
        if idx in index_values:
            index_values[idx] += val
        else:
            index_values[idx] = val
    
    # Sort indices to maintain deterministic order
    sorted_indices = sorted(index_values.keys())
    sorted_values = [index_values[idx] for idx in sorted_indices]
    
    return sorted_indices, sorted_values

async def upsert_documents(
    documents: List[Dict[str, Any]],
    dense_index: Any,
    sparse_index: Any,
    batch_size: int = 100
) -> None:
    """
    Upsert documents into both dense and sparse indices.
    
    Args:
        documents: List of documents to upsert
        dense_index: Pinecone dense index
        sparse_index: Pinecone sparse index
        batch_size: Number of documents to process in each batch
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Process documents in batches
    for i in tqdm(range(0, len(documents), batch_size), desc="Processing documents"):
        batch = documents[i:i + batch_size]
        
        # Generate embeddings and sparse vectors
        dense_vectors = []
        sparse_vectors = []
        
        for doc in batch:
            # Generate dense vector
            dense_vector = await get_embedding(doc['text'])
            
            # Generate sparse vector
            indices, values = await generate_sparse_vector(doc['text'])
            
            # Deduplicate indices
            indices, values = deduplicate_sparse_vector(indices, values)
            
            # Convert indices and values to lists
            sparse_dict = {
                'indices': [int(idx) for idx in indices],
                'values': [float(val) for val in values]
            }
            
            dense_vectors.append({
                'id': doc['id'],
                'values': dense_vector,
                'metadata': {
                    'text': doc['text'],
                    'author': doc.get('author', ''),
                    'date': doc.get('date', ''),
                    'title': doc.get('title', ''),
                    'keywords': doc.get('keywords', [])
                }
            })
            
            sparse_vectors.append({
                'id': doc['id'],
                'sparse_values': sparse_dict,  # Use correct format with indices and values lists
                'metadata': {
                    'text': doc['text'],
                    'author': doc.get('author', ''),
                    'date': doc.get('date', ''),
                    'title': doc.get('title', ''),
                    'keywords': doc.get('keywords', [])
                }
            })
        
        # Upsert to dense index
        try:
            dense_index.upsert(vectors=dense_vectors, namespace=PINECONE_NAMESPACE)
        except Exception as e:
            logger.error(f"Error upserting to dense index: {str(e)}")
        
        # Upsert to sparse index
        try:
            sparse_index.upsert(vectors=sparse_vectors, namespace=PINECONE_NAMESPACE)
        except Exception as e:
            logger.error(f"Error upserting to sparse index: {str(e)}")

async def main():
    """Main function to load data into Pinecone indices."""
    # Initialize Pinecone client
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Get indices
    dense_index = pc.Index(DENSE_INDEX_NAME, host=DENSE_INDEX_URL)
    sparse_index = pc.Index(SPARSE_INDEX_NAME, host=SPARSE_INDEX_URL)
    
    # Load documents
    documents = load_documents('data/documents.json')
    logger.info(f"Loaded {len(documents)} documents")
    
    # Upsert documents
    await upsert_documents(documents, dense_index, sparse_index)
    
    # Print index statistics
    dense_stats = dense_index.describe_index_stats()
    sparse_stats = sparse_index.describe_index_stats()
    
    logger.info(f"Dense index stats: {dense_stats}")
    logger.info(f"Sparse index stats: {sparse_stats}")

if __name__ == '__main__':
    asyncio.run(main()) 