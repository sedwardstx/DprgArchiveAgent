import asyncio
import logging
from src.agent.archive_agent import archive_agent
from src.schema.models import SearchQuery, ChatCompletionRequest, ChatMessage

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_search_and_chat():
    # Test query
    query = "Outdoor Contest Final Rules"
    
    # Test search
    logger.info(f"Testing search with query: {query}")
    search_results = await archive_agent.search(query)
    
    if hasattr(search_results, 'results'):
        logger.info(f"Search found {len(search_results.results)} results")
        for i, doc in enumerate(search_results.results[:3]):  # Show top 3 for brevity
            logger.info(f"Document {i+1}:")
            logger.info(f"  Title: {getattr(doc.metadata, 'title', 'Unknown')}")
            logger.info(f"  Author: {getattr(doc.metadata, 'author', 'Unknown')}")
            logger.info(f"  Excerpt: {doc.text_excerpt[:100]}...")
    else:
        logger.error(f"Search failed: {search_results}")
    
    # Test chat with the same query
    logger.info("\nTesting chat with the same query")
    
    # Create a search query with a lower threshold for debugging
    search_query = SearchQuery(
        query=query,
        search_type="hybrid",
        min_score=0.5,  # Lower threshold for chat context
        top_k=10,       # Retrieve more documents for better context
        filters={}       # No additional filters
    )
            
    # Perform the search with the lower threshold for debugging
    debug_search_results = await archive_agent.search(search_query)
    
    if hasattr(debug_search_results, 'results'):
        logger.info(f"Debug search found {len(debug_search_results.results)} results")
        for i, doc in enumerate(debug_search_results.results[:3]):  # Show top 3
            logger.info(f"Debug Document {i+1}:")
            logger.info(f"  Title: {getattr(doc.metadata, 'title', 'Unknown')}")
            logger.info(f"  Author: {getattr(doc.metadata, 'author', 'Unknown')}")
            logger.info(f"  Score: {doc.score}")
            logger.info(f"  Excerpt: {doc.text_excerpt[:100]}...")
    
    # Test the system prompt building
    if hasattr(debug_search_results, 'results'):
        logger.info("\nTesting system prompt building")
        system_prompt = archive_agent._build_system_prompt(debug_search_results.results)
        logger.info(f"System prompt preview: {system_prompt[:500]}...")
    
    # Now perform the actual chat
    chat_response = await archive_agent.chat(query)
    
    if hasattr(chat_response, 'message'):
        logger.info("\nChat response:")
        logger.info(f"  Content: {chat_response.message.content}")
        logger.info(f"  Referenced documents: {len(chat_response.referenced_documents)}")
    else:
        logger.error(f"Chat failed: {chat_response}")

if __name__ == "__main__":
    asyncio.run(test_search_and_chat()) 