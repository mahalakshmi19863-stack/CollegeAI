from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from pymongo.errors import AutoReconnect

from backend.app.database.mongodb import db_manager
from backend.app.documents.service import _memory_documents, document_service
from backend.app.documents.storage import storage
from backend.app.models.document import DocumentStatus
from backend.app.rag.ingestion import ingestion_pipeline
from backend.app.rag.vector_search import _memory_chunks


class FakeDownloadStream:
    def __init__(self, content: bytes):
        self.content = content

    async def read(self):
        return self.content


class FakeGridFSBucket:
    def __init__(self):
        self.files = {}

    async def upload_from_stream(self, filename, content, metadata=None):
        self.files["file-1"] = content
        return "file-1"

    async def open_download_stream(self, file_id):
        return FakeDownloadStream(self.files[str(file_id)])

    async def delete(self, file_id):
        del self.files[str(file_id)]


class FakeDocumentsCollection:
    def __init__(self):
        self.last_query = None
        self.last_update = None

    async def update_one(self, query, update):
        self.last_query = query
        self.last_update = update

    async def update_many(self, query, update):
        self.last_query = query
        self.last_update = update
        return type("Result", (), {"modified_count": 1})()


class FakeChunkCollection:
    def __init__(self):
        self.bulk_write_calls = 0
        self.records = []

    async def delete_many(self, query):
        self.records.clear()

    async def bulk_write(self, operations, ordered=False):
        self.bulk_write_calls += 1
        if self.bulk_write_calls == 1:
            raise AutoReconnect("temporary connection closed")
        self.records.extend(operation._doc["$set"] for operation in operations)


@pytest.fixture(autouse=True)
def reset_stores():
    original_connected = db_manager.is_connected
    original_db = db_manager.db
    _memory_documents.clear()
    _memory_chunks.clear()
    yield
    _memory_documents.clear()
    _memory_chunks.clear()
    db_manager.is_connected = original_connected
    db_manager.db = original_db


@pytest.mark.asyncio
async def test_gridfs_source_round_trip_and_delete(monkeypatch):
    bucket = FakeGridFSBucket()
    db_manager.is_connected = True
    db_manager.db = object()
    monkeypatch.setattr(storage, "_gridfs_bucket", lambda: bucket)

    reference = await storage.save_document("syllabus.pdf", b"official syllabus")

    assert reference == "gridfs:file-1"
    assert await storage.read_document(reference) == b"official syllabus"
    await storage.delete_document(reference)
    assert bucket.files == {}


@pytest.mark.asyncio
async def test_ingestion_from_durable_source_creates_chunks_and_processes(monkeypatch):
    document = await document_service.create_document(
        name="CSE Syllabus",
        original_filename="syllabus.txt",
        file_type="TXT",
        file_size=31,
        storage_path="gridfs:file-1",
        uploaded_by="Admin",
        category="Academics",
        department="CSE",
    )
    monkeypatch.setattr(
        storage,
        "read_document",
        lambda reference: _async_bytes(b"3rd semester CSE subjects include Data Structures."),
    )

    success = await ingestion_pipeline.process_document(
        document_id=document.id,
        file_path=None,
        source_reference=document.storage_reference,
        file_type="TXT",
        document_name=document.name,
        category=document.category,
        department=document.department,
    )

    assert success is True
    assert _memory_documents[document.id]["status"] == DocumentStatus.PROCESSED.value
    assert _memory_documents[document.id]["chunk_count"] == 1
    assert _memory_chunks[0]["content"].startswith("3rd semester CSE")


@pytest.mark.asyncio
async def test_failed_ingestion_marks_document_failed_with_error():
    document = await document_service.create_document(
        name="Missing Source",
        original_filename="missing.txt",
        file_type="TXT",
        file_size=1,
        storage_path="missing-file.txt",
        uploaded_by="Admin",
    )

    success = await ingestion_pipeline.process_document(
        document_id=document.id,
        file_path="missing-file.txt",
        file_type="TXT",
        document_name=document.name,
        category=document.category,
    )

    assert success is False
    assert _memory_documents[document.id]["status"] == DocumentStatus.FAILED.value
    assert _memory_documents[document.id]["processing_error"]


@pytest.mark.asyncio
async def test_reprocessing_reads_durable_source(monkeypatch):
    document = await document_service.create_document(
        name="Reprocessable Syllabus",
        original_filename="syllabus.txt",
        file_type="TXT",
        file_size=20,
        storage_path="gridfs:file-1",
        uploaded_by="Admin",
    )
    references = []

    async def read_source(reference):
        references.append(reference)
        return b"CSE course scheme and subjects."

    monkeypatch.setattr(storage, "read_document", read_source)
    success = await ingestion_pipeline.process_document(
        document_id=document.id,
        file_path=None,
        source_reference=document.storage_reference,
        file_type="TXT",
        document_name=document.name,
        category=document.category,
    )

    assert success is True
    assert references == ["gridfs:file-1"]


@pytest.mark.asyncio
async def test_stale_processing_documents_are_marked_failed():
    documents = FakeDocumentsCollection()
    db_manager.is_connected = True
    db_manager.db = type("Database", (), {"documents": documents})()
    stale_before = datetime.now(timezone.utc) - timedelta(minutes=30)

    recovered = await document_service.recover_stale_processing_documents(stale_before)

    assert recovered == 1
    assert documents.last_query["status"] == DocumentStatus.PROCESSING.value
    assert documents.last_update["$set"]["status"] == DocumentStatus.FAILED.value


@pytest.mark.asyncio
async def test_large_ingestion_batches_embeddings_and_retries_mongodb_write(monkeypatch):
    documents = FakeDocumentsCollection()
    chunks_collection = FakeChunkCollection()
    db_manager.is_connected = True
    db_manager.db = type(
        "Database",
        (),
        {"documents": documents, "document_chunks": chunks_collection},
    )()
    monkeypatch.setattr("backend.app.rag.ingestion.settings.INGESTION_BATCH_SIZE", 2)
    embedding_batch_sizes = []

    async def fake_embed(texts):
        embedding_batch_sizes.append(len(texts))
        return [[0.1] * 768 for _ in texts]

    monkeypatch.setattr(
        "backend.app.rag.ingestion.embedding_service.embed_documents", fake_embed
    )
    monkeypatch.setattr("backend.app.rag.ingestion.asyncio.sleep", lambda _: _async_sleep())

    chunks = [
        SimpleNamespace(
            id=f"chunk-{index}",
            content=f"CSE subject {index}",
            chunk_index=index,
            page_number=index + 1,
        )
        for index in range(5)
    ]
    monkeypatch.setattr(
        "backend.app.rag.ingestion.chunker.chunk_document_pages",
        lambda **kwargs: chunks,
    )

    success = await ingestion_pipeline.process_document(
        document_id="large-doc",
        file_path=__file__,
        file_type="TXT",
        document_name="Large CSE Syllabus",
        category="Academics",
    )

    assert success is True
    assert embedding_batch_sizes == [2, 2, 1]
    assert chunks_collection.bulk_write_calls == 4
    assert len(chunks_collection.records) == 5
    assert documents.last_update["$set"]["status"] == DocumentStatus.PROCESSED.value


async def _async_bytes(content: bytes) -> bytes:
    return content


async def _async_sleep():
    return None