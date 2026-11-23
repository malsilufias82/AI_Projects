from typing import List, Dict
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import get_current_user, require_permission
from app.core.exceptions import NotFoundException
from app.core.mongodb import MongoDB
from app.models.mongo_role import Role

router = APIRouter()


class RoleCreate(BaseModel):
    name: str
    display_name: str
    description: str = None
    permissions: List[str] = []


class RoleUpdate(BaseModel):
    display_name: str = None
    description: str = None
    permissions: List[str] = None


@router.get("", response_model=List[Dict])
async def get_all_roles(current_user: dict = Depends(require_permission("permissions", "view"))) -> List[Dict]:
    """Get all roles."""
    roles_collection = MongoDB.get_collection("roles")
    
    roles = await roles_collection.find({"deleted_at": None}).to_list(length=None)
    
    result = []
    for role in roles:
        role_id = str(role["_id"])
        
        # Get permission details
        permissions_collection = MongoDB.get_collection("permissions")
        permission_details = []
        for perm_id in role.get("permissions", []):
            # Convert string to ObjectId for query
            perm = await permissions_collection.find_one({"_id": ObjectId(perm_id)})
            if perm:
                permission_details.append({
                    "id": str(perm["_id"]),
                    "page": perm.get("page"),
                    "action": perm.get("action"),
                    "display_name": perm.get("display_name")
                })
        
        result.append({
            "id": role_id,
            "name": role.get("name"),
            "display_name": role.get("display_name"),
            "description": role.get("description"),
            "permissions": permission_details,
            "is_system": role.get("is_system", False),
            "is_default": role.get("is_default", False),
            "created_at": role.get("created_at"),
            "updated_at": role.get("updated_at")
        })
    
    return result


@router.post("", response_model=Dict)
async def create_role(role_data: RoleCreate, current_user: dict = Depends(require_permission("permissions", "add"))) -> Dict:
    """Create a new role."""
    roles_collection = MongoDB.get_collection("roles")
    
    # Check if role name already exists
    existing = await roles_collection.find_one({"name": role_data.name, "deleted_at": None})
    if existing:
        raise HTTPException(status_code=400, detail="Role with this name already exists")
    
    # Validate permissions exist
    permissions_collection = MongoDB.get_collection("permissions")
    valid_permissions = []
    for perm_id in role_data.permissions:
        perm = await permissions_collection.find_one({"_id": perm_id})
        if perm:
            valid_permissions.append(perm_id)
    
    # Create role
    role = Role(
        name=role_data.name,
        display_name=role_data.display_name,
        description=role_data.description,
        permissions=valid_permissions,
        is_system=False,
        is_default=False
    )
    
    result = await roles_collection.insert_one(role.to_mongo())
    
    return {
        "id": str(result.inserted_id),
        "name": role.name,
        "display_name": role.display_name,
        "description": role.description,
        "permissions": valid_permissions,
        "message": "Role created successfully"
    }


@router.get("/{role_id}", response_model=Dict)
async def get_role(role_id: str, current_user: dict = Depends(require_permission("permissions", "view"))) -> Dict:
    """Get a specific role by ID."""
    roles_collection = MongoDB.get_collection("roles")
    
    role = await roles_collection.find_one({"_id": ObjectId(role_id), "deleted_at": None})
    if not role:
        raise NotFoundException("Role not found")
    
    # Get permission details
    permissions_collection = MongoDB.get_collection("permissions")
    permission_details = []
    for perm_id in role.get("permissions", []):
        perm = await permissions_collection.find_one({"_id": ObjectId(perm_id)})
        if perm:
            permission_details.append({
                "id": str(perm["_id"]),
                "page": perm.get("page"),
                "action": perm.get("action"),
                "display_name": perm.get("display_name")
            })
    
    return {
        "id": str(role["_id"]),
        "name": role.get("name"),
        "display_name": role.get("display_name"),
        "description": role.get("description"),
        "permissions": permission_details,
        "is_system": role.get("is_system", False),
        "is_default": role.get("is_default", False),
        "created_at": role.get("created_at"),
        "updated_at": role.get("updated_at")
    }


