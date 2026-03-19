#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Minimal Odoo Company Bootstrap
# Purpose: ONLY rename YourCompany → InsightPulseAI + create TBWA\SMP + grant multi-company access
# Usage: ./bootstrap_companies_min.sh [container-name]
# ============================================================

ODOO_CONTAINER="${1:-odoo-erp-prod}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Minimal company bootstrap (no email/website/currency changes)..."
echo "Container: $ODOO_CONTAINER"
echo "---"

# Run minimal bootstrap
docker exec -i "$ODOO_CONTAINER" odoo shell -d odoo --no-http < "$SCRIPT_DIR/company_bootstrap_min.py"

echo ""
echo "✅ Bootstrap complete!"
echo ""
echo "🔍 Verifying..."

# Verify
docker exec -i "$ODOO_CONTAINER" odoo shell -d odoo --no-http <<'PY'
env.cr.execute("select id, name from res_company order by id;")
companies = env.cr.fetchall()
print("Companies:")
for cid, cname in companies:
    print(f"  [{cid}] {cname}")

u = env["res.users"].sudo().search([("login","=","admin")], limit=1)
if u:
    print(f"\nadmin default: {u.company_id.name}")
    print(f"admin allowed: {[c.name for c in u.company_ids]}")
PY

echo ""
echo "✅ Done!"
