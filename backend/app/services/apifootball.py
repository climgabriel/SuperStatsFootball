import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import asyncio
from app.core.config import settings
from app.utils.logger import logger


class APIFootballClient:
    """Client for API-Football API."""

    def __init__(self):
        self.base_url = settings.APIFOOTBALL_BASE_URL
        self.api_key = settings.APIFOOTBALL_API_KEY
        self.headers = {
            "x-rapidapi-host": "v3.football.api-sports.io",
            "x-rapidapi-key": self.api_key
        }
        self.client = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self.client is None:
            self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)
        return self.client

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make an API request with rate limiting and error handling."""
        if not self.api_key:
            logger.warning("API-Football API key not configured")
            return {"response": [], "errors": ["API key not configured"]}

        url = f"{self.base_url}/{endpoint}"
        client = await self._get_client()

        try:
            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # Log API usage
            logger.info(f"API-Football request: {endpoint} - {response.status_code}")
            rate_limit = response.headers.get('x-ratelimit-remaining', 'N/A')
            rate_limit_total = response.headers.get('x-ratelimit-limit', 'N/A')
            logger.info(f"Rate limit: {rate_limit}/{rate_limit_total}")

            if data.get("errors"):
                logger.error(f"API-Football error: {data['errors']}")
                raise Exception(f"API error: {data['errors']}")

            return data

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during API request: {str(e)}")
            return {"response": [], "errors": [str(e)]}
        except Exception as e:
            logger.error(f"Error during API request: {str(e)}")
            return {"response": [], "errors": [str(e)]}

    async def get_leagues(self, season: Optional[int] = None, country: Optional[str] = None) -> List[Dict]:
        """Get leagues."""
        params = {}
        if season:
            params["season"] = season
        if country:
            params["country"] = country

        data = await self._make_request("leagues", params)
        return data.get("response", [])

    async def get_teams(self, league_id: int, season: int) -> List[Dict]:
        """Get teams in a league for a season."""
        params = {
            "league": league_id,
            "season": season
        }

        data = await self._make_request("teams", params)
        return data.get("response", [])

    async def get_fixtures(
        self,
        league_id: Optional[int] = None,
        season: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        team_id: Optional[int] = None,
        fixture_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get fixtures."""
        params = {}

        if fixture_id:
            params["id"] = fixture_id
        if league_id:
            params["league"] = league_id
        if season:
            params["season"] = season
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to
        if team_id:
            params["team"] = team_id
        if status:
            params["status"] = status

        data = await self._make_request("fixtures", params)
        return data.get("response", [])

    async def get_fixture_statistics(self, fixture_id: int) -> List[Dict]:
        """Get statistics for a fixture."""
        params = {"fixture": fixture_id}
        data = await self._make_request("fixtures/statistics", params)
        return data.get("response", [])

    async def get_fixture_events(self, fixture_id: int) -> List[Dict]:
        """Get events (goals, cards, etc.) for a fixture."""
        params = {"fixture": fixture_id}
        data = await self._make_request("fixtures/events", params)
        return data.get("response", [])

    async def get_standings(self, league_id: int, season: int) -> List[Dict]:
        """Get league standings."""
        params = {
            "league": league_id,
            "season": season
        }
        data = await self._make_request("standings", params)
        return data.get("response", [])

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None


# Global client instance
api_football_client = APIFootballClient()
