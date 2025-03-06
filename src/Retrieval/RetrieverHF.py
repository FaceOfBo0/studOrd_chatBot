from sentence_transformers import SentenceTransformer
from Retrieval.abc.RetrieverABC import RetrieverABC
from database import DBHandler
from numpy import ndarray
import chromadb

class RetrieverHF(RetrieverABC):
    def __init__(self, model_name: str, db_path: str = "", device_name: str = ""):
        self._model_name = model_name
        self._model = SentenceTransformer(self._model_name, trust_remote_code=True)
        self._device = "cpu" if device_name == "" else device_name
        if (db_path == ""):
            self._db = DBHandler.initDB()
        else:
            self._db = DBHandler.initDB(db_path)


    def create_embs(self, docs: list[str]) -> ndarray:
        embeddings = self._model.encode(docs)
        return embeddings

    def save_embds_to_db(self, docs: list[str], coll: str):
        collection = self._db.create_collection(name=coll)
        embds = self._model.encode(docs, device=self._device)

        for i, doc in enumerate(docs):
            collection.add(
                ids=[str(i)],
                embeddings=embds[i],
                documents=[doc]
            )

    def get_results_from_db(self, query: str, top_k: int, coll: str) -> list[str]:
        collection = self._db.get_collection(name=coll)
        query_embd = self._model.encode(query, convert_to_numpy=True, device=self._device)
        
        results = collection.query(
            query_embeddings=query_embd,
            n_results=top_k
        )
        
        return results["documents"][0] if results and results["documents"] else []
