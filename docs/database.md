# Database

The configured database is MongoDB Atlas database `college_ai`. Collections are initialized by `backend/app/database/mongodb.py`.

## Collections

- `users`: UUID, name, normalized email, bcrypt hash, role, timestamps, last login.
- `documents`: filename, type, size, category, department, description, version, status, storage reference, uploader, active flag, processing error, chunk/page counts. `storage_reference` points to the configured storage provider's file.
- `document_chunks`: document metadata, content, chunk index, page number, embedding, active flag, timestamp.
- `conversations`: UUID, owner user ID, title, created/updated timestamps.
- `messages`: conversation/user IDs, USER or ASSISTANT role, content, sources, retrieval metadata, timestamp.
- `feedback`: message ID, user ID, rating, optional comment, timestamp.
- `revoked_tokens`: JWT `jti` and `expires_at`; the TTL index removes expired revocations.

## Indexes

The application creates indexes for user email/role, document status/category/active/time, chunk document/category/active, conversation owner/time, message conversation/user, feedback message/user, and revoked-token `jti`/expiry.

## Atlas Vector Search

The existing `vector_index` is on `document_chunks` with this effective mapping:

```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "embedding": {"type": "knnVector", "dimensions": 768, "similarity": "cosine"},
      "document_id": {"type": "token"},
      "document_version": {"type": "number"},
      "department": {"type": "token"},
      "category": {"type": "token"},
      "page_number": {"type": "number"},
      "is_active": {"type": "boolean"}
    }
  }
}
```

The application filters active chunks and optionally category/department during `$vectorSearch`. Do not change vector dimensions or embedding space without rebuilding the index and re-embedding all chunks.
