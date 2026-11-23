from datetime import date, timedelta

import pytest
from bson import ObjectId
from httpx import AsyncClient

from app.auth.handlers import generate_token_pair
from app.core.security import hash_password
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/users",
        json={
            "email": "newuser@example.com",
            "password": "securepass123",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient) -> None:
    payload = {"email": "duplicate@example.com", "password": "securepass123"}
    first = await client.post("/api/v1/users", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/users", json=payload)
    assert second.status_code == 409


@pytest.mark.asyncio
async def test_create_user_weak_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/users",
        json={"email": "weakpass@example.com", "password": "short"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, db_session) -> None:
    repo = UserRepository(db_session)
    user = await repo.create(
        email="me_test@example.com",
        hashed_password=hash_password("securepass123"),
        full_name="Me Test",
        is_active=True,
    )
    await db_session.commit()

    tokens = generate_token_pair(str(user.id))
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {tokens.access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me_test@example.com"


@pytest.mark.asyncio
async def test_get_current_user_unauthenticated(client: AsyncClient) -> None:
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient, db_session) -> None:
    repo = UserRepository(db_session)
    user = await repo.create(
        email="get_by_id@example.com",
        hashed_password=hash_password("securepass123"),
        full_name="Get By ID",
        is_active=True,
    )
    await db_session.commit()

    tokens = generate_token_pair(str(user.id))
    response = await client.get(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {tokens.access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == str(user.id)


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, db_session) -> None:
    repo = UserRepository(db_session)
    user = await repo.create(
        email="update_test@example.com",
        hashed_password=hash_password("securepass123"),
        full_name="Before Update",
        is_active=True,
    )
    await db_session.commit()

    tokens = generate_token_pair(str(user.id))
    response = await client.patch(
        f"/api/v1/users/{user.id}",
        json={"full_name": "After Update"},
        headers={"Authorization": f"Bearer {tokens.access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["full_name"] == "After Update"


@pytest.mark.asyncio
async def test_patch_onboarding_employee_allows_pending_item_with_older_completed_date(monkeypatch) -> None:
    from app.api.v1.routes.users import update_onboarding_employee
    from app.core import mongodb as mongodb_module

    user_id = str(ObjectId())
    user = {
        "_id": ObjectId(user_id),
        "email": "employee@example.com",
        "first_name": "Test",
        "last_name": "User",
        "deleted_at": None,
    }
    employee = {
        "_id": ObjectId(),
        "user_id": ObjectId(user_id),
        "employee_id": "EMP-202",
        "email": "employee@example.com",
        "email_id": "employee@example.com",
        "full_name": "Test User",
        "deleted_at": None,
    }

    class FakeCollection:
        def __init__(self, name):
            self.name = name

        async def find_one(self, query, *args, **kwargs):
            if self.name == "users":
                return user
            if self.name == "employees":
                return employee
            if self.name == "onboarding_employees":
                return {"employee_id": "EMP-202"}
            return None

        async def update_one(self, *args, **kwargs):
            return None

    monkeypatch.setattr(mongodb_module.MongoDB, "get_collection", lambda name: FakeCollection(name))

    async def fake_get_onboarding_employee(*args, **kwargs):
        return {
            "id": user_id,
            "employee": "Test User",
            "employeeCode": "EMP-202",
            "email": "employee@example.com",
            "tracking": [],
            "status": "Pending",
            "remarks": "",
        }

    monkeypatch.setattr("app.api.v1.routes.users.get_onboarding_employee", fake_get_onboarding_employee)

    response = await update_onboarding_employee(
        user_id,
        {
            "status": "Pending",
            "tracking": [
                {
                    "title": "Background Verification",
                    "requestedDate": "2024-06-10",
                    "completedDate": "2024-06-08",
                    "status": "Pending",
                }
            ],
        },
        current_user={"email": "admin@example.com"},
    )

    assert response["status"] == "Pending"


@pytest.mark.asyncio
async def test_get_onboarding_employee_accepts_employee_code(monkeypatch) -> None:
    from app.api.v1.routes.users import get_onboarding_employee
    from app.core import mongodb as mongodb_module

    user_id = str(ObjectId())
    user = {
        "_id": ObjectId(user_id),
        "email": "employee@example.com",
        "first_name": "Test",
        "last_name": "User",
        "deleted_at": None,
        "is_active": True,
    }
    employee = {
        "_id": ObjectId(),
        "user_id": ObjectId(user_id),
        "employee_id": "VIPL001492",
        "email": "employee@example.com",
        "email_id": "employee@example.com",
        "full_name": "Test User",
        "deleted_at": None,
    }
    onboarding = {
        "employee_id": "VIPL001492",
        "primaryskill": "Java",
        "bgv_status": "Pending",
        "vcf_status": "Pending",
        "credential_status": "Pending",
        "onboarding_status": "Pending",
        "remarks": "",
    }

    class FakeCursor:
        def __init__(self, rows):
            self.rows = rows

        async def to_list(self, length=None):
            return self.rows

    class FakeCollection:
        def __init__(self, name):
            self.name = name

        def find(self, *args, **kwargs):
            if self.name == "employees":
                return FakeCursor([employee])
            if self.name == "onboarding_employees":
                return FakeCursor([onboarding])
            return FakeCursor([])

        async def find_one(self, query, *args, **kwargs):
            if self.name == "users":
                if query.get("_id") == ObjectId(user_id):
                    return user
                if query.get("email") == "employee@example.com":
                    return user
                return None
            if self.name == "employees":
                if query.get("employee_id") == "VIPL001492":
                    return employee
                if query.get("user_id") == user_id:
                    return employee
                if query.get("email") == "employee@example.com":
                    return employee
                if query.get("email_id") == "employee@example.com":
                    return employee
                return employee
            if self.name == "onboarding_employees":
                return onboarding
            return None

        async def update_one(self, *args, **kwargs):
            return None

    monkeypatch.setattr(mongodb_module.MongoDB, "get_collection", lambda name: FakeCollection(name))

    response = await get_onboarding_employee("VIPL001492", {"email": "admin@example.com"})

    assert response["employeeCode"] == "VIPL001492"
    assert response["employee"] == "Test User"
    assert response["primarySkill"] == "Java"


@pytest.mark.asyncio
async def test_get_onboarding_metrics_uses_rag_counts_for_bgv_vcf_and_client_credentials(monkeypatch) -> None:
    from app.api.v1.routes.users import get_onboarding_metrics
    from app.core import mongodb as mongodb_module

    today = date.today()
    green_date = (today - timedelta(days=10)).isoformat()
    amber_date = (today - timedelta(days=24)).isoformat()
    red_date = (today - timedelta(days=45)).isoformat()

    class FakeCollection:
        def __init__(self, name):
            self.name = name

        async def find(self, *args, **kwargs):
            if self.name == "onboarding_employees":
                return FakeCursor([
                    {
                        "employee_id": "EMP-1",
                        "bgv_initiated_date": green_date,
                        "bgv_status": "Completed",
                        "vcf_sent_date": green_date,
                        "vcf_status": "Completed",
                        "credential_requested_date": green_date,
                        "credential_status": "Completed",
                        "onboarding_status": "Completed",
                    },
                    {
                        "employee_id": "EMP-2",
                        "bgv_initiated_date": amber_date,
                        "bgv_status": "InProgress",
                        "vcf_sent_date": amber_date,
                        "vcf_status": "InProgress",
                        "credential_requested_date": amber_date,
                        "credential_status": "InProgress",
                        "onboarding_status": "InProgress",
                    },
                    {
                        "employee_id": "EMP-3",
                        "bgv_initiated_date": red_date,
                        "bgv_status": "Pending",
                        "vcf_sent_date": red_date,
                        "vcf_status": "Pending",
                        "credential_requested_date": red_date,
                        "credential_status": "Pending",
                        "onboarding_status": "Pending",
                    },
                ])
            return FakeCursor([])

    class FakeCursor:
        def __init__(self, rows):
            self.rows = rows

        async def to_list(self, length=None):
            return self.rows

    monkeypatch.setattr(mongodb_module.MongoDB, "get_collection", lambda name: FakeCollection(name))

    response = await get_onboarding_metrics({"email": "admin@example.com"})

    assert response["bgv"]["Green"] == 1
    assert response["bgv"]["Amber"] == 1
    assert response["bgv"]["Red"] == 1
    assert response["vcf"] == response["bgv"]
    assert response["clientCredentials"] == response["vcf"]
    assert response["onboardedEmployees"]["Completed"] == 1


@pytest.mark.asyncio
async def test_send_onboarding_bgv_completion_email_uses_onboarding_status(monkeypatch) -> None:
    from app.api.v1.routes.users import send_onboarding_bgv_completion_email
    from app.core import mongodb as mongodb_module

    user_id = str(ObjectId())
    user = {
        "_id": ObjectId(user_id),
        "email": "employee@example.com",
        "first_name": "Test",
        "last_name": "User",
        "deleted_at": None,
    }
    employee = {
        "_id": ObjectId(),
        "user_id": ObjectId(user_id),
        "employee_id": "EMP-101",
        "email": "employee@example.com",
        "email_id": "employee@example.com",
        "full_name": "Test User",
        "team_lead": "Manager One",
        "account_manager": "Account Manager",
        "deleted_at": None,
    }
    onboarding = {
        "employee_id": "EMP-101",
        "bgv_status": "Completed",
    }

    class FakeCursor:
        def __init__(self, rows):
            self.rows = rows

        async def to_list(self, length=None):
            return self.rows

    class FakeCollection:
        def __init__(self, name):
            self.name = name

        def find(self, *args, **kwargs):
            if self.name == "employees":
                return FakeCursor([employee])
            if self.name == "onboarding_employees":
                return FakeCursor([onboarding])
            return FakeCursor([])

        async def find_one(self, query, *args, **kwargs):
            if self.name == "users":
                return user
            if self.name == "employees":
                if query.get("full_name") == "Manager One":
                    return {"full_name": "Manager One", "email": "manager@example.com"}
                if query.get("full_name") == "Account Manager":
                    return {"full_name": "Account Manager", "email_id": "account@example.com"}
                return employee
            if self.name == "onboarding_employees":
                return onboarding
            return None

    monkeypatch.setattr(mongodb_module.MongoDB, "get_collection", lambda name: FakeCollection(name))

    sent = {}

    def fake_send_bgv_completion_email(**kwargs):
        sent.update(kwargs)
        return {"status": "queued"}

    monkeypatch.setattr("app.api.v1.routes.users.send_bgv_completion_email", fake_send_bgv_completion_email)

    result = await send_onboarding_bgv_completion_email(user_id)

    assert result.message == "BGV completion email queued successfully"
    assert sent["to_email"] == "employee@example.com"
    assert sent["cc"] == ["manager@example.com", "account@example.com"]
