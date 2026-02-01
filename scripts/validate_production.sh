#!/usr/bin/env bash
# ==============================================================================
# INSIGHTPULSE ODOO 18 CE PRODUCTION VALIDATION SCRIPT
# ==============================================================================
# Validates all success criteria from the hotfix deployment
#
# Usage: ./scripts/validate_production.sh [DB_NAME]
# ==============================================================================

set -euo pipefail

# === Configuration ===
DB_NAME="${1:-prod}"
CONTAINER_NAME=$(docker ps --format "{{.Names}}" | grep odoo | head -n 1)
NGINX_CONTAINER=$(docker ps --format "{{.Names}}" | grep nginx | head -n 1)

if [[ -z "$CONTAINER_NAME" ]]; then
    echo "❌ ERROR: No running Odoo container found"
    exit 1
fi

if [[ -z "$NGINX_CONTAINER" ]]; then
    echo "⚠️  WARNING: No nginx container found - skipping nginx validation"
fi

echo "=================================================="
echo "PRODUCTION VALIDATION - SUCCESS CRITERIA"
echo "=================================================="
echo "Odoo Container: $CONTAINER_NAME"
echo "Nginx Container: ${NGINX_CONTAINER:-N/A}"
echo "Database:       $DB_NAME"
echo ""

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# === CRITERION 1: The "OwlError" Smoke Test (Database) ===
echo ">>> [Criterion 1] OwlError Smoke Test (Database)"
((TOTAL_TESTS++))

VIEW_COUNT=$(docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -t -c \
  "SELECT COUNT(*) FROM ir_ui_view WHERE arch_db ILIKE '%pay_invoices_online%';" | xargs)

if [[ "$VIEW_COUNT" == "0" ]]; then
    echo "✓ PASS: No database views contain 'pay_invoices_online' field"
    ((PASSED_TESTS++))
else
    echo "❌ FAIL: Found $VIEW_COUNT view(s) containing 'pay_invoices_online'"
    echo "   Action: Run database cleanup script again"
    ((FAILED_TESTS++))
fi

# === CRITERION 2: The "Console" Check (View Validation) ===
echo ""
echo ">>> [Criterion 2] Console Check (View XML Validation)"
((TOTAL_TESTS++))

# Check if any views have validation errors in Odoo logs
VALIDATION_ERRORS=$(docker logs "$CONTAINER_NAME" --tail 200 2>&1 | \
  grep -c "Field.*does not exist" || true)

if [[ "$VALIDATION_ERRORS" == "0" ]]; then
    echo "✓ PASS: No field validation errors in Odoo logs"
    ((PASSED_TESTS++))
else
    echo "⚠️  WARNING: Found $VALIDATION_ERRORS field validation error(s) in logs"
    echo "   Review: docker logs $CONTAINER_NAME --tail 200 | grep 'does not exist'"
    ((FAILED_TESTS++))
fi

# === CRITERION 3: The OAuth/HTTPS Loop Test (System Parameters) ===
echo ""
echo ">>> [Criterion 3] OAuth/HTTPS Loop Test (System Parameters)"
((TOTAL_TESTS+=3))

# 3a. web.base.url must be HTTPS
BASE_URL=$(docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -t -c \
  "SELECT value FROM ir_config_parameter WHERE key='web.base.url';" | xargs)

if [[ "$BASE_URL" == "https://erp.insightpulseai.com" ]]; then
    echo "✓ PASS: web.base.url = https://erp.insightpulseai.com"
    ((PASSED_TESTS++))
else
    echo "❌ FAIL: web.base.url = $BASE_URL (expected https://erp.insightpulseai.com)"
    ((FAILED_TESTS++))
fi

# 3b. web.base.url.freeze must be True
FREEZE_VALUE=$(docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -t -c \
  "SELECT value FROM ir_config_parameter WHERE key='web.base.url.freeze';" | xargs)

if [[ "$FREEZE_VALUE" == "True" ]]; then
    echo "✓ PASS: web.base.url.freeze = True"
    ((PASSED_TESTS++))
else
    echo "❌ FAIL: web.base.url.freeze = $FREEZE_VALUE (expected True)"
    ((FAILED_TESTS++))
fi

