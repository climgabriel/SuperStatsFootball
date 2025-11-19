"""
Quick data population script using the new apifootball.com API.

This script populates essential data to get the website working:
- A few top leagues
- Teams from those leagues
- Upcoming fixtures
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.services.apifootball import api_football_client
from app.models.league import League
from app.models.team import Team
from app.models.fixture import Fixture
from app.core.leagues_config import LEAGUE_METADATA, get_tier_for_league
from app.utils.logger import logger

# Top leagues to populate (API Football IDs from apifootball.com)
PRIORITY_LEAGUES = [
    152,  # Premier League
    302,  # La Liga
    175,  # Bundesliga
    207,  # Serie A
    168,  # Ligue 1
]


async def populate_data():
    """Populate database with essential data."""
    db = SessionLocal()

    try:
        logger.info("=" * 80)
        logger.info("QUICK DATA POPULATION")
        logger.info("=" * 80)

        # Get current season
        current_year = datetime.now().year
        current_month = datetime.now().month
        # Football season spans two years (e.g., 2024-2025 season is "2024")
        season = current_year if current_month >= 8 else current_year - 1

        logger.info(f"Using season: {season}")

        # STEP 1: Populate leagues
        logger.info("\n--- STEP 1: Populating Leagues ---")
        leagues_data = await api_football_client.get_leagues()
        logger.info(f"Retrieved {len(leagues_data)} leagues from API")

        for league_id in PRIORITY_LEAGUES:
            # Find league in API data
            league_info = next(
                (l for l in leagues_data if int(l.get("league_id", 0)) == league_id),
                None
            )

            if not league_info:
                logger.warning(f"League {league_id} not found in API data, using metadata")
                metadata = LEAGUE_METADATA.get(league_id, {})
                league = League(
                    id=league_id,
                    name=metadata.get("name", f"League {league_id}"),
                    country=metadata.get("country", "Unknown"),
                    season=season,
                    tier_required=get_tier_for_league(league_id),
                    is_active=True,
                    priority=metadata.get("priority", 0)
                )
            else:
                league = League(
                    id=league_id,
                    name=league_info.get("league_name", f"League {league_id}"),
                    country=league_info.get("country_name", "Unknown"),
                    logo=league_info.get("league_logo"),
                    season=season,
                    tier_required=get_tier_for_league(league_id),
                    is_active=True,
                    priority=LEAGUE_METADATA.get(league_id, {}).get("priority", 0)
                )

            db.add(league)
            logger.info(f"  Added league: {league.name} ({league.country})")

        db.commit()
        logger.info(f"✓ {len(PRIORITY_LEAGUES)} leagues added")

        # STEP 2: Populate teams
        logger.info("\n--- STEP 2: Populating Teams ---")
        total_teams = 0

        for league_id in PRIORITY_LEAGUES:
            await asyncio.sleep(0.5)  # Rate limiting

            teams_data = await api_football_client.get_teams(league_id)
            logger.info(f"  Retrieved {len(teams_data)} teams for league {league_id}")

            for team_info in teams_data:
                team_id = int(team_info.get("team_key", 0))
                if not team_id:
                    continue

                # Check if team exists
                existing = db.query(Team).filter(Team.id == team_id).first()
                if existing:
                    continue

                team = Team(
                    id=team_id,
                    name=team_info.get("team_name", f"Team {team_id}"),
                    code=team_info.get("team_badge", "")[:10] if team_info.get("team_badge") else None,
                    country=team_info.get("team_country"),
                    logo=team_info.get("team_badge"),
                    venue_name=team_info.get("venue", {}).get("venue_name") if isinstance(team_info.get("venue"), dict) else None
                )
                db.add(team)
                total_teams += 1

            db.commit()

        logger.info(f"✓ {total_teams} teams added")

        # STEP 3: Populate upcoming fixtures
        logger.info("\n--- STEP 3: Populating Upcoming Fixtures ---")
        now = datetime.now()
        date_from = now.strftime("%Y-%m-%d")
        date_to = (now + timedelta(days=14)).strftime("%Y-%m-%d")

        total_fixtures = 0

        for league_id in PRIORITY_LEAGUES:
            await asyncio.sleep(0.5)  # Rate limiting

            fixtures_data = await api_football_client.get_fixtures(
                league_id=league_id,
                date_from=date_from,
                date_to=date_to
            )

            logger.info(f"  Retrieved {len(fixtures_data)} fixtures for league {league_id}")

            for fixture_info in fixtures_data:
                try:
                    match_id = int(fixture_info.get("match_id", 0))
                    if not match_id:
                        continue

                    # Check if fixture exists
                    existing = db.query(Fixture).filter(Fixture.id == match_id).first()
                    if existing:
                        continue

                    # Parse match date
                    match_date_str = fixture_info.get("match_date")
                    match_time_str = fixture_info.get("match_time", "00:00")

                    if match_date_str:
                        try:
                            match_datetime = datetime.strptime(
                                f"{match_date_str} {match_time_str}",
                                "%Y-%m-%d %H:%M"
                            )
                        except:
                            match_datetime = datetime.strptime(match_date_str, "%Y-%m-%d")
                    else:
                        continue

                    # Get team IDs
                    home_team_id = int(fixture_info.get("match_hometeam_id", 0))
                    away_team_id = int(fixture_info.get("match_awayteam_id", 0))

                    if not home_team_id or not away_team_id:
                        continue

                    # Map status
                    status_map = {
                        "": "NS",
                        "Not Started": "NS",
                        "Finished": "FT",
                        "Postponed": "PST",
                        "Cancelled": "CANC"
                    }
                    status = status_map.get(fixture_info.get("match_status", ""), "NS")

                    fixture = Fixture(
                        id=match_id,
                        league_id=league_id,
                        season=season,
                        round=fixture_info.get("match_round"),
                        match_date=match_datetime,
                        timestamp=int(match_datetime.timestamp()),
                        home_team_id=home_team_id,
                        away_team_id=away_team_id,
                        status=status,
                        venue=fixture_info.get("match_stadium"),
                        referee=fixture_info.get("match_referee")
                    )

                    db.add(fixture)
                    total_fixtures += 1

                except Exception as e:
                    logger.error(f"Error processing fixture {fixture_info.get('match_id')}: {e}")
                    continue

            db.commit()

        logger.info(f"✓ {total_fixtures} fixtures added")

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("POPULATION COMPLETE!")
        logger.info("=" * 80)
        logger.info(f"Leagues: {len(PRIORITY_LEAGUES)}")
        logger.info(f"Teams: {total_teams}")
        logger.info(f"Fixtures: {total_fixtures}")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error during population: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
        await api_football_client.close()


if __name__ == "__main__":
    asyncio.run(populate_data())
