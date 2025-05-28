# Enterprise Document Processing & Knowledge Extraction System

## Step 1: Core Foundation

### Features
- Document upload (PDF, DOCX, TXT)
- File type detection and routing
- Basic text extraction
- PostgreSQL storage for metadata and content
- REST API (FastAPI)
- Simple web upload form
- Image upload (PNG, JPG) with OCR
- Video upload (MP4) with key frame extraction

### Requirements
- Python 3.8+
- PostgreSQL

### Additional Requirements
- Tesseract OCR (for pytesseract):
  - Install via Homebrew: `brew install tesseract`
  - Or via apt: `sudo apt-get install tesseract-ocr`

### Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables (optional, defaults shown):**
   ```bash
   export POSTGRES_USER=postgres
   export POSTGRES_PASSWORD=postgres
   export POSTGRES_DB=docdb
   export POSTGRES_HOST=localhost
   export POSTGRES_PORT=5432
   ```

3. **Create the database and tables:**
   ```python
   # In a Python shell:
   from app.db.models import Base
   from app.db.session import engine
   Base.metadata.create_all(bind=engine)
   ```

4. **Run the FastAPI app:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the web upload form:**
   - Open [http://localhost:8000/](http://localhost:8000/)

6. **API Endpoints:**
   - `POST /api/v1/documents/upload` (PDF, DOCX, TXT)
   - `POST /api/v1/images/upload` (PNG, JPG)
   - `POST /api/v1/videos/upload` (MP4)
   - `GET /api/v1/documents/{id}/status`
   - `GET /api/v1/documents/{id}/content`

---

- Image uploads will return OCR text.
- Video uploads will extract and store key frames (as base64-encoded JPEGs in the DB).
- Table extraction for PDFs is basic; advanced table/diagram support will come in later steps.

This is the foundation for a scalable, privacy-first, multi-modal document processing system. Next steps will add OCR, image, and video processing. 