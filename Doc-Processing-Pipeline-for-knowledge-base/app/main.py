from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from app.ingestion.router import detect_file_type, validate_file
from app.extraction.text import extract_text_pdf, extract_text_docx, extract_text_txt
from app.db.session import SessionLocal
from app.db.crud import create_document, get_document
from app.schemas.document import DocumentCreate, DocumentOut
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
        <head><title>Document Upload</title></head>
        <body>
            <h1>Upload a Document</h1>
            <form action="/api/v1/documents/upload" enctype="multipart/form-data" method="post">
                <input name="file" type="file" />
                <input type="submit" />
            </form>
        </body>
    </html>
    """

@app.post("/api/v1/documents/upload")
def upload_document(file: UploadFile = File(...)):
    if not validate_file(file):
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    filetype = detect_file_type(file.filename)
    # Reset file pointer for extraction
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
    return {"id": db_doc.id, "filename": db_doc.filename, "status": db_doc.status}

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