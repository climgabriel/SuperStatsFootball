"""
Script to create fixture_odds table in database.
Run this script to manually create the odds table if auto-migration doesn't work.

Usage:
    python scripts/create_odds_table.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import engine
from app.db.base import Base
from app.models.odds import FixtureOdds
from app.utils.logger import logger


def create_odds_table():
    """Create fixture_odds table in database."""
    try:
        logger.info("Creating fixture_odds table...")

        # Create only the FixtureOdds table
        FixtureOdds.__table__.create(bind=engine, checkfirst=True)

        logger.info("✅ fixture_odds table created successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Error creating fixture_odds table: {str(e)}")
        return False


if __name__ == "__main__":
    success = create_odds_table()
    sys.exit(0 if success else 1)
