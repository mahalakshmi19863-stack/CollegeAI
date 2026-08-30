from datetime import datetime, timezone
import uuid

import pytest
from httpx import AsyncClient

from backend.app.auth.security import create_access_token
from backend.app.auth.service import _memory_users
from backend.app.database.mongodb import db_manager
from backend.app.documents.service import _memory_documents, document_service
from backend.app.rag.vector_search import _memory_chunks


@pytest.fixture(autouse=True)
def reset_admin_stores():
    original_connected = db_manager.is_connected
    db_manager.is_connected = False
    _memory_users.clear()
    _memory_documents.clear()
    _memory_chunks.clear()
    yield
    _memory_users.clear()
    _memory_documents.clear()
    _memory_chunks.clear()
    db_manager.is_connected = original_connected


def auth_headers(role: str):
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    email = f"{role.lower()}@example.com"
    _memory_users[email] = {
        "_id": user_id,
        "name": role.title(),
        "email": email,
        "password_hash": "unused",
        "role": role,
        "created_at": now,
        "updated_at": now,
        "last_login": None,
    }
    return {"Authorization": f"Bearer {create_access_token(user_id, role)}"}


@pytest.mark.asyncio
async def test_newer_document_version_deactivates_previous_version(client: AsyncClient):
    admin = auth_headers("ADMIN")
    first = await document_service.create_document(
        name="Academic Calendar",
        original_filename="calendar-v1.txt",
        file_type="TXT",
        file_size=10,
        storage_path="",
        uploaded_by="Admin",
        version=1,
    )
    _memory_chunks.append({"_id": "old", "document_id": first.id, "is_active": True})
    second = await document_service.create_document(
        name="Academic Calendar",
        original_filename="calendar-v2.txt",
        file_type="TXT",
        file_size=10,
        storage_path="",
        uploaded_by="Admin",
        version=2,
    )

    assert second.version == 2
    assert _memory_documents[first.id]["is_active"] is False
    assert _memory_chunks[0]["is_active"] is False
    documents = await client.get("/api/documents", headers=admin)
    assert documents.status_code == 200
    assert [item["version"] for item in documents.json()["data"]] == [2, 1]


@pytest.mark.asyncio
async def test_student_cannot_access_admin_dashboard(client: AsyncClient):
    response = await client.get(
        "/api/admin/dashboard", headers=auth_headers("STUDENT")
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_replace_document_with_next_version(client: AsyncClient):
    admin = auth_headers("ADMIN")
    upload = await client.post(
        "/api/documents",
        headers=admin,
        files={"file": ("calendar-v1.txt", b"Old calendar", "text/plain")},
        data={"name": "Replaceable Calendar", "version": "1"},
    )
    assert upload.status_code == 200
    original_id = upload.json()["data"]["id"]

    replacement = await client.post(
        f"/api/documents/{original_id}/replace",
        headers=admin,
        files={"file": ("calendar-v2.txt", b"New calendar", "text/plain")},
    )
    assert replacement.status_code == 200
    assert replacement.json()["data"]["version"] == 2
    assert replacement.json()["data"]["name"] == "Replaceable Calendar"
    assert _memory_documents[original_id]["is_active"] is False
    await client.delete(
        f"/api/documents/{replacement.json()['data']['id']}", headers=admin
    )
    await client.delete(f"/api/documents/{original_id}", headers=admin)
