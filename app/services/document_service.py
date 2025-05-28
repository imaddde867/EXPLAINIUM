import os
import shutil
from typing import Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentCreate, DocumentUpdate
import uuid

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    def create_document(self, file: UploadFile) -> Document:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create document record
        doc_create = DocumentCreate(
            original_filename=file.filename,
            file_type=file.content_type,
            file_size=os.path.getsize(file_path)
        )

        db_document = Document(
            **doc_create.model_dump(),
            filename=unique_filename
        )
        
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        return db_document

    def get_document(self, document_id: int) -> Optional[Document]:
        return self.db.query(Document).filter(Document.id == document_id).first()

    def update_document(self, document_id: int, update_data: DocumentUpdate) -> Optional[Document]:
        document = self.get_document(document_id)
        if document:
            for field, value in update_data.model_dump(exclude_unset=True).items():
                setattr(document, field, value)
            self.db.commit()
            self.db.refresh(document)
        return document

    def delete_document(self, document_id: int) -> bool:
        document = self.get_document(document_id)
        if document:
            # Delete file
            file_path = os.path.join(self.upload_dir, document.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete database record
            self.db.delete(document)
            self.db.commit()
            return True
        return False

    def get_document_file_path(self, document_id: int) -> Optional[str]:
        document = self.get_document(document_id)
        if document:
            return os.path.join(self.upload_dir, document.filename)
        return None 