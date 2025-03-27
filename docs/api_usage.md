# API Usage Guide

The DprgArchiveAgent provides a REST API built with [FastAPI](https://fastapi.tiangolo.com/) for programmatic access to the DPRG archive. This guide covers how to use the API effectively.

## Starting the API Server

To start the API server:

```bash
python -m src.api
```

By default, the server will be available at:
- http://localhost:8000

The API documentation (OpenAPI/Swagger) will be available at:
- http://localhost:8000/docs

## API Endpoints

The API provides the following endpoints:

| Endpoint          | Method | Description                              |
|-------------------|--------|------------------------------------------|
| `/`               | GET    | Root endpoint with API info              |
| `/health`         | GET    | Health check endpoint                    |
| `/search`         | GET    | Search the archive with a text query     |
| `/metadata`       | GET    | Search the archive using only metadata   |
| `/chat`           | POST   | Chat completion endpoint                 |

## Endpoint Details

### Health Check

Check if the API is working correctly and properly configured:

```
GET /health
```

Example response:
```json
{
  "status": "healthy",
  "config_valid": true,
  "message": "All systems operational"
}
```

### Search Endpoint

Search the archive with a text query and optional filters:

```
GET /search?query=your+search+query&[additional parameters]
```

#### Query Parameters

| Parameter   | Type    | Description                                         | Default |
|-------------|---------|-----------------------------------------------------|---------|
| query       | string  | The search query text (required)                    | -       |
| top_k       | integer | Number of results to return                         | 10      |
| author      | string  | Filter by author                                    | null    |
| year        | integer | Filter by year                                      | null    |
| month       | integer | Filter by month                                     | null    |
| day         | integer | Filter by day                                       | null    |
| keywords    | string  | Comma-separated keywords to filter by               | null    |
| min_score   | float   | Minimum score threshold (0-1)                       | 0.7     |
| search_type | string  | Search type: "dense", "sparse", or "hybrid"         | "dense" |

#### Response Format

```json
{
  "results": [
    {
      "id": "document_id",
      "text_excerpt": "Document text excerpt...",
      "metadata": {
        "author": "author@example.com",
        "date": "2007-02-15T16:51:29.000Z",
        "day": 15,
        "month": 2,
        "year": 2007,
        "has_url": false,
        "keywords": ["keyword1", "keyword2"],
        "title": "Document Title"
      },
      "score": 0.89
    }
  ],
  "total": 1,
  "query": "your search query",
  "search_type": "dense",
  "elapsed_time": 0.523
}
```

### Metadata Endpoint

Search the archive using only metadata filters:

```
GET /metadata?[metadata parameters]
```

#### Query Parameters

| Parameter | Type    | Description                           | Default |
|-----------|---------|---------------------------------------|---------|
| author    | string  | Filter by author                      | null    |
| year      | integer | Filter by year                        | null    |
| month     | integer | Filter by month                       | null    |
| day       | integer | Filter by day                         | null    |
| keywords  | string  | Comma-separated keywords to filter by | null    |
| top_k     | integer | Number of results to return           | 10      |

Note: At least one metadata filter must be provided.

#### Response Format

The response format is the same as the search endpoint.

### Chat Completion Endpoint

The `/chat` endpoint enables conversational AI interactions with the DPRG archive. The agent reasons over retrieved documents to answer user questions.

#### Request

**URL**: `/chat`

**Method**: `POST`

**Body**:
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant."
    },
    {
      "role": "user",
      "content": "How can I test if my robot's PID controller is working correctly?"
    }
  ],
  "model": "gpt-4o",
  "max_tokens": 1024,
  "temperature": 0.7,
  "search_top_k": 5,
  "use_search_type": "dense"
}
```

**Parameters**:
- `messages` (required): Array of message objects with `role` and `content`. Each message represents a part of the conversation history.
  - Roles can be: `system`, `user`, or `assistant`
- `model` (optional): Model to use for completion (defaults to configuration setting)
- `max_tokens` (optional): Maximum tokens to generate
- `temperature` (optional): Sampling temperature, lower for more deterministic responses
- `search_top_k` (optional): Number of archive documents to retrieve for context (default: 5)
- `use_search_type` (optional): Search type to use: `dense`, `sparse`, or `hybrid` (default: `dense`)

#### Response

```json
{
  "message": {
    "role": "assistant",
    "content": "Based on the DPRG archive information, you can test if your robot's PID controller is working correctly by conducting a squareness test. This involves programming your robot to drive in a square pattern and checking if it returns to its starting position.\n\nAccording to a document from the DPRG archive titled 'PID Controller Testing Methods', you should:\n\n1. Mark your starting position on the floor\n2. Program the robot to drive forward 5 meters\n3. Turn 90 degrees\n4. Drive forward 5 meters\n5. Turn 90 degrees\n6. Drive forward 5 meters\n7. Turn 90 degrees\n8. Drive forward 5 meters\n\nIf the PID controller is tuned correctly, the robot should end up very close to where it started. Measure any deviation from the starting point to assess how well your controller is working."
  },
  "referenced_documents": [
    {
      "id": "doc123",
      "text_excerpt": "Testing a PID controller requires a square path test where the robot is programmed to drive in a square pattern and return to its starting position...",
      "metadata": {
        "author": "John Smith",
        "title": "PID Controller Testing Methods",
        "date": "2021-03-15",
        "keywords": ["robotics", "pid", "testing", "controller"]
      },
      "score": 0.89
    },
    // Additional documents...
  ],
  "elapsed_time": 2.45
}
```

#### Example Usage with cURL

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "How can I test if my robot'\''s PID controller is working correctly?"
      }
    ],
    "search_top_k": 5,
    "use_search_type": "dense",
    "temperature": 0.7
  }'
```

