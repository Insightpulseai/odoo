#!/bin/bash
set -euo pipefail

# Finance PPM Deployment Verification Script
# 5-step health check validation

ODOO_URL="http://localhost:8071"
ODOO_DB="odoo_accounting"
N8N_API_URL="${N8N_BASE_URL:-https://ipa.insightpulseai.com}/api/v1"
SUPABASE_URL="https://xkxyvboeubffxxbebsll.supabase.co"

echo "=== Finance PPM: Deployment Verification ==="

CHECKS_PASSED=0
TOTAL_CHECKS=5

# Check 1: Odoo UI Accessibility
echo ">>> Check 1: Odoo UI Accessibility"
if curl -sf "$ODOO_URL/web/login" > /dev/null 2>&1; then
  echo "✅ Odoo UI is accessible"
  ((CHECKS_PASSED++))
else
  echo "❌ Odoo UI is not accessible"
fi
echo ""

# Check 2: Module Installation Verification
echo ">>> Check 2: Module Installation Verification"
installed_count=$(docker exec odoo-accounting odoo-bin shell -d $ODOO_DB << 'EOF' 2>/dev/null | grep -c "installed" || echo "0"
env = self.env
modules = env['ir.module.module'].search([
  ('name', 'in', [
    'ipai_finance_ppm',
    'ipai_ppm_a1',
    'ipai_close_orchestration',
    'account_financial_report',
    'account_asset_management'
  ]),
  ('state', '=', 'installed')
])
for module in modules:
    print(f"installed: {module.name}")
EOF
)

if [ "$installed_count" -ge 5 ]; then
  echo "✅ Core modules installed ($installed_count modules)"
  ((CHECKS_PASSED++))
else
  echo "❌ Module installation incomplete ($installed_count modules)"
fi
echo ""

# Check 3: n8n Workflows Active
echo ">>> Check 3: n8n Workflows Active"
workflow_count=$(curl -sf \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  "$N8N_API_URL/workflows" | \
  python3 -c "import sys, json; print(len(json.load(sys.stdin).get('data', [])))" 2>/dev/null || echo "0")

if [ "$workflow_count" -ge 3 ]; then
  echo "✅ n8n workflows active ($workflow_count workflows)"
  ((CHECKS_PASSED++))
else
  echo "❌ n8n workflows missing ($workflow_count workflows)"
fi
echo ""

# Check 4: Supabase Schema Validation
echo ">>> Check 4: Supabase Schema Validation"
if curl -sf \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  "$SUPABASE_URL/rest/v1/finance_ppm.monthly_reports?limit=1" > /dev/null 2>&1; then
  echo "✅ Supabase schema exists"
  ((CHECKS_PASSED++))
else
  echo "❌ Supabase schema validation failed"
fi
echo ""

# Check 5: Mattermost Notification Test
echo ">>> Check 5: Mattermost Notification Test"
if curl -sf -X POST \
  -H "Content-Type: application/json" \
  -d '{"text": "✅ Finance PPM deployment verification complete"}' \
  "${MATTERMOST_WEBHOOK_URL}" > /dev/null 2>&1; then
  echo "✅ Mattermost notification sent"
  ((CHECKS_PASSED++))
else
  echo "❌ Mattermost notification failed"
fi
echo ""

# Final Result
echo "=== Deployment Verification Result ==="
echo "Checks Passed: $CHECKS_PASSED / $TOTAL_CHECKS"

if [ "$CHECKS_PASSED" -eq "$TOTAL_CHECKS" ]; then
  echo "✅ ALL CHECKS PASSED - Deployment successful"
  exit 0
else
  echo "❌ SOME CHECKS FAILED - Review deployment"
  exit 1
fi
