from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db, get_current_active_user
from app.core.security import check_tier_access
from app.models.league import League
from app.models.user import User
from app.schemas.league import LeagueResponse

router = APIRouter()


@router.get("/", response_model=List[LeagueResponse])
async def get_leagues(
    tier: Optional[str] = Query(None, description="Filter by tier"),
    is_active: bool = Query(True, description="Filter by active status"),
    country: Optional[str] = Query(None, description="Filter by country"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get list of leagues.

    Public endpoint - no authentication required.
    Returns leagues based on filters.
    """
    query = db.query(League)

    if is_active is not None:
        query = query.filter(League.is_active == is_active)

    if tier:
        query = query.filter(League.tier_required == tier)

    if country:
        query = query.filter(League.country.ilike(f"%{country}%"))

    query = query.order_by(League.priority.desc(), League.name)
    leagues = query.offset(offset).limit(limit).all()

    return leagues


@router.get("/{league_id}", response_model=LeagueResponse)
async def get_league(
    league_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific league by ID.

    Public endpoint - no authentication required.
    """
    league = db.query(League).filter(League.id == league_id).first()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"League {league_id} not found"
        )

    return league


@router.get("/accessible/me", response_model=List[LeagueResponse])
async def get_accessible_leagues(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get leagues accessible to the current user based on their subscription tier.

    Requires authentication.
    """
    # Get all active leagues
    all_leagues = db.query(League).filter(League.is_active == True).all()

    # Filter by user's tier access
    accessible_leagues = [
        league for league in all_leagues
        if check_tier_access(current_user.tier, league.tier_required)
    ]

    return accessible_leagues
