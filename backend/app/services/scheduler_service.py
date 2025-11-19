"""
Automatic Data Synchronization Scheduler
Runs periodic tasks to keep database up-to-date and prevent Supabase inactivity pausing
"""

import asyncio
from typing import Optional
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
import logging

from app.db.session import get_db
from app.services.data_sync_service import DataSyncService
from app.models.fixture import Fixture
from app.core.leagues_config import get_sync_priority_leagues

logger = logging.getLogger(__name__)


class AutoSyncScheduler:
    """Automatic synchronization scheduler for all data types."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        logger.info("AutoSyncScheduler initialized")

    async def full_data_sync(self):
        """
        Full synchronization: fixtures, teams, leagues, standings, top scorers
        Runs every 4 hours
        """
        try:
            logger.info("=" * 80)
            logger.info("STARTING FULL DATA SYNC (Every 4 hours)")
            logger.info("=" * 80)

            db: Session = next(get_db())
            service = DataSyncService(db)

            # Get priority leagues (configured in leagues_config.py)
            league_ids = get_sync_priority_leagues()
            logger.info(f"Syncing {len(league_ids)} priority leagues...")

            # 1. Sync all leagues with fixtures, teams, stats
            logger.info("Step 1/4: Syncing fixtures, teams, and stats...")
            sync_result = await service.sync_all_leagues()
            logger.info(f"Fixtures sync result: {sync_result}")

            # 2. Sync standings for each league
            logger.info("Step 2/4: Syncing standings...")
            standings_count = 0
            for league_id in league_ids[:20]:  # Top 20 leagues for standings
                result = await service.sync_standings(league_id)
                if result.get("status") == "success":
                    standings_count += result.get("standings_synced", 0)
                await asyncio.sleep(0.5)  # Rate limiting

            logger.info(f"Synced {standings_count} standings entries")

            # 3. Sync top scorers for each league
            logger.info("Step 3/4: Syncing top scorers...")
            scorers_count = 0
            for league_id in league_ids[:20]:  # Top 20 leagues for top scorers
                result = await service.sync_top_scorers(league_id)
                if result.get("status") == "success":
                    scorers_count += result.get("scorers_synced", 0)
                await asyncio.sleep(0.5)  # Rate limiting

            logger.info(f"Synced {scorers_count} top scorers")

            # 4. Sync pre-match odds (24 hours ahead)
            logger.info("Step 4/4: Syncing pre-match odds...")
            odds_result = await service.sync_pre_match_odds(days_ahead=1)
            logger.info(f"Odds sync result: {odds_result}")

            logger.info("=" * 80)
            logger.info("FULL DATA SYNC COMPLETED")
            logger.info(f"Summary: {sync_result.get('leagues_synced', 0)} leagues, "
                       f"{sync_result.get('total_fixtures', 0)} fixtures, "
                       f"{standings_count} standings, {scorers_count} top scorers")
            logger.info("=" * 80)

            db.close()

        except Exception as e:
            logger.error(f"Error in full_data_sync: {str(e)}", exc_info=True)

    async def live_match_updates(self):
        """
        Update live match data (stats, scores, odds)
        Runs every 5 seconds during match times
        """
        try:
            db: Session = next(get_db())
            service = DataSyncService(db)

            # Get all live fixtures
            live_fixtures = db.query(Fixture).filter(
                Fixture.status.in_(["1H", "2H", "HT", "ET", "P", "LIVE"])
            ).all()

            if not live_fixtures:
                # No live matches, skip
                db.close()
                return

            logger.info(f"Updating {len(live_fixtures)} live matches...")

            for fixture in live_fixtures:
                try:
                    # Update fixture data (score, stats)
                    fixture_data = await service.api_football_client.get_fixtures(
                        match_id=fixture.id
                    )

                    if fixture_data and len(fixture_data) > 0:
                        await service._upsert_fixture(fixture_data[0])

                    # Update live odds
                    await service._sync_fixture_odds(fixture.id, is_live=True)

                    # Small delay between fixtures
                    await asyncio.sleep(0.2)

                except Exception as e:
                    logger.error(f"Error updating live fixture {fixture.id}: {str(e)}")

            logger.info(f"Live updates completed for {len(live_fixtures)} matches")
            db.close()

        except Exception as e:
            logger.error(f"Error in live_match_updates: {str(e)}", exc_info=True)

    async def sync_upcoming_fixtures_data(self):
        """
        Sync detailed data for upcoming fixtures (lineups, predictions, H2H)
        Runs every 2 hours
        """
        try:
            logger.info("Syncing upcoming fixtures data (lineups, predictions, H2H)...")

            db: Session = next(get_db())
            service = DataSyncService(db)

            # Get fixtures in next 7 days
            now = datetime.utcnow()
            end_date = now + timedelta(days=7)

            upcoming_fixtures = db.query(Fixture).filter(
                Fixture.match_date >= now,
                Fixture.match_date <= end_date,
                Fixture.status.in_(["NS", "TBD"])
            ).limit(50).all()  # Limit to 50 fixtures per run

            logger.info(f"Found {len(upcoming_fixtures)} upcoming fixtures")

            synced_count = {"lineups": 0, "predictions": 0, "h2h": 0}

            for fixture in upcoming_fixtures:
                try:
                    # Sync API-Football prediction
                    pred_result = await service.sync_api_prediction(fixture.id)
                    if pred_result.get("status") == "success":
                        synced_count["predictions"] += 1

                    # Sync lineups (if available - usually 1-2 hours before kickoff)
                    hours_until_match = (fixture.match_date - now).total_seconds() / 3600
                    if hours_until_match <= 2:  # Only fetch lineups if within 2 hours
                        lineup_result = await service.sync_lineups(fixture.id)
                        if lineup_result.get("status") == "success":
                            synced_count["lineups"] += lineup_result.get("lineups_synced", 0)

                    # Sync H2H for teams
                    h2h_result = await service.sync_h2h(fixture.home_team_id, fixture.away_team_id)
                    if h2h_result.get("status") == "success":
                        synced_count["h2h"] += h2h_result.get("matches_synced", 0)

                    # Rate limiting
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.error(f"Error syncing data for fixture {fixture.id}: {str(e)}")

            logger.info(f"Upcoming fixtures data sync completed: {synced_count}")
            db.close()

        except Exception as e:
            logger.error(f"Error in sync_upcoming_fixtures_data: {str(e)}", exc_info=True)

    async def daily_standings_sync(self):
        """
        Sync standings after each matchday
        Runs daily at 23:00 UTC (after most matches finish)
        """
        try:
            logger.info("Running daily standings sync...")

            db: Session = next(get_db())
            service = DataSyncService(db)

            league_ids = get_sync_priority_leagues()

            standings_synced = 0
            for league_id in league_ids[:30]:  # Top 30 leagues
                result = await service.sync_standings(league_id)
                if result.get("status") == "success":
                    standings_synced += result.get("standings_synced", 0)

                await asyncio.sleep(0.5)

            logger.info(f"Daily standings sync completed: {standings_synced} entries updated")
            db.close()

        except Exception as e:
            logger.error(f"Error in daily_standings_sync: {str(e)}", exc_info=True)

    async def keepalive_ping(self):
        """
        Simple database query to keep Supabase active
        Runs every 30 minutes
        """
        try:
            db: Session = next(get_db())

            # Simple count query to touch the database
            from app.models.league import League
            count = db.query(League).count()

            logger.debug(f"Keepalive ping: {count} leagues in database")
            db.close()

        except Exception as e:
            logger.error(f"Error in keepalive_ping: {str(e)}", exc_info=True)

    def start(self):
        """Start the scheduler with all jobs."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        logger.info("Starting AutoSyncScheduler...")

        # Job 1: Full data sync every 4 hours
        self.scheduler.add_job(
            self.full_data_sync,
            trigger=IntervalTrigger(hours=4),
            id="full_data_sync",
            name="Full Data Sync (Fixtures, Teams, Standings, Top Scorers)",
            replace_existing=True,
            max_instances=1
        )
        logger.info("✓ Scheduled: Full data sync every 4 hours")

        # Job 2: Live match updates every 5 seconds
        self.scheduler.add_job(
            self.live_match_updates,
            trigger=IntervalTrigger(seconds=5),
            id="live_match_updates",
            name="Live Match Updates (Scores, Stats, Odds)",
            replace_existing=True,
            max_instances=1
        )
        logger.info("✓ Scheduled: Live match updates every 5 seconds")

        # Job 3: Upcoming fixtures data (lineups, predictions, H2H) every 2 hours
        self.scheduler.add_job(
            self.sync_upcoming_fixtures_data,
            trigger=IntervalTrigger(hours=2),
            id="upcoming_fixtures_data",
            name="Upcoming Fixtures Data (Lineups, Predictions, H2H)",
            replace_existing=True,
            max_instances=1
        )
        logger.info("✓ Scheduled: Upcoming fixtures data sync every 2 hours")

        # Job 4: Daily standings sync at 23:00 UTC
        self.scheduler.add_job(
            self.daily_standings_sync,
            trigger=CronTrigger(hour=23, minute=0),
            id="daily_standings_sync",
            name="Daily Standings Sync (After Matchday)",
            replace_existing=True,
            max_instances=1
        )
        logger.info("✓ Scheduled: Daily standings sync at 23:00 UTC")

        # Job 5: Keepalive ping every 30 minutes (prevent Supabase pause)
        self.scheduler.add_job(
            self.keepalive_ping,
            trigger=IntervalTrigger(minutes=30),
            id="keepalive_ping",
            name="Database Keepalive Ping",
            replace_existing=True,
            max_instances=1
        )
        logger.info("✓ Scheduled: Database keepalive every 30 minutes")

        # Start the scheduler
        self.scheduler.start()
        self.is_running = True

        logger.info("=" * 80)
        logger.info("AutoSyncScheduler STARTED successfully!")
        logger.info("All scheduled jobs are now active")
        logger.info("=" * 80)

        # Run initial sync immediately
        logger.info("Running initial full sync...")
        asyncio.create_task(self.full_data_sync())

    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return

        logger.info("Stopping AutoSyncScheduler...")
        self.scheduler.shutdown(wait=True)
        self.is_running = False
        logger.info("AutoSyncScheduler stopped")

    def get_jobs(self):
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()


# Global scheduler instance
auto_sync_scheduler = AutoSyncScheduler()
