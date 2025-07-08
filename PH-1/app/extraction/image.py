
EXPLAINIUM Image Processing Module

This module provides image processing and OCR capabilities including:
- Image preprocessing and enhancement
- OCR text extraction using Tesseract
- Multiple image format support
- Image quality optimization for better OCR results
"""

import logging
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from fastapi import UploadFile, HTTPException
from typing import Optional, Dict, List, Tuple
import io

# Configure logging
logger = logging.getLogger(__name__)

def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    """
    Preprocess image to improve OCR accuracy
    
    Args:
        image: PIL Image object
        
    Returns:
        Preprocessed PIL Image object
    """
    try:
        # Convert to grayscale if needed
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Apply slight sharpening
        image = image.filter(ImageFilter.SHARPEN)
        
        # Convert to OpenCV format for advanced preprocessing
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_GRAY2BGR)
        
        # Apply Gaussian blur to reduce noise
        cv_image = cv2.GaussianBlur(cv_image, (1, 1), 0)
        
        # Apply threshold to get binary image
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL
        return Image.fromarray(thresh)
        
    except Exception as e:
        logger.warning(f"Image preprocessing failed, using original: {e}")
        return image

def extract_text_from_image(file: UploadFile, preprocess: bool = True) -> Optional[str]:
    """
    Extract text from image using OCR
    
    Args:
        file: Uploaded image file
        preprocess: Whether to preprocess image for better OCR
        
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        file.file.seek(0)
        image_bytes = file.file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Preprocess image if requested
        if preprocess:
            image = preprocess_image_for_ocr(image)
        
        # Configure Tesseract options for better accuracy
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?-()[]{}:;"\'\ '"
        
        # Extract text
        text = pytesseract.image_to_string(image, config=custom_config)
        
        # Clean up extracted text
        cleaned_text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        
        if not cleaned_text or len(cleaned_text.strip()) < 3:
            logger.warning(f"Little or no text extracted from image: {file.filename}")
            return None
            
        logger.info(f"Successfully extracted {len(cleaned_text)} characters from image: {file.filename}")
        return cleaned_text
        
    except Exception as e:
        logger.error(f"Image OCR failed for {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Image OCR processing failed: {str(e)}")

def get_image_metadata(file: UploadFile) -> Dict:
    """
    Extract metadata from image file
    
    Args:
        file: Uploaded image file
        
    Returns:
        Dictionary containing image metadata
    """
    try:
        file.file.seek(0)
        image_bytes = file.file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        metadata = {
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
            "width": image.width,
            "height": image.height,
            "has_transparency": image.mode in ('RGBA', 'LA', 'P'),
            "file_size": len(image_bytes)
        }
        
        # Try to get EXIF data
        if hasattr(image, '_getexif'):
            exif_data = image._getexif()
            if exif_data:
                metadata["exif_available"] = True
                metadata["exif_keys"] = list(exif_data.keys())[:10]  # First 10 keys
            else:
                metadata["exif_available"] = False
        
        return metadata
        
    except Exception as e:
        logger.error(f"Failed to extract image metadata: {e}")
        return {"error": str(e)}

def detect_image_quality(file: UploadFile) -> Dict:
    """
    Assess image quality for OCR suitability
    
    Args:
        file: Uploaded image file
        
    Returns:
        Dictionary with quality assessment
    """
    try:
        file.file.seek(0)
        image_bytes = file.file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to grayscale for analysis
        if image.mode != 'L':
            gray_image = image.convert('L')
        else:
            gray_image = image
            
        # Convert to numpy array
        img_array = np.array(gray_image)
        
        # Calculate metrics
        variance = np.var(img_array)  # Higher variance = more contrast
        mean_brightness = np.mean(img_array)
        
        # Assess quality
        quality_score = min(100, max(0, (variance / 1000) * 100))
        
        assessment = {
            "quality_score": round(quality_score, 2),
            "variance": round(variance, 2),
            "mean_brightness": round(mean_brightness, 2),
            "resolution": f"{image.width}x{image.height}",
            "suitable_for_ocr": quality_score > 30 and mean_brightness > 50,
            "recommendations": []
        }
        
        # Add recommendations
        if quality_score < 30:
            assessment["recommendations"].append("Image has low contrast - consider preprocessing")
        if mean_brightness < 50:
            assessment["recommendations"].append("Image is too dark - increase brightness")
        if image.width < 300 or image.height < 300:
            assessment["recommendations"].append("Image resolution is low - consider higher resolution")
            
        return assessment
        
    except Exception as e:
        logger.error(f"Failed to assess image quality: {e}")
        return {"error": str(e), "suitable_for_ocr": False}

def extract_image_regions(file: UploadFile, min_area: int = 1000) -> List[Dict]:
    """
    Detect and extract text regions from image
    
    Args:
        file: Uploaded image file
        min_area: Minimum area for text regions
        
    Returns:
        List of detected text regions with their properties
    """
    try:
        file.file.seek(0)
        image_bytes = file.file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        regions = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Extract region
                region = gray[y:y+h, x:x+w]
                region_text = pytesseract.image_to_string(region).strip()
                
                if region_text:
                    regions.append({
                        "region_id": i,
                        "bbox": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                        "area": int(area),
                        "text": region_text,
                        "confidence": len(region_text) / max(1, w * h / 1000)  # Simple confidence metric
                    })
        
        logger.info(f"Detected {len(regions)} text regions in image")
        return regions
        
    except Exception as e:
        logger.error(f"Failed to extract image regions: {e}")
        return []
