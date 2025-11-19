"""
Test the new apifootball.com API client.
"""
import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.apifootball import api_football_client
from app.utils.logger import logger


async def test_new_api():
    """Test all major endpoints of the new API."""

    print("=" * 80)
    print("Testing APIFootball.com Client")
    print("=" * 80)

    try:
        # Test 1: Get countries
        print("\nTest 1: Getting countries...")
        countries = await api_football_client.get_countries()
        print(f"SUCCESS: Retrieved {len(countries)} countries")
        if countries:
            print(f"First country: {countries[0].get('country_name', 'N/A')}")

        # Test 2: Get leagues (England)
        print("\nTest 2: Getting leagues...")
        leagues = await api_football_client.get_leagues()
        print(f"SUCCESS: Retrieved {len(leagues)} leagues")
        if leagues:
            premier_league = next((l for l in leagues if 'Premier League' in l.get('league_name', '')), None)
            if premier_league:
                league_id = premier_league.get('league_id')
                print(f"Found Premier League: ID={league_id}")

                # Test 3: Get teams from Premier League
                if league_id:
                    print(f"\nTest 3: Getting teams from league {league_id}...")
                    teams = await api_football_client.get_teams(league_id=int(league_id))
                    print(f"SUCCESS: Retrieved {len(teams)} teams")
                    if teams:
                        print(f"First team: {teams[0].get('team_name', 'N/A')}")

        # Test 4: Get upcoming fixtures
        print("\nTest 4: Getting upcoming fixtures...")
        from datetime import datetime, timedelta
        today = datetime.now().strftime('%Y-%m-%d')
        week_ahead = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

        fixtures = await api_football_client.get_fixtures(
            date_from=today,
            date_to=week_ahead
        )
        print(f"SUCCESS: Retrieved {len(fixtures)} fixtures")
        if fixtures:
            first_match = fixtures[0]
            print(f"First match: {first_match.get('match_hometeam_name', 'N/A')} vs {first_match.get('match_awayteam_name', 'N/A')}")

        print("\n" + "=" * 80)
        print("All API tests completed successfully!")
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
    asyncio.run(test_new_api())
