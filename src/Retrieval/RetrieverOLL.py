from Retrieval.abc.RetrieverABC import RetrieverABC
import ollama, chromadb
from numpy import ndarray

class RetrieverOLL(RetrieverABC):
    """Ollama-based document retriever.
    
    This class implements the RetrieverABC interface using Ollama for creating
    embeddings and ChromaDB for storage and retrieval.
    """

    def __init__(self, model_name: str, db_path: str = ""):
        """Initialize the Ollama retriever.
        
        Args:
            model_name: Name of the Ollama model to use.
            db_path: Optional path to persist the database. If empty, uses in-memory storage.
        """
        
        self._model_name = model_name
        if (db_path == ""):
            self._db = chromadb.Client()
        else:
            self._db = chromadb.PersistentClient(db_path)

    def create_embs(self, docs: list[str]) -> ndarray:
        """Create embeddings using the Ollama model.
        
        Args:
            docs: List of document strings to create embeddings for.
            
        Returns:
            Array of document embeddings.
        """

        embeddings = ollama.embed(model=self._model_name, input=docs)
        return embeddings["embeddings"]

    def save_embds_to_db(self, docs: list[str]):
        """Save document embeddings to ChromaDB.
        
        Args:
            docs: List of document strings to save.
        """

        collection = self._db.create_collection(name="docs")
        embds = ollama.embed(
            model=self._model_name,
            input=docs,
        )

        for i, doc in enumerate(docs):
            collection.add(
                ids=[str(i)],
                embeddings=embds["embeddings"][i],
                documents=[doc]
            )
    
    def get_results_from_db(self, query: str, top_k: int) -> list[str]:
        """Retrieve similar documents from ChromaDB.
        
        Args:
            query: Query string to find similar documents for.
            top_k: Number of most similar documents to retrieve.
            
        Returns:
            List of retrieved document strings.
        """

        collection = self._db.get_collection(name="docs")
        query_embd = ollama.embed(
            model=self._model_name,
            input=query
        )
        
        results = collection.query(
            query_embeddings=query_embd["embeddings"],
            n_results=top_k
        )
        
        return results["documents"][0] if results and results["documents"] else []