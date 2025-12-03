from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Any, Dict

from documents.application.usecase.document_usecase import DocumentUseCase
from documents.infrastructure.repository.document_repository_impl import DocumentRepositoryImpl
# from account.adapter.input.web.session_helper import get_current_user  # 세션 연동 시

router = APIRouter(tags=["documents"])

repository = DocumentRepositoryImpl.getInstance()
document_usecase = DocumentUseCase(repository)


class UpdateResultRequest(BaseModel):
    result: Dict[str, Any]
    status: str | None = "completed"  # "completed" or "failed"


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_document(
    file: UploadFile = File(...),
    # uploader_id: int = Depends(get_current_user),
):
    # 1) S3 업로드
    s3_key, file_name = await document_usecase.upload_file_to_s3(file)

    # 로그인 붙이기 전까지는 임시 0
    uploader_id = 0

    # 2) DB 등록 (status="processing", result=None)
    doc_dto = document_usecase.register_document(
        file_name=file_name,
        s3_key=s3_key,
        uploader_id=uploader_id,
    )
    return doc_dto


@router.get("/list")
async def list_documents():
    return document_usecase.list_documents()


@router.get("/{document_id}")
async def get_document(document_id: int):
    doc = document_usecase.get_document_by_id(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.patch("/{document_id}/result")
async def update_document_result(
    document_id: int,
    payload: UpdateResultRequest,
):
    """
    pdf_analyzer 또는 프런트에서 분석이 끝난 후
    결과를 DB에 반영할 때 사용.
    """
    try:
        doc = document_usecase.update_result(
            document_id=document_id,
            result=payload.result,
            status=payload.status or "completed",
        )
        return doc
    except ValueError:
        raise HTTPException(status_code=404, detail="Document not found")
