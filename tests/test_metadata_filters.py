"""
Tests for metadata filtering in vector search clients.
"""
import pytest
import asyncio
from datetime import datetime
from typing import List, Dict, Any

from src.utils.vector_store import DenseVectorClient, SparseVectorClient
from src.schema.models import SearchQuery

@pytest.fixture
def dense_client(dense_vector_client):
    """Create a DenseVectorClient instance for testing."""
    return dense_vector_client

@pytest.fixture
def sparse_client(sparse_vector_client):
    """Create a SparseVectorClient instance for testing."""
    return sparse_vector_client

@pytest.mark.asyncio
async def test_author_filter_dense(dense_client, load_test_documents):
    """Test filtering by author in dense search."""
    client = await dense_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={"author": "test_author"},
        top_k=5
    )
    assert len(results) > 0
    for doc in results:
        assert doc.metadata.author == "test_author"

@pytest.mark.asyncio
async def test_author_filter_sparse(sparse_client, load_test_documents):
    """Test filtering by author in sparse search."""
    client = await sparse_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={"author": "test_author"},
        top_k=5
    )
    assert len(results) > 0
    for doc in results:
        assert doc.metadata.author == "test_author"

@pytest.mark.asyncio
async def test_year_filter_dense(dense_client, load_test_documents):
    """Test filtering by year in dense search."""
    client = await dense_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={"year": 2023},
        top_k=5
    )
    assert len(results) > 0
    for doc in results:
        assert doc.metadata.year == 2023

@pytest.mark.asyncio
async def test_year_filter_sparse(sparse_client, load_test_documents):
    """Test filtering by year in sparse search."""
    client = await sparse_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={"year": 2023},
        top_k=5
    )
    assert len(results) > 0
    for doc in results:
        assert doc.metadata.year == 2023

@pytest.mark.asyncio
async def test_month_filter_dense(dense_client, load_test_documents):
    """Test filtering by month in dense search."""
    client = await dense_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={"month": 1},
        top_k=5
    )
    assert len(results) > 0
    for doc in results:
        assert doc.metadata.month == 1

@pytest.mark.asyncio
async def test_month_filter_sparse(sparse_client, load_test_documents):
    """Test filtering by month in sparse search."""
    client = await sparse_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={"month": 1},
        top_k=5
    )
    assert len(results) > 0
    for doc in results:
        assert doc.metadata.month == 1

@pytest.mark.asyncio
async def test_day_filter_dense(dense_client, load_test_documents):
    """Test filtering by day in dense search."""
    client = await dense_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={"day": 1},
        top_k=5
    )
    assert len(results) > 0
    for doc in results:
        assert doc.metadata.day == 1

@pytest.mark.asyncio
async def test_day_filter_sparse(sparse_client, load_test_documents):
    """Test filtering by day in sparse search."""
    client = await sparse_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={"day": 1},
        top_k=5
    )
    assert len(results) > 0
    for doc in results:
        assert doc.metadata.day == 1

@pytest.mark.asyncio
async def test_keywords_filter_dense(dense_client, load_test_documents):
    """Test filtering by keywords in dense search."""
    client = await dense_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={"keywords": ["robotics", "test"]},
        top_k=5
    )
    assert len(results) > 0
    for doc in results:
        assert "robotics" in doc.metadata.keywords

@pytest.mark.asyncio
async def test_keywords_filter_sparse(sparse_client, load_test_documents):
    """Test filtering by keywords in sparse search."""
    client = await sparse_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={"keywords": ["robotics", "test"]},
        top_k=5
    )
    assert len(results) > 0
    for doc in results:
        assert "robotics" in doc.metadata.keywords

@pytest.mark.asyncio
async def test_title_filter_dense(dense_client, load_test_documents):
    """Test filtering by title in dense search."""
    client = await dense_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={"title": "Test Document 1"},
        top_k=5
    )
    assert len(results) > 0
    for doc in results:
        assert doc.metadata.title == "Test Document 1"

@pytest.mark.asyncio
async def test_title_filter_sparse(sparse_client, load_test_documents):
    """Test filtering by title in sparse search."""
    client = await sparse_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={"title": "Test Document 1"},
        top_k=5
    )
    assert len(results) > 0
    for doc in results:
        assert doc.metadata.title == "Test Document 1"

@pytest.mark.asyncio
async def test_combined_filters_dense(dense_client, load_test_documents):
    """Test combining multiple filters in dense search."""
    client = await dense_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={
            "author": "test_author",
            "year": 2023,
            "keywords": ["robotics"]
        },
        top_k=5
    )
    assert len(results) > 0
    for doc in results:
        assert doc.metadata.author == "test_author"
        assert doc.metadata.year == 2023
        assert "robotics" in doc.metadata.keywords

@pytest.mark.asyncio
async def test_combined_filters_sparse(sparse_client, load_test_documents):
    """Test combining multiple filters in sparse search."""
    client = await sparse_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={
            "author": "test_author",
            "year": 2023,
            "keywords": ["robotics"]
        },
        top_k=5
    )
    assert len(results) > 0
    for doc in results:
        assert doc.metadata.author == "test_author"
        assert doc.metadata.year == 2023
        assert "robotics" in doc.metadata.keywords

@pytest.mark.asyncio
async def test_no_filters_dense(dense_client, load_test_documents):
    """Test search without filters in dense search."""
    client = await dense_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={},
        top_k=5
    )
    assert len(results) > 0

@pytest.mark.asyncio
async def test_no_filters_sparse(sparse_client, load_test_documents):
    """Test search without filters in sparse search."""
    client = await sparse_client
    client.search.return_value = load_test_documents
    results = await client.search(
        query="robotics",
        filters={},
        top_k=5
    )
    assert len(results) > 0 