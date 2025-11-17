# SuperStatsFootball - Complete Deployment Guide

## 🚀 Production Deployment Checklist

This guide will walk you through deploying both the backend (Railway) and frontend (GreenGeeks) to production.

---

## Table of Contents

1. [Backend Deployment (Railway)](#backend-deployment-railway)
2. [Frontend Deployment (GreenGeeks)](#frontend-deployment-greengeeks)
3. [Testing & Verification](#testing--verification)
4. [Troubleshooting](#troubleshooting)
5. [Post-Deployment](#post-deployment)

---

## Backend Deployment (Railway)

### Prerequisites
- [x] Railway account created
- [x] GitHub repository connected
- [x] Database (Supabase PostgreSQL) provisioned

### Step 1: Configure Environment Variables

Go to Railway Dashboard → Your Service → Variables tab and add:

```bash
# Required Variables
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=<generate-with-command-below>
ENVIRONMENT=production
DEBUG=false

# API Configuration
API_V1_PREFIX=/api/v1
APP_NAME=SuperStatsFootball
VERSION=1.0.0

# Optional (for features)
APIFOOTBALL_API_KEY=your_api_football_key
STRIPE_SECRET_KEY=your_stripe_key
REDIS_URL=redis://...
SENTRY_DSN=https://...
```

**Generate SECRET_KEY:**
```bash
# Run this command locally
openssl rand -hex 32
# Copy the output and use as SECRET_KEY
```

### Step 2: Verify Build Settings

Railway should auto-detect Python and use:
- **Build Command:** `pip install -r backend/requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Root Directory:** `/backend`

### Step 3: Check Deployment Logs

After pushing code or triggering manual deploy:

1. Go to Railway Dashboard → Deployments → Latest
2. Watch the build logs:
   - ✅ Dependencies installed
   - ✅ ML libraries (XGBoost, LightGBM, CatBoost) installed
   - ✅ Application starts without errors
3. Check runtime logs for:
   ```
   ================================================================================
   🚀 SuperStatsFootball v1.0.0 STARTING...
   ================================================================================
   📍 Environment: production
   🔒 Debug mode: False
   🌐 Host: 0.0.0.0
   🔌 Port: 8000
   🗄️  Database: postgres://***:***@...
   🔍 Checking environment variables...
     ✅ DATABASE_URL: SET
     ✅ SECRET_KEY: SET
     ✅ ENVIRONMENT: SET
   ================================================================================
   ✅ STARTUP COMPLETE! Application is ready to accept requests.
   ================================================================================
   ```

### Step 4: Test Backend Health

Visit your Railway URL:
```
https://your-app.up.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0",
  "api": "operational",
  "database": "connected",
  "port": "8000"
}
```

### Step 5: Test API Endpoints

```bash
# Test registration
curl -X POST https://your-app.up.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'

# Test login
curl -X POST https://your-app.up.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

---

## Frontend Deployment (GreenGeeks)

### Prerequisites
- [x] GreenGeeks hosting account
- [x] cPanel access
- [x] Domain/subdomain configured

### Step 1: Prepare Files for Upload

**Files to upload** (all from `/frontend` directory):

```
frontend/
├── index.php                 ← Entry point
├── login_new.php            ← Login page
├── register_new.php         ← Registration page
├── logout.php               ← Logout handler
├── 1x2_new.php             ← Main dashboard
├── profile.php              ← User profile
├── subscription.php         ← Subscription plans
├── settings.php             ← User settings
├── config.php               ← Configuration
├── .htaccess                ← Apache configuration
├── error_401.php            ← Error pages
├── error_403.php
├── error_404.php
├── error_500.php
└── includes/
    ├── APIClient.php        ← API communication
    ├── auth-header.php      ← Auth page header
    ├── auth-footer.php      ← Auth page footer
    ├── auth-logo.php        ← Logo component
    ├── app-header.php       ← App navigation
    └── app-footer.php       ← App footer
```

### Step 2: Update Configuration

Before uploading, edit `frontend/config.php`:

```php
// Line 14 - Update with your Railway URL
define('API_BASE_URL', 'https://your-app.up.railway.app');

// Line 39 - Set to production
define('ENVIRONMENT', 'production');
```

### Step 3: Upload via cPanel

**Option A: File Manager**
1. Login to GreenGeeks cPanel
2. Navigate to File Manager
3. Go to `public_html` (or your domain folder)
4. Upload all files maintaining directory structure
5. Set permissions:
   - Files: `644`
   - Directories: `755`

**Option B: FTP**
1. Use FileZilla or similar FTP client
2. Connect to: `ftp.yourdomain.com`
3. Upload all files to `/public_html/`
4. Preserve directory structure

### Step 4: Configure PHP Settings

In cPanel → Select PHP Version:
- **PHP Version:** 7.4 or 8.0+ (recommended)
- **Extensions to enable:**
  - [x] curl
  - [x] json
  - [x] mbstring
  - [x] session
  - [x] pdo
  - [x] openssl

### Step 5: Test Frontend

1. **Visit your domain:**
   ```
   https://yourdomain.com
   ```
   - Should redirect to `login_new.php`

2. **Register new account:**
   - Fill in registration form
   - Should auto-login and redirect to dashboard

3. **Test login:**
   - Logout
   - Login again
   - Should access `1x2_new.php`

4. **Test protected pages:**
   - Try accessing `profile.php` directly without login
   - Should redirect to login

### Step 6: SSL Certificate (HTTPS)

In GreenGeeks cPanel:
1. Go to **SSL/TLS Status**
2. Enable AutoSSL for your domain
3. Wait 5-10 minutes for certificate issuance
4. Verify HTTPS works

**After SSL is active**, update `.htaccess`:
```apache
# Uncomment these lines in .htaccess (around line 113):
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
```

Also update `config.php`:
```php
// Update cookie security (around line 216 in APIClient.php)
php_value session.cookie_secure 1  // Change from 0 to 1
```

---

## Testing & Verification

### ✅ Backend Tests

| Test | URL | Expected Result |
|------|-----|-----------------|
| Health Check | `/health` | Status 200, healthy |
| API Docs | `/docs` | Should be disabled (404) |
| Registration | `/api/v1/auth/register` | Creates user, returns tokens |
| Login | `/api/v1/auth/login` | Returns tokens |
| Predictions | `/api/v1/combined/fixtures/predictions-with-odds` | Returns fixtures (auth required) |

### ✅ Frontend Tests

| Test | Action | Expected Result |
|------|--------|-----------------|
| Landing | Visit root URL | Redirect to login |
| Direct Access | Visit `1x2_new.php` without login | Redirect to login |
| Registration | Fill registration form | Account created, auto-login |
| Login | Login with credentials | Redirect to dashboard |
| Dashboard | Access predictions page | Shows matches table |
| Navigation | Click profile/subscription/settings | Pages load correctly |
| Logout | Click logout | Session cleared, redirect to login |
| Session Expiry | Wait 30 min inactive | Auto-logout, redirect to login |

### ✅ Security Tests

| Test | How | Expected Result |
|------|-----|-----------------|
| HTTPS | Check URL | SSL certificate valid |
| Headers | Check dev tools | Security headers present |
| XSS | Try script injection | Blocked |
| SQL Injection | Try SQL in forms | Blocked |
| Direct File Access | Visit `/includes/APIClient.php` | 403 Forbidden |
| Directory Listing | Visit `/includes/` | 403 Forbidden |

---

## Troubleshooting

### Backend Issues

#### Issue: Healthcheck failing
**Symptoms:** Railway shows "service unavailable"

**Solutions:**
1. Check environment variables are set:
   ```bash
   railway vars
   ```
2. View runtime logs:
   ```bash
   railway logs
   ```
3. Look for database connection errors
4. Verify `DATABASE_URL` format is correct

#### Issue: ML models failing
**Symptoms:** Predictions return errors

**Solutions:**
1. Check build logs - ensure XGBoost, LightGBM, CatBoost installed
2. Verify memory limits (Railway: 8GB recommended for ML models)
3. Check model training completed successfully

#### Issue: CORS errors
**Symptoms:** Frontend can't access backend

**Solutions:**
1. Update `backend/app/main.py` CORS origins:
   ```python
   cors_origins = ["https://yourdomain.com", "https://www.yourdomain.com"]
   ```
2. Redeploy backend

### Frontend Issues

#### Issue: "Failed to connect to API"
**Symptoms:** Login/registration doesn't work

**Solutions:**
1. Verify `config.php` has correct `API_BASE_URL`
2. Check Railway backend is running
3. Check browser console for errors
4. Verify CORS is configured on backend

#### Issue: Session not persisting
**Symptoms:** Logged out immediately after login

**Solutions:**
1. Check PHP sessions are enabled
2. Verify cookies are enabled in browser
3. Check `.htaccess` is uploaded
4. Verify session directory is writable

#### Issue: "Headers already sent" error
**Symptoms:** PHP warnings about headers

**Solutions:**
1. Check no whitespace before `<?php` in files
2. Verify files are saved in UTF-8 without BOM
3. Check no `echo` statements before redirects

#### Issue: 500 Internal Server Error
**Symptoms:** White screen or error page

**Solutions:**
1. Enable error display temporarily:
   ```php
   // In config.php
   ini_set('display_errors', 1);
   error_reporting(E_ALL);
   ```
2. Check error logs in cPanel
3. Verify all required PHP extensions enabled

---

## Post-Deployment

### Monitoring

**Backend (Railway):**
- Check logs daily for errors
- Monitor response times
- Watch database connection pool

**Frontend (GreenGeeks):**
- Check error logs in cPanel
- Monitor uptime
- Review traffic analytics

### Backups

**Backend:**
- Railway: Auto-backups enabled
- Database: Supabase daily backups

**Frontend:**
- cPanel: Weekly full backups
- Git: Code already backed up

### Performance Optimization

**Backend:**
1. Enable Redis caching (optional):
   ```python
   # Add to requirements.txt
   redis==4.5.1
   ```

2. Configure rate limiting
3. Monitor API response times

**Frontend:**
1. Enable compression (already in `.htaccess`)
2. Optimize images (use WebP format)
3. Enable browser caching (already configured)

### Security Updates

**Monthly tasks:**
- [ ] Update Python dependencies: `pip list --outdated`
- [ ] Update PHP version if needed
- [ ] Review security headers
- [ ] Check SSL certificate expiry
- [ ] Review access logs for suspicious activity

---

## Environment Comparison

| Feature | Development | Production |
|---------|-------------|------------|
| Backend URL | `localhost:8000` | `your-app.up.railway.app` |
| Frontend URL | `localhost` | `yourdomain.com` |
| Database | SQLite | PostgreSQL (Supabase) |
| Debug Mode | `true` | `false` |
| Error Display | On | Off |
| HTTPS | Optional | Required |
| Logging | Console | File + Sentry |
| CORS | `*` (all) | Specific domains |

---

## Quick Commands Reference

### Backend (Railway CLI)

```bash
# View logs
railway logs

# Check environment variables
railway vars

# Set environment variable
railway vars set SECRET_KEY=your_secret_key

# Trigger manual deploy
railway up

# SSH into container
railway run bash
```

### Frontend (cPanel Terminal)

```bash
# Check PHP version
php -v

# List enabled PHP modules
php -m

# Check error logs
tail -f ~/public_html/error_log

# Find large files
find ~/public_html -type f -size +10M

# Set permissions recursively
find ~/public_html -type f -exec chmod 644 {} \;
find ~/public_html -type d -exec chmod 755 {} \;
```

---

## File Permissions Guide

### Frontend Files

```bash
# Files (644 = rw-r--r--)
chmod 644 *.php
chmod 644 .htaccess
chmod 644 includes/*.php

# Directories (755 = rwxr-xr-x)
chmod 755 includes/

# Config (600 = rw-------)
chmod 600 config.php  # Optional for extra security
```

### What NOT to do
- ❌ Never use 777 permissions
- ❌ Don't commit `.env` files to Git
- ❌ Don't expose database credentials
- ❌ Don't disable security headers

---

## Success Criteria

Your deployment is successful when:

- ✅ Backend healthcheck returns 200 OK
- ✅ Frontend loads without errors
- ✅ User can register new account
- ✅ User can login successfully
- ✅ Dashboard shows predictions
- ✅ Session persists across page reloads
- ✅ Logout clears session
- ✅ HTTPS works without warnings
- ✅ Security headers are present
- ✅ Error pages display correctly

---

## Support & Resources

### Documentation
- Backend API Docs: `/docs` (development only)
- Authentication Guide: `AUTHENTICATION_GUIDE.md`
- ML Models Guide: `ML_MODELS_COMPLETE_GUIDE.md`
- Railway Troubleshooting: `RAILWAY_TROUBLESHOOTING.md`

### External Resources
- Railway Docs: https://docs.railway.app
- GreenGeeks Support: https://www.greengeeks.com/support
- FastAPI Docs: https://fastapi.tiangolo.com
- Bootstrap Docs: https://getbootstrap.com/docs/5.3

---

## Deployment Versions

**Current Deployment:**
- Backend: Railway (Python 3.11, FastAPI)
- Frontend: GreenGeeks (PHP 7.4+)
- Database: Supabase (PostgreSQL)
- ML Models: 22 models + 3 statistical = 25 total

**Version History:**
- v1.0.0 (2025-11-16): Initial production release
  - Complete authentication system
  - 25 prediction models
  - Strict auth-first architecture
  - Full security hardening

---

**Last Updated:** 2025-11-16
**Status:** Production Ready
**Maintained by:** SuperStatsFootball Team

---

## Next Steps After Deployment

1. **Test everything** using the checklists above
2. **Monitor logs** for first 24 hours
3. **Set up uptime monitoring** (UptimeRobot, Pingdom)
4. **Configure domain DNS** if not done
5. **Add Google Analytics** (optional)
6. **Set up email** for notifications (future)
7. **Configure payment gateway** (Stripe integration)
8. **Create admin panel** for user management

---

**Congratulations! Your SuperStatsFootball platform is now live! ⚽🎉**
