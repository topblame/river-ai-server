from pydantic import BaseModel
from typing import List

class SummaryRequest(BaseModel):
    content: str
    keywords: List[str]