"""
Data Synchronization Service for API-Football

Handles:
- Bulk league data synchronization
- Historical data import (current + 4 previous seasons)
- Season rotation and cleanup
- Rate limiting and error handling
- Progress tracking
"""

import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from app.services.apifootball import api_football_client
from app.services.season_manager import SeasonManager
from app.models.league import League
from app.models.team import Team
from app.models.fixture import Fixture, FixtureStat, FixtureScore
from app.models.odds import FixtureOdds
from app.models.standing import Standing
from app.models.lineup import Lineup, PlayerStatistic
from app.models.top_scorer import TopScorer
from app.models.api_prediction import APIFootballPrediction
from app.models.h2h import H2HMatch
from app.core.leagues_config import (
    get_all_league_ids,
    get_sync_priority_leagues,
    get_tier_for_league,
    LEAGUE_METADATA,
    SYNC_CONFIG
)

logger = logging.getLogger(__name__)


class DataSyncService:
    """Service for synchronizing football data from API-Football."""

    def __init__(self, db: Session):
        self.db = db
        self.season_manager = SeasonManager(db)
        self.sync_stats = {
            "leagues_synced": 0,
            "teams_synced": 0,
            "fixtures_synced": 0,
            "stats_synced": 0,
            "errors": []
        }

    async def sync_all_leagues(
        self,
        tier_filter: Optional[str] = None,
        limit: Optional[int] = None
    ) -> Dict:
        """
        Sync all leagues or filtered by tier.

        Args:
            tier_filter: Only sync leagues for specific tier
            limit: Limit number of leagues to sync

        Returns:
            Sync statistics dictionary
        """
        logger.info("Starting full league synchronization...")

        # Check and perform season cleanup first
        transition_info = self.season_manager.check_season_transition()
        if transition_info["cleanup_performed"]:
            logger.info(f"Season cleanup performed: {transition_info['cleanup_stats']}")

        # Get leagues to sync
        if tier_filter:
            from app.core.leagues_config import get_leagues_for_tier
            league_ids = get_leagues_for_tier(tier_filter)
        else:
            league_ids = get_sync_priority_leagues()

        if limit:
            league_ids = league_ids[:limit]

        logger.info(f"Syncing {len(league_ids)} leagues...")

        # Get valid seasons to sync
        current_season = self.season_manager.get_current_season()
        valid_seasons = self.season_manager.get_valid_seasons(current_season)

        # Sync leagues in batches to avoid overwhelming API
        batch_size = SYNC_CONFIG["parallel_leagues"]
        for i in range(0, len(league_ids), batch_size):
            batch = league_ids[i:i + batch_size]

            # Sync each league in batch
            tasks = []
            for league_id in batch:
                for season in valid_seasons:
                    task = self._sync_league_season(league_id, season)
                    tasks.append(task)

            # Wait for batch to complete
            await asyncio.gather(*tasks, return_exceptions=True)

            # Rate limiting between batches
            if i + batch_size < len(league_ids):
                await asyncio.sleep(SYNC_CONFIG["rate_limit_delay"])

        result = {
            "status": "completed",
            "transition_info": transition_info,
            "sync_stats": self.sync_stats,
            "leagues_synced": self.sync_stats["leagues_synced"],
            "total_fixtures": self.sync_stats["fixtures_synced"]
        }

        logger.info(f"Synchronization completed: {result}")
        return result

    async def _sync_league_season(self, league_id: int, season: int) -> None:
        """Sync a specific league for a specific season."""
        try:
            logger.info(f"Syncing league {league_id}, season {season}...")

            # 1. Sync or update league metadata
            await self._upsert_league(league_id, season)

            # 2. Sync teams for this league/season
            await self._sync_teams(league_id, season)

            # 3. Sync fixtures for this league/season
            await self._sync_fixtures(league_id, season)

            self.sync_stats["leagues_synced"] += 1

        except Exception as e:
            error_msg = f"Error syncing league {league_id}, season {season}: {str(e)}"
            logger.error(error_msg)
            self.sync_stats["errors"].append(error_msg)

    async def _upsert_league(self, league_id: int, season: int) -> None:
        """Create or update league in database."""
        try:
            # Rate limiting: Add delay before API call
            await asyncio.sleep(SYNC_CONFIG["api_call_delay"])

            # Get league info from API-Football
            leagues_data = await api_football_client.get_leagues(season=season)

            league_data = next(
                (l for l in leagues_data if l["league"]["id"] == league_id),
                None
            )

            if not league_data:
                # Use metadata if API doesn't return data
                metadata = LEAGUE_METADATA.get(league_id, {})
                if metadata:
                    league_data = {
                        "league": {
                            "id": league_id,
                            "name": metadata["name"],
                            "logo": None
                        },
                        "country": {
                            "name": metadata["country"]
                        }
                    }

            if not league_data:
                logger.warning(f"No data found for league {league_id}")
                return

            # Check if league exists (using composite primary key)
            league = self.db.query(League).filter(
                League.id == league_id,
                League.season == season
            ).first()

            tier = get_tier_for_league(league_id)

            if not league:
                league = League(
                    id=league_data["league"]["id"],
                    name=league_data["league"]["name"],
                    country=league_data["country"]["name"],
                    logo=league_data["league"].get("logo"),
                    season=season,
                    tier_required=tier,
                    is_active=True,
                    priority=LEAGUE_METADATA.get(league_id, {}).get("priority", 0)
                )
                self.db.add(league)
            else:
                # Update existing
                league.name = league_data["league"]["name"]
                league.logo = league_data["league"].get("logo")
                league.tier_required = tier
                league.updated_at = datetime.utcnow()

            self.db.commit()

        except Exception as e:
            logger.error(f"Error upserting league {league_id}: {str(e)}")
            self.db.rollback()
            raise

    async def _sync_teams(self, league_id: int, season: int) -> None:
        """Sync teams for a league/season."""
        try:
            # Rate limiting: Add delay before API call
            await asyncio.sleep(SYNC_CONFIG["api_call_delay"])

            teams_data = await api_football_client.get_teams(league_id, season)

            for team_data in teams_data:
                team_info = team_data["team"]
                venue_info = team_data.get("venue", {})

                team = self.db.query(Team).filter(Team.id == team_info["id"]).first()

                if not team:
                    team = Team(
                        id=team_info["id"],
                        name=team_info["name"],
                        code=team_info.get("code"),
                        country=team_info.get("country"),
                        logo=team_info.get("logo"),
                        founded=team_info.get("founded"),
                        venue_name=venue_info.get("name"),
                        venue_capacity=venue_info.get("capacity")
                    )
                    self.db.add(team)
                else:
                    # Update existing
                    team.name = team_info["name"]
                    team.logo = team_info.get("logo")
                    team.updated_at = datetime.utcnow()

                self.sync_stats["teams_synced"] += 1

            self.db.commit()

        except Exception as e:
            logger.error(f"Error syncing teams for league {league_id}: {str(e)}")
            self.db.rollback()
            raise

    async def _sync_fixtures(self, league_id: int, season: int) -> None:
        """Sync fixtures for a league/season."""
        try:
            # Rate limiting: Add delay before API call
            await asyncio.sleep(SYNC_CONFIG["api_call_delay"])

            fixtures_data = await api_football_client.get_fixtures(
                league_id=league_id,
                season=season
            )

            for fixture_data in fixtures_data:
                await self._upsert_fixture(fixture_data)

                # Small delay to avoid overwhelming database
                if self.sync_stats["fixtures_synced"] % 100 == 0:
                    await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Error syncing fixtures for league {league_id}: {str(e)}")
            raise

    async def _upsert_fixture(self, fixture_data: Dict) -> None:
        """Create or update a single fixture."""
        try:
            fixture_info = fixture_data["fixture"]
            league_info = fixture_data["league"]
            teams_info = fixture_data["teams"]
            score_info = fixture_data["score"]

            # Upsert fixture
            fixture = self.db.query(Fixture).filter(
                Fixture.id == fixture_info["id"]
            ).first()

            if not fixture:
                fixture = Fixture(
                    id=fixture_info["id"],
                    league_id=league_info["id"],
                    season=league_info["season"],
                    round=league_info.get("round"),
                    match_date=datetime.fromisoformat(
                        fixture_info["date"].replace("Z", "+00:00")
                    ),
                    timestamp=fixture_info["timestamp"],
                    home_team_id=teams_info["home"]["id"],
                    away_team_id=teams_info["away"]["id"],
                    status=fixture_info["status"]["short"],
                    elapsed_time=fixture_info["status"].get("elapsed"),
                    venue=fixture_info.get("venue", {}).get("name"),
                    referee=fixture_info.get("referee")
                )
                self.db.add(fixture)
            else:
                # Update existing
                fixture.status = fixture_info["status"]["short"]
                fixture.elapsed_time = fixture_info["status"].get("elapsed")
                fixture.updated_at = datetime.utcnow()

            self.db.commit()

            # Sync score
            await self._upsert_score(fixture.id, score_info)

            # Sync stats if match is finished
            if fixture.status in ["FT", "AET", "PEN"]:
                await self._sync_fixture_stats(fixture.id)

            self.sync_stats["fixtures_synced"] += 1

        except Exception as e:
            logger.error(f"Error upserting fixture: {str(e)}")
            self.db.rollback()
            raise

    async def _upsert_score(self, fixture_id: int, score_info: Dict) -> None:
        """Create or update fixture score."""
        try:
            score = self.db.query(FixtureScore).filter(
                FixtureScore.fixture_id == fixture_id
            ).first()

            halftime = score_info.get("halftime", {})
            fulltime = score_info.get("fulltime", {})
            extratime = score_info.get("extratime", {})
            penalty = score_info.get("penalty", {})

            if not score:
                score = FixtureScore(
                    fixture_id=fixture_id,
                    home_halftime=halftime.get("home"),
                    away_halftime=halftime.get("away"),
                    home_fulltime=fulltime.get("home"),
                    away_fulltime=fulltime.get("away"),
                    home_extratime=extratime.get("home"),
                    away_extratime=extratime.get("away"),
                    home_penalty=penalty.get("home"),
                    away_penalty=penalty.get("away")
                )
                self.db.add(score)
            else:
                score.home_halftime = halftime.get("home")
                score.away_halftime = halftime.get("away")
                score.home_fulltime = fulltime.get("home")
                score.away_fulltime = fulltime.get("away")
                score.home_extratime = extratime.get("home")
                score.away_extratime = extratime.get("away")
                score.home_penalty = penalty.get("home")
                score.away_penalty = penalty.get("away")
                score.updated_at = datetime.utcnow()

            self.db.commit()

        except Exception as e:
            logger.error(f"Error upserting score for fixture {fixture_id}: {str(e)}")
            self.db.rollback()

    async def _sync_fixture_stats(self, fixture_id: int) -> None:
        """Sync statistics for a finished fixture."""
        try:
            stats_data = await api_football_client.get_fixture_statistics(fixture_id)

            for team_stats in stats_data:
                team_id = team_stats["team"]["id"]
                statistics = {
                    stat["type"]: stat["value"]
                    for stat in team_stats["statistics"]
                }

                # Upsert fixture stats
                fixture_stat = self.db.query(FixtureStat).filter(
                    FixtureStat.fixture_id == fixture_id,
                    FixtureStat.team_id == team_id
                ).first()

                if not fixture_stat:
                    fixture_stat = FixtureStat(
                        fixture_id=fixture_id,
                        team_id=team_id
                    )
                    self.db.add(fixture_stat)

                # Map statistics
                fixture_stat.shots_on_goal = statistics.get("Shots on Goal")
                fixture_stat.shots_off_goal = statistics.get("Shots off Goal")
                fixture_stat.total_shots = statistics.get("Total Shots")
                fixture_stat.blocked_shots = statistics.get("Blocked Shots")
                fixture_stat.shots_inside_box = statistics.get("Shots insidebox")
                fixture_stat.shots_outside_box = statistics.get("Shots outsidebox")
                fixture_stat.fouls = statistics.get("Fouls")
                fixture_stat.corners = statistics.get("Corner Kicks")
                fixture_stat.offsides = statistics.get("Offsides")

                # Parse possession
                possession = statistics.get("Ball Possession", "0%")
                fixture_stat.ball_possession = int(possession.replace("%", ""))

                fixture_stat.yellow_cards = statistics.get("Yellow Cards")
                fixture_stat.red_cards = statistics.get("Red Cards")
                fixture_stat.goalkeeper_saves = statistics.get("Goalkeeper Saves")
                fixture_stat.total_passes = statistics.get("Total passes")
                fixture_stat.passes_accurate = statistics.get("Passes accurate")

                # Parse pass percentage
                passes_pct = statistics.get("Passes %", "0%")
                fixture_stat.passes_percentage = int(passes_pct.replace("%", ""))

                fixture_stat.updated_at = datetime.utcnow()

                self.sync_stats["stats_synced"] += 1

            self.db.commit()

        except Exception as e:
            logger.error(f"Error syncing stats for fixture {fixture_id}: {str(e)}")
            self.db.rollback()

    async def _get_superbet_id(self) -> Optional[int]:
        """
        Get Superbet.ro bookmaker ID from API-Football.
        Caches the result in class variable.
        """
        if not hasattr(self, '_superbet_id_cache'):
            try:
                bookmakers = await api_football_client.get_bookmakers()
                # Search for Superbet bookmaker
                superbet = next(
                    (b for b in bookmakers if "superbet" in b.get("name", "").lower()),
                    None
                )
                if superbet:
                    self._superbet_id_cache = superbet["id"]
                    logger.info(f"Found Superbet bookmaker ID: {self._superbet_id_cache}")
                else:
                    logger.warning("Superbet bookmaker not found in API-Football")
                    self._superbet_id_cache = None
            except Exception as e:
                logger.error(f"Error fetching bookmakers: {str(e)}")
                self._superbet_id_cache = None

        return self._superbet_id_cache

    def _parse_odds_value(self, bet_values: List[Dict], value_name: str) -> Optional[float]:
        """
        Parse odds value from API-Football bet values array.

        Args:
            bet_values: List of bet value objects
            value_name: Name of the value to extract (e.g., "Home", "Draw", "Away", "Over 2.5", "Under 2.5")

        Returns:
            Odds value as float or None
        """
        for value in bet_values:
            if value.get("value") == value_name:
                return float(value.get("odd", 0))
        return None

    async def _sync_fixture_odds(self, fixture_id: int, is_live: bool = False) -> None:
        """
        Sync Superbet odds for a specific fixture.

        Args:
            fixture_id: Fixture ID
            is_live: True for live odds, False for pre-match odds
        """
        try:
            superbet_id = await self._get_superbet_id()
            if not superbet_id:
                logger.warning("Cannot sync odds: Superbet bookmaker not found")
                return

            # Fetch odds from API-Football
            if is_live:
                odds_data = await api_football_client.get_live_odds(fixture_id, bookmaker=superbet_id)
            else:
                odds_data = await api_football_client.get_odds(fixture_id, bookmaker=superbet_id)

            if not odds_data:
                logger.debug(f"No odds data found for fixture {fixture_id}")
                return

            # Parse odds response
            for odds_entry in odds_data:
                bookmakers = odds_entry.get("bookmakers", [])
                if not bookmakers:
                    continue

                # Get Superbet bookmaker data
                superbet_data = next(
                    (b for b in bookmakers if b.get("id") == superbet_id),
                    None
                )
                if not superbet_data:
                    continue

                # Extract bets
                bets = superbet_data.get("bets", [])

                # Find Match Winner (1X2) bet (bet id: 1)
                match_winner = next((b for b in bets if b.get("id") == 1), None)
                # Find Goals Over/Under bet (bet id: 5)
                over_under = next((b for b in bets if b.get("id") == 5), None)
                # Find HT/FT bets if available
                ht_ft = next((b for b in bets if "halftime" in b.get("name", "").lower()), None)

                # Check if odds record exists
                odds_record = self.db.query(FixtureOdds).filter(
                    FixtureOdds.fixture_id == fixture_id,
                    FixtureOdds.bookmaker_id == superbet_id,
                    FixtureOdds.is_live == is_live
                ).first()

                if not odds_record:
                    odds_record = FixtureOdds(
                        fixture_id=fixture_id,
                        bookmaker_id=superbet_id,
                        bookmaker_name="Superbet",
                        is_live=is_live
                    )
                    self.db.add(odds_record)

                # Parse and update odds
                if match_winner:
                    values = match_winner.get("values", [])
                    odds_record.home_win_odds = self._parse_odds_value(values, "Home")
                    odds_record.draw_odds = self._parse_odds_value(values, "Draw")
                    odds_record.away_win_odds = self._parse_odds_value(values, "Away")

                    # Also set fulltime odds (same as match winner for now)
                    odds_record.ft_home_win_odds = odds_record.home_win_odds
                    odds_record.ft_draw_odds = odds_record.draw_odds
                    odds_record.ft_away_win_odds = odds_record.away_win_odds

                if over_under:
                    values = over_under.get("values", [])
                    odds_record.over_2_5_odds = self._parse_odds_value(values, "Over 2.5")
                    odds_record.under_2_5_odds = self._parse_odds_value(values, "Under 2.5")

                # For halftime odds, try to find halftime-specific bets
                if ht_ft:
                    values = ht_ft.get("values", [])
                    odds_record.ht_home_win_odds = self._parse_odds_value(values, "Home/Home")
                    odds_record.ht_draw_odds = self._parse_odds_value(values, "Draw/Draw")
                    odds_record.ht_away_win_odds = self._parse_odds_value(values, "Away/Away")

                # Update metadata
                odds_record.fetched_at = datetime.utcnow()
                odds_record.updated_at = datetime.utcnow()

                self.db.commit()
                logger.info(f"{'Live' if is_live else 'Pre-match'} odds synced for fixture {fixture_id}")

        except Exception as e:
            logger.error(f"Error syncing odds for fixture {fixture_id}: {str(e)}")
            self.db.rollback()

    async def sync_pre_match_odds(self, days_ahead: int = 7, league_id: Optional[int] = None) -> Dict:
        """
        Sync pre-match odds for upcoming fixtures.

        Args:
            days_ahead: Number of days to look ahead
            league_id: Optional league filter

        Returns:
            Sync statistics
        """
        try:
            logger.info(f"Starting pre-match odds sync for next {days_ahead} days...")

            # Get upcoming fixtures
            from datetime import timedelta
            now = datetime.utcnow()
            end_date = now + timedelta(days=days_ahead)

            query = self.db.query(Fixture).filter(
                Fixture.match_date >= now,
                Fixture.match_date <= end_date,
                Fixture.status.in_(["NS", "TBD"])  # Not started
            )

            if league_id:
                query = query.filter(Fixture.league_id == league_id)

            fixtures = query.all()

            logger.info(f"Found {len(fixtures)} upcoming fixtures")

            # Sync odds for each fixture
            synced_count = 0
            errors = []

            for fixture in fixtures:
                try:
                    await self._sync_fixture_odds(fixture.id, is_live=False)
                    synced_count += 1

                    # Rate limiting
                    await asyncio.sleep(0.5)  # 0.5 second delay between requests

                except Exception as e:
                    error_msg = f"Error syncing odds for fixture {fixture.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            result = {
                "status": "completed",
                "fixtures_processed": len(fixtures),
                "odds_synced": synced_count,
                "errors": errors
            }

            logger.info(f"Pre-match odds sync completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in pre-match odds sync: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def sync_live_odds(self, league_id: Optional[int] = None) -> Dict:
        """
        Sync live odds for ongoing matches.

        Args:
            league_id: Optional league filter

        Returns:
            Sync statistics
        """
        try:
            logger.info("Starting live odds sync...")

            # Get live fixtures
            query = self.db.query(Fixture).filter(
                Fixture.status.in_(["1H", "2H", "HT", "ET", "P", "LIVE"])
            )

            if league_id:
                query = query.filter(Fixture.league_id == league_id)

            fixtures = query.all()

            logger.info(f"Found {len(fixtures)} live fixtures")

            # Sync live odds for each fixture
            synced_count = 0
            errors = []

            for fixture in fixtures:
                try:
                    await self._sync_fixture_odds(fixture.id, is_live=True)
                    synced_count += 1

                    # Rate limiting
                    await asyncio.sleep(0.5)

                except Exception as e:
                    error_msg = f"Error syncing live odds for fixture {fixture.id}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)

            result = {
                "status": "completed",
                "fixtures_processed": len(fixtures),
                "odds_synced": synced_count,
                "errors": errors
            }

            logger.info(f"Live odds sync completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error in live odds sync: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }


    async def sync_standings(self, league_id: int, season: Optional[int] = None) -> Dict:
        """
        Sync league standings/table.

        Args:
            league_id: League ID
            season: Optional season (defaults to current)

        Returns:
            Sync statistics
        """
        try:
            if not season:
                season = self.season_manager.get_current_season()

            logger.info(f"Syncing standings for league {league_id}, season {season}...")

            standings_data = await api_football_client.get_standings(league_id)

            if not standings_data:
                logger.warning(f"No standings data for league {league_id}")
                return {"status": "no_data", "league_id": league_id}

            synced_count = 0

            for standing_entry in standings_data:
                team_id = standing_entry.get("team_id")
                if not team_id:
                    continue

                # Check if standing exists
                standing = self.db.query(Standing).filter(
                    Standing.league_id == league_id,
                    Standing.season == season,
                    Standing.team_id == team_id
                ).first()

                if not standing:
                    standing = Standing(
                        league_id=league_id,
                        season=season,
                        team_id=team_id,
                        last_update=datetime.utcnow()
                    )
                    self.db.add(standing)

                # Update standings data
                standing.rank = standing_entry.get("overall_league_position", 0)
                standing.points = standing_entry.get("overall_league_PTS", 0)
                standing.form = standing_entry.get("team_badge")  # Form data if available
                standing.status = standing_entry.get("league_round", "")
                standing.description = standing_entry.get("promotion", "")

                # Overall matches
                standing.played = standing_entry.get("overall_league_payed", 0)
                standing.win = standing_entry.get("overall_league_W", 0)
                standing.draw = standing_entry.get("overall_league_D", 0)
                standing.lose = standing_entry.get("overall_league_L", 0)
                standing.goals_for = standing_entry.get("overall_league_GF", 0)
                standing.goals_against = standing_entry.get("overall_league_GA", 0)
                standing.goal_diff = standing.goals_for - standing.goals_against

                # Home record
                standing.home_played = standing_entry.get("home_league_payed", 0)
                standing.home_win = standing_entry.get("home_league_W", 0)
                standing.home_draw = standing_entry.get("home_league_D", 0)
                standing.home_lose = standing_entry.get("home_league_L", 0)
                standing.home_goals_for = standing_entry.get("home_league_GF", 0)
                standing.home_goals_against = standing_entry.get("home_league_GA", 0)

                # Away record
                standing.away_played = standing_entry.get("away_league_payed", 0)
                standing.away_win = standing_entry.get("away_league_W", 0)
                standing.away_draw = standing_entry.get("away_league_D", 0)
                standing.away_lose = standing_entry.get("away_league_L", 0)
                standing.away_goals_for = standing_entry.get("away_league_GF", 0)
                standing.away_goals_against = standing_entry.get("away_league_GA", 0)

                standing.last_update = datetime.utcnow()
                standing.updated_at = datetime.utcnow()

                synced_count += 1

            self.db.commit()
            logger.info(f"Synced {synced_count} standings for league {league_id}")

            return {
                "status": "success",
                "league_id": league_id,
                "season": season,
                "standings_synced": synced_count
            }

        except Exception as e:
            logger.error(f"Error syncing standings for league {league_id}: {str(e)}")
            self.db.rollback()
            return {"status": "error", "message": str(e)}

    async def sync_lineups(self, fixture_id: int) -> Dict:
        """
        Sync lineups for a specific fixture.

        Args:
            fixture_id: Fixture ID

        Returns:
            Sync statistics
        """
        try:
            logger.info(f"Syncing lineups for fixture {fixture_id}...")

            lineups_data = await api_football_client.get_lineups(fixture_id)

            if not lineups_data:
                logger.warning(f"No lineup data for fixture {fixture_id}")
                return {"status": "no_data", "fixture_id": fixture_id}

            synced_count = 0

            for lineup_entry in lineups_data:
                team_id = lineup_entry.get("team_id")
                if not team_id:
                    continue

                # Check if lineup exists
                lineup = self.db.query(Lineup).filter(
                    Lineup.fixture_id == fixture_id,
                    Lineup.team_id == team_id
                ).first()

                if not lineup:
                    lineup = Lineup(
                        fixture_id=fixture_id,
                        team_id=team_id
                    )
                    self.db.add(lineup)

                # Update lineup data
                lineup.formation = lineup_entry.get("lineup_formation")
                lineup.coach_id = lineup_entry.get("coach_id")
                lineup.coach_name = lineup_entry.get("coach_name")

                # Starting XI and substitutes (stored as JSON)
                lineup.starting_xi = lineup_entry.get("starting_lineups", [])
                lineup.substitutes = lineup_entry.get("substitutes", [])
                lineup.updated_at = datetime.utcnow()

                synced_count += 1

            self.db.commit()
            logger.info(f"Synced {synced_count} lineups for fixture {fixture_id}")

            return {
                "status": "success",
                "fixture_id": fixture_id,
                "lineups_synced": synced_count
            }

        except Exception as e:
            logger.error(f"Error syncing lineups for fixture {fixture_id}: {str(e)}")
            self.db.rollback()
            return {"status": "error", "message": str(e)}

    async def sync_top_scorers(self, league_id: int, season: Optional[int] = None) -> Dict:
        """
        Sync top scorers for a league.

        Args:
            league_id: League ID
            season: Optional season (defaults to current)

        Returns:
            Sync statistics
        """
        try:
            if not season:
                season = self.season_manager.get_current_season()

            logger.info(f"Syncing top scorers for league {league_id}, season {season}...")

            scorers_data = await api_football_client.get_top_scorers(league_id)

            if not scorers_data:
                logger.warning(f"No top scorers data for league {league_id}")
                return {"status": "no_data", "league_id": league_id}

            synced_count = 0

            for scorer_entry in scorers_data:
                player_id = scorer_entry.get("player_id")
                team_id = scorer_entry.get("team_id")

                if not player_id or not team_id:
                    continue

                # Check if top scorer entry exists
                top_scorer = self.db.query(TopScorer).filter(
                    TopScorer.league_id == league_id,
                    TopScorer.season == season,
                    TopScorer.player_id == player_id
                ).first()

                if not top_scorer:
                    top_scorer = TopScorer(
                        league_id=league_id,
                        season=season,
                        player_id=player_id,
                        team_id=team_id,
                        last_update=datetime.utcnow()
                    )
                    self.db.add(top_scorer)

                # Update player info
                top_scorer.player_name = scorer_entry.get("player_name")
                top_scorer.player_age = scorer_entry.get("player_age")
                top_scorer.player_nationality = scorer_entry.get("player_country")
                top_scorer.team_id = team_id

                # Update statistics
                top_scorer.goals_total = int(scorer_entry.get("goals", 0))
                top_scorer.goals_assists = int(scorer_entry.get("assists", 0))
                top_scorer.games_appearances = int(scorer_entry.get("matches", 0))
                top_scorer.penalty_scored = int(scorer_entry.get("penalties", 0))

                top_scorer.last_update = datetime.utcnow()
                top_scorer.updated_at = datetime.utcnow()

                synced_count += 1

            self.db.commit()
            logger.info(f"Synced {synced_count} top scorers for league {league_id}")

            return {
                "status": "success",
                "league_id": league_id,
                "season": season,
                "scorers_synced": synced_count
            }

        except Exception as e:
            logger.error(f"Error syncing top scorers for league {league_id}: {str(e)}")
            self.db.rollback()
            return {"status": "error", "message": str(e)}

    async def sync_api_prediction(self, fixture_id: int) -> Dict:
        """
        Sync API-Football prediction for a fixture.

        Args:
            fixture_id: Fixture ID

        Returns:
            Sync statistics
        """
        try:
            logger.info(f"Syncing API prediction for fixture {fixture_id}...")

            predictions_data = await api_football_client.get_predictions(match_id=fixture_id)

            if not predictions_data or len(predictions_data) == 0:
                logger.warning(f"No prediction data for fixture {fixture_id}")
                return {"status": "no_data", "fixture_id": fixture_id}

            prediction_entry = predictions_data[0]

            # Check if prediction exists
            api_prediction = self.db.query(APIFootballPrediction).filter(
                APIFootballPrediction.fixture_id == fixture_id
            ).first()

            if not api_prediction:
                api_prediction = APIFootballPrediction(
                    fixture_id=fixture_id,
                    fetched_at=datetime.utcnow()
                )
                self.db.add(api_prediction)

            # Update prediction data
            predictions = prediction_entry.get("predictions", {})
            api_prediction.winner_name = predictions.get("winner_name")
            api_prediction.winner_comment = predictions.get("winner_comment")
            api_prediction.under_over = predictions.get("under_over")
            api_prediction.goals_home = predictions.get("goals_home")
            api_prediction.goals_away = predictions.get("goals_away")
            api_prediction.advice = predictions.get("advice")
            api_prediction.percent_home = predictions.get("percent_home")
            api_prediction.percent_draw = predictions.get("percent_draw")
            api_prediction.percent_away = predictions.get("percent_away")

            # Store comparison data as JSON
            api_prediction.comparison = prediction_entry.get("comparison", {})
            api_prediction.h2h = prediction_entry.get("h2h", {})
            api_prediction.league_stats = prediction_entry.get("league", {})
            api_prediction.teams_stats = prediction_entry.get("teams", {})

            api_prediction.fetched_at = datetime.utcnow()
            api_prediction.updated_at = datetime.utcnow()

            self.db.commit()
            logger.info(f"Synced API prediction for fixture {fixture_id}")

            return {
                "status": "success",
                "fixture_id": fixture_id
            }

        except Exception as e:
            logger.error(f"Error syncing API prediction for fixture {fixture_id}: {str(e)}")
            self.db.rollback()
            return {"status": "error", "message": str(e)}

    async def sync_h2h(self, team1_id: int, team2_id: int) -> Dict:
        """
        Sync head-to-head history between two teams.

        Args:
            team1_id: First team ID
            team2_id: Second team ID

        Returns:
            Sync statistics
        """
        try:
            logger.info(f"Syncing H2H for teams {team1_id} vs {team2_id}...")

            h2h_data = await api_football_client.get_h2h(team1_id, team2_id)

            if not h2h_data:
                logger.warning(f"No H2H data for teams {team1_id} vs {team2_id}")
                return {"status": "no_data"}

            synced_count = 0

            for match_entry in h2h_data:
                fixture_id = match_entry.get("match_id")
                if not fixture_id:
                    continue

                # Check if H2H entry exists
                h2h_match = self.db.query(H2HMatch).filter(
                    H2HMatch.fixture_id == fixture_id
                ).first()

                if not h2h_match:
                    h2h_match = H2HMatch(
                        fixture_id=fixture_id,
                        team1_id=team1_id,
                        team2_id=team2_id
                    )
                    self.db.add(h2h_match)

                # Update match data
                h2h_match.league_id = match_entry.get("league_id")
                h2h_match.season = match_entry.get("league_year")
                h2h_match.match_date = datetime.fromisoformat(
                    match_entry.get("match_date").replace("Z", "+00:00")
                ) if match_entry.get("match_date") else datetime.utcnow()
                h2h_match.home_team_id = match_entry.get("match_hometeam_id")
                h2h_match.away_team_id = match_entry.get("match_awayteam_id")
                h2h_match.home_score = match_entry.get("match_hometeam_score")
                h2h_match.away_score = match_entry.get("match_awayteam_score")
                h2h_match.status = match_entry.get("match_status")

                # Determine winner
                if h2h_match.home_score > h2h_match.away_score:
                    h2h_match.winner_id = h2h_match.home_team_id
                elif h2h_match.away_score > h2h_match.home_score:
                    h2h_match.winner_id = h2h_match.away_team_id
                else:
                    h2h_match.winner_id = None

                h2h_match.updated_at = datetime.utcnow()
                synced_count += 1

            self.db.commit()
            logger.info(f"Synced {synced_count} H2H matches")

            return {
                "status": "success",
                "matches_synced": synced_count
            }

        except Exception as e:
            logger.error(f"Error syncing H2H: {str(e)}")
            self.db.rollback()
            return {"status": "error", "message": str(e)}


async def run_full_sync(db: Session, tier: Optional[str] = None) -> Dict:
    """
    Run full synchronization for all leagues.

    Args:
        db: Database session
        tier: Optional tier filter

    Returns:
        Sync results dictionary
    """
    service = DataSyncService(db)
    result = await service.sync_all_leagues(tier_filter=tier)
    return result
