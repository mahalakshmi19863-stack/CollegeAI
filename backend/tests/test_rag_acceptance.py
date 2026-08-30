import os
import tempfile
import pytest
from backend.app.rag.ingestion import ingestion_pipeline
from backend.app.rag.pipeline import rag_pipeline
from backend.app.rag.prompting import UNKNOWN_INFORMATION_MESSAGE
from backend.app.rag.vector_search import vector_search_engine
from backend.app.documents.service import document_service


@pytest.mark.asyncio
async def test_mandatory_rag_acceptance_1_known_query():
    """
    Mandatory Acceptance Test 1 (Spec Section 57):
    Upload doc: 'The college library is open from 8:00 AM to 8:00 PM on weekdays.'
    Ask: 'What are the library opening hours?'
    Expected: Grounded response + source attribution with document name.
    """
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("The college library is open from 8:00 AM to 8:00 PM on weekdays.")
        f_path = f.name

    try:
        # Ingest document
        doc_id = "test-doc-lib-01"
        success = await ingestion_pipeline.process_document(
            document_id=doc_id,
            file_path=f_path,
            file_type="TXT",
            document_name="Library Handbook 2026",
            category="Library",
            version=1,
        )
        assert success is True

        # Query RAG
        res = await rag_pipeline.generate_response("What are the library opening hours?")
        assert res["answer"] != UNKNOWN_INFORMATION_MESSAGE
        assert "8:00 AM" in res["answer"] or "8:00 PM" in res["answer"]
        assert len(res["sources"]) >= 1
        assert res["sources"][0].document_name == "Library Handbook 2026"
    finally:
        if os.path.exists(f_path):
            os.remove(f_path)


@pytest.mark.asyncio
async def test_mandatory_rag_acceptance_2_unknown_query_zero_hallucination():
    """
    Mandatory Acceptance Test 2 (Spec Section 58):
    Query: 'What is the monthly salary of the college principal?'
    Expected: System must NOT hallucinate an answer. Returns unavailable information message.
    """
    res = await rag_pipeline.generate_response("What is the monthly salary of the college principal?")
    assert res["answer"] == UNKNOWN_INFORMATION_MESSAGE
    assert len(res["sources"]) == 0


@pytest.mark.asyncio
async def test_mandatory_rag_acceptance_3_retrieval_accuracy_separation():
    """
    Mandatory Acceptance Test 3 (Spec Section 59):
    Doc A: 'Hostel fee is ₹50,000 per year.'
    Doc B: 'Library fee is ₹2,000 per year.'
    Ask: 'What is the hostel fee?'
    Expected: Hostel document is retrieved and cited; answer contains ₹50,000.
    """
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f_hostel:
        f_hostel.write("Hostel fee is ₹50,000 per year.")
        path_hostel = f_hostel.name

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f_lib:
        f_lib.write("Library fee is ₹2,000 per year.")
        path_lib = f_lib.name

    try:
        await ingestion_pipeline.process_document(
            document_id="doc-hostel-acc-3",
            file_path=path_hostel,
            file_type="TXT",
            document_name="Hostel Information 2026",
            category="Hostel",
            version=1,
        )

        await ingestion_pipeline.process_document(
            document_id="doc-lib-acc-3",
            file_path=path_lib,
            file_type="TXT",
            document_name="Library Fee Schedule 2026",
            category="Library",
            version=1,
        )

        res = await rag_pipeline.generate_response("What is the hostel fee?")
        assert res["answer"] != UNKNOWN_INFORMATION_MESSAGE
        assert "50,000" in res["answer"]
        assert len(res["sources"]) >= 1
        assert res["sources"][0].document_name == "Hostel Information 2026"
    finally:
        for p in [path_hostel, path_lib]:
            if os.path.exists(p):
                os.remove(p)


@pytest.mark.asyncio
async def test_mandatory_rag_acceptance_4_document_versioning():
    """
    Mandatory Acceptance Test 4 (Spec Section 60):
    v1: 'Hostel fee: ₹50,000' (Inactive)
    v2: 'Hostel fee: ₹55,000' (Active)
    Ask: 'What is the hostel fee?'
    Expected: Active v2 takes precedence (₹55,000).
    """
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f_v1:
        f_v1.write("Hostel fee: ₹50,000")
        path_v1 = f_v1.name

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f_v2:
        f_v2.write("Hostel fee: ₹55,000")
        path_v2 = f_v2.name

    try:
        # Ingest v1
        await ingestion_pipeline.process_document(
            document_id="doc-hostel-v1",
            file_path=path_v1,
            file_type="TXT",
            document_name="Hostel Handbook v1",
            category="Hostel",
            version=1,
        )
        # Mark v1 inactive
        vector_search_engine.set_memory_chunks_active("doc-hostel-v1", is_active=False)

        # Ingest v2 (Active)
        await ingestion_pipeline.process_document(
            document_id="doc-hostel-v2",
            file_path=path_v2,
            file_type="TXT",
            document_name="Hostel Handbook v2",
            category="Hostel",
            version=2,
        )

        res = await rag_pipeline.generate_response("What is the hostel fee?")
        assert res["answer"] != UNKNOWN_INFORMATION_MESSAGE
        assert "55,000" in res["answer"]
        assert res["sources"][0].document_name == "Hostel Handbook v2"
    finally:
        for p in [path_v1, path_v2]:
            if os.path.exists(p):
                os.remove(p)
