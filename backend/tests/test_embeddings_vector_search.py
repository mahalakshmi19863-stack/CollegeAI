import pytest
import numpy as np
from backend.app.rag.embeddings import EmbeddingService, embedding_service
from backend.app.utils.errors import EmbeddingFailedException
from backend.app.rag.vector_search import cosine_similarity, vector_search_engine


@pytest.mark.asyncio
async def test_embedding_generation():
    texts = [
        "The college library is open from 8:00 AM to 8:00 PM on weekdays.",
        "Computer Science curriculum includes Artificial Intelligence and Data Structures.",
    ]
    embeddings = await embedding_service.embed_documents(texts)
    assert len(embeddings) == 2
    assert len(embeddings[0]) == embedding_service.dimension
    assert isinstance(embeddings[0][0], float)


@pytest.mark.asyncio
async def test_batch_embeddings_match_input_count_and_atlas_dimension():
    texts = ["Admissions deadline", "Scholarship eligibility"]

    embeddings = await embedding_service.embed_documents(texts)

    assert len(embeddings) == len(texts)
    assert all(len(embedding) == 768 for embedding in embeddings)
    assert all(np.isfinite(embedding).all() for embedding in embeddings)


def test_embedding_service_rejects_incompatible_provider_output():
    service = EmbeddingService()

    with pytest.raises(EmbeddingFailedException, match="expected 768"):
        service._validate_embeddings([[0.0] * 767])


def test_embedding_service_rejects_non_finite_provider_output():
    service = EmbeddingService()

    with pytest.raises(EmbeddingFailedException, match="non-finite"):
        service._validate_embeddings([[float("nan")] + [0.0] * 767])


@pytest.mark.asyncio
async def test_cosine_similarity_accuracy():
    # Same vector should have similarity 1.0
    v1 = [0.5, 0.5, 0.5, 0.5]
    sim = cosine_similarity(v1, v1)
    assert pytest.approx(sim, 0.001) == 1.0

    # Orthogonal vectors should have similarity 0.0
    v2 = [1.0, 0.0]
    v3 = [0.0, 1.0]
    sim_orth = cosine_similarity(v2, v3)
    assert pytest.approx(sim_orth, 0.001) == 0.0


@pytest.mark.asyncio
async def test_vector_search_ranking():
    doc1 = "The college library is open from 8:00 AM to 8:00 PM on weekdays."
    doc2 = "Hostel accommodation fee is ₹50,000 per year."

    emb1 = await embedding_service.embed_query(doc1)
    emb2 = await embedding_service.embed_query(doc2)

    chunk1 = {
        "_id": "c1",
        "document_id": "d1",
        "document_name": "Library Info",
        "document_version": 1,
        "content": doc1,
        "category": "Library",
        "embedding": emb1,
        "is_active": True,
    }
    chunk2 = {
        "_id": "c2",
        "document_id": "d2",
        "document_name": "Hostel Info",
        "document_version": 1,
        "content": doc2,
        "category": "Hostel",
        "embedding": emb2,
        "is_active": True,
    }

    vector_search_engine.register_memory_chunk(chunk1)
    vector_search_engine.register_memory_chunk(chunk2)

    query_emb = await embedding_service.embed_query("When does the library open?")
    results = await vector_search_engine.search(query_emb, top_k=2)

    assert len(results) >= 1
    # Library document should rank higher than hostel document
    assert results[0].document_name == "Library Info"
    assert results[0].score > 0.20


@pytest.mark.asyncio
async def test_vector_search_applies_metadata_filters():
    library_embedding = await embedding_service.embed_query("library hours")
    vector_search_engine.register_memory_chunk({
        "_id": "filtered-library",
        "document_id": "library-doc",
        "document_name": "Library Guide",
        "document_version": 1,
        "content": "Library hours are 8 AM to 8 PM.",
        "category": "Library",
        "department": "General",
        "embedding": library_embedding,
        "is_active": True,
    })
    vector_search_engine.register_memory_chunk({
        "_id": "filtered-hostel",
        "document_id": "hostel-doc",
        "document_name": "Hostel Guide",
        "document_version": 1,
        "content": "Hostel closes at 10 PM.",
        "category": "Hostel",
        "department": "General",
        "embedding": library_embedding,
        "is_active": True,
    })

    results = await vector_search_engine.search(
        library_embedding, top_k=5, category="Library"
    )

    assert [result.document_id for result in results] == ["library-doc"]
