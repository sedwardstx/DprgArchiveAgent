"""
Tests for archive agent.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.agent.archive_agent import ArchiveAgent
from src.tools.search_tool import SearchTool
from src.tools.chat_tool import ChatTool
from src.schema.models import (
    SearchResponse,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionError,
    ArchiveDocument,
    ArchiveMetadata,
    ChatMessage
)

@pytest.fixture
def mock_search_tool():
    """Mock search tool."""
    with patch('src.agent.archive_agent.SearchTool') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_chat_tool():
    """Mock chat tool."""
    with patch('src.agent.archive_agent.ChatTool') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.mark.asyncio
async def test_archive_agent_search(mock_search_tool):
    """Test archive agent search functionality."""
    # Setup mock search results
    mock_results = SearchResponse(
        results=[
            ArchiveDocument(
                id='doc1',
                text_excerpt='PDXbot implementation',
                metadata=ArchiveMetadata(title='PDXbot Documentation'),
                score=0.95
            )
        ],
        total=1,
        query="PDXbot",
        search_type="dense",
        elapsed_time=0.1
    )
    mock_search_tool.search.return_value = mock_results
    
    # Initialize agent
    agent = ArchiveAgent()
    
    # Test search
    results = await agent.search("PDXbot")
    
    # Verify results
    assert len(results.results) == 1
    assert results.results[0].id == 'doc1'
    assert results.results[0].score == 0.95
    assert results.results[0].text_excerpt == 'PDXbot implementation'

@pytest.mark.asyncio
async def test_archive_agent_chat(mock_search_tool, mock_chat_tool):
    """Test archive agent chat functionality."""
    # Setup mock search results
    mock_search_results = SearchResponse(
        results=[
            ArchiveDocument(
                id='doc1',
                text_excerpt='PDXbot implementation details',
                metadata=ArchiveMetadata(title='PDXbot Documentation'),
                score=0.95
            )
        ],
        total=1,
        query="PDXbot",
        search_type="dense",
        elapsed_time=0.1
    )
    mock_search_tool.search.return_value = mock_search_results
    
    # Setup mock chat response
    mock_chat_response = ChatCompletionResponse(
        message=ChatMessage(
            role="assistant",
            content="Here's information about PDXbot..."
        ),
        referenced_documents=[mock_search_results.results[0]],
        elapsed_time=0.2
    )
    mock_chat_tool.chat.return_value = mock_chat_response
    
    # Initialize agent
    agent = ArchiveAgent()
    
    # Test chat
    response = await agent.chat("Tell me about PDXbot")
    
    # Verify response
    assert isinstance(response, ChatCompletionResponse)
    assert response.message.content == "Here's information about PDXbot..."
    assert len(response.referenced_documents) == 1
    
    # Verify tools were called correctly
    mock_search_tool.search.assert_called_once()
    mock_chat_tool.chat.assert_called_once()

@pytest.mark.asyncio
async def test_archive_agent_chat_no_results(mock_search_tool, mock_chat_tool):
    """Test archive agent chat with no search results."""
    # Setup empty search results
    mock_search_results = SearchResponse(
        results=[],
        total=0,
        query="unknown",
        search_type="dense",
        elapsed_time=0.1
    )
    mock_search_tool.search.return_value = mock_search_results
    
    # Setup mock chat response
    mock_chat_response = ChatCompletionResponse(
        message=ChatMessage(
            role="assistant",
            content="I couldn't find any information about that."
        ),
        referenced_documents=[],
        elapsed_time=0.2
    )
    mock_chat_tool.chat.return_value = mock_chat_response
    
    # Initialize agent
    agent = ArchiveAgent()
    
    # Test chat
    response = await agent.chat("Tell me about something not in the archive")
    
    # Verify response
    assert isinstance(response, ChatCompletionResponse)
    assert response.message.content == "I couldn't find any information about that."
    assert len(response.referenced_documents) == 0

@pytest.mark.asyncio
async def test_archive_agent_chat_error_handling(mock_search_tool, mock_chat_tool):
    """Test archive agent chat error handling."""
    # Setup search tool to raise exception
    mock_search_tool.search.side_effect = Exception("Search error")
    
    # Initialize agent
    agent = ArchiveAgent()
    
    # Test chat
    response = await agent.chat("Tell me about PDXbot")
    
    # Verify error handling
    assert isinstance(response, ChatCompletionError)
    assert "Chat failed" in response.error

@pytest.mark.asyncio
async def test_archive_agent_chat_with_context(mock_search_tool, mock_chat_tool):
    """Test archive agent chat with context from search results."""
    # Setup mock search results with detailed context
    mock_search_results = SearchResponse(
        results=[
            ArchiveDocument(
                id='doc1',
                text_excerpt='PDXbot is a robot built by DPRG members.',
                metadata=ArchiveMetadata(title='PDXbot Overview'),
                score=0.95
            ),
            ArchiveDocument(
                id='doc2',
                text_excerpt='PDXbot uses a PID controller for movement.',
                metadata=ArchiveMetadata(title='PDXbot Technical Details'),
                score=0.85
            )
        ],
        total=2,
        query="PDXbot",
        search_type="dense",
        elapsed_time=0.1
    )
    mock_search_tool.search.return_value = mock_search_results
    
    # Setup mock chat response
    mock_chat_response = ChatCompletionResponse(
        message=ChatMessage(
            role="assistant",
            content="Based on the search results, PDXbot is a robot built by DPRG members that uses a PID controller for movement."
        ),
        referenced_documents=mock_search_results.results,
        elapsed_time=0.2
    )
    mock_chat_tool.chat.return_value = mock_chat_response
    
    # Initialize agent
    agent = ArchiveAgent()
    
    # Test chat
    response = await agent.chat("Tell me about PDXbot")
    
    # Verify response includes context from both results
    assert isinstance(response, ChatCompletionResponse)
    assert "robot built by DPRG members" in response.message.content
    assert "PID controller" in response.message.content
    assert len(response.referenced_documents) == 2 