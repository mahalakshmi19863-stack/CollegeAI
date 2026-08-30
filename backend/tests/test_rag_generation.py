import pytest

from backend.app.models.message import RetrievalStats, SourceItem
from backend.app.models.chunk import ChunkSearchCandidate
from backend.app.rag.pipeline import RAGPipeline
from backend.app.rag.prompting import UNKNOWN_INFORMATION_MESSAGE
from backend.app.rag.retrieval import RetrievalResult


@pytest.mark.asyncio
async def test_generation_prompt_contains_retrieved_context_and_history(monkeypatch):
    candidate = ChunkSearchCandidate(
        chunk_id="chunk-1",
        document_id="doc-1",
        document_name="Library Handbook",
        document_version=1,
        page_number=4,
        category="Library",
        department="General",
        content="The library is open from 8 AM to 8 PM.",
        score=0.91,
    )
    retrieval = RetrievalResult(
        candidates=[candidate],
        relevant_candidates=[candidate],
        sources=[
            SourceItem(
                document_id="doc-1",
                document_name="Library Handbook",
                page_number=4,
                relevance_score=0.91,
                category="Library",
                department="General",
                snippet=candidate.content,
            )
        ],
        formatted_context="--- [SOURCE: Library Handbook (Page 4)] ---\nThe library is open from 8 AM to 8 PM.",
        stats=RetrievalStats(chunks_retrieved=1, chunks_used=1),
    )
    captured = {}
    pipeline = RAGPipeline()

    async def fake_retrieve(**kwargs):
        return retrieval

    async def fake_gemini(prompt):
        captured["prompt"] = prompt
        return "The library is open from 8 AM to 8 PM."

    monkeypatch.setattr("backend.app.rag.pipeline.retrieval_service.retrieve", fake_retrieve)
    monkeypatch.setattr(pipeline, "_call_gemini", fake_gemini)
    pipeline.provider = "GEMINI"
    pipeline.api_key = "test-only"

    result = await pipeline.generate_response(
        "When is the library open?",
        conversation_context="USER: Tell me about campus facilities.",
    )

    assert "Library Handbook" in captured["prompt"]
    assert "The library is open from 8 AM to 8 PM." in captured["prompt"]
    assert "campus facilities" in captured["prompt"]
    assert result["answer"] == "The library is open from 8 AM to 8 PM."
    assert result["sources"][0].document_id == candidate.document_id
    assert result["sources"][0].document_name == candidate.document_name
    assert result["sources"][0].page_number == candidate.page_number


@pytest.mark.asyncio
async def test_generation_falls_back_to_retrieved_facts_when_llm_fails(monkeypatch):
    candidate = ChunkSearchCandidate(
        chunk_id="chunk-2",
        document_id="doc-2",
        document_name="Hostel Handbook",
        document_version=1,
        page_number=8,
        category="Hostel",
        department="General",
        content="The annual hostel fee is INR 50,000.",
        score=0.88,
    )
    retrieval = RetrievalResult(
        candidates=[candidate],
        relevant_candidates=[candidate],
        sources=[
            SourceItem(
                document_id="doc-2",
                document_name="Hostel Handbook",
                page_number=8,
                relevance_score=0.88,
                category="Hostel",
                department="General",
                snippet=candidate.content,
            )
        ],
        formatted_context="Hostel Handbook (Page 8): The annual hostel fee is INR 50,000.",
        stats=RetrievalStats(chunks_retrieved=1, chunks_used=1),
    )

    async def fake_retrieve(**kwargs):
        return retrieval

    async def failed_generation(prompt):
        raise RuntimeError("provider unavailable")

    pipeline = RAGPipeline()
    monkeypatch.setattr("backend.app.rag.pipeline.retrieval_service.retrieve", fake_retrieve)
    monkeypatch.setattr(pipeline, "_call_gemini", failed_generation)
    pipeline.provider = "GEMINI"
    pipeline.api_key = "test-only"

    result = await pipeline.generate_response("What is the hostel fee?")

    assert result["answer"] == "The annual hostel fee is INR 50,000."
    assert result["sources"][0].document_name == "Hostel Handbook"


@pytest.mark.asyncio
async def test_generation_rejects_missing_relevant_context(monkeypatch):
    retrieval = RetrievalResult(
        candidates=[],
        relevant_candidates=[],
        sources=[],
        formatted_context="",
        stats=RetrievalStats(),
    )
    called = False

    async def fake_retrieve(**kwargs):
        return retrieval

    async def fake_generation(prompt):
        nonlocal called
        called = True
        return "unsupported answer"

    pipeline = RAGPipeline()
    monkeypatch.setattr("backend.app.rag.pipeline.retrieval_service.retrieve", fake_retrieve)
    monkeypatch.setattr(pipeline, "_call_gemini", fake_generation)
    pipeline.provider = "GEMINI"
    pipeline.api_key = "test-only"

    result = await pipeline.generate_response("What is the principal salary?")

    assert result["answer"] == UNKNOWN_INFORMATION_MESSAGE
    assert result["sources"] == []
    assert called is False