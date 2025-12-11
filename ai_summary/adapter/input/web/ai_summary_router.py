from fastapi import APIRouter
from ai_summary.adapter.input.web.request.summary_request import SummaryRequest
from ai_summary.adapter.input.web.response.summary_response import SummaryResponse  # 추가
from ai_summary.application.factory.summarize_news_usecase_factory import SummarizeNewsUseCaseFactory

ai_summary_router = APIRouter(tags=["AI Summary"])


@ai_summary_router.post("/summarize", response_model=SummaryResponse)  # response_model 지정
async def summarize_news(request: SummaryRequest):
    usecase = SummarizeNewsUseCaseFactory.create()

    # UseCase가 문자열(str)을 반환한다고 가정했을 때
    summary_text = usecase.execute(request.content, request.keywords)

    return SummaryResponse(summary=summary_text)