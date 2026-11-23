from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from pydantic import BaseModel

from app.auth.handlers import generate_token_pair, refresh_access_token
from app.auth.dependencies import get_current_user
from app.core.logging import get_logger
from app.core.mongodb import MongoDB
from app.core.security import hash_password
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from app.schemas.base import MessageResponse
from app.services.mongo_user_service import MongoUserService

logger = get_logger(__name__)

router = APIRouter()


class SetPasswordRequest(BaseModel):
    """Request model for setting password."""
    token: str
    password: str


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
) -> TokenResponse:
    user_service = MongoUserService()
    user = await user_service.authenticate(data.email, data.password)
    return generate_token_pair(str(user["_id"]))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest) -> TokenResponse:
    return refresh_access_token(data.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout() -> MessageResponse:
    return MessageResponse(message="Successfully logged out.")


@router.get("/permissions", response_model=List[dict])
async def get_user_permissions(current_user: dict = Depends(get_current_user)) -> List[dict]:
    """Get current user's permissions."""
    user_id = str(current_user["_id"])
    user_permissions_collection = MongoDB.get_collection("user_permissions")
    permissions_collection = MongoDB.get_collection("permissions")
    
    # Get user's permission IDs
    user_permissions = await user_permissions_collection.find({"user_id": user_id}).to_list(length=None)
    permission_ids = [up["permission_id"] for up in user_permissions]
    
    if not permission_ids:
        return []
    
    # Convert string IDs to ObjectIds for MongoDB query
    object_ids = [ObjectId(pid) for pid in permission_ids]
    
    # Get full permission details
    permissions = await permissions_collection.find({
        "_id": {"$in": object_ids},
        "enabled": True
    }).to_list(length=None)
    
    # Convert to list of dicts with string IDs
    result = []
    for perm in permissions:
        perm_dict = dict(perm)
        perm_dict["id"] = str(perm_dict["_id"])
        del perm_dict["_id"]
        result.append(perm_dict)
    
    return result


@router.post("/set-password", response_model=MessageResponse)
async def set_password(data: SetPasswordRequest) -> MessageResponse:
    """
    Set password for a user using their user ID as token.
    
    This endpoint is used when a user clicks the password setup link from their email.
    """
    users_collection = MongoDB.get_collection("users")
    
    try:
        user_id = data.token
        logger.info("Setting password for user", user_id=user_id)
        
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            logger.warning("User not found for password set", user_id=user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Hash the password using the system's password hashing function
        hashed_password = hash_password(data.password)
        logger.info("Password hashed successfully", hash_prefix=hashed_password[:20] if hashed_password else "EMPTY")
        
        # Update user with new password and mark as set
        result = await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "hashed_password": hashed_password,
                    "password_set": True
                }
            }
        )
        
        logger.info("Password update result", matched_count=result.matched_count, modified_count=result.modified_count)
        
        return MessageResponse(message="Password set successfully")
        
    except Exception as e:
        logger.error("Failed to set password", error=str(e), user_id=data.token)
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to set password"
        )
