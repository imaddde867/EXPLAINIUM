# Document Processing Pipeline

A scalable, privacy-first document processing system that intelligently extracts and understands multi-modal content from enterprise documents.

## Features

- Document ingestion and routing system
- Support for multiple file formats (PDF, DOCX, TXT, MD)
- RESTful API for document management
- PostgreSQL database for metadata storage
- File storage with unique naming
- Status tracking for document processing

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (for future task queue implementation)

## Installation

1. Clone the repository:
```bash
git clone <https://github.com/imaddde867/Doc-Processing-Pipeline-for-knowledge-base.git>
cd doc-processing-pipeline
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
export POSTGRES_SERVER=localhost
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your_password
export POSTGRES_DB=doc_processing
```

5. Create the database:
```bash
createdb doc_processing
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation at:
```
http://localhost:8000/docs
```

## API Endpoints

- `POST /api/v1/documents/upload` - Upload a new document
- `GET /api/v1/documents/{document_id}` - Get document details
- `GET /api/v1/documents/` - List all documents
- `PATCH /api/v1/documents/{document_id}` - Update document metadata
- `DELETE /api/v1/documents/{document_id}` - Delete a document

## Project Structure

```
app/
├── api/
│   └── v1/
│       └── endpoints/
│           └── documents.py
├── core/
│   └── config.py
├── db/
│   ├── base_class.py
│   └── session.py
├── models/
│   └── document.py
├── schemas/
│   └── document.py
├── services/
│   └── document_service.py
└── main.py
```

## Development

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit them:
```bash
git add .
git commit -m "Description of your changes"
```

3. Push your changes:
```bash
git push origin feature/your-feature-name
```

## Testing

Run the test suite:
```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 