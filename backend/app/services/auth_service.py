from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import logging

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

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user registration and login."""

    @staticmethod
    def register_user(user_data: UserCreate, db: Session) -> TokenResponse:
        """Register a new user."""
        logger.info(f"🔵 Registration attempt for email: {user_data.email}")

        try:
            # Check if user already exists
            logger.debug(f"Checking if user {user_data.email} already exists...")
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                logger.warning(f"❌ Registration failed: Email {user_data.email} already registered")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )

            # Validate password strength
            logger.debug(f"Validating password strength for {user_data.email}...")
            is_valid, error_message = validate_password(user_data.password)
            if not is_valid:
                logger.warning(f"❌ Password validation failed for {user_data.email}: {error_message}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=error_message
                )

            # Create new user
            logger.info(f"Creating new user: {user_data.email}")
            try:
                hashed_password = get_password_hash(user_data.password)
            except ValueError as e:
                logger.warning(f"❌ Password rejected for {user_data.email}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
            except Exception as e:
                logger.error(f"🔴 Unexpected hashing error for {user_data.email}: {type(e).__name__}: {str(e)}")
                logger.error("Full traceback:", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Unable to process password"
                )
            new_user = User(
                email=user_data.email,
                password_hash=hashed_password,
                full_name=user_data.full_name,
                tier="free",
                subscription_status="active",
                last_login=datetime.utcnow()
            )

            logger.debug(f"Adding user {user_data.email} to database...")
            db.add(new_user)

            logger.debug(f"Committing user {user_data.email} to database...")
            db.commit()

            logger.debug(f"Refreshing user {user_data.email} from database...")
            db.refresh(new_user)

            logger.info(f"✅ User {user_data.email} created successfully with ID: {new_user.id}")

            # Generate tokens
            logger.debug(f"Generating tokens for user {new_user.id}...")
            access_token = create_access_token({"sub": str(new_user.id)})
            refresh_token = create_refresh_token({"sub": str(new_user.id)})

            logger.info(f"✅ Registration complete for {user_data.email}")
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user=UserResponse.model_validate(new_user)
            )

        except HTTPException:
            # Re-raise HTTP exceptions (they're already logged above)
            raise
        except Exception as e:
            logger.error(f"🔴 Unexpected error during registration for {user_data.email}: {type(e).__name__}: {str(e)}")
            logger.error(f"Full traceback:", exc_info=True)
            raise

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
        is_valid, needs_rehash = verify_password(login_data.password, user.password_hash)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Update last login
        user.last_login = datetime.utcnow()
        if needs_rehash:
            user.password_hash = get_password_hash(login_data.password)
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
