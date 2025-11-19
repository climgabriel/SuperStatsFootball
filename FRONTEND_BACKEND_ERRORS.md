# Frontend-Backend Integration Error Report

**Generated:** 2025-11-19
**Frontend Repository:** https://github.com/climgabriel/SuperStatsFootballw.git
**Backend Repository:** Current (SuperStatsFootball)

---

## 🔴 CRITICAL ERRORS (Breaking Issues)

### 1. API Endpoint Mismatches

#### ❌ Error 1.1: User Profile Endpoint Mismatch
**Severity:** CRITICAL
**Status:** 🔴 BROKEN

**Frontend Calls:**
- `GET /api/v1/users/me` (APIClient.php:160)

**Backend Provides:**
- `GET /api/v1/users/profile` (backend/app/routers/users.py:11)

**Impact:**
- User profile fetching will fail with 404 Not Found
- Frontend cannot retrieve current user information after login

**Fix Required:**
1. **Option A (Recommended):** Update frontend to use `/users/profile`
   - Change line 160 in `/tmp/frontend-repo/includes/APIClient.php`
   ```php
   // FROM:
   return $this->makeRequest('GET', '/users/me', null, true);

   // TO:
   return $this->makeRequest('GET', '/users/profile', null, true);
   ```

2. **Option B:** Add alias endpoint in backend
   ```python
   @router.get("/me", response_model=UserResponse)  # Alias
   @router.get("/profile", response_model=UserResponse)
   async def get_profile(current_user: User = Depends(get_current_active_user)):
       return current_user
   ```

---

#### ❌ Error 1.2: Authentication "Me" Endpoint Missing
**Severity:** CRITICAL
**Status:** 🔴 BROKEN

**Frontend Config:**
- `'auth_me' => API_PREFIX . '/auth/me'` (api-config.php:29)
- Called by `getCurrentUserInfo()` (ApiRepository.php:405)

**Backend Reality:**
- Endpoint does NOT exist
- Available auth endpoints: `/register`, `/login`, `/refresh`, `/logout`

**Impact:**
- Any call to get current user info via auth endpoint will fail with 404
- Breaking error if frontend uses ApiRepository.getCurrentUserInfo()

**Fix Required:**
1. **Option A (Recommended):** Remove `/auth/me` from frontend config and use `/users/profile` instead
   ```php
   // In api-config.php, REMOVE line 29:
   // 'auth_me' => API_PREFIX . '/auth/me',

   // In ApiRepository.php line 405, change to:
   public function getCurrentUserInfo() {
       return $this->request(API_BASE_URL . '/api/v1/users/profile', 'GET', null, [], false);
   }
   ```

2. **Option B:** Add `/auth/me` endpoint in backend (redirects to user profile)
   ```python
   # In backend/app/routers/auth.py
   @router.get("/me", response_model=UserResponse)
   async def get_current_user_auth(current_user: User = Depends(get_current_active_user)):
       """Get current authenticated user (auth alias)."""
       return current_user
   ```

---

#### ❌ Error 1.3: Offsides Statistics Endpoint Mismatch
**Severity:** CRITICAL
**Status:** 🔴 BROKEN

**Frontend Calls:**
- `GET /api/v1/statistics/offs` (api-config.php:37)

**Backend Provides:**
- `GET /api/v1/statistics/offsides` (backend/app/routers/statistics.py:370)

**Impact:**
- Offsides statistics page will fail with 404
- No data displayed on offsides page

**Fix Required:**
1. **Option A (Recommended):** Update frontend endpoint name
   ```php
   // In api-config.php line 37:
   // FROM:
   'stats_offsides' => API_PREFIX . '/statistics/offs',

   // TO:
   'stats_offsides' => API_PREFIX . '/statistics/offsides',
   ```

2. **Option B:** Add route alias in backend
   ```python
   # In backend/app/routers/statistics.py
   @router.get("/offs", response_model=OffsListResponse)  # Alias
   @router.get("/offsides", response_model=OffsListResponse)
   async def get_offsides_statistics(...):
       # existing implementation
   ```

---

### 2. Missing Response Fields in User Data

#### ❌ Error 2.1: Missing "role" Field
**Severity:** HIGH
**Status:** 🟡 DEGRADED

**Frontend Expects:**
```php
// UserManager.php:150
return $user['role'] ?? self::ROLE_USER;  // Expects 'role' field
```

**Backend Returns (UserResponse schema):**
```python
# backend/app/schemas/user.py:36-43
class UserResponse(UserBase):
    id: str
    tier: str                    # ❌ No 'role' field
    subscription_status: str
    created_at: datetime
```

**Impact:**
- Frontend cannot distinguish between regular users and admins
- Role-based access control (RBAC) broken on frontend
- UserManager.isAdmin() always returns false
- Admin features inaccessible

**Fix Required:**

**Option A (Recommended):** Add `role` field to backend UserResponse
```python
# In backend/app/schemas/user.py
class UserResponse(UserBase):
    id: str
    tier: str
    role: str = "user"  # NEW: Add role field (default "user")
    subscription_status: str
    created_at: datetime

    @property
    def role(self) -> str:
        """Derive role from tier."""
        return "admin" if self.tier == "ultimate" else "user"
```

