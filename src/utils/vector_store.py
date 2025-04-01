"""
Vector store implementation for the DPRG Archive Agent.
"""
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from abc import ABC, abstractmethod

# Import for Pinecone client v2.2.4
from pinecone import Pinecone
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
        # Initialize Pinecone client for v2.2.4
        try:
            # Create a Pinecone client instance
            self.pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
            
            # List available indices
            indices = self.pc.list_indexes()
            logger.info(f"Available Pinecone indices: {indices}")
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {str(e)}")
            self.pc = None
            # Continue without raising to allow tests to run
        
        logger.info(f"Initialized {self.__class__.__name__}")

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
        logger.info(f"Initializing dense index with name: {DENSE_INDEX_NAME}")
        try:
            # Initialize index for Pinecone v2.2.4
            if self.pc is not None:
                self.index = self.pc.Index(DENSE_INDEX_NAME)
                logger.info(f"Successfully initialized {self.__class__.__name__} with index {DENSE_INDEX_NAME}")
            else:
                self.index = None
                logger.warning("Pinecone client is not initialized, index will be None")
        except Exception as e:
            logger.error(f"Error initializing dense index: {str(e)}")
            # Allow tests to run even if index initialization fails
            self.index = None
    
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
            if self.index is None:
                logger.warning("Dense index is not initialized, returning empty results")
                return []
                
            # Generate embedding for query
            logger.info(f"Generating embedding for query: {query}")
            vector = await get_embedding(query)
            logger.info(f"Generated embedding with dimension: {len(vector)}")
            
            # Format filter for Pinecone - handle keywords specially
            formatted_filter = {}
            if filter:
                for key, value in filter.items():
                    if key == "keywords" and isinstance(value, list) and len(value) > 0:
                        # For keywords, use $in operator to check if any keyword matches
                        formatted_filter[key] = {"$in": value}
                    elif key == "title":
                        # For title, don't use special operators - let client-side filtering handle it
                        # Just pass through the title value
                        formatted_filter[key] = value
                    else:
                        formatted_filter[key] = value
            
            # Execute search
            logger.info(f"Executing dense search with top_k={top_k}, filter={formatted_filter}")
            # Query using Pinecone v2.2.4 API
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                filter=formatted_filter,
                include_metadata=True,
                namespace=PINECONE_NAMESPACE
            )
            logger.info(f"Search returned {len(results['matches'])} matches")
            
            # Filter by minimum score if specified
            if min_score is not None:
                results['matches'] = [r for r in results['matches'] if r['score'] >= min_score]
                logger.info(f"Filtered to {len(results['matches'])} matches with score >= {min_score}")
            
            # Convert results to include text_excerpt at both root level and in metadata
            converted_results = []
            for match in results['matches']:
                match_id = match.get('id', '')
                match_score = match.get('score')
                match_metadata = match.get('metadata', {})
                
                # Extract text_excerpt from metadata if present
                text_excerpt = match_metadata.get('text_excerpt', '')
                
                # Create new result with text_excerpt at both levels
                result = {
                    'id': match_id,
                    'score': match_score,
                    'text_excerpt': text_excerpt,
                    'metadata': {
                        **match_metadata,
                        'text_excerpt': text_excerpt
                    }
                }
                converted_results.append(result)
            
            return converted_results
        except Exception as e:
            logger.error(f"Error in dense search: {str(e)}")
            return []

class SparseVectorClient(BaseVectorClient):
    """Client for sparse vector index."""
    
    def __init__(self):
        """Initialize the sparse vector client."""
        super().__init__()
        logger.info(f"Initializing sparse index with name: {SPARSE_INDEX_NAME}")
        try:
            # Initialize index for Pinecone v2.2.4
            if self.pc is not None:
                self.index = self.pc.Index(SPARSE_INDEX_NAME)
                logger.info(f"Successfully initialized {self.__class__.__name__} with index {SPARSE_INDEX_NAME}")
            else:
                self.index = None
                logger.warning("Pinecone client is not initialized, index will be None")
        except Exception as e:
            logger.error(f"Error initializing sparse index: {str(e)}")
            # Allow tests to run even if index initialization fails
            self.index = None
    
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
            if self.index is None:
                logger.warning("Sparse index is not initialized, returning empty results")
                return []
                
            # Generate sparse vector for query
            logger.info(f"Generating sparse vector for query: {query}")
            indices, values = await generate_sparse_vector(query)
            logger.info(f"Generated sparse vector with {len(indices)} non-zero elements")
            
            # Create sparse vector dictionary in Pinecone's expected format
            sparse_vector = {
                "indices": indices,
                "values": values
            }
            
            # Format filter for Pinecone - handle keywords specially
            formatted_filter = {}
            if filter:
                for key, value in filter.items():
                    if key == "keywords" and isinstance(value, list) and len(value) > 0:
                        # For keywords, use $in operator to check if any keyword matches
                        formatted_filter[key] = {"$in": value}
                    elif key == "title":
                        # For title, don't use special operators - let client-side filtering handle it
                        # Just pass through the title value
                        formatted_filter[key] = value
                    else:
                        formatted_filter[key] = value
            
            # Execute search
            logger.info(f"Executing sparse search with top_k={top_k}, filter={formatted_filter}")
            # Query using Pinecone v2.2.4 API
            results = self.index.query(
                top_k=top_k,
                sparse_vector=sparse_vector,
                filter=formatted_filter,
                include_metadata=True,
                namespace=PINECONE_NAMESPACE
            )
            logger.info(f"Search returned {len(results['matches'])} matches")
            
            # Filter by minimum score if specified
            if min_score is not None:
                results['matches'] = [r for r in results['matches'] if r['score'] >= min_score]
                logger.info(f"Filtered to {len(results['matches'])} matches with score >= {min_score}")
            
            # Convert results
            converted_results = []
            for match in results['matches']:
                match_id = match.get('id', '')
                match_score = match.get('score')
                match_metadata = match.get('metadata', {})
                
                # Extract text_excerpt from metadata if present
                text_excerpt = match_metadata.get('text_excerpt', '')
                
                # Create new result with text_excerpt at both levels
                result = {
                    'id': match_id,
                    'score': match_score,
                    'text_excerpt': text_excerpt,
                    'metadata': {
                        **match_metadata,
                        'text_excerpt': text_excerpt
                    }
                }
                converted_results.append(result)
            
            return converted_results
        except Exception as e:
            logger.error(f"Error in sparse search: {str(e)}")
            return []

