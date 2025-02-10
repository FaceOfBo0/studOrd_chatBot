from abc import ABC, abstractmethod

class RetrieverABC(ABC):

    @abstractmethod
    def create_embs(self, docs: list[str]):
        pass

    @abstractmethod
    def create_embds_to_db(self, docs: list[str]):
        pass

    @abstractmethod
    def get_ctx_from_db(self, query: str, top_k: int) -> list[str]:
        pass