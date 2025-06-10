# EXPLAINIUM - Data Flow Architecture

*Professional data flow and processing pipeline documentation*

---

## 🔄 Data Flow Overview

### 📊 Complete Data Processing Pipeline

```mermaid
flowchart TD
    subgraph "🟡 INPUT SOURCES"
        DOC[📄 Documents<br/>PDF, DOCX, Videos]
        SENSORS[🔬 IoT Sensors<br/>Temperature, Pressure]
        AGENTS[🤖 Agent Outputs<br/>Tasks, Logs, Stats]
    end
    
    subgraph "🟣 PROCESSING ENGINES"
        OCR[📖 OCR Engine<br/>Tesseract + PaddleOCR]
        NLP[🧠 NLP Pipeline<br/>spaCy + Transformers]
        FUSION[🔄 Sensor Fusion<br/>Real-time Analytics]
        LEARNING[📈 Learning Engine<br/>Continuous Improvement]
    end
    
    subgraph "🔵 KNOWLEDGE LAYER"
        VECTOR[🎯 Vector Store<br/>ChromaDB Embeddings]
        GRAPH[🕸️ Knowledge Graph<br/>Neo4j Relationships]
        TIMESERIES[📊 Time Series<br/>TimescaleDB Metrics]
        STRUCTURED[🗃️ Structured Data<br/>PostgreSQL Tables]
    end
    
    subgraph "🟢 INTELLIGENCE HUB"
        REASONING[🧠 Reasoning Engine<br/>LLM + Logic Rules]
        DECISION[⚡ Decision Engine<br/>Real-time Inference]
        ORCHESTRATOR[🎭 Agent Orchestrator<br/>Multi-Agent Coordination]
    end
    
    subgraph "🟠 AGENT NETWORK"
        MAINTENANCE[🔧 Maintenance Agent]
        SAFETY[🛡️ Safety Agent]
        TRAINING[👨‍🏫 Training Agent]
        OPTIMIZATION[📊 Optimization Agent]
    end
    
    subgraph "⚪ OUTPUT CHANNELS"
        DASHBOARD[💻 Management Dashboard]
        MOBILE[📱 Mobile Apps]
        ALERTS[🚨 Real-time Alerts]
        REPORTS[📋 Automated Reports]
    end
    
    DOC --> OCR
    DOC --> NLP
    SENSORS --> FUSION
    AGENTS --> LEARNING
    
    OCR --> VECTOR
    NLP --> GRAPH
    FUSION --> TIMESERIES
    LEARNING --> STRUCTURED
    
    VECTOR --> REASONING
    GRAPH --> REASONING
    TIMESERIES --> DECISION
    STRUCTURED --> DECISION
    
    REASONING --> ORCHESTRATOR
    DECISION --> ORCHESTRATOR
    
    ORCHESTRATOR --> MAINTENANCE
    ORCHESTRATOR --> SAFETY
    ORCHESTRATOR --> TRAINING
    ORCHESTRATOR --> OPTIMIZATION
    
    MAINTENANCE --> DASHBOARD
    SAFETY --> MOBILE
    TRAINING --> ALERTS
    OPTIMIZATION --> REPORTS
    
    MAINTENANCE --> AGENTS
    SAFETY --> AGENTS
    TRAINING --> AGENTS
    OPTIMIZATION --> AGENTS
    
    classDef inputStyle fill:#ffd200,stroke:#333,stroke-width:2px,color:#000
    classDef processStyle fill:#8e44ad,stroke:#333,stroke-width:2px,color:#fff
    classDef knowledgeStyle fill:#3498db,stroke:#333,stroke-width:2px,color:#fff
    classDef intelligenceStyle fill:#27ae60,stroke:#333,stroke-width:2px,color:#fff
    classDef agentStyle fill:#e74c3c,stroke:#333,stroke-width:2px,color:#fff
    classDef outputStyle fill:#95a5a6,stroke:#333,stroke-width:2px,color:#000
    
    class DOC,SENSORS,AGENTS inputStyle
    class OCR,NLP,FUSION,LEARNING processStyle
    class VECTOR,GRAPH,TIMESERIES,STRUCTURED knowledgeStyle
    class REASONING,DECISION,ORCHESTRATOR intelligenceStyle
    class MAINTENANCE,SAFETY,TRAINING,OPTIMIZATION agentStyle
    class DASHBOARD,MOBILE,ALERTS,REPORTS outputStyle
```

---

## 🏗️ Processing Pipeline Details

### 📄 Document Processing Pipeline

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI Server
    participant Q as Celery Queue
    participant OCR as OCR Engine
    participant NLP as NLP Pipeline
    participant DB as Database
    participant VS as Vector Store
    
    U->>API: Upload Document
    API->>Q: Queue Processing Task
    Q->>OCR: Extract Text/Images
    OCR->>NLP: Send Extracted Content
    NLP->>NLP: Entity Recognition
    NLP->>NLP: Relationship Extraction
    NLP->>DB: Store Structured Data
    NLP->>VS: Store Vector Embeddings
    VS->>API: Processing Complete
    API->>U: Return Results
```

### 🔬 Sensor Data Pipeline

```mermaid
sequenceDiagram
    participant S as IoT Sensors
    participant E as Edge Gateway
    participant K as Kafka Stream
    participant F as Fusion Engine
    participant T as TimescaleDB
    participant A as Alert System
    
    S->>E: Raw Sensor Data
    E->>K: Preprocessed Stream
    K->>F: Real-time Processing
    F->>F: Pattern Analysis
    F->>T: Store Time Series
    F->>A: Trigger Alerts
    A->>A: Notify Stakeholders
