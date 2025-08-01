"""
EXPLAINIUM PH-1 - Smart Knowledge Extraction System
Main FastAPI application for document processing and knowledge extraction
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

# Import application modules
from app.ingestion.router import validate_file_strict
from app.extraction.text import extract_text_pdf, extract_text_docx, extract_text_txt
from app.extraction.knowledge import extract_entities, extract_relationships, classify_content
from app.db.session import SessionLocal, get_db_info
from app.db.crud import (
    create_document, get_document, get_documents, create_entity, create_relationship,
    create_category, get_entities_by_document, get_categories_by_document,
    get_knowledge_stats, search_entities, create_video_frame, get_video_frames_by_document
)
from app.schemas.document import DocumentCreate, DocumentOut, DocumentSummary
from app.schemas.knowledge import (
    EntityOut, RelationshipOut, ContentCategoryOut, EntityCreate, 
    ContentCategoryCreate, KnowledgeExtractionStats,
    VideoFrameCreate, VideoFrameOut, RelationshipCreate
)
from app.middleware import exception_handler
from app.utils.helpers import detect_file_type

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Initialize FastAPI application
app = FastAPI(
    title="EXPLAINIUM PH-1",
    description="Smart Knowledge Extraction System for industrial document processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.middleware("http")(exception_handler)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "EXPLAINIUM Knowledge Extraction"}

@app.get("/db-info")
def database_info():
    """Get information about the current database configuration"""
    return get_db_info()

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def process_document_content(file: UploadFile, db: Session):
    """Helper function to process document content and extract knowledge"""
    # Validate file
    validate_file_strict(file)
    
    filetype = detect_file_type(file.filename)
    if filetype not in ['pdf', 'docx', 'txt']:
        raise HTTPException(status_code=400, detail="Unsupported document type for knowledge extraction.")
    
    file.file.seek(0)
    
    # Extract content based on file type
    if filetype == 'pdf':
        content = extract_text_pdf(file)
    elif filetype == 'docx':
        content = extract_text_docx(file)
    elif filetype == 'txt':
        content = extract_text_txt(file)
    else:
        content = None
    
    if not content or len(content.strip()) < 10:
        raise HTTPException(status_code=400, detail="No extractable content found in document.")
    
    # Create document record
    doc_in = DocumentCreate(
        filename=file.filename, 
        filetype=filetype, 
        content=content,
        metadata={"content_length": len(content)}
    )
    db_doc = create_document(db, doc_in, status='processing')
    
    # Perform knowledge extraction
    try:
        # Extract entities
        entities = extract_entities(content)
        db_entities = []
        for entity in entities:
            entity_create = EntityCreate(
                document_id=db_doc.id,
                text=entity.text,
                label=entity.label,
                confidence=entity.confidence,
                start_position=entity.start,
                end_position=entity.end
            )
            db_entities.append(create_entity(db, entity_create))
        
        # Extract relationships
        relationships = extract_relationships(content, entities)
        for rel in relationships:
            source_entity = next((e for e in db_entities if e.text == rel.source_entity), None)
            target_entity = next((e for e in db_entities if e.text == rel.target_entity), None)
            if source_entity and target_entity:
                rel_create = RelationshipCreate(
                    source_entity_id=source_entity.id,
                    target_entity_id=target_entity.id,
                    relationship_type=rel.relationship_type,
                    confidence=rel.confidence,
                    context=rel.context
                )
                create_relationship(db, rel_create)

        # Classify content
        categories = classify_content(content)
        for category in categories:
            category_create = ContentCategoryCreate(
                document_id=db_doc.id,
                category=category.category,
                confidence=category.confidence,
                keywords=category.keywords
            )
            create_category(db, category_create)
        
        # Update document status
        db_doc.status = 'completed'
        db.commit()
        
        logger.info(f"Successfully processed document {db_doc.id}: {len(entities)} entities, {len(categories)} categories")
        return db_doc, entities, categories
        
    except Exception as e:
        logger.error(f"Knowledge extraction failed for document {db_doc.id}: {e}")
        db_doc.status = 'failed'
        db.commit()
        raise HTTPException(status_code=500, detail=f"Knowledge extraction failed: {str(e)}")

# API Endpoints
@app.post("/api/v1/images/upload", response_model=DocumentOut)
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process image"""
    validate_file_strict(file)
    filetype = detect_file_type(file.filename)
    if filetype != 'image':
        raise HTTPException(status_code=400, detail="Only image files are supported.")

    from app.extraction.image import extract_text_from_image, get_image_metadata, detect_image_quality
    try:
        content = extract_text_from_image(file)
        metadata = get_image_metadata(file)
        quality = detect_image_quality(file)
    except Exception as e:
        logger.error(f"Image processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

    doc_in = DocumentCreate(
        filename=file.filename,
        filetype=filetype,
        content=content,
        metadata={"content_length": len(content) if content else 0, "image_metadata": metadata, "image_quality": quality}
    )
    db_doc = create_document(db, doc_in, status='completed')
    # Return extra OCR text for test script compatibility
    return {**db_doc.__dict__, "ocr_text": content or ""}

@app.post("/api/v1/videos/upload", response_model=DocumentOut)
async def upload_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process video"""
    validate_file_strict(file)
    filetype = detect_file_type(file.filename)
    if filetype != 'video':
        raise HTTPException(status_code=400, detail="Only video files are supported.")

    from app.extraction.video import extract_video_keyframes, extract_text_from_video_frames
    try:
        frames_data = extract_video_keyframes(file, frame_interval=60, max_frames=10)
        text_data = extract_text_from_video_frames(frames_data)
        frames_extracted = len(frames_data)
        preview_frames = [f["frame_number"] for f in frames_data]
        combined_text = " ".join([f.get("text_extracted", "") for f in text_data if f.get("has_text")])
    except Exception as e:
        logger.error(f"Video processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")

    doc_in = DocumentCreate(
        filename=file.filename,
        filetype=filetype,
        content=combined_text,
        metadata={"frames_extracted": frames_extracted, "preview_frames": preview_frames}
    )
    db_doc = create_document(db, doc_in, status='completed')
    # Return extra fields for test script compatibility
    return {**db_doc.__dict__, "frames_extracted": frames_extracted, "preview_frames": preview_frames}

# Document processing endpoints
@app.post("/api/v1/documents/upload", response_model=DocumentOut)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process documents with smart knowledge extraction"""
    try:
        db_doc, entities, categories = process_document_content(file, db)
        return db_doc
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@app.get("/api/v1/documents/{doc_id}", response_model=DocumentOut)
def get_document_details(doc_id: int, db: Session = Depends(get_db)):
    """Get document details by ID"""
    document = get_document(db, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@app.get("/api/v1/documents/{doc_id}/content", response_model=str)
def get_document_content(doc_id: int, db: Session = Depends(get_db)):
    """Get extracted content of a document"""
    document = get_document(db, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document.content

@app.get("/api/v1/documents", response_model=List[DocumentSummary])
def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    filetype: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List documents with optional filtering"""
    documents = get_documents(db, skip=skip, limit=limit, filetype=filetype, status=status)
    
    summaries = []
    for doc in documents:
        entity_count = len(get_entities_by_document(db, doc.id))
        category_count = len(get_categories_by_document(db, doc.id))
        
        summary = DocumentSummary(
            id=doc.id,
            filename=doc.filename,
            filetype=doc.filetype,
            status=doc.status,
            content_length=len(doc.content) if doc.content else 0,
            entity_count=entity_count,
            relationship_count=0,
            created_at=doc.created_at
        )
        summaries.append(summary)
    
    return summaries

@app.get("/api/v1/documents/{doc_id}/entities", response_model=List[EntityOut])
def get_document_entities(doc_id: int, db: Session = Depends(get_db)):
    """Get all entities extracted from a document"""
    document = get_document(db, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    entities = get_entities_by_document(db, doc_id)
    return entities

@app.get("/api/v1/documents/{doc_id}/categories", response_model=List[ContentCategoryOut])
def get_document_categories(doc_id: int, db: Session = Depends(get_db)):
    """Get all content categories for a document"""
    document = get_document(db, doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    categories = get_categories_by_document(db, doc_id)
    return categories

@app.get("/api/v1/videos/{doc_id}/frames", response_model=List[VideoFrameOut])
def get_video_frames(doc_id: int, db: Session = Depends(get_db)):
    """Get video frame analysis"""
    document = get_document(db, doc_id)
    if not document or document.filetype != 'video':
        raise HTTPException(status_code=404, detail="Video document not found")
    
    frames = get_video_frames_by_document(db, doc_id)
    return frames

@app.get("/api/v1/knowledge/stats", response_model=KnowledgeExtractionStats)
def get_extraction_stats(db: Session = Depends(get_db)):
    """Get knowledge extraction statistics"""
    stats = get_knowledge_stats(db)
    
    return KnowledgeExtractionStats(
        total_documents=stats["total_documents"],
        total_entities=stats["total_entities"],
        total_relationships=stats["total_relationships"],
        total_categories=stats["total_categories"],
        entity_types=stats["entity_types"],
        relationship_types=stats["relationship_types"],
        category_distribution=stats["category_distribution"],
        average_confidence=stats["average_confidence"]["entities"]
    )

@app.post("/api/v1/search/entities", response_model=List[EntityOut])
def search_knowledge(
    query: str = Query(..., min_length=2),
    entity_types: Optional[List[str]] = Query(None),
    min_confidence: float = Query(0.5, ge=0.0, le=1.0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Search for entities in the knowledge base"""
    entities = search_entities(
        db, 
        query=query, 
        entity_types=entity_types,
        min_confidence=min_confidence,
        limit=limit
    )
    return entities



@app.get("/info", response_class=HTMLResponse)
def api_info(request: Request):
    """Return information about the EXPLAINIUM system"""
    return templates.TemplateResponse("info.html", {"request": request})


