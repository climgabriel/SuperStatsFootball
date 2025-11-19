# Comprehensive Automatic Data Synchronization System

## Overview

This implementation adds **automatic data synchronization** to prevent Supabase free tier inactivity pausing and ensures your database is always up-to-date with the latest football data from apifootball.com.

---

## What Was Implemented

### ✅ Automatic Sync Scheduler (APScheduler)

**File:** `backend/app/services/scheduler_service.py`

The scheduler runs **5 background jobs** automatically:

#### 1. **Full Data Sync** (Every 4 hours)
- Syncs fixtures, teams, leagues
- Syncs standings for top 20 leagues
- Syncs top scorers for top 20 leagues
- Syncs pre-match odds (24 hours ahead)
- **Prevents Supabase inactivity pause**

#### 2. **Live Match Updates** (Every 5 seconds)
- Updates scores and stats for ongoing matches
- Updates live odds
- Only runs when matches are in progress

#### 3. **Upcoming Fixtures Data** (Every 2 hours)
- Syncs API-Football predictions
- Syncs lineups (2 hours before kickoff)
- Syncs head-to-head history
- Limited to 50 fixtures per run

#### 4. **Daily Standings Sync** (23:00 UTC)
- Updates league tables after matchdays
- Syncs top 30 priority leagues
- Captures final standings for the day

#### 5. **Database Keepalive Ping** (Every 30 minutes)
- Simple database query to keep Supabase active
- **Critical: Prevents 7-day inactivity pause**

---

## New Database Tables

### 1. `standings` - League Tables
Stores league standings with home/away records:
- Rank, points, form, status
- Overall, home, and away statistics
- Goals for/against, goal difference
- Updated after each matchday

### 2. `lineups` - Match Lineups
Stores team formations and player lineups:
- Formation (e.g., "4-4-2")
- Coach information
- Starting XI (JSON)
- Substitutes (JSON)

### 3. `player_statistics` - Player Match Stats
Detailed player performance metrics:
- Goals, assists, shots
- Passes, dribbles, tackles
- Cards, fouls, penalties
- Goalkeeper saves

### 4. `top_scorers` - League Top Scorers
Top scorers and assists by league:
- Player info (name, age, nationality)
- Goals, assists, appearances
- Detailed statistics (shots, passes, tackles)
- Updated weekly

### 5. `api_predictions` - API-Football Predictions
AI predictions from API-Football:
- Winner prediction with probabilities
- Goals prediction (home/away)
- Under/Over recommendation
- Betting advice
- Comparison data (JSON)

### 6. `h2h_matches` - Head-to-Head History
Historical matches between teams:
- Past match results
- Scores, dates, winners
- Indexed for fast lookups

---

## New API Endpoints

### Extended API-Football Client

`backend/app/services/apifootball.py`:
- `get_top_scorers(league_id)` - Top scorers for a league
- `get_players(team_id, player_name)` - Player search

### Extended Data Sync Service

`backend/app/services/data_sync_service.py`:
- `sync_standings(league_id, season)` - Sync league tables
- `sync_lineups(fixture_id)` - Sync match lineups
- `sync_top_scorers(league_id, season)` - Sync top scorers
- `sync_api_prediction(fixture_id)` - Sync API predictions
- `sync_h2h(team1_id, team2_id)` - Sync head-to-head history

---

## How It Works

### Startup Sequence

1. **Railway/Server starts** → FastAPI application boots
2. **Database migration runs** → New tables created
3. **Scheduler starts** → All 5 background jobs activated
4. **Initial sync runs** → Immediate full data sync
5. **Jobs run automatically** → According to their schedules

### Data Flow

