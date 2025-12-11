from pydantic import BaseModel
from typing import List

class SentimentDetail(BaseModel):
    label: str
    score: float

class AnalysisResponse(BaseModel):
    sentiment: SentimentDetail
    keywords: List[str]