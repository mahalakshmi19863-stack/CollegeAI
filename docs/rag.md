# RAG Pipeline

## Ingestion

1. An administrator uploads PDF, DOCX, or TXT.
2. The file is validated and metadata is stored with `UPLOADED` status.
3. Background processing extracts text and page numbers.
4. Text is cleaned and split into overlapping 800-character chunks with 120-character overlap.
5. The configured embedding service creates one vector per chunk.
6. Chunks and metadata are persisted in `document_chunks`.
7. The document becomes `PROCESSED`, or `FAILED` with an error message.

PDF pages retain their source page number. DOCX paragraphs and table rows are preserved on page 1 because DOCX has no reliable page model in the current extractor. TXT files are treated as page 1.

## Retrieval and Generation

```text
Question
  -> query embedding
  -> Atlas $vectorSearch on vector_index
  -> active/category/department filters
  -> top-K candidates
  -> relevance threshold
  -> formatted source context
  -> grounded LLM prompt
  -> answer plus source/page metadata
```

The Atlas index uses `embedding` as a 768-dimensional cosine `knnVector` and token/number/boolean metadata mappings. The same configured embedding service is used for document chunks and queries. Retrieval returns candidate score, document, category, department, page, and content.

Only candidates at or above `RELEVANCE_THRESHOLD` (default `0.20`) become context. When no candidate qualifies, generation is skipped and the exact response below is returned:

> I couldn't find reliable information about this in the college knowledge base. Please try rephrasing your question or contact the college administration.

The system prompt identifies retrieved document context as the only source of college facts. Recent conversation turns may resolve references, but are explicitly not treated as factual evidence.

## Providers and Fallback

`LLM_PROVIDER` supports Gemini, OpenAI, or local fallback behavior. `EMBEDDING_PROVIDER` supports Gemini, OpenAI, or the deterministic local embedder. Provider exceptions fall back to grounded local synthesis. The local path returns text from retrieved chunks only; it does not bypass retrieval.
