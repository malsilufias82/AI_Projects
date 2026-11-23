from typing import Any, List, Dict, Optional
from datetime import date, datetime, timezone
import re
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.auth.dependencies import get_current_user, require_permission
from app.core.exceptions import NotFoundException
from app.core.logging import get_logger
from app.core.mongodb import MongoDB
from app.models.mongo_employee import Employee
from app.models.mongo_user import User
from app.schemas.base import MessageResponse, PaginatedResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.bgvcompletion import send_bgv_completion_email
from app.services.clientcredential import send_client_credential_email
from app.services.mongo_employee_service import MongoEmployeeService
from app.services.mongo_user_service import MongoUserService

router = APIRouter()
logger = get_logger(__name__)

def _mongo_id_values(entity_id: str) -> List[object]:
    values: List[object] = [entity_id]
    if ObjectId.is_valid(entity_id):
        values.append(ObjectId(entity_id))
    return values

async def ensure_employee_onboarding_records(employees_collection, onboarding_collection) -> None:
    """Ensure each active employee has a corresponding onboarding record."""
    employees = await employees_collection.find(
        {"$or": [{"deleted_at": None}, {"deleted_at": {"$exists": False}}]},
        {"employee_id": 1, "full_name": 1, "email": 1, "email_id": 1, "user_id": 1, "skill_set": 1},
    ).to_list(length=None)
    if not employees:
        return

    employee_ids = [employee.get("employee_id") for employee in employees if employee.get("employee_id")]
    if not employee_ids:
        return

    existing = await onboarding_collection.find(
        {"employee_id": {"$in": employee_ids}},
        {"employee_id": 1},
    ).to_list(length=None)
    existing_ids = {record.get("employee_id") for record in existing if record.get("employee_id")}

    for employee in employees:
        employee_id = employee.get("employee_id")
        if not employee_id:
            continue

        primary_skill = str(employee.get("skill_set") or "").strip()

        if employee_id in existing_ids:
            if primary_skill:
                await onboarding_collection.update_one(
                    {"employee_id": employee_id},
                    {"$set": {"primaryskill": primary_skill}},
                )
            continue

        onboard_payload = {
            "employee_id": employee_id,
            "credential_status": "Pending",
            "bgv_status": "Pending",
            "vcf_status": "Pending",
            "onboarding_status": "Pending",
            "remarks": "",
            "created_at": datetime.now(timezone.utc),
            "created_by": "system",
        }
        if primary_skill:
            onboard_payload["primaryskill"] = primary_skill

        await onboarding_collection.update_one(
            {"employee_id": employee_id},
            {
                "$setOnInsert": onboard_payload,
                "$set": {"primaryskill": primary_skill} if primary_skill else {},
            },
            upsert=True,
        )
        existing_ids.add(employee_id)


class UserProfileResponse(BaseModel):
    """User profile response combining user and employee data"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    team_lead: Optional[str] = None
    position: Optional[str] = None
    pillar: Optional[str] = None
    client: Optional[str] = None
    project: Optional[str] = None


class UserProfileUpdate(BaseModel):
    """User profile update request"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None


class UserPermissionCreate(BaseModel):
    user_id: str
    permission_id: str


