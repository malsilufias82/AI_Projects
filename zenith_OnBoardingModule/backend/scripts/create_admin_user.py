#!/usr/bin/env python3
"""
Script to create the first admin user directly in MongoDB.
Run this script to set up the initial admin account for the application.
"""

import asyncio
import sys
import os
from pathlib import Path
from getpass import getpass

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.mongodb import MongoDB
from app.core.security import hash_password
from app.core.logging import configure_logging, get_logger

configure_logging(log_level="INFO", log_format="json")
logger = get_logger(__name__)


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
                from datetime import datetime, timezone
                from uuid import uuid4
                
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
        from datetime import datetime, timezone
        from uuid import uuid4
        
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
        # Check if user already exists
        collection = MongoDB.get_collection("users")
        existing_user = await collection.find_one({"email": email})
        
        if existing_user:
            logger.warning(f"User with email '{email}' already exists, skipping creation")
            return
        
        # Create new admin user
        from datetime import datetime, timezone
        from uuid import uuid4
        
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
