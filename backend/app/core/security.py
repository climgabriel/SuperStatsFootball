from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from jose import JWTError, jwt
import hashlib
import hmac
import types
import bcrypt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from .config import settings

# The Rust bcrypt package (v4+) no longer exposes __about__.__version__,
# which passlib tries to read. Patch it in to avoid noisy warnings.
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = types.SimpleNamespace(__version__=bcrypt.__version__)

# Prefer bcrypt_sha256 to safely support passwords longer than 72 bytes, while
# keeping plain bcrypt hashes verifiable for existing users.
pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],
    deprecated="auto"
)


def _legacy_hash(password: str) -> str:
    """Generate the historical SHA-256 hash that was previously used."""
    return hashlib.sha256((password + settings.SECRET_KEY).encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> Tuple[bool, bool]:
    """
    Verify a password against a hash.

    Returns:
        (is_valid, needs_rehash)
    """
    try:
        if pwd_context.verify(plain_password, hashed_password):
            return True, pwd_context.needs_update(hashed_password)
    except (ValueError, TypeError):
        # Not a bcrypt hash, fall back to legacy check
        pass

    legacy_hash = _legacy_hash(plain_password)
    if hmac.compare_digest(legacy_hash, hashed_password or ""):
        # Legacy hashes must be upgraded to bcrypt immediately
        return True, True

    return False, False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {token_type}"
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


def check_tier_access(user_tier: str, required_tier: str) -> bool:
    """Check if user's tier meets the required tier."""
    user_level = settings.TIER_HIERARCHY.get(user_tier, 0)
    required_level = settings.TIER_HIERARCHY.get(required_tier, 0)
    return user_level >= required_level


def check_model_access(user_tier: str, model_type: str) -> bool:
    """Check if user's tier has access to the specified model."""
    allowed_models = settings.TIER_MODELS.get(user_tier, [])
    return model_type in allowed_models
