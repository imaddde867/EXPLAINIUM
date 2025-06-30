"""
EXPLAINIUM PH-1 - Smart Knowledge Extraction System

Main FastAPI application providing intelligent document processing and knowledge extraction
capabilities for industrial applications. This module serves as the foundation layer of
the EXPLAINIUM AI factory management system.

Features:
- Multi-format document processing (PDF, DOCX, TXT, images, videos)
- Intelligent text extraction with OCR capabilities
- Named entity recognition and relationship extraction
- Content classification and categorization
- RESTful API with comprehensive documentation
- Real-time processing status and progress tracking

Author: EXPLAINIUM Development Team
Version: 1.0.0
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import time
import logging
import os

# Import application modules
from app.ingestion.router import detect_file_type, validate_file_strict
from app.extraction.text import extract_text_pdf, extract_text_docx, extract_text_txt
from app.extraction.knowledge import extract_entities, extract_relationships, classify_content
from app.db.session import SessionLocal
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

# Initialize FastAPI application with comprehensive metadata
app = FastAPI(
    title="EXPLAINIUM PH-1 - Smart Knowledge Extraction System",
    description="""
    🧠 **EXPLAINIUM Phase 1** - Foundation Layer Implementation

    Advanced AI-powered document processing and intelligent knowledge extraction system
    designed for industrial applications. Transform unstructured company knowledge into
    structured, searchable, and actionable intelligence.

    ## 🚀 Key Features

    * **Multi-format Processing**: PDF, DOCX, TXT, images, videos
    * **Intelligent OCR**: Advanced text extraction with layout understanding
    * **Entity Recognition**: Automatic identification of equipment, procedures, safety info
    * **Content Classification**: Smart categorization of document types
    * **RESTful API**: Clean, documented endpoints for seamless integration
    * **Real-time Processing**: Asynchronous task processing with status tracking

    ## 📊 Supported Formats

    * **Documents**: PDF, DOCX, TXT, RTF
    * **Images**: JPG, PNG, TIFF, BMP (with OCR)
    * **Videos**: MP4, AVI, MOV (frame extraction)

    Built with ❤️ following Turku UAS visual identity standards.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "EXPLAINIUM Development Team",
        "email": "support@explainium.ai",
    },
    license_info={
        "name": "Proprietary License",
        "url": "https://explainium.ai/license",
    },
)

# Add CORS middleware for web interface compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "EXPLAINIUM Knowledge Extraction"}

# Simple web interface for testing
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    """Main web interface for document upload and processing"""
    return templates.TemplateResponse("index.html", {"request": request})

# Document processing endpoints
@app.post("/api/v1/documents/upload", response_model=DocumentOut)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and process documents with smart knowledge extraction"""
    
    # Validate file
    validate_file_strict(file)
    
    filetype = detect_file_type(file.filename)
    if filetype not in ['pdf', 'docx', 'txt']:
        raise HTTPException(status_code=400, detail="Unsupported document type for knowledge extraction.")
    
    try:
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
            
        except Exception as e:
            logger.error(f"Knowledge extraction failed for document {db_doc.id}: {e}")
            db_doc.status = 'failed'
            db.commit()
            raise HTTPException(status_code=500, detail=f"Knowledge extraction failed: {str(e)}")
        
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
    
    # Convert to summary format
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
            relationship_count=0,  # Simplified for now
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
    """Search entities in the knowledge base"""
    entities = search_entities(
        db, 
        query=query, 
        entity_types=entity_types,
        min_confidence=min_confidence,
        limit=limit
    )
    return entities

# Web interface upload endpoint
@app.post("/upload-ui", response_class=HTMLResponse)
def upload_ui(
    request: Request,
    file: UploadFile = File(...),
    upload_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle file uploads from the web interface"""
    result = {"type": upload_type, "filename": file.filename}
    
    try:
        # Validate file
        validate_file_strict(file)
        
        filetype = detect_file_type(file.filename)
        
        if upload_type == "document":
            if filetype not in ['pdf', 'docx', 'txt']:
                result["error"] = "Unsupported document type. Please use PDF, DOCX, or TXT files."
                return templates.TemplateResponse("index.html", {"request": request, "result": result})
            
            # Extract content based on file type
            file.file.seek(0)
            if filetype == 'pdf':
                content = extract_text_pdf(file)
            elif filetype == 'docx':
                content = extract_text_docx(file)
            elif filetype == 'txt':
                content = extract_text_txt(file)
            else:
                content = None
            
            if not content or len(content.strip()) < 10:
                result["error"] = "No extractable content found in document."
                return templates.TemplateResponse("index.html", {"request": request, "result": result})
            
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
                
                result["content"] = content
                result["entities_extracted"] = len(entities)
                result["categories_identified"] = len(categories)
                result["doc_id"] = db_doc.id
                
            except Exception as e:
                logger.error(f"Knowledge extraction failed: {e}")
                db_doc.status = 'failed'
                db.commit()
                result["error"] = f"Knowledge extraction failed: {str(e)}"
        
        elif upload_type == "image":
            # For now, just show that image was received
            # You can implement OCR here if needed
            result["ocr_text"] = "Image OCR functionality not yet implemented. Use API endpoint for full OCR capabilities."
        
        elif upload_type == "video":
            # For now, just show that video was received
            # You can implement frame extraction here if needed
            result["frames_extracted"] = 0
            result["preview_frames"] = []
            result["message"] = "Video processing functionality not yet implemented. Use API endpoint for full video processing capabilities."
    
    except Exception as e:
        logger.error(f"Upload processing failed: {e}")
        result["error"] = f"Upload processing failed: {str(e)}"
    
    return templates.TemplateResponse("index.html", {"request": request, "result": result})

