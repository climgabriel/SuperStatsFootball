from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.dependencies import get_db, get_current_active_user
from app.models.fixture import Fixture, FixtureScore, FixtureStat
from app.models.user import User
from app.schemas.fixture import FixtureResponse, FixtureDetailResponse

router = APIRouter()


@router.get("/", response_model=List[FixtureResponse])
async def get_fixtures(
    league_id: Optional[int] = Query(None),
    season: Optional[int] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    team_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    next_round_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get list of fixtures with optional filters.

    - **league_id**: Filter by league
    - **season**: Filter by season
    - **date_from**: Filter by date (YYYY-MM-DD)
    - **date_to**: Filter by date (YYYY-MM-DD)
    - **team_id**: Filter by team (home or away)
    - **status**: Filter by status (NS, LIVE, FT, etc.)
    - **next_round_only**: Show only next round fixtures
    """
    query = db.query(Fixture)

    if league_id:
        query = query.filter(Fixture.league_id == league_id)

    if season:
        query = query.filter(Fixture.season == season)

    if date_from:
        query = query.filter(Fixture.match_date >= datetime.fromisoformat(date_from))

    if date_to:
        query = query.filter(Fixture.match_date <= datetime.fromisoformat(date_to))

    if team_id:
        query = query.filter(
            (Fixture.home_team_id == team_id) | (Fixture.away_team_id == team_id)
        )

    if status:
        query = query.filter(Fixture.status == status)

    if next_round_only and league_id:
        # Get the next upcoming round
        next_fixture = query.filter(
            Fixture.status == "NS",
            Fixture.match_date >= datetime.utcnow()
        ).order_by(Fixture.match_date).first()

        if next_fixture:
            query = query.filter(Fixture.round == next_fixture.round)

    query = query.order_by(Fixture.match_date.desc())
    fixtures = query.offset(offset).limit(limit).all()

    return fixtures


@router.get("/upcoming", response_model=List[FixtureResponse])
async def get_upcoming_fixtures(
    league_id: Optional[int] = Query(None),
    next_round_only: bool = Query(True),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get upcoming fixtures.

    By default, shows only next round fixtures.
    """
    query = db.query(Fixture).filter(
        Fixture.status == "NS",
        Fixture.match_date >= datetime.utcnow()
    )

    if league_id:
        query = query.filter(Fixture.league_id == league_id)

        if next_round_only:
            next_fixture = query.order_by(Fixture.match_date).first()
            if next_fixture:
                query = query.filter(Fixture.round == next_fixture.round)

    query = query.order_by(Fixture.match_date)
    fixtures = query.limit(limit).all()

    return fixtures


@router.get("/{fixture_id}", response_model=FixtureDetailResponse)
async def get_fixture(
    fixture_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific fixture.

    Includes score and statistics if available.
    """
    fixture = db.query(Fixture).filter(Fixture.id == fixture_id).first()

    if not fixture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fixture {fixture_id} not found"
        )

    # Get score
    score = db.query(FixtureScore).filter(FixtureScore.fixture_id == fixture_id).first()

    # Get stats
    stats = db.query(FixtureStat).filter(FixtureStat.fixture_id == fixture_id).all()
    home_stats = next((s for s in stats if s.team_id == fixture.home_team_id), None)
    away_stats = next((s for s in stats if s.team_id == fixture.away_team_id), None)

    response = FixtureDetailResponse.model_validate(fixture)
    if score:
        response.score = score
    if home_stats:
        response.home_stats = home_stats
    if away_stats:
        response.away_stats = away_stats

    return response


@router.get("/{fixture_id}/stats")
async def get_fixture_stats(
    fixture_id: int,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific fixture.
    """
    fixture = db.query(Fixture).filter(Fixture.id == fixture_id).first()

    if not fixture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fixture {fixture_id} not found"
        )

    stats = db.query(FixtureStat).filter(FixtureStat.fixture_id == fixture_id).all()

    home_stats = next((s for s in stats if s.team_id == fixture.home_team_id), None)
    away_stats = next((s for s in stats if s.team_id == fixture.away_team_id), None)

    return {
        "fixture_id": fixture_id,
        "home_stats": home_stats,
        "away_stats": away_stats
    }
