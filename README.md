# AI-Powered Intelligent Document Management and Question Answering System Using Retrieval-Augmented Generation (RAG)

An enterprise-grade Document Management System (DMS) integrated with a Retrieval-Augmented Generation (RAG) conversational pipeline, fully compliant with **Review - I Project Report** and **Review - II Report** software engineering specifications.

---

## 🏛️ System Architecture

The application is structured into an N-tier layered architectural design pattern enforcing separation of concerns across presentation, orchestration/API, persistence, and cognitive services:

1. **Presentation Layer (Streamlit - Port 8501)**
   - Built in Python using Streamlit with `st.session_state` management.
   - Dynamic tab navigation between **Personal Documents** and **Public Documents**.
   - Dual-layout selector: **List View** vs. **Card / Grid View**.
   - Document upload drawer with format detection (PDF, DOCX, TXT), size check (max 25MB), and mandatory visibility classification (`PERSONAL` vs. `PUBLIC`).
   - Reactive chat window with multi-turn conversation support, session switching, "➕ New Chat", and semantic search scope radio selector (**Private Search** [default], **Public Search**, **Combined Search**).
   - Verifiable source citations with interactive badges and direct document download links.
   - Dedicated **Administrator Dashboard** for user oversight and telemetry metrics.

2. **Application & Orchestration Tier (FastAPI - Port 8000)**
   - Asynchronous REST endpoints with Pydantic v2 schemas and automatic OpenAPI documentation (`/docs`).
   - Secure credential verification with bcrypt password hashing and JWT access tokens.
   - Automated ingestion pipeline: file validation, text extraction via Factory Pattern, recursive chunking (800-character window with 150-character overlap), and vector embedding generation.
   - Synchronized Document-Vector Controller for atomic cascade deletion and vector re-indexing.

3. **Relational Persistence Layer (SQLite 3 via aiosqlite)**
   - ACID-compliant relational persistence for users, document metadata, file paths, and conversation logs.
   - Performance indexing:
     - `idx_docs_owner_vis ON documents(owner_id, visibility)`
     - `idx_messages_session ON chat_messages(session_id, timestamp)`

4. **Vector Persistence Layer (ChromaDB)**
   - In-process HNSW cosine distance vector store (`enterprise_knowledge_base`).
   - 1536-dimensional embeddings with scalar metadata filtering (`document_uuid`, `owner_id`, `visibility`, `chunk_index`, `filename`).

5. **Cognitive Cloud Layer (OpenAI API / Grounded Fallback)**
   - Supports OpenAI `text-embedding-3-small` (1536 dims) and `gpt-4o`.
   - Includes local deterministic dense embedding and strict-context synthesis fallback for offline/local execution.

---

## 🧩 Architectural Design Patterns Applied

| Design Pattern | Implementation in Codebase |
|---|---|
| **Factory Pattern** | `ParserFactory` dynamically instantiates `PDFParser`, `DocxParser`, or `PlainTextParser` based on file extension. |
| **Strategy Pattern** | `PrivateSearchStrategy`, `PublicSearchStrategy`, and `CombinedSearchStrategy` encapsulate ChromaDB metadata queries dynamically at runtime. |
| **Singleton Pattern** | `EmbeddingService` and `ChromaService` maintain persistent single connections across the application lifecycle. |
| **Observer / Sync Hook** | `VectorSyncService` executes atomic vector purges on document deletion and re-indexing upon file modification. |
| **Repository / Service Separation** | Clean decoupling of API routers, service business logic, and SQLAlchemy ORM models. |

---

## 📂 Project Directory Structure

