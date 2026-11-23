from typing import List, Union
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from bson import ObjectId

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.mongodb import MongoDB
from app.core.security import decode_token
from app.models.mongo_user import UserRole
from app.models.mongo_permission import PermissionAction
from app.services.mongo_user_service import MongoUserService

http_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> dict:
    if credentials is None:
        raise UnauthorizedException("Missing authentication credentials.")

    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise UnauthorizedException("Invalid token payload.")

    except JWTError:
        raise UnauthorizedException("Could not validate credentials.")

    user_service = MongoUserService()
    user = await user_service.get_by_id(user_id)

    if user is None:
        raise UnauthorizedException("User not found.")
    if not user.get("is_active", True):
        raise UnauthorizedException("User account is inactive.")

    return user


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if not current_user.get("is_active", True):
        raise UnauthorizedException("Inactive user.")
    return current_user


def require_roles(*roles: UserRole):
    async def _role_checker(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        user_role = current_user.get("role", UserRole.USER)
        if user_role not in roles:
            raise ForbiddenException(
                "You do not have permission to perform this action."
            )
        return current_user

    return _role_checker


require_admin = require_roles(UserRole.ADMIN)
require_user = require_roles(UserRole.USER)


async def get_user_permissions(user_id: str) -> List[str]:
    """Get user's permission IDs."""
    user_permissions_collection = MongoDB.get_collection("user_permissions")
    user_permissions = await user_permissions_collection.find({"user_id": user_id}).to_list(length=None)
    return [up["permission_id"] for up in user_permissions]


async def check_permission(page: str, action: Union[str, PermissionAction], current_user: dict = Depends(get_current_user)) -> dict:
    """Check if user has specific permission for a page and action."""
    user_id = str(current_user["_id"])
    
    # Get user's permission IDs
    permission_ids = await get_user_permissions(user_id)
    
    if not permission_ids:
        raise ForbiddenException(f"You do not have permission to {action} on {page}.")
    
    # Get the specific permission
    permissions_collection = MongoDB.get_collection("permissions")
    action_value = action.value if isinstance(action, PermissionAction) else action
    
    required_permission = await permissions_collection.find_one({
        "page": page,
        "action": action_value,
        "enabled": True
    })
    
    if not required_permission:
        raise ForbiddenException(f"Permission {action} on {page} does not exist or is disabled.")
    
    required_permission_id = str(required_permission["_id"])
    
    # Check if user has this permission (compare as strings since permission_ids are strings)
    if required_permission_id not in permission_ids:
        raise ForbiddenException(f"You do not have permission to {action} on {page}.")
    
    return current_user


def require_permission(page: str, action: Union[str, PermissionAction]):
    """Dependency factory to require specific permission."""
    async def _permission_checker(current_user: dict = Depends(get_current_user)) -> dict:
        return await check_permission(page, action, current_user)
    return _permission_checker


def require_any_permission(*permission_requirements: tuple):
    """Require user to have at least one of the specified permissions.
    
    Args:
        *permission_requirements: Tuple of (page, action) pairs
    """
    async def _any_permission_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_id = str(current_user["_id"])
        permission_ids = await get_user_permissions(user_id)
        
        if not permission_ids:
            raise ForbiddenException("You do not have any required permissions.")
        
        permissions_collection = MongoDB.get_collection("permissions")
        
        for page, action in permission_requirements:
            action_value = action.value if isinstance(action, PermissionAction) else action
            required_permission = await permissions_collection.find_one({
                "page": page,
                "action": action_value,
                "enabled": True
            })
            
            if required_permission and str(required_permission["_id"]) in permission_ids:
                return current_user
        
        raise ForbiddenException("You do not have any of the required permissions.")
    
    return _any_permission_checker
