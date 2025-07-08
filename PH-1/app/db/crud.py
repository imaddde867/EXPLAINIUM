from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from typing import List, Optional, Dict, Any
from .models import (
    Document, KnowledgeEntity, KnowledgeRelationship,
    ContentCategory, KeyPhrase, DocumentStructure, VideoFrame
)
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.schemas.knowledge import (
    EntityCreate, RelationshipCreate, ContentCategoryCreate,
    KeyPhraseCreate, DocumentStructureCreate, VideoFrameCreate
)

# Document CRUD operations
def create_document(db: Session, doc: DocumentCreate, status: str = 'pending') -> Document:
    """Create a new document"""
    db_doc = Document(
        filename=doc.filename,
        filetype=doc.filetype,
        content=doc.content,
        document_metadata=doc.metadata,
        processing_result=doc.processing_result,
        status=status
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def get_document(db: Session, doc_id: int) -> Optional[Document]:
    """Get a document by ID"""
    return db.query(Document).filter(Document.id == doc_id).first()

def get_documents(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filetype: Optional[str] = None,
    status: Optional[str] = None
) -> List[Document]:
    """Get documents with optional filtering"""
    query = db.query(Document)

    if filetype:
        query = query.filter(Document.filetype == filetype)
    if status:
        query = query.filter(Document.status == status)

    return query.offset(skip).limit(limit).all()

def update_document(db: Session, doc_id: int, doc_update: DocumentUpdate) -> Optional[Document]:
    """Update a document"""
    db_doc = db.query(Document).filter(Document.id == doc_id).first()
    if db_doc:
        update_data = doc_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_doc, field, value)
        db.commit()
        db.refresh(db_doc)
    return db_doc

def delete_document(db: Session, doc_id: int) -> bool:
    """Delete a document and all related data"""
    db_doc = db.query(Document).filter(Document.id == doc_id).first()
    if db_doc:
        db.delete(db_doc)
        db.commit()
        return True
    return False

# Knowledge Entity CRUD operations
def create_entity(db: Session, entity: EntityCreate) -> KnowledgeEntity:
    """Create a new knowledge entity"""
    db_entity = KnowledgeEntity(
        document_id=entity.document_id,
        text=entity.text,
        label=entity.label,
        confidence=entity.confidence,
        start_position=entity.start_position,
        end_position=entity.end_position,
        context=entity.context
    )
    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity

def get_entities_by_document(db: Session, doc_id: int) -> List[KnowledgeEntity]:
    """Get all entities for a document"""
    return db.query(KnowledgeEntity).filter(KnowledgeEntity.document_id == doc_id).all()

def get_entities_by_label(db: Session, label: str, limit: int = 100) -> List[KnowledgeEntity]:
    """Get entities by label type"""
    return db.query(KnowledgeEntity).filter(KnowledgeEntity.label == label).limit(limit).all()

# Knowledge Relationship CRUD operations
def create_relationship(db: Session, relationship: RelationshipCreate) -> KnowledgeRelationship:
    """Create a new knowledge relationship"""
    db_rel = KnowledgeRelationship(
        source_entity_id=relationship.source_entity_id,
        target_entity_id=relationship.target_entity_id,
        relationship_type=relationship.relationship_type,
        confidence=relationship.confidence,
        context=relationship.context
    )
    db.add(db_rel)
    db.commit()
    db.refresh(db_rel)
    return db_rel

def get_relationships_by_entity(db: Session, entity_id: int) -> List[KnowledgeRelationship]:
    """Get all relationships for an entity"""
    return db.query(KnowledgeRelationship).filter(
        or_(
            KnowledgeRelationship.source_entity_id == entity_id,
            KnowledgeRelationship.target_entity_id == entity_id
        )
    ).options(
        joinedload(KnowledgeRelationship.source_entity),
        joinedload(KnowledgeRelationship.target_entity)
    ).all()

