import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
import asyncio
from app.core.config import settings
from app.utils.logger import logger


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""
    pass


class APIFootballClient:
    """
    Client for APIFootball.com API (apiv3.apifootball.com).

    Uses query parameter authentication with action-based endpoints.
    """

    def __init__(self):
        self.base_url = settings.APIFOOTBALL_BASE_URL
        self.api_key = settings.APIFOOTBALL_API_KEY
        self.client = None
        self.max_retries = 3
        self.base_backoff = 2.0

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client (no auth headers needed)."""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=30.0)
        return self.client

    async def _make_request(self, action: str, params: Optional[Dict] = None) -> Any:
        """
        Make an API request with retry logic.

        Args:
            action: API action (e.g., 'get_leagues', 'get_teams')
            params: Additional query parameters

        Returns:
            API response data (usually a list)
        """
        if not self.api_key:
            logger.warning("API-Football API key not configured")
            return []

        if not self.api_key.strip():
            logger.error("API-Football API key is empty")
            return []

        # Build query parameters
        query_params = {"action": action, "APIkey": self.api_key}
        if params:
            query_params.update(params)

        client = await self._get_client()

        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                response = await client.get(self.base_url, params=query_params)
                response.raise_for_status()

                data = response.json()

                # Log API usage
                logger.info(f"APIFootball request: action={action} - {response.status_code}")

                # Check for errors in response
                if isinstance(data, dict) and 'error' in data:
                    error_msg = data['error']
                    logger.error(f"APIFootball error: {error_msg}")

                    if 'rate limit' in error_msg.lower() or 'quota' in error_msg.lower():
                        if attempt < self.max_retries - 1:
                            backoff_time = self.base_backoff * (2 ** attempt)
                            logger.warning(f"Rate limit error. Retrying in {backoff_time}s")
                            await asyncio.sleep(backoff_time)
                            continue
                        else:
                            raise RateLimitError(f"Rate limit exceeded: {error_msg}")

                    raise Exception(f"API error: {error_msg}")

                # Success - return data
                return data if data else []

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    if attempt < self.max_retries - 1:
                        backoff_time = self.base_backoff * (2 ** attempt)
                        logger.warning(f"HTTP 429 - Rate limit exceeded. Retrying in {backoff_time}s")
                        await asyncio.sleep(backoff_time)
                        continue
                    else:
                        logger.error(f"HTTP 429 - Rate limit exceeded after {self.max_retries} attempts")
                        return []
                else:
                    logger.error(f"HTTP error: {str(e)}")
                    return []

            except httpx.HTTPError as e:
                logger.error(f"HTTP error: {str(e)}")
                if attempt < self.max_retries - 1:
                    backoff_time = self.base_backoff * (2 ** attempt)
                    logger.warning(f"Retrying in {backoff_time}s")
                    await asyncio.sleep(backoff_time)
                    continue
                return []

            except Exception as e:
                logger.error(f"Error during API request: {str(e)}")
                if attempt < self.max_retries - 1:
                    backoff_time = self.base_backoff * (2 ** attempt)
                    await asyncio.sleep(backoff_time)
                    continue
                return []

        return []

    async def get_countries(self) -> List[Dict]:
        """Get all available countries."""
        return await self._make_request("get_countries")

    async def get_leagues(self, country_id: Optional[int] = None) -> List[Dict]:
        """
        Get leagues, optionally filtered by country.

        Args:
            country_id: Filter by country ID

        Returns:
            List of league data
        """
        params = {}
        if country_id:
            params["country_id"] = country_id

        return await self._make_request("get_leagues", params)

    async def get_teams(self, league_id: int) -> List[Dict]:
        """
        Get teams in a league.

        Args:
            league_id: League ID

        Returns:
            List of team data with full rosters
        """
        params = {"league_id": league_id}
        return await self._make_request("get_teams", params)

    async def get_team(self, team_id: int) -> List[Dict]:
        """
        Get specific team details.

        Args:
            team_id: Team ID

        Returns:
            Team data
        """
        params = {"team_id": team_id}
        return await self._make_request("get_teams", params)

    async def get_fixtures(
        self,
        league_id: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        team_id: Optional[int] = None,
        match_id: Optional[int] = None,
        match_live: bool = False
    ) -> List[Dict]:
        """
        Get fixtures/matches (called 'events' in apifootball.com).

        Args:
            league_id: Filter by league
            date_from: Start date (yyyy-mm-dd)
            date_to: End date (yyyy-mm-dd)
            team_id: Filter by team
            match_id: Get specific match
            match_live: Only get live matches

        Returns:
            List of match/fixture data
        """
        params = {}

        if match_id:
            params["match_id"] = match_id
        if league_id:
            params["league_id"] = league_id
        if team_id:
            params["team_id"] = team_id
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to
        if match_live:
            params["match_live"] = "1"

        return await self._make_request("get_events", params)

    async def get_fixture_statistics(self, match_id: int) -> List[Dict]:
        """
        Get statistics for a match.

        Args:
            match_id: Match ID

        Returns:
            Match statistics
        """
        params = {"match_id": match_id}
        return await self._make_request("get_statistics", params)

    async def get_lineups(self, match_id: int) -> List[Dict]:
        """
        Get lineups for a match.

        Args:
            match_id: Match ID

        Returns:
            Lineup data
        """
        params = {"match_id": match_id}
        return await self._make_request("get_lineups", params)

    async def get_standings(self, league_id: int) -> List[Dict]:
        """
        Get league standings/table.

        Args:
            league_id: League ID

        Returns:
            Standings data
        """
        params = {"league_id": league_id}
        return await self._make_request("get_standings", params)

    async def get_odds(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        match_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get betting odds.

        Args:
            date_from: Start date (yyyy-mm-dd)
            date_to: End date (yyyy-mm-dd)
            match_id: Specific match ID

        Returns:
            Odds data from multiple bookmakers
        """
        params = {}

        if match_id:
            params["match_id"] = match_id
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to

        return await self._make_request("get_odds", params)

    async def get_predictions(
        self,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        league_id: Optional[int] = None,
        match_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Get AI/mathematical predictions.

        Args:
            date_from: Start date (yyyy-mm-dd)
            date_to: End date (yyyy-mm-dd)
            league_id: Filter by league
            match_id: Specific match ID

        Returns:
            Prediction data with probabilities
        """
        params = {}

        if match_id:
            params["match_id"] = match_id
        if league_id:
            params["league_id"] = league_id
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to

        return await self._make_request("get_predictions", params)

    async def get_h2h(
        self,
        first_team_id: int,
        second_team_id: int
    ) -> List[Dict]:
        """
        Get head-to-head history between two teams.

        Args:
            first_team_id: First team ID
            second_team_id: Second team ID

        Returns:
            H2H match history
        """
        params = {
            "firstTeamId": first_team_id,
            "secondTeamId": second_team_id
        }
        return await self._make_request("get_H2H", params)

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None


# Global client instance
api_football_client = APIFootballClient()
