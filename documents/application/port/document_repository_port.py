from abc import ABC, abstractmethod
from typing import List, Optional, Any
from fastapi import UploadFile

from documents.domain.document import Document


class DocumentRepositoryPort(ABC):
    @abstractmethod
    async def upload(self, file: UploadFile) -> tuple[str | None, str | None]:
        ...

    @abstractmethod
    def save(self, document: Document) -> Document:
        ...

    @abstractmethod
    def find_all(self) -> List[Document]:
        ...

    @abstractmethod
    def find_by_id(self, document_id: int) -> Optional[Document]:
        ...

    @abstractmethod
    def update_result(
        self, document_id: int, result: dict, status: str | None = None
    ) -> Document:
        ...
