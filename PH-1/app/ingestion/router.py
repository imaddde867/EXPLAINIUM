import os
from fastapi import UploadFile, HTTPException, APIRouter
from typing import Literal, Union, Optional
from PIL import Image
import pytesseract

# Supported file types and their categories
SUPPORTED_TYPES = {
    '.pdf': 'pdf', '.docx': 'docx', '.txt': 'txt', '.md': 'txt',
    '.png': 'image', '.jpg': 'image', '.jpeg': 'image', '.gif': 'image', 
    '.bmp': 'image', '.tiff': 'image',
    '.mp4': 'video', '.avi': 'video', '.mov': 'video', '.mkv': 'video',
}

# File size limits (in bytes)
MAX_FILE_SIZES = {
    'pdf': 50 * 1024 * 1024, 'docx': 25 * 1024 * 1024, 'txt': 10 * 1024 * 1024,
    'image': 20 * 1024 * 1024, 'video': 500 * 1024 * 1024,
}

def detect_file_type(filename: str) -> Union[str, Literal['unsupported']]:
    """Detect file type based on extension"""
    if not filename:
        return 'unsupported'
    ext = os.path.splitext(filename)[1].lower()
    return SUPPORTED_TYPES.get(ext, 'unsupported')

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
        
def extract_text_image(file: UploadFile) -> Optional[str]:
    """Extract text from image using OCR"""
    try:
        file.file.seek(0)
        image_bytes = file.file.read()
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        text = pytesseract.image_to_string(image, lang='eng')
        return text.strip() if text.strip() else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

        
router = APIRouter()
@router.post("/upload-image")
async def upload_file(file: UploadFile):
    validate_file_strict(file)
    filetype = detect_file_type(file.filename)

    if filetype == "image":
        text  = extract_text_image(file)
        return {"extracted_text": text}
    else:
        raise HTTPException(status_code=400, detail="Only image files are supported for text extraction")

