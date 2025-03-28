"""
Test fixtures for the DPRG Archive Agent.
"""
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

from src.agent.archive_agent import ArchiveAgent
from src.tools.search_tool import SearchTool
from src.tools.chat_tool import ChatTool
from src.utils.vector_store import DenseVectorClient, SparseVectorClient, HybridSearchClient

@pytest.fixture(scope="session")
def event_loop_policy():
    """Create an event loop policy for the test session."""
    return asyncio.WindowsProactorEventLoopPolicy()

@pytest.fixture(scope="function")
def event_loop(event_loop_policy):
    """Create an event loop for each test function."""
    asyncio.set_event_loop_policy(event_loop_policy)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture
async def chat_tool():
    """Create a ChatTool instance for testing."""
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock()
    return ChatTool(mock_client)

@pytest.fixture
async def dense_vector_client():
    """Create a mock dense vector client."""
    mock_client = AsyncMock()
    mock_client.search = AsyncMock()
    return mock_client

@pytest.fixture
async def sparse_vector_client():
    """Create a mock sparse vector client."""
    mock_client = AsyncMock()
    mock_client.search = AsyncMock()
    return mock_client

@pytest.fixture
async def hybrid_search_client():
    """Create a mock HybridSearchClient for testing."""
    mock_client = AsyncMock()
    mock_client.search = AsyncMock()
    return mock_client

@pytest.fixture
async def search_tool(dense_vector_client, sparse_vector_client):
    """Create a SearchTool instance for testing."""
    return SearchTool(dense_vector_client, sparse_vector_client)

@pytest.fixture
async def archive_agent(search_tool, chat_tool):
    """Create an ArchiveAgent instance for testing."""
    tool = await search_tool
    chat = await chat_tool
    return ArchiveAgent(search_tool=tool, chat_tool=chat)

@pytest.fixture
def load_test_documents():
    """Load test documents for search."""
    from src.schema.models import ArchiveDocument, ArchiveMetadata
    
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
    
    return test_docs
