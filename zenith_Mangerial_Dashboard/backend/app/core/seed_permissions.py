import json
from pathlib import Path

from app.core.logging import get_logger
from app.core.mongodb import MongoDB
from app.models.mongo_permission import Permission, PermissionAction

logger = get_logger(__name__)


async def seed_permissions():
    """Seed permissions from pages.json file."""
    pages_json_path = Path(__file__).parent.parent.parent.parent / "pages.json"
    
    if not pages_json_path.exists():
        logger.warning(f"pages.json not found at {pages_json_path}, skipping permission seeding")
        return
    
    with open(pages_json_path, 'r') as f:
        pages_data = json.load(f)
    
    permissions_collection = MongoDB.get_collection("permissions")
    
    actions = [PermissionAction.VIEW, PermissionAction.MODIFY, PermissionAction.ADD, PermissionAction.DELETE]
    
    created_count = 0
    skipped_count = 0
    
    for page in pages_data["pages"]:
        # Skip if page is not enabled
        if not page.get("enabled", True):
            logger.info(f"Skipping disabled page: {page['name']}")
            continue
        
        page_name = page["name"]
        display_name = page.get("display_name", page_name)
        category = page.get("category", "general")
        icon = page.get("icon", "page")
        route = page.get("route", f"/{page_name}")
        order = page.get("order", 0)
        description = page.get("description", "")
        
        for action in actions:
            # Check if permission already exists
            existing = await permissions_collection.find_one({
                "page": page_name,
                "action": action.value
            })
            
            if existing:
                skipped_count += 1
            else:
                # Create new permission
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
    
    logger.info(f"Permission seeding complete: {created_count} created, {skipped_count} skipped")
