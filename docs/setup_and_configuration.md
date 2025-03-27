# Setup and Configuration

This guide walks you through setting up the DprgArchiveAgent and configuring it for your environment.

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.10 or higher
- A Pinecone account with API key
- An OpenAI account with API key
- Git (for cloning the repository)

## Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/DprgArchiveAgent.git
cd DprgArchiveAgent
```

### Create a Virtual Environment

It's recommended to use a virtual environment to isolate dependencies.

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### Install Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

## Configuration

The agent requires configuration through environment variables, which can be set via a `.env` file.

### Create Environment File

Copy the example environment file to create your own configuration:

```bash
cp .env.example .env
```

Then, edit the `.env` file with your API keys and preferences.

### Configure Environment Variables

Here's an explanation of each environment variable:

#### Essential Settings (Required)

```
# Pinecone API key and environment
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here

# OpenAI API key (for embeddings)
OPENAI_API_KEY=your_openai_api_key_here
```

#### Vector Store Settings

```
# Vector index URLs (pre-configured for DPRG archive)
DENSE_INDEX_URL=https://dprg-list-archive-dense-4p4f7lg.svc.aped-4627-b74a.pinecone.io
SPARSE_INDEX_URL=https://dprg-list-archive-sparse-4p4f7lg.svc.aped-4627-b74a.pinecone.io

# Namespace
PINECONE_NAMESPACE=dprg-archive
```

#### API Server Settings

```
# API settings
API_HOST=0.0.0.0  # Listen on all interfaces
API_PORT=8000     # Port for the API server
API_WORKERS=4     # Number of worker processes
```

#### Search Settings

```
# Search settings
DEFAULT_TOP_K=10              # Default number of results to return
MIN_SCORE_THRESHOLD=0.7       # Minimum similarity score (0-1)

# Hybrid search weights
DENSE_WEIGHT=0.7              # Weight for dense vector results
SPARSE_WEIGHT=0.3             # Weight for sparse vector results

# Embedding model
EMBEDDING_MODEL=text-embedding-3-large  # OpenAI embedding model
```

## Verifying Installation

After installation and configuration, you can verify your setup by running:

```bash
# CLI verification
python -m src.cli --help

# API verification (starts the API server)
python -m src.api
```

### Testing API Connection

Once the API server is running, you can verify it works by visiting:
```
http://localhost:8000/health
```

This endpoint should return a JSON response indicating the health status of the system.

## Next Steps

After completing the setup and configuration, you can proceed to:

- [CLI Usage Guide](cli_usage.md) for command-line operations
- [API Usage Guide](api_usage.md) for using the REST API
- [Example Usage Scenarios](examples.md) for practical examples

## Troubleshooting

### Common Issues

1. **"No module named 'src'"**:
   - Ensure you're in the root directory of the project
   - Verify the virtual environment is activated

2. **"Configuration Invalid" error**:
   - Check that your `.env` file contains all required API keys
   - Verify the API keys are valid

3. **Connection errors with Pinecone**:
   - Verify your Pinecone API key and environment 
   - Check your network connection
   - Ensure the index names are correct

4. **OpenAI API errors**:
   - Check that your OpenAI API key is valid
   - Verify you have sufficient quota for embeddings 