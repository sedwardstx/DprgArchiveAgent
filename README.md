# DPRG Archive Agent

A command-line tool to search and interact with the Dallas Personal Robotics Group (DPRG) archive.

## Features

- **Semantic Search**: Search the archive using dense vector, sparse vector, or hybrid search methods
- **Metadata Search**: Find documents by author, date, title, and keywords
- **Chat Interface**: Interact with the archive using natural language

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd DprgArchiveAgent

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Search Commands

#### Semantic Search

Search the archive using semantic meaning:

```bash
# Basic search
python -m src.cli search "robotics competition"

# Specify search type (dense, sparse, or hybrid)
python -m src.cli search "UMBMark calibration" --type hybrid

# Adjust result count
python -m src.cli search "line following robot" --top-k 20

# Filter by metadata
python -m src.cli search "outdoor navigation" --author "dpa@io.isem.smu.edu" --year 2008
```

#### Metadata Search

Search by metadata fields only (uses min_score=0.0 by default):

```bash
# Search by author
python -m src.cli metadata --author "dpa@io.isem.smu.edu"

# Search by year 
python -m src.cli metadata --year 2008

# Combined metadata filters
python -m src.cli metadata --author "dpa@io.isem.smu.edu" --year 2008 --top-k 15

# Search by title (partial match)
python -m src.cli metadata --title "Outdoor Contest" --top-k 10
```

### Chat Interface

Chat with the archive to get information based on document content:

```bash
# Interactive chat mode
python -m src.cli chat

# One-shot query
python -m src.cli chat --query "Tell me about the UMBMark calibration technique"

# Adjust search parameters for more results
python -m src.cli chat --query "What were the Outdoor Contest Final Rules?" --min-score 0.4 --top-k 10
```

## Search Parameters

- `--type, -t`: Search type (dense, sparse, hybrid)
- `--top-k, -k`: Number of results to return
- `--min-score, -s`: Minimum relevance score threshold
  - For semantic searches: 0.3 by default (higher means more relevant results)
  - For metadata searches: 0.0 by default (to return all matching documents)
- `--author, -a`: Filter by author
- `--year, -y`: Filter by year
- `--month, -m`: Filter by month
- `--day, -d`: Filter by day
- `--title`: Filter by title
- `--keywords, -kw`: Filter by keywords (comma-separated)
- `--no-filter`: Disable minimum score filtering

## Chat Parameters

- `--query, -q`: One-shot query (non-interactive mode)
- `--type, -t`: Search type for retrieving context
- `--top-k, -k`: Number of documents to retrieve for context
- `--min-score, -s`: Minimum relevance score threshold (0.5 by default)
- `--temperature`: Temperature for response generation (0.7 by default)
- `--max-tokens, -m`: Maximum tokens to generate in response (500 by default)

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
