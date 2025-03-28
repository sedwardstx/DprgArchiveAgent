"""
Test cases for verifying search results with known queries.
"""
import pytest
from src.agent.archive_agent import archive_agent
from src.schema.models import SearchError

@pytest.mark.asyncio
async def test_pdxbot_search():
    """Test search for 'PDXbot' which should return approximately 49 results."""
    result = await archive_agent.search_dense(
        query="PDXbot",
        top_k=100,  # Increased to ensure we get all results
        min_score=0.0  # No minimum score to see all results
    )
    
    # Verify we got results
    assert not isinstance(result, SearchError), f"Search failed with error: {result.error if isinstance(result, SearchError) else 'Unknown error'}"
    assert len(result.results) > 0, "No results found for 'PDXbot'"
    
    # Log the number of results for verification
    print(f"\nFound {len(result.results)} results for 'PDXbot'")
    
    # Verify some key aspects of the results
    for doc in result.results[:5]:  # Check first 5 results
        assert doc.metadata is not None, "Result missing metadata"
        assert doc.text_excerpt is not None, "Result missing text excerpt"
        assert doc.score is not None, "Result missing score"
        
        # Log details of first few results
        print(f"\nResult: {doc.metadata.title}")
        print(f"Score: {doc.score}")
        print(f"Excerpt: {doc.text_excerpt[:100]}...")

@pytest.mark.asyncio
async def test_bornstein_square_search():
    """Test search for 'Bornstein square' which should return over 200 results."""
    result = await archive_agent.search_dense(
        query="Bornstein square",
        top_k=250,  # Increased to ensure we get all results
        min_score=0.0  # No minimum score to see all results
    )
    
    # Verify we got results
    assert not isinstance(result, SearchError), f"Search failed with error: {result.error if isinstance(result, SearchError) else 'Unknown error'}"
    assert len(result.results) > 0, "No results found for 'Bornstein square'"
    
    # Log the number of results for verification
    print(f"\nFound {len(result.results)} results for 'Bornstein square'")
    
    # Verify some key aspects of the results
    for doc in result.results[:5]:  # Check first 5 results
        assert doc.metadata is not None, "Result missing metadata"
        assert doc.text_excerpt is not None, "Result missing text excerpt"
        assert doc.score is not None, "Result missing score"
        
        # Log details of first few results
        print(f"\nResult: {doc.metadata.title}")
        print(f"Score: {doc.score}")
        print(f"Excerpt: {doc.text_excerpt[:100]}...")

@pytest.mark.asyncio
async def test_hybrid_search_pdxbot():
    """Test hybrid search for 'PDXbot' to verify both dense and sparse components work."""
    result = await archive_agent.search_hybrid(
        query="PDXbot",
        top_k=100,
        min_score=0.0
    )
    
    # Verify we got results
    assert not isinstance(result, SearchError), f"Search failed with error: {result.error if isinstance(result, SearchError) else 'Unknown error'}"
    assert len(result.results) > 0, "No results found for hybrid search of 'PDXbot'"
    
    # Log the number of results for verification
    print(f"\nFound {len(result.results)} results for hybrid search of 'PDXbot'")

@pytest.mark.asyncio
async def test_sparse_search_pdxbot(load_test_documents):
    """Test sparse search with test data."""
    async for _ in load_test_documents:
        result = await archive_agent.search_sparse(
            query="test document",  # Using a query that matches our test data
            top_k=10,
            min_score=0.0
        )
        
        # Verify we got results
        assert not isinstance(result, SearchError), f"Search failed with error: {result.error if isinstance(result, SearchError) else 'Unknown error'}"
        assert len(result.results) > 0, "No results found for sparse search"
        
        # Log the number of results for verification
        print(f"\nFound {len(result.results)} results for sparse search")
        
        # Verify some key aspects of the results
        for doc in result.results[:5]:  # Check first 5 results
            assert doc.metadata is not None, "Result missing metadata"
            assert doc.text_excerpt is not None, "Result missing text excerpt"
            assert doc.score is not None, "Result missing score"
            
            # Log details of first few results
            print(f"\nResult: {doc.metadata.title}")
            print(f"Score: {doc.score}")
            print(f"Excerpt: {doc.text_excerpt[:100]}...") 