from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.user import UserCreate, UserLogin, TokenResponse, RefreshTokenRequest
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    - **email**: Valid email address
    - **password**: Password (min 8 characters, must include uppercase, lowercase, and digit)
    - **full_name**: Optional full name
    """
    return AuthService.register_user(user_data, db)


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password.

    Returns access token, refresh token, and user information.
    """
    return AuthService.login_user(login_data, db)


@router.post("/refresh")
async def refresh_token(token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.

    Returns new access token.
    """
    return AuthService.refresh_access_token(token_data.refresh_token, db)


@router.post("/logout")
async def logout():
    """
    Logout user.

    In a stateless JWT system, logout is handled client-side by removing tokens.
    This endpoint exists for consistency and future enhancements (e.g., token blacklisting).
    """
    return {"message": "Successfully logged out"}
