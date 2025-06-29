import os
from fastapi import UploadFile, HTTPException
from typing import Literal, Union

# Supported file types and their categories
SUPPORTED_TYPES = {
    '.pdf': 'pdf',
    '.docx': 'docx',
    '.txt': 'txt',
    '.md': 'txt',
    '.png': 'image',
    '.jpg': 'image',
    '.jpeg': 'image',
    '.gif': 'image',
    '.bmp': 'image',
    '.tiff': 'image',
    '.mp4': 'video',
    '.avi': 'video',
    '.mov': 'video',
    '.mkv': 'video',
}

# File size limits (in bytes)
MAX_FILE_SIZES = {
    'pdf': 50 * 1024 * 1024,      # 50MB
    'docx': 25 * 1024 * 1024,     # 25MB
    'txt': 10 * 1024 * 1024,      # 10MB
    'image': 20 * 1024 * 1024,    # 20MB
    'video': 500 * 1024 * 1024,   # 500MB
}

def detect_file_type(filename: str) -> Union[str, Literal['unsupported']]:
    """Detect file type based on extension"""
    if not filename:
        return 'unsupported'

    ext = os.path.splitext(filename)[1].lower()
    return SUPPORTED_TYPES.get(ext, 'unsupported')

def validate_file(file: UploadFile) -> bool:
    """Validate file type and basic properties"""
    if not file.filename:
        return False

    filetype = detect_file_type(file.filename)
    if filetype == 'unsupported':
        return False

    # Check file size if available
    if hasattr(file, 'size') and file.size:
        max_size = MAX_FILE_SIZES.get(filetype, 10 * 1024 * 1024)  # Default 10MB
        if file.size > max_size:
            return False

    return True

def validate_file_strict(file: UploadFile) -> None:
    """Strict validation with detailed error messages"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    filetype = detect_file_type(file.filename)
    if filetype == 'unsupported':
        supported_extensions = list(SUPPORTED_TYPES.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Supported extensions: {', '.join(supported_extensions)}"
        )

    # Check file size if available
    if hasattr(file, 'size') and file.size:
        max_size = MAX_FILE_SIZES.get(filetype, 10 * 1024 * 1024)
        if file.size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size for {filetype} files: {max_size_mb}MB"
            )