# DPRG Archive Agent

A powerful search and chat interface for the DPRG (Dallas Personal Robotics Group) archive, enabling semantic search and natural language interaction with historical DPRG content.

## Overview

The DPRG Archive Agent provides an intelligent interface to search and interact with the DPRG archive through:
- Semantic search capabilities
- Natural language chat interface
- Metadata-based filtering
- Command-line interface (CLI)
- RESTful API

## Features

- **Advanced Search**
  - Semantic search using embeddings
  - Keyword-based search
  - Hybrid search combining both approaches
  - Metadata filtering (author, date, keywords)
  - Title-based search

- **Chat Interface**
  - Natural language interaction
  - Context-aware responses
  - Reference tracking
  - Conversation history

- **Multiple Interfaces**
  - Command-line interface (CLI)
  - RESTful API
  - Web interface (coming soon)

- **Flexible Integration**
  - API key authentication
  - Rate limiting
  - Comprehensive error handling
  - Detailed documentation

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/sedwardstx/DprgArchiveAgent.git
   cd DprgArchiveAgent
   ```

2. Create and activate a virtual environment (requires Python 3.10 or 3.11, higher versions not yet compatible):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. Run the application:
   ```bash
   python -m src.main
   ```

## Documentation

For detailed documentation, please visit our [Documentation Index](docs/index.md) which includes:

- [Setup and Configuration](docs/setup_and_configuration.md)
- [API Reference](docs/api_reference.md)
- [CLI Usage Guide](docs/cli_usage.md)
- [Usage Examples](docs/examples.md)
- [Development Guide](docs/development_guide.md)
- [Contributing Guidelines](docs/contributing.md)
- [Code Style Guide](docs/code_style_guide.md)
- [Test Coverage Report](docs/test_coverage.md)
- [Deployment Guide](docs/deployment_guide.md)
- [Monitoring and Logging](docs/monitoring.md)
- [Security and Performance](docs/security_and_performance_examples.md)
- [WordPress Integration](docs/wordpress_integration.md)

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](docs/contributing.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Primary contributor and maintainer: [Steve Edwards](CONTRIBUTORS.md)
- DPRG community for providing the archive content
- Contributors and maintainers listed in [CONTRIBUTORS.md](CONTRIBUTORS.md)
