import asyncio
import logging
from src.cli import app
from typer.testing import CliRunner
from src.agent.archive_agent import archive_agent
from src.schema.models import SearchQuery

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

runner = CliRunner()

async def debug_cli_chat():
    """Debug the CLI chat function."""
    query = "What were the Outdoor Contest Final Rules?"
    
    # First, test direct access to archive_agent.chat
    logger.info(f"Testing direct chat with query: {query}")
    chat_response = await archive_agent.chat(query)
    
    if hasattr(chat_response, 'message'):
        logger.info("Direct chat response:")
        logger.info(f"  Content: {chat_response.message.content}")
        logger.info(f"  Referenced documents: {len(chat_response.referenced_documents)}")
    else:
        logger.error(f"Direct chat failed: {chat_response}")
    
    # Then run the CLI command
    logger.info("\nNow testing CLI chat command")
    # We can't run CLI in async mode, but we can print instructions
    logger.info("Run this command in a separate terminal:")
    logger.info(f"python -m src.cli chat --query \"{query}\" --type hybrid")
    
    # Test our understanding of how the system prompt is built
    search_query = SearchQuery(
        query=query,
        search_type="hybrid",
        min_score=0.5,
        top_k=10,
        filters={}
    )
    search_results = await archive_agent.search(search_query)
    if hasattr(search_results, 'results'):
        system_prompt = archive_agent._build_system_prompt(search_results.results)
        logger.info(f"\nSystem prompt used for chat (preview): {system_prompt[:500]}...")

if __name__ == "__main__":
    asyncio.run(debug_cli_chat()) 