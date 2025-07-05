from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class DocumentBase(BaseModel):
    """Base document model"""
    filename: str = Field(..., description="Document filename")
    filetype: str = Field(..., description="Document file type")
    status: str = Field(default="pending", description="Processing status")
    content: Optional[str] = Field(None, description="Extracted text content")

class DocumentCreate(BaseModel):
    """Document creation model"""
    filename: str = Field(..., description="Document filename")
    filetype: str = Field(..., description="Document file type")
    content: Optional[str] = Field(None, description="Extracted text content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class DocumentUpdate(BaseModel):
    """Document update model"""
    status: Optional[str] = Field(None, description="Processing status")
    content: Optional[str] = Field(None, description="Extracted text content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class DocumentOut(DocumentBase):
    """Document output model"""
    id: int
    metadata: Optional[Dict[str, Any]] = Field(None, alias="document_metadata") 
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True
        by_alias = True

class DocumentList(BaseModel):
    """Document list response model"""
    documents: List[DocumentOut]
    total: int
    page: int
    page_size: int

class DocumentSummary(BaseModel):
    """Document summary model"""
    id: int
    filename: str
    filetype: str
    status: str
    content_length: Optional[int] = None
    entity_count: Optional[int] = None
    relationship_count: Optional[int] = None
    created_at: datetime

class ProcessingStatus(BaseModel):
    """Processing status model"""
    document_id: int
    status: str
    progress: Optional[float] = Field(None, ge=0.0, le=1.0, description="Processing progress (0-1)")
    message: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None