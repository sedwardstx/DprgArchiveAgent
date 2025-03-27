"""
Command-line interface for the DPRG Archive Agent.
"""
import asyncio
import logging
import sys
import atexit
import os
import platform
import traceback
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
from .utils.vector_store import cleanup_clients

# Set up logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up debug logging for crash analysis
DEBUG_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "crash_debug.log")

def log_debug(message):
    """Write a debug message to the log file with a timestamp."""
    with open(DEBUG_LOG_FILE, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        f.write(f"{timestamp} - {message}\n")
        f.flush()  # Force write to disk
        os.fsync(f.fileno())  # Ensure it's written to the filesystem

# Modify the cleanup function to log its activity
@atexit.register
def final_cleanup():
    """Final cleanup before exit."""
    log_debug("Entering final_cleanup from atexit handler")
    try:
        cleanup_clients()
        log_debug("Successfully ran cleanup_clients from atexit handler")
    except Exception as e:
        log_debug(f"Error in final_cleanup: {str(e)}")
    log_debug("Exiting final_cleanup from atexit handler")
    
# Remove the previous atexit registration to avoid double calls
atexit.unregister(cleanup_clients)

# Create Typer app
app = typer.Typer(
    name="dprg-archive",
    help="Search the DPRG archive using vector search",
    add_completion=False,
)

# Create Rich console for pretty output
console = Console()


def run_async_safely(coro):
    """Run an async coroutine safely and handle cleanup properly."""
    log_debug("Starting run_async_safely")
    try:
        # Create a new event loop each time to avoid issues with existing loops
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        log_debug("Created new event loop")
        
        result = loop.run_until_complete(coro)
        log_debug("Coroutine completed successfully")
        return result
    except Exception as e:
        log_debug(f"Exception in run_async_safely: {str(e)}")
        log_debug(traceback.format_exc())
        raise
    finally:
        # Always properly close the loop
        log_debug("Closing event loop")
        loop.close()
        log_debug("Event loop closed")


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
    min_score: Optional[float] = typer.Option(0.3, "--min-score", "-s", help="Minimum score threshold"),
    search_type: str = typer.Option("dense", "--type", "-t", help="Search type: dense, sparse, or hybrid"),
    no_filter: bool = typer.Option(False, "--no-filter", help="Disable minimum score filtering"),
):
    """
    Search the DPRG archive.
    """
    try:
        # Validate environment
        log_debug("Starting search function")
        if not validate_environment():
            log_debug("Environment validation failed")
            sys.exit(1)
        
        # Handle no_filter option
        if no_filter:
            min_score = 0.0
        
        # Show search parameters
        log_debug("Displaying search parameters")
        console.print(
            Panel(
                f"Query: [bold]{query}[/bold]\n"
                f"Search Type: [cyan]{search_type}[/cyan]\n"
                f"Min Score: [cyan]{min_score if min_score else 'None'}[/cyan]\n"
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
        log_debug("Starting search execution")
        with console.status(f"Searching for '{query}'...", spinner="dots"):
            try:
                log_debug(f"Running search with type: {search_type}")
                if search_type == "hybrid":
                    result = run_async_safely(
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
                    result = run_async_safely(
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
                    result = run_async_safely(
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
                    log_debug(f"Search returned error: {result.error}")
                    console.print(f"Error: {result.error}", style="bold red")
                    sys.exit(1)
                    
                # Display results
                log_debug("Displaying search results")
                display_results(result, query, search_type)
                    
                # Explicitly attempt cleanup
                log_debug("Running cleanup_clients from search function")
                cleanup_clients()
                log_debug("Cleanup completed")
                    
            except Exception as e:
                log_debug(f"Exception during search execution: {str(e)}")
                log_debug(traceback.format_exc())
                console.print(f"Error: {str(e)}", style="bold red")
                sys.exit(1)
        
        log_debug("Search completed successfully, returning 0")
        # Add a clean exit to prevent segmentation fault
        return 0
    
    except KeyboardInterrupt:
        log_debug("Search interrupted by user")
        console.print("\nSearch cancelled by user", style="yellow")
        return 1
    except Exception as e:
        log_debug(f"Unexpected error in search: {str(e)}")
        log_debug(traceback.format_exc())
        console.print(f"Unexpected error: {str(e)}", style="bold red")
        logger.exception("Unexpected error during search")
        return 1


@app.command("metadata")
def search_metadata(
    author: Optional[str] = typer.Option(None, "--author", "-a", help="Filter by author"),
    year: Optional[int] = typer.Option(None, "--year", "-y", help="Filter by year"),
    month: Optional[int] = typer.Option(None, "--month", "-m", help="Filter by month"),
    day: Optional[int] = typer.Option(None, "--day", "-d", help="Filter by day"),
    keywords: Optional[List[str]] = typer.Option(None, "--keyword", "-kw", help="Filter by keyword (can be used multiple times)"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="Filter by title (partial match)"),
    top_k: int = typer.Option(10, "--top-k", "-k", help="Number of results to return"),
    min_score: Optional[float] = typer.Option(0.3, "--min-score", "-s", help="Minimum score threshold"),
    no_filter: bool = typer.Option(False, "--no-filter", help="Disable minimum score filtering"),
):
    """
    Search the DPRG archive by metadata only.
    """
    try:
        # Validate environment
        if not validate_environment():
            sys.exit(1)
            
        # Handle no_filter option
        if no_filter:
            min_score = 0.0
            
        # At least one metadata field must be provided
        if not any([author, year, month, day, keywords, title]):
            console.print("Error: At least one metadata filter must be provided", style="bold red")
            sys.exit(1)
        
        # Show search parameters
        console.print(
            Panel(
                f"Metadata Search\n"
                f"Min Score: [cyan]{min_score if min_score else 'None'}[/cyan]\n"
                f"Filters: "
                f"{f'Author=[blue]{author}[/blue]' if author else ''} "
                f"{f'Year=[blue]{year}[/blue]' if year else ''} "
                f"{f'Month=[blue]{month}[/blue]' if month else ''} "
                f"{f'Day=[blue]{day}[/blue]' if day else ''} "
                f"{f'Keywords=[blue]{keywords}[/blue]' if keywords else ''} "
                f"{f'Title=[blue]{title}[/blue]' if title else ''}",
                title="Search Parameters",
                expand=False,
            )
        )
        
        # Execute search
        with console.status("Searching by metadata...", spinner="dots"):
            try:
                result = run_async_safely(
                    archive_agent.search_by_metadata(
                        author=author,
                        year=year,
                        month=month,
                        day=day,
                        keywords=keywords,
                        title=title,
                        top_k=top_k,
                        min_score=min_score,
                    )
                )
                    
                # Check for error
                if isinstance(result, SearchError):
                    console.print(f"Error: {result.error}", style="bold red")
                    sys.exit(1)
                    
                # Display results
                display_results(result, "Metadata Search", "metadata")
                    
                # Explicitly attempt cleanup
                cleanup_clients()
                    
            except Exception as e:
                console.print(f"Error: {str(e)}", style="bold red")
                sys.exit(1)
        
        # Add a clean exit to prevent segmentation fault
        return 0
        
    except KeyboardInterrupt:
        console.print("\nSearch cancelled by user", style="yellow")
        return 1
    except Exception as e:
        console.print(f"Unexpected error: {str(e)}", style="bold red")
        logger.exception("Unexpected error during metadata search")
        return 1


if __name__ == "__main__":
    log_debug(f"Starting CLI with platform: {platform.system()} {platform.release()}")
    log_debug(f"Python version: {sys.version}")
    
    # Special handling for Windows (especially MINGW environment)
    windows_platform = platform.system().lower() == "windows"
    mingw_detected = "mingw" in sys.platform.lower() or "MINGW" in os.environ.get("MSYSTEM", "")
    
    log_debug(f"Windows platform: {windows_platform}, MINGW detected: {mingw_detected}")
    
    try:
        # Using a separate exit wrapper to ensure clean shutdown
        log_debug("Calling app()")
        exit_code = app()
        log_debug(f"App returned exit code: {exit_code}")
        
        # Force immediate exit on Windows with MINGW to avoid segmentation fault
        if windows_platform and mingw_detected:
            log_debug("Windows/MINGW detected, using os._exit to avoid segmentation fault")
            # Force immediate process termination without Python cleanup
            # This avoids segmentation faults in the MINGW environment
            os._exit(exit_code)
        else:
            # Force exit with the code rather than letting Python's cleanup cause issues
            log_debug("Calling sys.exit with exit code")
            sys.exit(exit_code)
    except KeyboardInterrupt:
        # Handle keyboard interrupt cleanly
        log_debug("KeyboardInterrupt in main")
        console.print("\nOperation cancelled by user", style="yellow")
        
        # Force immediate exit on Windows with MINGW
        if windows_platform and mingw_detected:
            os._exit(1)
        else:
            sys.exit(1)
    except Exception as e:
        # Catch and report any unexpected exceptions
        log_debug(f"Fatal error in main: {str(e)}")
        log_debug(traceback.format_exc())
        console.print(f"Unexpected error: {str(e)}", style="bold red")
        logger.exception("Fatal error in main application")
        
        # Force immediate exit on Windows with MINGW
        if windows_platform and mingw_detected:
            os._exit(1)
        else:
            sys.exit(1)