```

### 🤖 Agent Coordination Pipeline

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant M as Maintenance Agent
    participant S as Safety Agent
    participant T as Training Agent
    participant D as Decision Engine
    participant K as Knowledge Base
    
    O->>K: Query Current State
    K->>O: Return Context
    O->>M: Assign Maintenance Task
    O->>S: Monitor Safety Status
    O->>T: Update Training Plans
    M->>D: Report Findings
    S->>D: Safety Assessment
    T->>D: Training Progress
    D->>O: Consolidated Intelligence
    O->>K: Update Knowledge Base
```

---

## 📊 Data Models & Schemas

### 🗃️ Core Data Structures

```mermaid
erDiagram
    DOCUMENT ||--o{ ENTITY : contains
    DOCUMENT ||--o{ CATEGORY : classified_as
    DOCUMENT ||--o{ PHRASE : includes
    ENTITY ||--o{ RELATIONSHIP : participates_in
    SENSOR ||--o{ READING : generates
    AGENT ||--o{ TASK : executes
    TASK ||--o{ OUTPUT : produces
    
    DOCUMENT {
        int id PK
        string filename
        string filetype
        text content
        json metadata
        datetime created_at
        string status
    }
    
    ENTITY {
        int id PK
        int document_id FK
        string text
        string label
        float confidence
        int start_position
        int end_position
    }
    
    SENSOR {
        int id PK
        string sensor_type
        string location
        json configuration
        datetime last_seen
        string status
    }
    
    READING {
        int id PK
        int sensor_id FK
        float value
        string unit
        datetime timestamp
        json metadata
    }
    
    AGENT {
        int id PK
        string agent_type
        string name
        json capabilities
        datetime created_at
        string status
    }
    
    TASK {
        int id PK
        int agent_id FK
        string task_type
        json parameters
        datetime started_at
        datetime completed_at
        string status
    }
```

---

## ⚡ Real-time Processing Architecture

### 🔄 Stream Processing Flow

```mermaid
graph LR
    subgraph "📡 Data Sources"
        IOT[IoT Sensors]
        CAM[Cameras]
        MIC[Microphones]
        LOG[System Logs]
    end
    
    subgraph "🌊 Stream Processing"
        KAFKA[Kafka Streams]
        FLINK[Apache Flink]
        SPARK[Spark Streaming]
    end
    
    subgraph "🧠 Real-time Analytics"
        CEP[Complex Event Processing]
        ML[ML Inference]
        RULES[Business Rules Engine]
    end
    
    subgraph "⚡ Actions"
        ALERT[Instant Alerts]
        AUTO[Automated Actions]
        DASH[Live Dashboards]
    end
    
    IOT --> KAFKA
    CAM --> KAFKA
    MIC --> KAFKA
    LOG --> KAFKA
    
    KAFKA --> FLINK
    KAFKA --> SPARK
    
    FLINK --> CEP
    SPARK --> ML
    CEP --> RULES
    
    CEP --> ALERT
    ML --> AUTO
    RULES --> DASH
    
    classDef sourceStyle fill:#ffd200,stroke:#333,stroke-width:2px
    classDef streamStyle fill:#3498db,stroke:#333,stroke-width:2px,color:#fff
    classDef analyticsStyle fill:#8e44ad,stroke:#333,stroke-width:2px,color:#fff
    classDef actionStyle fill:#27ae60,stroke:#333,stroke-width:2px,color:#fff
    
    class IOT,CAM,MIC,LOG sourceStyle
    class KAFKA,FLINK,SPARK streamStyle
    class CEP,ML,RULES analyticsStyle
    class ALERT,AUTO,DASH actionStyle
```

---

## 🔒 Security & Privacy Architecture

### 🛡️ Security Layers

```mermaid
graph TB
    subgraph "🔐 Authentication Layer"
        AUTH[Multi-Factor Authentication]
        RBAC[Role-Based Access Control]
        SSO[Single Sign-On]
    end
    
    subgraph "🔒 Encryption Layer"
        TLS[TLS 1.3 Transport]
        AES[AES-256 Data Encryption]
        PKI[PKI Certificate Management]
    end
    
    subgraph "🛡️ Network Security"
        FW[Firewall Rules]
        VPN[VPN Access]
        IDS[Intrusion Detection]
    end
    
    subgraph "📊 Audit & Compliance"
        LOG[Audit Logging]
        MONITOR[Security Monitoring]
        COMPLIANCE[Compliance Reporting]
    end
    
    AUTH --> TLS
    RBAC --> AES
    SSO --> PKI
    
    TLS --> FW
    AES --> VPN
    PKI --> IDS
    
    FW --> LOG
    VPN --> MONITOR
    IDS --> COMPLIANCE
    
    classDef authStyle fill:#e74c3c,stroke:#333,stroke-width:2px,color:#fff
    classDef encryptStyle fill:#f39c12,stroke:#333,stroke-width:2px,color:#fff
    classDef networkStyle fill:#9b59b6,stroke:#333,stroke-width:2px,color:#fff
    classDef auditStyle fill:#34495e,stroke:#333,stroke-width:2px,color:#fff
    
    class AUTH,RBAC,SSO authStyle
    class TLS,AES,PKI encryptStyle
    class FW,VPN,IDS networkStyle
    class LOG,MONITOR,COMPLIANCE auditStyle
```

---

*Developed following Turku UAS visual identity standards*
*© 2024 EXPLAINIUM Project - Professional Technical Documentation*
