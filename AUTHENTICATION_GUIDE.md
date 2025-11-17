# SuperStatsFootball - Authentication System Guide

## Overview

SuperStatsFootball implements a **strict authentication-first** architecture where:

1. ✅ **ALL users MUST login/register before accessing any content**
2. ✅ **NO unauthenticated access** to application pages
3. ✅ **Session-based authentication** with JWT tokens
4. ✅ **Auto-logout** on session expiry (30 minutes)
5. ✅ **Token refresh** mechanism for seamless experience

---

## Architecture

### Entry Point Flow

```
User visits website
        ↓
   index.php (ENTRY POINT)
        ↓
  Is user logged in?
        ↓
    YES → Redirect to 1x2_new.php (Dashboard)
    NO  → Redirect to login_new.php
```

### Authentication Flow

```
1. User visits login_new.php
        ↓
2. Enters email/password
        ↓
3. APIClient sends POST to /api/v1/auth/login
        ↓
4. Backend validates credentials
        ↓
5. Backend returns JWT access_token + refresh_token
        ↓
6. Frontend stores tokens in:
   - Session ($_SESSION)
   - Cookies (HTTP-only, secure)
        ↓
7. Redirect to index.php
        ↓
8. index.php detects logged-in user
        ↓
9. Redirect to 1x2_new.php (Dashboard)
```

---

## File Structure

### Public Pages (No Auth Required)
- `index.php` - Entry point (redirects based on auth status)
- `login_new.php` - Login page
- `register_new.php` - Registration page

### Protected Pages (Auth Required)
- `1x2_new.php` - Main dashboard (predictions)
- `profile.php` - User profile (future)
- `subscription.php` - Subscription management (future)
- `settings.php` - User settings (future)

### System Pages
- `logout.php` - Destroys session and redirects to login
- `config.php` - Configuration and auth helper functions

### Includes
**Authentication Pages:**
- `includes/auth-header.php` - HTML header for login/register
- `includes/auth-footer.php` - HTML footer with JS for login/register
- `includes/auth-logo.php` - App logo component

**Application Pages:**
- `includes/app-header.php` - Navigation bar with user menu
- `includes/app-footer.php` - Footer with session management JS
- `includes/APIClient.php` - Backend API communication

---

## Key Files Explained

### 1. `index.php` - The Gatekeeper

**Purpose:** Main entry point that enforces authentication.

```php
<?php
require_once 'config.php';

if (isLoggedIn()) {
    header('Location: 1x2_new.php');  // Send to dashboard
    exit;
} else {
    header('Location: login_new.php'); // Send to login
    exit;
}
```

**Why it matters:**
- This file ensures NO ONE can bypass authentication
- All navigation ultimately goes through here
- Simple redirect logic based on login status

---

### 2. `config.php` - Authentication Helpers

**Key Functions:**

```php
// Check if user is logged in
function isLoggedIn() {
    return isset($_SESSION['user']) && isset($_SESSION['access_token']);
}

// Get user's subscription tier
function getUserTier() {
    return $_SESSION['user']['tier'] ?? 'free';
}

// Get JWT access token
function getAccessToken() {
    return $_SESSION['access_token'] ?? $_COOKIE[TOKEN_COOKIE_NAME] ?? null;
}

// Force authentication (use in all protected pages)
function requireAuth() {
    if (!isLoggedIn()) {
        redirectToLogin();
    }
}

// Redirect to login page
function redirectToLogin() {
    header('Location: login_new.php');
    exit;
}
```

**Usage in Protected Pages:**

```php
<?php
require_once 'config.php';
requireAuth(); // This line makes the page protected!

// Rest of your page code...
```

---

### 3. `login_new.php` - Login Page

**Features:**
- Email/username + password login
- Form validation
- Error message display
- "Remember me" checkbox
- Link to register page
- Auto-redirect if already logged in

**How it works:**

```php
// Redirect if already logged in
if (isLoggedIn()) {
    header('Location: index.php');
    exit;
}

// Handle form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $api = new APIClient();
    $result = $api->login($email, $password);

    if ($result['success']) {
        // Tokens stored in session/cookies automatically
        header('Refresh: 1; URL=index.php');
    } else {
        $error = $result['error'];
    }
}
```

---

### 4. `register_new.php` - Registration Page

**Features:**
- Full name, email, password, confirm password
- Email validation
- Password strength (min 8 characters)
- Terms & conditions agreement
- Auto-login after successful registration

