# DprgArchiveAgent

An AI agent for searching and querying the DPRG archive data stored in Pinecone vector indexes.

## Overview

DprgArchiveAgent provides a seamless interface to search through DPRG archives using both dense and sparse vector indexes. The system intelligently routes queries to the appropriate index based on the query type and content, providing optimal search results.

## Features

- Search DPRG archives with natural language queries
- Access both dense and sparse vector indexes
- Filter results by metadata (author, date, keywords, etc.)
- CLI interface for quick searches
- REST API for integration with other applications

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

# Vector index URLs
DENSE_INDEX_URL=https://dprg-list-archive-dense-4p4f7lg.svc.aped-4627-b74a.pinecone.io
SPARSE_INDEX_URL=https://dprg-list-archive-sparse-4p4f7lg.svc.aped-4627-b74a.pinecone.io

# Namespace
PINECONE_NAMESPACE=dprg-archive
```

## Usage

### CLI Interface

```bash
# Basic search
python -m src.cli search "DPRG robotics competition"

# Search with metadata filters
python -m src.cli search "progress video" --author "eric@sssi.com" --year 2007

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
GET /search?query=robotics+competition&limit=10
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
  ]
}
```

## Development

```bash
# Run tests
pytest

# Format code
black src tests

# Run linter
ruff check src tests
```

## License

MIT

## Acknowledgements

This project utilizes the DPRG archive data stored in Pinecone vector indexes.
