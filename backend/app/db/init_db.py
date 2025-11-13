"""
Database initialization script.

Creates all tables and optionally seeds with initial data.
"""

from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models.user import User
from app.models.league import League
from app.models.team import Team
from app.models.fixture import Fixture, FixtureStat, FixtureScore
from app.models.prediction import Prediction, TeamRating, UserSettings
from app.core.security import get_password_hash
from app.utils.logger import logger


def init_db() -> None:
    """Initialize database with tables."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {str(e)}")
        raise


def seed_initial_data(db: Session) -> None:
    """
    Seed database with initial data.

    Creates:
    - Admin user
    - Sample leagues (free tier)
    """
    try:
        # Check if admin user already exists
        admin_email = "admin@superstatsfootball.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()

        if not existing_admin:
            # Create admin user
            admin_user = User(
                email=admin_email,
                password_hash=get_password_hash("admin123"),  # Change in production!
                full_name="Admin User",
                tier="ultimate",
                subscription_status="active"
            )
            db.add(admin_user)
            logger.info(f"✅ Created admin user: {admin_email}")
        else:
            logger.info(f"ℹ️  Admin user already exists: {admin_email}")

        # Create sample free-tier leagues
        sample_leagues = [
            {
                "id": 39,
                "name": "Premier League",
                "country": "England",
                "season": 2024,
                "tier_required": "free",
                "is_active": True,
                "priority": 100
            },
            {
                "id": 140,
                "name": "La Liga",
                "country": "Spain",
                "season": 2024,
                "tier_required": "free",
                "is_active": True,
                "priority": 95
            },
            {
                "id": 78,
                "name": "Bundesliga",
                "country": "Germany",
                "season": 2024,
                "tier_required": "free",
                "is_active": True,
                "priority": 90
            }
        ]

        for league_data in sample_leagues:
            existing_league = db.query(League).filter(
                League.id == league_data["id"],
                League.season == league_data["season"]
            ).first()

            if not existing_league:
                league = League(**league_data)
                db.add(league)
                logger.info(f"✅ Created league: {league_data['name']}")
            else:
                logger.info(f"ℹ️  League already exists: {league_data['name']}")

        db.commit()
        logger.info("✅ Database seeded successfully")

    except Exception as e:
        logger.error(f"❌ Error seeding database: {str(e)}")
        db.rollback()
        raise


def reset_db() -> None:
    """Drop all tables and recreate (USE WITH CAUTION!)."""
    try:
        logger.warning("⚠️  Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Tables dropped")

        logger.info("🔄 Recreating tables...")
        init_db()

        logger.info("🌱 Seeding initial data...")
        db = SessionLocal()
        seed_initial_data(db)
        db.close()

        logger.info("✅ Database reset complete")

    except Exception as e:
        logger.error(f"❌ Error resetting database: {str(e)}")
        raise


if __name__ == "__main__":
    print("Database Initialization Script")
    print("=" * 50)
    print("1. Initialize database (create tables)")
    print("2. Seed initial data")
    print("3. Reset database (DROP ALL TABLES!)")
    print("=" * 50)

    choice = input("Enter your choice (1-3): ")

    if choice == "1":
        init_db()
    elif choice == "2":
        db = SessionLocal()
        seed_initial_data(db)
        db.close()
    elif choice == "3":
        confirm = input("⚠️  This will DELETE ALL DATA. Type 'RESET' to confirm: ")
        if confirm == "RESET":
            reset_db()
        else:
            print("Reset cancelled")
    else:
        print("Invalid choice")
