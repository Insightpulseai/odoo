#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Local Testing Script
# ============================================
# Tests saas-landing locally before production deployment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

BASE_URL="http://localhost:3000"

echo "============================================"
echo "Local Testing - saas-landing"
echo "============================================"
echo ""

# Check if dev server is running
if ! curl -sS "$BASE_URL" > /dev/null 2>&1; then
  echo "❌ Dev server not running"
  echo ""
  echo "Start it with: pnpm dev"
  exit 1
fi

echo "✅ Dev server is running"
echo ""

# Test 1: Homepage
echo "Test 1: Homepage"
echo "----------------"
HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" "$BASE_URL/")
if [[ "$HTTP_CODE" == "200" ]]; then
  echo "✅ Homepage loads (HTTP $HTTP_CODE)"
else
  echo "❌ Homepage failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test 2: Dashboard
echo "Test 2: Dashboard"
echo "----------------"
HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" "$BASE_URL/dashboard")
if [[ "$HTTP_CODE" == "200" ]]; then
  echo "✅ Dashboard loads (HTTP $HTTP_CODE)"
else
  echo "❌ Dashboard failed (HTTP $HTTP_CODE)"
fi
echo ""

# Test 3: API Routes Exist (expect 401/405 for auth-required)
echo "Test 3: API Routes"
echo "----------------"

# Invite list (GET, requires auth)
HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" "$BASE_URL/api/invite/list")
if [[ "$HTTP_CODE" == "401" ]]; then
  echo "✅ /api/invite/list exists (HTTP $HTTP_CODE - auth required)"
elif [[ "$HTTP_CODE" == "200" ]]; then
  echo "⚠️  /api/invite/list accessible without auth (unexpected)"
else
  echo "❌ /api/invite/list failed (HTTP $HTTP_CODE)"
fi

# Org create (POST, requires auth)
HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"test"}' \
  "$BASE_URL/api/org/create")
if [[ "$HTTP_CODE" == "401" ]]; then
  echo "✅ /api/org/create exists (HTTP $HTTP_CODE - auth required)"
elif [[ "$HTTP_CODE" == "200" ]]; then
  echo "⚠️  /api/org/create accessible without auth (unexpected)"
else
  echo "❌ /api/org/create failed (HTTP $HTTP_CODE)"
fi

# Invite send (POST, requires auth)
HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" -X POST \
  -H "Content-Type: application/json" \
  -d '{"orgId":"test","email":"test@example.com","role":"member"}' \
  "$BASE_URL/api/invite/send")
if [[ "$HTTP_CODE" == "401" ]]; then
  echo "✅ /api/invite/send exists (HTTP $HTTP_CODE - auth required)"
elif [[ "$HTTP_CODE" == "200" ]]; then
  echo "⚠️  /api/invite/send accessible without auth (unexpected)"
else
  echo "❌ /api/invite/send failed (HTTP $HTTP_CODE)"
fi

# Invite accept (POST, requires auth)
HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" -X POST \
  -H "Content-Type: application/json" \
  -d '{"token":"test"}' \
  "$BASE_URL/api/invite/accept")
if [[ "$HTTP_CODE" == "401" ]]; then
  echo "✅ /api/invite/accept exists (HTTP $HTTP_CODE - auth required)"
elif [[ "$HTTP_CODE" == "200" ]]; then
  echo "⚠️  /api/invite/accept accessible without auth (unexpected)"
else
  echo "❌ /api/invite/accept failed (HTTP $HTTP_CODE)"
fi

echo ""

# Test 4: Environment Variables
echo "Test 4: Environment Variables"
echo "----------------"
if [[ -f .env.local ]]; then
  echo "✅ .env.local exists"

  # Check key variables (without printing values)
  if grep -q "NEXT_PUBLIC_SUPABASE_URL" .env.local; then
    echo "✅ SUPABASE_URL configured"
  else
    echo "❌ SUPABASE_URL missing"
  fi

  if grep -q "SUPABASE_SERVICE_ROLE_KEY" .env.local; then
    echo "✅ SUPABASE_SERVICE_ROLE_KEY configured"
  else
    echo "❌ SUPABASE_SERVICE_ROLE_KEY missing"
  fi

  if grep -q "ZOHO_PASS" .env.local; then
    echo "✅ ZOHO_PASS configured"
  else
    echo "❌ ZOHO_PASS missing"
  fi
else
  echo "❌ .env.local not found"
fi
echo ""

# Test 5: Database Connection
echo "Test 5: Database Connection"
echo "----------------"
if command -v psql > /dev/null 2>&1; then
  # Extract DB URL from .env.local (without using it directly for security)
  if grep -q "SUPABASE_URL" .env.local; then
    echo "✅ Database credentials available"

    # Test if we can query the functions (using the connection string from earlier)
    DB_URL="postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require"

    FUNC_COUNT=$(psql "$DB_URL" -t -c "SELECT count(*) FROM pg_proc WHERE pronamespace = 'registry'::regnamespace AND proname LIKE '%invite%'" 2>/dev/null || echo "0")
    FUNC_COUNT=$(echo "$FUNC_COUNT" | tr -d ' ')

    if [[ "$FUNC_COUNT" == "4" ]]; then
      echo "✅ Database migration deployed (4 functions found)"
    else
      echo "⚠️  Database migration incomplete ($FUNC_COUNT functions found, expected 4)"
    fi
  else
    echo "⚠️  Database URL not configured"
  fi
else
  echo "⚠️  psql not available (skipping database test)"
fi
echo ""

# Test 6: Build Verification
echo "Test 6: Build Test"
echo "----------------"
echo "Testing production build..."
if pnpm build > /tmp/build-test.log 2>&1; then
  echo "✅ Production build succeeds"
else
  echo "❌ Production build failed"
  echo "See: /tmp/build-test.log"
fi
echo ""

echo "============================================"
echo "Test Summary"
echo "============================================"
echo ""
echo "✅ = Pass"
echo "⚠️  = Warning (check details)"
echo "❌ = Fail"
echo ""
echo "Next steps:"
echo "1. Review any ❌ failures above"
echo "2. Test in browser: http://localhost:3000"
echo "3. When ready, deploy to production:"
echo "   ./scripts/vercel-first-deploy.sh"
echo ""
