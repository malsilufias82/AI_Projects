import pytest
from httpx import AsyncClient

from app.core.security import hash_password
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session) -> None:
    repo = UserRepository(db_session)
    await repo.create(
        email="login_test@example.com",
        hashed_password=hash_password("securepass123"),
        full_name="Login Test",
        is_active=True,
    )
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login_test@example.com", "password": "securepass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, db_session) -> None:
    repo = UserRepository(db_session)
    await repo.create(
        email="wrong_pass@example.com",
        hashed_password=hash_password("correctpass123"),
        full_name="Wrong Pass User",
        is_active=True,
    )
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrong_pass@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "anypassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, db_session) -> None:
    repo = UserRepository(db_session)
    await repo.create(
        email="refresh_test@example.com",
        hashed_password=hash_password("securepass123"),
        full_name="Refresh Test",
        is_active=True,
    )
    await db_session.commit()

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "refresh_test@example.com", "password": "securepass123"},
    )
    assert login_resp.status_code == 200
    refresh_token = login_resp.json()["refresh_token"]

    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json()


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "totally.invalid.token"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out."