**Option B:** Update frontend to derive role from tier
```php
// In UserManager.php
public static function getUserRole() {
    $user = $_SESSION[SESSION_USER_KEY] ?? null;
    if (!$user) return self::ROLE_USER;

    // Derive role from tier
    $tier = $user['tier'] ?? 'free';
    return ($tier === 'ultimate') ? self::ROLE_ADMIN : self::ROLE_USER;
}
```

---

#### ❌ Error 2.2: Missing "plan" Field
**Severity:** HIGH
**Status:** 🟡 DEGRADED

**Frontend Expects:**
```php
// UserManager.php:165
return $user['plan'] ?? self::PLAN_FREE;  // Expects numeric plan (1-5)
```

**Backend Returns:**
```python
# Backend uses string 'tier' instead: "free", "starter", "pro", "premium", "ultimate"
tier: str  # NOT a numeric plan
```

**Impact:**
- UserManager.getUserPlan() returns default PLAN_FREE for all users
- Plan-based feature restrictions not enforced
- Subscription plan display broken
- Users can't see their actual subscription level

**Mapping:**
```
Frontend Plans          Backend Tiers
--------------          -------------
1 (PLAN_FREE)      <->  "free"
2 (PLAN_BASIC)     <->  "starter"
3 (PLAN_STANDARD)  <->  "pro"
4 (PLAN_PREMIUM)   <->  "premium"
5 (PLAN_ULTIMATE)  <->  "ultimate"
```

**Fix Required:**

**Option A (Recommended):** Add computed `plan` field to backend response
```python
# In backend/app/schemas/user.py
class UserResponse(UserBase):
    id: str
    tier: str
    subscription_status: str
    created_at: datetime

    @property
    def plan(self) -> int:
        """Convert tier to numeric plan."""
        tier_to_plan = {
            "free": 1,
            "starter": 2,
            "pro": 3,
            "premium": 4,
            "ultimate": 5
        }
        return tier_to_plan.get(self.tier, 1)
```

**Option B:** Update frontend to map tier to plan
```php
// In UserManager.php
public static function getUserPlan() {
    $user = $_SESSION[SESSION_USER_KEY] ?? null;
    if (!$user) return self::PLAN_FREE;

    // Map tier to plan
    $tierToPlan = [
        'free' => self::PLAN_FREE,
        'starter' => self::PLAN_BASIC,
        'pro' => self::PLAN_STANDARD,
        'premium' => self::PLAN_PREMIUM,
        'ultimate' => self::PLAN_ULTIMATE
    ];

    $tier = $user['tier'] ?? 'free';
    return $tierToPlan[$tier] ?? self::PLAN_FREE;
}
```

---

## 🟡 MEDIUM PRIORITY ISSUES

### 3. Data Type Inconsistencies

#### ⚠️ Issue 3.1: Statistics Response Structure Differs
**Severity:** MEDIUM

**Frontend Expects (based on PHP pages):**
```php
// Flat structure with direct probability fields
[
    'fixture_id' => string,
    'bts_ht_yes' => float,      // 0.0-1.0
    'goals_ft_u25' => float,
    'bookmaker_u25' => string,  // "2.10"
]
```

**Backend Returns (actual schema):**
```python
# Nested structure
class GoalsStatisticsResponse(BaseModel):
    fixture_id: int  # ❌ int, not string
    league_name: str
    match_date: datetime
    home_team: str
    away_team: str
    status: str
    goals_stats: GoalsStats  # ❌ Nested object

class GoalsStats(BaseModel):
    over_under_2_5: dict  # ❌ dict, not flat fields
    over_under_1_5: dict
    btts: dict
```

**Impact:**
- Frontend may need to navigate nested structures
- Field access patterns differ from expectations
- Possible JavaScript/PHP errors when accessing non-existent flat fields

**Fix:**
- Document actual response structure
- Update frontend to access nested fields: `response.goals_stats.over_under_2_5`

---

#### ⚠️ Issue 3.2: fixture_id Type Mismatch
**Severity:** MEDIUM

**Frontend:**
```php
'fixture_id' => string  // Treated as string in PHP
```

**Backend:**
```python
fixture_id: int  # Integer in Pydantic models
```

**Impact:**
- Type coercion may cause issues
- String comparisons vs integer comparisons
- Potential bugs in fixture lookups

**Fix:**
- Ensure consistent integer handling on frontend
- Cast to int when needed: `(int)$fixture['fixture_id']`

---

### 4. Configuration & CORS

#### ✅ CORS Configuration: OK
**Status:** 🟢 WORKING

**Backend Allows:**
```python
BACKEND_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://*.greengeeksclient.com",
    "https://superstatsfootball.com",
    "https://www.superstatsfootball.com",
    "*"  # All origins (development)
]
```

**Frontend Hosted:**
- GreenGeeks: Covered by wildcard pattern
- Production: Explicitly allowed
- Development: `*` allows all

**Note:** Remove `"*"` in production for security

---

