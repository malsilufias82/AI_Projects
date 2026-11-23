import sys
import argparse
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.mongodb import MongoDB
from app.models.mongo_user_permission import UserPermission
from app.models.mongo_permission import Permission
from app.models.mongo_user import User


async def add_permission_to_user(user_email: str, page: str, action: str, granted_by: str = None):
    """Add a permission to a user."""
    
    # Connect to MongoDB
    await MongoDB.connect()
    
    users_collection = MongoDB.get_collection("users")
    permissions_collection = MongoDB.get_collection("permissions")
    user_permissions_collection = MongoDB.get_collection("user_permissions")
    
    # Find user by email
    user = await users_collection.find_one({"email": user_email})
    if not user:
        print(f"Error: User with email '{user_email}' not found")
        await MongoDB.disconnect()
        return False
    
    user_id = str(user["_id"])
    print(f"Found user: {user.get('first_name', '')} {user.get('last_name', '')} ({user_email})")
    
    # Find permission by page and action
    permission = await permissions_collection.find_one({
        "page": page,
        "action": action
    })
    
    if not permission:
        print(f"Error: Permission for page '{page}' with action '{action}' not found")
        print("Available permissions:")
        all_permissions = permissions_collection.find({"enabled": True})
        async for perm in all_permissions:
            print(f"  - {perm['page']} - {perm['action']}")
        await MongoDB.disconnect()
        return False
    
    permission_id = str(permission["_id"])
    print(f"Found permission: {permission.get('display_name', page)} - {action}")
    
    # Check if user already has this permission
    existing = await user_permissions_collection.find_one({
        "user_id": user_id,
        "permission_id": permission_id
    })
    
    if existing:
        print(f"User already has this permission")
        await MongoDB.disconnect()
        return False
    
    # Create user permission
    user_permission = UserPermission(
        user_id=user_id,
        permission_id=permission_id,
        granted_by=granted_by
    )
    
    result = await user_permissions_collection.insert_one(user_permission.to_mongo())
    
    if result.inserted_id:
        print(f"Successfully added permission to user")
        print(f"  User: {user_email}")
        print(f"  Permission: {permission.get('display_name', page)} - {action}")
        print(f"  Granted by: {granted_by or 'System'}")
        await MongoDB.disconnect()
        return True
    else:
        print(f"Error: Failed to add permission")
        await MongoDB.disconnect()
        return False


async def list_user_permissions(user_email: str):
    """List all permissions for a user."""
    
    # Connect to MongoDB
    await MongoDB.connect()
    
    users_collection = MongoDB.get_collection("users")
    permissions_collection = MongoDB.get_collection("permissions")
    user_permissions_collection = MongoDB.get_collection("user_permissions")
    
    # Find user by email
    user = await users_collection.find_one({"email": user_email})
    if not user:
        print(f"Error: User with email '{user_email}' not found")
        await MongoDB.disconnect()
        return
    
    user_id = str(user["_id"])
    print(f"\nPermissions for {user.get('first_name', '')} {user.get('last_name', '')} ({user_email}):")
    print("-" * 60)
    
    # Get user permissions
    user_perms = user_permissions_collection.find({"user_id": user_id})
    permission_count = 0
    
    async for user_perm in user_perms:
        permission_id = user_perm["permission_id"]
        permission = await permissions_collection.find_one({"_id": permission_id})
        
        if permission:
            permission_count += 1
            print(f"  {permission_count}. {permission.get('display_name', permission['page'])} - {permission['action']}")
            print(f"     Page: {permission['page']}")
            print(f"     Route: {permission.get('route', 'N/A')}")
            print(f"     Granted at: {user_perm.get('granted_at', 'N/A')}")
            print()
    
    if permission_count == 0:
        print("  No permissions found")
    
    await MongoDB.disconnect()


async def remove_permission_from_user(user_email: str, page: str, action: str):
    """Remove a permission from a user."""
    
    # Connect to MongoDB
    await MongoDB.connect()
    
    users_collection = MongoDB.get_collection("users")
    permissions_collection = MongoDB.get_collection("permissions")
    user_permissions_collection = MongoDB.get_collection("user_permissions")
    
    # Find user by email
    user = await users_collection.find_one({"email": user_email})
    if not user:
        print(f"Error: User with email '{user_email}' not found")
        await MongoDB.disconnect()
        return False
    
    user_id = str(user["_id"])
    
    # Find permission by page and action
    permission = await permissions_collection.find_one({
        "page": page,
        "action": action
    })
    
    if not permission:
        print(f"Error: Permission for page '{page}' with action '{action}' not found")
        await MongoDB.disconnect()
        return False
    
    permission_id = str(permission["_id"])
    
    # Remove user permission
    result = await user_permissions_collection.delete_one({
        "user_id": user_id,
        "permission_id": permission_id
    })
    
    if result.deleted_count > 0:
        print(f"Successfully removed permission from user")
        print(f"  User: {user_email}")
        print(f"  Permission: {permission.get('display_name', page)} - {action}")
        await MongoDB.disconnect()
        return True
    else:
        print(f"Error: User did not have this permission")
        await MongoDB.disconnect()
        return False


if __name__ == "__main__":
    import asyncio
    
    parser = argparse.ArgumentParser(description="Manage user permissions")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Add permission command
    add_parser = subparsers.add_parser("add", help="Add permission to user")
    add_parser.add_argument("user_email", help="User email address")
    add_parser.add_argument("page", help="Page name (e.g., home, members, files)")
    add_parser.add_argument("action", help="Action (view, modify, add, delete)")
    add_parser.add_argument("--granted-by", help="Email of user granting permission")
    
    # List permissions command
    list_parser = subparsers.add_parser("list", help="List user permissions")
    list_parser.add_argument("user_email", help="User email address")
    
    # Remove permission command
    remove_parser = subparsers.add_parser("remove", help="Remove permission from user")
    remove_parser.add_argument("user_email", help="User email address")
    remove_parser.add_argument("page", help="Page name (e.g., home, members, files)")
    remove_parser.add_argument("action", help="Action (view, modify, add, delete)")
    
    args = parser.parse_args()
    
    if args.command == "add":
        asyncio.run(add_permission_to_user(args.user_email, args.page, args.action, args.granted_by))
    elif args.command == "list":
        asyncio.run(list_user_permissions(args.user_email))
    elif args.command == "remove":
        asyncio.run(remove_permission_from_user(args.user_email, args.page, args.action))
    else:
        parser.print_help()
