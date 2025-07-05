"""
EXPLAINIUM Knowledge Extraction Module

This module provides intelligent knowledge extraction capabilities including:
- Named Entity Recognition (NER)
- Relationship extraction
- Content classification
- Semantic analysis
"""

import re
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class Entity:
    """Represents an extracted entity"""
    text: str
    label: str
    start: int
    end: int
    confidence: float

@dataclass
class Relationship:
    """Represents a relationship between entities"""
    source_entity: str
    target_entity: str
    relationship_type: str
    confidence: float
    context: str

@dataclass
class ContentCategory:
    """Represents content classification"""
    category: str
    confidence: float
    keywords: List[str]

def extract_entities(text: str) -> List[Entity]:
    """Extract named entities from text using pattern matching for common industrial entities."""
    entities = []
    
    # More precise entity patterns with word boundaries
    entity_patterns = {
        "ORGANIZATION": [
            r'\bEXPLAINIUM\b',
            r'\b(?:Turku UAS|Turku University|Nokia|Microsoft|Google|Apple|Amazon|Meta|Tesla)\b',
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|Ltd|LLC|Group|Company|Organization|University|Institute)\b'
        ],
        "TECHNOLOGY": [
            r'\bNatural Language Processing\b',
            r'\b(?:Machine Learning|Artificial Intelligence|Computer Vision|OCR)\b',
            r'\b(?:AI|ML|NLP|API|FastAPI|Python|PostgreSQL|SQLite)\b',
            r'\bPH-\d+\b'  # Model numbers like PH-1
        ],
        "LOCATION": [
            r'\b(?:Finland|Helsinki|Turku|Stockholm|Copenhagen|Oslo|London|Berlin|Paris|New York|California|Europe|Nordic)\b'
        ],
        "DATE": [
            r'\b(?:2024|2023|2025|2022)\b',
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        ],
        "EQUIPMENT": [
            r'\b(?:Model number|Version):\s*[A-Z0-9.-]+\b',
            r'\bversion\s+\d+\.\d+(?:\.\d+)?\b'
        ],
        "PROCESS": [
            r'\b(?:text extraction|knowledge extraction|document processing|compliance checking|document management)\b'
        ]
    }
    
    # Extract entities with improved confidence scoring
    for label, patterns in entity_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                matched_text = match.group().strip()
                
                # Skip very short matches or common words
                if len(matched_text) < 2:
                    continue
                    
                # Calculate confidence based on pattern specificity and context
                confidence = calculate_entity_confidence(matched_text, label, text, match.start(), match.end())
                
                # Only include entities with reasonable confidence
                if confidence >= 0.7:
                    entities.append(Entity(
                        text=matched_text,
                        label=label,
                        start=match.start(),
                        end=match.end(),
                        confidence=confidence
                    ))
    
    # Remove duplicate entities (same text and position)
    entities = remove_duplicate_entities(entities)
    
    # Filter out overlapping entities, keeping the one with higher confidence
    entities = filter_overlapping_entities(entities)
    
    return entities

def calculate_entity_confidence(text: str, label: str, full_text: str, start: int, end: int) -> float:
    """Calculate confidence score for an entity based on context and specificity"""
    base_confidence = 0.7
    
    # Boost confidence for longer, more specific entities
    if len(text) > 10:
        base_confidence += 0.1
    elif len(text) < 4:
        base_confidence -= 0.2
        
    # Boost confidence for proper nouns (capitalized)
    if text[0].isupper():
        base_confidence += 0.1
        
    # Boost confidence for specific patterns
    if label == "TECHNOLOGY" and any(keyword in text.lower() for keyword in ["processing", "learning", "intelligence", "vision"]):
        base_confidence += 0.15
    elif label == "ORGANIZATION" and any(suffix in text.lower() for suffix in ["inc", "corp", "ltd", "university", "institute"]):
        base_confidence += 0.15
    elif label == "DATE" and re.match(r'\b\d{4}\b', text):
        base_confidence += 0.1
        
    # Reduce confidence for common words
    common_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
    if text.lower() in common_words:
        base_confidence -= 0.4
        
    return max(0.0, min(1.0, base_confidence))

def remove_duplicate_entities(entities: List[Entity]) -> List[Entity]:
    """Remove duplicate entities with same text and overlapping positions"""
    unique_entities = []
    seen = set()
    
    for entity in entities:
        key = (entity.text.lower(), entity.start, entity.end)
        if key not in seen:
            seen.add(key)
            unique_entities.append(entity)
    
    return unique_entities

