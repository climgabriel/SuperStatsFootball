from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.dependencies import get_db, get_current_active_user
from app.core.config import settings
from app.core.constants import (
    DEFAULT_DAYS_AHEAD, MIN_DAYS_AHEAD, MAX_DAYS_AHEAD,
    DEFAULT_LIMIT, MAX_LIMIT, DEFAULT_OFFSET,
    DEFAULT_HOME_XG, DEFAULT_AWAY_XG,
    DEFAULT_HOME_CORNERS, DEFAULT_AWAY_CORNERS,
    DEFAULT_HOME_YELLOW_CARDS, DEFAULT_AWAY_YELLOW_CARDS,
    DEFAULT_HOME_RED_CARDS, DEFAULT_AWAY_RED_CARDS,
    DEFAULT_HOME_TOTAL_SHOTS, DEFAULT_AWAY_TOTAL_SHOTS,
    DEFAULT_HOME_SHOTS_ON_GOAL, DEFAULT_AWAY_SHOTS_ON_GOAL,
    DEFAULT_HOME_FOULS, DEFAULT_AWAY_FOULS,
    DEFAULT_HOME_OFFSIDES, DEFAULT_AWAY_OFFSIDES,
    DEFAULT_HOME_SHOTS_FOR_TACTICAL, DEFAULT_AWAY_SHOTS_FOR_TACTICAL,
    OFFSIDES_HIGH_LINE_THRESHOLD,
    UPCOMING_FIXTURE_STATUSES,
    MIN_SAMPLE_SIZE,
    DISCIPLINE_INDEX_DIVISOR,
    TACTICAL_INDEX_MULTIPLIER,
    SAMPLE_ODDS
)
from app.models.user import User
from app.models.fixture import Fixture, FixtureStats
from app.models.league import League
from app.models.team import Team
from app.schemas.statistics import (
    GoalsListResponse,
    CornersListResponse,
    CardsListResponse,
    ShotsListResponse,
    FoulsListResponse,
    OffsListResponse
)
from app.utils.validators import validate_league_count
from app.utils.statistics_helpers import (
    validate_and_normalize_league_ids,
    build_upcoming_fixtures_query,
    get_fixtures_with_stats,
    calculate_team_stat_average,
    extract_fixture_display_data
)

router = APIRouter()


