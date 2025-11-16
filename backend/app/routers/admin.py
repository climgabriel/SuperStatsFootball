from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional

from app.core.dependencies import get_db, require_admin
from app.models.user import User
from app.models.fixture import Fixture
from app.models.league import League
from app.models.prediction import Prediction
from app.models.odds import FixtureOdds
from app.services.data_sync_service import DataSyncService, run_full_sync
from app.services.season_manager import SeasonManager
from app.db.session import engine

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


@router.post("/sync/full")
async def sync_all_leagues(
    tier_filter: Optional[str] = None,
    limit: Optional[int] = None,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Trigger full synchronization of all leagues (or filtered by tier).

    Admin only. Syncs 150+ leagues for current + 4 previous seasons.

    Query Parameters:
    - tier_filter: Only sync leagues for specific tier (free, starter, pro, premium, ultimate)
    - limit: Limit number of leagues to sync (useful for testing)
    """
    try:
        result = await run_full_sync(db, tier=tier_filter)
        return {
            "status": "completed",
            "message": "Full league synchronization completed successfully",
            "details": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Synchronization failed: {str(e)}"
        )


@router.post("/sync/league/{league_id}")
async def sync_single_league(
    league_id: int,
    season: Optional[int] = None,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Trigger synchronization for a specific league.

    Admin only. If season is not provided, syncs current + 4 previous seasons.
    """
    try:
        service = DataSyncService(db)
        season_manager = SeasonManager(db)

        if season:
            seasons_to_sync = [season]
        else:
            seasons_to_sync = season_manager.get_valid_seasons()

        for s in seasons_to_sync:
            await service._sync_league_season(league_id, s)

        return {
            "status": "completed",
            "league_id": league_id,
            "seasons_synced": seasons_to_sync,
            "sync_stats": service.sync_stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"League sync failed: {str(e)}"
        )


@router.get("/season/statistics")
async def get_season_statistics(
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Get statistics about seasons in database.

    Admin only. Shows current season, valid seasons, and fixture counts per season.
    """
    season_manager = SeasonManager(db)
    stats = season_manager.get_season_statistics()
    return stats


@router.post("/season/cleanup")
async def cleanup_old_seasons(
    league_id: Optional[int] = None,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Manually trigger cleanup of old seasons.

    Admin only. Removes data from seasons older than retention policy (current + 4 previous).

    Query Parameters:
    - league_id: Optional. Clean specific league, or all leagues if not provided
    """
    try:
        season_manager = SeasonManager(db)
        cleanup_stats = season_manager.cleanup_old_seasons(league_id=league_id)

        return {
            "status": "completed",
            "message": "Season cleanup completed successfully",
            "stats": cleanup_stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Season cleanup failed: {str(e)}"
        )


@router.post("/season/check-transition")
async def check_season_transition(
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Check if season transition has occurred and perform cleanup if needed.

    Admin only. Automatically detects new season and removes oldest season data.
    """
    try:
        season_manager = SeasonManager(db)
        transition_info = season_manager.check_season_transition()

        return {
            "status": "completed",
            "transition_info": transition_info,
            "message": "Season transition check completed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Season transition check failed: {str(e)}"
        )


@router.post("/database/create-odds-table")
async def create_odds_table(db: Session = Depends(get_db)):
    """
    Create the fixture_odds table in the database.

    One-time setup endpoint. No authentication required for initial setup.
    Run this once after deploying odds integration to create the table.
    """
    try:
        # Create only the FixtureOdds table
        FixtureOdds.__table__.create(bind=engine, checkfirst=True)

        # Verify table was created
        table_exists = db.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'fixture_odds')")
        ).scalar()

        return {
            "status": "success",
            "message": "fixture_odds table created successfully",
            "table_exists": table_exists
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create odds table: {str(e)}"
        )


@router.post("/odds/sync-upcoming")
async def sync_upcoming_odds(
    days_ahead: int = 7,
    league_id: Optional[int] = None,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Sync pre-match odds for upcoming fixtures.

    Admin only. Fetches Superbet odds from API-Football for fixtures
    in the next N days.

    Query Parameters:
    - days_ahead: Number of days to look ahead (default: 7)
    - league_id: Optional league filter
    """
    try:
        service = DataSyncService(db)
        result = await service.sync_pre_match_odds(days_ahead=days_ahead, league_id=league_id)

        return {
            "status": "completed",
            "message": "Pre-match odds sync completed",
            "details": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Odds sync failed: {str(e)}"
        )


@router.post("/odds/sync-live")
async def sync_live_odds(
    league_id: Optional[int] = None,
    current_user: User = Depends(require_admin()),
    db: Session = Depends(get_db)
):
    """
    Sync live odds for ongoing matches.

    Admin only. Fetches Superbet live odds from API-Football for
    all currently ongoing matches.

    Query Parameters:
    - league_id: Optional league filter
    """
    try:
        service = DataSyncService(db)
        result = await service.sync_live_odds(league_id=league_id)

        return {
            "status": "completed",
            "message": "Live odds sync completed",
            "details": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Live odds sync failed: {str(e)}"
        )
