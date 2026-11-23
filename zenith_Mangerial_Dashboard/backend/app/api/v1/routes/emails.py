from typing import List
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth.dependencies import get_current_user, require_permission
from app.core.config import settings
from app.core.mongodb import MongoDB
from app.schemas.base import MessageResponse
from app.services.email_service import send_bulk_account_setup_emails

router = APIRouter()


class BulkAccountSetupRequest(BaseModel):
    """Request model for bulk account setup emails."""
    user_ids: List[str]
    setup_url_base: str
    company_name: str = None


@router.post("/account-setup", response_model=MessageResponse, status_code=status.HTTP_202_ACCEPTED)
async def send_bulk_account_setup(
    data: BulkAccountSetupRequest,
    _: dict = Depends(require_permission("members", "modify")),
) -> MessageResponse:
    """
    Send account setup emails to multiple users.
    
    Accepts a list of user IDs, fetches their details from MongoDB,
    and sends account setup emails with password setup links.
    """
    users_collection = MongoDB.get_collection("users")
    
    # Fetch user details for all provided user IDs
    recipients = []
    
    for user_id in data.user_ids:
        try:
            user = await users_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                continue
            
            # Only send to users who haven't set their password yet
            if user.get("password_set", False):
                continue
            
            recipients.append({
                'email': user.get("email"),
                'name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user.get("email", "").split("@")[0],
                'token': user_id  # Use user_id as token for setup URL
            })
        except Exception as e:
            # Skip invalid user IDs
            continue
    
    if not recipients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid users found or all users have already set their passwords"
        )
    
    # Send bulk account setup emails
    result = send_bulk_account_setup_emails(
        recipients=recipients,
        setup_url_base=data.setup_url_base,
        company_name=data.company_name or settings.EMAIL_FROM_NAME
    )
    
    return MessageResponse(
        message=f"Account setup emails queued for {len(recipients)} users"
    )
