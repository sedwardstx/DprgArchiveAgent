"""
Test configuration and shared fixtures.
"""
import pytest
import os
from typing import Generator

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    # Set test environment variables
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["PINECONE_API_KEY"] = "test-key"
    os.environ["PINECONE_ENVIRONMENT"] = "test-env"
    os.environ["PINECONE_INDEX_NAME"] = "test-index"
    
    yield
    
    # Cleanup environment variables
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("PINECONE_API_KEY", None)
    os.environ.pop("PINECONE_ENVIRONMENT", None)
    os.environ.pop("PINECONE_INDEX_NAME", None)

@pytest.fixture
def mock_openai():
    """Mock OpenAI client."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("OPENAI_API_KEY", "test-key")
        yield

@pytest.fixture
def mock_pinecone():
    """Mock Pinecone client."""
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("PINECONE_API_KEY", "test-key")
        mp.setenv("PINECONE_ENVIRONMENT", "test-env")
        mp.setenv("PINECONE_INDEX_NAME", "test-index")
        yield 