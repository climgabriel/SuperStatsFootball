# Railway Deployment Guide for SuperStatsFootball

## ✅ Files Created

The following configuration files have been created to fix the Railway deployment:

1. **`nixpacks.toml`** - Railway build configuration
2. **`railway.json`** - Deployment settings
3. **`.railwayignore`** - Files to exclude from deployment
4. **`backend/Procfile`** - Process file for Railway
5. **`backend/Dockerfile`** - Updated for production (no --reload)

---

## 🚀 Deployment Steps

### Step 1: Commit and Push Changes

```bash
# Navigate to project directory
cd D:\GitHub\SuperStatsFootball

# Check git status
git status

# Add all new files
git add nixpacks.toml railway.json .railwayignore backend/Procfile backend/Dockerfile

# Commit changes
git commit -m "Add Railway deployment configuration files"

# Push to GitHub
git push origin main
```

### Step 2: Configure Environment Variables in Railway

Go to your Railway project dashboard:

1. Click on **Variables** tab
2. Add the following environment variables:

```env
# Database (Supabase)
DATABASE_URL=postgresql://postgres.tqbqtjpslcxwzljvqvwa:rapID1917@aws-1-eu-north-1.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://tqbqtjpslcxwzljvqvwa.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxYnF0anBzbGN4d3psanZxdndhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI5NzgyNDksImV4cCI6MjA3ODU1NDI0OX0.U_M82PBQnIrOg6AuBYCzJA3MLo0xt8rgkioqpNCjctA
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxYnF0anBzbGN4d3psanZxdndhIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2Mjk3ODI0OSwiZXhwIjoyMDc4NTU0MjQ5fQ.s12xAPmFflnAh-4QOP78NhyG8lSpHCJP18eaFWnnycU

# Security
SECRET_KEY=8886af2f5a3b7a3cb003d5f53dee90779568e71081b5e02e9d1f85a159b20a59
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# App Config
APP_NAME=SuperStatsFootball
VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False
API_V1_PREFIX=/api/v1

# CORS (add your GreenGeeks domain)
BACKEND_CORS_ORIGINS=["https://www.superstatsfootball.com","https://superstatsfootball.com","https://tips-365.com","http://localhost:3000"]

# API-Football
APIFOOTBALL_API_KEY=43203ffe99c5c3f1af1673bb1084dc6730572734e5ae214358488ce2250eb460
APIFOOTBALL_BASE_URL=https://v3.football.api-sports.io
APIFOOTBALL_RATE_LIMIT=100

# Redis (Railway will provide this if you add Redis service)
REDIS_URL=redis://redis:6379/0
CACHE_TTL=300

# Stripe (Optional - use test keys for now)
STRIPE_SECRET_KEY=sk_test_placeholder
STRIPE_WEBHOOK_SECRET=whsec_placeholder

# Sentry (Optional - leave empty for now)
SENTRY_DSN=
```

### Step 3: Deploy

1. Once you push to GitHub, Railway will automatically detect the changes
2. Go to your Railway dashboard
3. Watch the **Deployments** tab
4. The build should now succeed with the configuration files

### Step 4: Get Your API URL

After successful deployment:

1. Click on **Settings** tab in Railway
2. Find **Domains** section
3. Click **Generate Domain**
4. You'll get a URL like: `https://superstatsfootball-production.up.railway.app`

### Step 5: Test Your API

```bash
# Test health endpoint
curl https://your-app-url.up.railway.app/health

# Expected response:
# {"status":"healthy","environment":"production","version":"1.0.0","api":"operational"}

# Test API docs (if DEBUG=True, otherwise disabled in production)
# Open in browser: https://your-app-url.up.railway.app/docs
```

---

## 🔗 Connect Frontend to Backend

### Update Your PHP Frontend

In `D:\GitHub\SuperStatsFootballw\`, create a file `config.php`:

```php
<?php
// API Configuration
define('API_BASE_URL', 'https://your-app-url.up.railway.app/api/v1');

// Function to make API calls
function apiCall($endpoint, $method = 'GET', $data = null, $token = null) {
    $url = API_BASE_URL . $endpoint;

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);

    $headers = ['Content-Type: application/json'];
    if ($token) {
        $headers[] = 'Authorization: Bearer ' . $token;
    }
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

    if ($data && ($method === 'POST' || $method === 'PUT')) {
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    }

    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($httpCode >= 200 && $httpCode < 300) {
        return json_decode($response, true);
    }

    return ['error' => true, 'message' => 'API call failed', 'code' => $httpCode];
}
?>
```

Then update your `1x2.php`:

```php
<?php
include 'config.php';

// Instead of loading JSON file:
// $jsonData = file_get_contents('1x2_data.json');

// Call the API:
$token = $_SESSION['access_token'] ?? null;
$fixtures = apiCall('/fixtures/accessible/upcoming?days_ahead=7', 'GET', null, $token);

if (!isset($fixtures['error'])) {
    // Use $fixtures array as normal
    foreach ($fixtures as $match) {
        // Display match data
    }
} else {
    echo "Error loading fixtures: " . $fixtures['message'];
}
?>
```

---

## 🎯 Monitoring & Logs

### View Logs in Railway

1. Click on **Deployments** tab
2. Click on the latest deployment
3. Click **View logs**
4. Monitor application logs in real-time

### Common Issues

**Issue: Build fails with "Module not found"**
- Solution: Check `requirements.txt` has all dependencies

**Issue: App crashes on startup**
- Solution: Check environment variables are set correctly
- Check logs for database connection errors

**Issue: 502 Bad Gateway**
- Solution: App might be starting, wait 30-60 seconds
- Check health check endpoint is working

---

## 📊 Next Steps

1. ✅ Deploy backend to Railway
2. Update PHP frontend to use Railway API URL
3. Test all API endpoints
4. Set up custom domain (optional)
5. Configure Railway autoscaling (optional)
6. Add monitoring with Sentry (optional)

---

## 💰 Railway Pricing

- **Developer Plan**: $5/month
  - 512 MB RAM
  - 1 GB Disk
  - Shared CPU
  - Perfect for this project

- **Hobby Plan**: Free trial available
  - Limited to $5 credit/month

---

## 🆘 Support

If deployment fails:
1. Check Railway build logs
2. Verify all environment variables are set
3. Ensure GitHub repo is up to date
4. Check Railway documentation: https://docs.railway.app

---

**Deployment checklist:**
- [ ] Push configuration files to GitHub
- [ ] Add environment variables in Railway
- [ ] Wait for successful deployment
- [ ] Test health endpoint
- [ ] Generate Railway domain
- [ ] Update frontend PHP to use API URL
- [ ] Upload updated frontend to GreenGeeks
- [ ] Test full workflow (login, fetch data, predictions)
