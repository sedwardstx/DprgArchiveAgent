# Testing Guide

This guide covers how to run and write tests for the DprgArchiveAgent project.

## Test Environment Setup

Before running tests, ensure you have:

1. Installed all dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your `.env` file with test credentials:
```bash
cp .env.example .env
```

3. Configure the following environment variables in your `.env` file:
```
PINECONE_API_KEY=your_test_pinecone_api_key
PINECONE_ENVIRONMENT=your_test_environment
OPENAI_API_KEY=your_test_openai_api_key
```

## Running Tests

### Basic Test Commands

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_metadata_filters.py

# Run specific test function
pytest tests/test_metadata_filters.py::test_author_filter_dense

# Run tests with coverage report
pytest --cov=src
```

### Test Categories

1. **Metadata Filter Tests**
   - Tests for filtering by author
   - Tests for filtering by date (year, month, day)
   - Tests for filtering by keywords
   - Tests for filtering by title
   - Tests for combined filters
   - Tests for no filters

2. **Vector Store Tests**
   - Tests for dense vector search
   - Tests for sparse vector search
   - Tests for hybrid search
   - Tests for score thresholds
   - Tests for top-k results

## Test Fixtures

The project uses pytest fixtures to set up test data and clients:

### Vector Store Fixtures

```python
@pytest.fixture
def dense_client():
    """Initialize DenseVectorClient for testing."""
    return DenseVectorClient()

@pytest.fixture
def sparse_client():
    """Initialize SparseVectorClient for testing."""
    return SparseVectorClient()
```

### Test Data Fixture

```python
@pytest.fixture
def load_test_documents():
    """Load sample test documents into Pinecone indices."""
    # Sample test documents with metadata
    test_documents = [
        {
            "id": "doc1",
            "text": "Sample document 1",
            "metadata": {
                "author": "test@example.com",
                "year": 2007,
                "month": 2,
                "day": 15,
                "keywords": ["test", "document"],
                "title": "Test Document 1"
            }
        },
        # ... more test documents
    ]
    
    # Load documents into indices
    yield test_documents
    
    # Cleanup after tests
    # Delete test documents from indices
```

## Writing New Tests

### Test Structure

```python
@pytest.mark.asyncio
async def test_specific_feature():
    """Test description."""
    # Setup
    async for _ in load_test_documents:
        # Test code
        result = await client.search(query)
        
        # Assertions
        assert len(result) > 0
        assert result[0].metadata["author"] == "test@example.com"
```

### Best Practices

1. **Naming Conventions**
   - Test functions should be prefixed with `test_`
   - Use descriptive names that indicate what is being tested
   - Group related tests in the same file

2. **Test Data**
   - Use fixtures for common setup
   - Keep test data minimal but sufficient
   - Use realistic but test-safe values

3. **Assertions**
   - Test both positive and negative cases
   - Verify all relevant aspects of the response
   - Use specific assertions rather than broad ones

4. **Async Tests**
   - Use `@pytest.mark.asyncio` for async tests
   - Properly await async operations
   - Handle cleanup in fixtures

## Test Coverage

The project uses pytest-cov for coverage reporting:

```bash
# Generate coverage report
pytest --cov=src

# Generate HTML coverage report
pytest --cov=src --cov-report=html
```

Coverage reports show:
- Overall code coverage percentage
- Coverage by file
- Line-by-line coverage details
- Missing lines and branches

## Continuous Integration

Tests are automatically run in CI/CD pipelines:
- On every push to main
- On pull requests
- Before merging to main

## Troubleshooting Tests

### Common Issues

1. **Pinecone Connection Issues**
   - Verify API key and environment in `.env`
   - Check network connectivity
   - Ensure indices exist and are accessible

2. **Async Test Failures**
   - Ensure proper use of `@pytest.mark.asyncio`
   - Check for unhandled coroutines
   - Verify event loop configuration

3. **Test Data Issues**
   - Check fixture setup
   - Verify test data format
   - Ensure cleanup is working

4. **Coverage Issues**
   - Review missing lines
   - Add tests for uncovered code
   - Check for dead code

### Debugging Tips

1. **Verbose Output**
   ```bash
   pytest -v
   ```

2. **Print Debug Information**
   ```python
   print(f"Debug: {variable}")
   ```

3. **Use pytest -s**
   ```bash
   pytest -s
   ```

4. **Use pytest --pdb**
   ```bash
   pytest --pdb
   ``` 