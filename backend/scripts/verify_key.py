"""
Verify the API key is correctly loaded from .env
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings

print("=" * 80)
print("API Key Verification")
print("=" * 80)
print(f"APIFOOTBALL_API_KEY from settings:")
print(f"  Value: {settings.APIFOOTBALL_API_KEY}")
print(f"  Length: {len(settings.APIFOOTBALL_API_KEY)}")
print(f"  Type: {type(settings.APIFOOTBALL_API_KEY)}")
print(f"  First 20 chars: {settings.APIFOOTBALL_API_KEY[:20]}")
print(f"  Last 20 chars: {settings.APIFOOTBALL_API_KEY[-20:]}")
print("")
print("Expected from screenshot:")
print("  43203ffe99c5c31af1673bb1084dc67305727348e5ae214358488ce2250eb460")
print("")
print("Do they match?")
expected = "43203ffe99c5c31af1673bb1084dc67305727348e5ae214358488ce2250eb460"
print(f"  {settings.APIFOOTBALL_API_KEY == expected}")
print("=" * 80)
