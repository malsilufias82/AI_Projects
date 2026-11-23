import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.auth.dependencies import get_current_user, require_permission
from app.core.mongodb import MongoDB
from app.models.mongo_onboarding_employeeactivities_tracker import OnboardingEmployeeActivityTracker

router = APIRouter()


class Week0ColumnPayload(BaseModel):
    name: str
    label: str
    field: str
    align: str = "left"
    classes: str | None = None
    headerClasses: str | None = None


class Week0RowPayload(BaseModel):
    id: int
    day: str = ""
    activity: str = ""
    action: str = ""
    relevantLink: str = ""
    technology: str = "Applicable for all"
    project: str = "Applicable for all projects"
    comment: str = ""
    status: str = "Pending"
    updatedAt: datetime | None = None
    completedAt: datetime | None = None
    createdAt: datetime | None = None


class Week0TrackerResponse(BaseModel):
    columns: List[Week0ColumnPayload] = Field(default_factory=list)
    rows: List[Week0RowPayload] = Field(default_factory=list)
    counts: Dict[str, int] = Field(default_factory=dict)
    phaseCompletionDates: Dict[str, datetime] = Field(default_factory=dict)


class Week0TrackerUpdate(BaseModel):
    columns: List[Week0ColumnPayload] = Field(default_factory=list)
    rows: List[Week0RowPayload] = Field(default_factory=list)
    employeeId: str | None = None
    employee_id: str | None = None
    employeeCode: str | None = None


DEFAULT_COLUMNS = [
    {
        "name": "day",
        "label": "Day",
        "field": "day",
        "align": "left",
        "classes": "wrap-cell",
        "headerClasses": "wrap-cell",
    },
    {
        "name": "activity",
        "label": "Activity",
        "field": "activity",
        "align": "left",
        "classes": "wrap-cell",
        "headerClasses": "wrap-cell",
    },
    {
        "name": "action",
        "label": "Actions",
        "field": "action",
        "align": "left",
        "classes": "wrap-cell",
        "headerClasses": "wrap-cell",
    },
    {
        "name": "technology",
        "label": "Technology",
        "field": "technology",
        "align": "left",
    },
    {
        "name": "project",
        "label": "Project",
        "field": "project",
        "align": "left",
    },
    {
        "name": "comment",
        "label": "Comment",
        "field": "comment",
        "align": "left",
        "classes": "wrap-cell",
        "headerClasses": "wrap-cell",
    },
    {
        "name": "status",
        "label": "Status",
        "field": "status",
        "align": "left",
    },
]


DEFAULT_ROWS = []
VDI_ACTIVATION_DEFAULT_ROW = {
    "id": 0,
    "day": "Week0",
    "activity": "Client VDI",
    "action": "VDI Activation",
    "relevantLink": "VDI Activation",
    "technology": "Applicable for all",
    "project": "Applicable for all",
    "comment": "",
    "status": "Pending",
}


def _vdi_activation_week0_row_query() -> Dict:
    return {
        "day": {"$regex": "^week0$", "$options": "i"},
        "activity": {"$regex": "^client vdi$", "$options": "i"},
        "$or": [
            {"actions": {"$regex": "^vdi activation$", "$options": "i"}},
            {"action": {"$regex": "^vdi activation$", "$options": "i"}},
            {"relevantLink": {"$regex": "^vdi activation$", "$options": "i"}},
        ],
    }


def _is_vdi_activation_row(row: Dict) -> bool:
    normalized_day = re.sub(r"[\s_-]+", "", str(row.get("day") or "").strip().lower())
    if normalized_day == "vdiactivation":
        return True

    activity = str(row.get("activity") or "").strip().lower()
    action = str(row.get("action", row.get("relevantLink", row.get("actions", ""))) or "").strip().lower()
    return normalized_day == "week0" and activity == "client vdi" and action == "vdi activation"


