# DPRG Archive Agent - Usage Examples

This document provides examples for using the DPRG Archive Agent CLI to interact with the archive.

## Semantic Search Examples

Semantic search uses embeddings to find conceptually related content:

```bash
# Basic search with default parameters (dense search, top-k=10, min-score=0.3)
python -m src.cli search "outdoor robot navigation"

# Hybrid search (combines dense and sparse vectors)
python -m src.cli search "line following sensor placement" --type hybrid

# Increase results with lower relevance threshold
python -m src.cli search "UMBMark calibration" --min-score 0.2 --top-k 15

# Metadata filters with semantic search
python -m src.cli search "GPS coordinates" --author "dpa@io.isem.smu.edu" --year 2008
```

## Metadata Search Examples

Metadata search focuses on specific document attributes rather than content:

```bash
# Find all documents by a specific author 
# (uses min-score=0.0 by default to return all matches)
python -m src.cli metadata --author "dpa@io.isem.smu.edu"

# Search by date
python -m src.cli metadata --year 2008 --month 2

# Combine multiple metadata filters
python -m src.cli metadata --author "dpa@io.isem.smu.edu" --year 2008 --top-k 150

# Search by partial title match
python -m src.cli metadata --title "Outdoor Contest" 

# Search by keyword
python -m src.cli metadata --keyword "GPS" --keyword "navigation"
```

Note: Metadata searches use a default min_score of 0.0 to ensure all matching documents are returned, regardless of semantic similarity.

## Chat Interface Examples

The chat interface lets you interact with the archive in natural language:

```bash
# Start interactive chat session
python -m src.cli chat

# One-shot query with default parameters
python -m src.cli chat --query "What is the UMBMark calibration technique?"

# Adjust semantic search parameters for chat 
python -m src.cli chat --query "Tell me about the outdoor contest rules" --min-score 0.4 --top-k 10 --type hybrid

# Control response generation
python -m src.cli chat --query "What navigation approaches were used for robots in 2008?" --temperature 0.8 --max-tokens 300
```

## Advanced Usage

### Filtering and Combining Approaches

```bash
# Search with multiple metadata filters
python -m src.cli search "motion planning" --author "dpa@io.isem.smu.edu" --year 2008 --title "robot"

# Disable minimum score filtering completely
python -m src.cli search "experimental robot designs" --no-filter

# Find documents about a topic within a date range
python -m src.cli metadata --year 2007 --title "outdoor contest" --top-k 50
```

### Troubleshooting Tips

If you're not getting expected results:

1. For metadata searches, try using `--min-score 0.0` to ensure all matching documents are returned
2. For semantic searches that return no results, try lowering the min-score (default is 0.3)
3. When searching for specific authors, use their email address as found in previous search results
4. For chat, increase the context with `--top-k` and lower `--min-score` to provide more information to the model 