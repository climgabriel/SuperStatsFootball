from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.core.dependencies import get_db, require_admin
from app.models.user import User
from app.models.fixture import Fixture
from app.models.league import League
from app.models.prediction import Prediction

router = APIRouter()


@router.get("/debug")
async def get_debug_info(
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Get system debug information.

    Admin only. Shows system stats, database health, etc.
    """
    # Get database statistics
    total_users = db.query(func.count(User.id)).scalar()
    total_fixtures = db.query(func.count(Fixture.id)).scalar()
    total_leagues = db.query(func.count(League.id)).scalar()
    total_predictions = db.query(func.count(Prediction.id)).scalar()

    # User tier distribution
    tier_distribution = db.query(
        User.tier,
        func.count(User.id)
    ).group_by(User.tier).all()

    # Active fixtures
    active_fixtures = db.query(func.count(Fixture.id)).filter(
        Fixture.status == "LIVE"
    ).scalar()

    return {
        "system_stats": {
            "total_users": total_users,
            "total_fixtures": total_fixtures,
            "total_leagues": total_leagues,
            "total_predictions": total_predictions,
            "active_fixtures": active_fixtures
        },
        "user_tier_distribution": {
            tier: count for tier, count in tier_distribution
        },
        "database_health": "healthy",
        "api_status": "operational"
    }


@router.get("/users", response_model=List[dict])
async def get_all_users(
    tier: str = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Get list of all users.

    Admin only.
    """
    query = db.query(User)

    if tier:
        query = query.filter(User.tier == tier)

    users = query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()

    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "tier": user.tier,
            "subscription_status": user.subscription_status,
            "created_at": user.created_at
        }
        for user in users
    ]


@router.put("/users/{user_id}/tier")
async def update_user_tier(
    user_id: str,
    tier: str,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Update a user's subscription tier.

    Admin only.
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )

    valid_tiers = ["free", "starter", "pro", "premium", "ultimate"]
    if tier not in valid_tiers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid tier. Must be one of: {', '.join(valid_tiers)}"
        )

    user.tier = tier
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "tier": user.tier,
        "message": f"User tier updated to {tier}"
    }


@router.post("/sync/fixtures")
async def sync_fixtures(
    league_id: int,
    season: int,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Trigger manual fixture sync for a league/season.

    Admin only. This would trigger the background sync job.
    """
    # TODO: Implement actual sync logic
    return {
        "status": "started",
        "message": f"Fixture sync started for league {league_id}, season {season}",
        "note": "Sync job implementation pending"
    }
