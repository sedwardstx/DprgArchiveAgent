# Code Style Guide

This document outlines the coding standards and style guidelines for the DPRG Archive Agent project.

## Python Code Style

### General Guidelines

1. Follow PEP 8 style guide
2. Use meaningful variable and function names
3. Keep functions focused and small
4. Add type hints where appropriate
5. Document complex logic

### Naming Conventions

1. Variables and functions:
   ```python
   # Use snake_case for variables and functions
   user_name = "John"
   def get_user_data():
       pass
   ```

2. Classes:
   ```python
   # Use PascalCase for classes
   class UserManager:
       pass
   ```

3. Constants:
   ```python
   # Use UPPER_CASE for constants
   MAX_RETRIES = 3
   API_BASE_URL = "https://api.example.com"
   ```

### Code Formatting

1. Indentation:
   ```python
   # Use 4 spaces for indentation
   def example_function():
       if condition:
           do_something()
   ```

2. Line length:
   ```python
   # Maximum line length is 88 characters
   # Use parentheses for line continuation
   long_string = (
       "This is a very long string that needs to be "
       "split across multiple lines for readability"
   )
   ```

3. Imports:
   ```python
   # Standard library imports first
   import os
   import sys

   # Third-party imports second
   import requests
   import pandas as pd

   # Local imports last
   from .models import User
   from .utils import helpers
   ```

### Docstrings

1. Use Google style docstrings:
   ```python
   def process_data(data: dict) -> list:
       """Process input data and return formatted results.

       Args:
           data: Dictionary containing input data.

       Returns:
           List of processed results.

       Raises:
           ValueError: If input data is invalid.
       """
       pass
   ```

2. Include type hints:
   ```python
   from typing import List, Dict, Optional

   def get_users(active_only: bool = True) -> List[Dict[str, str]]:
       """Get list of users.

       Args:
           active_only: Whether to return only active users.

       Returns:
           List of user dictionaries.
       """
       pass
   ```

### Error Handling

1. Use specific exceptions:
   ```python
   try:
       result = process_data(data)
   except ValueError as e:
       logger.error(f"Invalid data: {e}")
       raise
   ```

2. Include error messages:
   ```python
   if not data:
       raise ValueError("Input data cannot be empty")
   ```

## TypeScript/JavaScript Code Style

### General Guidelines

1. Use TypeScript for type safety
2. Follow Airbnb style guide
3. Use meaningful variable names
4. Keep functions small and focused
5. Add JSDoc comments for complex logic

### Naming Conventions

1. Variables and functions:
   ```typescript
   // Use camelCase for variables and functions
   const userName = "John";
   function getUserData(): void {
     // ...
   }
   ```

2. Classes and interfaces:
   ```typescript
   // Use PascalCase for classes and interfaces
   interface UserData {
     id: string;
     name: string;
   }

   class UserManager {
     // ...
   }
   ```

3. Constants:
   ```typescript
   // Use UPPER_CASE for constants
   const MAX_RETRIES = 3;
   const API_BASE_URL = "https://api.example.com";
   ```

### Code Formatting

1. Use 2 spaces for indentation
2. Maximum line length: 100 characters
3. Use semicolons at the end of statements
4. Use single quotes for strings
5. Use trailing commas in objects and arrays

### Type Definitions

1. Use explicit types:
   ```typescript
   function processData(data: Record<string, unknown>): string[] {
     // ...
   }
   ```

2. Use interfaces for objects:
   ```typescript
   interface User {
     id: string;
     name: string;
     email: string;
   }
   ```

### Documentation

1. Use JSDoc comments:
   ```typescript
   /**
    * Process input data and return formatted results.
    * @param data - Input data object
    * @returns Array of processed results
    * @throws {Error} If input data is invalid
    */
   function processData(data: Record<string, unknown>): string[] {
     // ...
   }
   ```

## Markdown Documentation

### General Guidelines

1. Use clear headings
2. Include code examples
3. Add links to related documentation
4. Keep paragraphs short
5. Use lists for multiple items

### Formatting

1. Headers:
   ```markdown
   # Main Title
   ## Section
   ### Subsection
   ```

2. Code blocks:
   ```markdown
   ```python
   def example():
       pass
   ```
   ```

3. Lists:
   ```markdown
   - Item 1
   - Item 2
     - Subitem 2.1
     - Subitem 2.2
   ```

4. Links:
   ```markdown
   [Link text](url)
   ```

## Git Commit Messages

1. Use conventional commits:
   ```
   feat: add new feature
   fix: resolve bug
   docs: update documentation
   style: format code
   refactor: improve code structure
   test: add tests
   chore: update dependencies
   ```

2. Keep first line under 72 characters
3. Use imperative mood
4. Add detailed description if needed
5. Reference issues when applicable

## Code Review Guidelines

1. Check code style compliance
2. Verify test coverage
3. Review documentation updates
4. Check error handling
5. Look for security issues

## Tools

### Python

1. Black for code formatting
2. isort for import sorting
3. pylint for linting
4. mypy for type checking

### TypeScript/JavaScript

1. Prettier for code formatting
2. ESLint for linting
3. TypeScript compiler for type checking

### Documentation

1. Markdown lint
2. Documentation generators
3. Link checkers

## Continuous Integration

1. Run style checks
2. Run type checks
3. Run tests
4. Generate documentation
5. Check security vulnerabilities

## Resources

- [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Markdown Guide](https://www.markdownguide.org/) 