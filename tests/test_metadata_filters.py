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
def dense_client():
    """Create a dense vector client for testing."""
    return DenseVectorClient()

@pytest.fixture
def sparse_client():
    """Create a sparse vector client for testing."""
    return SparseVectorClient()

@pytest.mark.asyncio
async def test_author_filter_dense(dense_client, load_test_documents):
    """Test author filtering in dense search."""
    async for _ in load_test_documents:
        query = SearchQuery(
            query="test document",
            author="test@example.com"
        )
        
        results = await dense_client.search(
            query=query.query,
            filter={"author": query.author}
        )
        
        # Should return at least one document by test@example.com
        assert len(results) > 0, "No results found for author filter"
        assert any(r['metadata']['author'] == "test@example.com" for r in results), "No documents found with specified author"
        assert all(r['metadata']['author'] == "test@example.com" for r in results), "Found documents with incorrect author"

@pytest.mark.asyncio
async def test_author_filter_sparse(sparse_client, load_test_documents):
    """Test author filtering in sparse search."""
    async for _ in load_test_documents:
        query = SearchQuery(
            query="test document",
            author="test@example.com"
        )
        
        results = await sparse_client.search(
            query=query.query,
            filter={"author": query.author}
        )
        
        # Should only return documents by test@example.com
        assert len(results) > 0
        assert all(r['metadata']['author'] == "test@example.com" for r in results)

@pytest.mark.asyncio
async def test_year_filter_dense(dense_client, load_test_documents):
    """Test year filtering in dense search."""
    async for _ in load_test_documents:
        query = SearchQuery(
            query="test document",
            year=2023
        )
        
        results = await dense_client.search(
            query=query.query,
            filter={"year": query.year}
        )
        
        # Should only return documents from 2023
        assert len(results) > 0
        assert all(r['metadata']['year'] == 2023 for r in results)

@pytest.mark.asyncio
async def test_year_filter_sparse(sparse_client, load_test_documents):
    """Test year filtering in sparse search."""
    async for _ in load_test_documents:
        query = SearchQuery(
            query="test document",
            year=2023
        )
        
        results = await sparse_client.search(
            query=query.query,
            filter={"year": query.year}
        )
        
        # Should only return documents from 2023
        assert len(results) > 0
        assert all(r['metadata']['year'] == 2023 for r in results)

@pytest.mark.asyncio
async def test_month_filter_dense(dense_client, load_test_documents):
    """Test month filtering in dense search."""
    async for _ in load_test_documents:
        query = SearchQuery(
            query="test document",
            month=1
        )
        
        results = await dense_client.search(
            query=query.query,
            filter={"month": query.month}
        )
        
        # Should only return documents from January
        assert len(results) > 0
        assert all(r['metadata']['month'] == 1 for r in results)

@pytest.mark.asyncio
async def test_month_filter_sparse(sparse_client, load_test_documents):
    """Test month filtering in sparse search."""
    async for _ in load_test_documents:
        query = SearchQuery(
            query="test document",
            month=1
        )
        
        results = await sparse_client.search(
            query=query.query,
            filter={"month": query.month}
        )
        
        # Should only return documents from January
        assert len(results) > 0
        assert all(r['metadata']['month'] == 1 for r in results)

@pytest.mark.asyncio
async def test_day_filter_dense(dense_client, load_test_documents):
    """Test day filtering in dense search."""
    async for _ in load_test_documents:
        query = SearchQuery(
            query="test document",
            day=15
        )
        
        results = await dense_client.search(
            query=query.query,
            filter={"day": query.day}
        )
        
        # Should only return documents from day 15
        assert len(results) > 0
        assert all(r['metadata']['day'] == 15 for r in results)

@pytest.mark.asyncio
async def test_day_filter_sparse(sparse_client, load_test_documents):
    """Test day filtering in sparse search."""
    async for _ in load_test_documents:
        query = SearchQuery(
            query="test document",
            day=15
        )
        
        results = await sparse_client.search(
            query=query.query,
            filter={"day": query.day}
        )
        
        # Should only return documents from day 15
        assert len(results) > 0
        assert all(r['metadata']['day'] == 15 for r in results)

