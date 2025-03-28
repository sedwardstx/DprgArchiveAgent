"""
Command-line interface for the DPRG Archive Agent.
Uses Typer and Rich for a nice CLI experience.
"""
import asyncio
import logging
import sys
import atexit
import os
import platform
import traceback
from datetime import datetime
from typing import Optional, List, Any, Dict

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich import box

from .config import validate_config, DEFAULT_TOP_K
from .agent.archive_agent import archive_agent
from .schema.models import SearchError, SearchQuery, ChatMessage, ChatCompletionRequest

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

@atexit.register
def final_cleanup():
    """Final cleanup before exit."""
    log_debug("Entering final_cleanup from atexit handler")
    try:
        # Any cleanup needed before exit
        log_debug("Successfully ran cleanup from atexit handler")
    except Exception as e:
        log_debug(f"Error in final_cleanup: {str(e)}")
    log_debug("Exiting final_cleanup from atexit handler")

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
    
    # Print search parameters
    console.print(
        f"Search parameters:",
        style="bold",
    )
    console.print(f"  Query: {query}")
    console.print(f"  Search type: {search_type}")
    console.print(f"  Total results: {results.total}")
    if hasattr(results, 'min_score'):
        console.print(f"  min_score: {results.min_score}")
    if hasattr(results, 'top_k'):
        console.print(f"  top_k: {results.top_k}")
    
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
            return

        # Set min_score to None if no_filter is True
        if no_filter:
            min_score = None
            log_debug("No filter option enabled, setting min_score to None")

        # Build search query
        search_query = SearchQuery(
            query=query,
            top_k=top_k,
            author=author,
            year=year,
            month=month,
            day=day,
            keywords=keywords,
            min_score=min_score,
            search_type=search_type
        )

        # Execute search
        log_debug(f"Executing search with query: {search_query}")
        results = run_async_safely(archive_agent.search(search_query))
        log_debug("Search completed successfully")

        # Display results
        display_results(results, query, search_type)

    except SearchError as e:
        console.print(f"[bold red]Search Error:[/bold red] {str(e)}")
        log_debug(f"SearchError: {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        log_debug(f"Unexpected error: {str(e)}")
        log_debug(traceback.format_exc())
        sys.exit(1)


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


# Add a chat command
@app.command()
def chat(
    ctx: typer.Context,
    search_type: str = typer.Option(
        "dense", "--type", "-t", 
        help="Search type to use for retrieving context: dense, sparse, or hybrid"
    ),
    top_k: int = typer.Option(
        5, "--top-k", "-k", 
        help="Number of documents to retrieve for context"
    ),
    temperature: float = typer.Option(
        0.7, "--temperature", 
        help="Temperature for response generation"
    ),
):
    """
    Start an interactive chat session with the DPRG Archive Agent.
    The agent will answer questions using information from the archive.
    """
    console = Console()
    
    console.print(
        Panel.fit(
            "[bold blue]DPRG Archive Agent Chat[/bold blue]\n"
            "Ask questions about the DPRG archive. Type 'exit' or 'quit' to end the session.",
            title="Chat Mode",
            border_style="blue"
        )
    )
    
    # Initialize conversation history
    conversation = [
        ChatMessage(
            role="system",
            content="You are an expert on the DPRG (Dallas Personal Robotics Group) archive."
        )
    ]
    
    # Chat loop
    while True:
        # Get user input
        user_input = Prompt.ask("\n[bold green]You[/bold green]")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
            console.print("[bold blue]Agent[/bold blue]: Goodbye! Thanks for chatting.")
            break
        
        # Add user message to conversation
        conversation.append(ChatMessage(role="user", content=user_input))
        
        try:
            # Create chat request
            request = ChatCompletionRequest(
                messages=conversation,
                search_top_k=top_k,
                use_search_type=search_type,
                temperature=temperature
            )
            
            # Indicate that we're thinking
            with console.status("[bold blue]Thinking...[/bold blue]", spinner="dots"):
                # Get response from agent
                response = asyncio.run(archive_agent.chat(request))
            
            # Display referenced documents if any
            if hasattr(response, "referenced_documents") and response.referenced_documents:
                docs_table = Table(title="Referenced Documents", box=box.ROUNDED)
                docs_table.add_column("Title", style="cyan")
                docs_table.add_column("Author", style="green")
                docs_table.add_column("Date", style="yellow")
                
                for doc in response.referenced_documents[:3]:  # Show top 3 docs
                    # Format date if available
                    date_str = ""
                    if doc.metadata.year:
                        date_str = f"{doc.metadata.year}"
                        if doc.metadata.month:
                            date_str += f"-{doc.metadata.month}"
                            if doc.metadata.day:
                                date_str += f"-{doc.metadata.day}"
                    
                    docs_table.add_row(
                        doc.metadata.title or "Untitled",
                        doc.metadata.author or "Unknown",
                        date_str or "Unknown"
                    )
                
                console.print(docs_table)
            
            # Display agent response
            if hasattr(response, "message"):
                console.print("\n[bold blue]Agent[/bold blue]:")
                console.print(Markdown(response.message.content))
                
                # Add assistant message to conversation history
                conversation.append(response.message)
            else:
                console.print("[bold red]Error:[/bold red] Failed to get a response")
        
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")


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
