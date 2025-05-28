from sqlalchemy.orm import Session
from .models import Document, VideoFrame
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

def create_video_frame(db: Session, document_id: int, frame_index: int, image_data: str):
    frame = VideoFrame(document_id=document_id, frame_index=frame_index, image_data=image_data)
    db.add(frame)
    db.commit()
    db.refresh(frame)
    return frame 