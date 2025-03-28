"""
Tests for the search tool functionality.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.tools.search_tool import SearchTool
from src.schema.models import SearchQuery, SearchResponse, SearchError, ArchiveDocument, ArchiveMetadata

@pytest.fixture
def mock_dense_client():
    """Create a mock dense vector client."""
    client = AsyncMock()
    client.search = AsyncMock()
    return client

@pytest.fixture
def mock_sparse_client():
    """Create a mock sparse vector client."""
    client = AsyncMock()
    client.search = AsyncMock()
    return client

@pytest.fixture
def search_tool(mock_dense_client, mock_sparse_client):
    """Create a SearchTool instance for testing."""
    return SearchTool(mock_dense_client, mock_sparse_client)

@pytest.fixture
def test_documents():
    """Create test documents for search."""
    return [
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

@pytest.mark.asyncio
async def test_search_tool_basic(search_tool, mock_dense_client, mock_sparse_client, test_documents):
    """Test basic search functionality."""
    mock_dense_client.search.return_value = test_documents[:1]
    mock_sparse_client.search.return_value = []

    query = SearchQuery(query="test document")
    response = await search_tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1
    assert response.results[0].text_excerpt == "Test document 0 about robotics"

@pytest.mark.asyncio
async def test_search_tool_with_filters(search_tool, mock_dense_client, mock_sparse_client, test_documents):
    """Test search with metadata filters."""
    mock_dense_client.search.return_value = test_documents[:1]
    mock_sparse_client.search.return_value = []

    query = SearchQuery(
        query="test document",
        author="test_author",
        year=2023,
        month=1,
        day=1,
        keywords=["test"],
        title="Test Document 0"
    )
    response = await search_tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1
    assert response.results[0].metadata.author == "test_author"

@pytest.mark.asyncio
async def test_search_tool_with_search_types(search_tool, mock_dense_client, mock_sparse_client, test_documents):
    """Test search with different search types."""
    mock_dense_client.search.return_value = test_documents[:1]
    mock_sparse_client.search.return_value = []

    # Test dense search
    query = SearchQuery(query="test document", search_type="dense")
    response = await search_tool.search(query)
    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1

    # Test sparse search
    query = SearchQuery(query="test document", search_type="sparse")
    response = await search_tool.search(query)
    assert isinstance(response, SearchResponse)

    # Test hybrid search
    query = SearchQuery(query="test document", search_type="hybrid")
    response = await search_tool.search(query)
    assert isinstance(response, SearchResponse)

@pytest.mark.asyncio
async def test_search_tool_with_min_score(search_tool, mock_dense_client, mock_sparse_client, test_documents):
    """Test search with minimum score threshold."""
    mock_dense_client.search.return_value = [doc for doc in test_documents if doc.score >= 0.8]
    mock_sparse_client.search.return_value = []

    query = SearchQuery(query="test document", min_score=0.8)
    response = await search_tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) > 0
    for result in response.results:
        assert result.score >= 0.8

@pytest.mark.asyncio
async def test_search_tool_with_top_k(search_tool, mock_dense_client, mock_sparse_client, test_documents):
    """Test search with top_k parameter."""
    mock_dense_client.search.return_value = test_documents[:5]
    mock_sparse_client.search.return_value = []

    query = SearchQuery(query="test document", top_k=5)
    response = await search_tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 5

@pytest.mark.asyncio
async def test_search_tool_error_handling(search_tool):
    """Test error handling for invalid inputs."""
    query = SearchQuery(query="", search_type="invalid")
    response = await search_tool.search(query)
    assert isinstance(response, SearchError)

@pytest.mark.asyncio
async def test_search_tool_with_empty_results(search_tool, mock_dense_client, mock_sparse_client):
    """Test handling of queries that return no results."""
    mock_dense_client.search.return_value = []
    mock_sparse_client.search.return_value = []

    query = SearchQuery(query="xyzabc123nonexistent")
    response = await search_tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 0

@pytest.mark.asyncio
async def test_search_tool_with_special_characters(search_tool, mock_dense_client, mock_sparse_client, test_documents):
    """Test handling of special characters in query."""
    mock_dense_client.search.return_value = test_documents[:1]
    mock_sparse_client.search.return_value = []

    query = SearchQuery(query="test!@#$%^&*()")
    response = await search_tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1

@pytest.mark.asyncio
async def test_search_tool_with_unicode(search_tool, mock_dense_client, mock_sparse_client, test_documents):
    """Test handling of Unicode characters in query."""
    mock_dense_client.search.return_value = test_documents[:1]
    mock_sparse_client.search.return_value = []

    query = SearchQuery(query="test测试")
    response = await search_tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1

@pytest.mark.asyncio
async def test_search_tool_with_very_long_query(search_tool):
    """Test handling of very long queries."""
    long_query = "test " * 1000
    query = SearchQuery(query=long_query)
    response = await search_tool.search(query)
    assert isinstance(response, SearchError)

@pytest.mark.asyncio
async def test_search_tool_with_invalid_dates(search_tool):
    """Test handling of invalid date parameters."""
    query = SearchQuery(query="test", year=9999, month=13, day=32)
    response = await search_tool.search(query)
    assert isinstance(response, SearchError)

@pytest.mark.asyncio
async def test_search_tool_with_no_filter(search_tool, mock_dense_client, mock_sparse_client, test_documents):
    """Test search without any filters."""
    mock_dense_client.search.return_value = test_documents[:1]
    mock_sparse_client.search.return_value = []

    query = SearchQuery(query="test document")
    response = await search_tool.search(query)

    assert isinstance(response, SearchResponse)
    assert len(response.results) == 1 