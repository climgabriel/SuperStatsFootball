"""
Test API-Football account status
"""
import httpx
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings


async def test_account_status():
    """Test API account and different header combinations."""

    api_key = settings.APIFOOTBALL_API_KEY

    print("=" * 80)
    print("API-Football Account Status Test")
    print("=" * 80)
    print(f"API Key: {api_key}")
    print(f"Base URL: {settings.APIFOOTBALL_BASE_URL}")
    print("=" * 80)

    # Test different header combinations
    header_tests = [
        {"x-apisports-key": api_key},
        {"x-rapidapi-key": api_key},
        {"x-rapidapi-key": api_key, "x-rapidapi-host": "v3.football.api-sports.io"},
    ]

    for i, headers in enumerate(header_tests, 1):
        print(f"\nTest {i}: Headers = {list(headers.keys())}")

        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
            try:
                # Try the /status endpoint to check account
                response = await client.get(f"{settings.APIFOOTBALL_BASE_URL}/status")

                print(f"  Status Code: {response.status_code}")
                data = response.json()

                if 'errors' in data and data['errors']:
                    print(f"  ERROR: {data['errors']}")
                elif 'response' in data:
                    print(f"  SUCCESS!")
                    print(f"  Response: {data['response']}")
                else:
                    print(f"  Response: {data}")

            except Exception as e:
                print(f"  Exception: {str(e)}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_account_status())
