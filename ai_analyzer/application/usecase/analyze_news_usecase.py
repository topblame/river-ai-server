from ai_analyzer.application.port.sentiment_analysis_port import SentimentAnalysisPort
from ai_analyzer.application.port.keyword_extraction_port import KeywordExtractionPort
from ai_analyzer.domain.value_object.analysis_result_vo import AnalysisResultVO


class AnalyzeNewsUseCase:
    def __init__(self, sentiment_port: SentimentAnalysisPort, keyword_port: KeywordExtractionPort):
        self.sentiment_port = sentiment_port
        self.keyword_port = keyword_port

    def analyze(self, content: str) -> AnalysisResultVO:
        # 3. 감성 분석 수행
        sentiment_result = self.sentiment_port.analyze(content)

        # 4. 키워드 추출 수행
        keywords = self.keyword_port.extract_keywords(content, top_n=5)

        return AnalysisResultVO(
            sentiment_label=sentiment_result['label'],
            sentiment_score=sentiment_result['score'],
            keywords=keywords
        )