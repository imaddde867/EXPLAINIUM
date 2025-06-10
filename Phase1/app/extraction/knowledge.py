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
    """
    Extract named entities from text using rule-based and pattern matching approaches.
    
    In a full implementation, this would use spaCy or similar NLP libraries.
    For now, we use pattern matching for common industrial entities.
    """
    entities = []
    
    # Equipment patterns
    equipment_patterns = [
        r'\b(?:pump|motor|valve|sensor|conveyor|robot|machine|equipment)\s*(?:#?\d+|[A-Z]\d+)?\b',
        r'\b[A-Z]{2,4}-\d{2,6}\b',  # Equipment codes like PMP-001, VLV-123
        r'\b(?:Model|Part|Serial)\s*(?:No\.?|Number)?\s*:?\s*([A-Z0-9-]+)\b'
    ]
    
    for pattern in equipment_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            entities.append(Entity(
                text=match.group(),
                label="EQUIPMENT",
                start=match.start(),
                end=match.end(),
                confidence=0.8
            ))
    
    # Safety-related entities
    safety_patterns = [
        r'\b(?:PPE|personal protective equipment|safety glasses|hard hat|gloves|respirator)\b',
        r'\b(?:hazard|danger|warning|caution|risk)\b',
        r'\b(?:OSHA|safety procedure|lockout|tagout|LOTO)\b'
    ]
    
    for pattern in safety_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            entities.append(Entity(
                text=match.group(),
                label="SAFETY",
                start=match.start(),
                end=match.end(),
                confidence=0.9
            ))
    
    # Process-related entities
    process_patterns = [
        r'\b(?:temperature|pressure|flow rate|speed|RPM|PSI|°F|°C)\b',
        r'\b\d+\s*(?:PSI|RPM|°F|°C|GPM|CFM|Hz)\b',
        r'\b(?:start|stop|pause|resume|emergency stop|e-stop)\b'
    ]
    
    for pattern in process_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            entities.append(Entity(
                text=match.group(),
                label="PROCESS",
                start=match.start(),
                end=match.end(),
                confidence=0.7
            ))
    
    # Personnel and roles
    personnel_patterns = [
        r'\b(?:operator|technician|supervisor|manager|engineer|maintenance)\b',
        r'\b(?:shift|team|crew|department)\s*(?:lead|leader|supervisor)?\b'
    ]
    
    for pattern in personnel_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            entities.append(Entity(
                text=match.group(),
                label="PERSONNEL",
                start=match.start(),
                end=match.end(),
                confidence=0.8
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
    """
    Extract key phrases from text using simple frequency and pattern analysis.
    """
    # Simple key phrase extraction using noun phrases and important terms
    phrases = []
    
    # Pattern for potential key phrases (noun phrases, technical terms)
    phrase_patterns = [
        r'\b(?:[A-Z][a-z]+\s+){1,3}[A-Z][a-z]+\b',  # Capitalized phrases
        r'\b\d+\s*(?:PSI|RPM|°F|°C|GPM|CFM|Hz|mm|cm|inch|ft)\b',  # Technical measurements
        r'\b[A-Z]{2,}-\d+\b',  # Technical codes
        r'\b(?:step|procedure|process|method|technique)\s+\d+\b'  # Procedural references
    ]
    
    for pattern in phrase_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Simple scoring based on length and capitalization
            score = len(match.split()) * 0.3 + (1.0 if match[0].isupper() else 0.5)
            phrases.append((match, score))
    
    # Remove duplicates and sort by score
    unique_phrases = list(set(phrases))
    unique_phrases.sort(key=lambda x: x[1], reverse=True)
    
    return unique_phrases[:max_phrases]

def analyze_document_structure(text: str) -> Dict[str, any]:
    """
    Analyze the structure of a document to identify sections, lists, and formatting.
    """
    structure = {
        "sections": [],
        "lists": [],
        "tables": [],
        "references": []
    }
    
    lines = text.split('\n')
    
    # Identify sections (lines that look like headers)
    for i, line in enumerate(lines):
        line = line.strip()
        if line and (line.isupper() or re.match(r'^\d+\.?\s+[A-Z]', line)):
            structure["sections"].append({
                "title": line,
                "line_number": i + 1
            })
    
    # Identify lists (lines starting with bullets or numbers)
    list_patterns = [
        r'^\s*[-•*]\s+',  # Bullet points
        r'^\s*\d+\.?\s+',  # Numbered lists
        r'^\s*[a-zA-Z]\.?\s+'  # Lettered lists
    ]
    
    for i, line in enumerate(lines):
        for pattern in list_patterns:
            if re.match(pattern, line):
                structure["lists"].append({
                    "content": line.strip(),
                    "line_number": i + 1,
                    "type": "bullet" if pattern.startswith(r'^\s*[-•*]') else "numbered"
                })
                break
    
    # Identify potential table content (lines with multiple columns)
    for i, line in enumerate(lines):
        if '\t' in line or '|' in line or len(re.findall(r'\s{3,}', line)) > 1:
            structure["tables"].append({
                "content": line.strip(),
                "line_number": i + 1
            })
    
    return structure
