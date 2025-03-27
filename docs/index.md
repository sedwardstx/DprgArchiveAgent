# DprgArchiveAgent Documentation

Welcome to the documentation for DprgArchiveAgent, an AI-powered search interface for querying the DPRG archive data stored in Pinecone vector indexes.

## Overview

DprgArchiveAgent provides a seamless interface to search through DPRG archives using both dense and sparse vector indexes. The system intelligently routes queries to the appropriate index based on the query type and content, providing optimal search results with either semantic (meaning-based) or keyword search capabilities.

## Documentation Sections

- [Setup and Configuration](setup_and_configuration.md): How to set up the project and configure the environment
- [CLI Usage Guide](cli_usage.md): Documentation for the command-line interface
- [API Usage Guide](api_usage.md): Documentation for the REST API
- [Example Usage Scenarios](examples.md): Practical examples for both CLI and API

## Features

- Search DPRG archives with natural language queries
- Access both dense and sparse vector indexes
- Filter results by metadata (author, date, keywords, etc.)
- CLI interface for quick searches
- REST API for integration with other applications
- Hybrid search combining both dense and sparse search results

## Architecture

The system comprises the following key components:

1. **Vector Index Clients**: Interfaces with the Pinecone dense and sparse vector indexes
2. **Query Processing**: Processes user queries and determines which index strategy to use
3. **Search Tools**: Tools for searching archives with various filters and parameters
4. **User Interfaces**: Both CLI and API interfaces for interacting with the system

## Quick Start

For a quick start, see the [Setup and Configuration](setup_and_configuration.md) guide followed by the [Example Usage Scenarios](examples.md) documentation. 