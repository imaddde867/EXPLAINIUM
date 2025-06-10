# PH-1 Architecture Documentation

*Smart Knowledge Extraction System - Technical Architecture*

---

## 🏗️ System Architecture Overview

### 📊 High-Level Architecture

```mermaid
graph TB
    subgraph "🟡 INPUT LAYER"
        DOC[📄 Documents<br/>PDF • DOCX • TXT]
        IMG[🖼️ Images<br/>JPG • PNG • TIFF]
        VID[🎥 Videos<br/>MP4 • AVI • MOV]
    end
    
    subgraph "🟣 PROCESSING ENGINE"
        UPLOAD[📤 File Upload<br/>Validation & Storage]
        OCR[📖 OCR Engine<br/>Tesseract + PaddleOCR]
        NLP[🧠 NLP Pipeline<br/>Entity Recognition]
        CLASS[🏷️ Classification<br/>Content Categorization]
    end
    
    subgraph "🔵 KNOWLEDGE STORE"
        POSTGRES[🐘 PostgreSQL<br/>Structured Data]
        ENTITIES[🎯 Entities<br/>Named Entity Store]
        CATEGORIES[📂 Categories<br/>Content Classification]
        METADATA[📊 Metadata<br/>Document Properties]
    end
    
    subgraph "🟢 API LAYER"
        REST[🔗 REST API<br/>FastAPI Framework]
        DOCS[📚 API Documentation<br/>OpenAPI/Swagger]
        WEB[🌐 Web Interface<br/>Testing Dashboard]
    end
    
    DOC --> UPLOAD
    IMG --> UPLOAD
    VID --> UPLOAD
    
    UPLOAD --> OCR
    OCR --> NLP
    NLP --> CLASS
    
    CLASS --> POSTGRES
    NLP --> ENTITIES
    CLASS --> CATEGORIES
    UPLOAD --> METADATA
    
    POSTGRES --> REST
    ENTITIES --> REST
    CATEGORIES --> REST
    METADATA --> REST
    
    REST --> DOCS
    REST --> WEB
    
    classDef inputStyle fill:#ffd200,stroke:#333,stroke-width:2px,color:#000
    classDef processStyle fill:#8e44ad,stroke:#333,stroke-width:2px,color:#fff
    classDef storeStyle fill:#3498db,stroke:#333,stroke-width:2px,color:#fff
    classDef apiStyle fill:#27ae60,stroke:#333,stroke-width:2px,color:#fff
    
    class DOC,IMG,VID inputStyle
    class UPLOAD,OCR,NLP,CLASS processStyle
    class POSTGRES,ENTITIES,CATEGORIES,METADATA storeStyle
    class REST,DOCS,WEB apiStyle
```

---

## 🔄 Data Flow Architecture

### 📊 Document Processing Pipeline

```mermaid
sequenceDiagram
    participant C as Client
    participant API as FastAPI Server
    participant V as Validator
    participant E as Extraction Engine
    participant NLP as NLP Pipeline
    participant DB as PostgreSQL
    
    C->>API: Upload Document
    API->>V: Validate File
    V->>API: Validation Result
    API->>E: Extract Text/Content
    E->>NLP: Send Extracted Content
    NLP->>NLP: Entity Recognition
    NLP->>NLP: Content Classification
    NLP->>DB: Store Entities
    NLP->>DB: Store Categories
    DB->>API: Processing Complete
    API->>C: Return Results
```

---

## 🗃️ Database Schema

### 📊 Entity Relationship Diagram

```mermaid
erDiagram
    DOCUMENT ||--o{ KNOWLEDGE_ENTITY : contains
    DOCUMENT ||--o{ CONTENT_CATEGORY : classified_as
    DOCUMENT ||--o{ KEY_PHRASE : includes
    DOCUMENT ||--o{ DOCUMENT_STRUCTURE : has_structure
    KNOWLEDGE_ENTITY ||--o{ KNOWLEDGE_RELATIONSHIP : participates_in
    
    DOCUMENT {
        int id PK
        string filename
        string filetype
        string status
        text content
        json metadata
        datetime created_at
        datetime updated_at
    }
    
    KNOWLEDGE_ENTITY {
        int id PK
        int document_id FK
        string text
        string label
        float confidence
        int start_position
        int end_position
        text context
        datetime created_at
    }
    
    CONTENT_CATEGORY {
        int id PK
        int document_id FK
        string category
        float confidence
        json keywords
        datetime created_at
    }
    
    KEY_PHRASE {
        int id PK
        int document_id FK
        string phrase
        float score
        datetime created_at
    }
    
    DOCUMENT_STRUCTURE {
        int id PK
        int document_id FK
        string structure_type
        text content
        int line_number
        json metadata
        datetime created_at
    }
    
    KNOWLEDGE_RELATIONSHIP {
        int id PK
        int source_entity_id FK
        int target_entity_id FK
        string relationship_type
        float confidence
        text context
        datetime created_at
    }
```

---

## 🛠️ Technology Stack

### 🐍 Backend Components

