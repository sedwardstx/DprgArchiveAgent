# Development Guide

This guide provides information for developers working on the DPRG Archive Agent project.

## Development Environment Setup

### Prerequisites

1. Python 3.10 or 3.11 (higher versions not yet compatible)
2. Git
3. Virtual environment tool (venv, conda, etc.)
4. Code editor (VS Code recommended)

### Initial Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/DprgArchiveAgent.git
   cd DprgArchiveAgent
   ```

2. Create and activate a virtual environment:
   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Or using conda
   conda create -n dprg-archive python=3.8
   conda activate dprg-archive
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your development configuration
   ```

### Project Structure

```
DprgArchiveAgent/
├── src/
│   ├── api/              # API endpoints and routes
│   ├── search/           # Search functionality
│   ├── chat/            # Chat interface
│   ├── utils/           # Utility functions
│   └── config/          # Configuration management
├── tests/               # Test files
├── docs/               # Documentation
├── scripts/            # Development scripts
└── requirements/       # Dependency files
```

## Development Workflow

### 1. Branch Management

- Main branch: `main`
- Development branch: `develop`
- Feature branches: `feature/feature-name`
- Bug fix branches: `fix/bug-name`
- Release branches: `release/version`

### 2. Code Style

Follow the project's code style guide:
- Use PEP 8 for Python code
- Use Google style for docstrings
- Follow TypeScript/JavaScript style guide for frontend code
- Use meaningful variable and function names
- Add comments for complex logic

### 3. Testing

1. Run tests:
   ```bash
   pytest
   ```

2. Run with coverage:
   ```bash
   pytest --cov=src tests/
   ```

3. Run specific test files:
   ```bash
   pytest tests/test_search.py
   ```

### 4. Documentation

1. Update documentation when adding new features
2. Keep API documentation up to date
3. Add inline comments for complex logic
4. Update README.md for major changes

### 5. Code Review Process

1. Create a pull request
2. Ensure all tests pass
3. Update documentation
4. Request review from team members
5. Address feedback
6. Merge after approval

## Development Tools

### VS Code Extensions

Recommended extensions:
- Python
- Pylance
- GitLens
- REST Client
- Markdown All in One

### Development Scripts

Available scripts in the `scripts/` directory:
- `setup-dev.sh`: Setup development environment
- `run-tests.sh`: Run test suite
- `lint.sh`: Run linters
- `format.sh`: Format code

## Debugging

### Local Development

1. Enable debug logging:
   ```bash
   DEBUG=true python -m src.api
   ```

2. Use VS Code debugger:
   - Set breakpoints
   - Use debug console
   - Watch variables

### API Testing

Use the REST Client extension in VS Code:
```http
### Search Request
POST http://localhost:8000/api/v1/search
Content-Type: application/json

{
    "query": "test query",
    "year": 2007
}
```

## Performance Optimization

1. Profile code:
   ```bash
   python -m cProfile -o profile.stats src/api.py
   ```

2. Analyze results:
   ```bash
   python -m pstats profile.stats
   ```

3. Memory profiling:
   ```bash
   python -m memory_profiler src/api.py
   ```

## Security Considerations

1. Never commit sensitive data
2. Use environment variables for secrets
3. Validate all user input
4. Follow security best practices
5. Regular security audits

## Deployment

### Local Testing

1. Build Docker image:
   ```bash
   docker build -t dprg-archive-agent .
   ```

2. Run container:
   ```bash
   docker run -p 8000:8000 dprg-archive-agent
   ```

### Production Deployment

See the [Deployment Guide](deployment_guide.md) for production deployment instructions.

## Troubleshooting

Common issues and solutions:

1. **API Connection Issues**
   - Check environment variables
   - Verify network connectivity
   - Check API keys

2. **Test Failures**
   - Update test data
   - Check environment setup
   - Verify dependencies

3. **Performance Issues**
   - Check logging levels
   - Monitor resource usage
   - Profile code execution

## Getting Help

1. Check documentation
2. Review existing issues
3. Contact team members
4. Create detailed bug reports

## Contributing

See the [Contributing Guidelines](contributing.md) for information about contributing to the project. 