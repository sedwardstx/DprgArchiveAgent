# API Reference

This document provides detailed information about the DPRG Archive Agent API endpoints, request/response formats, and authentication.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All API requests require authentication using a Bearer token:

```http
Authorization: Bearer your_api_key_here
```

## Endpoints

### Search

#### POST /search

Search the DPRG archive using text queries and filters.

**Request Body:**
```json
{
    "query": "string",
    "year": "integer (optional)",
    "month": "integer (optional)",
    "type": "string (optional)",
    "top_k": "integer (optional)",
    "min_score": "float (optional)"
}
```

**Parameters:**
- `query`: Search query text (required)
- `year`: Filter results by year (optional)
- `month`: Filter results by month (optional)
- `type`: Search type - "dense", "sparse", or "hybrid" (optional, default: "hybrid")
- `top_k`: Number of results to return (optional, default: 10)
- `min_score`: Minimum similarity score threshold (optional, default: 0.5)

**Response:**
```json
{
    "results": [
        {
            "id": "string",
            "title": "string",
            "content": "string",
            "author": "string",
            "date": "string",
            "score": "float",
            "metadata": {
                "year": "integer",
                "month": "integer",
                "keywords": ["string"]
            }
        }
    ],
    "total": "integer",
    "took": "float"
}
```

### Chat

#### POST /chat

Interact with the DPRG archive using natural language queries.

**Request Body:**
```json
{
    "message": "string",
    "conversation_id": "string (optional)",
    "context": ["string (optional)"]
}
```

**Parameters:**
- `message`: User's message or question (required)
- `conversation_id`: ID for maintaining conversation context (optional)
- `context`: Additional context for the conversation (optional)

**Response:**
```json
{
    "reply": "string",
    "conversation_id": "string",
    "references": [
        {
            "id": "string",
            "title": "string",
            "excerpt": "string",
            "relevance": "float"
        }
    ]
}
```

### Metadata Search

#### POST /metadata

Search using only metadata filters.

**Request Body:**
```json
{
    "year": "integer (optional)",
    "month": "integer (optional)",
    "author": "string (optional)",
    "keywords": ["string (optional)"],
    "top_k": "integer (optional)"
}
```

**Parameters:**
- `year`: Filter by year (optional)
- `month`: Filter by month (optional)
- `author`: Filter by author (optional)
- `keywords`: Filter by keywords (optional)
- `top_k`: Number of results to return (optional, default: 10)

**Response:**
```json
{
    "results": [
        {
            "id": "string",
            "title": "string",
            "author": "string",
            "date": "string",
            "metadata": {
                "year": "integer",
                "month": "integer",
                "keywords": ["string"]
            }
        }
    ],
    "total": "integer",
    "took": "float"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "error": "string",
    "message": "string",
    "details": {}
}
```

### 401 Unauthorized
```json
{
    "error": "unauthorized",
    "message": "Invalid or missing API key"
}
```

### 429 Too Many Requests
```json
{
    "error": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Please try again later.",
    "retry_after": "integer"
}
```

### 500 Internal Server Error
```json
{
    "error": "internal_server_error",
    "message": "An unexpected error occurred"
}
```

## Rate Limiting

- Rate limit: 100 requests per hour per API key
- Rate limit headers are included in responses:
  - `X-RateLimit-Limit`: Maximum requests per hour
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time until rate limit reset

## Best Practices

1. **Error Handling**
   - Always check response status codes
   - Implement exponential backoff for retries
   - Handle rate limiting gracefully

2. **Performance**
   - Use appropriate `top_k` values
   - Implement client-side caching
   - Minimize unnecessary requests

3. **Security**
   - Keep API keys secure
   - Use HTTPS for all requests
   - Validate all user input

4. **Data Management**
   - Store conversation IDs for chat sessions
   - Cache frequently accessed results
   - Implement proper error logging 