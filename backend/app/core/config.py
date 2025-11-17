from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import secrets


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    # Application
    APP_NAME: str = "SuperStatsFootball"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = ""
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.greengeeksclient.com",  # GreenGeeks hosting
        "https://superstatsfootball.com",   # Production domain (if applicable)
        "https://www.superstatsfootball.com",  # Production domain with www
        "*"  # Allow all origins in development (remove in production)
    ]

    # API-Football
    APIFOOTBALL_API_KEY: str = ""
    APIFOOTBALL_BASE_URL: str = "https://v3.football.api-sports.io"
    APIFOOTBALL_RATE_LIMIT: int = 100  # requests per day for free tier

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_STARTER: str = ""
    STRIPE_PRICE_ID_PRO: str = ""
    STRIPE_PRICE_ID_PREMIUM: str = ""
    STRIPE_PRICE_ID_ULTIMATE: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 300  # 5 minutes

    # Sentry
    SENTRY_DSN: str = ""

    # Tiers
    TIER_HIERARCHY: dict = {
        "free": 0,
        "starter": 1,
        "pro": 2,
        "premium": 3,
        "ultimate": 4
    }

    TIER_MODELS: dict = {
        "free": ["poisson"],
        "starter": ["poisson", "dixon_coles"],
        "pro": ["poisson", "dixon_coles", "elo"],
        "premium": ["poisson", "dixon_coles", "elo", "logistic"],
        "ultimate": ["poisson", "dixon_coles", "elo", "logistic", "random_forest", "xgboost"]
    }

    TIER_LEAGUE_LIMITS: dict = {
        "free": 3,
        "starter": 10,
        "pro": 25,
        "premium": 50,
        "ultimate": 999
    }

    # League Search Limits (per query to prevent app crashes)
    MAX_LEAGUES_PER_SEARCH_REGULAR: int = 5  # Regular users (free-premium)
    MAX_LEAGUES_PER_SEARCH_ADMIN: int = 10    # Admin users (ultimate)

    # ML Models
    ML_MODEL_PATH: str = "app/ml/models"


settings = Settings()
