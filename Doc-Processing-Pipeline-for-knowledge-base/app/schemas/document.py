from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    filename: str
    filetype: str
    status: str
    content: Optional[str] = None
    created_at: Optional[datetime] = None

class DocumentCreate(BaseModel):
    filename: str
    filetype: str
    content: Optional[str] = None

class DocumentOut(DocumentBase):
    id: int
    class Config:
        orm_mode = True 