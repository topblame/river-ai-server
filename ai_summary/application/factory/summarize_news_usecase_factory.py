from ai_summary.application.usecase.summarize_news_usecase import SummarizeNewsUseCase
from ai_summary.adapter.output.ai.openai_summary_adapter import OpenAISummaryAdapter

class SummarizeNewsUseCaseFactory:
    @staticmethod
    def create() -> SummarizeNewsUseCase:
        return SummarizeNewsUseCase(
            llm_port=OpenAISummaryAdapter.getInstance()
        )