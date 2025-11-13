from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create SQLAlchemy engine
# For now, we'll use a default in-memory database if DATABASE_URL is not set
database_url = settings.DATABASE_URL if settings.DATABASE_URL else "sqlite:///./superstats.db"

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
)

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
