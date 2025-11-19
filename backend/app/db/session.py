from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.utils.logger import logger


def _create_engine():
    """
    Create a SQLAlchemy engine that MUST connect to the configured DATABASE_URL.
    Local SQLite fallbacks are intentionally removed to keep the backend aligned
    with Supabase/Postgres infrastructure.
    """
    configured_url = (settings.DATABASE_URL or "").strip()
    if not configured_url:
        raise RuntimeError(
            "DATABASE_URL is not configured. Supabase/Postgres connectivity "
            "is mandatory for this deployment."
        )

    try:
        engine = create_engine(
            configured_url,
            pool_pre_ping=True,
        )
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logger.info("Connected to database at %s", configured_url)
        return engine, configured_url
    except OperationalError as err:
        logger.error(f"Database connection failed for {configured_url}: {err}")
        raise


engine, database_url = _create_engine()

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
