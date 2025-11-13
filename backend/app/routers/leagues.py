from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db, get_current_active_user
from app.core.security import check_tier_access
from app.models.league import League
from app.models.user import User
from app.schemas.league import LeagueResponse
from app.core.leagues_config import get_leagues_for_tier, get_tier_for_league, LEAGUE_TIER_MAP

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


@router.get("/tier-info")
async def get_tier_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get information about leagues accessible at each tier level.

    Shows how many leagues are available at current tier and upgrade tiers.
    """
    tier_hierarchy = ["free", "starter", "pro", "premium", "ultimate"]
    current_tier_index = tier_hierarchy.index(current_user.tier) if current_user.tier in tier_hierarchy else 0

    accessible_leagues = get_leagues_for_tier(current_user.tier)

    tier_info = {
        "current_tier": current_user.tier,
        "accessible_leagues_count": len(accessible_leagues),
        "accessible_league_ids": accessible_leagues,
        "tier_breakdown": {}
    }

    # Show all tier information
    cumulative_count = 0
    for tier in tier_hierarchy:
        tier_leagues = LEAGUE_TIER_MAP.get(tier, [])
        cumulative_count += len(tier_leagues)

        tier_info["tier_breakdown"][tier] = {
            "leagues_in_tier": len(tier_leagues),
            "cumulative_total": cumulative_count,
            "locked": tier_hierarchy.index(tier) > current_tier_index
        }

    return tier_info


@router.get("/accessible/me", response_model=List[LeagueResponse])
async def get_accessible_leagues(
    season: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get leagues accessible to the current user based on their subscription tier.

    Requires authentication. Returns leagues from 150+ available based on tier:
    - Free: 3 leagues (Premier League, La Liga, Bundesliga)
    - Starter: 10 leagues (top European + international)
    - Pro: 25 leagues (all major competitions)
    - Premium: 50+ leagues (extensive coverage)
    - Ultimate: 150+ leagues (all leagues)
    """
    # Get league IDs accessible to user's tier
    accessible_league_ids = get_leagues_for_tier(current_user.tier)

    # Query leagues from database
    query = db.query(League).filter(
        League.id.in_(accessible_league_ids),
        League.is_active == True
    )

    if season:
        query = query.filter(League.season == season)

    leagues = query.order_by(League.priority.desc(), League.name).all()

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
