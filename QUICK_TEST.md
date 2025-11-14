# Quick Testing Guide - SuperStatsFootball

## ✅ System is Working!

All core features tested and working:
- ✅ Server running on port 8000
- ✅ Authentication system
- ✅ Tier-based access (Free: 3 leagues, Ultimate: 172 leagues)
- ✅ Season management (2025-2021)
- ✅ Admin endpoints
- ✅ User management

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start Server
```bash
cd /home/user/SuperStatsFootball/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Run Automated Tests
```bash
./test_system.sh
```

### Step 3: View Interactive API Docs
Open in browser: **http://localhost:8000/docs**

---

## 📊 What Works Right Now

| Feature | Status | Test Command |
|---------|--------|--------------|
| Health Check | ✅ | `curl http://localhost:8000/health` |
| Admin Login | ✅ | See TESTING_GUIDE.md |
| Season Stats | ✅ | Admin endpoint `/admin/season/statistics` |
| Tier System | ✅ | Free: 3 leagues, Ultimate: 172 leagues |
| User Registration | ✅ | POST `/auth/register` |
| Database | ✅ | 3 users, 3 leagues initialized |

---

## 🔑 Default Credentials

### Admin Account (Ultimate Tier - All 172 Leagues)
- **Email:** `admin@superstatsfootball.com`
- **Password:** `Admin123!`
- **Access:** All features + admin panel

### Test User (Free Tier - 3 Leagues)
- **Email:** `testfree@example.com`
- **Password:** `Test123!`
- **Access:** Premier League, La Liga, Bundesliga only

---

## 🧪 Test Scenarios

### Scenario 1: Test Tier System
```bash
# 1. Login as admin (gets 172 leagues)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@superstatsfootball.com","password":"Admin123!"}'

# Save the access_token, then:

# 2. Check accessible leagues
curl "http://localhost:8000/api/v1/leagues/tier-info" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected:** Admin sees 172 leagues, Free user sees 3 leagues

### Scenario 2: Test Season Management
```bash
# Login as admin first, then:

curl "http://localhost:8000/api/v1/admin/season/statistics" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Expected:**
```json
{
  "current_season": 2025,
  "valid_seasons": [2025, 2024, 2023, 2022, 2021],
  "seasons_in_db": [],
  "total_fixtures": 0
}
```

### Scenario 3: Test User Tier Upgrade
```bash
# 1. Create free user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@test.com","password":"Test123!","full_name":"New User"}'

# 2. Check their tier (should be "free" with 3 leagues)

# 3. Upgrade to premium (admin only)
curl -X PUT "http://localhost:8000/api/v1/admin/users/USER_ID/tier?tier=premium" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# 4. User now has access to 55 leagues!
```

---

## 🔄 Next: Test Data Sync (Requires API Key)

### Step 1: Add API-Football Key
Edit `/home/user/SuperStatsFootball/backend/.env`:
```env
APIFOOTBALL_API_KEY=your_api_key_here
```

### Step 2: Sync a Single League
```bash
# Sync Premier League (ID 152) for 2024 season
curl -X POST "http://localhost:8000/api/v1/admin/sync/league/152?season=2024" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

This will fetch:
- League metadata
- All teams
- All fixtures
- Match statistics

### Step 3: Verify Data
```bash
curl "http://localhost:8000/api/v1/admin/debug" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## 📈 Testing Predictions

After syncing data:

```bash
# 1. Get a fixture ID
curl "http://localhost:8000/api/v1/fixtures/?league_id=152&limit=1"

# 2. Generate prediction
curl -X POST "http://localhost:8000/api/v1/predictions/calculate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fixture_id":FIXTURE_ID,"model_type":"poisson"}'
```

**Free users** get: Poisson model
**Pro users** get: Poisson + Dixon-Coles + Elo
**Ultimate users** get: All models

---

## 🌐 Interactive Testing

### Option 1: Swagger UI (Recommended)
1. Open: http://localhost:8000/docs
2. Click "Authorize" button
3. Login to get token
4. Paste token (format: `Bearer YOUR_TOKEN`)
5. Test all endpoints with GUI

### Option 2: ReDoc
1. Open: http://localhost:8000/redoc
2. View all API documentation

### Option 3: curl Commands
See TESTING_GUIDE.md for 100+ example commands

---

## 📁 Test Files

| File | Purpose |
|------|---------|
| `test_system.sh` | Automated test script |
| `TESTING_GUIDE.md` | Complete testing documentation |
| `QUICK_TEST.md` | This file - quick reference |

---

## 🎯 Current Test Results

```
✅ Health check: PASSED
✅ Admin authentication: PASSED
✅ Season management: PASSED (2025-2021)
✅ Tier system: PASSED (172 vs 3 leagues)
✅ User management: PASSED
✅ Database: PASSED (3 users, 3 leagues)
⏳ Data sync: Needs API key
⏳ Predictions: Needs synced data
```

---

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill existing process
kill -9 PID
```

### Can't login
```bash
# Reset database
cd backend
rm app.db
python -m app.db.init_db
```

### Tests fail
```bash
# Check server logs
./test_system.sh

# View detailed logs in terminal running uvicorn
```

---

## 📞 Quick Help

- **Full guide:** See `TESTING_GUIDE.md`
- **API docs:** http://localhost:8000/docs
- **Server logs:** Check terminal where uvicorn is running
- **Database:** Located at `backend/app.db`

---

**Status:** System fully operational and ready for testing! 🚀
