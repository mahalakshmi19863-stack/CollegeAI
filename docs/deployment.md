# Deployment

## Atlas

1. Create a MongoDB Atlas cluster and database user.
2. Allow the deployment host to connect through Atlas Network Access.
3. Use database `college_ai`.
4. Create/verify the `vector_index` mapping in [database.md](database.md).
5. Keep the URI out of source control and logs.

## Render Backend

Configure a Render Python web service with root directory `backend`:

```text
Build: pip install -r requirements.txt
Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Required environment variables:

```text
MONGODB_URI
MONGODB_DATABASE=college_ai
JWT_SECRET
FRONTEND_URL
```

For external generation, also set `LLM_PROVIDER`, `LLM_API_KEY`, and `LLM_MODEL` (currently `gemini-3.6-flash`). For external embeddings, set `EMBEDDING_PROVIDER`, `EMBEDDING_API_KEY`, and `EMBEDDING_MODEL` (currently `gemini-embedding-001`). Keys stay server-side. Gemini embedding requests are configured for 768 output dimensions to match Atlas.

For source-file storage, set `STORAGE_PROVIDER=local` and `STORAGE_PATH=./storage` for development. On Render, mount a persistent disk at the configured path before relying on files across restarts. The application currently has no S3/GCS provider; adding one requires a separate provider implementation and credentials.

Verify `GET /api/health` reports a connected database and confirm the mounted storage path is writable. Render's default local filesystem is ephemeral; configure a persistent disk or external object storage before relying on uploaded files across deploys or instances.

## Vercel Frontend

Configure a Next.js project with root directory `frontend` and set:

```text
NEXT_PUBLIC_API_URL=https://your-backend.example.com
```

`NEXT_PUBLIC_API_URL` is the only Vercel environment variable required for the frontend backend connection. The frontend uses its localhost API default only in development; production builds do not embed a localhost backend URL.

The backend `FRONTEND_URL` and CORS policy must allow the deployed frontend origin. Use HTTPS in deployed environments.

## Pre-deployment Checks

```powershell
$env:PYTHONPATH = "."
python -m pytest backend/tests -q
cd frontend
npm run build
```

Then manually verify registration, login/logout, admin upload, processing status, replacement/versioning, student chat, source cards, history, feedback, and an unknown question.

## Current Readiness Notes

Atlas connectivity, vector search, ingestion, fallback RAG, authentication, chat, and admin workflows have been validated in this workspace. Live Gemini generation requires a configured `GEMINI_API_KEY`; without it, the application intentionally uses the local grounded fallback. Durable production file storage and production-domain CORS must be configured for a public deployment.
