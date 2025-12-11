# documents/domain/port/pdf_analyzer_port.py

from typing import Protocol, Dict, Any


class PdfAnalyzerPort(Protocol):
    """
    PDF 분석에 대한 도메인 포트 (입출력 규약만 정의).
    DocumentUseCase는 이 인터페이스에만 의존하고,
    구체 구현(LLM 호출, pdf_analyzer 모듈 등)은 어댑터에서 담당한다.
    """

    def analyze(self, file_url: str) -> Dict[str, Any]:
        """
        S3 등에서 접근 가능한 PDF URL을 받아서
        LLM 분석 결과(JSON)를 반환한다.
        """
        ...
