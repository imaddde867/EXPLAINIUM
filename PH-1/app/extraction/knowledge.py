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
    
    # Define entity patterns with their labels
    entity_patterns = {
        "EQUIPMENT": [
            r'\b(?:pump|motor|valve|sensor|conveyor|robot|machine|equipment)\s*(?:#?\d+|[A-Z]\d+)?\b',
            r'\b[A-Z]{2,4}-\d{2,6}\b',
            r'\b(?:Model|Part|Serial)\s*(?:No\.?|Number)?\s*:?\s*([A-Z0-9-]+)\b'
        ],
        "SAFETY": [
            r'\b(?:PPE|personal protective equipment|safety glasses|hard hat|gloves|respirator)\b',
            r'\b(?:hazard|danger|warning|caution|risk)\b',
            r'\b(?:OSHA|safety procedure|lockout|tagout|LOTO)\b'
        ],
        "PROCESS": [
            r'\b(?:temperature|pressure|flow rate|speed|RPM|PSI|°F|°C)\b',
            r'\b\d+\s*(?:PSI|RPM|°F|°C|GPM|CFM|Hz)\b',
            r'\b(?:start|stop|pause|resume|emergency stop|e-stop)\b'
        ],
        "PERSON": [
            r'\b(?:operator|technician|engineer|supervisor|manager|worker)\b',
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'  # Names
        ]
    }
    
    for label, patterns in entity_patterns.items():
        confidence = 0.9 if label == "SAFETY" else 0.8
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(Entity(
                    text=match.group(),
                    label=label,
                    start=match.start(),
                    end=match.end(),
                    confidence=confidence
                ))
    
    return entities

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
