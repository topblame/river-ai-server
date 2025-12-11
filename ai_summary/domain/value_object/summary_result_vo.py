from pydantic import BaseModel

class SummaryResultVO(BaseModel):
    summary_text: str

    class Config:
        frozen = True  # 불변 객체로 설정 (Value Object 특성)