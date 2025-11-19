# Quick Start Guide - Populating Database

## Overview

After migrating to apifootball.com API, your production database needs to be populated with football data.

## Run the Population Script on Railway

### Option 1: Via Railway CLI (Recommended)

```bash
# Install Railway CLI if you haven't
npm install -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Run the population script
railway run python scripts/quick_populate.py
```

### Option 2: Via Railway Dashboard

1. Go to your Railway project dashboard
2. Click on your backend service
3. Go to the "Settings" tab
4. Under "Deploy" section, add a one-time run command:
   ```
   python scripts/quick_populate.py
   ```
5. Or use the Railway shell to run it manually

### Option 3: Manually via Railway Shell

1. Go to Railway dashboard
2. Open your backend service
3. Click "Shell" or "Terminal"
4. Run:
   ```bash
   python scripts/quick_populate.py
   ```

## What Gets Populated

The script will populate:

- **5 Top Leagues**: Premier League, La Liga, Bundesliga, Serie A, Ligue 1
- **~96 Teams**: All teams from those 5 leagues
- **~100+ Fixtures**: Upcoming matches for the next 14 days

This should take about 30-60 seconds.

## Verify It Worked

After running, check your website at https://superstatsfootball.com/1x2.php

You should see:
- ✅ Real upcoming matches
- ✅ Team names
- ✅ Match dates
- ❌ NO "Live API data unavailable" message

## Running Locally

If you want to test locally first:

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python scripts/quick_populate.py
```

## Scheduling Regular Updates

To keep fixtures up-to-date, you can schedule this script to run:

- **Daily** to fetch new upcoming matches
- **Before matchdays** to ensure latest data

You can use Railway Cron Jobs or external schedulers like GitHub Actions.

## Troubleshooting

**Script fails with "API key not configured"**
- Ensure `APIFOOTBALL_API_KEY` environment variable is set in Railway

**No fixtures showing up**
- Check Railway logs for errors during population
- Verify your API key is valid at apifootball.com
- Run `python scripts/check_data.py` to see database contents

**"Live API data unavailable" still shows**
- Clear your browser cache
- Check Railway logs to ensure backend is running
- Verify database was actually populated

## Next Steps

Once you see real data on your website:

1. Set up automated daily syncing
2. Add more leagues if needed (edit `PRIORITY_LEAGUES` in script)
3. Implement odds fetching (future enhancement)
4. Update the full DataSyncService for comprehensive syncing
