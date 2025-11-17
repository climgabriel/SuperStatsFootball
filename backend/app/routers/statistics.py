from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.dependencies import get_db, get_current_active_user
from app.models.user import User
from app.models.fixture import Fixture, FixtureStat
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

router = APIRouter()


@router.get("/goals", response_model=GoalsListResponse)
async def get_goals_statistics(
    days_ahead: int = Query(7, ge=1, le=30, description="Number of days to look ahead"),
    league_id: Optional[int] = Query(None, description="Filter by league ID"),
    season: Optional[str] = Query(None, description="Filter by season"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
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
    # Calculate date range
    now = datetime.utcnow()
    end_date = now + timedelta(days=days_ahead)

    # Query fixtures
    query = db.query(Fixture).filter(
        Fixture.match_date >= now,
        Fixture.match_date <= end_date,
        Fixture.status.in_(["NS", "TBD"])
    )

    if league_id:
        query = query.filter(Fixture.league_id == league_id)
    if season:
        query = query.filter(Fixture.season == season)

    total = query.count()

    # Get fixtures with stats
    fixtures = query.options(
        joinedload(Fixture.league),
        joinedload(Fixture.home_team),
        joinedload(Fixture.away_team),
        joinedload(Fixture.stats)
    ).order_by(Fixture.match_date).limit(limit).offset(offset).all()

    # Transform to response format
    result_fixtures = []
    for fixture in fixtures:
        # Calculate goals statistics from historical data
        home_stats = db.query(FixtureStat).filter(
            FixtureStat.team_id == fixture.home_team_id
        ).all()

        away_stats = db.query(FixtureStat).filter(
            FixtureStat.team_id == fixture.away_team_id
        ).all()

        # Calculate averages (simplified - in production, use more sophisticated calculations)
        home_xg_avg = sum([s.expected_goals or 0 for s in home_stats]) / max(len(home_stats), 1) if home_stats else 1.5
        away_xg_avg = sum([s.expected_goals or 0 for s in away_stats]) / max(len(away_stats), 1) if away_stats else 1.2

        fixture_data = {
            "fixture_id": fixture.id,
            "league_name": fixture.league.name if fixture.league else f"League {fixture.league_id}",
            "match_date": fixture.match_date,
            "home_team": fixture.home_team.name if fixture.home_team else f"Team {fixture.home_team_id}",
            "away_team": fixture.away_team.name if fixture.away_team else f"Team {fixture.away_team_id}",
            "status": fixture.status,
            "goals_stats": {
                "over_under_2_5": {
                    "over": {"odds": "1.85", "probability": "54.2%"},
                    "under": {"odds": "1.95", "probability": "45.8%"},
                    "prediction": "Over 2.5"
                },
                "over_under_1_5": {
                    "over": {"odds": "1.25", "probability": "78.5%"},
                    "under": {"odds": "3.75", "probability": "21.5%"}
                },
                "over_under_3_5": {
                    "over": {"odds": "2.50", "probability": "38.2%"},
                    "under": {"odds": "1.50", "probability": "61.8%"}
                },
                "btts": {
                    "yes": {"odds": "1.65", "probability": "62.5%"},
                    "no": {"odds": "2.20", "probability": "37.5%"},
                    "prediction": "Yes"
                },
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
    days_ahead: int = Query(7, ge=1, le=30),
    league_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get corners statistics for upcoming fixtures.
    """
    now = datetime.utcnow()
    end_date = now + timedelta(days=days_ahead)

    query = db.query(Fixture).filter(
        Fixture.match_date >= now,
        Fixture.match_date <= end_date,
        Fixture.status.in_(["NS", "TBD"])
    )

    if league_id:
        query = query.filter(Fixture.league_id == league_id)

    total = query.count()

    fixtures = query.options(
        joinedload(Fixture.league),
        joinedload(Fixture.home_team),
        joinedload(Fixture.away_team),
        joinedload(Fixture.stats)
    ).order_by(Fixture.match_date).limit(limit).offset(offset).all()

    result_fixtures = []
    for fixture in fixtures:
        # Get corner stats from historical data
        home_stats = db.query(func.avg(FixtureStat.corners)).filter(
            FixtureStat.team_id == fixture.home_team_id
        ).scalar() or 6.0

        away_stats = db.query(func.avg(FixtureStat.corners)).filter(
            FixtureStat.team_id == fixture.away_team_id
        ).scalar() or 4.5

        fixture_data = {
            "fixture_id": fixture.id,
            "league_name": fixture.league.name if fixture.league else f"League {fixture.league_id}",
            "match_date": fixture.match_date,
            "home_team": fixture.home_team.name if fixture.home_team else f"Team {fixture.home_team_id}",
            "away_team": fixture.away_team.name if fixture.away_team else f"Team {fixture.away_team_id}",
            "status": fixture.status,
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
    days_ahead: int = Query(7, ge=1, le=30),
    league_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get yellow and red card statistics for upcoming fixtures.
    """
    now = datetime.utcnow()
    end_date = now + timedelta(days=days_ahead)

    query = db.query(Fixture).filter(
        Fixture.match_date >= now,
        Fixture.match_date <= end_date,
        Fixture.status.in_(["NS", "TBD"])
    )

    if league_id:
        query = query.filter(Fixture.league_id == league_id)

    total = query.count()

    fixtures = query.options(
        joinedload(Fixture.league),
        joinedload(Fixture.home_team),
        joinedload(Fixture.away_team)
    ).order_by(Fixture.match_date).limit(limit).offset(offset).all()

    result_fixtures = []
    for fixture in fixtures:
        # Get cards stats
        home_yellow_avg = db.query(func.avg(FixtureStat.yellow_cards)).filter(
            FixtureStat.team_id == fixture.home_team_id
        ).scalar() or 2.1

        away_yellow_avg = db.query(func.avg(FixtureStat.yellow_cards)).filter(
            FixtureStat.team_id == fixture.away_team_id
        ).scalar() or 1.9

        home_red_avg = db.query(func.avg(FixtureStat.red_cards)).filter(
            FixtureStat.team_id == fixture.home_team_id
        ).scalar() or 0.1

        away_red_avg = db.query(func.avg(FixtureStat.red_cards)).filter(
            FixtureStat.team_id == fixture.away_team_id
        ).scalar() or 0.1

        fixture_data = {
            "fixture_id": fixture.id,
            "league_name": fixture.league.name if fixture.league else f"League {fixture.league_id}",
            "match_date": fixture.match_date,
            "home_team": fixture.home_team.name if fixture.home_team else f"Team {fixture.home_team_id}",
            "away_team": fixture.away_team.name if fixture.away_team else f"Team {fixture.away_team_id}",
            "status": fixture.status,
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
    days_ahead: int = Query(7, ge=1, le=30),
    league_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get shots on target statistics for upcoming fixtures.
    """
    now = datetime.utcnow()
    end_date = now + timedelta(days=days_ahead)

    query = db.query(Fixture).filter(
        Fixture.match_date >= now,
        Fixture.match_date <= end_date,
        Fixture.status.in_(["NS", "TBD"])
    )

    if league_id:
        query = query.filter(Fixture.league_id == league_id)

    total = query.count()

    fixtures = query.options(
        joinedload(Fixture.league),
        joinedload(Fixture.home_team),
        joinedload(Fixture.away_team)
    ).order_by(Fixture.match_date).limit(limit).offset(offset).all()

    result_fixtures = []
    for fixture in fixtures:
        # Get shots stats
        home_shots_total = db.query(func.avg(FixtureStat.shots_total)).filter(
            FixtureStat.team_id == fixture.home_team_id
        ).scalar() or 12.5

        home_shots_on_goal = db.query(func.avg(FixtureStat.shots_on_goal)).filter(
            FixtureStat.team_id == fixture.home_team_id
        ).scalar() or 5.2

        away_shots_total = db.query(func.avg(FixtureStat.shots_total)).filter(
            FixtureStat.team_id == fixture.away_team_id
        ).scalar() or 9.8

        away_shots_on_goal = db.query(func.avg(FixtureStat.shots_on_goal)).filter(
            FixtureStat.team_id == fixture.away_team_id
        ).scalar() or 4.1

        fixture_data = {
            "fixture_id": fixture.id,
            "league_name": fixture.league.name if fixture.league else f"League {fixture.league_id}",
            "match_date": fixture.match_date,
            "home_team": fixture.home_team.name if fixture.home_team else f"Team {fixture.home_team_id}",
            "away_team": fixture.away_team.name if fixture.away_team else f"Team {fixture.away_team_id}",
            "status": fixture.status,
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
    days_ahead: int = Query(7, ge=1, le=30),
    league_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get fouls and faults statistics for upcoming fixtures.
    """
    now = datetime.utcnow()
    end_date = now + timedelta(days=days_ahead)

    query = db.query(Fixture).filter(
        Fixture.match_date >= now,
        Fixture.match_date <= end_date,
        Fixture.status.in_(["NS", "TBD"])
    )

    if league_id:
        query = query.filter(Fixture.league_id == league_id)

    total = query.count()

    fixtures = query.options(
        joinedload(Fixture.league),
        joinedload(Fixture.home_team),
        joinedload(Fixture.away_team)
    ).order_by(Fixture.match_date).limit(limit).offset(offset).all()

    result_fixtures = []
    for fixture in fixtures:
        # Get fouls stats
        home_fouls_avg = db.query(func.avg(FixtureStat.fouls)).filter(
            FixtureStat.team_id == fixture.home_team_id
        ).scalar() or 11.2

        away_fouls_avg = db.query(func.avg(FixtureStat.fouls)).filter(
            FixtureStat.team_id == fixture.away_team_id
        ).scalar() or 12.3

        fixture_data = {
            "fixture_id": fixture.id,
            "league_name": fixture.league.name if fixture.league else f"League {fixture.league_id}",
            "match_date": fixture.match_date,
            "home_team": fixture.home_team.name if fixture.home_team else f"Team {fixture.home_team_id}",
            "away_team": fixture.away_team.name if fixture.away_team else f"Team {fixture.away_team_id}",
            "status": fixture.status,
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
                    "home": f"{(home_fouls_avg / 4):.1f}",
                    "away": f"{(away_fouls_avg / 4):.1f}"
                }
            }
        }
        result_fixtures.append(fixture_data)

    return FoulsListResponse(total=total, fixtures=result_fixtures)


@router.get("/offsides", response_model=OffsListResponse)
async def get_offsides_statistics(
    days_ahead: int = Query(7, ge=1, le=30),
    league_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get offside statistics for upcoming fixtures.
    """
    now = datetime.utcnow()
    end_date = now + timedelta(days=days_ahead)

    query = db.query(Fixture).filter(
        Fixture.match_date >= now,
        Fixture.match_date <= end_date,
        Fixture.status.in_(["NS", "TBD"])
    )

    if league_id:
        query = query.filter(Fixture.league_id == league_id)

    total = query.count()

    fixtures = query.options(
        joinedload(Fixture.league),
        joinedload(Fixture.home_team),
        joinedload(Fixture.away_team)
    ).order_by(Fixture.match_date).limit(limit).offset(offset).all()

    result_fixtures = []
    for fixture in fixtures:
        # Get offsides stats
        home_offsides_avg = db.query(func.avg(FixtureStat.offsides)).filter(
            FixtureStat.team_id == fixture.home_team_id
        ).scalar() or 2.3

        away_offsides_avg = db.query(func.avg(FixtureStat.offsides)).filter(
            FixtureStat.team_id == fixture.away_team_id
        ).scalar() or 1.9

        # Get shots for tactical index calculation
        home_shots = db.query(func.avg(FixtureStat.shots_total)).filter(
            FixtureStat.team_id == fixture.home_team_id
        ).scalar() or 12.0

        away_shots = db.query(func.avg(FixtureStat.shots_total)).filter(
            FixtureStat.team_id == fixture.away_team_id
        ).scalar() or 10.0

        fixture_data = {
            "fixture_id": fixture.id,
            "league_name": fixture.league.name if fixture.league else f"League {fixture.league_id}",
            "match_date": fixture.match_date,
            "home_team": fixture.home_team.name if fixture.home_team else f"Team {fixture.home_team_id}",
            "away_team": fixture.away_team.name if fixture.away_team else f"Team {fixture.away_team_id}",
            "status": fixture.status,
            "offsides_stats": {
                "total_offsides": {
                    "over_3_5": {"odds": "1.95", "probability": "51.3%"},
                    "over_4_5": {"odds": "2.40", "probability": "41.7%"},
                    "predicted": f"{home_offsides_avg + away_offsides_avg:.1f}"
                },
                "home_offsides": {
                    "avg": f"{home_offsides_avg:.1f}",
                    "per_shot": f"{(home_offsides_avg / home_shots):.2f}",
                    "tactical_index": f"{(home_offsides_avg * 3):.1f}"
                },
                "away_offsides": {
                    "avg": f"{away_offsides_avg:.1f}",
                    "per_shot": f"{(away_offsides_avg / away_shots):.2f}",
                    "tactical_index": f"{(away_offsides_avg * 3):.1f}"
                },
                "attacking_style": {
                    "home": "High Line" if home_offsides_avg > 2.0 else "Balanced",
                    "away": "High Line" if away_offsides_avg > 2.0 else "Balanced"
                }
            }
        }
        result_fixtures.append(fixture_data)

    return OffsListResponse(total=total, fixtures=result_fixtures)
