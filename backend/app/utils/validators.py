import re
from typing import Optional
from datetime import datetime


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
    valid_models = ["poisson", "dixon_coles", "elo", "logistic", "random_forest", "xgboost"]
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
