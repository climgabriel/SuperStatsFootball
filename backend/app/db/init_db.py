"""
Database initialization script.

Creates all tables and optionally seeds with initial data.
"""

from datetime import datetime, timedelta
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
                password_hash=get_password_hash("Admin123!"),  # Change in production!
                full_name="Admin User",
                tier="ultimate",
                subscription_status="active"
            )
            db.add(admin_user)
            logger.info(f"✅ Created admin user: {admin_email}")
        else:
            logger.info(f"ℹ️  Admin user already exists: {admin_email}")

        # Create demo user for frontend auto-login
        demo_email = "demo@superstatsfootball.com"
        existing_demo = db.query(User).filter(User.email == demo_email).first()

        if not existing_demo:
            demo_user = User(
                email=demo_email,
                password_hash=get_password_hash("demo123"),
                full_name="Demo User",
                tier="starter",
                subscription_status="active"
            )
            db.add(demo_user)
            logger.info(f"✅ Created demo user: {demo_email}")
        else:
            logger.info(f"ℹ️  Demo user already exists: {demo_email}")

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

        # Create teams referenced by demo fixtures
        sample_teams = [
            {"id": 33, "name": "Manchester United", "code": "MUN", "country": "England"},
            {"id": 50, "name": "Manchester City", "code": "MCI", "country": "England"},
            {"id": 42, "name": "Arsenal", "code": "ARS", "country": "England"},
            {"id": 40, "name": "Liverpool", "code": "LIV", "country": "England"},
            {"id": 541, "name": "Real Madrid", "code": "RMA", "country": "Spain"},
            {"id": 529, "name": "Barcelona", "code": "BAR", "country": "Spain"},
            {"id": 157, "name": "Bayern Munich", "code": "FCB", "country": "Germany"},
            {"id": 165, "name": "Borussia Dortmund", "code": "BVB", "country": "Germany"}
        ]

        for team_data in sample_teams:
            existing_team = db.query(Team).filter(Team.id == team_data["id"]).first()
            if not existing_team:
                team = Team(
                    id=team_data["id"],
                    name=team_data["name"],
                    code=team_data["code"],
                    country=team_data["country"],
                    founded=1880
                )
                db.add(team)
                logger.info(f"✅ Created team: {team_data['name']}")
            else:
                logger.info(f"ℹ️  Team already exists: {team_data['name']}")

        # Create sample fixtures with statistics so the frontend has data immediately
        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        sample_fixtures = [
            {
                "id": 202401,
                "league_id": 39,
                "season": 2024,
                "round": "Regular Season - 12",
                "days_ahead": 1,
                "home_team_id": 33,
                "away_team_id": 50,
                "venue": "Old Trafford",
                "referee": "Michael Oliver",
                "stats": [
                    {
                        "team_id": 33,
                        "shots_on_goal": 6,
                        "shots_off_goal": 5,
                        "total_shots": 15,
                        "blocked_shots": 4,
                        "shots_inside_box": 9,
                        "shots_outside_box": 6,
                        "fouls": 12,
                        "corners": 6,
                        "offsides": 2,
                        "ball_possession": 52,
                        "yellow_cards": 2,
                        "red_cards": 0,
                        "goalkeeper_saves": 4,
                        "total_passes": 520,
                        "passes_accurate": 456,
                        "passes_percentage": 88,
                        "expected_goals": 1.6
                    },
                    {
                        "team_id": 50,
                        "shots_on_goal": 7,
                        "shots_off_goal": 6,
                        "total_shots": 17,
                        "blocked_shots": 4,
                        "shots_inside_box": 10,
                        "shots_outside_box": 7,
                        "fouls": 10,
                        "corners": 7,
                        "offsides": 3,
                        "ball_possession": 48,
                        "yellow_cards": 1,
                        "red_cards": 0,
                        "goalkeeper_saves": 3,
                        "total_passes": 545,
                        "passes_accurate": 472,
                        "passes_percentage": 87,
                        "expected_goals": 1.9
                    }
                ]
            },
            {
                "id": 202402,
                "league_id": 39,
                "season": 2024,
                "round": "Regular Season - 12",
                "days_ahead": 2,
                "home_team_id": 42,
                "away_team_id": 40,
                "venue": "Emirates Stadium",
                "referee": "Anthony Taylor",
                "stats": [
                    {
                        "team_id": 42,
                        "shots_on_goal": 5,
                        "shots_off_goal": 4,
                        "total_shots": 14,
                        "blocked_shots": 3,
                        "shots_inside_box": 7,
                        "shots_outside_box": 7,
                        "fouls": 9,
                        "corners": 5,
                        "offsides": 1,
                        "ball_possession": 55,
                        "yellow_cards": 1,
                        "red_cards": 0,
                        "goalkeeper_saves": 2,
                        "total_passes": 600,
                        "passes_accurate": 534,
                        "passes_percentage": 89,
                        "expected_goals": 1.7
                    },
                    {
                        "team_id": 40,
                        "shots_on_goal": 6,
                        "shots_off_goal": 5,
                        "total_shots": 16,
                        "blocked_shots": 4,
                        "shots_inside_box": 9,
                        "shots_outside_box": 7,
                        "fouls": 11,
                        "corners": 6,
                        "offsides": 2,
                        "ball_possession": 45,
                        "yellow_cards": 2,
                        "red_cards": 0,
                        "goalkeeper_saves": 3,
                        "total_passes": 520,
                        "passes_accurate": 455,
                        "passes_percentage": 87,
                        "expected_goals": 1.8
                    }
                ]
            },
            {
                "id": 202403,
                "league_id": 140,
                "season": 2024,
                "round": "Regular Season - 13",
                "days_ahead": 3,
                "home_team_id": 541,
                "away_team_id": 529,
                "venue": "Santiago Bernabéu",
                "referee": "Juan Martinez",
                "stats": [
                    {
                        "team_id": 541,
                        "shots_on_goal": 8,
                        "shots_off_goal": 6,
                        "total_shots": 18,
                        "blocked_shots": 4,
                        "shots_inside_box": 11,
                        "shots_outside_box": 7,
                        "fouls": 8,
                        "corners": 7,
                        "offsides": 2,
                        "ball_possession": 57,
                        "yellow_cards": 1,
                        "red_cards": 0,
                        "goalkeeper_saves": 2,
                        "total_passes": 640,
                        "passes_accurate": 580,
                        "passes_percentage": 91,
                        "expected_goals": 2.2
                    },
                    {
                        "team_id": 529,
                        "shots_on_goal": 5,
                        "shots_off_goal": 6,
                        "total_shots": 15,
                        "blocked_shots": 3,
                        "shots_inside_box": 8,
                        "shots_outside_box": 7,
                        "fouls": 11,
                        "corners": 5,
                        "offsides": 1,
                        "ball_possession": 43,
                        "yellow_cards": 3,
                        "red_cards": 0,
                        "goalkeeper_saves": 4,
                        "total_passes": 520,
                        "passes_accurate": 450,
                        "passes_percentage": 86,
                        "expected_goals": 1.4
                    }
                ]
            },
            {
                "id": 202404,
                "league_id": 78,
                "season": 2024,
                "round": "Regular Season - 11",
                "days_ahead": 4,
                "home_team_id": 157,
                "away_team_id": 165,
                "venue": "Allianz Arena",
                "referee": "Felix Zwayer",
                "stats": [
                    {
                        "team_id": 157,
                        "shots_on_goal": 7,
                        "shots_off_goal": 5,
                        "total_shots": 17,
                        "blocked_shots": 5,
                        "shots_inside_box": 10,
                        "shots_outside_box": 7,
                        "fouls": 13,
                        "corners": 8,
                        "offsides": 2,
                        "ball_possession": 58,
                        "yellow_cards": 2,
                        "red_cards": 0,
                        "goalkeeper_saves": 3,
                        "total_passes": 610,
                        "passes_accurate": 548,
                        "passes_percentage": 90,
                        "expected_goals": 2.1
                    },
                    {
                        "team_id": 165,
                        "shots_on_goal": 4,
                        "shots_off_goal": 4,
                        "total_shots": 13,
                        "blocked_shots": 2,
                        "shots_inside_box": 6,
                        "shots_outside_box": 7,
                        "fouls": 12,
                        "corners": 4,
                        "offsides": 2,
                        "ball_possession": 42,
                        "yellow_cards": 2,
                        "red_cards": 0,
                        "goalkeeper_saves": 6,
                        "total_passes": 470,
                        "passes_accurate": 400,
                        "passes_percentage": 85,
                        "expected_goals": 1.3
                    }
                ]
            }
        ]

        for fixture_data in sample_fixtures:
            existing_fixture = db.query(Fixture).filter(Fixture.id == fixture_data["id"]).first()
            match_date = now + timedelta(days=fixture_data["days_ahead"])

            if not existing_fixture:
                fixture = Fixture(
                    id=fixture_data["id"],
                    league_id=fixture_data["league_id"],
                    season=fixture_data["season"],
                    round=fixture_data["round"],
                    match_date=match_date,
                    timestamp=int(match_date.timestamp()),
                    home_team_id=fixture_data["home_team_id"],
                    away_team_id=fixture_data["away_team_id"],
                    status="NS",
                    venue=fixture_data.get("venue"),
                    referee=fixture_data.get("referee")
                )
                db.add(fixture)
                logger.info(f"✅ Created fixture: {fixture_data['id']}")
            else:
                logger.info(f"ℹ️  Fixture already exists: {fixture_data['id']}")

            for stat_data in fixture_data["stats"]:
                existing_stat = db.query(FixtureStat).filter(
                    FixtureStat.fixture_id == fixture_data["id"],
                    FixtureStat.team_id == stat_data["team_id"]
                ).first()

                if existing_stat:
                    continue

                stat = FixtureStat(
                    fixture_id=fixture_data["id"],
                    team_id=stat_data["team_id"],
                    shots_on_goal=stat_data.get("shots_on_goal"),
                    shots_off_goal=stat_data.get("shots_off_goal"),
                    total_shots=stat_data.get("total_shots"),
                    blocked_shots=stat_data.get("blocked_shots"),
                    shots_inside_box=stat_data.get("shots_inside_box"),
                    shots_outside_box=stat_data.get("shots_outside_box"),
                    fouls=stat_data.get("fouls"),
                    corners=stat_data.get("corners"),
                    offsides=stat_data.get("offsides"),
                    ball_possession=stat_data.get("ball_possession"),
                    yellow_cards=stat_data.get("yellow_cards"),
                    red_cards=stat_data.get("red_cards"),
                    goalkeeper_saves=stat_data.get("goalkeeper_saves"),
                    total_passes=stat_data.get("total_passes"),
                    passes_accurate=stat_data.get("passes_accurate"),
                    passes_percentage=stat_data.get("passes_percentage"),
                    expected_goals=stat_data.get("expected_goals")
                )
                db.add(stat)

        logger.info("✅ Sample fixtures and statistics created")

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