@pytest.mark.asyncio
async def test_keywords_filter_dense(dense_client, load_test_documents):
    """Test keywords filtering in dense search."""
    async for _ in load_test_documents:
        query = SearchQuery(
            query="test document",
            keywords=["test", "document"]
        )
        
        results = await dense_client.search(
            query=query.query,
            filter={"keywords": {"$in": query.keywords}}
        )
        
        # Should only return documents with both keywords
        assert len(results) > 0
        assert all(all(k in r['metadata']['keywords'] for k in query.keywords) for r in results)

@pytest.mark.asyncio
async def test_keywords_filter_sparse(sparse_client, load_test_documents):
    """Test keywords filtering in sparse search."""
    async for _ in load_test_documents:
        query = SearchQuery(
            query="test document",
            keywords=["test", "document"]
        )
        
        results = await sparse_client.search(
            query=query.query,
            filter={"keywords": {"$in": query.keywords}}
        )
        
        # Should only return documents with both keywords
        assert len(results) > 0
        assert all(all(k in r['metadata']['keywords'] for k in query.keywords) for r in results)

@pytest.mark.asyncio
async def test_title_filter_dense(dense_client, load_test_documents):
    """Test title filtering in dense search."""
    async for _ in load_test_documents:
        query = SearchQuery(
            query="test document",
            title="Test Document 1"
        )
        
        results = await dense_client.search(
            query=query.query,
            filter={"title": query.title}
        )
        
        # Should only return documents with exact title match
        assert len(results) > 0
        assert all(r['metadata']['title'] == "Test Document 1" for r in results)

@pytest.mark.asyncio
async def test_title_filter_sparse(sparse_client, load_test_documents):
    """Test title filtering in sparse search."""
    async for _ in load_test_documents:
        query = SearchQuery(
            query="test document",
            title="Test Document 1"
        )
        
        results = await sparse_client.search(
            query=query.query,
            filter={"title": query.title}
        )
        
        # Should only return documents with exact title match
        assert len(results) > 0
        assert all(r['metadata']['title'] == "Test Document 1" for r in results)

@pytest.mark.asyncio
async def test_combined_filters_dense(dense_client, load_test_documents):
    """Test combined metadata filters in dense search."""
    async for _ in load_test_documents:
        query = SearchQuery(
            query="test document",
            author="test@example.com",
            year=2023,
            month=1
        )
        
        results = await dense_client.search(
            query=query.query,
            filter={
                "author": query.author,
                "year": query.year,
                "month": query.month
            }
        )
        
        # Should only return documents matching all criteria
        assert len(results) > 0
        assert all(
            r['metadata']['author'] == "test@example.com" and
            r['metadata']['year'] == 2023 and
            r['metadata']['month'] == 1
            for r in results
        )

@pytest.mark.asyncio
async def test_combined_filters_sparse(sparse_client, load_test_documents):
    """Test combined metadata filters in sparse search."""
    async for _ in load_test_documents:
        query = SearchQuery(
            query="test document",
            author="test@example.com",
            year=2023,
            month=1
        )
        
        results = await sparse_client.search(
            query=query.query,
            filter={
                "author": query.author,
                "year": query.year,
                "month": query.month
            }
        )
        
        # Should only return documents matching all criteria
        assert len(results) > 0
        assert all(
            r['metadata']['author'] == "test@example.com" and
            r['metadata']['year'] == 2023 and
            r['metadata']['month'] == 1
            for r in results
        )

@pytest.mark.asyncio
async def test_no_filters_dense(dense_client, load_test_documents):
    """Test dense search without any filters."""
    async for _ in load_test_documents:
        query = SearchQuery(query="test document")
        
        results = await dense_client.search(
            query=query.query,
            filter=None
        )
        
        # Should return all matching documents
        assert len(results) > 0

@pytest.mark.asyncio
async def test_no_filters_sparse(sparse_client, load_test_documents):
    """Test sparse search without any filters."""
    async for _ in load_test_documents:
        query = SearchQuery(query="test document")
        
        results = await sparse_client.search(
            query=query.query,
            filter=None
        )
        
        # Should return all matching documents
        assert len(results) > 0 