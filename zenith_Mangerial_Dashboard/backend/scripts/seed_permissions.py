import json
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.mongodb import MongoDB
from app.models.mongo_permission import Permission, PermissionAction


async def seed_permissions():
    """Seed permissions from pages.json file."""
    
    # Connect to MongoDB
    await MongoDB.connect()
    
    # Load pages.json
    pages_json_path = Path(__file__).parent.parent.parent / "pages.json"
    
    if not pages_json_path.exists():
        print(f"Error: pages.json not found at {pages_json_path}")
        await MongoDB.disconnect()
        return
    
    with open(pages_json_path, 'r') as f:
        pages_data = json.load(f)
    
    permissions_collection = MongoDB.get_collection("permissions")
    
    actions = [PermissionAction.VIEW, PermissionAction.MODIFY, PermissionAction.ADD, PermissionAction.DELETE]
    
    created_count = 0
    skipped_count = 0
    
    for page in pages_data["pages"]:
        page_name = page["name"]
        display_name = page.get("display_name", page_name)
        description = page.get("description", "")
        category = page.get("category", "general")
        icon = page.get("icon", "apps")
        route = page.get("route", f"/{page_name}")
        order = page.get("order", 0)
        enabled = page.get("enabled", True)
        
        for action in actions:
            # Check if permission already exists
            existing = await permissions_collection.find_one({
                "page": page_name,
                "action": action.value
            })
            
            if existing:
                skipped_count += 1
                print(f"Skipped: {page_name} - {action.value} (already exists)")
            else:
                # Create new permission
                permission = Permission(
                    page=page_name,
                    display_name=display_name,
                    category=category,
                    icon=icon,
                    route=route,
                    order=order,
                    enabled=enabled,
                    action=action,
                    description=f"{description} - {action.value}"
                )
                
                result = await permissions_collection.insert_one(permission.to_mongo())
                created_count += 1
                print(f"Created: {page_name} - {action.value}")
    
    print(f"\nSummary:")
    print(f"Created: {created_count} permissions")
    print(f"Skipped: {skipped_count} permissions (already exist)")
    
    # Disconnect from MongoDB
    await MongoDB.disconnect()


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_permissions())
