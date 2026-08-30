from datetime import datetime, timezone
import logging
import os
import uuid
from typing import Optional
from ..config import settings
from ..database.mongodb import db_manager
from ..models.document import DocumentInDB, DocumentStatus
from .chunking import chunker
from .embeddings import embedding_service
from .extraction import extractor
from .vector_search import vector_search_engine

logger = logging.getLogger("college_ai.ingestion")


def utc_now():
    return datetime.now(timezone.utc)


class DocumentIngestionPipeline:
    async def process_document(
        self,
        document_id: str,
        file_path: str,
        file_type: str,
        document_name: str,
        category: str,
        department: Optional[str] = "General",
        version: int = 1,
    ) -> bool:
        """Process an uploaded document through the complete RAG ingestion pipeline."""
        logger.info(f"Starting ingestion for document {document_id} ({document_name})...")

        # 1. Update status to PROCESSING
        await self._update_document_status(
            document_id, DocumentStatus.PROCESSING
        )

        try:
            # 2. Extract text and page numbers
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found on disk at {file_path}")

            pages_content, total_pages = extractor.extract(file_path, file_type)
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

            # 4. Generate embeddings for all chunks in batch
            chunk_texts = [c.content for c in chunks]
            embeddings = await embedding_service.embed_documents(chunk_texts)

            if len(embeddings) != len(chunks):
                raise RuntimeError(
                    f"Mismatch between chunks count ({len(chunks)}) and embeddings count ({len(embeddings)})"
                )

            embedding_dimension = embedding_service.dimension
            if any(len(embedding) != embedding_dimension for embedding in embeddings):
                raise RuntimeError(
                    f"Embedding dimension must be {embedding_dimension} for Atlas Vector Search."
                )

            # 5. Prepare documents for MongoDB storage & memory index
            now = utc_now()
            chunk_records = []
            for i, chunk in enumerate(chunks):
                chunk_doc = {
                    "_id": chunk.id,
                    "document_id": document_id,
                    "document_name": document_name,
                    "document_version": version,
                    "content": chunk.content,
                    "chunk_index": chunk.chunk_index,
                    "page_number": chunk.page_number,
                    "category": category,
                    "department": department or "General",
                    "embedding": embeddings[i],
                    "is_active": True,
                    "created_at": now,
                }
                chunk_records.append(chunk_doc)
                vector_search_engine.register_memory_chunk(chunk_doc)

            # 6. Save chunks to MongoDB
            if db_manager.is_connected and db_manager.document_chunks is not None:
                await db_manager.document_chunks.delete_many(
                    {"document_id": document_id}
                )
                await db_manager.document_chunks.insert_many(chunk_records)

            # 7. Update document status to PROCESSED
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
            await self._update_document_status(
                document_id=document_id,
                status=DocumentStatus.FAILED,
                error_message=err_msg,
            )
            return False

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
            await db_manager.documents.update_one(
                {"_id": document_id}, {"$set": update_data}
            )

        from ..documents.service import document_service
        document_service.update_memory_document(document_id, update_data)


ingestion_pipeline = DocumentIngestionPipeline()
