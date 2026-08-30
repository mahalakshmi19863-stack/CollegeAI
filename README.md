# CollegeAI

CollegeAI is a full-stack college information assistant. It uses MongoDB Atlas Vector Search to retrieve official document chunks before producing a grounded answer. Supported uploads are PDF, DOCX, and TXT.

## Current Features

- Student registration, login, logout, JWT authentication, bcrypt password hashing, and role protection.
- Persistent conversations, message history, rename/delete controls, suggested questions, source cards, and answer feedback.
- Admin document upload, validation, search/filtering, processing status, update, replacement, versioning, reprocessing, and deletion.
- PDF page extraction, DOCX paragraph/table extraction, TXT decoding, text cleaning, page metadata, and overlapping chunking.
- Configurable Gemini or OpenAI embeddings/LLM providers with a deterministic local fallback.
- MongoDB Atlas persistence and a `vector_index` Atlas Search index on `document_chunks`.
- Configurable local persistent source-file storage through `STORAGE_PROVIDER` and `STORAGE_PATH`.
- Grounded context construction, relevance filtering, source/page attribution, and an unavailable-information response for weak retrieval.

## Architecture

```text
Frontend (Next.js)
    -> FastAPI REST API
       -> Auth, documents, chat, feedback, admin services
       -> Extraction -> chunking -> embeddings -> MongoDB Atlas
       -> Atlas $vectorSearch -> grounded prompt -> LLM or local fallback
```

Detailed design is in [docs/architecture.md](docs/architecture.md) and [docs/rag.md](docs/rag.md).

## Local Setup

Prerequisites: Python 3.11+ and Node.js 18+.

```powershell
cd backend
pip install -r requirements.txt
cd ..\frontend
npm install
```

Create a root `.env` with at least:

```env
MONGODB_URI=mongodb+srv://USERNAME:PASSWORD@CLUSTER/?retryWrites=true&w=majority
MONGODB_DATABASE=college_ai
JWT_SECRET=use-a-random-secret-at-least-32-characters
```

Optional provider settings are documented in [docs/deployment.md](docs/deployment.md). Never commit `.env` or expose provider keys to the frontend.

Run the backend from the repository root. The default configured port is `8002`.

```powershell
$env:PYTHONPATH = "."
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8002
```

Run the frontend separately:

```powershell
cd frontend
npm run dev
```

Set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` when the backend is not at its default URL.

## Verification

```powershell
$env:PYTHONPATH = "."
python -m pytest backend/tests -q
cd frontend
npm run build
```

The test suite covers authentication/RBAC, document lifecycle, extraction, chunking, embeddings, offline retrieval, grounded generation, conversations, feedback, versioning, and admin authorization. Live Atlas verification requires configured Atlas credentials and a ready `vector_index`; live Gemini verification additionally requires `GEMINI_API_KEY`.

See [docs/testing.md](docs/testing.md) for the acceptance flow and [docs/deployment.md](docs/deployment.md) for Render/Vercel deployment notes.
