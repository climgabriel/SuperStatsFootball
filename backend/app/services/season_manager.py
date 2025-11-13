"""
Season Management Service

Handles season rotation logic:
- Keeps current season + 4 previous seasons (5 total)
- Automatically removes oldest season when new season starts
- Manages season transitions
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime
from typing import List, Dict, Optional
import logging

from app.models.league import League
from app.models.fixture import Fixture, FixtureStat, FixtureScore
from app.models.prediction import Prediction, TeamRating
from app.core.leagues_config import SEASON_RETENTION

logger = logging.getLogger(__name__)


class SeasonManager:
    """Manages season data retention and rotation."""

    def __init__(self, db: Session):
        self.db = db
        self.max_seasons = SEASON_RETENTION["total_seasons"]  # 5 seasons total

    def get_current_season(self) -> int:
        """
        Determine current season based on current date.
        Football season typically runs from August to May.
        """
        now = datetime.now()
        year = now.year

        # If we're past July, it's the new season
        if now.month >= 8:
            return year
        else:
            # Still in previous season
            return year - 1

    def get_valid_seasons(self, current_season: Optional[int] = None) -> List[int]:
        """
        Get list of seasons that should be kept in database.
        Returns [current_season, current-1, current-2, current-3, current-4]
        """
        if current_season is None:
            current_season = self.get_current_season()

        return [current_season - i for i in range(self.max_seasons)]

    def get_seasons_to_delete(self, league_id: int) -> List[int]:
        """
        Get list of seasons that should be deleted for a league.
        """
        valid_seasons = self.get_valid_seasons()

        # Find all seasons in database for this league
        existing_seasons = self.db.query(Fixture.season).filter(
            Fixture.league_id == league_id
        ).distinct().all()

        existing_seasons = [s[0] for s in existing_seasons]

        # Seasons to delete are those not in valid list
        to_delete = [s for s in existing_seasons if s not in valid_seasons]

        return to_delete

    def cleanup_old_seasons(self, league_id: Optional[int] = None) -> Dict:
        """
        Remove data from seasons older than retention policy.

        Args:
            league_id: Specific league to clean, or None for all leagues

        Returns:
            Dictionary with cleanup statistics
        """
        valid_seasons = self.get_valid_seasons()
        stats = {
            "fixtures_deleted": 0,
            "stats_deleted": 0,
            "scores_deleted": 0,
            "predictions_deleted": 0,
            "ratings_deleted": 0,
            "leagues_cleaned": []
        }

        try:
            # Build base query
            if league_id:
                leagues_to_clean = [league_id]
            else:
                # Get all leagues
                leagues_to_clean = [l.id for l in self.db.query(League.id).all()]

            for lid in leagues_to_clean:
                # Get seasons to delete for this league
                seasons_to_delete = self.get_seasons_to_delete(lid)

                if not seasons_to_delete:
                    continue

                logger.info(f"Cleaning league {lid}, removing seasons: {seasons_to_delete}")

                # Delete fixtures and related data
                fixtures_to_delete = self.db.query(Fixture).filter(
                    and_(
                        Fixture.league_id == lid,
                        Fixture.season.in_(seasons_to_delete)
                    )
                ).all()

                fixture_ids = [f.id for f in fixtures_to_delete]

                if fixture_ids:
                    # Delete fixture stats
                    deleted_stats = self.db.query(FixtureStat).filter(
                        FixtureStat.fixture_id.in_(fixture_ids)
                    ).delete(synchronize_session=False)
                    stats["stats_deleted"] += deleted_stats

                    # Delete fixture scores
                    deleted_scores = self.db.query(FixtureScore).filter(
                        FixtureScore.fixture_id.in_(fixture_ids)
                    ).delete(synchronize_session=False)
                    stats["scores_deleted"] += deleted_scores

                    # Delete predictions
                    deleted_predictions = self.db.query(Prediction).filter(
                        Prediction.fixture_id.in_(fixture_ids)
                    ).delete(synchronize_session=False)
                    stats["predictions_deleted"] += deleted_predictions

                    # Delete fixtures
                    deleted_fixtures = self.db.query(Fixture).filter(
                        and_(
                            Fixture.league_id == lid,
                            Fixture.season.in_(seasons_to_delete)
                        )
                    ).delete(synchronize_session=False)
                    stats["fixtures_deleted"] += deleted_fixtures

                # Delete team ratings for old seasons
                deleted_ratings = self.db.query(TeamRating).filter(
                    and_(
                        TeamRating.league_id == lid,
                        TeamRating.season.in_(seasons_to_delete)
                    )
                ).delete(synchronize_session=False)
                stats["ratings_deleted"] += deleted_ratings

                stats["leagues_cleaned"].append(lid)

            self.db.commit()
            logger.info(f"Season cleanup completed: {stats}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during season cleanup: {str(e)}")
            raise

        return stats

    def check_season_transition(self) -> Dict:
        """
        Check if we've transitioned to a new season and trigger cleanup if needed.

        Returns:
            Dictionary with transition info and cleanup stats if performed
        """
        current_season = self.get_current_season()
        valid_seasons = self.get_valid_seasons(current_season)

        # Check if we have data from seasons that should be deleted
        old_fixtures = self.db.query(Fixture).filter(
            ~Fixture.season.in_(valid_seasons)
        ).count()

        result = {
            "current_season": current_season,
            "valid_seasons": valid_seasons,
            "old_fixtures_found": old_fixtures,
            "cleanup_performed": False,
            "cleanup_stats": None
        }

        if old_fixtures > 0:
            logger.info(f"Found {old_fixtures} fixtures from old seasons. Starting cleanup...")
            cleanup_stats = self.cleanup_old_seasons()
            result["cleanup_performed"] = True
            result["cleanup_stats"] = cleanup_stats

        return result

    def get_season_statistics(self) -> Dict:
        """
        Get statistics about seasons in database.
        """
        current_season = self.get_current_season()
        valid_seasons = self.get_valid_seasons(current_season)

        # Count fixtures per season
        season_counts = self.db.query(
            Fixture.season,
            func.count(Fixture.id).label('count')
        ).group_by(Fixture.season).all()

        season_data = {
            "current_season": current_season,
            "valid_seasons": valid_seasons,
            "seasons_in_db": [{"season": s.season, "fixtures": s.count} for s in season_counts],
            "total_fixtures": sum(s.count for s in season_counts)
        }

        return season_data

    def should_sync_season(self, season: int) -> bool:
        """
        Check if a season should be synced based on retention policy.
        """
        valid_seasons = self.get_valid_seasons()
        return season in valid_seasons
