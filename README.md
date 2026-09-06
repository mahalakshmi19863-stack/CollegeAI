# CollegeAI
### AI-Powered College Knowledge Assistant

CollegeAI is a full-stack Retrieval-Augmented Generation (RAG) assistant designed to help students get reliable, verified answers to academic and campus inquiries. Instead of relying on general knowledge or unverified web searches, CollegeAI answers questions grounded strictly in official college documents—such as syllabi, academic regulations, notices, and policies—uploaded and managed by college administrators. Every response includes page-level source citations, along with strict anti-hallucination safeguards that refuse to answer when information is not present in the verified knowledge base.

---

## 🚀 Live Demo

- **Frontend Application (Vercel):** [https://temporary-instant-harp-tb08yqz.vercel.app](https://temporary-instant-harp-tb08yqz.vercel.app)
- **Backend API Service (Render):** [https://collegeai-1.onrender.com/api](https://collegeai-1.onrender.com/api)
- **API Health Check:** [https://collegeai-1.onrender.com/api/health](https://collegeai-1.onrender.com/api/health)

*The frontend is deployed on Vercel with automated static optimization, and the FastAPI backend runs on Render connected to a live MongoDB Atlas cloud database.*

---

## ✨ Key Features

- **Student Authentication & Portal**: Self-service student registration, login, session persistence, and profile management.
- **Role-Based Access Control (RBAC)**: Distinct permissions for `STUDENT` and `ADMIN` users with JWT token revocation on logout.
- **AI-Powered Question Answering**: Grounded responses synthesized from verified college records using Google Gemini and Atlas Vector Search.
- **Retrieval-Augmented Generation (RAG)**: Combines semantic vector similarity with keyword relevance to locate exact course and policy details.
- **Official Document Ingestion**: Admin upload support for **PDF**, **DOCX**, and **TXT** files with durable storage in MongoDB GridFS.
- **Precise Source & Page Citations**: Every generated response includes clickable source attribution cards displaying document titles and page numbers.
- **Anti-Hallucination Guardrails**: Out-of-scope or undocumented questions safely trigger a standard unavailable-information refusal with zero citations.
- **Interactive Conversation History**: Students can revisit prior conversation threads, review message history, and continue discussions.
- **Answer Quality Feedback**: One-click helpful / not-helpful feedback on assistant responses to monitor answer quality.
- **Admin Control Center**: Comprehensive dashboard showing ingestion status, document counts, query volume, and category analytics.
- **Document Lifecycle Management**: Administrators can upload, search, filter, toggle active versions, reprocess, or delete documents.
- **Responsive Modern UI**: Clean, accessible interface built with Next.js and Tailwind CSS for mobile and desktop screens.

---

## 🧠 How CollegeAI Works

```text
Student Question
       │
       ▼
[ Query Processing & Normalization ]
       │
       ▼
[ MongoDB Atlas Vector Search ] ──> Vector Index (768-dim Cosine Similarity)
       │
       ▼
[ Relevant Document Chunks ] ──> Filtered by Relevance & Active Version
       │
       ▼
[ Grounded Context Assembly ] ──> Strict Anti-Hallucination System Prompt
       │
       ▼
[ LLM Generation (Gemini 3.6 Flash) ] ──> Factual Synthesis from Context Only
       │
       ▼
Grounded Answer + Page-Level Source Citations
```

### Why RAG?
Standard large language models (LLMs) suffer from knowledge cutoffs and frequently generate plausible-sounding but incorrect details (hallucinations) about college-specific policies, course codes, and exam rules. CollegeAI uses Retrieval-Augmented Generation (RAG) to ensure the language model acts solely as a factual reader: it only answers using retrieved excerpts from official, administrator-verified documents, and transparently cites the exact document and page number for every claim.

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                 Next.js Frontend (Vercel)                   │
│  - Student Portal & Chat UI     - Admin Control Center      │
│  - Conversation Management       - Document Management & KPI │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / JSON API
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Render)                   │
│  - JWT & RBAC Middleware        - Documents & GridFS Service│
│  - RAG Retrieval Pipeline       - Feedback & Analytics      │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
       Database & Search                       │ Embeddings & LLM
               │                               │
               ▼                               ▼
┌──────────────────────────────┐ ┌─────────────────────────────┐
│     MongoDB Atlas Cluster    │ │        Google Gemini        │
│  - Users & Revoked Tokens    │ │  - gemini-embedding-001     │
│  - Documents & GridFS Files  │ │    (768 dimensions)         │
│  - Chunks & vector_index     │ │  - gemini-3.6-flash         │
│  - Conversations & Feedback  │ │    (Grounded Synthesis)     │
└──────────────────────────────┘ └─────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | **Next.js 14** (Pages Router), **React 18**, **TypeScript**, **Tailwind CSS**, **Zustand** (State Management), **Lucide React** (Icons), **Axios** |
| **Backend API** | **FastAPI**, **Python 3.11**, **Pydantic V2**, **Uvicorn**, **Motor / PyMongo**, **GridFS** (Durable Storage) |
| **Authentication & Security** | **JSON Web Tokens (JWT)** via `python-jose` (`HS256`), **BCrypt** password hashing, Token Revocation List |
| **AI & RAG Pipeline** | **Google GenAI SDK** (`gemini-3.6-flash`, `gemini-embedding-001`), **Atlas Vector Search**, Sliding-Window Chunker, Local Grounded Fallback |
| **Document Processing** | **pypdf** (PDF extraction & page tracking), **python-docx** (DOCX tables/paragraphs), Python standard library |
| **Database** | **MongoDB Atlas** (Cloud Database, Collections, GridFS Bucket, Atlas Vector Search Index) |
| **Cloud Deployment** | **Vercel** (Frontend static/edge hosting), **Render** (Backend Python web service), **MongoDB Atlas** |

---

## 📚 Document Intelligence

1. **Upload & Validation**: Administrators upload official college files via the admin portal. Files are validated against supported formats (`PDF`, `DOCX`, `TXT`) and size constraints (up to 20MB).
2. **Durable File Storage**: Raw documents are stored securely using MongoDB GridFS, ensuring persistence across ephemeral container restarts.
3. **Text Extraction & Cleaning**: Content is extracted page-by-page to preserve accurate page boundaries, header structures, and table layouts.
4. **Sliding-Window Chunking**: Cleaned text is segmented into overlapping chunks (`CHUNK_SIZE=800` characters, `CHUNK_OVERLAP=120` characters) to maintain semantic context across sentence boundaries.
5. **Embedding Generation**: Chunks are transformed into 768-dimension dense vector representations using `gemini-embedding-001`.
6. **Vector Search Indexing**: Vector representations and chunk metadata (page numbers, document IDs, categories, departments) are indexed in MongoDB Atlas using `vector_index`.
7. **Semantic Retrieval**: Incoming student queries are embedded and matched against active document chunks using cosine similarity vector search.
8. **Grounded Synthesis**: Retrieved candidate excerpts are assembled into a structured prompt enforcing strict factual boundaries. The LLM synthesizes the answer exclusively from provided text.
9. **Source Attribution**: The response is returned to the user alongside verified document names, snippet excerpts, and page references.

---

## 🛡️ Reliability & Safety

- **Relevance Filtering**: Retrieval evaluates candidate similarity scores. If no retrieved chunks meet the relevance threshold, generation is skipped.
- **Safe Unknown-Information Refusal**: When an inquiry asks for undocumented information (e.g. hostel fees or external topics not in the syllabus), CollegeAI responds with a standardized safe refusal message and cites zero sources.
- **Role-Based Authorization**: Administrative endpoints (`/api/admin/*` and document deletion) are strictly protected with HTTP 403 checks against unauthorized student tokens.
- **JWT Revocation**: Tokens are explicitly revoked in MongoDB on logout to prevent replay attacks.
- **Password Security**: All user passwords are encrypted using BCrypt with 12 salt rounds before database persistence.
- **Document Versioning**: Active version toggles and replacement flows allow administrators to publish updated regulations while archiving older editions.
- **Interrupted Job Recovery**: The backend automatically identifies and marks stale processing jobs as `FAILED` on service startup, preventing stuck pipelines.
- **Consistent Envelope Responses**: All API endpoints return a unified `{ "success": bool, "data": ..., "error": ... }` schema with descriptive error codes.

---

## 📊 Production Verification

The project has been tested and audited against the live production environment. Current verified results:

| Verification Target | Result | Status |
|---|:---:|---|
| **Backend Test Suite** | **47 / 47 Passed** | Full coverage of auth, extraction, chunking, embeddings, vector search, RAG, and admin APIs |
| **Frontend TypeScript** | **0 Errors** | Strict type-checking passed (`npx tsc --noEmit`) |
| **Next.js Production Build** | **Successful** | All 12 application routes compiled and optimized |
| **Localhost API Leakage** | **0 Occurrences** | Scanned production bundles; all API calls target `https://collegeai-1.onrender.com/api` |
| **3rd-Semester CSE Syllabus Ingestion** | **PROCESSED** | 59 pages extracted, 227 chunks indexed with 768-dim embeddings |
| **Curriculum Retrieval Quality** | **Verified** | Query *"What subjects are included in the 3rd semester CSE syllabus?"* returned all 9 curriculum subjects with 13 page citations |
| **Anti-Hallucination Safe Refusal** | **Verified** | Query *"What is the hostel fee?"* returned safe refusal with 0 sources |
| **Atlas Vector Search** | **Operational** | Live `$vectorSearch` index operational on MongoDB Atlas cluster |
| **Cross-Origin Resource Sharing (CORS)** | **Verified** | Render backend accepts preflight requests from the Vercel frontend |

---

## 👨‍💼 Admin Capabilities

The administrative portal allows designated college staff to govern the institutional knowledge base:

- **Overview Metrics**: Real-time summary cards for total documents, processed files, failed jobs, registered students, and student questions asked.
- **Document Ingestion**: Multi-file upload interface with category assignment (e.g., Academic, Examination, Admission, General), department tags, and version metadata.
- **Status Monitoring**: Visual badges indicating whether uploaded files are currently `PENDING`, `PROCESSING`, `PROCESSED`, or `FAILED` (with error details).
- **Active Version Controls**: One-click toggling of document active status to instantly include or exclude materials from student vector search results.
- **Document Deletion Protection**: Built-in confirmation modal safeguards against accidental deletion of live curriculum documents.
- **Knowledge Analytics**: Department and category distribution breakdown reflecting document coverage across the college.

---

## 🎓 Example Queries

| Inquiry | Expected Behavior |
|---|---|
| *"What subjects are included in the 3rd semester CSE syllabus?"* | Returns complete list of all 9 third-semester subjects and course codes, citing the relevant pages of the official scheme document. |
| *"What is the course code for Data Structures?"* | Identifies course code `1BCS305` and provides course objectives with page citations. |
| *"What topics are covered in Operating Systems?"* | Details syllabus modules and textbook references from the syllabus document. |
| *"How many credits does Digital Design and Computer Organization carry?"* | Extracts exact credit weightage (e.g., 4 credits) from the course structure table. |
| *"What is the hostel fee?"* | **Safe Refusal:** Because hostel fees are not contained in the academic syllabus, CollegeAI answers: *"I couldn't find this information in the available college documents."* and cites **0 sources**. |

---

## 🔐 Security

> [!CAUTION]
> **Never commit `.env` files, API keys, database credentials, JWT secrets, or private passwords to source control.**

- Server-side environment variables (`MONGODB_URI`, `JWT_SECRET`, `LLM_API_KEY`, `EMBEDDING_API_KEY`) must remain in backend deployment environments only.
- The Next.js frontend only exposes `NEXT_PUBLIC_API_URL` to the client browser.
- All database queries and search pipelines use parameterized inputs to prevent injection vulnerabilities.

---

## 💻 Local Development

### Prerequisites
- **Python 3.11+**
- **Node.js 18+** & **npm**
- **MongoDB Atlas account** (or local MongoDB instance)

### 1. Clone the Repository
```bash
git clone https://github.com/mahalakshmi19863-stack/CollegeAI.git
cd CollegeAI
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the project root:
```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=college_ai
JWT_SECRET=your-secure-random-jwt-secret-at-least-32-chars
PORT=8002

# Optional AI Providers (Defaults to deterministic local fallback if omitted)
LLM_PROVIDER=GEMINI
LLM_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-3.6-flash
EMBEDDING_PROVIDER=GEMINI
EMBEDDING_API_KEY=your_gemini_api_key
EMBEDDING_MODEL=gemini-embedding-001
```

Run the FastAPI backend:
```bash
# From repository root:
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8002 --reload
```
The interactive Swagger API documentation will be available at `http://localhost:8002/docs`.

### 3. Frontend Setup
In a new terminal window:
```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8002/api
```

Run the development server:
```bash
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 🧪 Testing

Run the automated test suite from the repository root:

```bash
# Set Python path to repository root
$env:PYTHONPATH = "."        # Windows PowerShell
export PYTHONPATH="."        # Linux / macOS

python -m pytest backend/tests -v
```

### What the Test Suite Covers
- **Authentication & RBAC**: Registration, login, invalid credentials rejection, logout token revocation, and role boundary enforcement.
- **Document Processing**: PDF/DOCX/TXT text extraction, whitespace normalization, page numbering preservation, and chunk overlap boundaries.
- **Embeddings & Vector Ranking**: Dense vector generation, 768-dimension validation, and cosine similarity ranking.
- **Acceptance RAG Scenarios**: Grounded factual answers, unknown-question zero-citation rejection, category separation, and active version rollover.
- **Conversations & Feedback**: Thread persistence, message ordering, feedback submissions, and user isolation.

---

## 📁 Project Structure

```text
CollegeAI/
├── backend/
│   ├── app/
│   │   ├── admin/          # Admin routes & analytics service
│   │   ├── auth/           # JWT, BCrypt, security dependencies, and RBAC
│   │   ├── chat/           # Chat routes, conversation & message storage
│   │   ├── database/       # MongoDB connection lifecycle & GridFS bucket
│   │   ├── documents/      # Upload, validation, lifecycle & storage engine
│   │   ├── feedback/       # Student answer rating routes and service
│   │   ├── models/         # Pydantic schemas (User, Document, Chunk, Chat)
│   │   ├── rag/            # Extraction, chunking, embeddings, retrieval & pipeline
│   │   ├── utils/          # Standard response envelopes and custom exceptions
│   │   ├── config.py       # Pydantic Settings & environment variables
│   │   └── main.py         # FastAPI application entrypoint & CORS middleware
│   ├── tests/              # 47 automated unit, integration, and acceptance tests
│   └── requirements.txt    # Backend Python dependencies
├── frontend/
│   ├── components/
│   │   ├── admin/          # DocumentTable, StatCard, DocumentUploadModal
│   │   ├── chat/           # MessageBubble, SourceCard, SuggestedQuestions, FeedbackModal
│   │   ├── common/         # Reusable UI elements (Badge, Modal, LoadingSpinner)
│   │   └── layout/         # Navigation bar and page shell
│   ├── pages/
│   │   ├── admin/          # /admin, /admin/documents, /admin/analytics
│   │   ├── chat/[id].tsx   # Active conversation view
│   │   ├── conversations.tsx# Conversation history list
│   │   ├── dashboard.tsx   # Student chat interface
│   │   ├── login.tsx       # User sign-in page
│   │   ├── register.tsx    # User registration page
│   │   └── index.tsx       # Public landing page
│   ├── services/           # Axios client & typed API endpoints
│   ├── store/              # Zustand stores (authStore, chatStore)
│   ├── styles/             # Global CSS and Tailwind configuration
│   └── types/              # TypeScript interface definitions
├── docs/                   # Architectural notes, API specifications & guides
├── .env.example            # Environment variables template
├── .gitignore              # Source control exclusion rules
├── README.md               # Project documentation
└── spec.md                 # Complete system requirements specification
```

---

## 🚀 Deployment

The production deployment consists of decoupled frontend and backend services:

- **Frontend → Vercel**: Connect the repository to Vercel, set the root directory to `frontend`, and configure `NEXT_PUBLIC_API_URL=https://collegeai-1.onrender.com/api`.
- **Backend → Render**: Deploy as a Python Web Service with root directory `backend`, start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, and configure server environment variables (`MONGODB_URI`, `JWT_SECRET`, `FRONTEND_URL`, Gemini keys).
- **Database → MongoDB Atlas**: Cloud-hosted MongoDB cluster running database `college_ai` with an active Atlas Search vector index (`vector_index`) on the `document_chunks` collection.
- **AI Models → Google Gemini**: Live generation via `gemini-3.6-flash` and dense embeddings via `gemini-embedding-001`.

---

## 📸 Screenshots

*Screenshots can be added to the showcase by placing images into a media folder and referencing them below:*

| Screen | Description |
|---|---|
| **Student Dashboard** | *[Screenshot Placeholder: Interactive student chat interface with suggested inquiry chips]* |
| **AI Chat & Source Citations** | *[Screenshot Placeholder: Grounded answer display with attached page citations]* |
| **Admin Overview Dashboard** | *[Screenshot Placeholder: Administrative metrics, student queries, and system status]* |
| **Document Management** | *[Screenshot Placeholder: Document table showing processing status, versions, and delete controls]* |
| **Knowledge Analytics** | *[Screenshot Placeholder: Category and department coverage charts]* |

---

## 👩‍💻 Author

- **GitHub Repository Owner:** [mahalakshmi19863](https://github.com/mahalakshmi19863)  
- **Repository:** [mahalakshmi19863-stack/CollegeAI](https://github.com/mahalakshmi19863-stack/CollegeAI)

---

## 📄 License

A software license has not yet been specified for this repository and can be added later.
