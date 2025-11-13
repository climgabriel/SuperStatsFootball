from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)
from app.utils.validators import validate_password


class AuthService:
    """Authentication service for user registration and login."""

    @staticmethod
    def register_user(user_data: UserCreate, db: Session) -> TokenResponse:
        """Register a new user."""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Validate password strength
        is_valid, error_message = validate_password(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            full_name=user_data.full_name,
            tier="free",
            subscription_status="active",
            last_login=datetime.utcnow()
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Generate tokens
        access_token = create_access_token({"sub": str(new_user.id)})
        refresh_token = create_refresh_token({"sub": str(new_user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(new_user)
        )

    @staticmethod
    def login_user(login_data: UserLogin, db: Session) -> TokenResponse:
        """Login a user."""
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    def refresh_access_token(refresh_token: str, db: Session) -> dict:
        """Refresh access token using refresh token."""
        # Verify refresh token
        payload = verify_token(refresh_token, token_type="refresh")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Generate new access token
        access_token = create_access_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
