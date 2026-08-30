# Testing

## Automated Suite

Run from the repository root:

```powershell
$env:PYTHONPATH = "."
python -m pytest backend/tests -q
```

The suite covers:

- Registration, login, invalid credentials, JWT revocation, RBAC, and protected routes.
- PDF/DOCX/TXT extraction, cleaning, page metadata, table extraction, and chunking.
- Batch embeddings, 768-dimension validation, finite vectors, and offline vector ranking.
- Document upload validation, metadata, status, search/filtering, update, deletion, and stored-file cleanup.
- Atlas-compatible retrieval filters and grounded prompt context injection.
- Mandatory RAG known, unknown, category separation, and versioning acceptance behavior.
- Conversation/message persistence, source metadata, feedback ownership, and conversation isolation.
- Admin dashboard authorization, analytics access, version rollover, and replacement.

## Mandatory RAG Acceptance Cases

1. A library-hours document produces an answer and cites its document/page.
2. An undocumented principal-salary question returns the exact unavailable-information message with zero sources.
3. Hostel and library fee documents remain separated by semantic retrieval.
4. An active newer version takes precedence over an inactive older version.

## Frontend

```powershell
cd frontend
npm run build
```

This runs Next.js linting, TypeScript validation, compilation, and static page generation.

## Live Atlas Verification

Use temporary records only. Verify:

1. Atlas health reports `connected`.
2. Upload processing reaches `PROCESSED`.
3. `document_chunks` contains a 768-value embedding and page metadata.
4. A real `$vectorSearch` using `vector_index` returns the relevant chunk.
5. Grounded output contains the retrieved fact and matching source/page.
6. Unknown output has zero sources.
7. Delete all temporary users, documents, chunks, messages, feedback, and files.

Atlas Search is eventually consistent after writes, so live checks should poll for a bounded period before declaring retrieval failure.

## External LLM Status

Do not claim live Gemini verification unless `GEMINI_API_KEY` is configured and a real request succeeds. Without the key, report fallback verification separately. API keys and MongoDB credentials must never be printed in test output.
