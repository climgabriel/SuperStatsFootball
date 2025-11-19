"""
Initialize database tables in production.

This script creates all database tables defined in SQLAlchemy models.
Run this script once to set up the database schema.
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import engine
from app.db.base import Base
from app.utils.logger import logger

# Import all models to ensure they are registered with Base.metadata
from app.models import user, league, team, fixture, prediction, odds


def init_database():
    """Create all database tables."""
    try:
        logger.info("=" * 80)
        logger.info("🏗️  Initializing database tables...")
        logger.info("=" * 80)

        # Create all tables
        Base.metadata.create_all(bind=engine)

        logger.info("✅ All database tables created successfully!")
        logger.info("=" * 80)
        logger.info("Created tables:")
        for table in Base.metadata.sorted_tables:
            logger.info(f"  - {table.name}")
        logger.info("=" * 80)

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ Error creating database tables: {str(e)}")
        logger.error("=" * 80)
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    init_database()