@router.get("/goals", response_model=GoalsListResponse)
async def get_goals_statistics(
    days_ahead: int = Query(DEFAULT_DAYS_AHEAD, ge=MIN_DAYS_AHEAD, le=MAX_DAYS_AHEAD, description="Number of days to look ahead"),
    league_id: Optional[int] = Query(None, description="Filter by single league ID (deprecated, use league_ids)"),
    league_ids: Optional[List[int]] = Query(None, description="Filter by multiple league IDs (max 5 for regular users, 10 for admin)"),
    season: Optional[str] = Query(None, description="Filter by season"),
    limit: int = Query(DEFAULT_LIMIT, ge=MIN_SAMPLE_SIZE, le=MAX_LIMIT),
    offset: int = Query(DEFAULT_OFFSET, ge=DEFAULT_OFFSET),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get goals statistics for upcoming fixtures.

    Includes:
    - Over/Under 2.5, 1.5, 3.5 goals
    - Both Teams To Score (BTTS)
    - Expected Goals (xG)
    """
    # Validate and normalize league IDs
    requested_league_ids = validate_and_normalize_league_ids(league_id, league_ids, current_user.tier)

    # Build query for upcoming fixtures
    query = build_upcoming_fixtures_query(db, days_ahead, requested_league_ids, season)

    # Get fixtures with all related data
    total, fixtures = get_fixtures_with_stats(query, limit, offset)

    # Transform to response format
    result_fixtures = []
    for fixture in fixtures:
        # Calculate expected goals from pre-loaded stats
        home_xg_avg = calculate_team_stat_average(fixture.stats, fixture.home_team_id, 'expected_goals', DEFAULT_HOME_XG)
        away_xg_avg = calculate_team_stat_average(fixture.stats, fixture.away_team_id, 'expected_goals', DEFAULT_AWAY_XG)

        # Build fixture data with common display fields
        fixture_data = {
            **extract_fixture_display_data(fixture),
            "goals_stats": {
                "over_under_2_5": {**SAMPLE_ODDS["over_under_2_5"], "prediction": "Over 2.5"},
                "over_under_1_5": SAMPLE_ODDS["over_under_1_5"],
                "over_under_3_5": SAMPLE_ODDS["over_under_3_5"],
                "btts": {**SAMPLE_ODDS["btts"], "prediction": "Yes"},
                "total_goals": {
                    "predicted": f"{home_xg_avg + away_xg_avg:.1f}",
                    "home_expected": f"{home_xg_avg:.1f}",
                    "away_expected": f"{away_xg_avg:.1f}"
                }
            }
        }
        result_fixtures.append(fixture_data)

    return GoalsListResponse(total=total, fixtures=result_fixtures)


@router.get("/corners", response_model=CornersListResponse)
async def get_corners_statistics(
    days_ahead: int = Query(DEFAULT_DAYS_AHEAD, ge=MIN_DAYS_AHEAD, le=MAX_DAYS_AHEAD),
    league_id: Optional[int] = Query(None, description="Filter by single league ID (deprecated, use league_ids)"),
    league_ids: Optional[List[int]] = Query(None, description="Filter by multiple league IDs (max 5 for regular users, 10 for admin)"),
    limit: int = Query(DEFAULT_LIMIT, ge=MIN_SAMPLE_SIZE, le=MAX_LIMIT),
    offset: int = Query(DEFAULT_OFFSET, ge=DEFAULT_OFFSET),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get corners statistics for upcoming fixtures.
    """
    # Validate and normalize league IDs
    requested_league_ids = validate_and_normalize_league_ids(league_id, league_ids, current_user.tier)

    # Build query and get fixtures
    query = build_upcoming_fixtures_query(db, days_ahead, requested_league_ids)
    total, fixtures = get_fixtures_with_stats(query, limit, offset)

    result_fixtures = []
    for fixture in fixtures:
        # Calculate corner statistics from pre-loaded stats
        home_stats = calculate_team_stat_average(fixture.stats, fixture.home_team_id, 'corners', DEFAULT_HOME_CORNERS)
        away_stats = calculate_team_stat_average(fixture.stats, fixture.away_team_id, 'corners', DEFAULT_AWAY_CORNERS)

        fixture_data = {
            **extract_fixture_display_data(fixture),
            "corners_stats": {
                "total_corners": {
                    "over_9_5": {"odds": "1.90", "probability": "52.6%"},
                    "over_10_5": {"odds": "2.10", "probability": "47.6%"},
                    "over_11_5": {"odds": "2.50", "probability": "40.0%"},
                    "predicted": f"{home_stats + away_stats:.1f}"
                },
                "home_corners": {
                    "avg": f"{home_stats:.1f}",
                    "over_5_5": {"odds": "1.75", "probability": "57.1%"}
                },
                "away_corners": {
                    "avg": f"{away_stats:.1f}",
                    "over_4_5": {"odds": "2.00", "probability": "50.0%"}
                },
                "first_corner": {"home": "1.80", "away": "2.00"},
                "last_corner": {"home": "1.85", "away": "1.95"}
            }
        }
        result_fixtures.append(fixture_data)

    return CornersListResponse(total=total, fixtures=result_fixtures)


@router.get("/cards", response_model=CardsListResponse)
async def get_cards_statistics(
    days_ahead: int = Query(DEFAULT_DAYS_AHEAD, ge=MIN_DAYS_AHEAD, le=MAX_DAYS_AHEAD),
    league_id: Optional[int] = Query(None, description="Filter by single league ID (deprecated, use league_ids)"),
    league_ids: Optional[List[int]] = Query(None, description="Filter by multiple league IDs (max 5 for regular users, 10 for admin)"),
    limit: int = Query(DEFAULT_LIMIT, ge=MIN_SAMPLE_SIZE, le=MAX_LIMIT),
    offset: int = Query(DEFAULT_OFFSET, ge=DEFAULT_OFFSET),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get yellow and red card statistics for upcoming fixtures.
    """
    # Validate and normalize league IDs
    requested_league_ids = validate_and_normalize_league_ids(league_id, league_ids, current_user.tier)

    # Build query and get fixtures
    query = build_upcoming_fixtures_query(db, days_ahead, requested_league_ids)
    total, fixtures = get_fixtures_with_stats(query, limit, offset)

    result_fixtures = []
    for fixture in fixtures:
        # Calculate card statistics from pre-loaded stats
        home_yellow_avg = calculate_team_stat_average(fixture.stats, fixture.home_team_id, 'yellow_cards', DEFAULT_HOME_YELLOW_CARDS)
        away_yellow_avg = calculate_team_stat_average(fixture.stats, fixture.away_team_id, 'yellow_cards', DEFAULT_AWAY_YELLOW_CARDS)
        home_red_avg = calculate_team_stat_average(fixture.stats, fixture.home_team_id, 'red_cards', DEFAULT_HOME_RED_CARDS)
        away_red_avg = calculate_team_stat_average(fixture.stats, fixture.away_team_id, 'red_cards', DEFAULT_AWAY_RED_CARDS)

        fixture_data = {
            **extract_fixture_display_data(fixture),
            "cards_stats": {
                "total_cards": {
                    "over_3_5": {"odds": "1.90", "probability": "52.6%"},
                    "over_4_5": {"odds": "2.30", "probability": "43.5%"},
                    "predicted": f"{home_yellow_avg + away_yellow_avg + home_red_avg + away_red_avg:.1f}"
                },
                "home_cards": {
                    "yellow": f"{home_yellow_avg:.1f}",
                    "red": f"{home_red_avg:.1f}",
                    "total": f"{home_yellow_avg + home_red_avg:.1f}"
                },
                "away_cards": {
                    "yellow": f"{away_yellow_avg:.1f}",
                    "red": f"{away_red_avg:.1f}",
                    "total": f"{away_yellow_avg + away_red_avg:.1f}"
                },
                "bookings": {
                    "home_booking": {"yes": "1.40", "no": "2.80"},
                    "away_booking": {"yes": "1.45", "no": "2.65"}
                }
            }
        }
        result_fixtures.append(fixture_data)

    return CardsListResponse(total=total, fixtures=result_fixtures)


@router.get("/shots", response_model=ShotsListResponse)
async def get_shots_statistics(
    days_ahead: int = Query(DEFAULT_DAYS_AHEAD, ge=MIN_DAYS_AHEAD, le=MAX_DAYS_AHEAD),
    league_id: Optional[int] = Query(None, description="Filter by single league ID (deprecated, use league_ids)"),
    league_ids: Optional[List[int]] = Query(None, description="Filter by multiple league IDs (max 5 for regular users, 10 for admin)"),
    limit: int = Query(DEFAULT_LIMIT, ge=MIN_SAMPLE_SIZE, le=MAX_LIMIT),
    offset: int = Query(DEFAULT_OFFSET, ge=DEFAULT_OFFSET),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get shots on target statistics for upcoming fixtures.
    """
    # Validate and normalize league IDs
    requested_league_ids = validate_and_normalize_league_ids(league_id, league_ids, current_user.tier)

    # Build query and get fixtures
    query = build_upcoming_fixtures_query(db, days_ahead, requested_league_ids)
    total, fixtures = get_fixtures_with_stats(query, limit, offset)

    result_fixtures = []
    for fixture in fixtures:
        # Calculate shot statistics from pre-loaded stats
        home_shots_total = calculate_team_stat_average(fixture.stats, fixture.home_team_id, 'total_shots', DEFAULT_HOME_TOTAL_SHOTS)
        home_shots_on_goal = calculate_team_stat_average(fixture.stats, fixture.home_team_id, 'shots_on_goal', DEFAULT_HOME_SHOTS_ON_GOAL)
        away_shots_total = calculate_team_stat_average(fixture.stats, fixture.away_team_id, 'total_shots', DEFAULT_AWAY_TOTAL_SHOTS)
        away_shots_on_goal = calculate_team_stat_average(fixture.stats, fixture.away_team_id, 'shots_on_goal', DEFAULT_AWAY_SHOTS_ON_GOAL)

        fixture_data = {
            **extract_fixture_display_data(fixture),
            "shots_stats": {
                "total_shots": {
                    "over_20_5": {"odds": "1.85", "probability": "54.1%"},
                    "over_22_5": {"odds": "2.10", "probability": "47.6%"},
                    "predicted": f"{home_shots_total + away_shots_total:.1f}"
                },
                "home_shots": {
                    "total_avg": f"{home_shots_total:.1f}",
                    "on_target_avg": f"{home_shots_on_goal:.1f}",
                    "accuracy": f"{(home_shots_on_goal / home_shots_total * 100):.1f}%",
                    "over_4_5_on_target": "1.75"
                },
                "away_shots": {
                    "total_avg": f"{away_shots_total:.1f}",
                    "on_target_avg": f"{away_shots_on_goal:.1f}",
                    "accuracy": f"{(away_shots_on_goal / away_shots_total * 100):.1f}%",
                    "over_3_5_on_target": "1.90"
                }
            }
        }
        result_fixtures.append(fixture_data)

    return ShotsListResponse(total=total, fixtures=result_fixtures)


@router.get("/fouls", response_model=FoulsListResponse)
async def get_fouls_statistics(
    days_ahead: int = Query(DEFAULT_DAYS_AHEAD, ge=MIN_DAYS_AHEAD, le=MAX_DAYS_AHEAD),
    league_id: Optional[int] = Query(None, description="Filter by single league ID (deprecated, use league_ids)"),
    league_ids: Optional[List[int]] = Query(None, description="Filter by multiple league IDs (max 5 for regular users, 10 for admin)"),
    limit: int = Query(DEFAULT_LIMIT, ge=MIN_SAMPLE_SIZE, le=MAX_LIMIT),
    offset: int = Query(DEFAULT_OFFSET, ge=DEFAULT_OFFSET),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get fouls and faults statistics for upcoming fixtures.
    """
    # Validate and normalize league IDs
    requested_league_ids = validate_and_normalize_league_ids(league_id, league_ids, current_user.tier)

    # Build query and get fixtures
    query = build_upcoming_fixtures_query(db, days_ahead, requested_league_ids)
    total, fixtures = get_fixtures_with_stats(query, limit, offset)

    result_fixtures = []
    for fixture in fixtures:
        # Calculate foul statistics from pre-loaded stats
        home_fouls_avg = calculate_team_stat_average(fixture.stats, fixture.home_team_id, 'fouls', DEFAULT_HOME_FOULS)
        away_fouls_avg = calculate_team_stat_average(fixture.stats, fixture.away_team_id, 'fouls', DEFAULT_AWAY_FOULS)

        fixture_data = {
            **extract_fixture_display_data(fixture),
            "fouls_stats": {
                "total_fouls": {
                    "over_22_5": {"odds": "1.90", "probability": "52.6%"},
                    "over_24_5": {"odds": "2.20", "probability": "45.5%"},
                    "predicted": f"{home_fouls_avg + away_fouls_avg:.1f}"
                },
                "home_fouls": {
                    "committed_avg": f"{home_fouls_avg:.1f}",
                    "suffered_avg": f"{away_fouls_avg:.1f}",
                    "diff": f"{home_fouls_avg - away_fouls_avg:+.1f}"
                },
                "away_fouls": {
                    "committed_avg": f"{away_fouls_avg:.1f}",
                    "suffered_avg": f"{home_fouls_avg:.1f}",
                    "diff": f"{away_fouls_avg - home_fouls_avg:+.1f}"
                },
                "discipline_index": {
                    "home": f"{(home_fouls_avg / DISCIPLINE_INDEX_DIVISOR):.1f}",
                    "away": f"{(away_fouls_avg / DISCIPLINE_INDEX_DIVISOR):.1f}"
                }
            }
        }
        result_fixtures.append(fixture_data)

    return FoulsListResponse(total=total, fixtures=result_fixtures)


@router.get("/offsides", response_model=OffsListResponse)
async def get_offsides_statistics(
    days_ahead: int = Query(DEFAULT_DAYS_AHEAD, ge=MIN_DAYS_AHEAD, le=MAX_DAYS_AHEAD),
    league_id: Optional[int] = Query(None, description="Filter by single league ID (deprecated, use league_ids)"),
    league_ids: Optional[List[int]] = Query(None, description="Filter by multiple league IDs (max 5 for regular users, 10 for admin)"),
    limit: int = Query(DEFAULT_LIMIT, ge=MIN_SAMPLE_SIZE, le=MAX_LIMIT),
    offset: int = Query(DEFAULT_OFFSET, ge=DEFAULT_OFFSET),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get offside statistics for upcoming fixtures.
    """
    # Validate and normalize league IDs
    requested_league_ids = validate_and_normalize_league_ids(league_id, league_ids, current_user.tier)

    # Build query and get fixtures
    query = build_upcoming_fixtures_query(db, days_ahead, requested_league_ids)
    total, fixtures = get_fixtures_with_stats(query, limit, offset)

    result_fixtures = []
    for fixture in fixtures:
        # Calculate offside and shot statistics from pre-loaded stats
        home_offsides_avg = calculate_team_stat_average(fixture.stats, fixture.home_team_id, 'offsides', DEFAULT_HOME_OFFSIDES)
        away_offsides_avg = calculate_team_stat_average(fixture.stats, fixture.away_team_id, 'offsides', DEFAULT_AWAY_OFFSIDES)

        # Get shots for tactical index calculation
        home_shots = calculate_team_stat_average(fixture.stats, fixture.home_team_id, 'total_shots', DEFAULT_HOME_SHOTS_FOR_TACTICAL)
        away_shots = calculate_team_stat_average(fixture.stats, fixture.away_team_id, 'total_shots', DEFAULT_AWAY_SHOTS_FOR_TACTICAL)

        fixture_data = {
            **extract_fixture_display_data(fixture),
            "offsides_stats": {
                "total_offsides": {
                    "over_3_5": {"odds": "1.95", "probability": "51.3%"},
                    "over_4_5": {"odds": "2.40", "probability": "41.7%"},
                    "predicted": f"{home_offsides_avg + away_offsides_avg:.1f}"
                },
                "home_offsides": {
                    "avg": f"{home_offsides_avg:.1f}",
                    "per_shot": f"{(home_offsides_avg / home_shots):.2f}",
                    "tactical_index": f"{(home_offsides_avg * TACTICAL_INDEX_MULTIPLIER):.1f}"
                },
                "away_offsides": {
                    "avg": f"{away_offsides_avg:.1f}",
                    "per_shot": f"{(away_offsides_avg / away_shots):.2f}",
                    "tactical_index": f"{(away_offsides_avg * TACTICAL_INDEX_MULTIPLIER):.1f}"
                },
                "attacking_style": {
                    "home": "High Line" if home_offsides_avg > OFFSIDES_HIGH_LINE_THRESHOLD else "Balanced",
                    "away": "High Line" if away_offsides_avg > OFFSIDES_HIGH_LINE_THRESHOLD else "Balanced"
                }
            }
        }
        result_fixtures.append(fixture_data)

    return OffsListResponse(total=total, fixtures=result_fixtures)
