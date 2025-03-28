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
    DENSE_WEIGHT,
    SPARSE_WEIGHT,
    MIN_SCORE_THRESHOLD
)

# Set up logger
logger = logging.getLogger(__name__)

class BaseVectorClient(ABC):
    """Base class for vector index clients."""
    
    def __init__(self):
        """Initialize the vector client."""
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        logger.info(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search the vector index."""
        pass

class DenseVectorClient(BaseVectorClient):
    """Client for dense vector index."""
    
    def __init__(self):
        """Initialize the dense vector client."""
        super().__init__()
        self.index = self.pc.Index(DENSE_INDEX_NAME)
        logger.info(f"Initialized {self.__class__.__name__} with index {DENSE_INDEX_NAME}")
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search the dense vector index.
        
        Args:
            query: The search query
            top_k: Number of results to return
            filter: Optional filter dictionary
            
        Returns:
            List of search results
        """
        try:
            results = self.index.query(
                vector=query,
                top_k=top_k,
                filter=filter,
                include_metadata=True
            )
            return results.matches
        except Exception as e:
            logger.error(f"Error in dense search: {str(e)}")
            return []

class SparseVectorClient(BaseVectorClient):
    """Client for sparse vector index."""
    
    def __init__(self):
        """Initialize the sparse vector client."""
        super().__init__()
        self.index = self.pc.Index(SPARSE_INDEX_NAME)
        logger.info(f"Initialized {self.__class__.__name__} with index {SPARSE_INDEX_NAME}")
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search the sparse vector index.
        
        Args:
            query: The search query
            top_k: Number of results to return
            filter: Optional filter dictionary
            
        Returns:
            List of search results
        """
        try:
            results = self.index.query(
                vector=query,
                top_k=top_k,
                filter=filter,
                include_metadata=True
            )
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
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining dense and sparse results.
        
        Args:
            query: The search query
            top_k: Number of results to return
            filter: Optional filter dictionary
            
        Returns:
            List of search results
        """
        try:
            # Execute both searches in parallel
            dense_results = await self.dense_client.search(query, top_k, filter)
            sparse_results = await self.sparse_client.search(query, top_k, filter)
            
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
            
            # Filter by minimum score
            results = [r for r in results if r['score'] >= MIN_SCORE_THRESHOLD]
            
            # Return top k results
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return [] 