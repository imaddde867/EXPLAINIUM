from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.services.document_service import DocumentService
from app.schemas.document import Document, DocumentUpdate
from app.core.config import settings

router = APIRouter()

@router.post("/upload", response_model=Document)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    document_service = DocumentService(db)
    return document_service.create_document(file)

@router.get("/{document_id}", response_model=Document)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document_service = DocumentService(db)
    document = document_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("/", response_model=List[Document])
def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    document_service = DocumentService(db)
    return document_service.db.query(Document).offset(skip).limit(limit).all()

@router.patch("/{document_id}", response_model=Document)
def update_document(
    document_id: int,
    update_data: DocumentUpdate,
    db: Session = Depends(get_db)
):
    document_service = DocumentService(db)
    document = document_service.update_document(document_id, update_data)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document_service = DocumentService(db)
    if not document_service.delete_document(document_id):
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"} 