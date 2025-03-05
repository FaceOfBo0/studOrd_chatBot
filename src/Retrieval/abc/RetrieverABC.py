from abc import ABC, abstractmethod
from numpy import ndarray

class RetrieverABC(ABC):

    @abstractmethod
    def create_embs(self, docs: list[str]) -> ndarray:
        pass

    @abstractmethod
    def save_embds_to_db_para(self, docs: list[str]):
        pass

    @abstractmethod
    def get_ctx_from_db_para(self, query: str, top_k: int) -> list[str]:
        pass
