# SuperStatsFootball Testing Guide

Complete guide to test the data synchronization and prediction system.

## Prerequisites

1. **Start the backend server:**
```bash
cd /home/user/SuperStatsFootball/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Verify server is running:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","environment":"development","version":"1.0.0","api":"operational"}
```

---

## Test 1: Authentication & User Management

### 1.1 Login as Admin
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@superstatsfootball.com","password":"Admin123!"}'
```

**Save the access_token from the response!** You'll need it for admin endpoints.

### 1.2 Create a Test User (Free Tier)
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"testuser@example.com",
    "password":"Test123!",
    "full_name":"Test User"
  }'
```

### 1.3 Login as Test User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"Test123!"}'
```

---

## Test 2: Season Management (Admin Only)

Replace `YOUR_ADMIN_TOKEN` with the token from Test 1.1

### 2.1 Check Current Season Statistics
```bash
curl "http://localhost:8000/api/v1/admin/season/statistics" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected response:
```json
{
  "current_season": 2025,
  "valid_seasons": [2025, 2024, 2023, 2022, 2021],
  "seasons_in_db": [],
  "total_fixtures": 0
}
```

### 2.2 Check Season Transition
```bash
curl -X POST "http://localhost:8000/api/v1/admin/season/check-transition" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Test 3: League Tier System

### 3.1 Get Tier Information (as Admin - Ultimate tier)
```bash
curl "http://localhost:8000/api/v1/leagues/tier-info" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

Expected: Shows all 150+ leagues accessible to ultimate tier

### 3.2 Get Tier Information (as Free User)
```bash
curl "http://localhost:8000/api/v1/leagues/tier-info" \
  -H "Authorization: Bearer YOUR_FREE_USER_TOKEN"
```

Expected: Shows only 3 leagues (Premier League, La Liga, Bundesliga)

### 3.3 Get Accessible Leagues
```bash
curl "http://localhost:8000/api/v1/leagues/accessible/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Test 4: Data Synchronization (Admin Only)

**IMPORTANT:** These tests require a valid API-Football API key in your .env file.

### 4.1 Sync a Single League (Test with Premier League - ID 152)
```bash
curl -X POST "http://localhost:8000/api/v1/admin/sync/league/152?season=2024" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

This will:
- Fetch league metadata
- Fetch teams for the league
- Fetch fixtures for the season
- Fetch statistics for each fixture

### 4.2 Sync Multiple Leagues (Free Tier Only - for testing)
```bash
curl -X POST "http://localhost:8000/api/v1/admin/sync/full?tier_filter=free&limit=3" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

This syncs only the 3 free-tier leagues (Premier League, La Liga, Bundesliga) for 5 seasons.

### 4.3 Check Sync Progress
After syncing, check the database:
```bash
curl "http://localhost:8000/api/v1/admin/debug" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Test 5: Fixtures & Data Access

### 5.1 Get All Fixtures (Public)
```bash
curl "http://localhost:8000/api/v1/fixtures/?limit=10"
```

### 5.2 Get Fixtures for Specific League
```bash
curl "http://localhost:8000/api/v1/fixtures/?league_id=152&season=2024&limit=10"
```

### 5.3 Get Accessible Fixtures (Tier-Based)
```bash
curl "http://localhost:8000/api/v1/fixtures/accessible/me?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Free users will only see fixtures from their 3 accessible leagues.

### 5.4 Get Upcoming Fixtures (Tier-Based)
```bash
curl "http://localhost:8000/api/v1/fixtures/accessible/upcoming?days_ahead=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Test 6: Predictions

**NOTE:** You need fixtures in the database first (run Test 4 first)

### 6.1 Generate Prediction for a Fixture
First, get a fixture ID from Test 5.2, then:

```bash
curl -X POST "http://localhost:8000/api/v1/predictions/calculate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fixture_id": FIXTURE_ID,
    "model_type": "poisson"
  }'
```

Response will include:
- Home/Draw/Away probabilities
- Team statistics
- Model predictions (Poisson, Dixon-Coles, Elo based on tier)
- Consensus recommendation

### 6.2 Generate Predictions for Upcoming Matches
```bash
curl "http://localhost:8000/api/v1/predictions/upcoming?days_ahead=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6.3 Get User's Prediction History
```bash
curl "http://localhost:8000/api/v1/predictions/user/history?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Test 7: User Tier Upgrades (Admin)

