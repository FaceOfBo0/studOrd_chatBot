from abc import ABC, abstractmethod
from numpy import ndarray

class RetrieverABC(ABC):

    @abstractmethod
    def create_embs(self, docs: list[str]) -> ndarray:
        pass

    @abstractmethod
    def save_embds_to_db(self, docs: list[str], coll: str):
        pass

    @abstractmethod
    def get_results_from_db(self, query: str, top_k: int, coll: str) -> list[str]:
        pass
