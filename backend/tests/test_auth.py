import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "ok"
    assert "components" in data["data"]


@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient):
    # 1. Register student
    reg_payload = {
        "name": "Jane Doe",
        "email": "jane.doe@college.edu",
        "password": "Password123!",
        "role": "STUDENT",
    }
    reg_res = await client.post("/api/auth/register", json=reg_payload)
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert reg_data["success"] is True
    assert reg_data["data"]["email"] == "jane.doe@college.edu"

    # 2. Login
    login_payload = {
        "email": "jane.doe@college.edu",
        "password": "Password123!",
    }
    login_res = await client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["success"] is True
    token = login_data["data"]["access_token"]
    assert token is not None

    # 3. Access protected /me
    me_res = await client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["data"]["email"] == "jane.doe@college.edu"


@pytest.mark.asyncio
async def test_invalid_login_rejected(client: AsyncClient):
    payload = {
        "email": "nonexistent@college.edu",
        "password": "WrongPassword",
    }
    res = await client.post("/api/auth/login", json=payload)
    assert res.status_code == 401
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_public_registration_cannot_create_admin(client: AsyncClient):
    response = await client.post(
        "/api/auth/register",
        json={
            "name": "Requested Admin",
            "email": "requested.admin@college.edu",
            "password": "Password123!",
            "role": "ADMIN",
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["role"] == "STUDENT"


@pytest.mark.asyncio
async def test_student_cannot_access_admin_endpoint(client: AsyncClient):
    register_response = await client.post(
        "/api/auth/register",
        json={
            "name": "Student User",
            "email": "student.user@college.edu",
            "password": "Password123!",
        },
    )
    assert register_response.status_code == 200

    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "student.user@college.edu",
            "password": "Password123!",
        },
    )
    token = login_response.json()["data"]["access_token"]

    response = await client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_logout_revokes_token(client: AsyncClient):
    register_response = await client.post(
        "/api/auth/register",
        json={
            "name": "Logout User",
            "email": "logout.user@college.edu",
            "password": "Password123!",
        },
    )
    assert register_response.status_code == 200

    login_response = await client.post(
        "/api/auth/login",
        json={
            "email": "logout.user@college.edu",
            "password": "Password123!",
        },
    )
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    logout_response = await client.post("/api/auth/logout", headers=headers)
    assert logout_response.status_code == 200

    me_response = await client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 401
