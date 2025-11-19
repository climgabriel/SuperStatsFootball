from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
@router.get("/me", response_model=UserResponse)  # Alias for frontend compatibility
async def get_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get current user's profile.

    Requires authentication.
    Aliased to /me for frontend compatibility.
    """
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.

    Can update: full_name, timezone
    Cannot update: tier, subscription (requires admin or payment)
    """
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name

    # Note: timezone would be stored in user_settings table
    # For now, we'll skip it

    db.commit()
    db.refresh(current_user)

    return current_user


@router.get("/subscription")
async def get_subscription(current_user: User = Depends(get_current_active_user)):
    """
    Get current user's subscription information.
    """
    return {
        "tier": current_user.tier,
        "status": current_user.subscription_status,
        "subscription_id": current_user.subscription_id,
        "stripe_customer_id": current_user.stripe_customer_id
    }
