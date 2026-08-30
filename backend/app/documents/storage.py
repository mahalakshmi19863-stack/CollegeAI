import re
import uuid
from pathlib import Path

from ..config import settings
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


def get_storage():
    if settings.STORAGE_PROVIDER.lower() != "local":
        raise StorageException(
            f"Unsupported storage provider: {settings.STORAGE_PROVIDER}"
        )
    return LocalStorage(settings.STORAGE_PATH)


storage = get_storage()