```text
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py               # JWT auth & Admin RBAC dependencies
│   │   │   └── routers/
│   │   │       ├── admin.py          # Admin stats & user oversight endpoints
│   │   │       ├── auth.py           # Register, login, me endpoints
│   │   │       ├── chat.py           # Multi-turn chat & RAG query endpoints
│   │   │       └── documents.py      # Upload, download, CRUD & sync endpoints
│   │   ├── core/
│   │   │   ├── config.py             # System configuration & environment settings
│   │   │   ├── database.py           # Async SQLAlchemy engine & table initializers
│   │   │   └── security.py           # Bcrypt hashing & JWT token issuance
│   │   ├── models/
│   │   │   ├── models.py             # SQLAlchemy models (User, Document, ChatSession, ChatMessage)
│   │   │   └── schemas.py            # Pydantic v2 schemas
│   │   ├── services/
│   │   │   ├── chroma_service.py     # ChromaDB vector store wrapper
│   │   │   ├── chunker.py            # Recursive text chunker (800 window / 150 overlap)
│   │   │   ├── embedding_service.py  # 1536-dim embedding service (OpenAI / fallback)
│   │   │   ├── parser_factory.py     # Factory pattern parsers (PDF, DOCX, TXT)
│   │   │   ├── rag_service.py        # RAG query engine & search filter strategies
│   │   │   └── sync_service.py       # Vector sync service (cascade deletion & re-indexing)
│   │   └── main.py                   # FastAPI application entrypoint
├── frontend/
│   ├── api_client.py                 # REST client for backend API communication
│   └── app.py                        # Streamlit presentation tier
├── tests/
│   ├── conftest.py                   # Async test fixtures with test DB
│   └── test_system.py                # Full verification test suite
├── uploads/                          # Stored document binaries
├── data/                             # SQLite DB and ChromaDB data directories
├── requirements.txt                  # Python dependencies
├── run.py                            # Unified startup runner
├── start_backend.bat                 # Windows backend launcher
├── start_frontend.bat                # Windows frontend launcher
└── README.md
```

---

## 🧪 Verification & Test Results (Table 5.2 Conformance)

The automated test suite (`pytest tests/ -v`) executes 12 comprehensive unit and integration test cases with a **100% pass rate**:

| Test ID | Test Scenario | Expected Result | Status |
|---|---|---|---|
| **TC-SEC-01** | Personal Document Isolation in Private Search | User B querying User A's private doc returns 0 chunks and grounded fallback message. | ✅ **PASS** |
| **TC-SEC-02** | Public Search Scope Restriction | Public search query retrieves only public chunks; private documents are strictly excluded. | ✅ **PASS** |
| **TC-SYNC-01** | Cascade Vector Purge on Deletion | Deleting document removes binary, SQLite row, and purges all ChromaDB vector chunks. | ✅ **PASS** |
| **TC-SYNC-02** | Vector Re-indexing on Content Update | Updating document purges old vectors, re-chunks new text, and re-indexes in ChromaDB. | ✅ **PASS** |
| **TC-RAG-01** | Verifiable Citation Generation | Grounded answer contains source document metadata and functional download URL. | ✅ **PASS** |
| **TC-VAL-01** | Unsupported File Rejection | Uploading `.exe` is rejected with HTTP 422 and clear validation error message. | ✅ **PASS** |
| **UNIT-01** | Recursive Text Chunker Boundaries | Recursive boundary splitting on `\n\n`, `\n`, `. ` respects 800-char window & 150 overlap. | ✅ **PASS** |
| **UNIT-02** | Recursive Text Chunker Empty Input | Empty/whitespace text handled gracefully without raising errors. | ✅ **PASS** |
| **UNIT-03** | Bcrypt Password Hashing & Verification | Passwords securely salted, hashed, and verified. | ✅ **PASS** |
| **UNIT-04** | JWT Token Lifecycle | Token creation, payload encoding, and decoding verified. | ✅ **PASS** |
| **UNIT-05** | Parser Factory Mime Routing | Dedicated parser resolved correctly for `.pdf`, `.docx`, `.txt`, rejecting unsupported formats. | ✅ **PASS** |
| **INTEG-01**| User Registration & Login Flow | Complete user lifecycle from signup to authenticated `/me` verified. | ✅ **PASS** |

---

## 🚀 Getting Started

### 1. Pre-configured Seed Accounts
The system automatically initializes SQLite on first run and seeds the following test accounts:
- **Administrator**: `admin@example.com` / `admin123` (Access to Document Manager, RAG Chat, and Admin Dashboard)
- **Standard User**: `user@example.com` / `user123` (Access to Personal/Public Documents and RAG Chat)

### 2. Optional OpenAI Configuration
To use live OpenAI GPT-4o and text-embedding-3-small, set your API key:
```powershell
$env:OPENAI_API_KEY="sk-..."
```
*(If no API key is provided, the system functions seamlessly using local deterministic 1536-dim embeddings and grounded extraction synthesis).*

### 3. Launching the System

#### Option A: Unified Launcher
```powershell
python run.py
```
This starts both the FastAPI backend on `http://127.0.0.1:8000` and the Streamlit frontend on `http://localhost:8501`.

#### Option B: Independent Terminals
**Terminal 1 (Backend):**
```powershell
.\start_backend.bat
# or
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 (Frontend):**
```powershell
.\start_frontend.bat
# or
python -m streamlit run frontend\app.py --server.port 8501
```

### 4. Running Automated Tests
```powershell
pytest tests/ -v
```
