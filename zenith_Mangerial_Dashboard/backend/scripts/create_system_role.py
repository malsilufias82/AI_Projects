"""
Script to create a system role that cannot be deleted or modified.
System roles are protected and can only be modified through direct database operations.
"""
import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from bson import ObjectId
from app.core.config import settings
from app.core.mongodb import MongoDB
from app.models.mongo_role import Role


async def create_system_role(
    name: str,
    display_name: str,
    description: str = None,
    permissions: list = None
):
    """
    Create a system role with the given parameters.
    
    Args:
        name: Internal name for the role (e.g., 'super_admin')
        display_name: Human-readable name for the role
        description: Optional description of the role
        permissions: List of permission IDs to assign to the role
    """
    # Initialize MongoDB connection
    await MongoDB.connect()
    
    roles_collection = MongoDB.get_collection("roles")
    permissions_collection = MongoDB.get_collection("permissions")
    
    # Check if role already exists
    existing = await roles_collection.find_one({"name": name, "deleted_at": None})
    if existing:
        print(f"Role '{name}' already exists. Skipping creation.")
        return existing
    
    # Validate permissions if provided
    valid_permissions = []
    if permissions:
        for perm_id in permissions:
            try:
                # Handle both string and ObjectId
                if isinstance(perm_id, str):
                    perm = await permissions_collection.find_one({"_id": ObjectId(perm_id)})
                else:
                    perm = await permissions_collection.find_one({"_id": perm_id})
                
                if perm:
                    # Convert ObjectId to string for Role model
                    valid_permissions.append(str(perm["_id"]))
                else:
                    print(f"Warning: Permission {perm_id} not found, skipping")
            except Exception as e:
                print(f"Warning: Invalid permission ID {perm_id}: {e}")
    
    # Create system role
    role = Role(
        name=name,
        display_name=display_name,
        description=description,
        permissions=valid_permissions,
        is_system=True,  # This makes it a system role
        is_default=False
    )
    
    result = await roles_collection.insert_one(role.to_mongo())
    
    print(f"✅ System role '{display_name}' created successfully!")
    print(f"   Role ID: {result.inserted_id}")
    print(f"   Internal name: {name}")
    print(f"   Permissions assigned: {len(valid_permissions)}")
    print(f"   ⚠️  This role cannot be deleted or modified through the API")
    
    return result


async def create_super_admin_role():
    """Create a super admin system role with all permissions."""
    await MongoDB.connect()
    
    permissions_collection = MongoDB.get_collection("permissions")
    
    # Get all available permissions
    all_permissions = await permissions_collection.find({"enabled": True}).to_list(length=None)
    permission_ids = [perm["_id"] for perm in all_permissions]
    
    print(f"Found {len(permission_ids)} permissions to assign to super admin role")
    
    await create_system_role(
        name="super_admin",
        display_name="Super Admin",
        description="System administrator with full access to all features. This role cannot be deleted or modified.",
        permissions=permission_ids
    )


async def main():
    """Main function to run the script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create a system role")
    parser.add_argument("--name", help="Internal name for the role (required unless --super-admin)")
    parser.add_argument("--display-name", help="Human-readable name (required unless --super-admin)")
    parser.add_argument("--description", help="Role description")
    parser.add_argument("--permissions", nargs="*", help="Permission IDs to assign")
    parser.add_argument("--super-admin", action="store_true", help="Create super admin role with all permissions")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.super_admin:
        if args.name or args.display_name or args.permissions:
            print("⚠️  Warning: --name, --display-name, and --permissions are ignored when using --super-admin")
    else:
        if not args.name or not args.display_name:
            parser.error("--name and --display-name are required unless --super-admin is used")
    
    try:
        if args.super_admin:
            print("Creating Super Admin system role...")
            await create_super_admin_role()
        else:
            print(f"Creating system role: {args.display_name}")
            await create_system_role(
                name=args.name,
                display_name=args.display_name,
                description=args.description,
                permissions=args.permissions
            )
    except Exception as e:
        print(f"❌ Error creating system role: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