class UserRoleCreate(BaseModel):
    user_id: str
    role_id: str


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
) -> UserResponse:
    payload = data.model_dump(exclude_unset=True)
    create_fields = set(UserCreate.model_fields)
    user_fields = create_fields.intersection(User.model_fields)
    employee_fields = create_fields.intersection(Employee.model_fields) - user_fields
    employee_data = {
        key: payload.pop(key)
        for key in employee_fields
        if key in payload
    }

    user_service = MongoUserService()
    user_dict = await user_service.create_user(UserCreate.model_validate(payload))

    # Persist employee attributes independently. Roll back the user insert if
    # the employee record cannot be saved, avoiding a partially-created pair.
    try:
        employee_data.update({
            "user_id": str(user_dict.get("_id") or user_dict.get("id")),
            "created_at": datetime.now(timezone.utc),
            "deleted_at": None,
        })
        employee_dict = await MongoEmployeeService().create_employee(employee_data)
    except Exception as exc:
        user_id = user_dict.get("_id") or user_dict.get("id")
        if user_id is not None:
            await user_service.delete_user(str(user_id))
        raise HTTPException(status_code=500, detail="User and employee information could not be saved") from exc

    # Convert MongoDB _id to id for response
    if "_id" in user_dict:
        user_dict["id"] = str(user_dict["_id"])
    return UserResponse.model_validate({**employee_dict, **user_dict})


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    # Convert MongoDB _id to id for response
    user_data = current_user.copy()
    if "_id" in user_data:
        user_data["id"] = str(user_data["_id"])
    return UserResponse.model_validate(user_data)


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: dict = Depends(get_current_user),
) -> UserProfileResponse:
    """Get user profile combining user and employee data"""
    try:
        user_id = str(current_user.get("_id") or current_user.get("id"))
        user_service = MongoUserService()
        employee_service = MongoEmployeeService()
        user = await user_service.get_by_id(user_id)
        employee = await employee_service.get_by_user_id(user_id)
        team_lead = None
        team_lead_id = employee.get("team_lead_id") if employee else None
        if team_lead_id:
            team_lead_id = str(team_lead_id)
            team_lead = await user_service.get_by_id(team_lead_id)

        lead_first_name = ((team_lead or {}).get("first_name") or "").strip()
        lead_last_name = ((team_lead or {}).get("last_name") or "").strip()
        team_lead_name = " ".join(
            name for name in (lead_first_name, lead_last_name) if name
        ) or ((employee or {}).get("team_lead") or None)
        profile_data = {
            "first_name": user.get("first_name") if user else None,
            "last_name": user.get("last_name") if user else None,
            "email": user.get("email") if user else None,
            "phone_number": user.get("phone_number") if user else None,
            "team_lead": team_lead_name,
            "position": employee.get("role_description") if employee else None,
            "pillar": employee.get("pillar") if employee else  None,
            "client": employee.get("client") if employee else None,
            "project": employee.get("project") if employee else None,
        }

        return UserProfileResponse(**profile_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile", response_model=MessageResponse)
async def update_user_profile(
    data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
) -> MessageResponse:
    """Update user profile (first name, last name, phone number)"""
    try:
        await MongoDB.connect()
        users_collection = MongoDB.get_collection("users")

        user_id = str(current_user.get("_id"))

        # Update user data (first name, last name)
        if data.first_name is not None or data.last_name is not None:
            update_data = {}
            if data.first_name is not None:
                update_data["first_name"] = data.first_name
            if data.last_name is not None:
                update_data["last_name"] = data.last_name

            if update_data:
                await users_collection.update_one(
                    {"_id": {"$in": _mongo_id_values(user_id)}},
                    {"$set": update_data}
                )

        # Phone number belongs to the user account.
        if data.phone_number is not None:
            await users_collection.update_one(
                {"_id": {"$in": _mongo_id_values(user_id)}},
                {"$set": {"phone_number": data.phone_number}}
            )

        return MessageResponse(message="Profile updated successfully")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=PaginatedResponse[UserResponse])
