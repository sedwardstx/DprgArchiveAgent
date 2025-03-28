"""
Tests for the FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.schema.models import SearchQuery, ChatRequest
from src.config import get_settings

client = TestClient(app)
settings = get_settings()

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_search_endpoint():
    """Test the search endpoint."""
    response = client.post("/search", json={
        "query": "test document"
    })
    assert response.status_code == 200
    assert "results" in response.json()
    assert "total" in response.json()

def test_search_endpoint_with_filters():
    """Test search endpoint with metadata filters."""
    response = client.post("/search", json={
        "query": "test query",
        "filters": {
            "author": "test author",
            "year": 2024
        }
    })
    assert response.status_code == 200
    assert "results" in response.json()

def test_metadata_endpoint():
    """Test the metadata endpoint."""
    response = client.post("/metadata", json={
        "query": "test document"
    })
    assert response.status_code == 200
    assert "metadata" in response.json()

def test_chat_endpoint():
    """Test the chat completion endpoint."""
    response = client.post("/chat", json={
        "messages": [{"role": "user", "content": "Hello"}]
    })
    assert response.status_code == 200
    assert "message" in response.json()
    assert "referenced_documents" in response.json()

def test_chat_endpoint_error_handling():
    """Test error handling in chat endpoint."""
    response = client.post("/chat", json={
        "invalid": "data"
    })
    assert response.status_code == 422
    assert "detail" in response.json()

def test_search_endpoint_error_handling():
    """Test error handling in search endpoint."""
    response = client.post("/search", json={
        "invalid": "data"
    })
    assert response.status_code == 422
    assert "detail" in response.json()

def test_metadata_endpoint_error_handling():
    """Test error handling in metadata endpoint."""
    response = client.post("/metadata", json={
        "invalid": "data"
    })
    assert response.status_code == 422
    assert "detail" in response.json()

def test_invalid_date_handling():
    """Test handling of invalid dates in search."""
    response = client.post("/search", json={
        "query": "test document",
        "year": "invalid",
        "month": "invalid",
        "day": "invalid"
    })
    assert response.status_code == 422
    assert "detail" in response.json()

def test_rate_limiting():
    """Test rate limiting."""
    # Clear any existing rate limit state
    client.get("/health")
    
    # Make multiple requests in quick succession
    responses = [
        client.post("/search", json={"query": "test"})
        for _ in range(10)  # Increased number of requests
    ]
    
    # At least one should be rate limited
    assert any(r.status_code == 429 for r in responses)
    if any(r.status_code == 429 for r in responses):
        rate_limited = next(r for r in responses if r.status_code == 429)
        assert "Retry-After" in rate_limited.headers 