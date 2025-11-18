from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.utils.logger import logger

DEFAULT_SQLITE_URL = "sqlite:///./superstats.db"


def _create_engine_with_fallback():
    """
    Create SQLAlchemy engine and fall back to SQLite when the configured database
    is unreachable (e.g., Supabase from a sandboxed environment).
    """
    configured_url = (settings.DATABASE_URL or "").strip()
    urls_to_try = []
    if configured_url:
        urls_to_try.append(configured_url)
    urls_to_try.append(DEFAULT_SQLITE_URL)

    last_error = None
    for url in urls_to_try:
        try:
            engine = create_engine(
                url,
                pool_pre_ping=True,
                connect_args={"check_same_thread": False} if "sqlite" in url else {}
            )
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            if configured_url and url != configured_url:
                logger.warning(
                    "Primary DATABASE_URL is unreachable. Falling back to SQLite at %s",
                    url
                )
            else:
                logger.info("Connected to database at %s", url)

            return engine, url
        except OperationalError as err:
            last_error = err
            logger.error(f"Database connection failed for {url}: {err}")

    raise last_error or RuntimeError("Unable to establish a database connection")


engine, database_url = _create_engine_with_fallback()

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
