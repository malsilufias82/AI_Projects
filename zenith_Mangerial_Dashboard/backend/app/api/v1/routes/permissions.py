from typing import List, Dict, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth.dependencies import get_current_user, require_permission
from app.core.exceptions import NotFoundException
from app.core.mongodb import MongoDB

router = APIRouter()


class PermissionUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None


@router.get("/all", response_model=List[Dict])
async def get_all_permissions_with_counts(current_user: dict = Depends(require_permission("permissions", "view"))) -> List[Dict]:
    """Get all permissions with user assignment counts."""
    permissions_collection = MongoDB.get_collection("permissions")
    user_permissions_collection = MongoDB.get_collection("user_permissions")
    
    # Get all enabled permissions
    permissions = await permissions_collection.find({"enabled": True}).to_list(length=None)
    
    result = []
    
    for perm in permissions:
        perm_id = str(perm["_id"])
        
        # Count how many users have this permission
        assignment_count = await user_permissions_collection.count_documents({"permission_id": perm_id})
        
        result.append({
            "id": perm_id,
            "page": perm.get("page"),
            "action": perm.get("action"),
            "display_name": perm.get("display_name"),
            "description": perm.get("description"),
            "category": perm.get("category"),
            "icon": perm.get("icon"),
            "route": perm.get("route"),
            "order": perm.get("order"),
            "enabled": perm.get("enabled"),
            "total_assigned": assignment_count
        })
    
    # Sort by page, then by action
    result.sort(key=lambda x: (x.get("page", ""), x.get("action", "")))
    
    return result


@router.get("/{permission_id}/assignments", response_model=List[Dict])
async def get_permission_assignments(permission_id: str, current_user: dict = Depends(require_permission("permissions", "view"))) -> List[Dict]:
    """Get all users and roles that have this permission."""
    user_permissions_collection = MongoDB.get_collection("user_permissions")
    users_collection = MongoDB.get_collection("users")
    roles_collection = MongoDB.get_collection("roles")
    
    result = []
    
    # Get direct user assignments
    user_assignments = user_permissions_collection.find({"permission_id": permission_id})
    async for assignment in user_assignments:
        user_id = assignment["user_id"]
        # Try to find user by ObjectId or UUID
        try:
            user = await users_collection.find_one({"_id": ObjectId(user_id)})
        except:
            user = await users_collection.find_one({"_id": user_id})
        
        if user:
            result.append({
                "type": "user",
                "id": str(user["_id"]),
                "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user.get("email", ""),
                "email": user.get("email"),
                "assignment_type": "direct"
            })
    
    # Get role assignments
    roles = await roles_collection.find({"permissions": permission_id, "deleted_at": None}).to_list(length=None)
    for role in roles:
        result.append({
            "type": "role",
            "id": str(role["_id"]),
            "name": role.get("display_name", role.get("name")),
            "description": role.get("description"),
            "assignment_type": "role"
        })
    
    return result


@router.put("/{permission_id}", response_model=Dict)
async def update_permission(permission_id: str, data: PermissionUpdate, current_user: dict = Depends(require_permission("permissions", "modify"))) -> Dict:
    """Update a permission."""
    permissions_collection = MongoDB.get_collection("permissions")
    
    permission = await permissions_collection.find_one({"_id": ObjectId(permission_id)})
    if not permission:
        raise NotFoundException("Permission not found")
    
    update_data = {}
    if data.display_name is not None:
        update_data["display_name"] = data.display_name
    if data.description is not None:
        update_data["description"] = data.description
    if data.enabled is not None:
        update_data["enabled"] = data.enabled
    
    if update_data:
        await permissions_collection.update_one(
            {"_id": ObjectId(permission_id)},
            {"$set": update_data}
        )
    
    return {"message": "Permission updated successfully"}


@router.delete("/{permission_id}", response_model=Dict)
async def delete_permission(permission_id: str, current_user: dict = Depends(require_permission("permissions", "delete"))) -> Dict:
    """Delete a permission."""
    permissions_collection = MongoDB.get_collection("permissions")
    user_permissions_collection = MongoDB.get_collection("user_permissions")
    roles_collection = MongoDB.get_collection("roles")
    
    permission = await permissions_collection.find_one({"_id": ObjectId(permission_id)})
    if not permission:
        raise NotFoundException("Permission not found")
    
    # Check if permission is assigned to any users
    user_count = await user_permissions_collection.count_documents({"permission_id": permission_id})
    if user_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete permission assigned to {user_count} users. Remove assignments first."
        )
    
    # Check if permission is assigned to any roles
    role_count = await roles_collection.count_documents({"permissions": permission_id})
    if role_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete permission assigned to {role_count} roles. Remove from roles first."
        )
    
    # Delete the permission
    await permissions_collection.delete_one({"_id": ObjectId(permission_id)})
    
    return {"message": "Permission deleted successfully"}
