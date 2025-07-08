"""
EXPLAINIUM Knowledge Schemas

Pydantic models for knowledge extraction and management.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class EntityBase(BaseModel):
    """Base entity model"""
    text: str = Field(..., description="The entity text")
    label: str = Field(..., description="Entity type/label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")

class EntityCreate(EntityBase):
    """Entity creation model"""
    document_id: int = Field(..., description="Associated document ID")
    start_position: Optional[int] = Field(None, description="Start position in text")
    end_position: Optional[int] = Field(None, description="End position in text")
    context: Optional[str] = Field(None, description="Surrounding context")

class EntityOut(EntityBase):
    """Entity output model"""
    id: int
    document_id: int
    start_position: Optional[int] = None
    end_position: Optional[int] = None
    context: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class RelationshipBase(BaseModel):
    """Base relationship model"""
    relationship_type: str = Field(..., description="Type of relationship")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")

class RelationshipCreate(RelationshipBase):
    """Relationship creation model"""
    source_entity_id: int = Field(..., description="Source entity ID")
    target_entity_id: int = Field(..., description="Target entity ID")
    context: Optional[str] = Field(None, description="Context where relationship was found")

class RelationshipOut(RelationshipBase):
    """Relationship output model"""
    id: int
    source_entity_id: int
    target_entity_id: int
    source_entity: Optional[EntityOut] = None
    target_entity: Optional[EntityOut] = None
    context: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ContentCategoryBase(BaseModel):
    """Base content category model"""
    category: str = Field(..., description="Content category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")

class ContentCategoryCreate(ContentCategoryBase):
    """Content category creation model"""
    document_id: int = Field(..., description="Associated document ID")
    keywords: Optional[List[str]] = Field(None, description="Keywords that led to classification")

class ContentCategoryOut(ContentCategoryBase):
    """Content category output model"""
    id: int
    document_id: int
    keywords: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class KeyPhraseBase(BaseModel):
    """Base key phrase model"""
    phrase: str = Field(..., description="Extracted key phrase")
    score: float = Field(..., ge=0.0, description="Importance score")

class KeyPhraseCreate(KeyPhraseBase):
    """Key phrase creation model"""
    document_id: int = Field(..., description="Associated document ID")

class KeyPhraseOut(KeyPhraseBase):
    """Key phrase output model"""
    id: int
    document_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentStructureBase(BaseModel):
    """Base document structure model"""
    structure_type: str = Field(..., description="Type of structure (section, list, table)")
    content: str = Field(..., description="Structure content")
    line_number: Optional[int] = Field(None, description="Line number in document")

class DocumentStructureCreate(DocumentStructureBase):
    """Document structure creation model"""
    document_id: int = Field(..., description="Associated document ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional structure metadata")

class DocumentStructureOut(DocumentStructureBase):
    """Document structure output model"""
    id: int
    document_id: int
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., description="Search query")
    limit: Optional[int] = Field(10, ge=1, le=100, description="Maximum number of results")
    filters: Optional[Dict[str, Any]] = Field(None, description="Search filters")
    include_entities: Optional[bool] = Field(True, description="Include entity matches")
    include_relationships: Optional[bool] = Field(False, description="Include relationship matches")
    min_confidence: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")

class SearchResult(BaseModel):
    """Individual search result"""
    document_id: int
    document_filename: str
    match_type: str = Field(..., description="Type of match (content, entity, relationship)")
    match_text: str = Field(..., description="Matching text")
    confidence: float = Field(..., description="Match confidence")
    context: Optional[str] = Field(None, description="Surrounding context")

class SearchResponse(BaseModel):
    """Search response model"""
    query: str
    total_results: int
    results: List[SearchResult]
    execution_time_ms: float

class KnowledgeGraphNode(BaseModel):
    """Knowledge graph node model"""
    id: str
    label: str
    type: str
    properties: Dict[str, Any]

class KnowledgeGraphEdge(BaseModel):
    """Knowledge graph edge model"""
    source: str
    target: str
    relationship: str
    confidence: float
    properties: Optional[Dict[str, Any]] = None

class KnowledgeGraphResponse(BaseModel):
    """Knowledge graph response model"""
    nodes: List[KnowledgeGraphNode]
    edges: List[KnowledgeGraphEdge]
    center_node: Optional[str] = None

class DocumentAnalysisRequest(BaseModel):
    """Document analysis request model"""
    extract_entities: Optional[bool] = Field(True, description="Extract named entities")
    extract_relationships: Optional[bool] = Field(True, description="Extract relationships")
    classify_content: Optional[bool] = Field(True, description="Classify content")
    extract_key_phrases: Optional[bool] = Field(True, description="Extract key phrases")
    analyze_structure: Optional[bool] = Field(True, description="Analyze document structure")
    confidence_threshold: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")

class DocumentAnalysisResponse(BaseModel):
    """Document analysis response model"""
    document_id: int
    entities: Optional[List[EntityOut]] = None
    relationships: Optional[List[RelationshipOut]] = None
    categories: Optional[List[ContentCategoryOut]] = None
    key_phrases: Optional[List[KeyPhraseOut]] = None
    structure: Optional[List[DocumentStructureOut]] = None
    processing_time_ms: float
    status: str = Field(..., description="Analysis status")

class KnowledgeExtractionStats(BaseModel):
    """Knowledge extraction statistics"""
    total_documents: int
    total_entities: int
    total_relationships: int
    total_categories: int
    entity_types: Dict[str, int]
    relationship_types: Dict[str, int]
    category_distribution: Dict[str, int]
    average_confidence: float

class BatchProcessingRequest(BaseModel):
    """Batch processing request model"""
    document_ids: List[int] = Field(..., description="List of document IDs to process")
    analysis_options: DocumentAnalysisRequest = Field(..., description="Analysis options")
    priority: Optional[str] = Field("normal", description="Processing priority")

class BatchProcessingResponse(BaseModel):
    """Batch processing response model"""
    batch_id: str
    total_documents: int
    status: str
    estimated_completion_time: Optional[datetime] = None
    created_at: datetime

class VideoFrameBase(BaseModel):
    """Base video frame model"""
    frame_number: int = Field(..., description="Frame number in the video")
    content: str = Field(..., description="Extracted text content from the frame")

class VideoFrameCreate(VideoFrameBase):
    """Video frame creation model"""
    document_id: int = Field(..., description="Associated document ID")

class VideoFrameOut(VideoFrameBase):
    """Video frame output model"""
    id: int
    document_id: int

    class Config:
        from_attributes = True
