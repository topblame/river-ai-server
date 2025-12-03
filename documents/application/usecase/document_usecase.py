import os
from typing import List, Dict, Any, Optional

from fastapi import UploadFile, HTTPException

from documents.domain.document import Document
from documents.application.port.document_repository_port import DocumentRepositoryPort


class DocumentUseCase:
    """
    Hexagonal Application 계층.
    - RepositoryPort: S3 업로드 + DB 연동
    - PDF 분석은 여기서 하지 않고, 별도 /pdf-analyzer/analyze 에서 수행.
    """

    def __init__(self, repository: DocumentRepositoryPort) -> None:
        self.repository = repository

    async def upload_file_to_s3(self, file: UploadFile) -> tuple[str, str]:
        """
        S3에 파일 업로드 후 (s3_key, filename)을 반환.
        """
        if file is None:
            raise HTTPException(status_code=404, detail="File Not Found")

        file_key, filename = await self.repository.upload(file=file)
        if not file_key or not filename:
            raise HTTPException(status_code=404, detail="Upload Failed")

        return file_key, filename

    def _build_s3_url(self, s3_key: str) -> str:
        """
        프런트/분석기가 사용할 수 있는 S3 URL 생성.
        예: https://{bucket}.s3.{region}.amazonaws.com/{key}
        """
        bucket = os.getenv("AWS_S3_BUCKET")
        region = os.getenv("AWS_REGION")

        if not bucket or not region:
            raise RuntimeError("AWS_S3_BUCKET 또는 AWS_REGION 환경 변수가 설정되지 않았습니다.")

        return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"

    def _to_dto(self, document: Document) -> Dict[str, Any]:
        """
        프런트에서 바로 사용 가능한 DTO로 변환.
        """
        status = getattr(document, "status", None)
        if status is None:
            status = "completed" if document.result else "processing"

        dto: Dict[str, Any] = {
            "id": document.id,
            "file_name": document.file_name,
            "s3_key": document.s3_key,
            "file_url": self._build_s3_url(document.s3_key),
            "uploader_id": document.uploader_id,
            "uploaded_at": document.uploaded_at.isoformat() if document.uploaded_at else None,
            "updated_at": document.updated_at.isoformat() if document.updated_at else None,
            "result": getattr(document, "result", None),
            "status": status,
        }
        return dto

    def register_document(
        self,
        file_name: str,
        s3_key: str,
        uploader_id: int,
    ) -> Dict[str, Any]:
        """
        1) 도메인 Document 생성
        2) status = "processing" 으로 초기화
        3) Repository.save(document)로 DB에 저장
        4) DTO(dict)로 반환
        """

        doc = Document.create(file_name, s3_key, uploader_id)
        setattr(doc, "status", "processing")

        saved = self.repository.save(doc)
        return self._to_dto(saved)

    def update_result(
        self,
        document_id: int,
        result: Dict[str, Any],
        status: str = "completed",
    ) -> Dict[str, Any]:
        """
        PDF 분석 결과를 DB에 반영.
        - result: LLM 분석 결과 JSON
        - status: "completed" 또는 "failed"
        """

        doc = self.repository.update_result(document_id, result, status)
        return self._to_dto(doc)

    def list_documents(self) -> List[Dict[str, Any]]:
        docs = self.repository.find_all()
        return [self._to_dto(doc) for doc in docs]

    def get_document_by_id(self, document_id: int) -> Optional[Dict[str, Any]]:
        doc = self.repository.find_by_id(document_id)
        if doc is None:
            return None
        return self._to_dto(doc)
