# Architecture

## Runtime Flow

```text
Browser
  -> Next.js Pages Router and Zustand stores
  -> Axios API client with Bearer JWT
  -> FastAPI routes
  -> Domain services
  -> MongoDB Atlas / local in-memory fallback
```

The backend keeps routes thin. Auth, document, chat, feedback, and admin services own business operations. The RAG modules are separated into extraction, chunking, embeddings, vector search, retrieval, prompting, and pipeline orchestration.

## Frontend

The `frontend/` app contains student pages (`/dashboard`, `/conversations`, `/chat/[id]`) and admin pages (`/admin`, `/admin/documents`, `/admin/analytics`). `services/api.ts` centralizes HTTP calls and attaches the browser token. `Layout` protects frontend routes, while backend dependencies independently enforce authorization.

## Backend

- `auth/`: bcrypt password hashing, JWT creation/revocation, current-user lookup, and role checks.
- `documents/`: upload validation, metadata, replacement/versioning, status, and background ingestion.
- `rag/`: extraction, page-aware chunking, embedding generation, Atlas vector search, relevance filtering, grounded prompting, and fallback synthesis.
- `chat/`: user-scoped conversations and messages with retrieval metadata and sources.
- `feedback/`: validates that feedback targets the authenticated user's assistant message.
- `admin/`: dashboard counts and category/department analytics.
- `database/`: Motor connection, indexes, Atlas selection, and connection state.

## Storage

MongoDB Atlas is the configured production database. If connection fails and `MONGODB_USE_LOCAL_FALLBACK` is enabled, selected services use in-memory stores for local development and tests. The fallback does not replace Atlas when Atlas is connected.

Uploaded files use the configured storage provider. The current provider is local filesystem storage at `STORAGE_PATH` (default `./storage`), with sanitized generated filenames and the resulting path stored as `storage_reference` in MongoDB. A durable mounted volume or object-storage provider is required for a multi-instance deployment.
