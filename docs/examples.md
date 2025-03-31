# Usage Examples

This document provides practical examples of using the DPRG Archive Agent API and CLI.

## API Examples

### Search API

```python
import requests

# Basic search
response = requests.post(
    "http://localhost:8000/api/v1/search",
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "query": "robotics competition",
        "top_k": 10
    }
)

# Search with filters
response = requests.post(
    "http://localhost:8000/api/v1/search",
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "query": "progress video",
        "author": "john.doe@example.com",
        "year": 2007,
        "month": 2,
        "day": 15,
        "keywords": ["dprg", "video"],
        "min_score": 0.8,
        "search_type": "hybrid"
    }
)

# Search by title
response = requests.post(
    "http://localhost:8000/api/v1/search",
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "title": "meeting notes",
        "year": 2007
    }
)
```

### Chat API

```python
# Basic chat
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "message": "What was the DPRG robotics competition in 2007?",
        "search_type": "hybrid",
        "top_k": 5,
        "temperature": 0.7
    }
)

# Chat with context
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "message": "Tell me more about the robot designs",
        "conversation_id": "previous-conversation-id",
        "search_type": "hybrid",
        "top_k": 5
    }
)
```

### Metadata Search API

```python
# Search by metadata only
response = requests.post(
    "http://localhost:8000/api/v1/metadata",
    headers={"Authorization": "Bearer your-api-key"},
    json={
        "author": "john.doe@example.com",
        "year": 2007,
        "keywords": ["dprg", "video"],
        "title": "report"
    }
)
```

## CLI Examples

### Search Command

```bash
# Basic search
python -m src.cli search "robotics competition"

# Search with filters
python -m src.cli search "progress video" --author "john.doe@example.com" --year 2007 --month 2 --day 15

# Search with multiple keywords
python -m src.cli search "competition" --keyword "dprg" --keyword "video"

# Search by title
python -m src.cli search --title "meeting notes" --year 2007

# Search with custom parameters
python -m src.cli search "robotics" --top-k 5 --min-score 0.8 --type hybrid
```

### Metadata Command

```bash
# Search by author
python -m src.cli metadata --author "john.doe@example.com"

# Search by year
python -m src.cli metadata --year 2007

# Search with multiple filters
python -m src.cli metadata --author "john.doe@example.com" --year 2007 --keyword "dprg" --keyword "video"

# Search by title
python -m src.cli metadata --title "meeting notes"
```

### Chat Command

```bash
# Start chat session
python -m src.cli chat

# Chat with custom parameters
python -m src.cli chat --type hybrid --top-k 10 --temperature 0.3
```

## Response Examples

### Search Response

```json
{
    "results": [
        {
            "id": "doc_123",
            "score": 0.95,
            "title": "DPRG Robotics Competition 2007",
            "author": "john.doe@example.com",
            "date": "2007-02-15",
            "excerpt": "The annual DPRG robotics competition was held...",
            "url": "http://example.com/dprg/2007/competition"
        }
    ],
    "total": 1,
    "search_time": 0.15
}
```

### Chat Response

```json
{
    "response": "The DPRG robotics competition in 2007 featured several innovative robot designs...",
    "references": [
        {
            "id": "doc_123",
            "title": "DPRG Robotics Competition 2007",
            "excerpt": "The annual DPRG robotics competition was held...",
            "relevance_score": 0.95
        }
    ],
    "conversation_id": "conv_456",
    "processing_time": 0.25
}
```

### Metadata Response

```json
{
    "results": [
        {
            "id": "doc_123",
            "title": "DPRG Robotics Competition 2007",
            "author": "john.doe@example.com",
            "date": "2007-02-15",
            "keywords": ["dprg", "competition", "robotics"],
            "url": "http://example.com/dprg/2007/competition"
        }
    ],
    "total": 1,
    "search_time": 0.08
}
```

## Error Response Examples

### Authentication Error

```json
{
    "error": "Unauthorized",
    "message": "Invalid or missing API key",
    "status_code": 401
}
```

### Rate Limit Error

```json
{
    "error": "Too Many Requests",
    "message": "Rate limit exceeded. Please try again later.",
    "status_code": 429,
    "retry_after": 60
}
```

### Validation Error

```json
{
    "error": "Bad Request",
    "message": "Invalid search parameters",
    "details": {
        "year": ["Year must be between 1990 and 2024"],
        "month": ["Month must be between 1 and 12"]
    },
    "status_code": 400
}
```

## Best Practices

1. **API Key Management**
   - Store API keys securely
   - Use environment variables
   - Never commit API keys to version control

2. **Error Handling**
   - Always check response status codes
   - Implement proper error handling
   - Handle rate limiting gracefully

3. **Performance**
   - Use appropriate `top_k` values
   - Implement caching where possible
   - Monitor response times

4. **Search Optimization**
   - Use hybrid search for best results
   - Combine text and metadata filters
   - Adjust score thresholds as needed

5. **Chat Usage**
   - Maintain conversation context
   - Use appropriate temperature values
   - Monitor token usage

## Additional Resources

- [API Reference](api_reference.md)
- [CLI Usage Guide](cli_usage.md)
- [Setup and Configuration](setup_and_configuration.md)