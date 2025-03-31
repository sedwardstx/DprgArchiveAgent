# Contributing Guidelines

Thank you for your interest in contributing to the DPRG Archive Agent project! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read it before contributing.

## How to Contribute

### 1. Fork the Repository

1. Go to the [GitHub repository](https://github.com/yourusername/DprgArchiveAgent)
2. Click the "Fork" button in the top right
3. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/DprgArchiveAgent.git
   cd DprgArchiveAgent
   ```

### 2. Set Up Development Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### 3. Create a Branch

1. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-fix-name
   ```

2. Make your changes following our [Code Style Guide](code_style_guide.md)

### 4. Commit Changes

1. Stage your changes:
   ```bash
   git add .
   ```

2. Commit with a descriptive message:
   ```bash
   git commit -m "feat: add new feature X"
   # or
   git commit -m "fix: resolve issue Y"
   ```

3. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

### 5. Create a Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select the base branch (usually `main`)
4. Add a description of your changes
5. Request review from team members

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use Google style for docstrings
- Follow TypeScript/JavaScript style guide for frontend code
- Use meaningful variable and function names
- Add comments for complex logic

### Testing

1. Write tests for new features
2. Update existing tests if needed
3. Ensure all tests pass:
   ```bash
   pytest
   ```

4. Check test coverage:
   ```bash
   pytest --cov=src tests/
   ```

### Documentation

1. Update relevant documentation
2. Add inline comments for complex logic
3. Update README.md if needed
4. Add/update API documentation

### Code Review Process

1. Address all review comments
2. Make requested changes
3. Push updates to your branch
4. Request re-review if needed

## Types of Contributions

### Bug Reports

1. Use the GitHub issue tracker
2. Include:
   - Description of the bug
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details

### Feature Requests

1. Use the GitHub issue tracker
2. Include:
   - Description of the feature
   - Use cases
   - Potential implementation
   - Benefits

### Documentation

1. Fix typos and errors
2. Add missing information
3. Improve clarity
4. Add examples

### Code Contributions

1. Bug fixes
2. New features
3. Performance improvements
4. Security fixes

## Getting Help

1. Check existing documentation
2. Review open/closed issues
3. Ask in discussions
4. Contact maintainers

## Release Process

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Create GitHub release
6. Merge to main

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## Questions?

If you have any questions, please:
1. Check existing documentation
2. Open a discussion
3. Contact maintainers

Thank you for contributing to the DPRG Archive Agent project! 