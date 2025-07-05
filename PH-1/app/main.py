"""
EXPLAINIUM PH-1 - Smart Knowledge Extraction System
Main FastAPI application for document processing and knowledge extraction
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from PIL import Image
import pytesseract
import io
import time
import logging

# Import application modules
from app.ingestion.router import detect_file_type, validate_file_strict
from app.extraction.text import extract_text_pdf, extract_text_docx, extract_text_txt
from app.extraction.knowledge import extract_entities, extract_relationships, classify_content
from app.db.session import SessionLocal, get_db_info
from app.db.crud import (
    create_document, get_document, get_documents, create_entity, create_relationship,
    create_category, get_entities_by_document, get_categories_by_document,
    get_knowledge_stats, search_entities
)
from app.schemas.document import DocumentCreate, DocumentOut, DocumentSummary
from app.schemas.knowledge import (
    EntityOut, RelationshipOut, ContentCategoryOut, EntityCreate, 
    ContentCategoryCreate, SearchRequest, SearchResponse, KnowledgeExtractionStats
)

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        for entity in entities:
            entity_create = EntityCreate(
                document_id=db_doc.id,
                text=entity.text,
                label=entity.label,
                confidence=entity.confidence,
                start_position=entity.start,
                end_position=entity.end
            )
            create_entity(db, entity_create)
        
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

@app.post("/api/v1/knowledge/search", response_model=List[EntityOut])
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

@app.post("/upload-ui", response_class=HTMLResponse)
async def upload_ui(
    request: Request,
    file: UploadFile = File(...),
    upload_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle file uploads from the web interface"""
    result = {"type": upload_type, "filename": file.filename}
    
    try:
        if upload_type == "document":
            db_doc, entities, categories = process_document_content(file, db)
            result.update({
                "content": db_doc.content,
                "entities_extracted": len(entities),
                "categories_identified": len(categories),
                "doc_id": db_doc.id
            })
        elif upload_type == "image":
            image_bytes = await file.read()
            image = Image.open(io.BytesIO(image_bytes))

            # Perform OCR
            ocr_text = pytesseract.image_to_string(image)
            
            result["ocr_text"] = ocr_text

        elif upload_type == "video":
            from app.extraction.video import extract_video_keyframes, extract_text_from_video_frames, get_video_text_summary
            
            # Extract video frames
            frames_data = extract_video_keyframes(file, frame_interval=60, max_frames=10)
            
            # Extract text from frames
            text_data = extract_text_from_video_frames(frames_data)
            summary = get_video_text_summary(text_data)
            
            result.update({
                "frames_extracted": len(frames_data),
                "frames_with_text": summary.get("frames_with_text", 0),
                "total_text_extracted": summary.get("combined_text_length", 0),
                "text_summary": summary.get("combined_text", "")[:500] + "..." if len(summary.get("combined_text", "")) > 500 else summary.get("combined_text", ""),
                "extraction_success": summary.get("extraction_success", False)
            })
    except Exception as e:
        logger.error(f"Upload processing failed: {e}")
        result["error"] = f"Upload processing failed: {str(e)}"
    
    return templates.TemplateResponse("index.html", {"request": request, "result": result})

@app.get("/info", response_class=HTMLResponse)
def api_info(request: Request):
    """Return information about the EXPLAINIUM system"""
    return templates.TemplateResponse("info.html", {"request": request})


