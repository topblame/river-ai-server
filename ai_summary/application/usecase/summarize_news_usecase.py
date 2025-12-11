from typing import List
from ai_summary.application.port.llm_summary_port import LLMSummaryPort

class SummarizeNewsUseCase:
    def __init__(self, llm_port: LLMSummaryPort):
        self.llm_port = llm_port

    def execute(self, content: str, keywords: List[str]) -> str:
        # 5. 키워드 기반 GPT 요약
        return self.llm_port.summarize(content, keywords)