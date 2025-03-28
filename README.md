# DprgArchiveAgent

An AI agent for searching and querying the DPRG archive data stored in Pinecone vector indexes.

## Overview

DprgArchiveAgent provides a seamless interface to search through DPRG archives using both dense and sparse vector indexes. The system intelligently routes queries to the appropriate index based on the query type and content, providing optimal search results.

## Features

- Search DPRG archives with natural language queries
- Multiple search types:
  - Dense vector search (semantic similarity)
  - Sparse vector search (keyword matching)
  - Hybrid search (combines both approaches)
- Rich metadata filtering:
  - Author
  - Date (year, month, day)
  - Keywords
  - Title
- CLI interface for quick searches
- REST API for integration with other applications
- Comprehensive test suite

## Installation

```bash
# Clone the repository
git clone https://github.com/sedwardstx/DprgArchiveAgent.git
cd DprgArchiveAgent

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with the following variables:

```
# Pinecone API key and environment
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment

# OpenAI API key (for embeddings)
OPENAI_API_KEY=your_openai_api_key

# Vector index configuration
DENSE_INDEX_NAME=your_dense_index_name
SPARSE_INDEX_NAME=your_sparse_index_name
DENSE_INDEX_URL=your_dense_index_url
SPARSE_INDEX_URL=your_sparse_index_url

# Namespace
PINECONE_NAMESPACE=your_namespace

# Optional settings
MIN_SCORE_THRESHOLD=0.7  # Minimum score for search results
DENSE_WEIGHT=0.5        # Weight for dense results in hybrid search
SPARSE_WEIGHT=0.5       # Weight for sparse results in hybrid search
```

## Usage

### CLI Interface

```bash
# Basic search
python -m src.cli search "DPRG robotics competition"

# Search with metadata filters
python -m src.cli search "progress video" --author "eric@sssi.com" --year 2007

# Specify search type
python -m src.cli search "robotics" --type dense    # Semantic search
python -m src.cli search "robotics" --type sparse   # Keyword search
python -m src.cli search "robotics" --type hybrid   # Combined search

# Get help
python -m src.cli --help
```

### API Server

```bash
# Start the API server
python -m src.api

# The server will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

## API Examples

### Search Endpoint

```
GET /search?query=robotics+competition&type=hybrid&limit=10
```

Response:
```json
{
  "results": [
    {
      "author": "eric@sssi.com",
      "date": "2007-02-15T16:51:29.000Z",
      "title": "DPRG: YaTu4b Progress Video",
      "text_excerpt": "at cadence.com Thu Mar 4 18:28:11 1999 From: ctimmons at cadence.com (Clay Timmons) Date: Thu Feb 15 16:51:30 2007 Subject: DPRG: Contestants please read this Message-ID: <mailman.8215.1171579890.5280.dprglist@dprg.org> Contestants, A few before, dur",
      "keywords": ["dprg", "yatu4b", "progress", "video", "cadence", "com"],
      "score": 0.89
    }
  ],
  "total": 1,
  "query": "robotics competition",
  "search_type": "hybrid",
  "elapsed_time": 0.543
}
```

## Development

### Code Quality

```bash
# Format code
black src tests

# Run linter
ruff check src tests
```

### Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src

# Run specific test file
pytest tests/test_metadata_filters.py
```

For detailed testing documentation, see [docs/testing.md](docs/testing.md).

## License

MIT

## Acknowledgements

This project utilizes the DPRG archive data stored in Pinecone vector indexes.
