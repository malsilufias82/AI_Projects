from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from bson import ObjectId
from pydantic import BaseModel

from app.auth.handlers import generate_token_pair, refresh_access_token
from app.auth.dependencies import get_current_user
from app.core.config import settings
from app.core.logging import get_logger
from app.core.mongodb import MongoDB
from app.core.security import hash_password
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse, ForgotPasswordRequest
from app.schemas.base import MessageResponse
from app.services.email_service import send_password_reset_email
from app.services.mongo_user_service import MongoUserService

try:
    from app.core.rate_limit import limiter
except ImportError:
    limiter = None

logger = get_logger(__name__)

router = APIRouter()


class SetPasswordRequest(BaseModel):
    """Request model for setting password."""
    token: str
    password: str


def _rate_limit_decorator(limit: str):
    """Apply rate limit if slowapi is installed, otherwise no-op."""
    if limiter is not None:
        return limiter.limit(limit)
    return lambda f: f


@router.post("/login", response_model=TokenResponse)
@_rate_limit_decorator("5/minute")
async def login(
    request: Request,
    data: LoginRequest,
) -> TokenResponse:
    user_service = MongoUserService()
    user = await user_service.authenticate(data.email, data.password)
    return generate_token_pair(str(user["_id"]))


@router.post("/refresh", response_model=TokenResponse)
@_rate_limit_decorator("30/minute")
async def refresh_token(
    request: Request,
    data: RefreshTokenRequest,
) -> TokenResponse:
    return refresh_access_token(data.refresh_token)


@router.post("/logout", response_model=MessageResponse)
@_rate_limit_decorator("10/minute")
async def logout(
    request: Request,
) -> MessageResponse:
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
    """Set password for a user using a token from forgot-password."""
    users_collection = MongoDB.get_collection("users")

    try:
        # The token is the user's _id (stored as a string UUID by MongoBaseRepository)
        user = await users_collection.find_one({"_id": data.token})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired token"
            )

        # Hash and update password
        from datetime import datetime
        hashed = hash_password(data.password)
        result = await users_collection.update_one(
            {"_id": data.token},
            {"$set": {"hashed_password": hashed, "password_set": True, "updated_at": datetime.utcnow()}}
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


@router.post("/forgot-password", response_model=MessageResponse)
@_rate_limit_decorator("3/hour")
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
) -> MessageResponse:
    """
    Send a password reset link to the user's email.

    Returns the same generic success message regardless of whether the email
    is registered, to prevent user enumeration. Rate limiting (3/hour per IP)
    provides additional protection against enumeration attacks.
    """
    user_service = MongoUserService()
    user = await user_service.get_by_email(data.email)

    if user:
        user_id = str(user["_id"])
        recipient_name = (
            f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            or user.get("email", "").split("@")[0]
        )
        reset_url = f"{settings.FRONTEND_URL}/set-password?token={user_id}"
        send_password_reset_email(
            to=data.email,
            recipient_name=recipient_name,
            reset_url=reset_url,
        )
        logger.info("Password reset email queued", email=data.email)
    else:
        logger.warning("Password reset requested for unregistered email", email=data.email)

    return MessageResponse(
        message="If an account with that email exists, a password reset link has been sent."
    )