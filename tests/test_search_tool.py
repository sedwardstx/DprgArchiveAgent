"""
Tests for the search tool functionality.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.tools.search_tool import SearchTool
from src.schema.models import SearchQuery, SearchResponse, SearchError, ArchiveDocument, ArchiveMetadata

@pytest.fixture
async def search_tool(dense_vector_client, sparse_vector_client):
    """Create a SearchTool instance for testing."""
    return SearchTool(dense_vector_client, sparse_vector_client)

@pytest.fixture
async def load_test_documents(dense_vector_client, sparse_vector_client):
    """Load test documents for search."""
    test_docs = [
        ArchiveDocument(
            id=f"doc{i}",
            text_excerpt=f"Test document {i} about robotics",
            metadata=ArchiveMetadata(
                author="test_author",
                year=2023,
                month=1,
                day=1,
                keywords=["test", "robotics"],
                title=f"Test Document {i}"
            ),
            score=0.9 - (i * 0.1)
        ) for i in range(10)
    ]
    
    dense_vector_client.search.return_value = test_docs
    sparse_vector_client.search.return_value = test_docs
    return test_docs

@pytest.mark.asyncio
async def test_search_tool_basic(search_tool, dense_vector_client, sparse_vector_client):
    """Test basic search functionality."""
    tool = await search_tool
    dense_client = await dense_vector_client
    sparse_client = await sparse_vector_client
    
    dense_client.search.return_value = [
        ArchiveDocument(
            id="1",
            text_excerpt="Test document 1",
            metadata=ArchiveMetadata(
                author="test@example.com",
                year=2023,
                month=1,
                day=1,
                keywords=["test"],
                title="Test Document 1"
            )
        )
    ]
    sparse_client.search.return_value = []

    query = SearchQuery(query="test document")
    response = await tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1
    assert response.results[0].text_excerpt == "Test document 1"

@pytest.mark.asyncio
async def test_search_tool_with_filters(search_tool, dense_vector_client, sparse_vector_client):
    """Test search with metadata filters."""
    tool = await search_tool
    dense_client = await dense_vector_client
    sparse_client = await sparse_vector_client
    
    dense_client.search.return_value = [
        ArchiveDocument(
            id="1",
            text_excerpt="Test document 1",
            metadata=ArchiveMetadata(
                author="test@example.com",
                year=2023,
                month=1,
                day=1,
                keywords=["test"],
                title="Test Document 1"
            )
        )
    ]
    sparse_client.search.return_value = []

    query = SearchQuery(
        query="test document",
        author="test@example.com",
        year=2023,
        month=1,
        day=1,
        keywords=["test"],
        title="Test Document 1"
    )
    response = await tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1
    assert response.results[0].metadata.author == "test@example.com"

@pytest.mark.asyncio
async def test_search_tool_with_search_types(search_tool, dense_vector_client, sparse_vector_client):
    """Test search with different search types."""
    tool = await search_tool
    dense_client = await dense_vector_client
    sparse_client = await sparse_vector_client
    
    dense_client.search.return_value = [
        ArchiveDocument(
            id="1",
            text_excerpt="Test document 1",
            metadata=ArchiveMetadata(
                author="test@example.com",
                year=2023,
                month=1,
                day=1,
                keywords=["test"],
                title="Test Document 1"
            )
        )
    ]
    sparse_client.search.return_value = []

    # Test dense search
    query = SearchQuery(query="test document", search_type="dense")
    response = await tool.search(query)
    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1

    # Test sparse search
    query = SearchQuery(query="test document", search_type="sparse")
    response = await tool.search(query)
    assert isinstance(response, SearchResponse)

    # Test hybrid search
    query = SearchQuery(query="test document", search_type="hybrid")
    response = await tool.search(query)
    assert isinstance(response, SearchResponse)

@pytest.mark.asyncio
async def test_search_tool_with_min_score(search_tool, dense_vector_client, sparse_vector_client):
    """Test search with minimum score threshold."""
    tool = await search_tool
    dense_client = await dense_vector_client
    sparse_client = await sparse_vector_client
    
    dense_client.search.return_value = [
        ArchiveDocument(
            id="1",
            text_excerpt="Test document 1",
            metadata=ArchiveMetadata(
                author="test@example.com",
                year=2023,
                month=1,
                day=1,
                keywords=["test"],
                title="Test Document 1"
            ),
            score=0.9
        )
    ]
    sparse_client.search.return_value = []

    query = SearchQuery(query="test document", min_score=0.8)
    response = await tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1
    assert response.results[0].score >= 0.8

@pytest.mark.asyncio
async def test_search_tool_with_top_k(search_tool, dense_vector_client, sparse_vector_client):
    """Test search with top_k parameter."""
    tool = await search_tool
    dense_client = await dense_vector_client
    sparse_client = await sparse_vector_client
    
    dense_client.search.return_value = [
        ArchiveDocument(
            id=str(i),
            text_excerpt=f"Test document {i}",
            metadata=ArchiveMetadata(
                author="test@example.com",
                year=2023,
                month=1,
                day=1,
                keywords=["test"],
                title=f"Test Document {i}"
            )
        )
        for i in range(10)
    ]
    sparse_client.search.return_value = []

    query = SearchQuery(query="test document", top_k=5)
    response = await tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 5

@pytest.mark.asyncio
async def test_search_tool_error_handling(search_tool):
    """Test error handling for invalid inputs."""
    tool = await search_tool
    with pytest.raises(ValueError):
        await tool.search(SearchQuery(query=""))

    with pytest.raises(ValueError):
        await tool.search(SearchQuery(query="test document", search_type="invalid"))

@pytest.mark.asyncio
async def test_search_tool_with_empty_results(search_tool, dense_vector_client, sparse_vector_client):
    """Test handling of queries that return no results."""
    tool = await search_tool
    dense_client = await dense_vector_client
    sparse_client = await sparse_vector_client
    
    dense_client.search.return_value = []
    sparse_client.search.return_value = []

    query = SearchQuery(query="xyzabc123nonexistent")
    response = await tool.search(query)

    assert len(response.results) == 0
    assert response.total == 0

@pytest.mark.asyncio
async def test_search_tool_with_special_characters(search_tool, dense_vector_client, sparse_vector_client):
    """Test handling of special characters in query."""
    tool = await search_tool
    dense_client = await dense_vector_client
    sparse_client = await sparse_vector_client
    
    dense_client.search.return_value = [
        ArchiveDocument(
            id="1",
            text_excerpt="Test document 1",
            metadata=ArchiveMetadata(
                author="test@example.com",
                year=2023,
                month=1,
                day=1,
                keywords=["test"],
                title="Test Document 1"
            )
        )
    ]
    sparse_client.search.return_value = []

    query = SearchQuery(query="test!@#$%^&*()")
    response = await tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1

@pytest.mark.asyncio
async def test_search_tool_with_unicode(search_tool, dense_vector_client, sparse_vector_client):
    """Test handling of Unicode characters in query."""
    tool = await search_tool
    dense_client = await dense_vector_client
    sparse_client = await sparse_vector_client
    
    dense_client.search.return_value = [
        ArchiveDocument(
            id="1",
            text_excerpt="Test document 1",
            metadata=ArchiveMetadata(
                author="test@example.com",
                year=2023,
                month=1,
                day=1,
                keywords=["test"],
                title="Test Document 1"
            )
        )
    ]
    sparse_client.search.return_value = []

    query = SearchQuery(query="test测试")
    response = await tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1

@pytest.mark.asyncio
async def test_search_tool_with_very_long_query(search_tool):
    """Test handling of very long queries."""
    tool = await search_tool
    long_query = "test " * 1000
    with pytest.raises(ValueError):
        await tool.search(SearchQuery(query=long_query))

@pytest.mark.asyncio
async def test_search_tool_with_invalid_dates(search_tool):
    """Test handling of invalid date parameters."""
    tool = await search_tool
    with pytest.raises(ValueError):
        await tool.search(SearchQuery(
            query="test document",
            year=9999,
            month=13,
            day=32
        ))

@pytest.mark.asyncio
async def test_search_tool_with_no_filter(search_tool, dense_vector_client, sparse_vector_client):
    """Test search without any filters."""
    tool = await search_tool
    dense_client = await dense_vector_client
    sparse_client = await sparse_vector_client
    
    dense_client.search.return_value = [
        ArchiveDocument(
            id="1",
            text_excerpt="Test document 1",
            metadata=ArchiveMetadata(
                author="test@example.com",
                year=2023,
                month=1,
                day=1,
                keywords=["test"],
                title="Test Document 1"
            )
        )
    ]
    sparse_client.search.return_value = []

    query = SearchQuery(query="test document")
    response = await tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1 