### 7.1 Upgrade User to Pro Tier
```bash
# First, get the user ID from login response or:
curl "http://localhost:8000/api/v1/admin/users?limit=10" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Then upgrade:
curl -X PUT "http://localhost:8000/api/v1/admin/users/USER_ID/tier?tier=pro" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 7.2 Verify Upgraded Access
Login again as the upgraded user and check tier info:
```bash
curl "http://localhost:8000/api/v1/leagues/tier-info" \
  -H "Authorization: Bearer UPGRADED_USER_TOKEN"
```

Now they should see 25 leagues instead of 3!

---

## Test 8: Season Cleanup

### 8.1 Manual Season Cleanup
```bash
curl -X POST "http://localhost:8000/api/v1/admin/season/cleanup" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

This will delete data from seasons older than the retention policy (current + 4 previous).

---

## Test 9: API Documentation

### 9.1 View Interactive API Docs
Open in browser:
```
http://localhost:8000/docs
```

This provides Swagger UI where you can test all endpoints interactively.

### 9.2 View ReDoc
```
http://localhost:8000/redoc
```

---

## Complete Test Flow Example

Here's a complete end-to-end test scenario:

```bash
# 1. Start server
cd /home/user/SuperStatsFootball/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 2. Login as admin (in another terminal)
ADMIN_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@superstatsfootball.com","password":"Admin123!"}' | \
  jq -r '.access_token')

echo "Admin token: $ADMIN_TOKEN"

# 3. Check season stats
curl -s "http://localhost:8000/api/v1/admin/season/statistics" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# 4. Sync Premier League (ID 152) for 2024 season
curl -s -X POST "http://localhost:8000/api/v1/admin/sync/league/152?season=2024" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# 5. Check debug info
curl -s "http://localhost:8000/api/v1/admin/debug" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# 6. Create free user
curl -s -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"freeuser@test.com","password":"Free123!","full_name":"Free User"}' | jq

# 7. Login as free user
FREE_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"freeuser@test.com","password":"Free123!"}' | \
  jq -r '.access_token')

# 8. Check tier info (should show only 3 leagues)
curl -s "http://localhost:8000/api/v1/leagues/tier-info" \
  -H "Authorization: Bearer $FREE_TOKEN" | jq

# 9. Get accessible fixtures (only from 3 free leagues)
curl -s "http://localhost:8000/api/v1/fixtures/accessible/me?limit=5" \
  -H "Authorization: Bearer $FREE_TOKEN" | jq

# 10. Upgrade user to premium
USER_ID=$(curl -s "http://localhost:8000/api/v1/admin/users?limit=50" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | \
  jq -r '.[] | select(.email=="freeuser@test.com") | .id')

curl -s -X PUT "http://localhost:8000/api/v1/admin/users/$USER_ID/tier?tier=premium" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# 11. Login again and verify upgrade
FREE_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"freeuser@test.com","password":"Free123!"}' | \
  jq -r '.access_token')

curl -s "http://localhost:8000/api/v1/leagues/tier-info" \
  -H "Authorization: Bearer $FREE_TOKEN" | jq
```

---

## Expected Results by Tier

### Free Tier (3 leagues)
- Premier League (152)
- La Liga (140)
- Bundesliga (78)
- Model: Poisson only

### Starter Tier (10 leagues)
- All Free leagues +
- Serie A, Ligue 1, Eredivisie, Primeira Liga, etc.
- Models: Poisson + Dixon-Coles

### Pro Tier (25 leagues)
- All Starter leagues +
- UEFA Champions League, Europa League, Conference League
- Models: Poisson + Dixon-Coles + Elo

### Premium Tier (50+ leagues)
- All Pro leagues +
- Championship, League One, Serie B, etc.
- Models: Poisson + Dixon-Coles + Elo + Logistic Regression

### Ultimate Tier (150+ leagues)
- ALL leagues worldwide
- Models: All models including Random Forest, XGBoost

---

## Troubleshooting

### Issue: "API key not configured"
**Solution:** Add your API-Football key to `.env`:
```
APIFOOTBALL_API_KEY=your_api_key_here
```

### Issue: "Fixture not found" when generating predictions
**Solution:** You need to sync data first using Test 4

### Issue: 401 Unauthorized
**Solution:** Token expired. Login again to get a fresh token

### Issue: Empty fixtures list
**Solution:** Sync some leagues first using the admin sync endpoints

---

## Next Steps

After testing:
1. Set up a cron job to sync data daily
2. Implement frontend React app to display predictions
3. Add payment integration for tier upgrades
4. Deploy to production (GreenGeeks/cloud provider)
