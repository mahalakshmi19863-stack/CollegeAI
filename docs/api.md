# API Reference

All responses use `{ success, data, error }`. Protected routes require `Authorization: Bearer <JWT>`.

## Public

- `GET /api/health`: API, database, vector search, embedding, and LLM status.
- `POST /api/auth/register`: Create a student account. Public requests cannot create admin accounts.
- `POST /api/auth/login`: Return a JWT and user profile.

## Authentication

- `POST /api/auth/logout`: Revoke the presented JWT.
- `GET /api/auth/me`: Return the current user.

## Documents

Admin is required for upload, update, replacement, reprocess, and deletion. Authenticated users may list and view documents.

- `POST /api/documents`: Multipart upload with `file`, `name`, `category`, `department`, `description`, and `version`.
- `GET /api/documents`: List with `search`, `category`, `department`, `status`, and `is_active` filters.
- `GET /api/documents/{id}`: Read document metadata and status.
- `PATCH /api/documents/{id}`: Update metadata or active state.
- `POST /api/documents/{id}/replace`: Upload a new file as the next active version.
- `POST /api/documents/{id}/reprocess`: Run extraction and ingestion again.
- `DELETE /api/documents/{id}`: Delete metadata, stored file, and chunks.

Supported file types are PDF, DOCX, and TXT. Upload processing is asynchronous.

## Chat and Feedback

- `POST /api/chat`: Ask a question, optionally with `conversation_id`; returns answer, sources, page numbers, and retrieval statistics.
- `GET /api/conversations`: List the current user's conversations.
- `GET /api/conversations/{id}`: Read a user-scoped conversation and messages.
- `PATCH /api/conversations/{id}`: Rename a conversation.
- `DELETE /api/conversations/{id}`: Delete a conversation and messages.
- `POST /api/feedback`: Submit `helpful` or `not_helpful` feedback for the current user's assistant message.

## Admin

- `GET /api/admin/dashboard`: Document, processing, student, question, recent-upload, and feedback metrics.
- `GET /api/admin/analytics`: Category and department document counts plus dashboard metrics.

Interactive OpenAPI documentation is available at `/docs` when the backend is running.