def filter_overlapping_entities(entities: List[Entity]) -> List[Entity]:
    """Filter out overlapping entities, keeping the one with higher confidence"""
    if not entities:
        return entities
        
    # Sort by start position
    sorted_entities = sorted(entities, key=lambda e: e.start)
    filtered = [sorted_entities[0]]
    
    for current in sorted_entities[1:]:
        last = filtered[-1]
        
        # Check if entities overlap
        if current.start < last.end:
            # Keep the entity with higher confidence
            if current.confidence > last.confidence:
                filtered[-1] = current
        else:
            filtered.append(current)
    
    return filtered

def extract_relationships(text: str, entities: List[Entity]) -> List[Relationship]:
    """
    Extract relationships between entities based on proximity and context patterns.
    """
    relationships = []
    
    # Simple proximity-based relationship extraction
    for i, entity1 in enumerate(entities):
        for j, entity2 in enumerate(entities[i+1:], i+1):
            # Check if entities are close to each other (within 50 characters)
            distance = abs(entity1.start - entity2.start)
            if distance < 50:
                # Determine relationship type based on entity labels
                rel_type = determine_relationship_type(entity1.label, entity2.label, text)
                if rel_type:
                    # Extract context around the entities
                    context_start = max(0, min(entity1.start, entity2.start) - 25)
                    context_end = min(len(text), max(entity1.end, entity2.end) + 25)
                    context = text[context_start:context_end]
                    
                    relationships.append(Relationship(
                        source_entity=entity1.text,
                        target_entity=entity2.text,
                        relationship_type=rel_type,
                        confidence=0.7,
                        context=context
                    ))
    
    return relationships

def determine_relationship_type(label1: str, label2: str, text: str) -> Optional[str]:
    """Determine the type of relationship between two entity labels"""
    
    relationship_rules = {
        ("PERSONNEL", "EQUIPMENT"): "OPERATES",
        ("PERSONNEL", "SAFETY"): "FOLLOWS",
        ("EQUIPMENT", "PROCESS"): "CONTROLS",
        ("SAFETY", "PROCESS"): "PROTECTS",
        ("EQUIPMENT", "EQUIPMENT"): "CONNECTS_TO",
        ("PERSONNEL", "PERSONNEL"): "REPORTS_TO"
    }
    
    # Check both directions
    rel_type = relationship_rules.get((label1, label2))
    if not rel_type:
        rel_type = relationship_rules.get((label2, label1))
    
    return rel_type

def classify_content(text: str) -> List[ContentCategory]:
    """
    Classify content into predefined categories based on keywords and patterns.
    """
    categories = []
    
    # Define category keywords
    category_keywords = {
        "SAFETY_MANUAL": [
            "safety", "hazard", "PPE", "OSHA", "emergency", "accident", "injury",
            "lockout", "tagout", "confined space", "chemical", "MSDS"
        ],
        "MAINTENANCE_PROCEDURE": [
            "maintenance", "repair", "service", "inspection", "lubrication",
            "replacement", "troubleshooting", "preventive", "scheduled"
        ],
        "OPERATING_INSTRUCTION": [
            "operation", "startup", "shutdown", "procedure", "step", "instruction",
            "control", "monitor", "adjust", "setting"
        ],
        "TRAINING_MATERIAL": [
            "training", "course", "lesson", "certification", "competency",
            "skill", "knowledge", "assessment", "qualification"
        ],
        "TECHNICAL_SPECIFICATION": [
            "specification", "technical", "drawing", "schematic", "blueprint",
            "dimension", "tolerance", "material", "standard"
        ]
    }
    
    text_lower = text.lower()
    
    for category, keywords in category_keywords.items():
        # Count keyword matches
        matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
        
        if matches > 0:
            # Calculate confidence based on keyword density
            confidence = min(0.95, matches / len(keywords) * 2)
            
            if confidence > 0.3:  # Minimum threshold
                categories.append(ContentCategory(
                    category=category,
                    confidence=confidence,
                    keywords=[kw for kw in keywords if kw.lower() in text_lower]
                ))
    
    # Sort by confidence
    categories.sort(key=lambda x: x.confidence, reverse=True)
    
    return categories

def extract_key_phrases(text: str, max_phrases: int = 10) -> List[Tuple[str, float]]:
    """Extract key phrases from text using simple pattern analysis."""
    phrases = []
    
    phrase_patterns = [
        r'\b(?:[A-Z][a-z]+\s+){1,3}[A-Z][a-z]+\b',  # Capitalized phrases
        r'\b\d+\s*(?:PSI|RPM|°F|°C|GPM|CFM|Hz|mm|cm|inch|ft)\b',  # Technical measurements
        r'\b[A-Z]{2,}-\d+\b',  # Technical codes
    ]
    
    for pattern in phrase_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            score = len(match.split()) * 0.3 + (1.0 if match[0].isupper() else 0.5)
            phrases.append((match, score))
    
    unique_phrases = list(set(phrases))
    unique_phrases.sort(key=lambda x: x[1], reverse=True)
    
    return unique_phrases[:max_phrases]
