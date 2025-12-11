from fastapi import APIRouter, HTTPException

from ai_analyzer.adapter.input.web.request.analyze_request import AnalyzeRequest
from ai_analyzer.application.factory.analyze_news_usecase_factory import AnalyzeNewsUseCaseFactory

ai_analyzer_router = APIRouter(tags=["AI Analyzer"])


@ai_analyzer_router.post("/analyze")
async def analyze_financial_news(request: AnalyzeRequest):
    usecase = AnalyzeNewsUseCaseFactory.create()
    result = usecase.analyze(request.content)

    return {
        "sentiment": {
            "label": result.sentiment_label,
            "score": result.sentiment_score
        },
        "keywords": result.keywords
    }