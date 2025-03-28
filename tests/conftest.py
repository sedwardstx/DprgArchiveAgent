"""
Test configuration and fixtures.
"""
import pytest
import asyncio
from typing import List, Dict, Any
from pinecone import Pinecone

from src.config import (
    PINECONE_API_KEY,
    DENSE_INDEX_NAME,
    SPARSE_INDEX_NAME,
    DENSE_INDEX_URL,
    SPARSE_INDEX_URL,
    PINECONE_NAMESPACE
)
from src.utils.embeddings import get_embedding, generate_sparse_vector

# Sample test documents with various metadata
TEST_DOCUMENTS = [
    {
        "id": "1",
        "text": "First test document",
        "metadata": {
            "author": "test@example.com",
            "year": 2023,
            "month": 1,
            "day": 15,
            "keywords": ["test", "document"],
            "title": "Test Document 1"
        }
    },
    {
        "id": "2",
        "text": "Second test document",
        "metadata": {
            "author": "another@example.com",
            "year": 2023,
            "month": 2,
            "day": 20,
            "keywords": ["test", "document", "second"],
            "title": "Test Document 2"
        }
    },
    {
        "id": "3",
        "text": "Third test document",
        "metadata": {
            "author": "test@example.com",
            "year": 2024,
            "month": 1,
            "day": 1,
            "keywords": ["test", "document", "third"],
            "title": "Test Document 3"
        }
    }
]

@pytest.fixture(scope="session")
def pinecone_client():
    """Create a Pinecone client for the test session."""
    return Pinecone(api_key=PINECONE_API_KEY)

@pytest.fixture(scope="session")
def dense_index(pinecone_client):
    """Get the dense index for testing."""
    return pinecone_client.Index(DENSE_INDEX_NAME, host=DENSE_INDEX_URL)

@pytest.fixture(scope="session")
def sparse_index(pinecone_client):
    """Get the sparse index for testing."""
    return pinecone_client.Index(SPARSE_INDEX_NAME, host=SPARSE_INDEX_URL)

@pytest.fixture(scope="session")
async def load_test_documents(dense_index, sparse_index):
    """Load test documents into both indices."""
    # Generate vectors for each document
    dense_vectors = []
    sparse_vectors = []
    
    for doc in TEST_DOCUMENTS:
        # Generate dense vector
        dense_vector = await get_embedding(doc['text'])
        
        # Generate sparse vector
        indices, values = await generate_sparse_vector(doc['text'])
        
        # Create dense vector record
        dense_vectors.append({
            'id': doc['id'],
            'values': dense_vector,
            'metadata': doc['metadata']
        })
        
        # Create sparse vector record
        sparse_vectors.append({
            'id': doc['id'],
            'sparse_values': {
                'indices': indices,
                'values': values
            },
            'metadata': doc['metadata']
        })
    
    # Upsert to indices
    try:
        dense_index.upsert(vectors=dense_vectors, namespace=PINECONE_NAMESPACE)
        sparse_index.upsert(vectors=sparse_vectors, namespace=PINECONE_NAMESPACE)
    except Exception as e:
        print(f"Error loading test documents: {str(e)}")
        raise
    
    yield
    
    # Clean up test documents
    try:
        dense_index.delete(ids=[doc['id'] for doc in TEST_DOCUMENTS], namespace=PINECONE_NAMESPACE)
        sparse_index.delete(ids=[doc['id'] for doc in TEST_DOCUMENTS], namespace=PINECONE_NAMESPACE)
    except Exception as e:
        print(f"Error cleaning up test documents: {str(e)}")
        raise 