```
┌─────────────────────────────────────────────┐
│      APScheduler Background Jobs            │
├─────────────────────────────────────────────┤
│  Every 4 hours:  Full Sync                  │
│  Every 5 sec:    Live Updates (if matches)  │
│  Every 2 hours:  Upcoming Fixtures Data     │
│  Daily 23:00:    Standings Sync             │
│  Every 30 min:   Keepalive Ping             │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      API-Football.com (VIP Unlimited)       │
│  - Fixtures, Teams, Leagues                 │
│  - Statistics, Odds, Predictions            │
│  - Standings, Top Scorers, Lineups          │
│  - Head-to-Head History                     │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      Supabase PostgreSQL Database           │
│  - All data stored and indexed              │
│  - Never pauses (constant activity)         │
│  - Always up-to-date                        │
└─────────────────────────────────────────────┘
```

---

## Deployment Instructions

### 1. Resume Your Supabase Project

**Important:** Resume your paused Supabase project first!

1. Go to [Supabase Dashboard](https://app.supabase.com/)
2. Find your "SSF" project
3. Click **"Resume project"**
4. Wait for it to come online (~1-2 minutes)

### 2. Deploy to Railway

The code has been pushed to branch `claude/audit-repository-01PpGJYCsTM5ZjKxCdUELMvU`.

**Option A: Merge and Auto-Deploy**
```bash
# If Railway is watching your main branch:
git checkout main
git merge claude/audit-repository-01PpGJYCsTM5ZjKxCdUELMvU
git push origin main
```

**Option B: Railway CLI Deploy**
```bash
# If you have Railway CLI installed:
railway up
```

**Option C: Railway Dashboard**
1. Go to your Railway project
2. Settings → Triggers
3. Add the new branch or redeploy

### 3. Verify Deployment

Watch the Railway logs to ensure:

```
✅ Database tables created successfully
✅ Automatic sync scheduler started successfully
✅ Full data sync starting...
```

### 4. Install Dependencies

Railway will automatically run:
```bash
pip install -r requirements.txt
```

This installs `apscheduler==3.10.4` and all dependencies.

### 5. Run Migration (If Needed)

The migration should run automatically on Railway startup. If not:

```bash
# SSH into Railway or run locally:
cd backend
python scripts/apply_migrations.py
```

---

## Testing

### Test Locally (Optional)

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
export DATABASE_URL="your_supabase_url"
export APIFOOTBALL_API_KEY="your_api_key"
export SECRET_KEY="your_secret_key"
```

3. **Run the application:**
```bash
uvicorn app.main:app --reload
```

4. **Check logs:**
You should see:
```
🔄 Starting automatic data synchronization scheduler...
✅ Scheduled: Full data sync every 4 hours
✅ Scheduled: Live match updates every 5 seconds
✅ Scheduled: Upcoming fixtures data sync every 2 hours
✅ Scheduled: Daily standings sync at 23:00 UTC
✅ Scheduled: Database keepalive every 30 minutes
✅ Automatic sync scheduler started successfully
```

### Monitor Live on Railway

1. Go to Railway dashboard
2. Click on your backend service
3. Go to **Logs** tab
4. Watch for sync activity:
   - Initial full sync
   - Keepalive pings every 30 minutes
   - Live match updates (during match times)

---

## What This Solves

### ❌ Before (Problems)
- Supabase paused after 7 days of inactivity
- Manual data syncing required
- No live match updates
- Missing data types (standings, lineups, etc.)
- Database could become stale

### ✅ After (Solutions)
- **Supabase never pauses** (keepalive every 30 min)
- **Automatic syncing** every 4 hours
- **Live updates** every 5 seconds during matches
- **All data types** from apifootball.com synced
- **Always up-to-date** database

---

## API Rate Limits

With **VIP Unlimited** plan from apifootball.com:
- ✅ No rate limit concerns
- ✅ Unlimited API calls
- ✅ All data types accessible

The scheduler includes rate limiting delays to be respectful:
- 0.5 seconds between league syncs
- 0.2 seconds between live fixture updates
- Configurable in `app/core/leagues_config.py` (`SYNC_CONFIG`)

---

## Configuration

### Adjust Sync Frequency

Edit `backend/app/services/scheduler_service.py`:

```python
# Change from 4 hours to 6 hours:
trigger=IntervalTrigger(hours=6),  # Line ~245

# Change live updates from 5 seconds to 10 seconds:
trigger=IntervalTrigger(seconds=10),  # Line ~258

# Change keepalive from 30 minutes to 1 hour:
trigger=IntervalTrigger(minutes=60),  # Line ~285
```

### Adjust Which Leagues to Sync

Edit `backend/app/core/leagues_config.py`:

```python
# Add more leagues to priority sync:
SYNC_CONFIG = {
    "parallel_leagues": 5,  # How many leagues to sync in parallel
    "rate_limit_delay": 2,  # Delay between league batches
    "api_call_delay": 0.5   # Delay between API calls
}
```

---

## Monitoring

### Check Scheduler Status

Add this endpoint to `backend/app/routers/admin.py`:

```python
@router.get("/scheduler/status")
async def get_scheduler_status(current_user: User = Depends(get_current_admin_user)):
    """Get scheduler status and jobs."""
    from app.services.scheduler_service import auto_sync_scheduler

    jobs = auto_sync_scheduler.get_jobs()

    return {
        "is_running": auto_sync_scheduler.is_running,
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None
            }
            for job in jobs
        ]
    }