async def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    _: dict = Depends(require_permission("members", "view")),
) -> PaginatedResponse[UserResponse]:
    user_service = MongoUserService()
    skip = (page - 1) * page_size
    items = await user_service.get_all_users(skip=skip, limit=page_size)
    employee_service = MongoEmployeeService()
    # For simplicity, we'll return the count as the length of items
    # In production, you'd want to implement proper counting
    total = len(items)
    
    # Convert MongoDB _id to id for each user before validation
    converted_items = []
    for u in items:
        user_dict = u.copy()
        if "_id" in user_dict:
            user_dict["id"] = str(user_dict["_id"])
        employee = await employee_service.get_by_user_id(str(user_dict.get("id", "")))
        if employee:
            employee_fields = set(Employee.model_fields) - {
                "id",
                "user_id",
                "country",
            }
            user_dict.update({
                key: value
                for key, value in employee.items()
                if key in employee_fields
            })
        converted_items.append(user_dict)
    
    return PaginatedResponse[UserResponse].create(
        items=[UserResponse.model_validate(u) for u in converted_items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/skill-sets", response_model=List[str])
async def list_employee_skill_sets(
    _: dict = Depends(get_current_user),
) -> List[str]:
    """Return unique skill set values from employees for dropdown usage."""
    employees_collection = MongoDB.get_collection("employees")
    employees = await employees_collection.find(
        {"deleted_at": None},
        {"skill_set": 1},
    ).to_list(length=None)

    skills = set()
    for employee in employees:
        raw_skill_set = employee.get("skill_set")
        if not raw_skill_set:
            continue

        if isinstance(raw_skill_set, list):
            values = raw_skill_set
        else:
            values = re.split(r",", str(raw_skill_set))

        for value in values:
            skill = str(value).strip()
            if not skill:
                continue
            if skill.lower() in {"na", "n/a", "none", "null"}:
                continue
            skills.add(skill)

    return sorted(skills, key=str.lower)


@router.get("/projects", response_model=List[str])
async def list_employee_projects(
    _: dict = Depends(get_current_user),
) -> List[str]:
    """Return unique project values from employees for dropdown usage."""
    employees_collection = MongoDB.get_collection("employees")
    employees = await employees_collection.find(
        {"deleted_at": None},
        {"project": 1},
    ).to_list(length=None)

    projects = set()
    for employee in employees:
        raw_project = employee.get("project")
        if not raw_project:
            continue

        values = re.split(r",", str(raw_project))
        for value in values:
            project = str(value).strip()
            if not project:
                continue
            if project.lower() in {"na", "n/a", "none", "null"}:
                continue
            projects.add(project)

    return sorted(projects, key=str.lower)


@router.get("/onboarding", response_model=List[Dict])
async def list_onboarding_employees(
    _: dict = Depends(require_permission("members", "view")),
) -> List[Dict]:
    """Return users joined with their employee onboarding details."""
    users_collection = MongoDB.get_collection("users")
    employees_collection = MongoDB.get_collection("employees")
    onboarding_collection = MongoDB.get_collection("onboarding_employees")

    await ensure_employee_onboarding_records(employees_collection, onboarding_collection)

    users = await users_collection.find({"deleted_at": None}).to_list(length=None)
    employees = await employees_collection.find({"deleted_at": None}).to_list(length=None)
    onboarding_records = await onboarding_collection.find({}).to_list(length=None)
    onboarding_by_employee_id = {
        record.get("employee_id"): record
        for record in onboarding_records
        if record.get("employee_id")
    }
    employees_by_user_id = {str(employee.get("user_id")): employee for employee in employees if employee.get("user_id")}
    employees_by_email = {
        value.lower(): employee
        for employee in employees
        for value in (employee.get("email"), employee.get("email_id"))
        if value
    }
    result = []
    for user in users:
        user_id = str(user["_id"])
        employee = employees_by_user_id.get(user_id) or employees_by_email.get(user.get("email", "").lower(), {})
        onboarding = onboarding_by_employee_id.get(employee.get("employee_id"), {})
        full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
        primary_skill = onboarding.get("primaryskill") or employee.get("skill_set") or ""
        result.append({
            "id": user_id,
            "employee": employee.get("full_name") or full_name or user.get("email", ""),
            "employeeCode": employee.get("employee_id"),
            "email": user.get("email"),
            "client": employee.get("client"),
            "project": employee.get("project"),
            "teamLead": employee.get("team_lead"),
            "primarySkill": primary_skill,
            "primaryskill": primary_skill,
            "accountManager": employee.get("account_manager"),
            "joiningDate": employee.get("onboarding_vlink") or user.get("created_at"),
            "teamLeadId": str(employee.get("team_lead_id") or ""),
            "credential": onboarding.get("credential_status") or ("Completed" if employee.get("client_credential_received") else "Pending"),
            "bgv": onboarding.get("bgv_status") or ("Completed" if employee.get("bgv_clear") else "Pending"),
            "vcf": onboarding.get("vcf_status") or ("Completed" if employee.get("vcf_sent") else "Pending"),
            "status": onboarding.get("onboarding_status") or employee.get("status") or ("Active" if user.get("is_active", True) else "Inactive"),
            "rag": onboarding.get("rag_status") or employee.get("rag_status") or "Green",
            "createdAt": user.get("created_at"),
        })

    return sorted(result, key=lambda item: item["employee"].lower())


def _normalize_status_value(value: Optional[str]) -> str:
    status = str(value or "").strip()
    if not status:
        return "Pending"

    normalized = status.lower()
    if normalized in {"inprogress", "in_progress", "in progress"}:
        return "InProgress"
    if normalized == "cancelled":
        return "Cancelled"
    if normalized == "completed":
        return "Completed"
    if normalized == "pending":
        return "Pending"
    return status.title()


def _rag_from_initiated_date(value: Optional[str]) -> str:
    """Compute onboarding RAG from initiated date to today."""
    candidate = str(value or "").strip()
    if not candidate:
        return "Green"

    try:
        start_date = date.fromisoformat(candidate)
    except ValueError:
        return "Green"

    age_days = max(0, (datetime.now(timezone.utc).date() - start_date).days)
    if age_days <= 21:
        return "Green"
    if age_days <= 30:
        return "Amber"
    return "Red"


@router.get("/onboarding/metrics", response_model=Dict)
async def get_onboarding_metrics(
    _: dict = Depends(require_permission("members", "view")),
) -> Dict:
    """Return aggregated onboarding metrics using the configured RAG rule for BGV and VCF items."""
    onboarding_collection = MongoDB.get_collection("onboarding_employees")
    onboarding_records = await onboarding_collection.find({}).to_list(length=None)
    status_order = ["Completed", "InProgress", "Pending", "Cancelled"]
    rag_order = ["Green", "Amber", "Red"]

    def build_status_metric(field_name: str) -> Dict[str, int]:
        counts = {status: 0 for status in status_order}
        for record in onboarding_records:
            status = _normalize_status_value(record.get(field_name))
            if status in counts:
                counts[status] += 1
            else:
                counts["Pending"] += 1
        return counts

    def build_rag_metric(date_field: str) -> Dict[str, int]:
        counts = {rag: 0 for rag in rag_order}
        for record in onboarding_records:
            initiated_date = record.get(date_field)
            rag = _rag_from_initiated_date(initiated_date)
            if rag in counts:
                counts[rag] += 1
        return counts

    bgv = build_rag_metric("bgv_initiated_date")
    vcf = build_rag_metric("vcf_sent_date")

    return {
        "bgv": bgv,
        "vcf": vcf,
        "clientCredentials": vcf,
        "onboardedEmployees": build_status_metric("onboarding_status"),
    }


async def _resolve_user_and_employee(users_collection, employees_collection, user_id: str):
    """Resolve a user and employee record from either a real Mongo _id, user id, or employee code."""
    resolved_user = None
    if ObjectId.is_valid(user_id):
        try:
            resolved_user = await users_collection.find_one({"_id": ObjectId(user_id), "deleted_at": None})
        except Exception:
            resolved_user = None

    if not resolved_user:
        employee = await employees_collection.find_one({
            "$or": [
                {"employee_id": user_id},
                {"user_id": user_id},
                {"email": user_id},
                {"email_id": user_id},
            ],
            "deleted_at": None,
        })
        if employee:
            raw_user_id = employee.get("user_id")
            if raw_user_id:
                try:
                    if ObjectId.is_valid(str(raw_user_id)):
                        resolved_user = await users_collection.find_one({"_id": ObjectId(str(raw_user_id)), "deleted_at": None})
                except Exception:
                    resolved_user = None

                if not resolved_user:
                    resolved_user = await users_collection.find_one({"_id": str(raw_user_id), "deleted_at": None})

            if not resolved_user and employee.get("email_id"):
                resolved_user = await users_collection.find_one({"email": employee.get("email_id"), "deleted_at": None})
            if not resolved_user and employee.get("email"):
                resolved_user = await users_collection.find_one({"email": employee.get("email"), "deleted_at": None})
        else:
            resolved_user = await users_collection.find_one({"email": user_id, "deleted_at": None})

    user = resolved_user
    if not user:
        return None, None

    employee_query = {
        "$or": [
            {"user_id": user.get("_id")},
            {"user_id": str(user.get("_id"))},
            {"user_id": user_id},
            {"employee_id": user_id},
            {"email": user.get("email")},
            {"email_id": user.get("email")},
        ],
        "deleted_at": None,
    }
    employee = await employees_collection.find_one(employee_query) or {}
    return user, employee


@router.get("/onboarding/{user_id}", response_model=Dict)
async def get_onboarding_employee(
    user_id: str,
    _: dict = Depends(require_permission("members", "view")),
) -> Dict:
    """Return one user's employee and onboarding milestone details."""
    users_collection = MongoDB.get_collection("users")
    employees_collection = MongoDB.get_collection("employees")
    onboarding_collection = MongoDB.get_collection("onboarding_employees")
    await ensure_employee_onboarding_records(employees_collection, onboarding_collection)

    user, employee = await _resolve_user_and_employee(users_collection, employees_collection, user_id)
    if not user:
        raise NotFoundException(f"User '{user_id}' not found.")

    if not employee:
        employee = {}
    employee_id = employee.get("employee_id") or user_id
    onboarding = await onboarding_collection.find_one({"employee_id": employee_id}) or {}
    full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()

    def normalize_person_name(value: Optional[str]) -> str:
        return str(value or "").strip().lower()

    team_lead_email = ""
    account_manager_email = ""
    team_lead_name = employee.get("team_lead")
    account_manager_name = employee.get("account_manager")

    names_to_resolve = {
        normalize_person_name(team_lead_name),
        normalize_person_name(account_manager_name),
    }
    names_to_resolve.discard("")

    if names_to_resolve:
        related_people = await employees_collection.find(
            {
                "deleted_at": None,
                "full_name": {"$in": [name for name in [team_lead_name, account_manager_name] if name]},
            },
            {"full_name": 1, "email": 1, "email_id": 1},
        ).to_list(length=None)

        email_by_name = {
            normalize_person_name(person.get("full_name")): person.get("email") or person.get("email_id") or ""
            for person in related_people
        }
        team_lead_email = email_by_name.get(normalize_person_name(team_lead_name), "")
        account_manager_email = email_by_name.get(normalize_person_name(account_manager_name), "")

    def milestone(title, requested_key, completed_key, status_key, fallback_status, rag, label1, label2, fallback_requested, fallback_completed):
        requested_date = onboarding.get(requested_key) or employee.get(fallback_requested) or ""
        completed_date = onboarding.get(completed_key) or employee.get(fallback_completed) or ""
        end_date = completed_date or datetime.now(timezone.utc).date().isoformat()
        waiting_days = 0
        if requested_date:
            try:
                waiting_days = max(0, (date.fromisoformat(end_date) - date.fromisoformat(requested_date)).days)
            except ValueError:
                waiting_days = 0
        return {
            "title": title,
            "requestedDate": requested_date,
            "completedDate": completed_date,
            "status": onboarding.get(status_key) or fallback_status,
            "waitingDays": waiting_days,
            "rag": onboarding.get("rag_status") or rag,
            "label1": label1,
            "label2": label2,
        }

    primary_skill = onboarding.get("primaryskill") or employee.get("skill_set") or ""

    return {
        "id": user_id,
        "employee": employee.get("full_name") or full_name or user.get("email", ""),
        "employeeCode": employee_id,
        "email": user.get("email"),
        "client": employee.get("client"),
        "project": employee.get("project"),
        "teamLead": employee.get("team_lead"),
        "teamLeadEmail": team_lead_email,
        "accountManager": employee.get("account_manager"),
        "accountManagerEmail": account_manager_email,
        "primarySkill": primary_skill,
        "primaryskill": primary_skill,
        "joiningDate": employee.get("onboarding_vlink") or "",
        "tracking": [
            milestone("Client Credentials", "credential_requested_date", "credential_received_date", "credential_status", "Pending", "Amber", "Credential Requested Date", "Credential Received Date", "onboarding_vlink", "client_credential_received"),
            milestone("Background Verification", "bgv_initiated_date", "bgv_completed_date", "bgv_status", "Pending", "Green", "BGV Initiated Date", "BGV Completed Date", "bgv_start", "bgv_clear"),
            milestone("VCF Tracking", "vcf_sent_date", "client_credential_received_date", "vcf_status", "Pending", "Green", "VCF Sent Date", "Client Credential Received Date", "vcf_sent", "client_credential_received"),
        ],
        "status": onboarding.get("onboarding_status") or employee.get("status") or ("Active" if user.get("is_active", True) else "Inactive"),
        "remarks": onboarding.get("remarks") or "",
        "rag": onboarding.get("rag_status") or "Green",
    }


@router.patch("/onboarding/{user_id}", response_model=Dict)
async def update_onboarding_employee(
    user_id: str,
    data: Dict,
    current_user: dict = Depends(require_permission("members", "modify")),
) -> Dict:
    """Save editable onboarding milestone fields for one user."""
    users_collection = MongoDB.get_collection("users")
    employees_collection = MongoDB.get_collection("employees")
    onboarding_collection = MongoDB.get_collection("onboarding_employees")
    await ensure_employee_onboarding_records(employees_collection, onboarding_collection)
    user, employee = await _resolve_user_and_employee(users_collection, employees_collection, user_id)

    if not user:
        raise NotFoundException(f"User '{user_id}' not found.")

    if not employee:
        raise NotFoundException(f"Employee details for user '{user_id}' not found.")

    employee_id = employee.get("employee_id") or user_id
    field_map = {
        "Client Credentials": {
            "requestedDate": "credential_requested_date",
            "completedDate": "credential_received_date",
            "status": "credential_status",
        },
        "Background Verification": {
            "requestedDate": "bgv_initiated_date",
            "completedDate": "bgv_completed_date",
            "status": "bgv_status",
        },
        "VCF Tracking": {
            "requestedDate": "vcf_sent_date",
            "completedDate": "client_credential_received_date",
            "status": "vcf_status",
        },
    }
    updates = {}
    if "primarySkill" in data:
        primary_skill = str(data.get("primarySkill") or "").strip()
        updates["primaryskill"] = primary_skill or None

    for item in data.get("tracking", []):
        fields = field_map.get(item.get("title"), {})
        requested_date = item.get("requestedDate")
        completed_date = item.get("completedDate")
        item_status = str(item.get("status") or "").strip().lower()
        if requested_date and completed_date and item_status == "completed":
            try:
                if date.fromisoformat(completed_date) < date.fromisoformat(requested_date):
                    raise HTTPException(status_code=400, detail="Invalid data")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid data")
        for payload_key, onboarding_key in fields.items():
            if payload_key in item:
                updates[onboarding_key] = item[payload_key] or None

    credential_received_key = "credential_received_date"
    vcf_received_key = "client_credential_received_date"
    if credential_received_key in updates or vcf_received_key in updates:
        synchronized_received_date = updates.get(vcf_received_key) or updates.get(credential_received_key)
        updates[credential_received_key] = synchronized_received_date
        updates[vcf_received_key] = synchronized_received_date

    if "status" in data:
        updates["onboarding_status"] = data["status"]
    if "remarks" in data:
        updates["remarks"] = data["remarks"] or None

    updates["updated_at"] = datetime.now(timezone.utc)
    if updates:
        await onboarding_collection.update_one(
            {"employee_id": employee_id},
            {
                "$set": updates,
                "$setOnInsert": {
                    "employee_id": employee_id,
                    "created_at": datetime.now(timezone.utc),
                    "created_by": current_user.get("email") or str(current_user.get("_id")),
                },
            },
            upsert=True,
        )

    return await get_onboarding_employee(user_id, current_user)


@router.post("/onboarding/{user_id}/bgv-completion-email", response_model=MessageResponse)
async def send_onboarding_bgv_completion_email(
    user_id: str,
    _: dict = Depends(require_permission("members", "modify")),
) -> MessageResponse:
    """Send BGV completion email for a user when BGV is marked completed."""
    users_collection = MongoDB.get_collection("users")
    employees_collection = MongoDB.get_collection("employees")
    onboarding_collection = MongoDB.get_collection("onboarding_employees")
    await ensure_employee_onboarding_records(employees_collection, onboarding_collection)

    user, employee = await _resolve_user_and_employee(users_collection, employees_collection, user_id)
    if not user:
        raise NotFoundException(f"User '{user_id}' not found.")
    if not employee:
        raise NotFoundException(f"Employee details for user '{user_id}' not found.")

    employee_id = employee.get("employee_id") or user_id
    onboarding = await onboarding_collection.find_one({"employee_id": employee_id}) or {}
    is_bgv_completed = str(onboarding.get("bgv_status") or "").strip().lower() == "completed"
    if not is_bgv_completed:
        raise HTTPException(status_code=400, detail="BGV status must be Completed before sending email")

    recipient_email = employee.get("email") or employee.get("email_id") or user.get("email")
    if not recipient_email:
        raise HTTPException(status_code=400, detail="Recipient email is not available")

    recipient_name = employee.get("full_name") or f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "Employee"

    cc_candidates = []
    for manager_name in [employee.get("team_lead"), employee.get("account_manager")]:
        if not manager_name:
            continue
        manager = await employees_collection.find_one(
            {"full_name": manager_name, "deleted_at": None},
            {"email": 1, "email_id": 1},
        )
        if manager:
            cc_candidates.append(manager.get("email") or manager.get("email_id"))

    try:
        send_bgv_completion_email(
            to_email=recipient_email,
            recipient_name=recipient_name,
            cc=cc_candidates,
        )
    except Exception as exc:
        logger.error(
            "Failed to queue BGV completion email",
            user_id=user_id,
            employee_id=employee_id,
            error=str(exc),
        )
        raise HTTPException(status_code=500, detail="Failed to queue BGV completion email")

    return MessageResponse(message="BGV completion email queued successfully")



@router.post("/onboarding/{user_id}/client-credential-email", response_model=MessageResponse)
async def send_onboarding_client_credential_email(
    user_id: str,
    _: dict = Depends(require_permission("members", "modify")),
) -> MessageResponse:
    """Send client credential received email for a user when Client Credentials is completed."""
    users_collection = MongoDB.get_collection("users")
    employees_collection = MongoDB.get_collection("employees")
    onboarding_collection = MongoDB.get_collection("onboarding_employees")
    await ensure_employee_onboarding_records(employees_collection, onboarding_collection)

    user, employee = await _resolve_user_and_employee(users_collection, employees_collection, user_id)
    if not user:
        raise NotFoundException(f"User '{user_id}' not found.")
    if not employee:
        raise NotFoundException(f"Employee details for user '{user_id}' not found.")

    employee_id = employee.get("employee_id") or user_id
    onboarding = await onboarding_collection.find_one({"employee_id": employee_id}) or {}
    completed_statuses = {
        str(onboarding.get("credential_status") or "").strip().lower(),
        str(onboarding.get("vcf_status") or "").strip().lower(),
    }
    is_client_credentials_completed = "completed" in completed_statuses
    if not is_client_credentials_completed:
        raise HTTPException(status_code=400, detail="Client Credentials or VCF status must be Completed before sending email")

    recipient_email = employee.get("email") or employee.get("email_id") or user.get("email")
    if not recipient_email:
        raise HTTPException(status_code=400, detail="Recipient email is not available")

    recipient_name = employee.get("full_name") or f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "Employee"

    cc_candidates = []
    for manager_name in [employee.get("team_lead"), employee.get("account_manager")]:
        if not manager_name:
            continue
        manager = await employees_collection.find_one(
            {"full_name": manager_name, "deleted_at": None},
            {"email": 1, "email_id": 1},
        )
        if manager:
            cc_candidates.append(manager.get("email") or manager.get("email_id"))

    try:
        send_client_credential_email(
            to_email=recipient_email,
            recipient_name=recipient_name,
            cc=cc_candidates,
        )
    except Exception as exc:
        logger.error(
            "Failed to queue client credential received email",
            user_id=user_id,
            employee_id=employee_id,
            error=str(exc),
        )
        raise HTTPException(status_code=500, detail="Failed to queue client credential received email")

    return MessageResponse(message="Client credential received email queued successfully")


@router.get("/permissions-summary", response_model=List[Dict])
async def get_users_permissions_summary(
    _: dict = Depends(require_permission("permissions", "view"))
) -> List[Dict]:
    """Get all users with their permissions and roles summary."""
    users_collection = MongoDB.get_collection("users")
    user_permissions_collection = MongoDB.get_collection("user_permissions")
    user_roles_collection = MongoDB.get_collection("user_roles")
    roles_collection = MongoDB.get_collection("roles")
    permissions_collection = MongoDB.get_collection("permissions")
    
    # Get all active users
    users = await users_collection.find({"is_active": True, "deleted_at": None}).to_list(length=None)
    
    result = []
    
    for user in users:
        user_id = str(user["_id"])
        
        # Get direct permissions
        user_perms = user_permissions_collection.find({"user_id": user_id})
        direct_permissions = []
        async for user_perm in user_perms:
            perm_id = user_perm["permission_id"]
            perm = await permissions_collection.find_one({"_id": ObjectId(perm_id)})
            if perm:
                direct_permissions.append({
                    "id": str(perm["_id"]),
                    "page": perm.get("page"),
                    "action": perm.get("action"),
                    "display_name": perm.get("display_name")
                })
        
        # Get roles
        user_roles = user_roles_collection.find({"user_id": user_id})
        roles = []
        role_permissions = []
        
        async for user_role in user_roles:
            role_id = str(user_role["role_id"])
            role = await roles_collection.find_one({
                "_id": {"$in": _mongo_id_values(role_id)},
                "deleted_at": None
            })
            if role:
                roles.append({
                    "id": str(role["_id"]),
                    "name": role.get("name"),
                    "display_name": role.get("display_name")
                })
                
                # Get permissions from role
                for perm_id in role.get("permissions", []):
                    perm = await permissions_collection.find_one({"_id": ObjectId(perm_id)})
                    if perm:
                        role_permissions.append({
                            "id": str(perm["_id"]),
                            "page": perm.get("page"),
                            "action": perm.get("action"),
                            "display_name": perm.get("display_name")
                        })
        
        # Combine direct and role permissions (remove duplicates)
        all_permissions = direct_permissions.copy()
        seen = {p["id"] for p in direct_permissions}
        for rp in role_permissions:
            if rp["id"] not in seen:
                all_permissions.append(rp)
                seen.add(rp["id"])
        
        result.append({
            "id": user_id,
            "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user.get("email", ""),
            "email": user.get("email"),
            "totalPermissions": len(all_permissions),
            "directPermissions": direct_permissions,
            "roles": roles,
            "rolePermissions": role_permissions,
            "allPermissions": all_permissions
        })
    
    # Sort by name
    result.sort(key=lambda x: x["name"].lower())
    
    return result


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    _: dict = Depends(get_current_user),
) -> UserResponse:
    user_service = MongoUserService()
    user = await user_service.get_by_id(user_id)
    if not user:
        raise NotFoundException(f"User '{user_id}' not found.")
    employee_fields = (
        set(UserResponse.model_fields)
        .intersection(Employee.model_fields)
        .difference(User.model_fields)
    )
    employee = await MongoEmployeeService().get_by_user_id(user_id)
    if employee:
        user.update({
            key: value for key, value in employee.items()
            if key in employee_fields
        })
    # Convert MongoDB _id to id for response
    if "_id" in user:
        user["id"] = str(user["_id"])
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    data: UserUpdate,
    _: dict = Depends(get_current_user),
) -> UserResponse:
    user_service = MongoUserService()
    payload = data.model_dump(exclude_unset=True)
    team_lead_id = payload.get("team_lead_id")
    if team_lead_id is not None and str(team_lead_id) == str(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A member cannot be their own team lead.",
        )
    employee_fields = (
        set(UserResponse.model_fields)
        .intersection(Employee.model_fields)
        .difference(User.model_fields)
    )
    employee_data = {
        key: payload[key]
        for key in employee_fields
        if key in payload
    }
    user_data = {
        key: value
        for key, value in payload.items()
        if key in User.model_fields
    }

    user = await user_service.update_user(
        user_id, UserUpdate.model_validate(user_data)
    ) if user_data else await user_service.get_by_id(user_id)
    if not user:
        raise NotFoundException(f"User not found.")

    employee_service = MongoEmployeeService()
    employee = await employee_service.get_by_user_id(user_id)
    if employee_data:
        if employee:
            employee_id = str(employee.get("_id") or employee.get("id"))
            employee = await employee_service.update_employee(
                employee_id, employee_data
            )
        else:
            employee = await employee_service.create_employee(
                {"user_id": user_id, **employee_data}
            )
        if not employee:
            raise NotFoundException(
                "User not found: Employee information could not be updated."
            )
    if employee:
        user.update({
            key: value
            for key, value in employee.items()
            if key in employee_fields
        })

    # Convert MongoDB _id to id for response
    if "_id" in user:
        user["id"] = str(user["_id"])
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str,
    _: dict = Depends(require_permission("members", "delete")),
) -> MessageResponse:
    user_service = MongoUserService()
    deleted_user = await user_service.delete_user(user_id)
    if deleted_user is False:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User information could not be deleted.",
        )

    employee_service = MongoEmployeeService()
    employee = await employee_service.get_by_user_id(user_id)
    if employee:
        employee_id = str(employee.get("_id") or employee.get("id"))
        if not await employee_service.delete_employee(employee_id):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Employee information could not be deleted.",
            )
    user_permissions_collection = MongoDB.get_collection("user_permissions")
    await user_permissions_collection.delete_many(
        {"user_id": {"$in": _mongo_id_values(user_id)}}
    )
    return MessageResponse(message=f"User '{user_id}' deleted successfully.")


