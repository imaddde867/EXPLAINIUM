import pdfplumber
import docx
from fastapi import UploadFile
from typing import Optional
import pytesseract
from PIL import Image
import io
import cv2
import numpy as np
import tempfile

def extract_text_pdf(file: UploadFile) -> Optional[str]:
    with pdfplumber.open(file.file) as pdf:
        return "\n".join(page.extract_text() or '' for page in pdf.pages)

def extract_text_docx(file: UploadFile) -> Optional[str]:
    doc = docx.Document(file.file)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_txt(file: UploadFile) -> Optional[str]:
    content = file.file.read()
    try:
        return content.decode('utf-8')
    except Exception:
        return content.decode('latin-1', errors='ignore')

def extract_text_image(file: UploadFile) -> Optional[str]:
    image_bytes = file.file.read()
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image)
    return text

def extract_video_keyframes(file: UploadFile, frame_interval: int = 30) -> list:
    # Save file to temp location for OpenCV
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name
    cap = cv2.VideoCapture(tmp_path)
    frames = []
    idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if idx % frame_interval == 0:
            # Convert frame to JPEG bytes
            _, buf = cv2.imencode('.jpg', frame)
            frames.append(buf.tobytes())
        idx += 1
    cap.release()
    return frames 