#### ⚠️ Issue 4.1: API Base URL Environment Variables
**Severity:** LOW

**Frontend checks (in order):**
1. `API_BASE_URL` env var (GreenGeeks)
2. `BACKEND_API_URL` env var (local dev)
3. Default: `https://superstatsfootball-production.up.railway.app`

**Recommendation:**
- Ensure GreenGeeks environment has `API_BASE_URL` set correctly
- Verify Railway URL is still active and correct
- Add health check to verify connectivity

---

## 🟢 WORKING CORRECTLY

### ✅ Authentication Flow
**Status:** 🟢 WORKING (with fixes above)

- JWT token generation: ✅ Working
- Token refresh: ✅ Working
- Session management: ✅ Working
- Cookie security: ✅ HTTP-only, Secure flag enabled

### ✅ Statistics Endpoints
**Status:** 🟢 WORKING (except offsides)

All statistics endpoints working:
- ✅ `/statistics/goals` - Working
- ✅ `/statistics/corners` - Working
- ✅ `/statistics/cards` - Working
- ✅ `/statistics/shots` - Working
- ✅ `/statistics/fouls` - Working
- ❌ `/statistics/offs` - BROKEN (should be `/offsides`)

### ✅ Combined Predictions Endpoint
**Status:** 🟢 WORKING

- ✅ `/combined/fixtures/predictions-with-odds` - Working
- Frontend correctly calls this endpoint
- Response structure matches expectations

---

## 📋 PRIORITY FIX CHECKLIST

### Immediate (Critical - Breaks Functionality)
- [ ] **Fix 1.1:** Change `/users/me` → `/users/profile` in frontend
- [ ] **Fix 1.2:** Remove `/auth/me`, use `/users/profile` instead
- [ ] **Fix 1.3:** Change `/statistics/offs` → `/statistics/offsides`

### High Priority (Degrades Features)
- [ ] **Fix 2.1:** Add `role` field to UserResponse or map tier→role
- [ ] **Fix 2.2:** Add `plan` field to UserResponse or map tier→plan

### Medium Priority (Improves Compatibility)
- [ ] **Fix 3.1:** Document nested response structures
- [ ] **Fix 3.2:** Ensure consistent fixture_id integer handling

### Low Priority (Maintenance)
- [ ] **Fix 4.1:** Verify environment variables on GreenGeeks
- [ ] Remove `"*"` from CORS origins in production
- [ ] Add API health check endpoint monitoring

---

## 🛠️ RECOMMENDED IMPLEMENTATION APPROACH

### Backend Changes (Recommended)
Add compatibility layer for frontend expectations:

```python
# In backend/app/schemas/user.py
from pydantic import computed_field

class UserResponse(UserBase):
    id: str
    tier: str
    subscription_status: str
    created_at: datetime

    @computed_field
    @property
    def role(self) -> str:
        """Derive role from tier for frontend compatibility."""
        return "admin" if self.tier == "ultimate" else "user"

    @computed_field
    @property
    def plan(self) -> int:
        """Convert tier to numeric plan for frontend compatibility."""
        tier_to_plan = {
            "free": 1,
            "starter": 2,
            "pro": 3,
            "premium": 4,
            "ultimate": 5
        }
        return tier_to_plan.get(self.tier, 1)
```

### Frontend Changes (Required)
Update API endpoint paths:

```php
// In includes/api-config.php
define('API_ENDPOINTS', [
    // Authentication
    'auth_login' => API_PREFIX . '/auth/login',
    'auth_register' => API_PREFIX . '/auth/register',
    // REMOVE: 'auth_me' => API_PREFIX . '/auth/me',

    // Users - FIXED
    'user_profile' => API_PREFIX . '/users/profile',  // NEW

    // Statistics - FIXED
    'stats_offsides' => API_PREFIX . '/statistics/offsides',  // was: /offs

    // ... rest unchanged
]);
```

```php
// In includes/APIClient.php line 160
public function getUserProfile() {
    return $this->makeRequest('GET', '/users/profile', null, true);  // was: /users/me
}
```

```php
// In includes/ApiRepository.php line 405
public function getCurrentUserInfo() {
    return $this->request(API_BASE_URL . '/api/v1/users/profile', 'GET', null, [], false);
}
```

---

## 📊 ERROR SUMMARY

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| Endpoint Mismatches | 3 | 0 | 0 | 0 | 3 |
| Missing Fields | 0 | 2 | 0 | 0 | 2 |
| Type Inconsistencies | 0 | 0 | 2 | 0 | 2 |
| Configuration | 0 | 0 | 0 | 1 | 1 |
| **TOTAL** | **3** | **2** | **2** | **1** | **8** |

**Blocking Issues:** 3
**Non-Blocking Issues:** 5
**Working Correctly:** 10+ features

---

## 🎯 NEXT STEPS

1. **Immediate:** Fix 3 critical endpoint mismatches (frontend changes)
2. **Today:** Add role/plan computed fields to backend UserResponse
3. **This Week:** Test all statistics endpoints with corrected paths
4. **Ongoing:** Monitor logs for 404 errors on the fixed endpoints

---

**Report End**
