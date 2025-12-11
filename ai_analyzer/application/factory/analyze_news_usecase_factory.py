from ai_analyzer.application.usecase.analyze_news_usecase import AnalyzeNewsUseCase
from ai_analyzer.adapter.output.ai.finbert_sentiment_adapter import FinbertSentimentAdapter
from ai_analyzer.adapter.output.ai.keybert_keyword_adapter import KeybertKeywordAdapter

class AnalyzeNewsUseCaseFactory:
    @staticmethod
    def create() -> AnalyzeNewsUseCase:
        return AnalyzeNewsUseCase(
            sentiment_port=FinbertSentimentAdapter.getInstance(),
            keyword_port=KeybertKeywordAdapter.getInstance()
        )