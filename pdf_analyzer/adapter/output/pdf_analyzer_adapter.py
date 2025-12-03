# pdf_analyzer/adapter/output/pdf_analyzer_adapter.py

import os
from typing import Dict, Any

import requests

from documents.domain.port.pdf_analyzer_port import PdfAnalyzerPort


class PdfAnalyzerAdapter(PdfAnalyzerPort):
    """
    PdfAnalyzerPort 구현체.
    같은 서버에서 구동 중인 pdf_analyzer FastAPI 라우터
    (POST /pdf-analyzer/analyze)를 HTTP로 호출해 분석 결과를 가져온다.
    """

    def __init__(self) -> None:
        # 기본적으로 같은 FastAPI 인스턴스를 향하도록 설정
        self.base_url = os.getenv("PDF_ANALYZER_BASE_URL", "http://localhost:33333")

    def analyze(self, file_url: str) -> Dict[str, Any]:
        """
        file_url: S3에 업로드된 PDF의 전체 URL.
        예: https://{bucket}.s3.{region}.amazonaws.com/{key}
        """

        endpoint = f"{self.base_url}/pdf-analyzer/analyze"

        try:
            response = requests.post(
                endpoint,
                json={"file_url": file_url},
                timeout=120,
            )
        except requests.RequestException as e:
            # 네트워크/타임아웃 등
            raise RuntimeError(f"pdf_analyzer 호출 중 오류가 발생했습니다: {e}") from e

        if not response.ok:
            # FastAPI 쪽에서 4xx/5xx를 반환한 경우
            try:
                detail = response.json().get("detail")
            except Exception:
                detail = response.text
            raise RuntimeError(
                f"pdf_analyzer 분석 요청 실패 (status={response.status_code}): {detail}"
            )

        # 분석 결과 JSON (요약/키워드/감성 등)을 그대로 반환
        try:
            return response.json()
        except ValueError as e:
            raise RuntimeError(
                f"pdf_analyzer 응답을 JSON으로 파싱하지 못했습니다: {e}"
            ) from e
