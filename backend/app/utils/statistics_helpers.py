"""
Helper functions for statistics endpoints to reduce code duplication.

This module contains reusable query builders and data extractors
that are shared across all statistics endpoints.
"""

from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, Query, joinedload

from app.models.fixture import Fixture, FixtureStat
from app.models.user import User
from app.core.config import settings
from app.core.constants import UPCOMING_FIXTURE_STATUSES
from app.utils.validators import validate_league_count


def validate_and_normalize_league_ids(
    league_id: Optional[int],
    league_ids: Optional[List[int]],
    user_tier: str
) -> List[int]:
    """
    Validate and normalize league IDs from both single and multiple inputs.

    Args:
        league_id: Single league ID (deprecated parameter)
        league_ids: List of league IDs
        user_tier: User's subscription tier

    Returns:
        List of validated league IDs

    Raises:
        HTTPException: If league count exceeds allowed limit
    """
    # Handle league filtering (support both single and multiple league IDs)
    requested_league_ids = []
    if league_ids:
        requested_league_ids = league_ids
    elif league_id:
        # Backward compatibility: convert single league_id to list
        requested_league_ids = [league_id]

    # Validate league count to prevent app crashes
    if requested_league_ids:
        validate_league_count(
            league_ids=requested_league_ids,
            user_tier=user_tier,
            max_regular=settings.MAX_LEAGUES_PER_SEARCH_REGULAR,
            max_admin=settings.MAX_LEAGUES_PER_SEARCH_ADMIN
        )

    return requested_league_ids


def build_upcoming_fixtures_query(
    db: Session,
    days_ahead: int,
    league_ids: List[int],
    season: Optional[str] = None
) -> Query:
    """
    Build a query for upcoming fixtures with common filters.

    Args:
        db: Database session
        days_ahead: Number of days to look ahead
        league_ids: List of league IDs to filter by
        season: Optional season filter

    Returns:
        SQLAlchemy query object
    """
    # Calculate date range
    now = datetime.utcnow()
    end_date = now + timedelta(days=days_ahead)

    # Build base query
    query = db.query(Fixture).filter(
        Fixture.match_date >= now,
        Fixture.match_date <= end_date,
        Fixture.status.in_(UPCOMING_FIXTURE_STATUSES)
    )

    # Apply league filter
    if league_ids:
        query = query.filter(Fixture.league_id.in_(league_ids))

    # Apply season filter
    if season:
        query = query.filter(Fixture.season == season)

    return query


def get_fixtures_with_stats(
    query: Query,
    limit: int,
    offset: int
) -> Tuple[int, List[Fixture]]:
    """
    Execute query and retrieve fixtures with all related data eager-loaded.

    Args:
        query: Base query to execute
        limit: Maximum number of results
        offset: Pagination offset

    Returns:
        Tuple of (total_count, fixtures_list)
    """
    # Get total count before pagination
    total = query.count()

    # Execute query with eager loading
    fixtures = query.options(
        joinedload(Fixture.league),
        joinedload(Fixture.home_team),
        joinedload(Fixture.away_team),
        joinedload(Fixture.stats)
    ).order_by(Fixture.match_date).limit(limit).offset(offset).all()

    return total, fixtures


def calculate_team_stat_average(
    fixture_stats: List[FixtureStat],
    team_id: int,
    stat_field: str,
    default_value: float
) -> float:
    """
    Calculate average value for a specific statistic from pre-loaded fixture stats.

    Args:
        fixture_stats: List of FixtureStat objects (from fixture.stats)
        team_id: Team ID to filter by
        stat_field: Field name to extract (e.g., 'corners', 'yellow_cards')
        default_value: Default value if no stats found

    Returns:
        Average value or default if no data
    """
    # Extract stat values for the team
    stat_values = [
        getattr(s, stat_field)
        for s in fixture_stats
        if s.team_id == team_id and getattr(s, stat_field) is not None
    ]

    # Calculate average or return default
    if stat_values:
        return sum(stat_values) / len(stat_values)
    else:
        return default_value


def extract_fixture_display_data(fixture: Fixture) -> dict:
    """
    Extract common display data from a fixture.

    Args:
        fixture: Fixture object with loaded relationships

    Returns:
        Dictionary with common fixture display fields
    """
    return {
        "fixture_id": fixture.id,
        "league_name": fixture.league.name if fixture.league else f"League {fixture.league_id}",
        "match_date": fixture.match_date,
        "home_team": fixture.home_team.name if fixture.home_team else f"Team {fixture.home_team_id}",
        "away_team": fixture.away_team.name if fixture.away_team else f"Team {fixture.away_team_id}",
        "status": fixture.status
    }
