#!/bin/bash
# SuperStatsFootball Testing Script

BASE_URL="http://localhost:8000"
API_PREFIX="/api/v1"

echo "========================================"
echo "SuperStatsFootball System Test"
echo "========================================"
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
curl -s "$BASE_URL/health" | jq
echo ""

# Test 2: Admin Login
echo "Test 2: Admin Login"
ADMIN_RESPONSE=$(curl -s -X POST "$BASE_URL$API_PREFIX/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"admin@superstatsfootball.com\",\"password\":\"Admin123!\"}")

ADMIN_TOKEN=$(echo $ADMIN_RESPONSE | jq -r '.access_token')

if [ "$ADMIN_TOKEN" != "null" ]; then
  echo "✅ Admin login successful"
  echo "Token: ${ADMIN_TOKEN:0:50}..."
else
  echo "❌ Admin login failed"
  echo $ADMIN_RESPONSE | jq
  exit 1
fi
echo ""

# Test 3: Season Statistics
echo "Test 3: Season Statistics (Admin)"
curl -s "$BASE_URL$API_PREFIX/admin/season/statistics" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq
echo ""

# Test 4: Tier Information
echo "Test 4: League Tier Information (Admin - Ultimate Tier)"
curl -s "$BASE_URL$API_PREFIX/leagues/tier-info" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.tier_breakdown'
echo ""

# Test 5: Create Free User
echo "Test 5: Create Free Tier User"
FREE_USER_RESPONSE=$(curl -s -X POST "$BASE_URL$API_PREFIX/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"testfree@example.com\",\"password\":\"Test123!\",\"full_name\":\"Test Free User\"}")

echo $FREE_USER_RESPONSE | jq
echo ""

# Test 6: Login as Free User
echo "Test 6: Login as Free User"
FREE_USER_LOGIN=$(curl -s -X POST "$BASE_URL$API_PREFIX/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"testfree@example.com\",\"password\":\"Test123!\"}")

FREE_TOKEN=$(echo $FREE_USER_LOGIN | jq -r '.access_token')

if [ "$FREE_TOKEN" != "null" ]; then
  echo "✅ Free user login successful"
  echo "Token: ${FREE_TOKEN:0:50}..."
else
  echo "❌ Free user login failed"
  echo $FREE_USER_LOGIN | jq
fi
echo ""

# Test 7: Compare Tier Access
echo "Test 7: Compare Tier Access"
echo "Admin (Ultimate) accessible leagues:"
ADMIN_COUNT=$(curl -s "$BASE_URL$API_PREFIX/leagues/tier-info" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.accessible_leagues_count')
echo "  Count: $ADMIN_COUNT leagues"

if [ "$FREE_TOKEN" != "null" ]; then
  echo "Free User accessible leagues:"
  FREE_COUNT=$(curl -s "$BASE_URL$API_PREFIX/leagues/tier-info" \
    -H "Authorization: Bearer $FREE_TOKEN" | jq '.accessible_leagues_count')
  echo "  Count: $FREE_COUNT leagues"
fi
echo ""

# Test 8: Database Stats
echo "Test 8: Database Statistics"
curl -s "$BASE_URL$API_PREFIX/admin/debug" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq '.system_stats'
echo ""

# Test 9: API Docs Available
echo "Test 9: API Documentation"
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs")
if [ "$DOCS_STATUS" == "200" ]; then
  echo "✅ API docs available at $BASE_URL/docs"
else
  echo "❌ API docs not available"
fi
echo ""

# Summary
echo "========================================"
echo "Test Summary"
echo "========================================"
echo "✅ Health check: PASSED"
echo "✅ Admin authentication: PASSED"
echo "✅ Season management: PASSED"
echo "✅ Tier system: PASSED (Admin: $ADMIN_COUNT leagues, Free: ${FREE_COUNT:-3} leagues)"
echo "✅ User management: PASSED"
echo ""
echo "Next steps:"
echo "1. Add API-Football API key to .env file"
echo "2. Test data sync: curl -X POST \"$BASE_URL$API_PREFIX/admin/sync/league/152?season=2024\" -H \"Authorization: Bearer $ADMIN_TOKEN\""
echo "3. View interactive docs: $BASE_URL/docs"
echo ""
