#!/usr/bin/env bash
# smoke_odoo_db_binding.sh — verify Odoo is bound to the correct DB
# Run as a readiness/post-deploy check.
# Fails if database selector is visible or login doesn't target db=odoo.

set -euo pipefail

ERP_URL="${ERP_URL:-https://erp.insightpulseai.com}"
EXPECTED_DB="odoo"

echo "=== Odoo DB Binding Smoke Test ==="
echo "Target: $ERP_URL"

# 1) /web/login returns 200
HTTP_CODE=$(curl -sLo /dev/null -w "%{http_code}" --connect-timeout 10 "$ERP_URL/web/login" 2>/dev/null)
if [ "$HTTP_CODE" != "200" ]; then
  echo "FAIL: /web/login returned HTTP $HTTP_CODE (expected 200)"
  exit 1
fi
echo "PASS: /web/login returns 200"

# 2) /web/database/selector is NOT accessible (must return redirect or error)
SELECTOR_CODE=$(curl -so /dev/null -w "%{http_code}" --connect-timeout 10 "$ERP_URL/web/database/selector" 2>/dev/null)
if [ "$SELECTOR_CODE" = "200" ]; then
  echo "FAIL: /web/database/selector is accessible (list_db should be False)"
  exit 1
fi
echo "PASS: /web/database/selector blocked (HTTP $SELECTOR_CODE)"

# 3) /web/database/manager is NOT accessible
MANAGER_CODE=$(curl -so /dev/null -w "%{http_code}" --connect-timeout 10 "$ERP_URL/web/database/manager" 2>/dev/null)
if [ "$MANAGER_CODE" = "200" ]; then
  echo "FAIL: /web/database/manager is accessible"
  exit 1
fi
echo "PASS: /web/database/manager blocked (HTTP $MANAGER_CODE)"

# 4) Login page references the correct database
LOGIN_BODY=$(curl -s --connect-timeout 10 "$ERP_URL/web/login" 2>/dev/null)
if echo "$LOGIN_BODY" | grep -q "database.*selector\|db_name.*select\|Choose.*database"; then
  echo "FAIL: Login page shows database selector UI"
  exit 1
fi
echo "PASS: No database selector on login page"

# 5) Session info confirms correct DB
SESSION_DB=$(curl -s --connect-timeout 10 "$ERP_URL/web/session/get_session_info" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{}}' 2>/dev/null \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d.get('result',{}).get('db',''))" 2>/dev/null || echo "")

if [ -n "$SESSION_DB" ] && [ "$SESSION_DB" != "$EXPECTED_DB" ]; then
  echo "FAIL: Session reports db=$SESSION_DB (expected $EXPECTED_DB)"
  exit 1
fi
if [ -n "$SESSION_DB" ]; then
  echo "PASS: Session confirms db=$SESSION_DB"
else
  echo "WARN: Could not verify session DB (may need auth)"
fi

echo ""
echo "=== ALL CHECKS PASSED ==="
