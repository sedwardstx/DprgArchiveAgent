"""
Vector store implementation for the DPRG Archive Agent.
"""
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from abc import ABC, abstractmethod

from pinecone import Pinecone, ServerlessSpec
from ..config import (
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    DENSE_INDEX_NAME,
    SPARSE_INDEX_NAME,
    DENSE_INDEX_URL,
    SPARSE_INDEX_URL,
    DENSE_WEIGHT,
    SPARSE_WEIGHT,
    MIN_SCORE_THRESHOLD,
    PINECONE_NAMESPACE
)
from .embeddings import get_embedding, generate_sparse_vector

# Set up logger
logger = logging.getLogger(__name__)

class BaseVectorClient(ABC):
    """Base class for vector index clients."""
    
    def __init__(self):
        """Initialize the vector client."""
        logger.info(f"Initializing Pinecone client with API key: {PINECONE_API_KEY[:5]}...")
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        logger.info(f"Initialized {self.__class__.__name__}")
        
        # List available indices
        try:
            indices = self.pc.list_indexes()
            logger.info(f"Available Pinecone indices: {[index.name for index in indices]}")
        except Exception as e:
            logger.error(f"Error listing Pinecone indices: {str(e)}")

    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = MIN_SCORE_THRESHOLD
    ) -> List[Dict[str, Any]]:
        """Search the vector index."""
        pass

class DenseVectorClient(BaseVectorClient):
    """Client for dense vector index."""
    
    def __init__(self):
        """Initialize the dense vector client."""
        super().__init__()
        logger.info(f"Initializing dense index with name: {DENSE_INDEX_NAME} and URL: {DENSE_INDEX_URL}")
        try:
            self.index = self.pc.Index(DENSE_INDEX_NAME, host=DENSE_INDEX_URL)
            logger.info(f"Successfully initialized {self.__class__.__name__} with index {DENSE_INDEX_NAME}")
        except Exception as e:
            logger.error(f"Error initializing dense index: {str(e)}")
            raise
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = MIN_SCORE_THRESHOLD
    ) -> List[Dict[str, Any]]:
        """
        Search the dense vector index.
        
        Args:
            query: The search query
            top_k: Number of results to return
            filter: Optional filter dictionary
            min_score: Minimum score threshold
            
        Returns:
            List of search results
        """
        try:
            # Generate embedding for query
            logger.info(f"Generating embedding for query: {query}")
            vector = await get_embedding(query)
            logger.info(f"Generated embedding with dimension: {len(vector)}")
            
            # Execute search
            logger.info(f"Executing dense search with top_k={top_k}, filter={filter}")
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                filter=filter,
                include_metadata=True,
                namespace=PINECONE_NAMESPACE
            )
            logger.info(f"Search returned {len(results.matches)} matches")
            
            # Filter by minimum score if specified
            if min_score is not None:
                results.matches = [r for r in results.matches if r['score'] >= min_score]
                logger.info(f"Filtered to {len(results.matches)} matches with score >= {min_score}")
            
            return results.matches
        except Exception as e:
            logger.error(f"Error in dense search: {str(e)}")
            return []

class SparseVectorClient(BaseVectorClient):
    """Client for sparse vector index."""
    
    def __init__(self):
        """Initialize the sparse vector client."""
        super().__init__()
        logger.info(f"Initializing sparse index with name: {SPARSE_INDEX_NAME} and URL: {SPARSE_INDEX_URL}")
        try:
            self.index = self.pc.Index(SPARSE_INDEX_NAME, host=SPARSE_INDEX_URL)
            logger.info(f"Successfully initialized {self.__class__.__name__} with index {SPARSE_INDEX_NAME}")
        except Exception as e:
            logger.error(f"Error initializing sparse index: {str(e)}")
            raise
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = MIN_SCORE_THRESHOLD
    ) -> List[Dict[str, Any]]:
        """
        Search the sparse vector index.
        
        Args:
            query: The search query
            top_k: Number of results to return
            filter: Optional filter dictionary
            min_score: Minimum score threshold
            
        Returns:
            List of search results
        """
        try:
            # Generate sparse vector for query
            logger.info(f"Generating sparse vector for query: {query}")
            indices, values = await generate_sparse_vector(query)
            logger.info(f"Generated sparse vector with {len(indices)} non-zero elements")
            
            # Create sparse vector dictionary in Pinecone's expected format
            sparse_vector = {
                "indices": indices,
                "values": values
            }
            
            # Execute search
            logger.info(f"Executing sparse search with top_k={top_k}, filter={filter}")
            results = self.index.query(
                sparse_vector=sparse_vector,
                top_k=top_k,
                filter=filter,
                include_metadata=True,
                namespace=PINECONE_NAMESPACE
            )
            logger.info(f"Search returned {len(results.matches)} matches")
            
            # Filter by minimum score if specified
            if min_score is not None:
                results.matches = [r for r in results.matches if r['score'] >= min_score]
                logger.info(f"Filtered to {len(results.matches)} matches with score >= {min_score}")
            
            return results.matches
        except Exception as e:
            logger.error(f"Error in sparse search: {str(e)}")
            return []

class HybridSearchClient(BaseVectorClient):
    """Client for hybrid search combining dense and sparse results."""
    
    def __init__(self):
        """Initialize the hybrid search client."""
        super().__init__()
        self.dense_client = DenseVectorClient()
        self.sparse_client = SparseVectorClient()
        logger.info(f"Initialized {self.__class__.__name__}")
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = MIN_SCORE_THRESHOLD
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining dense and sparse results.
        
        Args:
            query: The search query
            top_k: Number of results to return
            filter: Optional filter dictionary
            min_score: Minimum score threshold
            
        Returns:
            List of search results
        """
        try:
            # Execute both searches in parallel
            dense_results = await self.dense_client.search(query, top_k, filter, min_score=None)
            sparse_results = await self.sparse_client.search(query, top_k, filter, min_score=None)
            
            # Combine results
            combined_results = {}
            for result in dense_results:
                combined_results[result['id']] = {
                    'id': result['id'],
                    'metadata': result['metadata'],
                    'score': result['score'] * DENSE_WEIGHT
                }
            
            for result in sparse_results:
                if result['id'] in combined_results:
                    combined_results[result['id']]['score'] += result['score'] * SPARSE_WEIGHT
                else:
                    combined_results[result['id']] = {
                        'id': result['id'],
                        'metadata': result['metadata'],
                        'score': result['score'] * SPARSE_WEIGHT
                    }
            
            # Convert to list and sort by score
            results = list(combined_results.values())
            results.sort(key=lambda x: x['score'], reverse=True)
            
            # Filter by minimum score if specified
            if min_score is not None:
                results = [r for r in results if r['score'] >= min_score]
                logger.info(f"Filtered to {len(results)} matches with score >= {min_score}")
            
            # Return top k results
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return [] 