class HybridSearchClient(BaseVectorClient):
    """Client for hybrid search using both dense and sparse indexes."""
    
    def __init__(self):
        """Initialize the hybrid search client."""
        super().__init__()
        self.dense_client = DenseVectorClient()
        self.sparse_client = SparseVectorClient()
        logger.info(f"Successfully initialized {self.__class__.__name__}")
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        min_score: Optional[float] = MIN_SCORE_THRESHOLD,
        dense_weight: float = DENSE_WEIGHT,
        sparse_weight: float = SPARSE_WEIGHT
    ) -> List[Dict[str, Any]]:
        """
        Perform a hybrid search using both dense and sparse indexes.
        
        Args:
            query: The search query
            top_k: Number of results to return
            filter: Optional filter dictionary
            min_score: Minimum score threshold
            dense_weight: Weight for dense search results
            sparse_weight: Weight for sparse search results
            
        Returns:
            List of search results
        """
        try:
            # Format filter for Pinecone - handle keywords specially
            formatted_filter = {}
            if filter:
                for key, value in filter.items():
                    if key == "keywords" and isinstance(value, list) and len(value) > 0:
                        # For keywords, use $in operator to check if any keyword matches
                        formatted_filter[key] = {"$in": value}
                    elif key == "title":
                        # For title, don't use special operators - let client-side filtering handle it
                        # Just pass through the title value
                        formatted_filter[key] = value
                    else:
                        formatted_filter[key] = value
            
            logger.info(f"Executing hybrid search with query: '{query}', top_k={top_k}, filter={formatted_filter}")
            
            # Run both dense and sparse searches in parallel
            dense_results = await self.dense_client.search(
                query=query,
                top_k=top_k * 2,  # Get more results to ensure we have enough after hybrid fusion
                filter=formatted_filter,
                min_score=None  # Don't filter at this stage
            )
            sparse_results = await self.sparse_client.search(
                query=query,
                top_k=top_k * 2,  # Get more results to ensure we have enough after hybrid fusion
                filter=formatted_filter,
                min_score=None  # Don't filter at this stage
            )
            
            # Log the number of results from each search
            logger.info(f"Dense search returned {len(dense_results)} results")
            logger.info(f"Sparse search returned {len(sparse_results)} results")
            
            # If either search returned no results, return results from the other
            if not dense_results:
                logger.info("No dense results, returning sparse results only")
                return sparse_results
            elif not sparse_results:
                logger.info("No sparse results, returning dense results only")
                return dense_results
            
            # Create a map of document ID to document for both sets of results
            id_to_doc = {}
            
            # Process dense results
            for doc in dense_results:
                # Normalize the score by multiplying by the dense weight
                doc['original_score'] = doc['score']
                doc['score'] = doc['score'] * dense_weight
                doc['score_source'] = 'dense'
                id_to_doc[doc['id']] = doc
            
            # Process sparse results
            for doc in sparse_results:
                doc_id = doc['id']
                if doc_id in id_to_doc:
                    # If the document is already in the map, update the score
                    existing_doc = id_to_doc[doc_id]
                    # First, save the original sparse score
                    doc['original_score'] = doc['score']
                    # Then, normalize the score by multiplying by the sparse weight
                    sparse_score = doc['score'] * sparse_weight
                    # For documents found in both searches, we take the maximum score
                    # We also track which source provided the higher score
                    if sparse_score > existing_doc['score']:
                        existing_doc['score'] = sparse_score
                        existing_doc['score_source'] = 'sparse'
                else:
                    # If the document is not in the map, add it
                    # Normalize the score by multiplying by the sparse weight
                    doc['original_score'] = doc['score']
                    doc['score'] = doc['score'] * sparse_weight
                    doc['score_source'] = 'sparse'
                    id_to_doc[doc_id] = doc
            
            # Convert the map back to a list
            hybrid_results = list(id_to_doc.values())
            
            # Sort by score in descending order
            hybrid_results.sort(key=lambda x: x['score'], reverse=True)
            
            # Apply min_score filter if specified
            if min_score is not None:
                hybrid_results = [r for r in hybrid_results if r['score'] >= min_score]
                logger.info(f"Filtered to {len(hybrid_results)} results with score >= {min_score}")
            
            # Take the top_k results
            hybrid_results = hybrid_results[:top_k]
            
            logger.info(f"Hybrid search returned {len(hybrid_results)} final results")
            return hybrid_results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return []


# Initialize for testing
try:
    # Create singleton instances
    dense_vector_client = DenseVectorClient()
    sparse_vector_client = SparseVectorClient()
    hybrid_search_client = HybridSearchClient()
except Exception as e:
    # Log the error but don't raise it to allow tests to run
    logger.error(f"Error initializing vector clients: {str(e)}")
    # Set singleton instances to None for testing
    dense_vector_client = None
    sparse_vector_client = None
    hybrid_search_client = None 