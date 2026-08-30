import os
import sys
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.app.main import app
from backend.app.auth.security import create_access_token
from backend.app.rag.vector_search import _memory_chunks


@pytest_asyncio.fixture(autouse=True)
def reset_memory_stores():
    """Ensure in-memory vector search chunks and caches are isolated per test."""
    _memory_chunks.clear()
    yield
    _memory_chunks.clear()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
def student_auth_headers():
    token = create_access_token(subject="test-student-id", role="STUDENT")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
def admin_auth_headers():
    token = create_access_token(subject="test-admin-id", role="ADMIN")
    return {"Authorization": f"Bearer {token}"}
