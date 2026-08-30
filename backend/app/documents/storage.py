import re
import uuid
from pathlib import Path
from typing import Any, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from ..config import settings
from ..database.mongodb import db_manager
from ..utils.errors import StorageException


class LocalStorage:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self.root_path.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: bytes) -> str:
        safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(filename).name)
        path = self.root_path / f"{uuid.uuid4()}_{safe_name}"
        try:
            path.write_bytes(content)
        except OSError as error:
            raise StorageException("Unable to persist uploaded document.") from error
        return str(path)

    def resolve(self, storage_reference: str) -> str:
        path = Path(storage_reference)
        return str(path if path.is_absolute() else self.root_path / path)

    def delete(self, storage_reference: str) -> None:
        path = Path(self.resolve(storage_reference))
        try:
            if path.exists():
                path.unlink()
        except OSError as error:
            raise StorageException("Unable to remove stored document.") from error

    @staticmethod
    def _is_gridfs_reference(storage_reference: Optional[str]) -> bool:
        return bool(storage_reference and storage_reference.startswith("gridfs:"))

    @staticmethod
    def _gridfs_file_id(storage_reference: str) -> Any:
        raw_id = storage_reference.removeprefix("gridfs:")
        try:
            return ObjectId(raw_id)
        except Exception:
            return raw_id

    @staticmethod
    def _gridfs_bucket() -> AsyncIOMotorGridFSBucket:
        if not db_manager.is_connected or db_manager.db is None:
            raise StorageException("MongoDB is required for GridFS storage.")
        return AsyncIOMotorGridFSBucket(db_manager.db, bucket_name="document_files")

    async def save_document(
        self, filename: str, content: bytes, metadata: Optional[dict] = None
    ) -> str:
        """Persist source bytes in GridFS when MongoDB is available."""
        if db_manager.is_connected and db_manager.db is not None:
            file_id = await self._gridfs_bucket().upload_from_stream(
                filename, content, metadata=metadata or {}
            )
            return f"gridfs:{file_id}"
        return self.save(filename, content)

    async def read_document(self, storage_reference: str) -> bytes:
        """Read a source from GridFS or the legacy local fallback."""
        if self._is_gridfs_reference(storage_reference):
            stream = await self._gridfs_bucket().open_download_stream(
                self._gridfs_file_id(storage_reference)
            )
            return await stream.read()
        try:
            return Path(self.resolve(storage_reference)).read_bytes()
        except OSError as error:
            raise StorageException("Unable to read stored document.") from error

    async def delete_document(self, storage_reference: str) -> None:
        """Delete only the source object referenced by a document."""
        if self._is_gridfs_reference(storage_reference):
            await self._gridfs_bucket().delete(
                self._gridfs_file_id(storage_reference)
            )
            return
        self.delete(storage_reference)


def get_storage():
    if settings.STORAGE_PROVIDER.lower() != "local":
        raise StorageException(
            f"Unsupported storage provider: {settings.STORAGE_PROVIDER}"
        )
    return LocalStorage(settings.STORAGE_PATH)


storage = get_storage()