@router.put("/{role_id}", response_model=Dict)
async def update_role(role_id: str, role_data: RoleUpdate, current_user: dict = Depends(require_permission("permissions", "modify"))) -> Dict:
    """Update a role."""
    roles_collection = MongoDB.get_collection("roles")
    
    role = await roles_collection.find_one({"_id": ObjectId(role_id), "deleted_at": None})
    if not role:
        raise NotFoundException("Role not found")
    
    if role.get("is_system", False):
        raise HTTPException(status_code=400, detail="Cannot modify system roles")
    
    # Build update data
    update_data = {}
    if role_data.display_name is not None:
        update_data["display_name"] = role_data.display_name
    if role_data.description is not None:
        update_data["description"] = role_data.description
    if role_data.permissions is not None:
        # Validate permissions exist
        permissions_collection = MongoDB.get_collection("permissions")
        valid_permissions = []
        for perm_id in role_data.permissions:
            perm = await permissions_collection.find_one({"_id": ObjectId(perm_id)})
            if perm:
                valid_permissions.append(perm_id)
        update_data["permissions"] = valid_permissions
    
    if update_data:
        await roles_collection.update_one(
            {"_id": ObjectId(role_id)},
            {"$set": update_data}
        )
    
    return {"message": "Role updated successfully"}


@router.delete("/{role_id}", response_model=Dict)
async def delete_role(role_id: str, current_user: dict = Depends(require_permission("permissions", "delete"))) -> Dict:
    """Delete a role."""
    roles_collection = MongoDB.get_collection("roles")
    
    role = await roles_collection.find_one({"_id": ObjectId(role_id), "deleted_at": None})
    if not role:
        raise NotFoundException("Role not found")
    
    if role.get("is_system", False):
        raise HTTPException(status_code=400, detail="Cannot delete system roles")
    
    # Soft delete
    await roles_collection.update_one(
        {"_id": ObjectId(role_id)},
        {"$set": {"deleted_at": "now()"}}
    )
    
    return {"message": "Role deleted successfully"}


@router.post("/{role_id}/permissions/{permission_id}", response_model=Dict)
async def add_permission_to_role(role_id: str, permission_id: str, current_user: dict = Depends(require_permission("permissions", "modify"))) -> Dict:
    """Add a permission to a role."""
    roles_collection = MongoDB.get_collection("roles")
    permissions_collection = MongoDB.get_collection("permissions")
    
    # Check role exists
    role = await roles_collection.find_one({"_id": ObjectId(role_id), "deleted_at": None})
    if not role:
        raise NotFoundException("Role not found")
    
    # Check permission exists
    permission = await permissions_collection.find_one({"_id": ObjectId(permission_id)})
    if not permission:
        raise NotFoundException("Permission not found")
    
    # Add permission if not already present
    current_permissions = role.get("permissions", [])
    if permission_id not in current_permissions:
        await roles_collection.update_one(
            {"_id": role_id},
            {"$push": {"permissions": permission_id}}
        )
    
    return {"message": "Permission added to role successfully"}


@router.delete("/{role_id}/permissions/{permission_id}", response_model=Dict)
async def remove_permission_from_role(role_id: str, permission_id: str, current_user: dict = Depends(require_permission("permissions", "modify"))) -> Dict:
    """Remove a permission from a role."""
    roles_collection = MongoDB.get_collection("roles")
    
    # Check role exists
    role = await roles_collection.find_one({"_id": ObjectId(role_id), "deleted_at": None})
    if not role:
        raise NotFoundException("Role not found")
    
    # Remove permission
    await roles_collection.update_one(
        {"_id": ObjectId(role_id)},
        {"$pull": {"permissions": permission_id}}
    )
    
    return {"message": "Permission removed from role successfully"}
