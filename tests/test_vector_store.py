"""
Tests for vector store clients.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.utils.vector_store import (
    DenseVectorClient,
    SparseVectorClient,
    HybridSearchClient
)
from src.schema.models import SearchResponse, ArchiveDocument, ArchiveMetadata

@pytest.fixture
def mock_pinecone():
    """Mock Pinecone client."""
    with patch('src.utils.vector_store.Pinecone') as mock:
        mock_instance = Mock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.mark.asyncio
async def test_sparse_vector_client_search(mock_pinecone):
    """Test sparse vector client search functionality."""
    # Setup mock response
    mock_response = Mock()
    mock_response.matches = [{
        'id': 'doc1',
        'score': 0.95,
        'metadata': {
            'text_excerpt': 'PDXbot implementation',
            'title': 'PDXbot Documentation'
        }
    }]
    mock_pinecone.Index.return_value.query.return_value = mock_response

    # Initialize client
    client = SparseVectorClient()

    # Test search
    results = await client.search("PDXbot")

    # Verify results
    assert len(results) == 1
    assert results[0]['id'] == 'doc1'
    assert results[0]['score'] == 0.95
    assert results[0]['metadata']['text_excerpt'] == 'PDXbot implementation'

@pytest.mark.asyncio
async def test_sparse_vector_client_empty_response(mock_pinecone):
    """Test sparse vector client handles empty response."""
    # Setup mock response with no matches
    mock_response = Mock()
    mock_response.matches = []
    mock_pinecone.Index.return_value.query.return_value = mock_response

    # Initialize client
    client = SparseVectorClient()

    # Test search
    results = await client.search("PDXbot")

    # Verify empty results
    assert len(results) == 0

@pytest.mark.asyncio
async def test_sparse_vector_client_error_handling(mock_pinecone):
    """Test sparse vector client error handling."""
    # Setup mock to raise exception
    mock_pinecone.Index.return_value.query.side_effect = Exception("Test error")

    # Initialize client
    client = SparseVectorClient()

    # Test search
    results = await client.search("PDXbot")
    assert len(results) == 0

@pytest.mark.asyncio
async def test_hybrid_search_client(mock_pinecone):
    """Test hybrid search client functionality."""
    # Setup mock responses
    mock_dense_response = Mock()
    mock_dense_response.matches = [{
        'id': 'doc1',
        'score': 0.9,
        'metadata': {
            'text_excerpt': 'PDXbot implementation',
            'title': 'PDXbot Documentation'
        }
    }]
    mock_sparse_response = Mock()
    mock_sparse_response.matches = [{
        'id': 'doc1',
        'score': 0.95,
        'metadata': {
            'text_excerpt': 'PDXbot implementation',
            'title': 'PDXbot Documentation'
        }
    }]

    # Mock both dense and sparse queries
    mock_index = mock_pinecone.Index.return_value
    mock_index.query.side_effect = [mock_dense_response, mock_sparse_response]

    # Initialize client
    client = HybridSearchClient()

    # Test hybrid search
    results = await client.search("PDXbot")

    # Verify results
    assert len(results) == 1
    assert results[0]['id'] == 'doc1'
    assert results[0]['score'] > 0.9  # Combined score should be higher

@pytest.mark.asyncio
async def test_dense_vector_client(mock_pinecone):
    """Test dense vector client functionality."""
    # Setup mock response
    mock_response = Mock()
    mock_response.matches = [{
        'id': 'doc1',
        'score': 0.9,
        'metadata': {
            'text_excerpt': 'PDXbot implementation',
            'title': 'PDXbot Documentation'
        }
    }]
    mock_pinecone.Index.return_value.query.return_value = mock_response

    # Initialize client
    client = DenseVectorClient()

    # Test search
    results = await client.search("PDXbot")

    # Verify results
    assert len(results) == 1
    assert results[0]['id'] == 'doc1'
    assert results[0]['score'] == 0.9
    assert results[0]['metadata']['text_excerpt'] == 'PDXbot implementation' 