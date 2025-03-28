"""
Tests for the chat tool.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.schema.models import Message, ChatRequest
from src.tools.chat_tool import ChatTool

@pytest.fixture
async def chat_tool():
    """Create a ChatTool instance for testing."""
    return ChatTool()

@pytest.mark.asyncio
async def test_chat_tool_basic(chat_tool):
    """Test basic chat functionality."""
    chat_tool = await chat_tool
    with patch('src.utils.openai_client.openai_client.chat.completions.create', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        )
        
        request = ChatRequest(
            messages=[Message(role="user", content="Hello")]
        )
        
        response = await chat_tool.process(request)
        assert response.message.content == "Test response"
        assert response.referenced_documents == []
        assert response.elapsed_time >= 0

@pytest.mark.asyncio
async def test_chat_tool_with_search_type(chat_tool):
    """Test chat with different search types."""
    chat_tool = await chat_tool
    with patch('src.utils.openai_client.openai_client.chat.completions.create', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        )
        
        request = ChatRequest(
            messages=[Message(role="user", content="Hello")]
        )
        
        response = await chat_tool.process(request, search_type="dense")
        assert response.message.content == "Test response"
        assert response.referenced_documents == []

@pytest.mark.asyncio
async def test_chat_tool_with_search_top_k(chat_tool):
    """Test chat with different top_k values."""
    chat_tool = await chat_tool
    with patch('src.utils.openai_client.openai_client.chat.completions.create', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        )
        
        request = ChatRequest(
            messages=[Message(role="user", content="Hello")]
        )
        
        response = await chat_tool.process(request, search_top_k=5)
        assert response.message.content == "Test response"
        assert response.referenced_documents == []

@pytest.mark.asyncio
async def test_chat_tool_with_temperature(chat_tool):
    """Test chat with different temperature values."""
    chat_tool = await chat_tool
    with patch('src.utils.openai_client.openai_client.chat.completions.create', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        )
        
        request = ChatRequest(
            messages=[Message(role="user", content="Hello")]
        )
        
        response = await chat_tool.process(request, temperature=0.8)
        assert response.message.content == "Test response"
        assert response.referenced_documents == []

@pytest.mark.asyncio
async def test_chat_tool_with_max_tokens(chat_tool):
    """Test chat with different max_tokens values."""
    chat_tool = await chat_tool
    with patch('src.utils.openai_client.openai_client.chat.completions.create', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        )
        
        request = ChatRequest(
            messages=[Message(role="user", content="Hello")]
        )
        
        response = await chat_tool.process(request, max_tokens=100)
        assert response.message.content == "Test response"
        assert response.referenced_documents == []

@pytest.mark.asyncio
async def test_chat_tool_error_handling(chat_tool):
    """Test error handling in chat tool."""
    chat_tool = await chat_tool
    with patch('src.utils.openai_client.openai_client.chat.completions.create', new_callable=AsyncMock) as mock_chat:
        mock_chat.side_effect = Exception("Test error")
        
        request = ChatRequest(
            messages=[Message(role="user", content="Hello")]
        )
        
        with pytest.raises(Exception) as exc_info:
            await chat_tool.process(request)
        assert str(exc_info.value) == "Error processing chat request: Test error"

@pytest.mark.asyncio
async def test_chat_tool_with_empty_context(chat_tool):
    """Test chat with no relevant context found."""
    chat_tool = await chat_tool
    with patch('src.utils.openai_client.openai_client.chat.completions.create', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        )
        
        request = ChatRequest(
            messages=[Message(role="user", content="")]
        )
        
        response = await chat_tool.process(request)
        assert response.message.content == "Test response"
        assert response.referenced_documents == []

@pytest.mark.asyncio
async def test_chat_tool_with_special_characters(chat_tool):
    """Test chat with special characters in query."""
    chat_tool = await chat_tool
    with patch('src.utils.openai_client.openai_client.chat.completions.create', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        )
        
        request = ChatRequest(
            messages=[Message(role="user", content="Hello! @#$%^&*()")]
        )
        
        response = await chat_tool.process(request)
        assert response.message.content == "Test response"
        assert response.referenced_documents == []

@pytest.mark.asyncio
async def test_chat_tool_with_unicode(chat_tool):
    """Test chat with Unicode characters in query."""
    chat_tool = await chat_tool
    with patch('src.utils.openai_client.openai_client.chat.completions.create', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        )
        
        request = ChatRequest(
            messages=[Message(role="user", content="Hello 你好")]
        )
        
        response = await chat_tool.process(request)
        assert response.message.content == "Test response"
        assert response.referenced_documents == []

@pytest.mark.asyncio
async def test_chat_tool_with_very_long_query(chat_tool):
    """Test chat with very long query."""
    chat_tool = await chat_tool
    with patch('src.utils.openai_client.openai_client.chat.completions.create', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        )
        
        request = ChatRequest(
            messages=[Message(role="user", content="Hello " * 1000)]
        )
        
        response = await chat_tool.process(request)
        assert response.message.content == "Test response"
        assert response.referenced_documents == []

@pytest.mark.asyncio
async def test_chat_tool_with_conversation_history(chat_tool):
    """Test chat with conversation history."""
    chat_tool = await chat_tool
    with patch('src.utils.openai_client.openai_client.chat.completions.create', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        )
        
        request = ChatRequest(
            messages=[
                Message(role="user", content="Hello"),
                Message(role="assistant", content="Hi there!"),
                Message(role="user", content="How are you?")
            ]
        )
        
        response = await chat_tool.process(request)
        assert response.message.content == "Test response"
        assert response.referenced_documents == [] 