"""Import onboarding employees and activities from the BLK tracker workbook."""

import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from openpyxl import load_workbook


TRACKED_DAYS = {
    "week0": "Week0",
    "week0a": "Week0",
    "day0": "Week0",
    "day0a": "Week0",
    "day1": "Day1",
    "day1a": "Day1",
    "day2": "Day2",
    "day2a": "Day2",
    "day3": "Day3",
    "day3a": "Day3",
    "day4": "Day4",
    "day4a": "Day4",
    "day5": "Day5",
    "day5a": "Day5",
}


def clean_value(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()[:10]
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    cleaned = str(value).strip()
    return cleaned or None


def _normalize_day(value: Any) -> str | None:
    raw_day = clean_value(value)
    if not raw_day:
        return None
    key = re.sub(r"[\s_-]+", "", raw_day).casefold()
    return TRACKED_DAYS.get(key)


def _resource_vlinker_labels(workbook_path: Path) -> set[str]:
    workbook = load_workbook(workbook_path, data_only=True, read_only=True)
    try:
        resource_sheet = workbook["Resource List"]
        headers = [clean_value(cell.value) or "" for cell in resource_sheet[2]]
        try:
            vlinker_index = next(index for index, header in enumerate(headers) if header.casefold() == "vlinker")
        except StopIteration:
            return set()

        return {
            value
            for row in resource_sheet.iter_rows(min_row=3, values_only=True)
            if vlinker_index < len(row)
            if (value := clean_value(row[vlinker_index]))
        }
    finally:
        workbook.close()


def parse_blk_workbook(workbook_path: Path) -> tuple[list[dict], list[dict], list[dict]]:
    workbook = load_workbook(workbook_path, data_only=True, read_only=True)
    if "Resource List" not in workbook.sheetnames or "Phase1 - Machine Setup" not in workbook.sheetnames:
        workbook.close()
        raise ValueError("Workbook must contain Resource List and Phase1 - Machine Setup sheets")

    phase_sheet = workbook["Phase1 - Machine Setup"]
    employees_by_name: dict[str, dict] = {}
    for col_index in range(9, phase_sheet.max_column + 1):
        full_name = clean_value(phase_sheet.cell(row=2, column=col_index).value)
        if not full_name:
            continue
        key = full_name.casefold()
        employees_by_name.setdefault(key, {
            "full_name": full_name,
            "source_employee_name": full_name,
            "source_system": "blk_onboarding_tracker",
        })

    if not employees_by_name:
        workbook.close()
        raise ValueError("Phase1 - Machine Setup does not contain employee names in row 2")

    employees = list(employees_by_name.values())
    onboarding = [
        {
            "source_employee_name": employee["source_employee_name"],
            "credential_status": "Pending",
            "bgv_status": "Pending",
            "vcf_status": "Pending",
            "onboarding_status": "Pending",
            "remarks": "",
        }
        for employee in employees
    ]

    activities = []
    for row_index in range(6, phase_sheet.max_row + 1):
        day = _normalize_day(phase_sheet.cell(row=row_index, column=2).value)
        activity_action = clean_value(phase_sheet.cell(row=row_index, column=4).value)
        if not day or not activity_action:
            continue
        area = clean_value(phase_sheet.cell(row=row_index, column=3).value)
        how_to = clean_value(phase_sheet.cell(row=row_index, column=5).value)
        activity = f"{area}: {activity_action}" if area else activity_action
        activities.append({
            "day": day,
            "activity": activity,
            "action": how_to or activity_action,
            "relevantLink": how_to or activity_action,
            "technology": "Applicable for all",
            "project": "Applicable for all projects",
            "projects": "Applicable for all projects",
            "status": "Pending",
            "comment": "",
        })

    workbook.close()
    return employees, onboarding, activities


async def import_blk_workbook(workbook_path: Path) -> dict[str, int]:
    employees, onboarding_records, activities = parse_blk_workbook(workbook_path)
    resource_vlinker_labels = _resource_vlinker_labels(workbook_path)
    from app.core.config import settings
    from motor.motor_asyncio import AsyncIOMotorClient

    client = AsyncIOMotorClient(
        settings.MONGODB_URL,
        maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
        minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
    )
    try:
        await client.admin.command("ping")
        database = client[settings.MONGODB_DATABASE]
        employees_collection = database["employees"]
        onboarding_collection = database["onboarding_employees"]
        activity_collection = database["onboarding_tracker_rows"]
        inserted_employees = 0
        updated_employees = 0
        inserted_onboarding = 0
        inserted_activities = 0
        archived_role_employees = 0
        now = datetime.now(timezone.utc)

        for role_label in resource_vlinker_labels:
            legacy_role_employees = await employees_collection.find({
                "vlinker": role_label,
                "full_name": role_label,
                "employee_id": {"$in": [None, ""]},
                "user_id": {"$in": [None, ""]},
                "email": {"$in": [None, ""]},
                "email_id": {"$in": [None, ""]},
                "deleted_at": None,
            }, {"_id": 1}).to_list(length=20)
            for legacy_employee in legacy_role_employees:
                employee_doc_id = legacy_employee["_id"]
                await employees_collection.update_one(
                    {"_id": employee_doc_id},
                    {"$set": {
                        "deleted_at": now,
                        "is_deleted": True,
                        "archive_reason": "Resource List VLinker is a role label, not an employee identity",
                        "updated_at": now,
                    }},
                )
                await onboarding_collection.update_many(
                    {
                        "employee_id": str(employee_doc_id),
                        "created_by": "BLK onboarding tracker import",
                        "deleted_at": None,
                    },
                    {"$set": {"deleted_at": now, "updated_at": now}},
                )
                archived_role_employees += 1

        for employee, source_record in zip(employees, onboarding_records):
            employee_name = employee["source_employee_name"]
            existing = await employees_collection.find_one({
                "source_system": "blk_onboarding_tracker",
                "source_employee_name": employee_name,
            })
            imported_fields = dict(employee)
            if existing:
                await employees_collection.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        **imported_fields,
                        "deleted_at": None,
                        "is_deleted": False,
                        "updated_at": now,
                    }},
                )
                employee_doc_id = existing["_id"]
                updated_employees += 1
            else:
                result = await employees_collection.insert_one({
                    **imported_fields,
                    "created_at": now,
                    "updated_at": now,
                    "is_deleted": False,
                    "deleted_at": None,
                    "employee_id": None,
                    "client": None,
                    "project": None,
                    "team_lead": None,
                })
                employee_doc_id = result.inserted_id
                inserted_employees += 1

            onboarding_key = str(employee_doc_id)
            onboarding_payload = dict(source_record)
            onboarding_payload.update({
                "employee_id": onboarding_key,
                "created_at": now,
                "created_by": "BLK Phase1 name import",
            })
            result = await onboarding_collection.update_one(
                {"employee_id": onboarding_key},
                {"$setOnInsert": onboarding_payload},
                upsert=True,
            )
            if result.upserted_id:
                inserted_onboarding += 1

        for activity_index, activity in enumerate(activities, start=1):
            identity_filter = {
                "day": activity["day"],
                "activity": activity["activity"],
                "technology": activity["technology"],
                "$or": [
                    {"actions": activity["action"]},
                    {"action": activity["action"]},
                    {"relevantLink": activity["action"]},
                ],
            }
            if await activity_collection.find_one(identity_filter, {"_id": 1}):
                continue
            now = datetime.now(timezone.utc)
            await activity_collection.insert_one({
                **activity,
                "id": activity_index,
                "actions": activity["action"],
                "source": "week0_tracker",
                "createdAt": now,
                "updatedAt": now,
            })
            inserted_activities += 1

        return {
            "employees_inserted": inserted_employees,
            "employees_updated": updated_employees,
            "onboarding_records_inserted": inserted_onboarding,
            "activities_inserted": inserted_activities,
            "role_label_employees_archived": archived_role_employees,
        }
    finally:
        client.close()
