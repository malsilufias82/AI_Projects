"""
Migration script: Add new member fields to existing MongoDB users collection.

New fields added:
  - phone_number (str, optional)
  - employee_id (str, optional, indexed)
  - department (str, optional)
  - status (str, default "Active")
  - address (str, optional)
  - city (str, optional)
  - country (str, optional)
  - team_lead_id (str, optional, indexed) — references another user's _id
  - role_description (str, optional)
  - work_location (str, optional)
  - employment_type (str, optional)
  - client (str, optional)
  - project (str, optional)
  - vlinker (str, optional)
  - dev_qa (str, optional)
  - onboarding (str, optional)

Run:  docker compose exec api python scripts/migrate_add_member_fields.py
"""
import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.mongodb import MongoDB
from app.core.logging import configure_logging, get_logger

configure_logging(log_level="INFO", log_format="console")
logger = get_logger(__name__)

NEW_FIELDS = {
    "phone_number": None,
    "employee_id": None,
    "department": None,
    "status": "Active",
    "address": None,
    "city": None,
    "country": None,
    "team_lead_id": None,
    "role_description": None,
    "work_location": None,
    "employment_type": None,
    "client": None,
    "project": None,
    "vlinker": None,
    "dev_qa": None,
    "onboarding": None,
}


async def migrate():
    await MongoDB.connect()
    users = MongoDB.get_collection("users")

    existing_fields = set()
    sample = await users.find_one({}, {"_id": 0})
    if sample:
        existing_fields = set(sample.keys())

    missing_fields = {k: v for k, v in NEW_FIELDS.items() if k not in existing_fields}
    if not missing_fields:
        logger.info("All new fields already exist in the collection. No migration needed.")
        return

    updates = {"$set": {k: v for k, v in missing_fields.items() if v is not None}}
    unset_fields = {k: "" for k, v in missing_fields.items() if v is None}

    if unset_fields:
        updates["$setOnInsert"] = {}

    if updates:
        result = await users.update_many(
            {"$or": [{"deleted_at": None}, {"deleted_at": {"$exists": False}}]},
            {"$set": {k: v for k, v in missing_fields.items() if v is not None}},
        )
        logger.info(f"Added default values to {result.modified_count} user documents")

    for field in missing_fields:
        if missing_fields[field] is None:
            result = await users.update_many(
                {field: {"$exists": False}},
                {"$set": {field: None}},
            )
            logger.info(f"  Field '{field}': set to null for {result.modified_count} documents")
        else:
            result = await users.update_many(
                {field: {"$exists": False}},
                {"$set": {field: missing_fields[field]}},
            )
            logger.info(f"  Field '{field}': set default '{missing_fields[field]}' for {result.modified_count} documents")

    logger.info("Migration complete.")
    await MongoDB.disconnect()


if __name__ == "__main__":
    asyncio.run(migrate())
