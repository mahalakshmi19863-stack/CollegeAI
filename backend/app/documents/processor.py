import asyncio
import logging
from ..rag.ingestion import ingestion_pipeline

logger = logging.getLogger("college_ai.processor")


async def process_document_background(
    document_id: str,
    file_path: str,
    file_type: str,
    document_name: str,
    category: str,
    department: str = "General",
    version: int = 1,
):
    """Background task wrapper for executing document ingestion."""
    try:
        await ingestion_pipeline.process_document(
            document_id=document_id,
            file_path=file_path,
            file_type=file_type,
            document_name=document_name,
            category=category,
            department=department,
            version=version,
        )
    except Exception as e:
        logger.error(
            f"Unhandled exception during background document processing: {e}"
        )
