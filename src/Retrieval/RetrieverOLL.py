from Retrieval.abc.RetrieverABC import RetrieverABC
import ollama, chromadb
from numpy import ndarray

class RetrieverOLL(RetrieverABC):

    def __init__(self, model_name: str, db_path: str = ""):
        self._model_name = model_name
        if (db_path == ""):
            self._db = chromadb.Client()
        else:
            self._db = chromadb.PersistentClient(db_path)

    def create_embs(self, docs: list[str]) -> ndarray:
        embeddings = ollama.embed(model=self._model_name, input=docs)
        return embeddings["embeddings"]

    def save_embds_to_db_para(self, docs: list[str]):
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
    
    def get_ctx_from_db_para(self, query: str, top_k: int) -> list[str]:
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