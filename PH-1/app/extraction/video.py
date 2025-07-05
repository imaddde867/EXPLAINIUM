"""
EXPLAINIUM Video Processing Module

This module provides video processing capabilities including:
- Video frame extraction
- Key frame detection
- Video metadata extraction
- Batch frame processing for OCR
- Video format support (MP4, AVI, MOV, etc.)
"""

import logging
import cv2
import numpy as np
import tempfile
import os
from PIL import Image
from fastapi import UploadFile, HTTPException
from typing import List, Dict, Optional, Tuple
import pytesseract
from datetime import timedelta

# Configure logging
logger = logging.getLogger(__name__)

def get_video_metadata(file: UploadFile) -> Dict:
    """
    Extract metadata from video file
    
    Args:
        file: Uploaded video file
        
    Returns:
        Dictionary containing video metadata
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            file.file.seek(0)
            temp_file.write(file.file.read())
            temp_path = temp_file.name
        
        try:
            # Open video file
            cap = cv2.VideoCapture(temp_path)
            
            if not cap.isOpened():
                raise ValueError("Could not open video file")
            
            # Get video properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            metadata = {
                "frame_count": frame_count,
                "fps": round(fps, 2),
                "width": width,
                "height": height,
                "resolution": f"{width}x{height}",
                "duration_seconds": round(duration, 2),
                "duration_formatted": str(timedelta(seconds=duration)),
                "file_size": os.path.getsize(temp_path),
                "codec": "Unknown"  # OpenCV doesn't easily provide codec info
            }
            
            cap.release()
            return metadata
            
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        logger.error(f"Failed to extract video metadata: {e}")
        raise HTTPException(status_code=500, detail=f"Video metadata extraction failed: {str(e)}")

def extract_video_keyframes(file: UploadFile, 
                          frame_interval: int = 30, 
                          max_frames: int = 50,
                          quality_threshold: float = 0.7) -> List[Dict]:
    """
    Extract key frames from video with quality assessment
    
    Args:
        file: Uploaded video file
        frame_interval: Extract every Nth frame
        max_frames: Maximum number of frames to extract
        quality_threshold: Minimum quality score for frame selection
        
    Returns:
        List of frame data with metadata
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            file.file.seek(0)
            temp_file.write(file.file.read())
            temp_path = temp_file.name
        
        frames_data = []
        
        try:
            # Open video file
            cap = cv2.VideoCapture(temp_path)
            
            if not cap.isOpened():
                raise ValueError("Could not open video file")
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            frame_number = 0
            extracted_count = 0
            
            while extracted_count < max_frames and frame_number < frame_count:
                # Set frame position
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Assess frame quality
                quality_score = assess_frame_quality(frame)
                
                if quality_score >= quality_threshold:
                    # Convert frame to RGB for PIL
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_image = Image.fromarray(frame_rgb)
                    
                    # Calculate timestamp
                    timestamp = frame_number / fps if fps > 0 else 0
                    
                    frame_data = {
                        "frame_number": frame_number,
                        "timestamp": round(timestamp, 2),
                        "timestamp_formatted": str(timedelta(seconds=timestamp)),
                        "quality_score": round(quality_score, 3),
                        "width": frame.shape[1],
                        "height": frame.shape[0],
                        "image": pil_image  # Store PIL image for further processing
                    }
                    
                    frames_data.append(frame_data)
                    extracted_count += 1
                    logger.debug(f"Extracted frame {frame_number} with quality {quality_score}")
                
                frame_number += frame_interval
            
            cap.release()
            
            logger.info(f"Extracted {len(frames_data)} quality frames from video")
            return frames_data
            
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except Exception as e:
        logger.error(f"Failed to extract video frames: {e}")
        raise HTTPException(status_code=500, detail=f"Video frame extraction failed: {str(e)}")

