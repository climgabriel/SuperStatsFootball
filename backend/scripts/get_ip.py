"""
Get the current public IP address of the server.
This is needed to whitelist the IP in API-Football.
"""

import sys
import os
import asyncio
import httpx

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


async def get_public_ip():
    """Get public IP address using multiple services."""

    print("=" * 80)
    print("Getting Public IP Address")
    print("=" * 80)

    services = [
        "https://api.ipify.org?format=json",
        "https://ifconfig.me/ip",
        "https://icanhazip.com",
    ]

    async with httpx.AsyncClient(timeout=10.0) as client:
        for service in services:
            try:
                print(f"\nTrying {service}...")
                response = await client.get(service)

                if "json" in service:
                    ip = response.json()["ip"]
                else:
                    ip = response.text.strip()

                print(f"SUCCESS: Your public IP is: {ip}")
                print("=" * 80)
                print("\nNext steps:")
                print("1. Copy this IP address")
                print("2. Go to https://www.api-football.com/")
                print("3. Navigate to 'SET IP' section")
                print("4. Add this IP to the whitelist")
                print("5. Click 'Save'")
                print("=" * 80)
                return ip

            except Exception as e:
                print(f"Failed: {str(e)}")
                continue

    print("\nERROR: Could not determine public IP")
    return None


if __name__ == "__main__":
    asyncio.run(get_public_ip())
