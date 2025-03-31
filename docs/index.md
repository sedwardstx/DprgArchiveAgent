# DPRG Archive Agent Documentation

Welcome to the DPRG Archive Agent documentation. This guide will help you understand, set up, and use the DPRG Archive Agent effectively.

## Table of Contents

### Getting Started
- [Setup and Configuration](setup_and_configuration.md)
- [CLI Usage Guide](cli_usage.md)
- [API Reference](api_reference.md)

### Integration Guides
- [WordPress Integration](wordpress_integration.md)
- [Security and Performance Examples](security_and_performance_examples.md)

### Development
- [Development Guide](development_guide.md)
- [Contributing Guidelines](contributing.md)
- [Code Style Guide](code_style_guide.md)

### Testing
- [Testing Guide](testing_guide.md)
- [Test Coverage Report](test_coverage.md)

### Deployment
- [Deployment Guide](deployment_guide.md)
- [Monitoring and Logging](monitoring.md)

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DprgArchiveAgent.git
   cd DprgArchiveAgent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. Start the API server:
   ```bash
   python -m src.api
   ```

## Key Features

- **Advanced Search Capabilities**
  - Semantic search using dense vectors
  - Keyword-based search using sparse vectors
  - Hybrid search combining both approaches
  - Metadata filtering (year, month, author)

- **Interactive Chat Interface**
  - Natural language queries
  - Context-aware responses
  - Document references
  - Conversation history

- **WordPress Integration**
  - Easy-to-use shortcodes
  - Responsive UI components
  - Advanced filtering options
  - Real-time search results

## Configuration

The DPRG Archive Agent can be configured through environment variables. See the [Setup and Configuration](setup_and_configuration.md) guide for detailed information about:

- Essential settings (API keys)
- Vector store configuration
- Search parameters
- Performance tuning
- Debug options

## Security and Performance

For detailed information about implementing security measures and optimizing performance, see:

- [Security and Performance Examples](security_and_performance_examples.md)
  - Rate limiting
  - Input validation
  - Nonce implementation
  - Error handling
  - Response caching
  - Lazy loading
  - Asset optimization

## WordPress Integration

The DPRG Archive Agent can be integrated into WordPress websites. See the [WordPress Integration](wordpress_integration.md) guide for:

- Plugin structure
- UI components
- Security considerations
- Performance optimization
- Maintenance guidelines

## Development

For developers working on the DPRG Archive Agent:

- [Development Guide](development_guide.md) - Setting up the development environment
- [Contributing Guidelines](contributing.md) - How to contribute to the project
- [Code Style Guide](code_style_guide.md) - Coding standards and best practices

## Testing

Comprehensive testing information:

- [Testing Guide](testing_guide.md) - Running and writing tests
- [Test Coverage Report](test_coverage.md) - Current test coverage status

## Deployment

Information about deploying the DPRG Archive Agent:

- [Deployment Guide](deployment_guide.md) - Deployment procedures and requirements
- [Monitoring and Logging](monitoring.md) - Monitoring setup and log management

## Support

For additional support:

1. Check the [Setup and Configuration](setup_and_configuration.md) guide
2. Review the [CLI Usage Guide](cli_usage.md)
3. Consult the [API Reference](api_reference.md)
4. Submit issues through the GitHub repository

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 