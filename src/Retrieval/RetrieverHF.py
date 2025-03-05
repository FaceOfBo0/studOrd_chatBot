from sentence_transformers import SentenceTransformer
from Retrieval.abc.RetrieverABC import RetrieverABC
from numpy import ndarray
import chromadb

class RetrieverHF(RetrieverABC):
    def __init__(self, model_name: str, db_path: str = ""):
        self._model_name = model_name
        self._model = SentenceTransformer(self._model_name, trust_remote_code=True)
        if (db_path == ""):
            self._db = chromadb.Client()
        else:
            self._db = chromadb.PersistentClient(db_path)


    def create_embs(self, docs: list[str]) -> ndarray:
        embeddings = self._model.encode(docs)
        return embeddings

    def save_embds_to_db_sent(self, docs: list[str]):
        collection = self._db.create_collection(name="docs_sent")
        embds = self._model.encode(docs, device="cuda")

        for i, doc in enumerate(docs):
            collection.add(
                ids=[str(i)],
                embeddings=embds[i],
                documents=[doc]
            )

    def save_embds_to_db_para(self, docs: list[str]):
        collection = self._db.create_collection(name="docs")
        embds = self._model.encode(docs, device="cuda")

        for i, doc in enumerate(docs):
            collection.add(
                ids=[str(i)],
                embeddings=embds[i],
                documents=[doc]
            )

    def get_ctx_from_db_sent(self, query: str, top_k: int) -> list[str]:
        collection = self._db.get_collection(name="docs_sent")
        query_embd = self._model.encode(query, convert_to_numpy=True, device="cuda")
        
        results = collection.query(
            query_embeddings=query_embd,
            n_results=top_k
        )
        
        return results["documents"][0] if results and results["documents"] else []

    def get_ctx_from_db_para(self, query: str, top_k: int) -> list[str]:
        collection = self._db.get_collection(name="docs")
        query_embd = self._model.encode(query, convert_to_numpy=True, device="cuda")
        
        results = collection.query(
            query_embeddings=query_embd,
            n_results=top_k
        )
        
        return results["documents"][0] if results and results["documents"] else []
