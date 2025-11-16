from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.dependencies import get_db
from app.models.fixture import Fixture
from app.models.odds import FixtureOdds
from app.models.league import League
from app.models.team import Team
from app.schemas.odds import OddsResponse, FixtureWithOdds, OddsListResponse, Odds1X2, OddsHalfTime, OddsOverUnder

router = APIRouter()


@router.get("/fixture/{fixture_id}", response_model=OddsResponse)
async def get_fixture_odds(
    fixture_id: int,
    is_live: bool = Query(False, description="Get live odds instead of pre-match"),
    db: Session = Depends(get_db)
):
    """
    Get Superbet odds for a specific fixture.

    - **fixture_id**: Fixture ID
    - **is_live**: Set to true for live odds, false for pre-match odds
    """
    # Query for odds filtering by bookmaker (Superbet) and live status
    odds = db.query(FixtureOdds).filter(
        FixtureOdds.fixture_id == fixture_id,
        FixtureOdds.bookmaker_name == "Superbet",
        FixtureOdds.is_live == is_live
    ).order_by(FixtureOdds.fetched_at.desc()).first()

    if not odds:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No {'live' if is_live else 'pre-match'} odds found for fixture {fixture_id}"
        )

    return odds


@router.get("/upcoming", response_model=OddsListResponse)
async def get_upcoming_odds(
    days_ahead: int = Query(7, ge=1, le=30, description="Number of days to look ahead"),
    league_id: Optional[int] = Query(None, description="Filter by league ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get Superbet odds for upcoming fixtures with predictions.

    - **days_ahead**: Number of days to look ahead (default: 7)
    - **league_id**: Optional league filter
    - **limit**: Max results per page
    - **offset**: Pagination offset
    """
    # Calculate date range
    now = datetime.utcnow()
    end_date = now + timedelta(days=days_ahead)

    # Query fixtures with odds
    query = db.query(Fixture).join(
        FixtureOdds,
        (Fixture.id == FixtureOdds.fixture_id) & (FixtureOdds.bookmaker_name == "Superbet") & (FixtureOdds.is_live == False)
    ).filter(
        Fixture.match_date >= now,
        Fixture.match_date <= end_date,
        Fixture.status.in_(["NS", "TBD"])  # Not started fixtures
    )

    if league_id:
        query = query.filter(Fixture.league_id == league_id)

    # Get total count
    total = query.count()

    # Get fixtures with eager loading (including leagues and teams)
    fixtures = query.options(
        joinedload(Fixture.odds),
        joinedload(Fixture.league),
        joinedload(Fixture.home_team),
        joinedload(Fixture.away_team)
    ).order_by(Fixture.match_date).limit(limit).offset(offset).all()

    # Transform to response format
    result_fixtures = []
    for fixture in fixtures:
        # Get leagues and teams with proper names
        odds_obj = next((o for o in fixture.odds if o.bookmaker_name == "Superbet" and not o.is_live), None)

        if not odds_obj:
            continue

        fixture_with_odds = FixtureWithOdds(
            fixture_id=fixture.id,
            league_name=fixture.league.name if fixture.league else f"League {fixture.league_id}",
            match_date=fixture.match_date,
            home_team=fixture.home_team.name if fixture.home_team else f"Team {fixture.home_team_id}",
            away_team=fixture.away_team.name if fixture.away_team else f"Team {fixture.away_team_id}",
            status=fixture.status,
            bookmaker="Superbet",
            odds_1x2=Odds1X2(
                home=odds_obj.home_win_odds,
                draw=odds_obj.draw_odds,
                away=odds_obj.away_win_odds
            ),
            odds_halftime=OddsHalfTime(
                home=odds_obj.ht_home_win_odds,
                draw=odds_obj.ht_draw_odds,
                away=odds_obj.ht_away_win_odds
            ),
            odds_fulltime=Odds1X2(
                home=odds_obj.ft_home_win_odds,
                draw=odds_obj.ft_draw_odds,
                away=odds_obj.ft_away_win_odds
            ),
            odds_over_under_2_5=OddsOverUnder(
                over=odds_obj.over_2_5_odds,
                under=odds_obj.under_2_5_odds
            ),
            is_live=False,
            fetched_at=odds_obj.fetched_at
        )
        result_fixtures.append(fixture_with_odds)

    return OddsListResponse(total=total, fixtures=result_fixtures)


@router.get("/live", response_model=OddsListResponse)
async def get_live_odds(
    league_id: Optional[int] = Query(None, description="Filter by league ID"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get Superbet live odds for ongoing matches.

    - **league_id**: Optional league filter
    - **limit**: Max results per page
    - **offset**: Pagination offset
    """
    # Query live fixtures with odds
    query = db.query(Fixture).join(
        FixtureOdds,
        (Fixture.id == FixtureOdds.fixture_id) & (FixtureOdds.bookmaker_name == "Superbet") & (FixtureOdds.is_live == True)
    ).filter(
        Fixture.status.in_(["1H", "2H", "HT", "ET", "P", "LIVE"])  # Live match statuses
    )

    if league_id:
        query = query.filter(Fixture.league_id == league_id)

    # Get total count
    total = query.count()

    # Get fixtures with eager loading (including leagues and teams)
    fixtures = query.options(
        joinedload(Fixture.odds),
        joinedload(Fixture.league),
        joinedload(Fixture.home_team),
        joinedload(Fixture.away_team)
    ).order_by(Fixture.elapsed_time.desc()).limit(limit).offset(offset).all()

    # Transform to response format
    result_fixtures = []
    for fixture in fixtures:
        odds_obj = next((o for o in fixture.odds if o.bookmaker_name == "Superbet" and o.is_live), None)

        if not odds_obj:
            continue

        fixture_with_odds = FixtureWithOdds(
            fixture_id=fixture.id,
            league_name=fixture.league.name if fixture.league else f"League {fixture.league_id}",
            match_date=fixture.match_date,
            home_team=fixture.home_team.name if fixture.home_team else f"Team {fixture.home_team_id}",
            away_team=fixture.away_team.name if fixture.away_team else f"Team {fixture.away_team_id}",
            status=fixture.status,
            bookmaker="Superbet",
            odds_1x2=Odds1X2(
                home=odds_obj.home_win_odds,
                draw=odds_obj.draw_odds,
                away=odds_obj.away_win_odds
            ),
            odds_halftime=OddsHalfTime(
                home=odds_obj.ht_home_win_odds,
                draw=odds_obj.ht_draw_odds,
                away=odds_obj.ht_away_win_odds
            ),
            odds_fulltime=Odds1X2(
                home=odds_obj.ft_home_win_odds,
                draw=odds_obj.ft_draw_odds,
                away=odds_obj.ft_away_win_odds
            ),
            odds_over_under_2_5=OddsOverUnder(
                over=odds_obj.over_2_5_odds,
                under=odds_obj.under_2_5_odds
            ),
            is_live=True,
            fetched_at=odds_obj.fetched_at
        )
        result_fixtures.append(fixture_with_odds)

    return OddsListResponse(total=total, fixtures=result_fixtures)
