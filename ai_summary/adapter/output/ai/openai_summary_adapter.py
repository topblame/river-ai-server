from typing import List
from ai_summary.application.port.llm_summary_port import LLMSummaryPort

# [변경] 이미 설정된 openai client를 가져옵니다.
from config.openai.config import client as openai_client

class OpenAISummaryAdapter(LLMSummaryPort):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            # [변경] 외부에서 생성된 client 주입
            cls.__instance.client = openai_client
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def summarize(self, text: str, keywords: List[str]) -> str:
        keyword_str = ", ".join(keywords)
        prompt = (
            f"다음 금융 뉴스 기사를 요약해줘. "
            f"주요 키워드는 '{keyword_str}'야. "
            f"투자자에게 도움이 되도록 3문장 이내로 핵심만 간결하게 요약해.\n\n"
            f"기사 내용:\n{text}"
        )

        # 동기(sync) 방식 호출
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # gpt-3.5-turbo 등 사용 가능 모델 지정
            messages=[
                {"role": "system", "content": "You are a helpful financial news assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()