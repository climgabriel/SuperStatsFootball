"""
Test if the API key works with apifootball.com domain
"""
import httpx
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings


async def test_different_domains():
    """Test API key with different domain endpoints."""

    api_key = settings.APIFOOTBALL_API_KEY

    print("=" * 80)
    print("Testing Different API Domains")
    print("=" * 80)
    print(f"API Key: {api_key[:20]}...")
    print("=" * 80)

    # Test different base URLs
    test_configs = [
        {
            "name": "API-Sports.io (current)",
            "base_url": "https://v3.football.api-sports.io",
            "headers": {"x-apisports-key": api_key},
            "endpoint": "/leagues",
            "params": {"season": 2024}
        },
        {
            "name": "APIFootball.com (query param)",
            "base_url": "https://apiv3.apifootball.com",
            "headers": {},
            "endpoint": "",
            "params": {"action": "get_countries", "APIkey": api_key}
        },
    ]

    for config in test_configs:
        print(f"\n{config['name']}:")
        print(f"  URL: {config['base_url']}")
        print(f"  Headers: {list(config['headers'].keys())}")

        async with httpx.AsyncClient(headers=config['headers'], timeout=10.0) as client:
            try:
                url = f"{config['base_url']}{config['endpoint']}"
                response = await client.get(url, params=config['params'])

                print(f"  Status: {response.status_code}")

                data = response.json()

                if 'errors' in data and data['errors']:
                    print(f"  ERROR: {data['errors']}")
                elif 'error' in data:
                    print(f"  ERROR: {data['error']}")
                elif isinstance(data, list) and len(data) > 0:
                    print(f"  SUCCESS: Got {len(data)} results")
                    print(f"  First result: {list(data[0].keys())[:5]}")
                elif 'response' in data:
                    print(f"  SUCCESS: Got {len(data.get('response', []))} results")
                else:
                    print(f"  Response keys: {list(data.keys())}")

            except Exception as e:
                print(f"  Exception: {str(e)}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(test_different_domains())
