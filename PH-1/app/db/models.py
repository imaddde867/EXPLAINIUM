from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Document(Base):
    """Document model for storing processed documents"""
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filetype = Column(String(50), nullable=False)
    status = Column(String(50), default='pending')
    content = Column(Text)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    entities = relationship("KnowledgeEntity", back_populates="document", cascade="all, delete-orphan")
    categories = relationship("ContentCategory", back_populates="document", cascade="all, delete-orphan")
    key_phrases = relationship("KeyPhrase", back_populates="document", cascade="all, delete-orphan")
    structures = relationship("DocumentStructure", back_populates="document", cascade="all, delete-orphan")

class KnowledgeEntity(Base):
    """Entity model for storing extracted named entities"""
    __tablename__ = 'knowledge_entities'

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    text = Column(String(500), nullable=False)
    label = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    start_position = Column(Integer)
    end_position = Column(Integer)
    context = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="entities")
    source_relationships = relationship("KnowledgeRelationship", foreign_keys="KnowledgeRelationship.source_entity_id", back_populates="source_entity")
    target_relationships = relationship("KnowledgeRelationship", foreign_keys="KnowledgeRelationship.target_entity_id", back_populates="target_entity")

class KnowledgeRelationship(Base):
    """Relationship model for storing entity relationships"""
    __tablename__ = 'knowledge_relationships'

    id = Column(Integer, primary_key=True, index=True)
    source_entity_id = Column(Integer, ForeignKey('knowledge_entities.id'), nullable=False)
    target_entity_id = Column(Integer, ForeignKey('knowledge_entities.id'), nullable=False)
    relationship_type = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    context = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    source_entity = relationship("KnowledgeEntity", foreign_keys=[source_entity_id], back_populates="source_relationships")
    target_entity = relationship("KnowledgeEntity", foreign_keys=[target_entity_id], back_populates="target_relationships")

class ContentCategory(Base):
    """Content category model for document classification"""
    __tablename__ = 'content_categories'

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    category = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    keywords = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="categories")

class KeyPhrase(Base):
    """Key phrase model for storing important phrases"""
    __tablename__ = 'key_phrases'

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    phrase = Column(String(500), nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="key_phrases")

class DocumentStructure(Base):
    """Document structure model for storing structural elements"""
    __tablename__ = 'document_structures'

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'), nullable=False)
    structure_type = Column(String(50), nullable=False)  # section, list, table, etc.
    content = Column(Text, nullable=False)
    line_number = Column(Integer)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="structures")