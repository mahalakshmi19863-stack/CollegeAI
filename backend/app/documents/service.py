import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from ..config import settings
from ..database.mongodb import db_manager
from ..models.document import (
    DocumentInDB,
    DocumentResponse,
    DocumentStatus,
    DocumentUpdate,
)
from ..rag.vector_search import vector_search_engine
from ..utils.errors import DocumentNotFoundException
from .storage import storage

# In-memory document storage fallback
_memory_documents: Dict[str, dict] = {}


def utc_now():
    return datetime.now(timezone.utc)


class DocumentService:
    @staticmethod
    def update_memory_document(doc_id: str, updates: dict):
        if doc_id in _memory_documents:
            _memory_documents[doc_id].update(updates)

    @classmethod
    async def create_document(
        cls,
        name: str,
        original_filename: str,
        file_type: str,
        file_size: int,
        storage_path: str,
        uploaded_by: str,
        category: str = "General",
        department: Optional[str] = "General",
        description: Optional[str] = None,
        version: int = 1,
    ) -> DocumentResponse:
        doc_id = str(uuid.uuid4())
        now = utc_now()

        doc_dict = {
            "_id": doc_id,
            "name": name,
            "original_filename": original_filename,
            "file_type": file_type.upper(),
            "file_size": file_size,
            "category": category,
            "department": department or "General",
            "description": description,
            "version": version,
            "status": DocumentStatus.UPLOADED.value,
            "storage_reference": storage_path,
            "uploaded_by": uploaded_by,
            "uploaded_at": now,
            "updated_at": now,
            "is_active": True,
            "processing_error": None,
            "chunk_count": 0,
            "total_pages": None,
        }

        if db_manager.is_connected and db_manager.documents is not None:
            older_versions = await db_manager.documents.find(
                {
                    "name": name,
                    "_id": {"$ne": doc_id},
                    "version": {"$lt": version},
                    "is_active": True,
                },
                {"_id": 1},
            ).to_list(length=500)
            older_ids = [item["_id"] for item in older_versions]
            if older_ids:
                await db_manager.documents.update_many(
                    {"_id": {"$in": older_ids}},
                    {"$set": {"is_active": False, "updated_at": now}},
                )
                await db_manager.document_chunks.update_many(
                    {"document_id": {"$in": older_ids}},
                    {"$set": {"is_active": False}},
                )
            await db_manager.documents.insert_one(doc_dict)
        else:
            for existing in _memory_documents.values():
                if (
                    existing.get("name") == name
                    and existing.get("version", 1) < version
                    and existing.get("is_active", True)
                ):
                    existing["is_active"] = False
                    existing["updated_at"] = now
                    vector_search_engine.set_memory_chunks_active(
                        existing["_id"], False
                    )
            _memory_documents[doc_id] = doc_dict

        return cls._to_response(doc_dict)

    @classmethod
    async def get_document_by_id(cls, doc_id: str) -> DocumentResponse:
        doc_dict = None
        if db_manager.is_connected and db_manager.documents is not None:
            doc_dict = await db_manager.documents.find_one({"_id": doc_id})
        else:
            doc_dict = _memory_documents.get(doc_id)

        if not doc_dict:
            raise DocumentNotFoundException(f"Document with ID {doc_id} not found.")

        return cls._to_response(doc_dict)

    @classmethod
    async def list_documents(
        cls,
        search: Optional[str] = None,
        category: Optional[str] = None,
        department: Optional[str] = None,
        status: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> List[DocumentResponse]:
        results: List[dict] = []

        if db_manager.is_connected and db_manager.documents is not None:
            query: dict = {}
            if category:
                query["category"] = category
            if department:
                query["department"] = department
            if status:
                query["status"] = status
            if is_active is not None:
                query["is_active"] = is_active
            if search:
                query["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"original_filename": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}},
                ]

            cursor = db_manager.documents.find(query).sort("uploaded_at", -1)
            results = await cursor.to_list(length=500)
        else:
            for doc in _memory_documents.values():
                if category and doc.get("category") != category:
                    continue
                if department and doc.get("department") != department:
                    continue
                if status and doc.get("status") != status:
                    continue
                if is_active is not None and doc.get("is_active") != is_active:
                    continue
                if search:
                    s_low = search.lower()
                    if (
                        s_low not in doc.get("name", "").lower()
                        and s_low not in doc.get("original_filename", "").lower()
                        and s_low not in (doc.get("description") or "").lower()
                    ):
                        continue
                results.append(doc)
            results.sort(key=lambda x: x.get("uploaded_at"), reverse=True)

        return [cls._to_response(d) for d in results]

    @classmethod
    async def update_document(
        cls, doc_id: str, updates: DocumentUpdate
    ) -> DocumentResponse:
        update_fields = {
            k: v for k, v in updates.model_dump(exclude_unset=True).items()
        }
        if not update_fields:
            return await cls.get_document_by_id(doc_id)

        update_fields["updated_at"] = utc_now()

        if db_manager.is_connected and db_manager.documents is not None:
            result = await db_manager.documents.find_one_and_update(
                {"_id": doc_id},
                {"$set": update_fields},
                return_document=True,
            )
            if not result:
                raise DocumentNotFoundException()
            if "is_active" in update_fields:
                await db_manager.document_chunks.update_many(
                    {"document_id": doc_id},
                    {"$set": {"is_active": update_fields["is_active"]}},
                )
                vector_search_engine.set_memory_chunks_active(
                    doc_id, update_fields["is_active"]
                )
            return cls._to_response(result)
        else:
            doc = _memory_documents.get(doc_id)
            if not doc:
                raise DocumentNotFoundException()
            doc.update(update_fields)
            if "is_active" in update_fields:
                vector_search_engine.set_memory_chunks_active(
                    doc_id, update_fields["is_active"]
                )
            return cls._to_response(doc)

    @classmethod
    async def delete_document(cls, doc_id: str) -> bool:
        doc = await cls.get_document_by_id(doc_id)

        storage_path = None
        if db_manager.is_connected and db_manager.documents is not None:
            stored_doc = await db_manager.documents.find_one({"_id": doc_id})
            storage_path = stored_doc.get("storage_reference") if stored_doc else None
        else:
            stored_doc = _memory_documents.get(doc_id)
            storage_path = stored_doc.get("storage_reference") if stored_doc else None

        if storage_path:
            try:
                storage.delete(storage_path)
            except Exception:
                pass

        if db_manager.is_connected and db_manager.documents is not None:
            await db_manager.documents.delete_one({"_id": doc_id})
            await db_manager.document_chunks.delete_many({"document_id": doc_id})
        else:
            _memory_documents.pop(doc_id, None)

        vector_search_engine.remove_memory_chunks_for_doc(doc_id)
        return True

    @staticmethod
    def _to_response(doc_dict: dict) -> DocumentResponse:
        return DocumentResponse(
            id=str(doc_dict.get("_id", doc_dict.get("id"))),
            name=doc_dict["name"],
            original_filename=doc_dict["original_filename"],
            file_type=doc_dict["file_type"],
            file_size=doc_dict["file_size"],
            storage_reference=doc_dict["storage_reference"],
            category=doc_dict.get("category", "General"),
            department=doc_dict.get("department", "General"),
            description=doc_dict.get("description"),
            version=doc_dict.get("version", 1),
            status=DocumentStatus(doc_dict.get("status", DocumentStatus.UPLOADED.value)),
            uploaded_by=doc_dict.get("uploaded_by", "Admin"),
            uploaded_at=doc_dict["uploaded_at"],
            updated_at=doc_dict.get("updated_at", doc_dict["uploaded_at"]),
            is_active=doc_dict.get("is_active", True),
            processing_error=doc_dict.get("processing_error"),
            chunk_count=doc_dict.get("chunk_count", 0),
            total_pages=doc_dict.get("total_pages"),
        )


document_service = DocumentService()
