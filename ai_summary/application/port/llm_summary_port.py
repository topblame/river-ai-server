from abc import ABC, abstractmethod
from typing import List

class LLMSummaryPort(ABC):
    @abstractmethod
    def summarize(self, text: str, keywords: List[str]) -> str:
        pass