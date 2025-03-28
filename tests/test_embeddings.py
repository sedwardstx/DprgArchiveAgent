"""
Tests for embeddings and sparse vector generation.
"""
import pytest
import numpy as np
from src.utils.embeddings import (
    tokenize_text,
    generate_sparse_vector,
    compute_idf
)

@pytest.mark.asyncio
async def test_tokenize_text():
    """Test tokenization preserves technical terms and case."""
    # Test case with technical terms
    text = "PDXbot PID controller implementation"
    tokens = tokenize_text(text)
    assert "PDXbot" in tokens
    assert "PID" in tokens
    assert "controller" in tokens
    assert "implementation" in tokens
    
    # Test case with mixed case
    text = "PDXbot pdxbot PDXBOT"
    tokens = tokenize_text(text)
    assert len(tokens) == 3  # All should be preserved as different tokens
    assert "PDXbot" in tokens
    assert "pdxbot" in tokens
    assert "PDXBOT" in tokens

@pytest.mark.asyncio
async def test_generate_sparse_vector():
    """Test sparse vector generation is consistent."""
    # Test with technical term
    text = "PDXbot"
    indices1, values1 = await generate_sparse_vector(text)
    indices2, values2 = await generate_sparse_vector(text)
    
    # Should generate same vectors for same input
    assert indices1 == indices2
    assert values1 == values2
    
    # Should have at least one non-zero value
    assert len(indices1) > 0
    assert len(values1) > 0
    
    # Test with multiple terms
    text = "PDXbot PID controller"
    indices, values = await generate_sparse_vector(text)
    assert len(indices) > 1  # Should have multiple non-zero values
    assert len(values) > 1

@pytest.mark.asyncio
async def test_sparse_vector_consistency():
    """Test that sparse vectors are consistent across different runs."""
    text = "PDXbot"
    vectors = []
    
    # Generate vectors multiple times
    for _ in range(5):
        indices, values = await generate_sparse_vector(text)
        vectors.append((indices, values))
    
    # All vectors should be identical
    for i in range(1, len(vectors)):
        assert vectors[0] == vectors[i]

@pytest.mark.asyncio
async def test_sparse_vector_similarity():
    """Test that similar terms generate similar sparse vectors."""
    # Test with similar technical terms
    text1 = "PDXbot"
    text2 = "PDXbot"
    text3 = "DifferentBot"
    
    vec1 = await generate_sparse_vector(text1)
    vec2 = await generate_sparse_vector(text2)
    vec3 = await generate_sparse_vector(text3)
    
    # Identical terms should have identical vectors
    assert vec1 == vec2
    
    # Different terms should have different vectors
    assert vec1 != vec3

def test_compute_idf():
    """Test IDF computation."""
    corpus = [
        ["PDXbot", "PID", "controller"],
        ["PDXbot", "implementation"],
        ["DifferentBot", "controller"]
    ]
    
    idf = compute_idf(corpus)
    
    # Check IDF values
    assert "PDXbot" in idf
    assert "PID" in idf
    assert "controller" in idf
    assert "DifferentBot" in idf
    
    # Terms appearing in more documents should have lower IDF
    assert idf["PDXbot"] < idf["PID"]  # PDXbot appears in 2 docs, PID in 1

@pytest.mark.asyncio
async def test_sparse_vector_dimensions():
    """Test that sparse vectors have correct dimensions."""
    text = "PDXbot"
    indices, values = await generate_sparse_vector(text)
    
    # Check that indices are within bounds (0-999)
    assert all(0 <= idx < 1000 for idx in indices)
    
    # Check that values are positive
    assert all(v > 0 for v in values)
    
    # Check that indices and values have same length
    assert len(indices) == len(values) 