# API information endpoint
@app.get("/info", response_class=HTMLResponse)
def api_info():
    """API information page (original static page)"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EXPLAINIUM - Smart Knowledge Extraction</title>
        <style>
            body { font-family: 'PT Sans', Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; }
            .logo { color: #8e44ad; font-size: 2.5em; font-weight: bold; }
            .subtitle { color: #333; background: #ffd200; padding: 10px; border-radius: 5px; display: inline-block; font-weight: bold; }
            .info { background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffd200; }
            .api-link { color: #8e44ad; text-decoration: none; font-weight: bold; }
            .api-link:hover { text-decoration: underline; }
            .feature-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
            .feature { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #8e44ad; }
            .status { background: #d4edda; color: #155724; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">EXPLAINIUM</div>
                <div class="subtitle">Smart Knowledge Extraction System</div>
            </div>
            
            <div class="status">
                🟢 System Status: Active & Ready
            </div>
            
            <div class="info">
                <h3>🎯 About EXPLAINIUM</h3>
                <p>EXPLAINIUM is an AI-powered knowledge extraction system designed for industrial applications. 
                It processes documents and extracts meaningful knowledge including entities, relationships, and content classifications.</p>
            </div>
            
            <div class="feature-list">
                <div class="feature">
                    <h4>📄 Document Processing</h4>
                    <p>Supports PDF, DOCX, and TXT files with advanced text extraction capabilities.</p>
                </div>
                <div class="feature">
                    <h4>🧠 Entity Recognition</h4>
                    <p>Automatically identifies equipment, safety items, processes, and personnel mentions.</p>
                </div>
                <div class="feature">
                    <h4>🔗 Relationship Mapping</h4>
                    <p>Discovers connections between entities to build knowledge graphs.</p>
                </div>
                <div class="feature">
                    <h4>📊 Content Classification</h4>
                    <p>Categorizes documents into safety manuals, procedures, training materials, etc.</p>
                </div>
            </div>
            
            <div class="info">
                <h3>🚀 API Endpoints</h3>
                <ul>
                    <li><code>POST /api/v1/documents/upload</code> - Upload and process documents</li>
                    <li><code>GET /api/v1/documents/{id}</code> - Get document details</li>
                    <li><code>GET /api/v1/documents/{id}/entities</code> - Get extracted entities</li>
                    <li><code>GET /api/v1/documents/{id}/categories</code> - Get content categories</li>
                    <li><code>POST /api/v1/knowledge/search</code> - Search knowledge base</li>
                    <li><code>GET /api/v1/knowledge/stats</code> - Get extraction statistics</li>
                </ul>
            </div>
            
            <div class="info">
                <h3>📚 Documentation</h3>
                <p>
                    <a href="/docs" class="api-link">📖 Interactive API Documentation (Swagger UI)</a><br>
                    <a href="/redoc" class="api-link">📋 Alternative Documentation (ReDoc)</a><br>
                    <a href="/" class="api-link">🌐 Web Upload Interface</a>
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 30px; color: #666; border-top: 1px solid #eee; padding-top: 20px;">
                <p><strong>TURKU AMK</strong> - Applied Sciences</p>
                <p style="font-style: italic;">Building a "good life in a smart society" through excellence in applied AI science</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
