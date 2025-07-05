"""
EXPLAINIUM Helper Functions
Common utility functions for file processing, text cleaning, and data validation
"""

import os
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename
    
    Args:
        filename: File name with extension
        
    Returns:
        File extension in lowercase (without dot)
    """
    return Path(filename).suffix.lower().lstrip('.')

def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """
    Validate if file type is allowed
    
    Args:
        filename: File name to validate
        allowed_types: List of allowed file extensions
        
    Returns:
        True if file type is allowed, False otherwise
    """
    file_ext = get_file_extension(filename)
    return file_ext in [ext.lower() for ext in allowed_types]

def clean_text(text: str, remove_extra_whitespace: bool = True, 
               remove_special_chars: bool = False) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Input text to clean
        remove_extra_whitespace: Remove extra spaces and normalize whitespace
        remove_special_chars: Remove special characters (keep only alphanumeric and basic punctuation)
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove null bytes and control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t\r')
    
    if remove_extra_whitespace:
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace from each line
        text = '\n'.join(line.strip() for line in text.split('\n'))
        # Remove excessive newlines
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    if remove_special_chars:
        # Keep only alphanumeric, basic punctuation, and whitespace
        text = re.sub(r'[^\w\s.,!?;:\-()[\]{}"\'\n\t]', '', text)
    
    return text.strip()

def calculate_confidence_score(scores: List[float], weights: Optional[List[float]] = None) -> float:
    """
    Calculate weighted confidence score
    
    Args:
        scores: List of confidence scores (0.0 to 1.0)
        weights: Optional weights for each score
        
    Returns:
        Weighted average confidence score
    """
    if not scores:
        return 0.0
    
    if weights is None:
        weights = [1.0] * len(scores)
    
    if len(scores) != len(weights):
        logger.warning("Scores and weights length mismatch, using equal weights")
        weights = [1.0] * len(scores)
    
    weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
    total_weight = sum(weights)
    
    return weighted_sum / total_weight if total_weight > 0 else 0.0

def generate_summary_stats(data: List[Dict], fields: List[str]) -> Dict:
    """
    Generate summary statistics for specified fields
    
    Args:
        data: List of dictionaries containing data
        fields: List of field names to analyze
        
    Returns:
        Dictionary with summary statistics
    """
    stats = {}
    
    for field in fields:
        values = []
        for item in data:
            if field in item and item[field] is not None:
                try:
                    if isinstance(item[field], (int, float)):
                        values.append(float(item[field]))
                    elif isinstance(item[field], str) and item[field].replace('.', '').isdigit():
                        values.append(float(item[field]))
                except (ValueError, TypeError):
                    continue
        
        if values:
            stats[field] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "total": sum(values)
            }
        else:
            stats[field] = {
                "count": 0,
                "min": None,
                "max": None,
                "mean": None,
                "total": 0
            }
    
    return stats

def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename for safe storage
    
    Args:
        filename: Original filename
        max_length: Maximum allowed filename length
        
    Returns:
        Sanitized filename
    """
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = "untitled"
    
    # Truncate if too long
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        max_name_length = max_length - len(ext)
        filename = name[:max_name_length] + ext
    
    return filename

def get_timestamp(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Get current timestamp in specified format
    
    Args:
        format_str: Datetime format string
        
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(format_str)

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string (e.g., "1h 23m 45s")
    """
    if seconds < 0:
        return "0s"
    
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)

def extract_keywords(text: str, min_length: int = 3, max_keywords: int = 20) -> List[str]:
    """
    Extract keywords from text using simple frequency analysis
    
    Args:
        text: Input text
        min_length: Minimum word length
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of extracted keywords
    """
    if not text:
        return []
    
    # Clean and normalize text
    text = clean_text(text, remove_special_chars=True).lower()
    
    # Common stop words to exclude
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'between', 'among', 'under', 'over', 'is', 'are', 'was', 'were',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i',
        'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
    }
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    
    # Filter words
    words = [word for word in words 
             if len(word) >= min_length and word.lower() not in stop_words]
    
    # Count word frequency
    word_freq = {}
    for word in words:
        word_freq[word.lower()] = word_freq.get(word.lower(), 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, freq in sorted_words[:max_keywords]]
    
    return keywords

def merge_overlapping_ranges(ranges: List[Tuple[int, int]], 
                           overlap_threshold: int = 5) -> List[Tuple[int, int]]:
    """
    Merge overlapping or nearby text ranges
    
    Args:
        ranges: List of (start, end) tuples
        overlap_threshold: Minimum gap to consider ranges separate
        
    Returns:
        List of merged ranges
    """
    if not ranges:
        return []
    
    # Sort ranges by start position
    sorted_ranges = sorted(ranges)
    merged = [sorted_ranges[0]]
    
    for current in sorted_ranges[1:]:
        last_merged = merged[-1]
        
        # Check if ranges overlap or are close enough to merge
        if current[0] <= last_merged[1] + overlap_threshold:
            # Merge ranges
            merged[-1] = (last_merged[0], max(last_merged[1], current[1]))
        else:
            # Add as separate range
            merged.append(current)
    
    return merged

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[Dict]:
    """
    Split text into overlapping chunks for processing
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks with metadata
    """
    if not text or len(text) <= chunk_size:
        return [{"text": text, "start": 0, "end": len(text), "chunk_id": 0}]
    
    chunks = []
    start = 0
    chunk_id = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Try to break at word boundary
        if end < len(text):
            # Look for word boundary within the last 10% of chunk
            boundary_search_start = max(start, end - chunk_size // 10)
            word_boundary = text.rfind(' ', boundary_search_start, end)
            if word_boundary > start:
                end = word_boundary
        
        chunk_text = text[start:end]
        chunks.append({
            "text": chunk_text,
            "start": start,
            "end": end,
            "chunk_id": chunk_id,
            "length": len(chunk_text)
        })
        
        chunk_id += 1
        start = max(start + 1, end - overlap)  # Ensure progress
    
    return chunks