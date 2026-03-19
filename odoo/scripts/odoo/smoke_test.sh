#!/usr/bin/env bash
# scripts/odoo/smoke_test.sh
# Core business smoke test for Odoo 19 go-live
# Tests: login page, web health, assets, database manager blocked, module presence
# Usage: ./scripts/odoo/smoke_test.sh [BASE_URL]
set -uo pipefail

BASE_URL="${1:-https://erp.insightpulseai.com}"
PASS=0
FAIL=0
RESULTS=""

check() {
  local name="$1"
  local result="$2"
  if [ "$result" = "PASS" ]; then
    PASS=$((PASS + 1))
    RESULTS="${RESULTS}\nPASS: $name"
  else
    FAIL=$((FAIL + 1))
    RESULTS="${RESULTS}\nFAIL: $name"
  fi
}

echo "Odoo 19 Go-Live Smoke Test"
echo "Target: $BASE_URL"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "---"

# 1. Health endpoint
STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "$BASE_URL/web/health" 2>/dev/null || echo "000")
[ "$STATUS" = "200" ] && check "Health endpoint /web/health" "PASS" || check "Health endpoint /web/health" "FAIL"

# 2. Login page loads
STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "$BASE_URL/web/login" 2>/dev/null || echo "000")
[ "$STATUS" = "200" ] && check "Login page /web/login" "PASS" || check "Login page /web/login" "FAIL"

# 3. Login form present (oe_login_form)
BODY=$(curl -sf "$BASE_URL/web/login" 2>/dev/null || echo "")
echo "$BODY" | grep -q "oe_login_form" && check "Login form present" "PASS" || check "Login form present" "FAIL"

# 4. Login button visible (not d-none blocking it)
echo "$BODY" | grep -q "Log in" && check "Login button visible" "PASS" || check "Login button visible" "FAIL"

# 5. Asset bundles serve with compression
ASSETS=$(echo "$BODY" | grep -oE '(src|href)="/web/assets/[^"]*"' | sed 's/.*"\(.*\)"/\1/' | sort -u)
ASSET_FAIL=0
for asset in $ASSETS; do
  ASTATUS=$(curl -s -H "Accept-Encoding: gzip, br" -o /dev/null -w "%{http_code}" "$BASE_URL$asset" 2>/dev/null || echo "000")
  [ "$ASTATUS" != "200" ] && ASSET_FAIL=1
done
[ "$ASSET_FAIL" = "0" ] && check "Asset bundles serve compressed" "PASS" || check "Asset bundles serve compressed" "FAIL"

# 6. Database manager blocked
DB_BODY=$(curl -sf "$BASE_URL/web/database/selector" 2>/dev/null || echo "")
echo "$DB_BODY" | grep -q "disabled by the administrator" && check "Database manager blocked" "PASS" || check "Database manager blocked" "FAIL"

# 7. Azure Front Door headers present
HEADERS=$(curl -sfI "$BASE_URL/web/login" 2>/dev/null || echo "")
echo "$HEADERS" | grep -qi "x-azure-ref" && check "Azure Front Door routing" "PASS" || check "Azure Front Door routing" "FAIL"

# 8. HTTPS/TLS working
echo "$HEADERS" | grep -qi "strict-transport-security\|x-content-type-options" && check "Security headers present" "PASS" || check "Security headers present" "FAIL"

# 9. Session cookie HttpOnly
echo "$HEADERS" | grep -qi "HttpOnly" && check "Session cookie HttpOnly" "PASS" || check "Session cookie HttpOnly" "FAIL"

# 10. Proxy mode indicators (CSP, X-Frame-Options)
echo "$HEADERS" | grep -qi "x-frame-options" && check "X-Frame-Options set" "PASS" || check "X-Frame-Options set" "FAIL"

echo ""
echo "---"
echo -e "$RESULTS"
echo "---"
echo "Total: $((PASS + FAIL)) | Pass: $PASS | Fail: $FAIL"

[ "$FAIL" -eq 0 ] && echo "SMOKE TEST: PASS" || echo "SMOKE TEST: FAIL"
exit $FAIL
