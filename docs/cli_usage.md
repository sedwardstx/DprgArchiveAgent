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
  -ti, --title TEXT           Search for documents by title
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

### Title Search

You can now search for documents by their title using the `--title` or `-ti` flag:

```bash
# Search for documents with titles containing "meeting notes"
python -m src.cli search --title "meeting notes"

# Shorthand version
python -m src.cli search -ti "meeting notes"
```

The title search is case-insensitive and matches any documents where the title contains the specified text.

#### Combining with Other Search Parameters

Title search can be combined with other search parameters:

```bash
# Search for documents with "meeting" in the title and created after 2023-01-01
python -m src.cli search -ti "meeting" --year 2007

# Search for documents with "report" in the title and of specific type
python -m src.cli search -ti "report" -t dense --author "eric@sssi.com"
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
  -ti, --title TEXT           Search for documents by title
  --help                      Show this message and exit.
```

### Example Metadata Searches

```bash
# Find documents from a specific year
python -m src.cli metadata --year 2007

# Find documents with specific keywords
python -m src.cli metadata --keyword "dprg" --keyword "video"

# Find documents with "meeting" in the title
python -m src.cli metadata -ti "meeting"

# Combined metadata filters
python -m src.cli metadata --author "eric@sssi.com" --year 2007 -ti "report"
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

## Chat Command

The CLI now supports an interactive chat mode where you can have a conversation with an AI assistant that has access to the DPRG archive.

### Basic Chat Usage

```bash
python -m src.cli chat
```

This starts an interactive chat session where you can ask questions about the DPRG archive.

### Chat Options

```
Options:
  -t, --type TEXT          Search type to use for retrieving context: dense, sparse, or hybrid  [default: dense]
  -k, --top-k INTEGER      Number of documents to retrieve for context  [default: 5]
  --temperature FLOAT      Temperature for response generation  [default: 0.7]
  --help                   Show this message and exit.
```

### Example Chat Session

```bash
# Start a chat session with default parameters
python -m src.cli chat

# Use sparse search for document retrieval
python -m src.cli chat -t sparse

# Retrieve more documents for better context
python -m src.cli chat -k 10

# Use a lower temperature for more deterministic responses
python -m src.cli chat --temperature 0.3
```

During the chat session:
- Type your questions or statements about the DPRG archive
- The agent will retrieve relevant documents and answer based on those documents
- The agent will show you which documents it referenced
- Type 'exit' or 'quit' to end the session

## Environment Configuration

The CLI respects the configuration set in your `.env` file. If you encounter errors:

1. Ensure your `.env` file is properly configured
2. Check that you have valid Pinecone and OpenAI API keys
3. Verify your network connection

See the [Setup and Configuration](setup_and_configuration.md) guide for more details. 