"""
Full Data Synchronization Script

This script syncs football data from API-Football to the database:
- Leagues and their metadata
- Teams from each league
- Upcoming and recent fixtures
- Match statistics
- Bookmaker odds (Superbet)

Usage:
    python scripts/sync_full_data.py                    # Sync all leagues
    python scripts/sync_full_data.py --tier free        # Sync only free tier leagues
    python scripts/sync_full_data.py --tier starter     # Sync only starter tier leagues
    python scripts/sync_full_data.py --limit 5          # Sync only 5 leagues (for testing)
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.services.data_sync_service import DataSyncService
from app.utils.logger import logger


async def sync_data(tier: str = None, limit: int = None):
    """Run full data synchronization."""

    logger.info("=" * 80)
    logger.info("🔄 Starting Full Data Synchronization")
    logger.info("=" * 80)

    if tier:
        logger.info(f"📊 Tier filter: {tier}")
    if limit:
        logger.info(f"🔢 League limit: {limit}")

    logger.info("=" * 80)

    db = SessionLocal()

    try:
        # Initialize sync service
        sync_service = DataSyncService(db)

        # Run synchronization
        logger.info("🚀 Starting league synchronization...")
        stats = await sync_service.sync_all_leagues(tier_filter=tier, limit=limit)

        logger.info("=" * 80)
        logger.info("✅ Synchronization Complete!")
        logger.info("=" * 80)
        logger.info(f"📈 Leagues synced: {stats.get('leagues_synced', 0)}")
        logger.info(f"👥 Teams synced: {stats.get('teams_synced', 0)}")
        logger.info(f"⚽ Fixtures synced: {stats.get('fixtures_synced', 0)}")
        logger.info(f"📊 Stats synced: {stats.get('stats_synced', 0)}")

        if stats.get('errors'):
            logger.warning(f"⚠️  Errors encountered: {len(stats['errors'])}")
            for error in stats['errors'][:5]:  # Show first 5 errors
                logger.warning(f"  - {error}")

        logger.info("=" * 80)

        # Sync odds for upcoming fixtures
        logger.info("🎲 Syncing odds for upcoming fixtures...")
        odds_stats = await sync_service.sync_pre_match_odds(days_ahead=7)

        logger.info("=" * 80)
        logger.info("✅ Odds Synchronization Complete!")
        logger.info("=" * 80)
        logger.info(f"🎯 Fixtures with odds: {odds_stats.get('fixtures_processed', 0)}")
        logger.info(f"📊 Odds records created: {odds_stats.get('odds_created', 0)}")
        logger.info("=" * 80)

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ Synchronization failed: {str(e)}")
        logger.error("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Sync football data from API-Football')
    parser.add_argument(
        '--tier',
        type=str,
        choices=['free', 'starter', 'pro', 'premium', 'ultimate'],
        help='Only sync leagues for specific tier'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of leagues to sync (useful for testing)'
    )

    args = parser.parse_args()

    # Run async function
    asyncio.run(sync_data(tier=args.tier, limit=args.limit))


if __name__ == "__main__":
    main()
