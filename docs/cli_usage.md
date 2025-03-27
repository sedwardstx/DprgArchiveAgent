# CLI Usage Guide

The DprgArchiveAgent provides a powerful command-line interface (CLI) for searching the DPRG archive. This guide covers how to use the CLI tool effectively.

## Getting Started

The CLI uses the [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/) libraries to provide a user-friendly interface with colorful output.

### Basic Commands

To get help on available commands:

```bash
python -m src.cli --help
```

The CLI provides two main commands:
- `search`: Search the archive using a text query
- `metadata`: Search the archive using only metadata filters

## Search Command

The `search` command allows you to search the archive using a text query, with optional filters.

### Basic Search

```bash
python -m src.cli search "robotics competition"
```

This performs a basic search using the default dense vector index.

### Command Parameters

```
Arguments:
  QUERY  Search query text  [required]

Options:
  -k, --top-k INTEGER         Number of results to return  [default: 10]
  -a, --author TEXT           Filter by author
  -y, --year INTEGER          Filter by year
  -m, --month INTEGER         Filter by month
  -d, --day INTEGER           Filter by day
  -kw, --keyword TEXT         Filter by keyword (can be used multiple times)
  -s, --min-score FLOAT       Minimum score threshold
  -t, --type TEXT             Search type: dense, sparse, or hybrid  [default: dense]
  --help                      Show this message and exit.
```

### Search Types

The CLI supports three search types:

1. **Dense Search** (default): Semantic search using embeddings
   ```bash
   python -m src.cli search "robotics competition" --type dense
   ```

2. **Sparse Search**: Keyword-based search
   ```bash
   python -m src.cli search "robotics competition" --type sparse
   ```

3. **Hybrid Search**: Combines both dense and sparse search results
   ```bash
   python -m src.cli search "robotics competition" --type hybrid
   ```

### Filtering Results

You can filter search results using metadata:

```bash
# Filter by author
python -m src.cli search "progress video" --author "eric@sssi.com"

# Filter by year
python -m src.cli search "robot contest" --year 2007

# Filter by multiple criteria
python -m src.cli search "DPRG" --year 2007 --month 2 --day 15

# Filter by keywords (can be used multiple times for AND filtering)
python -m src.cli search "competition" --keyword "dprg" --keyword "video"
```

### Controlling Result Count

Control the number of results returned:

```bash
# Return top 5 results
python -m src.cli search "robotics" --top-k 5

# Return top 20 results
python -m src.cli search "robotics" --top-k 20
```

### Setting Score Threshold

Set a minimum similarity score threshold (0-1):

```bash
# Only return results with a score of 0.8 or higher
python -m src.cli search "robotics" --min-score 0.8
```

## Metadata Command

The `metadata` command allows you to search the archive using only metadata filters, without a text query.

### Basic Metadata Search

```bash
python -m src.cli metadata --author "eric@sssi.com"
```

This searches for all documents by a specific author.

### Command Parameters

```
Options:
  -a, --author TEXT           Filter by author
  -y, --year INTEGER          Filter by year
  -m, --month INTEGER         Filter by month
  -d, --day INTEGER           Filter by day
  -kw, --keyword TEXT         Filter by keyword (can be used multiple times)
  -k, --top-k INTEGER         Number of results to return  [default: 10]
  --help                      Show this message and exit.
```

### Example Metadata Searches

```bash
# Find documents from a specific year
python -m src.cli metadata --year 2007

# Find documents with specific keywords
python -m src.cli metadata --keyword "dprg" --keyword "video"

# Combined metadata filters
python -m src.cli metadata --author "eric@sssi.com" --year 2007
```

Note: At least one metadata filter must be provided when using the `metadata` command.

## Output Format

The CLI presents search results in a nicely formatted table with:
- Relevance score
- Document title
- Author
- Date
- Text excerpt

For each query, you'll also see:
- The search parameters used
- Total number of results found
- Search time in seconds

## Environment Configuration

The CLI respects the configuration set in your `.env` file. If you encounter errors:

1. Ensure your `.env` file is properly configured
2. Check that you have valid Pinecone and OpenAI API keys
3. Verify your network connection

See the [Setup and Configuration](setup_and_configuration.md) guide for more details. 