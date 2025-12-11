from abc import ABC, abstractmethod
from typing import List

class KeywordExtractionPort(ABC):
    @abstractmethod
    def extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        pass