**Flow:**
1. User submits registration form
2. APIClient sends POST to `/api/v1/auth/register`
3. Backend creates user account
4. Frontend auto-logs in the new user
5. Redirect to index.php → Dashboard

---

### 5. `logout.php` - Session Termination

**What it does:**
1. Calls backend logout API endpoint
2. Destroys PHP session
3. Clears all session variables
4. Deletes authentication cookies
5. Redirects to login page

```php
// Call API logout
$api->logout();

// Destroy session
session_destroy();
$_SESSION = array();

// Delete cookies
setcookie(TOKEN_COOKIE_NAME, '', time() - 3600, '/');

// Redirect to login
header('Location: login_new.php?logged_out=1');
```

---

### 6. `APIClient.php` - Backend Communication

**Key Methods:**

```php
// Login - stores tokens in session & cookies
$api->login($email, $password);

// Register - creates new account
$api->register($email, $password, $fullName);

// Logout - clears all auth data
$api->logout();

// Refresh access token when expired
$api->refreshAccessToken();

// Get user profile
$api->getUserProfile();

// Get predictions with odds (requires auth)
$api->getPredictionsWithOdds($daysAhead, $leagueId, $limit);
```

**Token Management:**
- Stores tokens in both session and HTTP-only cookies
- Automatically includes `Authorization: Bearer {token}` header
- Auto-refreshes expired tokens on 401 errors
- Retries failed requests after token refresh

---

## Session Management

### Token Storage

**Session Variables:**
```php
$_SESSION['user']          // User info (id, email, full_name, tier)
$_SESSION['access_token']  // JWT access token
$_SESSION['refresh_token'] // JWT refresh token
```

**Cookies (HTTP-only, Secure):**
```php
$_COOKIE['ssf_access_token']  // JWT access token (30 min expiry)
$_COOKIE['ssf_refresh_token'] // JWT refresh token (7 days expiry)
```

### Auto-Logout

**Client-side (JavaScript in app-footer.php):**
- Tracks user inactivity
- Auto-logout after 30 minutes of no activity
- Resets timer on any user interaction (click, scroll, keyboard)

```javascript
let sessionTimeout;

function resetSessionTimeout() {
    clearTimeout(sessionTimeout);
    sessionTimeout = setTimeout(() => {
        alert('Your session has expired. Please login again.');
        window.location.href = 'logout.php';
    }, 30 * 60 * 1000); // 30 minutes
}

// Reset on user activity
['mousedown', 'keydown', 'scroll', 'touchstart'].forEach(event => {
    document.addEventListener(event, resetSessionTimeout);
});
```

---

## User Tiers

Users have different subscription tiers that control access to ML models:

- **Free** - 4 ML models (basic)
- **Starter** - 9 ML models
- **Pro** - 15 ML models
- **Premium** - 20 ML models
- **Ultimate** - ALL 22 ML models

**Access tier:**
```php
$userTier = getUserTier(); // Returns: 'free', 'starter', 'pro', 'premium', 'ultimate'
```

**Display tier badge:**
```html
<span class="badge badge-tier badge-<?php echo strtolower(getUserTier()); ?>">
    <?php echo htmlspecialchars(getUserTier()); ?>
</span>
```

---

## Security Features

### 1. **HTTPS-Only Cookies**
```php
setcookie($name, $value, $expiry, '/', '', true, true);
//                                          ↑     ↑
//                                      secure  httponly
```

### 2. **HTTP-Only Flag**
- Prevents JavaScript access to tokens
- Protects against XSS attacks

### 3. **Session Regeneration**
- New session ID on login
- Prevents session fixation attacks

### 4. **CSRF Protection** (Future)
- Add CSRF tokens to forms
- Validate on backend

### 5. **Password Validation**
- Minimum 8 characters (frontend)
- Backend uses secure hashing (bcrypt)

### 6. **Auto Token Refresh**
- Seamless user experience
- No manual re-login required
- Happens automatically on 401 errors

---

## Testing the Authentication Flow

### Test 1: Unauthenticated Access
1. Open browser in incognito mode
2. Visit `http://your-domain.com/index.php`
3. **Expected:** Redirect to `login_new.php`
4. Try directly accessing `1x2_new.php`
5. **Expected:** Redirect back to `login_new.php`

### Test 2: Registration
1. Visit `register_new.php`
2. Fill in: Full Name, Email, Password
3. Agree to terms
4. Click "Create Account"
5. **Expected:** Account created, auto-logged in, redirect to dashboard

