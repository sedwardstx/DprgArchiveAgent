"""
Command-line interface for the DPRG Archive Agent.
"""
import asyncio
import logging
import sys
from datetime import datetime
from typing import Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .config import validate_config
from .agent.archive_agent import archive_agent
from .schema.models import SearchError

# Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Typer app
app = typer.Typer(
    name="dprg-archive",
    help="Search the DPRG archive using vector search",
    add_completion=False,
)

# Create Rich console for pretty output
console = Console()


def validate_environment():
    """Validate the environment configuration."""
    config_status = validate_config()
    if not config_status["valid"]:
        console.print(
            Panel(
                f"[bold red]Error:[/bold red] {config_status['message']}",
                title="Configuration Error",
                expand=False,
            )
        )
        return False
    return True


def format_date(date_str: Optional[str]) -> str:
    """Format a date string for display."""
    if not date_str:
        return "N/A"
    
    try:
        # Handle datetime objects directly
        if isinstance(date_str, datetime):
            return date_str.strftime("%Y-%m-%d %H:%M:%S")
        
        # Handle string dates
        date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return date.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError, AttributeError) as e:
        # Fall back to returning the original value if conversion fails
        logger.warning(f"Failed to format date: {date_str}, error: {str(e)}")
        return str(date_str)


def display_results(results, query: str, search_type: str):
    """Display search results in a pretty table."""
    if not results or len(results.results) == 0:
        console.print(
            Panel(
                f"No results found for query: [bold]{query}[/bold]",
                title="Search Results",
                expand=False,
            )
        )
        return
    
    # Create table
    table = Table(
        title=f"Search Results for: '{query}' (using {search_type} search)",
        show_header=True,
        header_style="bold magenta",
    )
    
    # Add columns
    table.add_column("Score", justify="right")
    table.add_column("Title")
    table.add_column("Author")
    table.add_column("Date")
    table.add_column("Excerpt", no_wrap=False)
    
    # Add rows
    for doc in results.results:
        try:
            # Handle date formatting safely
            date_display = "N/A"
            if doc.metadata.date:
                date_display = format_date(doc.metadata.date) 

            table.add_row(
                f"{doc.score:.2f}" if doc.score else "N/A",
                doc.metadata.title or "No Title",
                doc.metadata.author or "Unknown",
                date_display,
                doc.text_excerpt[:100] + "..." if len(doc.text_excerpt) > 100 else doc.text_excerpt,
            )
        except Exception as e:
            # Log the error but continue processing other results
            logger.error(f"Error formatting result: {str(e)}")
            continue
    
    # Add search stats
    console.print(
        f"Found {results.total} results in {results.elapsed_time:.2f}s",
        style="italic",
    )
    
    # Print table
    console.print(table)


@app.command("search")
def search(
    query: str = typer.Argument(..., help="Search query text"),
    top_k: int = typer.Option(10, "--top-k", "-k", help="Number of results to return"),
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Filter by author"),
    year: Optional[int] = typer.Option(None, "--year", "-y", help="Filter by year"),
    month: Optional[int] = typer.Option(None, "--month", "-m", help="Filter by month"),
    day: Optional[int] = typer.Option(None, "--day", "-d", help="Filter by day"),
    keywords: Optional[List[str]] = typer.Option(None, "--keyword", "-kw", help="Filter by keyword (can be used multiple times)"),
    min_score: Optional[float] = typer.Option(0.5, "--min-score", "-s", help="Minimum score threshold"),
    search_type: str = typer.Option("dense", "--type", "-t", help="Search type: dense, sparse, or hybrid"),
):
    """
    Search the DPRG archive.
    """
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Show search parameters
    console.print(
        Panel(
            f"Query: [bold]{query}[/bold]\n"
            f"Search Type: [cyan]{search_type}[/cyan]\n"
            f"Filters: "
            f"{f'Author=[blue]{author}[/blue]' if author else ''} "
            f"{f'Year=[blue]{year}[/blue]' if year else ''} "
            f"{f'Month=[blue]{month}[/blue]' if month else ''} "
            f"{f'Day=[blue]{day}[/blue]' if day else ''} "
            f"{f'Keywords=[blue]{keywords}[/blue]' if keywords else ''}",
            title="Search Parameters",
            expand=False,
        )
    )
    
    # Execute search
    with console.status(f"Searching for '{query}'...", spinner="dots"):
        try:
            if search_type == "hybrid":
                result = asyncio.run(
                    archive_agent.search_hybrid(
                        query=query,
                        top_k=top_k,
                        author=author,
                        year=year,
                        month=month,
                        day=day,
                        keywords=keywords,
                        min_score=min_score,
                    )
                )
            elif search_type == "sparse":
                result = asyncio.run(
                    archive_agent.search_sparse(
                        query=query,
                        top_k=top_k,
                        author=author,
                        year=year,
                        month=month,
                        day=day,
                        keywords=keywords,
                        min_score=min_score,
                    )
                )
            else:  # dense
                result = asyncio.run(
                    archive_agent.search_dense(
                        query=query,
                        top_k=top_k,
                        author=author,
                        year=year,
                        month=month,
                        day=day,
                        keywords=keywords,
                        min_score=min_score,
                    )
                )
                
            # Check for error
            if isinstance(result, SearchError):
                console.print(f"Error: {result.error}", style="bold red")
                sys.exit(1)
                
            # Display results
            display_results(result, query, search_type)
                
        except Exception as e:
            console.print(f"Error: {str(e)}", style="bold red")
            sys.exit(1)


@app.command("metadata")
def search_metadata(
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Filter by author"),
    year: Optional[int] = typer.Option(None, "--year", "-y", help="Filter by year"),
    month: Optional[int] = typer.Option(None, "--month", "-m", help="Filter by month"),
    day: Optional[int] = typer.Option(None, "--day", "-d", help="Filter by day"),
    keywords: Optional[List[str]] = typer.Option(None, "--keyword", "-kw", help="Filter by keyword (can be used multiple times)"),
    top_k: int = typer.Option(10, "--top-k", "-k", help="Number of results to return"),
):
    """
    Search the DPRG archive by metadata only.
    """
    # Validate environment
    if not validate_environment():
        sys.exit(1)
        
    # At least one metadata field must be provided
    if not any([author, year, month, day, keywords]):
        console.print("Error: At least one metadata filter must be provided", style="bold red")
        sys.exit(1)
    
    # Show search parameters
    console.print(
        Panel(
            f"Metadata Search\n"
            f"Filters: "
            f"{f'Author=[blue]{author}[/blue]' if author else ''} "
            f"{f'Year=[blue]{year}[/blue]' if year else ''} "
            f"{f'Month=[blue]{month}[/blue]' if month else ''} "
            f"{f'Day=[blue]{day}[/blue]' if day else ''} "
            f"{f'Keywords=[blue]{keywords}[/blue]' if keywords else ''}",
            title="Search Parameters",
            expand=False,
        )
    )
    
    # Execute search
    with console.status("Searching by metadata...", spinner="dots"):
        try:
            result = asyncio.run(
                archive_agent.search_by_metadata(
                    author=author,
                    year=year,
                    month=month,
                    day=day,
                    keywords=keywords,
                    top_k=top_k,
                )
            )
                
            # Check for error
            if isinstance(result, SearchError):
                console.print(f"Error: {result.error}", style="bold red")
                sys.exit(1)
                
            # Display results
            display_results(result, "Metadata Search", "metadata")
                
        except Exception as e:
            console.print(f"Error: {str(e)}", style="bold red")
            sys.exit(1)


if __name__ == "__main__":
    app()
