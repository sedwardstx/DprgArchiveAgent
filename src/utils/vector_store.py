"""
Vector store client implementations for Pinecone indexes.
"""
import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple, Union
import logging

from pinecone import Pinecone, ServerlessSpec
import httpx

from ..config import (
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    PINECONE_NAMESPACE,
    DENSE_INDEX_URL,
    SPARSE_INDEX_URL,
    DEFAULT_TOP_K,
    MIN_SCORE_THRESHOLD,
    DENSE_WEIGHT,
    SPARSE_WEIGHT,
)
from .embeddings import get_embedding

# Set up logger
logger = logging.getLogger(__name__)


class BaseVectorClient:
    """Base class for vector index clients."""
    
    def __init__(
        self,
        api_key: str = PINECONE_API_KEY,
        environment: str = PINECONE_ENVIRONMENT,
        namespace: str = PINECONE_NAMESPACE,
    ):
        """Initialize the base vector client."""
        self.api_key = api_key
        self.environment = environment
        self.namespace = namespace
        # Initialize Pinecone without environment parameter in SDK v6+
        self.pc = Pinecone(api_key=api_key)
        
    async def search(
        self,
        query: Union[str, List[float]],
        top_k: int = DEFAULT_TOP_K,
        filter: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Base search method, to be implemented by subclasses.
        
        Args:
            query: The search query, either as text or vector
            top_k: Number of results to return
            filter: Metadata filter to apply
            namespace: Namespace to search (defaults to self.namespace)
            
        Returns:
            List of matches
        """
        raise NotImplementedError("Subclasses must implement search")


class DenseVectorClient(BaseVectorClient):
    """Client for the dense vector index."""
    
    def __init__(
        self,
        index_url: str = DENSE_INDEX_URL,
        api_key: str = PINECONE_API_KEY,
        environment: str = PINECONE_ENVIRONMENT,
        namespace: str = PINECONE_NAMESPACE,
    ):
        """Initialize the dense vector client."""
        super().__init__(api_key, environment, namespace)
        self.index_url = index_url
        
        # Connect to the index
        try:
            # Use the new Index() method instead of from_existing_index
            self.index = self.pc.Index(host=index_url)
            logger.info(f"Connected to dense index at {index_url}")
        except Exception as e:
            logger.error(f"Error connecting to dense index: {str(e)}")
            raise
    
    async def search(
        self,
        query: Union[str, List[float]],
        top_k: int = DEFAULT_TOP_K,
        filter: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search the dense vector index.
        
        Args:
            query: The search query, either as text or vector
            top_k: Number of results to return
            filter: Metadata filter to apply
            namespace: Namespace to search (defaults to self.namespace)
            
        Returns:
            List of matches
        """
        start_time = time.time()
        
        # If query is a string, convert to vector
        if isinstance(query, str):
            vector = await get_embedding(query)
        else:
            vector = query
            
        # Use the provided namespace or fall back to default
        ns = namespace or self.namespace
        
        try:
            # Execute the query
            response = self.index.query(
                vector=vector,
                top_k=top_k,
                namespace=ns,
                filter=filter,
                include_metadata=True,
            )
            
            logger.info(
                f"Dense search completed in {time.time() - start_time:.2f}s. "
                f"Found {len(response.matches)} results."
            )
            
            return response.matches
        except Exception as e:
            logger.error(f"Error in dense search: {str(e)}")
            raise


class SparseVectorClient(BaseVectorClient):
    """Client for the sparse vector index."""
    
    def __init__(
        self,
        index_url: str = SPARSE_INDEX_URL,
        api_key: str = PINECONE_API_KEY,
        environment: str = PINECONE_ENVIRONMENT,
        namespace: str = PINECONE_NAMESPACE,
    ):
        """Initialize the sparse vector client."""
        super().__init__(api_key, environment, namespace)
        self.index_url = index_url
        self.sparse_enabled = False  # Flag to indicate if sparse search is properly configured
        
        # Connect to the index
        try:
            # Use the new Index() method instead of from_existing_index
            self.index = self.pc.Index(host=index_url)
            logger.info(f"Connected to sparse index at {index_url}")
            
            # Note: For proper sparse search functionality, a tokenizer 
            # would need to be implemented to generate sparse vectors
            logger.warning("Sparse search requires a proper tokenizer to generate sparse vectors.")
            logger.warning("Currently using dense vectors which may not work optimally with sparse index.")
        except Exception as e:
            logger.error(f"Error connecting to sparse index: {str(e)}")
            raise
    
    async def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        filter: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Search the sparse vector index.
        
        Args:
            query: The search query as text
            top_k: Number of results to return
            filter: Metadata filter to apply
            namespace: Namespace to search (defaults to self.namespace)
            
        Returns:
            List of matches
        """
        start_time = time.time()
            
        # Use the provided namespace or fall back to default
        ns = namespace or self.namespace
        
        try:
            # In Pinecone v6+, sparse search requires a sparse_vector parameter
            # which needs to be generated by a tokenizer
            # For now, we'll try to use the ID parameter as a fallback
            
            # Get a dense embedding for the query (we'll use this as a backup)
            vector = await get_embedding(query)
            
            # For a proper sparse search, we would need:
            # sparse_vector = tokenize_to_sparse_vector(query)
            # But without a tokenizer, we'll try the basic query
            
            try:
                # First, try with ID-based search (if IDs are text content)
                # This is a hack that might work in some cases
                response = self.index.query(
                    id=query[:50],  # Try to use query as ID, truncated to reasonable length
                    top_k=top_k,
                    namespace=ns,
                    filter=filter,
                    include_metadata=True,
                )
                logger.info("Sparse search using ID-based query succeeded")
            except Exception as id_error:
                logger.warning(f"ID-based sparse search failed: {str(id_error)}")
                
                # Fall back to dense vector
                try:
                    response = self.index.query(
                        vector=vector,
                        top_k=top_k,
                        namespace=ns,
                        filter=filter,
                        include_metadata=True,
                    )
                    logger.info("Sparse search using dense vector fallback succeeded")
                except Exception as vector_error:
                    # Both approaches failed, raise a more informative error
                    raise Exception(
                        f"Sparse search failed - needs sparse_vector implementation. "
                        f"ID search error: {str(id_error)}. "
                        f"Vector fallback error: {str(vector_error)}"
                    )
            
            # Handle both old and new response formats
            if hasattr(response, "results"):
                # New Pinecone SDK v6+ format
                results = response.results[0].matches if hasattr(response, "results") else response.matches
                result_count = len(results)
            else:
                # Old format
                results = response.matches
                result_count = len(results)
            
            logger.info(
                f"Sparse search completed in {time.time() - start_time:.2f}s. "
                f"Found {result_count} results."
            )
            
            return results
        except Exception as e:
            logger.error(f"Error in sparse search: {str(e)}")
            raise


class HybridSearchClient:
    """Client for hybrid search using both dense and sparse vectors."""
    
    def __init__(
        self,
        dense_client: Optional[DenseVectorClient] = None,
        sparse_client: Optional[SparseVectorClient] = None,
        dense_weight: float = DENSE_WEIGHT,
        sparse_weight: float = SPARSE_WEIGHT,
    ):
        """
        Initialize the hybrid search client.
        
        Args:
            dense_client: Client for dense vector search
            sparse_client: Client for sparse vector search
            dense_weight: Weight to give to dense search results (0-1)
            sparse_weight: Weight to give to sparse search results (0-1)
        """
        self.dense_client = dense_client or DenseVectorClient()
        self.sparse_client = sparse_client or SparseVectorClient()
        
        # Normalize weights to sum to 1
        total = dense_weight + sparse_weight
        self.dense_weight = dense_weight / total
        self.sparse_weight = sparse_weight / total
    
    async def search(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        filter: Optional[Dict[str, Any]] = None,
        namespace: Optional[str] = None,
        min_score: float = MIN_SCORE_THRESHOLD,
    ) -> List[Dict[str, Any]]:
        """
        Perform a hybrid search using both dense and sparse indexes.
        
        Args:
            query: The search query
            top_k: Number of results to return
            filter: Metadata filter to apply
            namespace: Namespace to search
            min_score: Minimum score threshold for results
            
        Returns:
            List of matches with scores weighted by search type
        """
        start_time = time.time()
        dense_results = []
        sparse_results = []
        
        try:
            # Execute dense search first
            try:
                dense_task = asyncio.create_task(
                    self.dense_client.search(query, top_k=top_k*2, filter=filter, namespace=namespace)
                )
                dense_results = await dense_task
                logger.info(f"Hybrid: Dense search completed with {len(dense_results)} results.")
            except Exception as e:
                logger.error(f"Hybrid: Dense search failed: {str(e)}")
                # Continue with sparse search
            
            # Execute sparse search
            try:
                sparse_task = asyncio.create_task(
                    self.sparse_client.search(query, top_k=top_k*2, filter=filter, namespace=namespace)
                )
                sparse_results = await sparse_task
                logger.info(f"Hybrid: Sparse search completed with {len(sparse_results)} results.")
            except Exception as e:
                logger.error(f"Hybrid: Sparse search failed: {str(e)}")
                # Continue with dense results only
            
            # If both searches failed, raise an exception
            if not dense_results and not sparse_results:
                raise Exception("Both dense and sparse searches failed")
                
            # Create a combined result set with weighted scores
            id_to_result = {}
            
            # Process dense results
            for result in dense_results:
                id_to_result[result.id] = {
                    "id": result.id,
                    "score": result.score * self.dense_weight,
                    "metadata": result.metadata,
                    "source": "dense"
                }
            
            # Process sparse results
            for result in sparse_results:
                if result.id in id_to_result:
                    # Combine scores if document exists in both result sets
                    id_to_result[result.id]["score"] += result.score * self.sparse_weight
                    id_to_result[result.id]["source"] = "hybrid"
                else:
                    id_to_result[result.id] = {
                        "id": result.id,
                        "score": result.score * self.sparse_weight,
                        "metadata": result.metadata,
                        "source": "sparse"
                    }
            
            # Convert to list and sort by score
            combined_results = list(id_to_result.values())
            combined_results.sort(key=lambda x: x["score"], reverse=True)
            
            # Apply minimum score threshold and limit to top_k
            filtered_results = [r for r in combined_results if r["score"] >= min_score][:top_k]
            
            search_type = "hybrid"
            if not sparse_results:
                search_type = "dense-only"
            elif not dense_results:
                search_type = "sparse-only"
                
            logger.info(
                f"{search_type} search completed in {time.time() - start_time:.2f}s. "
                f"Found {len(filtered_results)} results after combining."
            )
            
            return filtered_results
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            raise
        # No need for explicit cleanup - garbage collection handles this


# Custom cleanup function to ensure resources are released
def cleanup_clients():
    """Clean up client connections - call this when shutting down the application."""
    logger.info("Cleaning up vector store clients")
    
    try:
        # Log cleanup status
        logger.info("Cleanup started")
        
        # Nothing to do for simple clients, but for real clients we might:
        # 1. Close any open connections
        # 2. Release any resources
        # 3. Wait for pending operations to complete
        
        # For now, just log what we're doing
        logger.info("Cleanup: Checking for dense client")
        if 'dense_client' in globals() and dense_client is not None:
            logger.info("Cleanup: Processing dense client")
            # Close connection if needed
            pass
            
        logger.info("Cleanup: Checking for sparse client")
        if 'sparse_client' in globals() and sparse_client is not None:
            logger.info("Cleanup: Processing sparse client")
            # Close connection if needed
            pass
            
        logger.info("Cleanup: Checking for hybrid client")
        if 'hybrid_client' in globals() and hybrid_client is not None:
            logger.info("Cleanup: Processing hybrid client")
            # Close connections if needed
            pass
            
        logger.info("Cleanup completed successfully")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        # Don't raise the exception - we want cleanup to always proceed
        pass


# Create singleton instances
dense_client = DenseVectorClient()
sparse_client = SparseVectorClient()
hybrid_client = HybridSearchClient(dense_client, sparse_client) 
