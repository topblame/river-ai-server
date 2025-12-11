# documents/infrastructure/repository/document_repository_impl.py

import io
import os
import uuid
import boto3

from typing import List
from sqlalchemy.orm import Session

from fastapi import UploadFile

from config.database.session import SessionLocal
from documents.application.port.document_repository_port import DocumentRepositoryPort
from documents.domain.document import Document
from documents.infrastructure.orm.document_orm import DocumentORM


s3_client = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


class DocumentRepositoryImpl(DocumentRepositoryPort):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    async def upload(self, file: UploadFile):
        try:
            file_bytes = await file.read()

            file_key = f"documents/{uuid.uuid4()}-{file.filename}"
            bucket = os.getenv("AWS_S3_BUCKET")
            s3_client.upload_fileobj(
                Fileobj=io.BytesIO(file_bytes),
                Bucket=bucket,
                Key=file_key,
                ExtraArgs={"ContentType": file.content_type},
            )
            print(file_key, file.filename)
            return file_key, file.filename
        except Exception as e:
            print(e)
            return None, None

    def save(self, document: Document) -> Document:
        db: Session = SessionLocal()
        try:
            # result / status 컬럼이 ORM에 있으면 함께 저장
            kwargs = dict(
                file_name=document.file_name,
                s3_key=document.s3_key,
                uploader_id=document.uploader_id,
            )

            if hasattr(DocumentORM, "result"):
                kwargs["result"] = getattr(document, "result", None)
            if hasattr(DocumentORM, "status"):
                kwargs["status"] = getattr(document, "status", None)

            db_obj = DocumentORM(**kwargs)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)

            # DB에서 받은 id와 timestamp, result/status를 도메인 객체에 반영
            document.id = db_obj.id
            document.uploaded_at = db_obj.uploaded_at
            document.updated_at = db_obj.updated_at

            if hasattr(db_obj, "result"):
                document.result = db_obj.result
            if hasattr(db_obj, "status"):
                document.status = db_obj.status

        finally:
            db.close()

        return document

    def find_all(self) -> List[Document]:
        db: Session = SessionLocal()
        documents: List[Document] = []
        try:
            db_objs = db.query(DocumentORM).all()
            for obj in db_objs:
                doc = Document(
                    file_name=obj.file_name,
                    s3_key=obj.s3_key,
                    uploader_id=obj.uploader_id,
                )
                doc.id = obj.id
                doc.uploaded_at = obj.uploaded_at
                doc.updated_at = obj.updated_at
                # result / status 복원
                if hasattr(obj, "result"):
                    doc.result = obj.result
                if hasattr(obj, "status"):
                    doc.status = obj.status
                documents.append(doc)
        finally:
            db.close()

        return documents

    def find_by_id(self, document_id: int) -> Document | None:
        db: Session = SessionLocal()
        try:
            obj = (
                db.query(DocumentORM)
                .filter(DocumentORM.id == document_id)
                .first()
            )
            if obj is None:
                return None
            doc = Document(
                file_name=obj.file_name,
                s3_key=obj.s3_key,
                uploader_id=obj.uploader_id,
            )
            doc.id = obj.id
            doc.uploaded_at = obj.uploaded_at
            doc.updated_at = obj.updated_at
            if hasattr(obj, "result"):
                doc.result = obj.result
            if hasattr(obj, "status"):
                doc.status = obj.status
            return doc
        finally:
            db.close()
    def update_result(
        self,
        document_id: int,
        result: dict,
        status: str | None = None,
    ) -> Document:
        """
        분석 결과 및 상태를 업데이트하고 도메인 Document로 반환.
        """
        db: Session = SessionLocal()
        try:
            obj = (
                db.query(DocumentORM)
                .filter(DocumentORM.id == document_id)
                .first()
            )
            if obj is None:
                raise ValueError(f"Document(id={document_id}) not found")

            obj.result = result
            if hasattr(obj, "status") and status is not None:
                obj.status = status

            db.add(obj)
            db.commit()
            db.refresh(obj)

            doc = Document(
                file_name=obj.file_name,
                s3_key=obj.s3_key,
                uploader_id=obj.uploader_id,
            )
            doc.id = obj.id
            doc.uploaded_at = obj.uploaded_at
            doc.updated_at = obj.updated_at
            doc.result = obj.result
            if hasattr(obj, "status"):
                doc.status = obj.status

            return doc
        finally:
            db.close()


