#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Odoo Company Bootstrap Script
# Purpose: Rename YourCompany → InsightPulseAI + create TBWA\SMP
# Usage: ./bootstrap_companies.sh [container-name]
# ============================================================

ODOO_CONTAINER="${1:-odoo-erp-prod}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Bootstrapping Odoo companies via ORM shell..."
echo "Container: $ODOO_CONTAINER"
echo "---"

# Run bootstrap script inside Odoo container
docker exec -i "$ODOO_CONTAINER" odoo shell -d odoo --no-http < "$SCRIPT_DIR/company_bootstrap.py"

echo ""
echo "✅ Company bootstrap complete!"
echo ""
echo "🔍 Verifying via Odoo shell..."

# Verify results
docker exec -i "$ODOO_CONTAINER" odoo shell -d odoo --no-http <<'PY'
env.cr.execute("select id, name from res_company order by id;")
companies = env.cr.fetchall()
print("Companies in database:")
for cid, cname in companies:
    print(f"  [{cid}] {cname}")

u = env["res.users"].sudo().search([("login","=","admin")], limit=1)
if u:
    print(f"\nadmin default company: {u.company_id.name}")
    print(f"admin allowed companies: {[c.name for c in u.company_ids]}")
else:
    print("\nWARNING: admin user not found")
PY

echo ""
echo "✅ Verification complete!"