def assess_frame_quality(frame: np.ndarray) -> float:
    """
    Assess the quality of a video frame for OCR suitability
    
    Args:
        frame: OpenCV frame (BGR format)
        
    Returns:
        Quality score between 0 and 1
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate variance (measure of contrast)
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate mean brightness
        mean_brightness = np.mean(gray)
        
        # Calculate histogram distribution
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_normalized = hist / hist.sum()
        entropy = -np.sum(hist_normalized * np.log2(hist_normalized + 1e-10))
        
        # Normalize metrics to 0-1 range
        variance_score = min(1.0, variance / 1000.0)
        brightness_score = 1.0 - abs(mean_brightness - 128) / 128.0  # Optimal at 128
        entropy_score = entropy / 8.0  # Max entropy is 8 for 8-bit images
        
        # Weighted combination
        quality_score = (0.4 * variance_score + 0.3 * brightness_score + 0.3 * entropy_score)
        
        return max(0.0, min(1.0, quality_score))
        
    except Exception as e:
        logger.warning(f"Frame quality assessment failed: {e}")
        return 0.5  # Default moderate quality

def extract_text_from_video_frames(frames_data: List[Dict], 
                                 ocr_confidence_threshold: float = 0.6) -> List[Dict]:
    """
    Extract text from video frames using OCR
    
    Args:
        frames_data: List of frame data from extract_video_keyframes
        ocr_confidence_threshold: Minimum confidence for OCR results
        
    Returns:
        List of frames with extracted text data
    """
    results = []
    
    for frame_data in frames_data:
        try:
            pil_image = frame_data.get("image")
            if not pil_image:
                continue
            
            # Convert to grayscale for better OCR
            if pil_image.mode != 'L':
                gray_image = pil_image.convert('L')
            else:
                gray_image = pil_image
            
            # Extract text with confidence data
            ocr_data = pytesseract.image_to_data(
                gray_image, 
                output_type=pytesseract.Output.DICT,
                config='--oem 3 --psm 6'
            )
            
            # Filter and process OCR results
            extracted_text = []
            word_count = 0
            total_confidence = 0
            
            for i, text in enumerate(ocr_data['text']):
                confidence = int(ocr_data['conf'][i])
                if confidence > (ocr_confidence_threshold * 100) and text.strip():
                    extracted_text.append({
                        "text": text.strip(),
                        "confidence": confidence / 100.0,
                        "bbox": {
                            "x": ocr_data['left'][i],
                            "y": ocr_data['top'][i],
                            "width": ocr_data['width'][i],
                            "height": ocr_data['height'][i]
                        }
                    })
                    word_count += 1
                    total_confidence += confidence
            
            # Combine all text
            full_text = ' '.join([item['text'] for item in extracted_text])
            avg_confidence = total_confidence / max(1, word_count) / 100.0
            
            result = {
                "frame_number": frame_data["frame_number"],
                "timestamp": frame_data["timestamp"],
                "timestamp_formatted": frame_data["timestamp_formatted"],
                "quality_score": frame_data["quality_score"],
                "text_extracted": full_text,
                "word_count": word_count,
                "average_confidence": round(avg_confidence, 3),
                "text_regions": extracted_text,
                "has_text": len(full_text.strip()) > 0
            }
            
            # Remove PIL image to reduce memory usage
            result_copy = frame_data.copy()
            if "image" in result_copy:
                del result_copy["image"]
            result.update(result_copy)
            
            results.append(result)
            
            if full_text.strip():
                logger.debug(f"Frame {frame_data['frame_number']}: extracted {word_count} words")
            
        except Exception as e:
            logger.error(f"OCR failed for frame {frame_data.get('frame_number', 'unknown')}: {e}")
            # Add frame without text data
            result = frame_data.copy()
            if "image" in result:
                del result["image"]
            result.update({
                "text_extracted": "",
                "word_count": 0,
                "average_confidence": 0,
                "text_regions": [],
                "has_text": False,
                "error": str(e)
            })
            results.append(result)
    
    logger.info(f"Processed {len(results)} frames for text extraction")
    return results

def get_video_text_summary(video_text_data: List[Dict]) -> Dict:
    """
    Generate a summary of text extracted from video
    
    Args:
        video_text_data: List of frame text data from extract_text_from_video_frames
        
    Returns:
        Summary statistics and combined text
    """
    try:
        total_frames = len(video_text_data)
        frames_with_text = sum(1 for frame in video_text_data if frame.get("has_text", False))
        total_words = sum(frame.get("word_count", 0) for frame in video_text_data)
        
        # Combine all unique text
        all_text = []
        seen_text = set()
        
        for frame in video_text_data:
            text = frame.get("text_extracted", "").strip()
            if text and text not in seen_text:
                all_text.append(text)
                seen_text.add(text)
        
        combined_text = ' '.join(all_text)
        
        # Calculate average confidence
        confidences = [frame.get("average_confidence", 0) for frame in video_text_data if frame.get("has_text", False)]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        summary = {
            "total_frames_processed": total_frames,
            "frames_with_text": frames_with_text,
            "text_detection_rate": round(frames_with_text / max(1, total_frames), 3),
            "total_words_extracted": total_words,
            "unique_text_segments": len(all_text),
            "combined_text": combined_text,
            "combined_text_length": len(combined_text),
            "average_confidence": round(avg_confidence, 3),
            "extraction_success": frames_with_text > 0
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Failed to generate video text summary: {e}")
        return {
            "error": str(e),
            "extraction_success": False
        }