@router.get("/{user_id}/permissions", response_model=List[Dict])
async def get_user_permissions(
    user_id: str,
    _: dict = Depends(require_permission("permissions", "view"))
) -> List[Dict]:
    """Get all permissions for a specific user."""
    user_permissions_collection = MongoDB.get_collection("user_permissions")
    permissions_collection = MongoDB.get_collection("permissions")
    
    # Get user's direct permissions
    user_perms = user_permissions_collection.find({"user_id": user_id})
    permissions = []
    
    async for user_perm in user_perms:
        perm_id = user_perm["permission_id"]
        perm = await permissions_collection.find_one({"_id": ObjectId(perm_id)})
        if perm:
            permissions.append({
                "permission_id": str(perm["_id"]),
                "page": perm.get("page"),
                "action": perm.get("action"),
                "display_name": perm.get("display_name")
            })
    
    return permissions


@router.post("/permissions", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_user_permission(
    data: UserPermissionCreate,
    _: dict = Depends(require_permission("permissions", "modify"))
) -> MessageResponse:
    """Add a permission to a user."""
    user_permissions_collection = MongoDB.get_collection("user_permissions")
    
    # Check if permission already exists
    existing = await user_permissions_collection.find_one({
        "user_id": data.user_id,
        "permission_id": data.permission_id
    })
    
    if existing:
        return MessageResponse(message="Permission already assigned to user.")
    
    # Add permission
    await user_permissions_collection.insert_one({
        "user_id": data.user_id,
        "permission_id": data.permission_id
    })
    
    return MessageResponse(message="Permission added to user successfully.")


@router.delete("/permissions/{user_id}/{permission_id}", response_model=MessageResponse)
async def remove_user_permission(
    user_id: str,
    permission_id: str,
    _: dict = Depends(require_permission("permissions", "modify"))
) -> MessageResponse:
    """Remove a permission from a user."""
    user_permissions_collection = MongoDB.get_collection("user_permissions")
    
    result = await user_permissions_collection.delete_one({
        "user_id": user_id,
        "permission_id": permission_id
    })
    
    if result.deleted_count == 0:
        raise NotFoundException("Permission assignment not found.")
    
    return MessageResponse(message="Permission removed from user successfully.")


@router.post("/roles", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_user_role(
    data: UserRoleCreate,
    _: dict = Depends(require_permission("permissions", "modify"))
) -> MessageResponse:
    """Add a role to a user."""
    user_roles_collection = MongoDB.get_collection("user_roles")
    roles_collection = MongoDB.get_collection("roles")
    
    # Check if role exists
    role = await roles_collection.find_one({"_id": ObjectId(data.role_id), "deleted_at": None})
    if not role:
        raise NotFoundException("Role not found")
    
    # Check if user already has this role
    existing = await user_roles_collection.find_one({
        "user_id": data.user_id,
        "role_id": data.role_id
    })
    if existing:
        raise HTTPException(status_code=400, detail="User already has this role")
    
    # Add role to user
    await user_roles_collection.insert_one({
        "user_id": data.user_id,
        "role_id": data.role_id,
        "created_at": datetime.now(timezone.utc)
    })
    
    return MessageResponse(message="Role added to user successfully")


@router.delete("/roles/{user_id}/{role_id}", response_model=MessageResponse)
async def remove_user_role(
    user_id: str,
    role_id: str,
    _: dict = Depends(require_permission("permissions", "modify"))
) -> MessageResponse:
    """Remove a role from a user."""
    user_roles_collection = MongoDB.get_collection("user_roles")
    
    result = await user_roles_collection.delete_one({
        "user_id": user_id,
        "role_id": role_id
    })
    
    if result.deleted_count == 0:
        raise NotFoundException("User role not found")
    
    return MessageResponse(message="Role removed from user successfully")