async def _ensure_vdi_activation_seed_row(collection) -> None:
    row_filter = _row_filter(VDI_ACTIVATION_DEFAULT_ROW)
    seed_document = _row_document(VDI_ACTIVATION_DEFAULT_ROW)
    seed_document["createdAt"] = datetime.now(timezone.utc)
    await collection.update_one(row_filter, {"$setOnInsert": seed_document}, upsert=True)


def _normalize_columns(raw_columns: List[Dict] | None) -> List[Dict]:
    canonical = [dict(col) for col in DEFAULT_COLUMNS]
    incoming = raw_columns or []
    if not incoming:
        return canonical

    alias_to_name = {
        "relevantLink": "action",
        "actions": "action",
        "action": "action",
        "projects": "project",
        "blocker": "comment",
        "comment": "comment",
    }
    by_name = {col["name"]: col for col in canonical}

    for column in incoming:
        if not isinstance(column, dict):
            continue
        raw_name = str(column.get("name") or column.get("field") or "").strip()
        if not raw_name:
            continue
        normalized_name = alias_to_name.get(raw_name, raw_name)
        if normalized_name not in by_name:
            continue

        base = by_name[normalized_name]
        base["align"] = str(column.get("align") or base.get("align") or "left")
        base["classes"] = column.get("classes", base.get("classes"))
        base["headerClasses"] = column.get("headerClasses", base.get("headerClasses"))

    # Enforce exact labels requested.
    by_name["day"]["label"] = "Day"
    by_name["activity"]["label"] = "Activity"
    by_name["action"]["label"] = "Actions"
    by_name["technology"]["label"] = "Technology"
    by_name["project"]["label"] = "Project"
    by_name["comment"]["label"] = "Comment"

    return [
        by_name["day"],
        by_name["activity"],
        by_name["action"],
        by_name["technology"],
        by_name["project"],
        by_name["comment"],
        by_name["status"],
    ]


def _normalize_status(value: str) -> str:
    normalized = str(value).strip().lower()
    if normalized in {"completed", "complete"}:
        return "Completed"
    if normalized in {"not applicable", "not_applicable", "n/a"}:
        return "Not Applicable"
    if normalized in {"in progress", "in-progress", "in_progress", "inprogress"}:
        return "In Progress"
    if normalized == "blocked":
        return "Blocked"
    return "Pending"


def _is_completed_status(value: str) -> bool:
    return _normalize_status(value) in {"Completed", "Not Applicable"}


def _as_utc_datetime(value: Any) -> datetime | None:
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _normalize_row(raw: Dict) -> Dict:
    action = str(raw.get("action", raw.get("relevantLink", "")) or "")
    project = str(raw.get("project", raw.get("projects", "Applicable for all projects")) or "Applicable for all projects")
    comment = str(raw.get("comment", raw.get("blocker", "")) or "")
    return {
        "id": int(raw.get("id", 0)),
        "day": str(raw.get("day", "") or ""),
        "activity": str(raw.get("activity", "") or ""),
        "action": action,
        "relevantLink": action,
        "technology": str(raw.get("technology", "Applicable for all") or "Applicable for all"),
        "project": project,
        "projects": project,
        "comment": comment,
        "status": _normalize_status(raw.get("status", "Pending")),
    }


def _normalize_seed_row(raw: Dict, fallback_id: int) -> Dict:
    action = str(raw.get("action", raw.get("relevantLink", raw.get("actions", ""))) or "")
    project = str(raw.get("project", raw.get("projects", "Applicable for all projects")) or "Applicable for all projects")
    comment = str(raw.get("comment", raw.get("blocker", "")) or "")
    return {
        "id": int(raw.get("id", fallback_id) or fallback_id),
        "day": str(raw.get("day", "") or ""),
        "activity": str(raw.get("activity", "") or ""),
        "action": action,
        "relevantLink": action,
        "technology": str(raw.get("technology", "Applicable for all") or "Applicable for all"),
        "project": project,
        "projects": project,
        "comment": comment,
        "status": _normalize_status(raw.get("status", "Pending")),
    }


