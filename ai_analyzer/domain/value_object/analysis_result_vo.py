from pydantic import BaseModel
from typing import List

class AnalysisResultVO(BaseModel):
    sentiment_label: str
    sentiment_score: float
    keywords: List[str]