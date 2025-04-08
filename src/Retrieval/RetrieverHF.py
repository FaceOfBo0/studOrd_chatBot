from sentence_transformers import SentenceTransformer
from Retrieval.abc.RetrieverABC import RetrieverABC
from database import DBHandler
from numpy import ndarray
from torch.cuda import is_available

class RetrieverHF(RetrieverABC):
    """HuggingFace-based document retriever using sentence transformers.
    
    This class implements the RetrieverABC interface using HuggingFace's
    sentence transformers for creating embeddings and ChromaDB for storage
    and retrieval.
    """

    def __init__(self, model_name: str, db_path: str = "", task_name: str = ""):
        """Initialize the HuggingFace retriever.
        
        Args:
            model_name: Name of the HuggingFace model to use.
            db_path: Optional path to persist the database. If empty, uses in-memory storage.
            task_name: Optional task name for task-specific embeddings.
        """
        
        self._model_name = model_name
        self._task_name = task_name
        self._model = SentenceTransformer(self._model_name, trust_remote_code=True)
        self._device = "cuda" if is_available() else "cpu"
        if (db_path == ""):
            self._db = DBHandler.initDB()
        else:
            self._db = DBHandler.initDB(db_path)


    def create_embs(self, docs: list[str]) -> ndarray:
        """Create embeddings using the HuggingFace model.
        
        Args:
            docs: List of document strings to create embeddings for.
            
        Returns:
            Array of document embeddings.
        """

        embeddings = self._model.encode(docs)
        return embeddings

    def save_embds_to_db(self, docs: list[str], coll: str, id_prefix: str):
        """Save document embeddings to ChromaDB.
        
        Args:
            docs: List of document strings to save.
            coll: Name of the collection to save to.
            id_prefix: Prefix for document IDs in the database.
        """

        collection = self._db.get_or_create_collection(name=coll)
        if self._task_name == "":
            embds = self._model.encode(docs, device=self._device)
        else:
            embds = self._model.encode(docs, device=self._device, task=self._task_name, prompt_name=self._task_name)

        for i, doc in enumerate(docs):
            collection.add(
                ids=[id_prefix+str(i)],
                embeddings=embds[i],
                documents=[doc]
            )

    def get_results_from_db(self, query: str, top_k: int, coll: str) -> list[str]:
        """Retrieve similar documents from ChromaDB.
        
        Args:
            query: Query string to find similar documents for.
            top_k: Number of most similar documents to retrieve.
            coll: Name of the collection to search in.
            
        Returns:
            List of retrieved document strings.
        """

        collection = self._db.get_collection(name=coll)
        query_embd = self._model.encode(query, convert_to_numpy=True, device=self._device)

        results = collection.query(
            query_embeddings=query_embd,
            n_results=top_k
        )
        return results["documents"][0] if results and results["documents"] else []
