from datetime import datetime, timezone
import uuid

import pytest
from httpx import AsyncClient

from backend.app.auth.security import create_access_token
from backend.app.auth.service import _memory_users
from backend.app.chat.service import (
    _memory_conversations,
    _memory_messages,
    chat_service,
)
from backend.app.database.mongodb import db_manager
from backend.app.models.message import RetrievalStats, SourceItem
from backend.app.rag.pipeline import rag_pipeline
from backend.app.rag.vector_search import _memory_chunks
from backend.app.feedback.service import _memory_feedback


@pytest.fixture(autouse=True)
def reset_chat_stores():
    original_connected = db_manager.is_connected
    db_manager.is_connected = False
    _memory_users.clear()
    _memory_conversations.clear()
    _memory_messages.clear()
    _memory_feedback.clear()
    _memory_chunks.clear()
    yield
    _memory_users.clear()
    _memory_conversations.clear()
    _memory_messages.clear()
    _memory_feedback.clear()
    _memory_chunks.clear()
    db_manager.is_connected = original_connected


@pytest.fixture
def student_headers():
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    _memory_users["chat.student@college.edu"] = {
        "_id": user_id,
        "name": "Chat Student",
        "email": "chat.student@college.edu",
        "password_hash": "unused",
        "role": "STUDENT",
        "created_at": now,
        "updated_at": now,
        "last_login": None,
    }
    token = create_access_token(subject=user_id, role="STUDENT")
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_chat_persists_conversation_messages_and_feedback(
    client: AsyncClient, student_headers, monkeypatch
):
    async def fake_response(question, **kwargs):
        source = SourceItem(
            document_id="doc-1",
            document_name="Library Guide",
            page_number=2,
            relevance_score=0.9,
            category="Library",
            snippet="Library hours are 8 AM to 8 PM.",
        )
        return {
            "answer": "Library hours are 8 AM to 8 PM.",
            "sources": [source],
            "retrieval": RetrievalStats(chunks_retrieved=1, chunks_used=1),
        }

    monkeypatch.setattr(rag_pipeline, "generate_response", fake_response)
    response = await client.post(
        "/api/chat", headers=student_headers, json={"question": "Library hours?"}
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["answer"] == "Library hours are 8 AM to 8 PM."
    assert data["sources"][0]["page_number"] == 2
    assert len(_memory_conversations) == 1
    assert len(_memory_messages) == 2

    feedback = await client.post(
        "/api/feedback",
        headers=student_headers,
        json={"message_id": data["message_id"], "rating": "helpful"},
    )
    assert feedback.status_code == 200
    assert len(_memory_feedback) == 1


@pytest.mark.asyncio
async def test_feedback_rejects_unknown_or_other_users_messages(
    client: AsyncClient, student_headers
):
    unknown = await client.post(
        "/api/feedback",
        headers=student_headers,
        json={"message_id": "missing-message", "rating": "helpful"},
    )
    assert unknown.status_code == 404
    assert unknown.json()["error"]["code"] == "MESSAGE_NOT_FOUND"

    other_user_message = {
        "_id": "other-assistant-message",
        "conversation_id": "other-conversation",
        "user_id": "different-user",
        "role": "ASSISTANT",
        "content": "Private answer",
        "created_at": datetime.now(timezone.utc),
    }
    _memory_messages.append(other_user_message)
    forbidden_feedback = await client.post(
        "/api/feedback",
        headers=student_headers,
        json={
            "message_id": "other-assistant-message",
            "rating": "not_helpful",
        },
    )
    assert forbidden_feedback.status_code == 404
    assert len(_memory_feedback) == 0


@pytest.mark.asyncio
async def test_conversation_access_is_scoped_to_authenticated_user(
    client: AsyncClient, student_headers
):
    conversation = await chat_service.create_conversation("different-user")

    response = await client.get(
        f"/api/conversations/{conversation.id}", headers=student_headers
    )

    assert response.status_code == 404