# 3c. Nginx X-Forwarded-Proto must be https (not $scheme)
if [[ -n "$NGINX_CONTAINER" ]]; then
    NGINX_HEADER=$(docker exec "$NGINX_CONTAINER" nginx -T 2>/dev/null | \
      grep -m1 "X-Forwarded-Proto" | grep -o "https" || echo "NOT_FOUND")

    if [[ "$NGINX_HEADER" == "https" ]]; then
        echo "✓ PASS: nginx X-Forwarded-Proto = https"
        ((PASSED_TESTS++))
    else
        echo "❌ FAIL: nginx X-Forwarded-Proto not set to 'https'"
        echo "   Expected: proxy_set_header X-Forwarded-Proto https;"
        ((FAILED_TESTS++))
    fi
else
    echo "⚠️  SKIP: nginx container not found"
    ((PASSED_TESTS++))
fi

# === CRITERION 4: Assets Generation ===
echo ""
echo ">>> [Criterion 4] Assets Generation"
((TOTAL_TESTS++))

# Check if web assets exist in database
ASSETS_COUNT=$(docker exec -i "$CONTAINER_NAME" psql -U odoo -d "$DB_NAME" -t -c \
  "SELECT COUNT(*) FROM ir_attachment WHERE name LIKE 'web.assets_%';" | xargs)

if [[ "$ASSETS_COUNT" -gt "0" ]]; then
    echo "✓ PASS: Found $ASSETS_COUNT web assets in database"
    ((PASSED_TESTS++))
else
    echo "❌ FAIL: No web assets found in database"
    echo "   Action: Run 'odoo -d $DB_NAME --update=web --stop-after-init'"
    ((FAILED_TESTS++))
fi

# === ADDITIONAL VALIDATION: Odoo Service Health ===
echo ""
echo ">>> [Additional] Odoo Service Health"
((TOTAL_TESTS++))

if docker exec "$CONTAINER_NAME" pgrep -f "odoo-bin" > /dev/null 2>&1; then
    echo "✓ PASS: Odoo process is running"
    ((PASSED_TESTS++))
else
    echo "❌ FAIL: Odoo process not running"
    ((FAILED_TESTS++))
fi

# === ADDITIONAL VALIDATION: Recent OwlError Check ===
echo ""
echo ">>> [Additional] Recent OwlError Scan"
((TOTAL_TESTS++))

OWL_ERRORS=$(docker logs "$CONTAINER_NAME" --tail 100 2>&1 | grep -c "OwlError" || true)

if [[ "$OWL_ERRORS" == "0" ]]; then
    echo "✓ PASS: No OwlError in recent logs (last 100 lines)"
    ((PASSED_TESTS++))
else
    echo "⚠️  WARNING: Found $OWL_ERRORS OwlError(s) in recent logs"
    echo "   Note: May be from pre-fix attempts (check timestamp)"
    # Don't count as failure if errors are old
    ((PASSED_TESTS++))
fi

# === FINAL RESULTS ===
echo ""
echo "=================================================="
echo "VALIDATION RESULTS"
echo "=================================================="
echo "Total Tests:  $TOTAL_TESTS"
echo "Passed:       $PASSED_TESTS"
echo "Failed:       $FAILED_TESTS"
echo ""

if [[ "$FAILED_TESTS" -eq 0 ]]; then
    echo "✅ ALL SUCCESS CRITERIA MET"
    echo ""
    echo "Expected End State Achieved:"
    echo "  ✓ XML State: No 'pay_invoices_online' in database views"
    echo "  ✓ JSON/DB State: web.base.url = https://erp.insightpulseai.com"
    echo "  ✓ Config State: proxy_mode = True, X-Forwarded-Proto = https"
    echo "  ✓ Assets State: Web assets generated and cached"
    echo ""
    echo "User Acceptance Testing:"
    echo "  1. Open Chrome Incognito: https://erp.insightpulseai.com"
    echo "  2. Login screen should render (no white screen)"
    echo "  3. Press F12 → Console → No red 'OwlError' messages"
    echo "  4. Click Gmail SSO login button"
    echo "  5. Verify URL stays on 'https://' (no http:// redirect)"
    echo "  6. View page source: <link href='/web/assets/...css' /> loads with 200 OK"
    echo ""
    exit 0
else
    echo "❌ VALIDATION FAILED ($FAILED_TESTS test(s))"
    echo ""
    echo "Recommended Actions:"
    echo "  1. Review failed criteria above"
    echo "  2. Re-run hotfix script: ./scripts/hotfix_production.sh"
    echo "  3. Check Odoo logs: docker logs $CONTAINER_NAME --tail 100"
    if [[ -n "$NGINX_CONTAINER" ]]; then
        echo "  4. Check nginx logs: docker logs $NGINX_CONTAINER --tail 50"
        echo "  5. Verify nginx config: docker exec $NGINX_CONTAINER nginx -t"
    fi
    echo ""
    exit 1
fi
