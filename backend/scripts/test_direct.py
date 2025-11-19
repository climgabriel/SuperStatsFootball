"""
Direct API test without using the client class.
"""
import httpx
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings


async def test_direct():
    """Test API-Football directly."""

    api_key = settings.APIFOOTBALL_API_KEY

    print("=" * 80)
    print("Direct API-Football Test")
    print("=" * 80)
    print(f"API Key: {api_key[:20]}...")
    print(f"Base URL: {settings.APIFOOTBALL_BASE_URL}")
    print("=" * 80)

    # Test with correct header
    headers = {
        "x-apisports-key": api_key
    }

    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        try:
            print("\nTest 1: GET /leagues (with x-apisports-key header)")
            response = await client.get(
                f"{settings.APIFOOTBALL_BASE_URL}/leagues",
                params={"season": 2024}
            )

            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")

            data = response.json()
            print(f"\nResponse:")

            if data.get("errors"):
                print(f"ERRORS: {data['errors']}")
            else:
                print(f"SUCCESS: Got {len(data.get('response', []))} leagues")
                if data.get('response'):
                    first_league = data['response'][0]
                    print(f"First league: {first_league['league']['name']}")

        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_direct())
