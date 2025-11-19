"""
Test API-Football connection and basic data fetching.
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.apifootball import api_football_client
from app.core.config import settings
from app.utils.logger import logger


async def test_api():
    """Test API-Football connection."""

    print("=" * 80)
    print("Testing API-Football Connection")
    print("=" * 80)
    print(f"API Key: {settings.APIFOOTBALL_API_KEY[:20]}...")
    print(f"Base URL: {settings.APIFOOTBALL_BASE_URL}")
    print("=" * 80)

    try:
        # Test 1: Get current season leagues
        print("\nTest 1: Fetching leagues for 2024 season...")
        leagues = await api_football_client.get_leagues(season=2024)
        print(f"SUCCESS: Retrieved {len(leagues)} leagues")

        if leagues:
            print(f"\nFirst league: {leagues[0]['league']['name']} ({leagues[0]['country']['name']})")

        # Test 2: Get a specific league (Premier League - ID 39 or 152)
        print("\nTest 2: Fetching Premier League teams...")
        teams = await api_football_client.get_teams(league_id=39, season=2024)
        print(f"SUCCESS: Retrieved {len(teams)} teams")

        if teams:
            print(f"First team: {teams[0]['team']['name']}")

        # Test 3: Get recent fixtures
        print("\nTest 3: Fetching recent fixtures for Premier League...")
        fixtures = await api_football_client.get_fixtures(league_id=39, season=2024, last=10)
        print(f"SUCCESS: Retrieved {len(fixtures)} fixtures")

        if fixtures:
            first = fixtures[0]
            print(f"First fixture: {first['teams']['home']['name']} vs {first['teams']['away']['name']}")

        print("\n" + "=" * 80)
        print("All API tests passed!")
        print("=" * 80)

    except Exception as e:
        print("\n" + "=" * 80)
        print(f"ERROR: {str(e)}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
    finally:
        await api_football_client.close()


if __name__ == "__main__":
    asyncio.run(test_api())
