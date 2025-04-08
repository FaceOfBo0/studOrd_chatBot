from abc import ABC, abstractmethod
from numpy import ndarray

class RetrieverABC(ABC):
    """Abstract base class for document retrievers.
    
    This class defines the interface for document retrieval systems that use
    embedding-based similarity search. Implementations should provide methods
    for creating embeddings, saving them to a database, and retrieving similar
    documents.
    """

    @abstractmethod
    def create_embs(self, docs: list[str]) -> ndarray:
        """Create embeddings for a list of documents.
        
        Args:
            docs: List of document strings to create embeddings for.
            
        Returns:
            Array of document embeddings.
        """
        pass

    @abstractmethod
    def save_embds_to_db(self, docs: list[str], coll: str, id_prefix: str):
        """Save document embeddings to a database.
        
        Args:
            docs: List of document strings to save.
            coll: Name of the collection to save to.
            id_prefix: Prefix for document IDs in the database.
        """
        pass

    @abstractmethod
    def get_results_from_db(self, query: str, top_k: int, coll: str) -> list[str]:
        """Retrieve similar documents from the database.
        
        Args:
            query: Query string to find similar documents for.
            top_k: Number of most similar documents to retrieve.
            coll: Name of the collection to search in.
            
        Returns:
            List of retrieved document strings.
        """
        pass
