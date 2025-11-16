# Railway Deployment Troubleshooting

## Issue: Healthcheck Failing After Build Success

### Symptoms
- Build completes successfully
- All ML dependencies installed (XGBoost, LightGBM, CatBoost)
- Healthcheck endpoint `/health` returns "service unavailable"
- Deployment fails after 6 retry attempts

### Most Likely Causes

#### 1. Missing Environment Variables ⚠️
Railway requires these environment variables to be set:

**Required:**
- `DATABASE_URL` - PostgreSQL connection string from Supabase
- `SECRET_KEY` - JWT secret key

**Recommended:**
- `ENVIRONMENT=production`
- `DEBUG=false`

**Optional (for full functionality):**
- `APIFOOTBALL_API_KEY` - API-Football.com API key
- `STRIPE_SECRET_KEY` - Stripe payments
- `REDIS_URL` - Redis caching
- `SENTRY_DSN` - Error tracking

#### 2. Port Configuration
Railway automatically sets the `PORT` environment variable. The Dockerfile is configured to use it:
```dockerfile
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
```

#### 3. Database Connection
If `DATABASE_URL` is not set or incorrect, the app falls back to SQLite which should work for testing.

### How to Fix

#### Step 1: Check Railway Environment Variables
1. Go to Railway dashboard
2. Select your service
3. Click on "Variables" tab
4. Ensure `DATABASE_URL` is set with your Supabase PostgreSQL URL

Example format:
```
postgresql://postgres:[password]@[host]:5432/postgres
```

#### Step 2: View Runtime Logs
1. In Railway dashboard, click on your service
2. Click "Deployments" tab
3. Click on the failed deployment
4. Look for "Logs" or "Runtime logs" (not just build logs)
5. Check for Python errors or import failures

#### Step 3: Test Locally with Docker
```bash
cd backend
docker build -t superstats-backend .
docker run -p 8000:8000 -e DATABASE_URL="sqlite:///./test.db" -e ENVIRONMENT="development" superstats-backend
```

Then test healthcheck:
```bash
curl http://localhost:8000/health
```

### Expected Response
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0",
  "api": "operational"
}
```

### Common Solutions

#### Solution 1: Set Required Environment Variables
```bash
# In Railway dashboard Variables tab, add:
DATABASE_URL=postgresql://...
SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=production
DEBUG=false
```

#### Solution 2: Check Build Start Command
Railway should auto-detect the Dockerfile, but if not:
- Build Command: (leave empty, uses Dockerfile)
- Start Command: (leave empty, uses Dockerfile CMD)

#### Solution 3: Reduce Image Size (if timeout)
If the healthcheck is timing out due to large image size (catboost is 98.7 MB), try:
1. Use multi-stage Docker build
2. Remove unused dependencies
3. Increase healthcheck timeout in Railway settings

#### Solution 4: Simplify for Testing
Temporarily disable optional features:
```python
# In main.py, comment out:
# - Sentry initialization (lines 15-24)
# - Database table creation (lines 75-79)
```

### Debugging Checklist

- [ ] `DATABASE_URL` environment variable set in Railway
- [ ] Supabase database is accessible from Railway
- [ ] Railway runtime logs checked for errors
- [ ] Healthcheck endpoint returns 200 locally
- [ ] Port configuration using Railway's `$PORT` variable
- [ ] No import errors in application code
- [ ] All dependencies in requirements.txt installed (check build logs)

### Get Runtime Logs from Railway

To see the actual startup error:
1. Railway Dashboard → Your Service
2. Deployments tab → Select failed deployment
3. Look for "Logs" or "View Logs" button
4. Check for Python tracebacks or error messages

### Contact Support

If issue persists:
1. Copy runtime logs from Railway
2. Copy environment variables (redact sensitive values)
3. Share the specific error message from logs

---

## Recent Changes

### Latest Commit: ML Models Implementation
- Added 22 ML models (XGBoost, LightGBM, CatBoost, etc.)
- Updated requirements.txt with new dependencies
- All builds succeeded, healthcheck endpoint exists
- Models are NOT imported at startup (lazy loading)

### Files Modified
- `requirements.txt` - Added lightgbm==4.2.0, catboost==1.2.2
- `backend/app/ml/` - New ML model files (not imported until used)
- `backend/app/main.py` - Improved startup error handling

### What This Means
The ML models themselves are NOT causing the healthcheck failure because they're not imported during application startup. The issue is likely environment configuration or database connection.

---

**Last Updated:** 2025-11-16
**Status:** Investigating healthcheck failure on Railway
