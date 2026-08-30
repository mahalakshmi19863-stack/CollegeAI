from datetime import datetime, timezone
import asyncio
import logging
import os
import tempfile
import uuid
from typing import Optional
from pymongo.errors import (
    AutoReconnect,
    ConnectionFailure,
    NetworkTimeout,
    ServerSelectionTimeoutError,
    WaitQueueTimeoutError,
)
from pymongo import UpdateOne
from ..config import settings
from ..database.mongodb import db_manager
from ..models.document import DocumentInDB, DocumentStatus
from ..documents.storage import storage
from .chunking import chunker
from .embeddings import embedding_service
from .extraction import extractor
from .vector_search import vector_search_engine

logger = logging.getLogger("college_ai.ingestion")

TRANSIENT_MONGO_ERRORS = (
    AutoReconnect,
    ConnectionFailure,
    NetworkTimeout,
    ServerSelectionTimeoutError,
    WaitQueueTimeoutError,
)


def utc_now():
    return datetime.now(timezone.utc)


class DocumentIngestionPipeline:
    @staticmethod
    async def _retry_mongo_operation(operation, description: str):
        for attempt in range(3):
            try:
                return await operation()
            except TRANSIENT_MONGO_ERRORS:
                if attempt == 2:
                    raise
                delay = 2**attempt
                logger.warning(
                    "Transient MongoDB error during %s; retrying in %ss.",
                    description,
                    delay,
                )
                await asyncio.sleep(delay)

    async def process_document(
        self,
        document_id: str,
        file_path: Optional[str],
        file_type: str,
        document_name: str,
        category: str,
        department: Optional[str] = "General",
        version: int = 1,
        source_reference: Optional[str] = None,
    ) -> bool:
        """Process an uploaded document through the complete RAG ingestion pipeline."""
        logger.info(f"Starting ingestion for document {document_id} ({document_name})...")

        # 1. Update status to PROCESSING
        temporary_path = None
        try:
            await self._update_document_status(
                document_id, DocumentStatus.PROCESSING
            )

            # 2. Extract text and page numbers
            extraction_path = file_path
            if source_reference:
                source_bytes = await storage.read_document(source_reference)
                suffix = f".{file_type.lower().lstrip('.') }"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temporary_file:
                    temporary_file.write(source_bytes)
                    temporary_path = temporary_file.name
                extraction_path = temporary_path

            if not extraction_path or not os.path.exists(extraction_path):
                raise FileNotFoundError(
                    f"Stored document is unavailable: {source_reference or file_path}"
                )

            pages_content, total_pages = extractor.extract(extraction_path, file_type)
            if not pages_content:
                raise ValueError("No extractable text found in the document.")

            # 3. Chunk text preserving page numbers & metadata
            chunks = chunker.chunk_document_pages(
                pages_content=pages_content,
                document_id=document_id,
                document_name=document_name,
                document_version=version,
                category=category,
                department=department,
            )
            if not chunks:
                raise ValueError("Chunking produced 0 chunks.")

            embedding_dimension = embedding_service.dimension
            # 4. Replace old indexed chunks, then process bounded batches.
            if db_manager.is_connected and db_manager.document_chunks is not None:
                await self._retry_mongo_operation(
                    lambda: db_manager.document_chunks.delete_many(
                        {"document_id": document_id}
                    ),
                    "removing previous document chunks",
                )

            now = utc_now()
            processed_chunks = 0
            batch_size = max(1, settings.INGESTION_BATCH_SIZE)
            for start in range(0, len(chunks), batch_size):
                chunk_batch = chunks[start : start + batch_size]
                embeddings = await embedding_service.embed_documents(
                    [chunk.content for chunk in chunk_batch]
                )
                if len(embeddings) != len(chunk_batch):
                    raise RuntimeError(
                        f"Mismatch between chunks count ({len(chunk_batch)}) and embeddings count ({len(embeddings)})"
                    )
                if any(len(embedding) != embedding_dimension for embedding in embeddings):
                    raise RuntimeError(
                        f"Embedding dimension must be {embedding_dimension} for Atlas Vector Search."
                    )

                chunk_records = [
                    {
                        "_id": chunk.id,
                        "document_id": document_id,
                        "document_name": document_name,
                        "document_version": version,
                        "content": chunk.content,
                        "chunk_index": chunk.chunk_index,
                        "page_number": chunk.page_number,
                        "category": category,
                        "department": department or "General",
                        "embedding": embedding,
                        "is_active": True,
                        "created_at": now,
                    }
                    for chunk, embedding in zip(chunk_batch, embeddings)
                ]

                if db_manager.is_connected and db_manager.document_chunks is not None:
                    operations = [
                        UpdateOne(
                            {"_id": record["_id"]},
                            {"$set": record},
                            upsert=True,
                        )
                        for record in chunk_records
                    ]
                    await self._retry_mongo_operation(
                        lambda: db_manager.document_chunks.bulk_write(operations, ordered=False),
                        f"inserting chunk batch {start // batch_size + 1}",
                    )
                for chunk_doc in chunk_records:
                    vector_search_engine.register_memory_chunk(chunk_doc)
                processed_chunks += len(chunk_records)
                await self._update_document_status(
                    document_id=document_id,
                    status=DocumentStatus.PROCESSING,
                    chunk_count=processed_chunks,
                )

            # 5. Update document status to PROCESSED
            await self._update_document_status(
                document_id=document_id,
                status=DocumentStatus.PROCESSED,
                chunk_count=len(chunks),
                total_pages=total_pages,
            )

            logger.info(
                f"Successfully processed document {document_id}: {len(chunks)} chunks embedded and indexed."
            )
            return True

        except Exception as e:
            err_msg = str(e)
            logger.error(f"Ingestion failed for document {document_id}: {err_msg}")
            if temporary_path and os.path.exists(temporary_path):
                os.unlink(temporary_path)
            await self._update_document_status(
                document_id=document_id,
                status=DocumentStatus.FAILED,
                error_message=err_msg,
            )
            return False
        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.unlink(temporary_path)

    async def _update_document_status(
        self,
        document_id: str,
        status: DocumentStatus,
        error_message: Optional[str] = None,
        chunk_count: int = 0,
        total_pages: Optional[int] = None,
    ):
        """Update the document state in MongoDB and/or memory store."""
        update_data = {
            "status": status.value,
            "updated_at": utc_now(),
            "processing_error": error_message,
        }
        if chunk_count > 0:
            update_data["chunk_count"] = chunk_count
        if total_pages is not None:
            update_data["total_pages"] = total_pages

        if db_manager.is_connected and db_manager.documents is not None:
            await self._retry_mongo_operation(
                lambda: db_manager.documents.update_one(
                    {"_id": document_id}, {"$set": update_data}
                ),
                f"updating status for document {document_id}",
            )

        from ..documents.service import document_service
        document_service.update_memory_document(document_id, update_data)


ingestion_pipeline = DocumentIngestionPipeline()