# Content Category CRUD operations
def create_category(db: Session, category: ContentCategoryCreate) -> ContentCategory:
    """Create a new content category"""
    db_category = ContentCategory(
        document_id=category.document_id,
        category=category.category,
        confidence=category.confidence,
        keywords=category.keywords
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories_by_document(db: Session, doc_id: int) -> List[ContentCategory]:
    """Get all categories for a document"""
    return db.query(ContentCategory).filter(ContentCategory.document_id == doc_id).all()

# Key Phrase CRUD operations
def create_key_phrase(db: Session, key_phrase: KeyPhraseCreate) -> KeyPhrase:
    """Create a new key phrase"""
    db_phrase = KeyPhrase(
        document_id=key_phrase.document_id,
        phrase=key_phrase.phrase,
        score=key_phrase.score
    )
    db.add(db_phrase)
    db.commit()
    db.refresh(db_phrase)
    return db_phrase

def get_key_phrases_by_document(db: Session, doc_id: int) -> List[KeyPhrase]:
    """Get all key phrases for a document"""
    return db.query(KeyPhrase).filter(KeyPhrase.document_id == doc_id).all()

# Document Structure CRUD operations
def create_structure(db: Session, structure: DocumentStructureCreate) -> DocumentStructure:
    """Create a new document structure"""
    db_structure = DocumentStructure(
        document_id=structure.document_id,
        structure_type=structure.structure_type,
        content=structure.content,
        line_number=structure.line_number,
        metadata=structure.metadata
    )
    db.add(db_structure)
    db.commit()
    db.refresh(db_structure)
    return db_structure

def get_structures_by_document(db: Session, doc_id: int) -> List[DocumentStructure]:
    """Get all structures for a document"""
    return db.query(DocumentStructure).filter(DocumentStructure.document_id == doc_id).all()

# VideoFrame CRUD operations
def create_video_frame(db: Session, frame: VideoFrameCreate) -> VideoFrame:
    """Create a new video frame"""
    db_frame = VideoFrame(
        document_id=frame.document_id,
        frame_number=frame.frame_number,
        content=frame.content
    )
    db.add(db_frame)
    db.commit()
    db.refresh(db_frame)
    return db_frame

def get_video_frames_by_document(db: Session, doc_id: int) -> List[VideoFrame]:
    """Get all video frames for a document"""
    return db.query(VideoFrame).filter(VideoFrame.document_id == doc_id).all()

# Search and analytics functions
def search_entities(
    db: Session,
    query: str,
    entity_types: Optional[List[str]] = None,
    min_confidence: float = 0.5,
    limit: int = 100
) -> List[KnowledgeEntity]:
    """Search entities by text content"""
    db_query = db.query(KnowledgeEntity).filter(
        and_(
            KnowledgeEntity.text.ilike(f"%{query}%"),
            KnowledgeEntity.confidence >= min_confidence
        )
    )

    if entity_types:
        db_query = db_query.filter(KnowledgeEntity.label.in_(entity_types))

    return db_query.limit(limit).all()

def get_knowledge_stats(db: Session) -> Dict[str, Any]:
    """Get knowledge extraction statistics"""
    stats = {
        "total_documents": db.query(Document).count(),
        "total_entities": db.query(KnowledgeEntity).count(),
        "total_relationships": db.query(KnowledgeRelationship).count(),
        "total_categories": db.query(ContentCategory).count(),
    }

    # Entity type distribution
    entity_types = db.query(
        KnowledgeEntity.label,
        func.count(KnowledgeEntity.id)
    ).group_by(KnowledgeEntity.label).all()
    stats["entity_types"] = {label: count for label, count in entity_types}

    # Relationship type distribution
    rel_types = db.query(
        KnowledgeRelationship.relationship_type,
        func.count(KnowledgeRelationship.id)
    ).group_by(KnowledgeRelationship.relationship_type).all()
    stats["relationship_types"] = {rel_type: count for rel_type, count in rel_types}

    # Category distribution
    categories = db.query(
        ContentCategory.category,
        func.count(ContentCategory.id)
    ).group_by(ContentCategory.category).all()
    stats["category_distribution"] = {category: count for category, count in categories}

    # Average confidence scores
    avg_entity_confidence = db.query(func.avg(KnowledgeEntity.confidence)).scalar() or 0.0
    avg_rel_confidence = db.query(func.avg(KnowledgeRelationship.confidence)).scalar() or 0.0
    stats["average_confidence"] = {
        "entities": round(avg_entity_confidence, 3),
        "relationships": round(avg_rel_confidence, 3)
    }

    return stats