def _row_filter(row: Dict) -> Dict:
    action = str(row.get("action", row.get("relevantLink", row.get("actions", ""))) or "")
    day_value = str(row.get("day", "") or "").strip()
    day_filter: Dict | str
    if day_value.lower() in {"week0", "week-0", "week0-a"}:
        day_filter = {"$regex": "^week0(-a)?$", "$options": "i"}
    elif re.sub(r"[\s_-]+", "", day_value.lower()) == "vdiactivation":
        day_filter = {"$regex": "^vdi[-_ ]?activation$", "$options": "i"}
    else:
        day_filter = day_value

    project_value = str(row.get("project", row.get("projects", "Applicable for all projects")) or "Applicable for all projects")

    return {
        "source": "week0_tracker",
        "day": day_filter,
        "activity": row.get("activity", ""),
        "technology": str(row.get("technology", "Applicable for all") or "Applicable for all"),
        "$and": [
            {
                "$or": [
                    {"project": project_value},
                    {"projects": project_value},
                ]
            }
        ],
        "$or": [
            {"actions": action},
            {"action": action},
            {"relevantLink": action},
        ],
    }


def _deduplicate_seed_rows(rows: List[Dict]) -> List[Dict]:
    deduped_rows: List[Dict] = []
    seen = set()

    for row in rows:
        key = (
            row.get("day", "").strip().lower(),
            row.get("activity", "").strip().lower(),
            row.get("action", "").strip().lower(),
            row.get("technology", "").strip().lower(),
            row.get("project", "").strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped_rows.append(row)

    for idx, row in enumerate(deduped_rows, start=1):
        row["id"] = idx

    return deduped_rows


def _build_phase_counts(rows: List[Dict]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in rows or []:
        raw_day = str(row.get("day") or "").strip()
        if not raw_day:
            continue
        normalized_day = raw_day.lower().replace(" ", "").replace("-", "")
        if _is_vdi_activation_row(row):
            key = "VDI Activation"
        elif normalized_day in {"week0", "week0a", "day0"}:
            key = "Week0"
        elif normalized_day == "vdiactivation":
            key = "VDI Activation"
        elif re.fullmatch(r"day([1-5])a?", normalized_day):
            key = f"Day{normalized_day[3]}"
        elif normalized_day.startswith("day") and normalized_day[3:].isdigit():
            key = f"Day{normalized_day[3:]}"
        else:
            key = raw_day

        counts[key] = counts.get(key, 0) + 1
        counts[f"{key}_total"] = counts.get(f"{key}_total", 0) + 1

        status = _normalize_status(row.get("status", "Pending"))
        if _is_completed_status(status):
            counts[f"{key}_completed"] = counts.get(f"{key}_completed", 0) + 1
        else:
            counts[f"{key}_pending"] = counts.get(f"{key}_pending", 0) + 1

    return counts


def _build_employee_activity_records(employees: List[Dict], tracker_rows: List[Dict], employee_id: str | None = None) -> List[Dict]:
    records: List[Dict] = []
    target_employee_ids = []
    if employee_id:
        target_employee_ids = [str(employee_id).strip()]
    else:
        for employee in employees:
            employee_value = str(employee.get("employee_id") or "").strip()
            if employee_value:
                target_employee_ids.append(employee_value)

    seen = {}
    for employee_value in target_employee_ids:
        if not employee_value:
            continue

        for row in tracker_rows:
            activity_id = row.get("_id")
            if activity_id is None:
                fallback_id = row.get("id")
                if isinstance(fallback_id, str) and ObjectId.is_valid(fallback_id):
                    activity_id = ObjectId(fallback_id)
                elif isinstance(fallback_id, ObjectId):
                    activity_id = fallback_id
                else:
                    activity_id = fallback_id
            if activity_id in (None, ""):
                continue

            record = {
                "employee_id": employee_value,
                "activityid": str(activity_id),
                "activity": str(row.get("activity") or ""),
                "status": _normalize_status(row.get("status") or "Pending"),
                "comment": str(row.get("comment", row.get("blocker", "")) or ""),
                "day": str(row.get("day") or ""),
            }
            record_key = (employee_value, str(activity_id))
            seen[record_key] = record

    return list(seen.values())


def _build_employee_activity_updates(
    employee_ids: List[str],
    payload_rows: List[Dict],
    stored_rows: List[Dict] | None = None,
    existing_activity_rows: List[Dict] | None = None,
    now: datetime | None = None,
) -> List[Dict]:
    unique_employee_ids: List[str] = []
    seen_employee_ids = set()
    for employee_id in employee_ids:
        cleaned = str(employee_id or "").strip()
        if not cleaned or cleaned in seen_employee_ids:
            continue
        unique_employee_ids.append(cleaned)
        seen_employee_ids.add(cleaned)

    if not unique_employee_ids or not payload_rows:
        return []

    stored_by_activity: Dict[str, Dict] = {}
    for stored_row in stored_rows or []:
        activity_name = str(stored_row.get("activity") or "").strip()
        if not activity_name:
            continue
        stored_by_activity[activity_name.lower()] = stored_row

    existing_by_key: Dict[tuple[str, str, str], Dict] = {}
    for activity_row in existing_activity_rows or []:
        key = (
            str(activity_row.get("employee_id") or "").strip().lower(),
            str(activity_row.get("day") or "").strip().lower(),
            str(activity_row.get("activity") or "").strip().lower(),
        )
        if key[0] and key[2]:
            existing_by_key[key] = activity_row

    completion_timestamp = now or datetime.now(timezone.utc)
    updates: List[Dict] = []
    for employee_id in unique_employee_ids:
        for row in payload_rows:
            activity_name = str(row.get("activity") or "").strip()
            if not activity_name:
                continue

            activity_id_source = row.get("id")
            stored_match = stored_by_activity.get(activity_name.lower())
            if stored_match and stored_match.get("_id") is not None:
                activity_id_source = stored_match.get("_id")
            elif stored_match and stored_match.get("activityid") is not None:
                activity_id_source = stored_match.get("activityid")

            if activity_id_source in (None, ""):
                continue

            comment_value = str(row.get("comment", row.get("blocker", "")) or "")
            day_name = str(row.get("day") or "")
            activity_key = (
                employee_id.lower(),
                day_name.strip().lower(),
                activity_name.lower(),
            )
            existing_activity = existing_by_key.get(activity_key, {})
            status = _normalize_status(row.get("status") or "Pending")
            existing_status = _normalize_status(existing_activity.get("status") or "Pending")
            completed_at = None
            if _is_completed_status(status):
                if _is_completed_status(existing_status):
                    existing_completed_at = _as_utc_datetime(existing_activity.get("completedAt"))
                    if existing_completed_at:
                        completed_at = existing_completed_at
                    else:
                        completed_at = None
                else:
                    completed_at = completion_timestamp

            updates.append({
                "employee_id": employee_id,
                "activityid": str(activity_id_source),
                "activity": activity_name,
                "status": status,
                "comment": comment_value,
                "day": day_name,
                "completedAt": completed_at,
            })

    return updates


def _merge_employee_tracker_values(template_rows: List[Dict], tracker_rows: List[Dict], employee_id: str | None = None) -> List[Dict]:
    merged_rows: List[Dict] = []
    if not template_rows:
        return merged_rows

    target_employee_ids = []
    if employee_id:
        target_employee_ids = [str(employee_id).strip()]
    else:
        for row in tracker_rows:
            employee_value = str(row.get("employee_id") or "").strip()
            if employee_value:
                target_employee_ids.append(employee_value)

    employee_values = set(v for v in target_employee_ids if v)
    by_day_activity: Dict[str, Dict] = {}

    for row in tracker_rows:
        row_employee_id = str(row.get("employee_id") or "").strip()
        if employee_id and row_employee_id and row_employee_id != str(employee_id).strip():
            continue
        if not employee_id and row_employee_id and row_employee_id not in employee_values:
            continue

        activity_name = str(row.get("activity") or "").strip()
        day_name = str(row.get("day") or "").strip()
        if not activity_name:
            continue

        key = (row_employee_id or str(employee_id or "")).lower(), day_name.lower(), activity_name.lower()
        by_day_activity[key] = {
            "status": _normalize_status(row.get("status") or "Pending"),
            "comment": str(row.get("comment", row.get("blocker", "")) or ""),
            "updatedAt": _as_utc_datetime(row.get("updatedAt")),
            "completedAt": _as_utc_datetime(row.get("completedAt")),
            "createdAt": _as_utc_datetime(row.get("createdAt")),
        }

    for row in template_rows:
        merged_row = dict(row)
        merged_row["status"] = "Pending"
        merged_row["comment"] = ""

        activity_name = str(row.get("activity") or "").strip()
        day_name = str(row.get("day") or "").strip()
        if activity_name and day_name:
            match_key = (str(employee_id or "").lower(), day_name.lower(), activity_name.lower())
            match = by_day_activity.get(match_key)
            if match:
                merged_row["status"] = match["status"]
                merged_row["comment"] = match["comment"]
                merged_row["updatedAt"] = match["updatedAt"]
                merged_row["completedAt"] = match["completedAt"]
                merged_row["createdAt"] = match["createdAt"]
        merged_rows.append(merged_row)

    return merged_rows


def _row_document(row: Dict) -> Dict:
    action = str(row.get("action", row.get("relevantLink", row.get("actions", ""))) or "")
    project = str(row.get("project", row.get("projects", "Applicable for all projects")) or "Applicable for all projects")
    comment = str(row.get("comment", row.get("blocker", "")) or "")
    status = _normalize_status(row.get("status", "Pending"))
    return {
        "source": "week0_tracker",
        "day": str(row.get("day", "") or ""),
        "activity": str(row.get("activity", "") or ""),
        "actions": action,
        "action": action,
        "relevantLink": action,
        "technology": str(row.get("technology", "Applicable for all") or "Applicable for all"),
        "projects": project,
        "project": project,
        "comment": comment,
        "status": status,
        "updatedAt": datetime.now(timezone.utc),
    }


async def _cleanup_tracker_row_employee_ids(collection) -> None:
    """Remove stale employee_id values from the tracker template rows collection."""
    await collection.update_many({"employee_id": {"$exists": True}}, {"$unset": {"employee_id": ""}})


async def _cleanup_null_tracker_activity_rows(collection) -> None:
    """Remove legacy activity rows that have blank/null key values, which can trigger duplicate-key collisions."""
    await collection.delete_many({
        "$or": [
            {"employee_id": {"$exists": False}},
            {"employee_id": None},
            {"employee_id": ""},
            {"activityid": {"$exists": False}},
            {"activityid": None},
            {"activityid": ""},
        ]
    })


async def _get_or_create_tracker_document() -> Dict:
    collection = MongoDB.get_collection("mongo_week0")
    document = await collection.find_one({"key": "default"})

    if document:
        rows = document.get("rows") or []
        first_row = rows[0] if rows else {}
        if rows and first_row.get("activity") == "ABLK Security Alert - Email Auto-Forwards - Compliance" and not document.get("updated_by"):
            await collection.update_one(
                {"key": "default"},
                {
                    "$set": {
                        "rows": [],
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )
            document["rows"] = []
        return document

    now = datetime.now(timezone.utc)
    seed_document = {
        "key": "default",
        "columns": DEFAULT_COLUMNS,
        "rows": DEFAULT_ROWS,
        "created_at": now,
        "updated_at": now,
    }
    await collection.insert_one(seed_document)
    return seed_document


async def _resolve_employee_ids(raw_employee_id: str | None) -> List[str]:
    values: List[str] = []
    seen = set()

    for candidate in [raw_employee_id]:
        if candidate is None:
            continue
        cleaned = str(candidate).strip()
        if not cleaned or cleaned.lower() in {"null", "none", "undefined"}:
            continue
        if cleaned not in seen:
            values.append(cleaned)
            seen.add(cleaned)

    if not values:
        return []

    employees_collection = MongoDB.get_collection("employees")
    for candidate in list(values):
        query = {
            "$or": [
                {"employee_id": candidate},
                {"user_id": candidate},
                {"user_id": ObjectId(candidate) if ObjectId.is_valid(candidate) else candidate},
                {"email": candidate},
                {"email_id": candidate},
            ]
        }
        if ObjectId.is_valid(candidate):
            query["$or"].append({"_id": ObjectId(candidate)})
        employee = await employees_collection.find_one(query, {"employee_id": 1, "user_id": 1})
        if not employee:
            continue

        actual_employee_id = str(employee.get("employee_id") or employee.get("_id") or "").strip()
        if actual_employee_id and actual_employee_id not in seen:
            values.insert(0, actual_employee_id)
            seen.add(actual_employee_id)

    return values


@router.get("/tracker", response_model=Week0TrackerResponse)
async def get_week0_tracker(
    day: str | None = Query(default=None),
    employeeId: str | None = Query(default=None),
    employee_id: str | None = Query(default=None),
    _: dict = Depends(get_current_user),
) -> Week0TrackerResponse:
    """Get Week0 tracker columns and rows from MongoDB."""
    try:
        document = await _get_or_create_tracker_document()
        columns = _normalize_columns(document.get("columns"))
        normalized_rows: List[Dict] = []

        seed_collection = MongoDB.get_collection("onboarding_tracker_rows")
        await _cleanup_tracker_row_employee_ids(seed_collection)
        await _ensure_vdi_activation_seed_row(seed_collection)
        selected_day = str(day or "").strip().lower().replace(" ", "").replace("-", "")
        if selected_day in {"week0", "week0a", "day0"}:
            day_filter = {
                "$or": [
                    {"day": {"$regex": "^week0$", "$options": "i"}},
                    {"day": {"$regex": "^week0-a$", "$options": "i"}},
                    {"day": {"$regex": "^day0$", "$options": "i"}},
                    {"day": {"$regex": "^day0-a$", "$options": "i"}},
                ],
                "$nor": [_vdi_activation_week0_row_query()],
            }
        elif selected_day == "vdiactivation":
            day_filter = {
                "$or": [
                    {"day": {"$regex": "^vdi[-_ ]?activation$", "$options": "i"}},
                    _vdi_activation_week0_row_query(),
                ]
            }
        elif selected_day:
            day_filter = {"day": {"$regex": f"^{day}$", "$options": "i"}}
        else:
            day_filter = {
                "$or": [
                    {"day": {"$regex": "^week0$", "$options": "i"}},
                    {"day": {"$regex": "^week0-a$", "$options": "i"}},
                    {"day": {"$regex": "^day0$", "$options": "i"}},
                    {"day": {"$regex": "^day0-a$", "$options": "i"}},
                    {"day": {"$regex": "^vdi[-_ ]?activation$", "$options": "i"}},
                    _vdi_activation_week0_row_query(),
                    {"day": {"$regex": "^day1$", "$options": "i"}},
                    {"day": {"$regex": "^day1-a$", "$options": "i"}},
                    {"day": {"$regex": "^day2$", "$options": "i"}},
                    {"day": {"$regex": "^day2-a$", "$options": "i"}},
                    {"day": {"$regex": "^day3$", "$options": "i"}},
                    {"day": {"$regex": "^day3-a$", "$options": "i"}},
                    {"day": {"$regex": "^day4$", "$options": "i"}},
                    {"day": {"$regex": "^day4-a$", "$options": "i"}},
                    {"day": {"$regex": "^day5$", "$options": "i"}},
                    {"day": {"$regex": "^day5-a$", "$options": "i"}},
                ]
            }

        seed_cursor = seed_collection.find(
            day_filter,
            {
                "_id": 0,
                "day": 1,
                "id": 1,
                "activity": 1,
                "relevantLink": 1,
                "actions": 1,
                "action": 1,
                "technology": 1,
                "project": 1,
                "projects": 1,
                "updatedAt": 1,
                "createdAt": 1,
            },
        ).sort([("updatedAt", -1), ("createdAt", -1), ("day", 1), ("id", 1), ("activity", 1)])
        seed_rows = await seed_cursor.to_list(length=1000)
        normalized_seed_rows = [_normalize_seed_row(row, idx + 1) for idx, row in enumerate(seed_rows)]
        normalized_rows = _deduplicate_seed_rows(normalized_seed_rows)

        resolved_employee_id = str(employeeId or employee_id or "").strip() or None
        resolved_employee_ids = await _resolve_employee_ids(resolved_employee_id)
        employee_activity_collection = MongoDB.get_collection("onboarding_employeeactivities_tracker")
        employee_tracker_rows: List[Dict] = []
        if resolved_employee_ids:
            employee_tracker_rows = await employee_activity_collection.find(
                {"employee_id": {"$in": resolved_employee_ids}},
                {
                    "_id": 0,
                    "employee_id": 1,
                    "activity": 1,
                    "status": 1,
                    "comment": 1,
                    "blocker": 1,
                    "day": 1,
                    "activityid": 1,
                    "updatedAt": 1,
                    "completedAt": 1,
                    "createdAt": 1,
                },
            ).to_list(length=1000)

        merge_employee_id = resolved_employee_ids[0] if len(resolved_employee_ids) == 1 else None
        merged_rows = _merge_employee_tracker_values(normalized_rows, employee_tracker_rows, employee_id=merge_employee_id)
        counts = _build_phase_counts(merged_rows)
        phase_completion_dates: Dict[str, datetime] = {}
        if merge_employee_id:
            onboarding_collection = MongoDB.get_collection("onboarding_employees")
            onboarding_record = await onboarding_collection.find_one(
                {"employee_id": merge_employee_id},
                {"_id": 0, "phase_completion_dates": 1},
            )
            stored_dates = (onboarding_record or {}).get("phase_completion_dates") or {}
            for day_number in range(1, 6):
                day_key = f"Day{day_number}"
                completion_date = _as_utc_datetime(stored_dates.get(day_key))
                if completion_date:
                    phase_completion_dates[day_key] = completion_date
        return Week0TrackerResponse(
            columns=columns,
            rows=merged_rows,
            counts=counts,
            phaseCompletionDates=phase_completion_dates,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tracker", response_model=Week0TrackerResponse)
async def update_week0_tracker(
    payload: Week0TrackerUpdate,
    current_user: dict = Depends(get_current_user),
) -> Week0TrackerResponse:
    """Update Week0 tracker columns and rows in MongoDB."""
    try:
        tracker_collection = MongoDB.get_collection("mongo_week0")
        seed_collection = MongoDB.get_collection("onboarding_tracker_rows")
        await _cleanup_tracker_row_employee_ids(seed_collection)
        employee_activity_collection = MongoDB.get_collection("onboarding_employeeactivities_tracker")
        employees_collection = MongoDB.get_collection("onboarding_employees")
        await _cleanup_null_tracker_activity_rows(employee_activity_collection)
        rows = [_normalize_row(row.model_dump()) for row in payload.rows]
        columns = _normalize_columns([column.model_dump() for column in payload.columns])
        target_employee_id = (
            str(payload.employeeId or payload.employee_id or payload.employeeCode or "").strip() or None
        )
        resolved_employee_ids = await _resolve_employee_ids(target_employee_id)
        resolved_target_employee_id = resolved_employee_ids[0] if resolved_employee_ids else None
        now = datetime.now(timezone.utc)

        stored_rows = []
        for row in rows:
            saved_row = await seed_collection.find_one_and_update(
                _row_filter(row),
                {
                    "$set": _row_document(row),
                    "$setOnInsert": {"createdAt": now},
                },
                upsert=True,
                return_document=True,
            )
            if saved_row:
                stored_rows.append(saved_row)
            else:
                stored_rows.append(await seed_collection.find_one(_row_filter(row)) or row)

        if resolved_target_employee_id:
            employee_rows = [{"employee_id": resolved_target_employee_id}]
        else:
            employee_rows = await employees_collection.find({"employee_id": {"$exists": True, "$ne": ""}}, {"employee_id": 1}).to_list(length=None)

        employee_activity_records = _build_employee_activity_records(employee_rows, stored_rows, employee_id=resolved_target_employee_id)
        update_employee_ids = [
            str(record.get("employee_id") or "").strip()
            for record in employee_activity_records
            if str(record.get("employee_id") or "").strip()
        ]
        existing_activity_rows = []
        if update_employee_ids:
            existing_activity_rows = await employee_activity_collection.find(
                {"employee_id": {"$in": update_employee_ids}},
                {
                    "_id": 0,
                    "employee_id": 1,
                    "activity": 1,
                    "day": 1,
                    "status": 1,
                    "completedAt": 1,
                    "updatedAt": 1,
                    "createdAt": 1,
                },
            ).to_list(length=None)
        employee_activity_updates = _build_employee_activity_updates(
            update_employee_ids,
            rows,
            stored_rows,
            existing_activity_rows,
            now,
        )
        await employee_activity_collection.create_index(
            [("employee_id", 1), ("activityid", 1)],
            unique=True,
            background=True,
            name="employee_activity_unique_idx",
        )

        for record in employee_activity_records:
            employee_id_value = str(record.get("employee_id") or "").strip()
            activity_id_value = str(record.get("activityid") or "").strip()
            if not employee_id_value or not activity_id_value:
                continue

            tracker_document = OnboardingEmployeeActivityTracker(
                employee_id=employee_id_value,
                activityid=activity_id_value,
                activity=record["activity"],
                status=record["status"],
                comment=record.get("comment") or "",
                day=record["day"],
            )
            tracker_payload = tracker_document.model_dump(exclude_none=True) if hasattr(tracker_document, "model_dump") else tracker_document.dict(exclude_none=True)
            await employee_activity_collection.update_one(
                {"employee_id": tracker_payload["employee_id"], "activityid": tracker_payload["activityid"]},
                {
                    "$set": {
                        **tracker_payload,
                        "updatedAt": now,
                    },
                    "$setOnInsert": {"createdAt": now},
                },
                upsert=True,
            )

        for record in employee_activity_updates:
            employee_id_value = str(record.get("employee_id") or "").strip()
            activity_id_value = str(record.get("activityid") or "").strip()
            if not employee_id_value or not activity_id_value:
                continue

            await employee_activity_collection.update_one(
                {"employee_id": employee_id_value, "activityid": activity_id_value},
                {
                    "$set": {
                        **record,
                        "updatedAt": now,
                    },
                    "$setOnInsert": {"createdAt": now},
                },
                upsert=True,
            )

        await tracker_collection.update_one(
            {"key": "default"},
            {
                "$set": {
                    "columns": columns,
                    "rows": rows,
                    "updated_at": now,
                    "updated_by": str(current_user.get("email") or current_user.get("_id") or "system"),
                },
                "$setOnInsert": {
                    "created_at": now,
                },
            },
            upsert=True,
        )

        counts = _build_phase_counts(rows)
        return Week0TrackerResponse(columns=columns, rows=rows, counts=counts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))