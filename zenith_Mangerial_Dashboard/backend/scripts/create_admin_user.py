#!/usr/bin/env python3
"""
Script to create the first admin user directly in MongoDB.
Run this script to set up the initial admin account for the application.
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from getpass import getpass
from bson import ObjectId
from datetime import datetime, timezone
from uuid import uuid4

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.mongodb import MongoDB
from app.core.security import hash_password
from app.core.logging import configure_logging, get_logger
from app.models.mongo_permission import Permission, PermissionAction

configure_logging(log_level="INFO", log_format="json")
logger = get_logger(__name__)


async def seed_permissions_if_empty():
    """Seed permissions from pages.json if the permissions collection is empty."""
    try:
        permissions_collection = MongoDB.get_collection("permissions")
        existing_count = await permissions_collection.count_documents({})

        if existing_count > 0:
            logger.info(f"Permissions already seeded ({existing_count} found), skipping")
            return existing_count

        # Load pages.json
        pages_json_path = Path(__file__).parent.parent.parent / "pages.json"
        if not pages_json_path.exists():
            logger.warning(f"pages.json not found at {pages_json_path}, skipping permission seeding")
            return 0

        with open(pages_json_path, 'r') as f:
            pages_data = json.load(f)

        actions = [PermissionAction.VIEW, PermissionAction.MODIFY, PermissionAction.ADD, PermissionAction.DELETE]

        created_count = 0
        for page in pages_data["pages"]:
            if not page.get("enabled", True):
                continue

            page_name = page["name"]
            display_name = page.get("display_name", page_name)
            category = page.get("category", "general")
            icon = page.get("icon", "page")
            route = page.get("route", f"/{page_name}")
            order = page.get("order", 0)
            description = page.get("description", "")

            for action in actions:
                permission = Permission(
                    page=page_name,
                    display_name=display_name,
                    category=category,
                    icon=icon,
                    route=route,
                    order=order,
                    enabled=True,
                    action=action,
                    description=f"{description} - {action.value}"
                )

                await permissions_collection.insert_one(permission.to_mongo())
                created_count += 1
                logger.info(f"Created permission: {page_name} - {action.value}")

        logger.info(f"Permission seeding complete: {created_count} created")
        return created_count
    except Exception as e:
        logger.error(f"Error seeding permissions: {e}")
        raise


async def assign_admin_role_to_user(user_id: str):
    """Assign an admin role to the user via user_roles collection."""
    try:
        roles_collection = MongoDB.get_collection("roles")
        user_roles_collection = MongoDB.get_collection("user_roles")

        # Look for an admin/super admin role
        admin_role = await roles_collection.find_one({
            "name": {"$regex": "^(admin|super_admin|superadmin)$", "$options": "i"},
            "deleted_at": None
        })

        if not admin_role:
            # Create a Super Admin role if none exists
            permissions_collection = MongoDB.get_collection("permissions")
            permissions = await permissions_collection.find({"enabled": True}).to_list(length=None)
            permission_ids = [str(p["_id"]) for p in permissions]

            role_id = str(uuid4())
            role_document = {
                "_id": role_id,
                "name": "super_admin",
                "display_name": "Super Administrator",
                "description": "Full system access with all permissions",
                "permissions": permission_ids,
                "is_system": True,
                "is_default": False,
                "deleted_at": None,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            await roles_collection.insert_one(role_document)
            admin_role = role_document
            logger.info(f"Created Super Admin role with ID: {role_id}")

        role_id = str(admin_role["_id"])

        # Check if user already has this role
        existing = await user_roles_collection.find_one({
            "user_id": user_id,
            "role_id": role_id
        })

        if not existing:
            await user_roles_collection.insert_one({
                "user_id": user_id,
                "role_id": role_id,
                "created_at": datetime.now(timezone.utc),
            })
            logger.info(f"Assigned admin role '{role_id}' to user {user_id}")
        else:
            logger.info(f"User {user_id} already has admin role '{role_id}'")

    except Exception as e:
        logger.error(f"Error assigning admin role: {e}")
        raise


async def grant_all_permissions_to_user(user_id: str):
    """Grant all available permissions to a user."""
    try:
        permissions_collection = MongoDB.get_collection("permissions")
        user_permissions_collection = MongoDB.get_collection("user_permissions")

        # Get all permissions
        permissions = await permissions_collection.find({"enabled": True}).to_list(length=None)

        granted_count = 0
        for permission in permissions:
            permission_id = str(permission["_id"])

            # Check if user already has this permission
            existing = await user_permissions_collection.find_one({
                "user_id": user_id,
                "permission_id": permission_id
            })

            if not existing:
                user_permission = {
                    "_id": str(uuid4()),
                    "user_id": user_id,
                    "permission_id": permission_id,
                    "granted_at": datetime.now(timezone.utc),
                    "granted_by": user_id  # Self-granted for admin
                }

                await user_permissions_collection.insert_one(user_permission)
                granted_count += 1
                logger.info(f"Granted permission: {permission['page']} - {permission['action']}")

        logger.info(f"Granted {granted_count} permissions to user {user_id}")
        return granted_count
    except Exception as e:
        logger.error(f"Error granting permissions: {e}")
        raise


async def create_admin_user():
    """Create an admin user in MongoDB."""

    # Connect to MongoDB
    try:
        await MongoDB.connect()
        logger.info("Connected to MongoDB successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

    try:
        # Seed permissions if empty (needed for admin to see pages)
        await seed_permissions_if_empty()

        # Get user input
        print("\n=== Create Admin User ===")
        email = input("Enter admin email: ").strip()

        if not email:
            logger.error("Email is required")
            sys.exit(1)

        password = getpass("Enter admin password: ")
        if not password:
            logger.error("Password is required")
            sys.exit(1)

        confirm_password = getpass("Confirm admin password: ")
        if password != confirm_password:
            logger.error("Passwords do not match")
            sys.exit(1)

        first_name = input("Enter first name (optional): ").strip() or "Admin"
        last_name = input("Enter last name (optional): ").strip() or "User"

        # Check if user already exists
        collection = MongoDB.get_collection("users")
        existing_user = await collection.find_one({"email": email})

        if existing_user:
            logger.warning(f"User with email '{email}' already exists")
            overwrite = input("Do you want to overwrite this user? (y/N): ").strip().lower()
            if overwrite != 'y':
                logger.info("Operation cancelled")
                sys.exit(0)

            # Delete existing user
            await collection.delete_one({"email": email})
            logger.info(f"Deleted existing user with email '{email}'")

        # Create new admin user
        user_document = {
            "_id": str(uuid4()),
            "email": email,
            "hashed_password": hash_password(password),
            "first_name": first_name,
            "last_name": last_name,
            "is_active": True,
            "role": "admin",
            "is_deleted": False,
            "deleted_at": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        result = await collection.insert_one(user_document)

        if result.inserted_id:
            user_id = str(result.inserted_id)
            logger.info(f"Admin user created successfully with ID: {user_id}")
            logger.info(f"Email: {email}")
            logger.info(f"Role: admin")

            # Grant all permissions to admin user
            await grant_all_permissions_to_user(user_id)

            # Assign admin role to user via user_roles collection
            await assign_admin_role_to_user(user_id)

            print("\n✓ Admin user created successfully!")
            print(f"  Email: {email}")
            print(f"  Role: admin")
            print(f"  ID: {user_id}")
            print(f"  Permissions: All permissions granted")
        else:
            logger.error("Failed to create admin user")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        sys.exit(1)
    finally:
        # Disconnect from MongoDB
        await MongoDB.disconnect()
        logger.info("Disconnected from MongoDB")


async def create_admin_user_with_defaults(email: str, password: str, first_name: str = "Admin", last_name: str = "User"):
    """Create admin user with provided credentials (non-interactive)."""

    # Connect to MongoDB
    try:
        await MongoDB.connect()
        logger.info("Connected to MongoDB successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        sys.exit(1)

    try:
        # Seed permissions if empty
        await seed_permissions_if_empty()

        # Check if user already exists
        collection = MongoDB.get_collection("users")
        existing_user = await collection.find_one({"email": email})

        if existing_user:
            logger.warning(f"User with email '{email}' already exists, skipping creation")
            return

        # Create new admin user
        user_document = {
            "_id": str(uuid4()),
            "email": email,
            "hashed_password": hash_password(password),
            "first_name": first_name,
            "last_name": last_name,
            "is_active": True,
            "role": "admin",
            "is_deleted": False,
            "deleted_at": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        result = await collection.insert_one(user_document)

        if result.inserted_id:
            user_id = str(result.inserted_id)
            logger.info(f"Admin user created successfully with ID: {user_id}")
            logger.info(f"Email: {email}")

            # Grant all permissions to admin user
            await grant_all_permissions_to_user(user_id)

            # Assign admin role to user via user_roles collection
            await assign_admin_role_to_user(user_id)
        else:
            logger.error("Failed to create admin user")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        sys.exit(1)
    finally:
        # Disconnect from MongoDB
        await MongoDB.disconnect()
        logger.info("Disconnected from MongoDB")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create admin user in MongoDB")
    parser.add_argument("--email", help="Admin email (if not provided, will prompt)")
    parser.add_argument("--password", help="Admin password (if not provided, will prompt)")
    parser.add_argument("--first-name", help="Admin first name (default: 'Admin')", default="Admin")
    parser.add_argument("--last-name", help="Admin last name (default: 'User')", default="User")

    args = parser.parse_args()

    if args.email and args.password:
        # Non-interactive mode
        asyncio.run(create_admin_user_with_defaults(args.email, args.password, args.first_name, args.last_name))
    else:
        # Interactive mode
        asyncio.run(create_admin_user())
