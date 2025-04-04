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
  -t, --type TEXT           Search type to use for retrieving context: dense, sparse, or hybrid  [default: hybrid]
  -k, --top-k INTEGER       Number of documents to retrieve for context  [default: 5]
  --temperature FLOAT       Temperature for response generation  [default: 0.7]
  --min-score FLOAT         Minimum score threshold for relevant documents [default: 0.3]
  --max-tokens INTEGER      Maximum tokens for response generation [default: 500]
  --log-level TEXT          Logging verbosity: debug, info, warning, error, critical [default: info]
  --gpt-model TEXT          OpenAI GPT model to use [default: gpt-4]
  --fallback-model TEXT     Fallback OpenAI GPT model [default: gpt-3.5-turbo]
  --help                    Show this message and exit.
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
- Type 'reset', 'clear', or 'restart' to clear conversation history and start fresh

### Special Chat Commands

The chat interface supports several special commands:

| Command | Aliases | Description |
|---------|---------|-------------|
| `exit` | `quit`, `bye`, `goodbye` | End the chat session |
| `reset` | `clear`, `restart` | Clear conversation history and start fresh without exiting |

### Adjusting Search Parameters

You can adjust the search parameters directly from the chat interface using simple commands:

| Parameter | Example Commands | Description |
| --- | --- | --- |
| `top-k` | `set top-k to 20`, `return 30 results` | Change the number of documents retrieved (1-50) |
| `temperature` | `set temperature to 0.8` | Adjust response creativity (0.0-1.0) |
| `min-score` | `set min-score to 0.5`, `set threshold to 0.4` | Modify relevance threshold (0.0-1.0) |
| `search-type` | `set search-type to dense`, `use sparse search` | Change search algorithm (dense, sparse, hybrid) |
| `max-tokens` | `set max-tokens to 1000` | Adjust maximum response length (100-2000) |
| `log-level` | `set log-level to debug`, `set verbosity to info` | Change logging verbosity (debug, info, warning, error, critical) |
| `gpt-model` | `set gpt-model to gpt-4`, `use model gpt-4-turbo` | Set OpenAI model for chat completions |
| `fallback-model` | `set fallback-model to gpt-3.5-turbo` | Set backup model if primary model fails |

### Displaying Current Search Parameters

You can view the current search parameters by asking the agent:

```
> show current settings
> display parameters 
> what settings are you using
> list current configuration
```

This will display a table showing all adjustable parameters, their current values, and descriptions.

### Summarizing Documents

You can ask the agent to summarize a specific document in full, rather than just working with the excerpt shown in the Referenced Documents table:

```
summarize document 3       # Summarize document #3 from the latest results
summarize this post        # Summarize the only document mentioned in the conversation
summary of document 2      # Get a summary of document #2
```

When you ask for a summary, the system will:
1. Retrieve the complete document text (rather than just the excerpt)
2. Provide a more comprehensive summary based on the full content
3. Include details about the document's author, title, and date

This is particularly useful when you want to understand the complete content of a document without having to read through all the raw text.

### General Knowledge Fallback

When you ask a question that doesn't have relevant information in the DPRG archives, the agent will now:

1. Inform you that no relevant information was found in the archives
2. Provide a response based on the LLM's general knowledge about the topic

This helps ensure you get useful answers even when the information isn't available in the DPRG-specific documents. The agent will clearly indicate when it's using its general knowledge versus when it's citing DPRG archive information.

Example:
```
> Tell me about the Borenstein test for robotics
Agent: I couldn't find specific information about a "Borenstein test" in the DPRG archives.

Based on general knowledge, Johann Borenstein is known for his work in mobile robotics, 
particularly in navigation and error correction. He developed methods for dead reckoning error 
correction in mobile robots, including the UMBmark test (University of Michigan Benchmark), 
which measures and corrects systematic odometry errors in differential-drive mobile robots.

This test involves driving the robot in square patterns both clockwise and counter-clockwise 
to identify and quantify systematic errors in the robot's odometry system.
```

## Environment Configuration

The CLI respects the configuration set in your `.env` file. If you encounter errors:

1. Ensure your `.env` file is properly configured
2. Check that you have valid Pinecone and OpenAI API keys
3. Verify your network connection

See the [Setup and Configuration](setup_and_configuration.md) guide for more details. 

| Parameter | Example Commands | Description |
| --- | --- | --- |
| `top-k` | `set top-k to 20`, `return 30 results` | Change the number of documents retrieved (1-50) |
| `temperature` | `set temperature to 0.8` | Adjust response creativity (0.0-1.0) |
| `min-score` | `set min-score to 0.5`, `set threshold to 0.4` | Modify relevance threshold (0.0-1.0) |
| `search-type` | `set search-type to dense`, `use sparse search` | Change search algorithm (dense, sparse, hybrid) |
| `max-tokens` | `set max-tokens to 1000` | Adjust maximum response length (100-2000) |
| `log-level` | `set log-level to debug`, `set verbosity to info` | Change logging verbosity (debug, info, warning, error, critical) |
| `gpt-model` | `set gpt-model to gpt-4`, `use model gpt-4-turbo` | Set OpenAI model for chat completions |
| `fallback-model` | `set fallback-model to gpt-3.5-turbo` | Set backup model if primary model fails |

```
Options:
  -t, --type TEXT           Search type to use for retrieving context: dense, sparse, or hybrid  [default: hybrid]
  -k, --top-k INTEGER       Number of documents to retrieve for context  [default: 5]
  --temperature FLOAT       Temperature for response generation  [default: 0.7]
  --min-score FLOAT         Minimum score threshold for relevant documents [default: 0.3]
  --max-tokens INTEGER      Maximum tokens for response generation [default: 500]
  --log-level TEXT          Logging verbosity: debug, info, warning, error, critical [default: info]
  --gpt-model TEXT          OpenAI GPT model to use [default: gpt-4]
  --fallback-model TEXT     Fallback OpenAI GPT model [default: gpt-3.5-turbo]
  --help                    Show this message and exit.
``` 