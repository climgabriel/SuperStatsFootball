import re
from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    return True, None


def validate_tier(tier: str) -> bool:
    """Validate subscription tier."""
    valid_tiers = ["free", "starter", "pro", "premium", "ultimate"]
    return tier.lower() in valid_tiers


def validate_model_type(model_type: str) -> bool:
    """Validate prediction model type."""
    valid_models = ["poisson", "dixon_coles", "bivariate_poisson", "elo", "glicko"]
    return model_type.lower() in valid_models


def validate_date_format(date_str: str) -> bool:
    """Validate date format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_season(season: int) -> bool:
    """Validate season year."""
    current_year = datetime.now().year
    return 2000 <= season <= current_year + 1


def validate_league_count(league_ids: List[int], user_tier: str, max_regular: int = 5, max_admin: int = 10) -> None:
    """
    Validate the number of leagues requested in a single query.
    Raises HTTPException if limit is exceeded.

    Args:
        league_ids: List of league IDs being requested
        user_tier: User's subscription tier
        max_regular: Maximum leagues for regular users (default: 5)
        max_admin: Maximum leagues for admin users (default: 10)

    Raises:
        HTTPException: If league count exceeds allowed limit
    """
    league_count = len(league_ids)
    is_admin = user_tier == "ultimate"
    max_allowed = max_admin if is_admin else max_regular

    if league_count > max_allowed:
        user_type = "admin" if is_admin else "regular"
        raise HTTPException(
            status_code=400,
            detail=f"Too many leagues requested. {user_type.capitalize()} users can search up to {max_allowed} leagues at a time. You requested {league_count}."
        )
