from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.security import verify_token
from app.models.user import User

security = HTTPBearer()


def get_db() -> Generator:
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token, token_type="access")

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if current_user.subscription_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return current_user


def require_tier(required_tier: str):
    """Dependency to require a specific subscription tier."""
    async def tier_checker(current_user: User = Depends(get_current_active_user)) -> User:
        from app.core.security import check_tier_access

        if not check_tier_access(current_user.tier, required_tier):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {required_tier} tier or higher"
            )
        return current_user

    return tier_checker


def require_admin():
    """Dependency to require admin access."""
    async def admin_checker(current_user: User = Depends(get_current_active_user)) -> User:
        # In a real app, you'd have an is_admin field
        # For now, we'll use ultimate tier as admin
        if current_user.tier != "ultimate":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user

    return admin_checker
