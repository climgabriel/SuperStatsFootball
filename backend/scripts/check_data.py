"""
Quick script to check what data exists in the database.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.models.league import League
from app.models.team import Team
from app.models.fixture import Fixture
from app.models.odds import FixtureOdds

db = SessionLocal()

print("=" * 80)
print("DATABASE CONTENTS CHECK")
print("=" * 80)

# Count leagues
league_count = db.query(League).count()
print(f"Leagues: {league_count}")

# Count teams
team_count = db.query(Team).count()
print(f"Teams: {team_count}")

# Count fixtures
fixture_count = db.query(Fixture).count()
print(f"Fixtures (total): {fixture_count}")

# Count upcoming fixtures
from datetime import datetime, timedelta
now = datetime.utcnow()
end_date = now + timedelta(days=7)
upcoming = db.query(Fixture).filter(
    Fixture.match_date >= now,
    Fixture.match_date <= end_date,
    Fixture.status.in_(["NS", "TBD"])
).count()
print(f"Upcoming fixtures (next 7 days): {upcoming}")

# Count odds
odds_count = db.query(FixtureOdds).count()
print(f"Odds records: {odds_count}")

print("=" * 80)

# Show sample upcoming fixtures if any
if upcoming > 0:
    print("\nSample upcoming fixtures:")
    fixtures = db.query(Fixture).filter(
        Fixture.match_date >= now,
        Fixture.match_date <= end_date,
        Fixture.status.in_(["NS", "TBD"])
    ).limit(5).all()

    for f in fixtures:
        print(f"  - {f.id}: League {f.league_id}, {f.match_date}")

db.close()
