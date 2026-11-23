import pytest
from bson import ObjectId


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows

    async def to_list(self, length=None):
        return self.rows


@pytest.mark.asyncio
async def test_onboarding_directory_includes_employee_records_without_user_accounts(monkeypatch) -> None:
    from app.api.v1.routes.users import list_onboarding_employees
    from app.core import mongodb as mongodb_module

    employee_id = ObjectId()
    employees = [{
        "_id": employee_id,
        "vlinker": "Workbook Employee",
        "full_name": "Workbook Employee",
        "employee_id": None,
        "skill_set": "Python",
        "deleted_at": None,
    }]
    admin = {
        "_id": ObjectId(),
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "deleted_at": None,
    }
    onboarding = {
        "employee_id": str(employee_id),
        "primaryskill": "Python",
        "credential_status": "Pending",
        "bgv_status": "Pending",
        "vcf_status": "Pending",
        "onboarding_status": "Pending",
    }

    class FakeCollection:
        def __init__(self, name):
            self.name = name

        def find(self, *args, **kwargs):
            rows = {
                "users": [admin],
                "employees": employees,
                "onboarding_employees": [onboarding],
            }[self.name]
            return FakeCursor(rows)

        async def find_one(self, *args, **kwargs):
            return None

        async def update_one(self, *args, **kwargs):
            return None

    monkeypatch.setattr(mongodb_module.MongoDB, "get_collection", lambda name: FakeCollection(name))

    rows = await list_onboarding_employees()

    workbook_row = next(row for row in rows if row["employee"] == "Workbook Employee")
    admin_row = next(row for row in rows if row["employee"] == "Admin User")
    assert workbook_row["id"] == str(employee_id)
    assert workbook_row["employeeCode"] is None
    assert workbook_row["primarySkill"] == "Python"
    assert workbook_row["bgv"] == "Pending"
    assert admin_row["userId"] == str(admin["_id"])


@pytest.mark.asyncio
async def test_onboarding_detail_can_resolve_employee_without_user_account(monkeypatch) -> None:
    from app.api.v1.routes.users import get_onboarding_employee
    from app.core import mongodb as mongodb_module

    employee_id = ObjectId()
    employee = {
        "_id": employee_id,
        "vlinker": "Workbook Employee",
        "full_name": "Workbook Employee",
        "employee_id": None,
        "skill_set": "Python",
        "deleted_at": None,
    }
    onboarding = {
        "employee_id": str(employee_id),
        "primaryskill": "Python",
        "credential_status": "Pending",
        "bgv_status": "Pending",
        "vcf_status": "Pending",
        "onboarding_status": "Pending",
    }

    class FakeCollection:
        def __init__(self, name):
            self.name = name

        def find(self, *args, **kwargs):
            return FakeCursor([employee] if self.name == "employees" else [])

        async def find_one(self, query, *args, **kwargs):
            if self.name == "employees":
                return employee
            if self.name == "onboarding_employees":
                return onboarding
            return None

        async def update_one(self, *args, **kwargs):
            return None

    monkeypatch.setattr(mongodb_module.MongoDB, "get_collection", lambda name: FakeCollection(name))

    result = await get_onboarding_employee(str(employee_id))

    assert result["id"] == str(employee_id)
    assert result["employee"] == "Workbook Employee"
    assert result["employeeCode"] is None
    assert result["primarySkill"] == "Python"


@pytest.mark.asyncio
async def test_onboarding_milestones_can_be_updated_without_user_account(monkeypatch) -> None:
    from app.api.v1.routes.users import update_onboarding_employee
    from app.core import mongodb as mongodb_module

    employee_id = ObjectId()
    employee = {
        "_id": employee_id,
        "vlinker": "Workbook Employee",
        "full_name": "Workbook Employee",
        "employee_id": None,
        "skill_set": "Python",
        "deleted_at": None,
    }
    onboarding = {
        "employee_id": str(employee_id),
        "primaryskill": "Python",
        "credential_status": "Pending",
        "bgv_status": "Pending",
        "vcf_status": "Pending",
        "onboarding_status": "Pending",
    }
    updates = []

    class FakeCollection:
        def __init__(self, name):
            self.name = name

        def find(self, *args, **kwargs):
            return FakeCursor([employee] if self.name == "employees" else [])

        async def find_one(self, query, *args, **kwargs):
            if self.name == "employees":
                return employee
            if self.name == "onboarding_employees":
                return onboarding
            return None

        async def update_one(self, query, update, **kwargs):
            updates.append(update)
            return None

    monkeypatch.setattr(mongodb_module.MongoDB, "get_collection", lambda name: FakeCollection(name))

    await update_onboarding_employee(
        str(employee_id),
        {
            "tracking": [{
                "title": "Background Verification",
                "requestedDate": "2026-09-01",
                "status": "InProgress",
            }],
        },
        current_user={"email": "admin@example.com"},
    )

    milestone_update = next(update for update in updates if update.get("$set", {}).get("bgv_status"))
    assert milestone_update["$set"]["bgv_status"] == "InProgress"


@pytest.mark.asyncio
async def test_week0_tracker_resolves_employee_without_employee_code(monkeypatch) -> None:
    from app.api.v1.routes.week0 import _resolve_employee_ids
    from app.core import mongodb as mongodb_module

    user_id = ObjectId()
    employee_id = ObjectId()
    employee = {"_id": employee_id, "user_id": user_id, "employee_id": None}

    class FakeCollection:
        async def find_one(self, query, *args, **kwargs):
            return employee

    monkeypatch.setattr(mongodb_module.MongoDB, "get_collection", lambda name: FakeCollection())

    result = await _resolve_employee_ids(str(user_id))

    assert result == [str(employee_id), str(user_id)]
