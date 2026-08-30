import os
import uuid
from datetime import datetime, timezone

import pytest
from httpx import AsyncClient

from backend.app.auth.security import create_access_token, hash_password
from backend.app.auth.service import _memory_users
from backend.app.database.mongodb import db_manager
from backend.app.documents.service import _memory_documents
from backend.app.rag.vector_search import _memory_chunks


@pytest.fixture(autouse=True)
def reset_document_stores():
    original_connected = db_manager.is_connected
    db_manager.is_connected = False
    _memory_documents.clear()
    _memory_users.clear()
    _memory_chunks.clear()
    yield
    _memory_documents.clear()
    _memory_users.clear()
    _memory_chunks.clear()
    db_manager.is_connected = original_connected


@pytest.fixture
def admin_headers():
    user_id = str(uuid.uuid4())
    _memory_users["phase3.admin@college.edu"] = {
        "_id": user_id,
        "name": "Phase Three Admin",
        "email": "phase3.admin@college.edu",
        "password_hash": hash_password("Password123!"),
        "role": "ADMIN",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "last_login": None,
    }
    token = create_access_token(subject=user_id, role="ADMIN")
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_document_upload_validation_and_metadata_listing(
    client: AsyncClient, admin_headers
):
    invalid = await client.post(
        "/api/documents",
        headers=admin_headers,
        files={"file": ("notes.md", b"unsupported", "text/markdown")},
    )
    assert invalid.status_code == 400
    assert invalid.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"

    upload = await client.post(
        "/api/documents",
        headers=admin_headers,
        files={"file": ("library.txt", b"Library hours are 8 AM to 8 PM.", "text/plain")},
        data={
            "name": "Library Handbook",
            "category": "Library",
            "department": "General",
            "description": "Library access information",
            "version": "2",
        },
    )
    assert upload.status_code == 200
    document = upload.json()["data"]
    assert document["name"] == "Library Handbook"
    assert document["version"] == 2
    assert document["status"] == "UPLOADED"

    listed = await client.get(
        "/api/documents",
        headers=admin_headers,
        params={"search": "library", "status": "PROCESSED", "category": "Library"},
    )
    assert listed.status_code == 200
    listed_document = listed.json()["data"][0]
    assert listed_document["id"] == document["id"]
    assert listed_document["status"] == "PROCESSED"


@pytest.mark.asyncio
async def test_document_update_and_delete_remove_stored_file(
    client: AsyncClient, admin_headers
):
    upload = await client.post(
        "/api/documents",
        headers=admin_headers,
        files={"file": ("rules.txt", b"Campus rules.", "text/plain")},
    )
    assert upload.status_code == 200
    document = upload.json()["data"]
    document_id = document["id"]
    storage_path = _memory_documents[document_id]["storage_reference"]
    assert os.path.exists(storage_path)

    updated = await client.patch(
        f"/api/documents/{document_id}",
        headers=admin_headers,
        json={"description": "Updated rules", "is_active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["description"] == "Updated rules"
    assert updated.json()["data"]["is_active"] is False

    deleted = await client.delete(
        f"/api/documents/{document_id}", headers=admin_headers
    )
    assert deleted.status_code == 200
    assert document_id not in _memory_documents
    assert not os.path.exists(storage_path)
