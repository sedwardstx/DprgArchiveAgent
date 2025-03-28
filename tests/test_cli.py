"""
Tests for the command-line interface.
"""
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, AsyncMock, MagicMock
from src.cli import app, run_async_safely
from src.schema.models import SearchResponse, ArchiveDocument, ArchiveMetadata
import asyncio

runner = CliRunner()

@pytest.fixture
def mock_search_response():
    """Create a mock search response."""
    return SearchResponse(
        results=[
            ArchiveDocument(
                id="doc1",
                text_excerpt="Test document 1",
                metadata=ArchiveMetadata(
                    author="test@example.com",
                    year=2023,
                    month=1,
                    day=15,
                    keywords=["test", "document"],
                    title="Test Document 1"
                ),
                score=0.9
            )
        ],
        total=1,
        query="test document",
        search_type="dense",
        elapsed_time=0.1
    )

@pytest.fixture
def mock_archive_agent(mock_search_response):
    """Create a mock archive agent."""
    mock = MagicMock()
    async def mock_search(*args, **kwargs):
        return mock_search_response
    mock.search = mock_search
    return mock

def test_search_command(mock_search_response, mock_archive_agent):
    """Test the search command."""
    with patch("src.cli.archive_agent", mock_archive_agent):
        result = runner.invoke(app, ["search", "test document"])
        assert result.exit_code == 0
        assert "results" in result.stdout
        assert "Total" in result.stdout
        assert "elapsed_time" in result.stdout

def test_search_command_with_filters(mock_search_response, mock_archive_agent):
    """Test the search command with metadata filters."""
    with patch("src.cli.archive_agent", mock_archive_agent):
        result = runner.invoke(app, [
            "search",
            "test document",
            "--author", "test@example.com",
            "--year", "2023",
            "--month", "1",
            "--day", "15",
            "--keywords", "test,document",
            "--title", "Test Document 1"
        ])
        assert result.exit_code == 0
        assert "results" in result.stdout
        assert len(result.stdout.split("\n")) > 10  # Should have multiple results

def test_search_command_with_search_type(mock_search_response, mock_archive_agent):
    """Test the search command with different search types."""
    with patch("src.cli.archive_agent", mock_archive_agent):
        for search_type in ["dense", "sparse", "hybrid"]:
            result = runner.invoke(app, [
                "search",
                "test document",
                "--type", search_type
            ])
            assert result.exit_code == 0
            assert f"Search type: {search_type}" in result.stdout

def test_search_command_with_min_score(mock_search_response, mock_archive_agent):
    """Test the search command with minimum score threshold."""
    with patch("src.cli.archive_agent", mock_archive_agent):
        result = runner.invoke(app, [
            "search",
            "test document",
            "--min-score", "0.8"
        ])
        assert result.exit_code == 0
        assert "results" in result.stdout
        assert "min_score: 0.8" in result.stdout

def test_search_command_with_top_k(mock_search_response, mock_archive_agent):
    """Test the search command with top_k parameter."""
    with patch("src.cli.archive_agent", mock_archive_agent):
        result = runner.invoke(app, [
            "search",
            "test document",
            "--top-k", "5"
        ])
        assert result.exit_code == 0
        assert "results" in result.stdout
        assert "top_k: 5" in result.stdout

def test_search_command_with_no_filter(mock_search_response, mock_archive_agent):
    """Test the search command with no-filter option."""
    with patch("src.cli.archive_agent", mock_archive_agent):
        result = runner.invoke(app, [
            "search",
            "test document",
            "--no-filter"
        ])
        assert result.exit_code == 0
        assert "results" in result.stdout
        assert "No filters applied" in result.stdout

def test_search_command_error_handling():
    """Test error handling in the search command."""
    # Test with invalid search type
    result = runner.invoke(app, [
        "search",
        "test document",
        "--type", "invalid"
    ])
    assert result.exit_code != 0
    assert "error" in result.stdout.lower()

    # Test with invalid min_score
    result = runner.invoke(app, [
        "search",
        "test document",
        "--min-score", "invalid"
    ])
    assert result.exit_code != 0
    assert "error" in result.stdout.lower()

    # Test with invalid top_k
    result = runner.invoke(app, [
        "search",
        "test document",
        "--top-k", "invalid"
    ])
    assert result.exit_code != 0
    assert "error" in result.stdout.lower()

def test_search_command_with_invalid_dates():
    """Test the search command with invalid date parameters."""
    result = runner.invoke(app, [
        "search",
        "test document",
        "--year", "invalid",
        "--month", "invalid",
        "--day", "invalid"
    ])
    assert result.exit_code != 0
    assert "error" in result.stdout.lower()

def test_search_command_with_empty_query():
    """Test the search command with an empty query."""
    result = runner.invoke(app, ["search", ""])
    assert result.exit_code != 0
    assert "error" in result.stdout.lower()

def test_search_command_with_very_long_query():
    """Test the search command with a very long query."""
    long_query = "test " * 1000
    result = runner.invoke(app, ["search", long_query])
    assert result.exit_code != 0
    assert "error" in result.stdout.lower()

def test_search_command_with_special_characters(mock_search_response, mock_archive_agent):
    """Test the search command with special characters in the query."""
    with patch("src.cli.archive_agent", mock_archive_agent):
        result = runner.invoke(app, ["search", "test!@#$%^&*()"])
        assert result.exit_code == 0
        assert "results" in result.stdout

def test_search_command_with_unicode(mock_search_response, mock_archive_agent):
    """Test the search command with Unicode characters in the query."""
    with patch("src.cli.archive_agent", mock_archive_agent):
        result = runner.invoke(app, ["search", "test 测试"])
        assert result.exit_code == 0
        assert "results" in result.stdout 