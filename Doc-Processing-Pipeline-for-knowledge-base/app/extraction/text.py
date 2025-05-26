import pdfplumber
import docx
from fastapi import UploadFile
from typing import Optional

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