```

### Check Database Activity

Query Supabase logs or run:

```sql
-- Check recent standings updates
SELECT league_id, COUNT(*), MAX(updated_at)
FROM standings
GROUP BY league_id
ORDER BY MAX(updated_at) DESC;

-- Check recent top scorers
SELECT league_id, COUNT(*), MAX(updated_at)
FROM top_scorers
GROUP BY league_id
ORDER BY MAX(updated_at) DESC;
```

---

## Troubleshooting

### Scheduler Not Starting

**Check logs for:**
```
❌ Error starting scheduler: [error message]
```

**Solution:**
- Ensure `apscheduler` is installed
- Check for port conflicts
- Verify database connection

### No Data Being Synced

**Check:**
1. API-Football API key is valid
2. Database connection is working
3. Leagues are configured in `leagues_config.py`
4. Railway logs show sync attempts

**Test API manually:**
```python
from app.services.apifootball import api_football_client
result = await api_football_client.get_leagues()
print(result)
```

### Supabase Still Pausing

**Verify:**
1. Keepalive job is running (check logs every 30 min)
2. Database URL is correct
3. Supabase project is active (not hibernated)
4. Check Supabase dashboard for activity

---

## Performance Optimization

### Reduce API Calls

If you want to reduce API usage (though unlimited):

1. Increase sync intervals
2. Reduce number of leagues synced
3. Disable certain data types

### Reduce Database Load

1. Add indexes (already included in migration)
2. Limit historical data retention
3. Archive old seasons periodically

---

## Next Steps (Optional Enhancements)

### 1. Add Webhooks for Real-time Updates
Instead of polling every 5 seconds, use websockets or webhooks if API-Football supports it.

### 2. Implement Data Cleanup
Add a job to delete old data:
```python
async def cleanup_old_data():
    """Delete data older than 2 years."""
    cutoff_date = datetime.utcnow() - timedelta(days=730)
    db.query(Fixture).filter(Fixture.match_date < cutoff_date).delete()
```

### 3. Add Admin Dashboard
Create a web UI to:
- View scheduler status
- Trigger manual syncs
- View sync statistics
- Configure sync settings

### 4. Add Alerts
Send notifications when:
- Sync fails
- API rate limit approached
- Database errors occur

---

## Summary

You now have a **production-ready, fully automated** data synchronization system that:

✅ **Syncs all data types** from apifootball.com
✅ **Updates every 4 hours** automatically
✅ **Updates live matches every 5 seconds**
✅ **Never lets Supabase pause** (keepalive every 30 min)
✅ **Handles rate limiting** gracefully
✅ **Logs all activity** for monitoring
✅ **Starts automatically** on server boot

Your database will **always be up-to-date** and **never pause due to inactivity** again!

---

## Questions?

If you have any questions or need adjustments:
1. Check the logs first (`Railway → Logs`)
2. Verify Supabase is active
3. Test the API-Football connection
4. Review this documentation

The system is designed to be **robust, automatic, and maintenance-free**.