```mermaid
graph LR
    subgraph "🌐 Web Framework"
        FASTAPI[FastAPI<br/>REST API Server]
        UVICORN[Uvicorn<br/>ASGI Server]
        PYDANTIC[Pydantic<br/>Data Validation]
    end
    
    subgraph "🧠 AI/ML Stack"
        SPACY[spaCy<br/>NLP Processing]
        TESSERACT[Tesseract<br/>OCR Engine]
        PADDLE[PaddleOCR<br/>Advanced OCR]
        SKLEARN[scikit-learn<br/>ML Utilities]
    end
    
    subgraph "🗃️ Data Layer"
        POSTGRES[PostgreSQL<br/>Primary Database]
        SQLALCHEMY[SQLAlchemy<br/>ORM Framework]
        ALEMBIC[Alembic<br/>Database Migrations]
    end
    
    subgraph "🔧 Utilities"
        PYPDF[PyPDF2<br/>PDF Processing]
        DOCX[python-docx<br/>Word Documents]
        PILLOW[Pillow<br/>Image Processing]
        OPENCV[OpenCV<br/>Computer Vision]
    end
    
    FASTAPI --> SPACY
    FASTAPI --> POSTGRES
    UVICORN --> FASTAPI
    PYDANTIC --> FASTAPI
    
    SPACY --> SKLEARN
    TESSERACT --> PADDLE
    
    POSTGRES --> SQLALCHEMY
    SQLALCHEMY --> ALEMBIC
    
    PYPDF --> DOCX
    PILLOW --> OPENCV
    
    classDef webStyle fill:#27ae60,stroke:#333,stroke-width:2px,color:#fff
    classDef aiStyle fill:#e74c3c,stroke:#333,stroke-width:2px,color:#fff
    classDef dataStyle fill:#3498db,stroke:#333,stroke-width:2px,color:#fff
    classDef utilStyle fill:#f39c12,stroke:#333,stroke-width:2px,color:#fff
    
    class FASTAPI,UVICORN,PYDANTIC webStyle
    class SPACY,TESSERACT,PADDLE,SKLEARN aiStyle
    class POSTGRES,SQLALCHEMY,ALEMBIC dataStyle
    class PYPDF,DOCX,PILLOW,OPENCV utilStyle
```

---

## 📁 Project Structure

### 🗂️ Directory Organization

```
PH-1/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── db/                       # Database layer
│   │   ├── __init__.py
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── crud.py               # Database operations
│   │   └── session.py            # Database session management
│   ├── schemas/                  # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── document.py           # Document schemas
│   │   └── knowledge.py          # Knowledge extraction schemas
│   ├── ingestion/                # File ingestion and validation
│   │   ├── __init__.py
│   │   └── router.py             # File handling utilities
│   ├── extraction/               # Content extraction engines
│   │   ├── __init__.py
│   │   ├── text.py               # Text extraction (PDF, DOCX, TXT)
│   │   ├── knowledge.py          # Knowledge extraction (NER, classification)
│   │   ├── image.py              # Image processing and OCR
│   │   └── video.py              # Video frame extraction
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   └── helpers.py            # Common helper functions
│   └── templates/                # HTML templates (if needed)
├── test_data/                    # Sample test files
├── requirements.txt              # Python dependencies
├── init_db.py                    # Database initialization script
├── test_api.py                   # API testing script
├── README.md                     # Project documentation
└── ARCHITECTURE.md               # This file
```

---

## 🔧 Configuration & Environment

### ⚙️ Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/explainium_ph1
DB_HOST=localhost
DB_PORT=5432
DB_NAME=explainium_ph1
DB_USER=username
DB_PASSWORD=password

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false
LOG_LEVEL=INFO

# File Processing Configuration
MAX_FILE_SIZE=100MB
ALLOWED_EXTENSIONS=pdf,docx,txt,jpg,png,tiff,mp4,avi,mov
UPLOAD_DIRECTORY=./uploads

# AI/ML Configuration
SPACY_MODEL=en_core_web_sm
OCR_LANGUAGE=eng
CONFIDENCE_THRESHOLD=0.5
```

---

## 🚀 Deployment Architecture

### 🐳 Container Deployment

```mermaid
graph TB
    subgraph "🌐 Load Balancer"
        LB[Nginx<br/>Load Balancer]
    end
    
    subgraph "🐳 Application Containers"
        APP1[PH-1 Instance 1<br/>FastAPI + Uvicorn]
        APP2[PH-1 Instance 2<br/>FastAPI + Uvicorn]
        APP3[PH-1 Instance 3<br/>FastAPI + Uvicorn]
    end
    
    subgraph "🗃️ Data Layer"
        DB[PostgreSQL<br/>Primary Database]
        REDIS[Redis<br/>Cache & Sessions]
        STORAGE[File Storage<br/>MinIO/S3]
    end
    
    subgraph "📊 Monitoring"
        GRAFANA[Grafana<br/>Dashboards]
        PROMETHEUS[Prometheus<br/>Metrics]
        LOGS[ELK Stack<br/>Logging]
    end
    
    LB --> APP1
    LB --> APP2
    LB --> APP3
    
    APP1 --> DB
    APP2 --> DB
    APP3 --> DB
    
    APP1 --> REDIS
    APP2 --> REDIS
    APP3 --> REDIS
    
    APP1 --> STORAGE
    APP2 --> STORAGE
    APP3 --> STORAGE
    
    APP1 --> PROMETHEUS
    APP2 --> PROMETHEUS
    APP3 --> PROMETHEUS
    
    PROMETHEUS --> GRAFANA
    APP1 --> LOGS
    APP2 --> LOGS
    APP3 --> LOGS
    
    classDef lbStyle fill:#27ae60,stroke:#333,stroke-width:2px,color:#fff
    classDef appStyle fill:#3498db,stroke:#333,stroke-width:2px,color:#fff
    classDef dataStyle fill:#e74c3c,stroke:#333,stroke-width:2px,color:#fff
    classDef monitorStyle fill:#f39c12,stroke:#333,stroke-width:2px,color:#fff
    
    class LB lbStyle
    class APP1,APP2,APP3 appStyle
    class DB,REDIS,STORAGE dataStyle
    class GRAFANA,PROMETHEUS,LOGS monitorStyle
```

---

*Developed following Turku UAS visual identity standards*
*© 2024 EXPLAINIUM PH-1 - Technical Architecture Documentation*
