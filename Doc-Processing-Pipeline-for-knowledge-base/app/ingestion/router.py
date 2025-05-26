import os
from fastapi import UploadFile
from typing import Literal

SUPPORTED_TYPES = {
    '.pdf': 'pdf',
    '.docx': 'docx',
    '.txt': 'txt',
}

def detect_file_type(filename: str) -> Literal['pdf', 'docx', 'txt', 'unsupported']:
    ext = os.path.splitext(filename)[1].lower()
    return SUPPORTED_TYPES.get(ext, 'unsupported')


def validate_file(file: UploadFile) -> bool:
    filetype = detect_file_type(file.filename)
    return filetype != 'unsupported' 