### Test 3: Login
1. Visit `login_new.php`
2. Enter email and password
3. Click "Login"
4. **Expected:** Redirect to dashboard (`1x2_new.php`)

### Test 4: Session Persistence
1. Login successfully
2. Close browser tab (don't close entire browser)
3. Reopen the website
4. **Expected:** Still logged in (cookies persist)

### Test 5: Logout
1. While logged in, click user menu
2. Click "Logout"
3. **Expected:** Redirect to login page
4. Try accessing `1x2_new.php`
5. **Expected:** Redirect back to login page

### Test 6: Auto-Logout
1. Login successfully
2. Wait 30 minutes without any activity
3. **Expected:** Alert about session expiry, redirect to login

---

## How to Protect New Pages

When you create a new page, add this at the top:

```php
<?php
require_once 'config.php';
requireAuth(); // This single line protects the entire page!

// Your page code here...
```

That's it! The page is now protected and only accessible to logged-in users.

---

## Common Issues and Solutions

### Issue 1: "Headers already sent" error
**Cause:** Output before `header()` call
**Solution:** Ensure no whitespace or echo before redirects

### Issue 2: Login successful but still redirected to login
**Cause:** Session not started or cookies blocked
**Solution:**
- Check that `session_start()` is called in `config.php`
- Enable cookies in browser
- Check for cookie domain/path issues

### Issue 3: Auto-logout not working
**Cause:** JavaScript disabled or timer not initialized
**Solution:**
- Ensure `app-footer.php` is included
- Check browser console for errors

### Issue 4: 401 errors even after login
**Cause:** Token not being sent to backend
**Solution:**
- Check that `Authorization: Bearer` header is included
- Verify token is stored in session/cookies
- Check APIClient.php `makeRequest()` method

---

## API Endpoints Used

### Authentication Endpoints

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/v1/auth/register` | POST | No | Create new account |
| `/api/v1/auth/login` | POST | No | Login and get tokens |
| `/api/v1/auth/logout` | POST | Yes | Invalidate tokens |
| `/api/v1/auth/refresh` | POST | No | Get new access token |
| `/api/v1/users/me` | GET | Yes | Get current user info |

### Data Endpoints

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/v1/combined/fixtures/predictions-with-odds` | GET | Yes | Get predictions + odds |
| `/api/v1/leagues/accessible/me` | GET | Yes | Get user's accessible leagues |
| `/api/v1/leagues/tier-info` | GET | No | Get tier information |

---

## Next Steps

### Planned Features

1. **Email Verification**
   - Send verification email on registration
   - Activate account via email link

2. **Password Reset**
   - "Forgot Password" functionality
   - Email-based password reset

3. **Two-Factor Authentication (2FA)**
   - Optional 2FA for enhanced security
   - TOTP or SMS-based codes

4. **Remember Me**
   - Extended session (30 days)
   - Secure persistent login

5. **Social Login**
   - Login with Google
   - Login with Facebook

6. **Admin Panel**
   - User management
   - Subscription management
   - System monitoring

---

## File Checklist

Use this checklist to verify all authentication files are in place:

- [x] `/frontend/index.php` - Entry point
- [x] `/frontend/config.php` - Configuration
- [x] `/frontend/login_new.php` - Login page
- [x] `/frontend/register_new.php` - Registration page
- [x] `/frontend/logout.php` - Logout handler
- [x] `/frontend/1x2_new.php` - Protected dashboard
- [x] `/frontend/includes/auth-header.php` - Auth page header
- [x] `/frontend/includes/auth-footer.php` - Auth page footer
- [x] `/frontend/includes/auth-logo.php` - Logo component
- [x] `/frontend/includes/app-header.php` - App navigation
- [x] `/frontend/includes/app-footer.php` - App footer + JS
- [x] `/frontend/includes/APIClient.php` - API communication

---

## Summary

✅ **Strict Authentication:** NO access without login
✅ **Session Management:** 30-minute auto-logout
✅ **Token Security:** HTTP-only, secure cookies
✅ **Auto Refresh:** Seamless token renewal
✅ **Tier-Based Access:** Control features by subscription
✅ **Simple Protection:** One line to protect any page

**The Result:** A secure, user-friendly authentication system that keeps your football statistics platform safe while providing an excellent user experience.

---

**Last Updated:** 2025-11-16
**Version:** 1.0.0
**Status:** Production Ready
