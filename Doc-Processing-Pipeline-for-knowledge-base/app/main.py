from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from app.ingestion.router import detect_file_type, validate_file
from app.extraction.text import extract_text_pdf, extract_text_docx, extract_text_txt, extract_text_image, extract_video_keyframes
from app.db.session import SessionLocal
from app.db.crud import create_document, get_document, create_video_frame
from app.schemas.document import DocumentCreate, DocumentOut
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
import base64
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os

app = FastAPI()

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/upload-ui", response_class=HTMLResponse)
def upload_ui(request: Request, file: UploadFile = File(...), upload_type: str = Form(...)):
    # Route to correct endpoint logic
    if upload_type == 'document':
        if not validate_file(file):
            return templates.TemplateResponse("index.html", {"request": request, "result": {"error": "Unsupported file type."}})
        filetype = detect_file_type(file.filename)
        file.file.seek(0)
        if filetype == 'pdf':
            content = extract_text_pdf(file)
        elif filetype == 'docx':
            content = extract_text_docx(file)
        elif filetype == 'txt':
            content = extract_text_txt(file)
        else:
            content = None
        db = SessionLocal()
        doc_in = DocumentCreate(filename=file.filename, filetype=filetype, content=content)
        db_doc = create_document(db, doc_in, status='processed')
        db.close()
        result = {"type": "document", "filename": file.filename, "content": content}
    elif upload_type == 'image':
        file.file.seek(0)
        ocr_text = extract_text_image(file)
        db = SessionLocal()
        doc_in = DocumentCreate(filename=file.filename, filetype='image', content=ocr_text)
        db_doc = create_document(db, doc_in, status='processed')
        db.close()
        result = {"type": "image", "filename": file.filename, "ocr_text": ocr_text}
    elif upload_type == 'video':
        file.file.seek(0)
        db = SessionLocal()
        doc_in = DocumentCreate(filename=file.filename, filetype='video', content=None)
        db_doc = create_document(db, doc_in, status='processing')
        frames = extract_video_keyframes(file)
        preview_frames = []
        for idx, frame_bytes in enumerate(frames):
            img_b64 = base64.b64encode(frame_bytes).decode('utf-8')
            create_video_frame(db, db_doc.id, idx, img_b64)
            if idx < 3:
                preview_frames.append(img_b64)
        db_doc.status = 'processed'
        db.commit()
        db.close()
        result = {"type": "video", "filename": file.filename, "frames_extracted": len(frames), "preview_frames": preview_frames, "doc_id": db_doc.id}
    else:
        result = {"error": "Unknown upload type."}
    return templates.TemplateResponse("index.html", {"request": request, "result": result})

@app.post("/api/v1/images/upload")
def upload_image(file: UploadFile = File(...)):
    if detect_file_type(file.filename) != 'image':
        raise HTTPException(status_code=400, detail="Unsupported image type.")
    file.file.seek(0)
    ocr_text = extract_text_image(file)
    db = SessionLocal()
    doc_in = DocumentCreate(filename=file.filename, filetype='image', content=ocr_text)
    db_doc = create_document(db, doc_in, status='processed')
    db.close()
    return {"id": db_doc.id, "filename": db_doc.filename, "ocr_text": ocr_text}

@app.post("/api/v1/videos/upload")
def upload_video(file: UploadFile = File(...)):
    if detect_file_type(file.filename) != 'video':
        raise HTTPException(status_code=400, detail="Unsupported video type.")
    file.file.seek(0)
    db = SessionLocal()
    doc_in = DocumentCreate(filename=file.filename, filetype='video', content=None)
    db_doc = create_document(db, doc_in, status='processing')
    frames = extract_video_keyframes(file)
    preview_frames = []
    for idx, frame_bytes in enumerate(frames):
        img_b64 = base64.b64encode(frame_bytes).decode('utf-8')
        create_video_frame(db, db_doc.id, idx, img_b64)
        if idx < 3:
            preview_frames.append(img_b64)
    db_doc.status = 'processed'
    db.commit()
    db.close()
    return {
        "id": db_doc.id,
        "filename": db_doc.filename,
        "frames_extracted": len(frames),
        "preview_frames": preview_frames,
        "message": f"Upload successful. Use /api/v1/videos/{db_doc.id}/frame/{'{index}'} to retrieve frames."
    }

@app.get("/api/v1/videos/{doc_id}/frame/{frame_index}")
def get_video_frame(doc_id: int, frame_index: int):
    db = SessionLocal()
    from app.db.models import VideoFrame
    frame = db.query(VideoFrame).filter_by(document_id=doc_id, frame_index=frame_index).first()
    db.close()
    if not frame:
        raise HTTPException(status_code=404, detail="Frame not found.")
    return {"frame_index": frame_index, "image_base64": frame.image_data}

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/v1/documents/{doc_id}/status")
def get_doc_status(doc_id: int, db: Session = Depends(get_db)):
    doc = get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"id": doc.id, "filename": doc.filename, "status": doc.status}

@app.get("/api/v1/documents/{doc_id}/content", response_model=DocumentOut)
def get_doc_content(doc_id: int, db: Session = Depends(get_db)):
    doc = get_document(db, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc 