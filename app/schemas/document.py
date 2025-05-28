from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.document import DocumentStatus

class DocumentBase(BaseModel):
    original_filename: str
    file_type: str
    file_size: int
    title: Optional[str] = None
    author: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    status: Optional[DocumentStatus] = None
    error_message: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None

class DocumentInDBBase(DocumentBase):
    id: int
    filename: str
    status: DocumentStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Document(DocumentInDBBase):
    pass

class DocumentInDB(DocumentInDBBase):
    pass 