from sqlalchemy.orm import Session
from .models import Document
from app.schemas.document import DocumentCreate

def create_document(db: Session, doc: DocumentCreate, status: str = 'pending'):
    db_doc = Document(
        filename=doc.filename,
        filetype=doc.filetype,
        content=doc.content,
        status=status
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def get_document(db: Session, doc_id: int):
    return db.query(Document).filter(Document.id == doc_id).first() 