#### Example Usage with Python Requests

```python
import requests
import json

url = "http://localhost:8000/chat"

data = {
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "How can I test if my robot's PID controller is working correctly?"
        }
    ],
    "search_top_k": 5,
    "use_search_type": "dense",
    "temperature": 0.7
}

response = requests.post(url, json=data)
print(json.dumps(response.json(), indent=2))
```

## Making API Requests

### Using cURL

```bash
# Basic search
curl -X GET "http://localhost:8000/search?query=robotics+competition"

# Search with filters
curl -X GET "http://localhost:8000/search?query=progress+video&author=eric@sssi.com&year=2007"

# Metadata search
curl -X GET "http://localhost:8000/metadata?author=eric@sssi.com&year=2007"
```

### Using Python Requests

```python
import requests

# Basic search
response = requests.get(
    "http://localhost:8000/search",
    params={"query": "robotics competition"}
)
results = response.json()
print(f"Found {results['total']} results")

# Search with metadata filters
response = requests.get(
    "http://localhost:8000/search",
    params={
        "query": "progress video",
        "author": "eric@sssi.com",
        "year": 2007,
        "search_type": "hybrid"
    }
)
results = response.json()
```

### Using JavaScript/Fetch

```javascript
// Basic search
fetch('http://localhost:8000/search?query=robotics+competition')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.total} results`);
    data.results.forEach(result => {
      console.log(`${result.metadata.title} (Score: ${result.score})`);
    });
  });

// Search with filters
const params = new URLSearchParams({
  query: 'progress video',
  author: 'eric@sssi.com',
  year: 2007,
  search_type: 'hybrid'
});

fetch(`http://localhost:8000/search?${params.toString()}`)
  .then(response => response.json())
  .then(data => console.log(data));
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid request parameters
- `500 Internal Server Error`: Server-side errors

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## API Configuration

The API server uses the configuration from your `.env` file for:
- Host and port settings
- Number of worker processes
- Vector index connections
- Search parameters

See the [Setup and Configuration](setup_and_configuration.md) guide for details on configuring these settings. 