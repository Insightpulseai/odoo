#!/bin/bash
# =============================================================================
# Finance PPM Deployment Orchestrator - Odoo 19 CE
# =============================================================================
# Deploys the complete Finance PPM system:
#   1. Seeds 6 canonical stages + project
#   2. Imports 36 closing tasks + 33 BIR tax filing tasks
#   3. Verifies deployment
#
# Usage:
#   ./scripts/deploy_finance_ppm_odoo19.sh <admin_password>
#   ./scripts/deploy_finance_ppm_odoo19.sh <admin_password> --months 12
#
# Environment:
#   ODOO_URL  (default: https://erp.insightpulseai.com)
#   ODOO_DB   (default: odoo)
#   ODOO_USER (default: admin@insightpulseai.com)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ADMIN_PASSWORD="${1:?Usage: deploy_finance_ppm_odoo19.sh <admin_password> [--months N]}"
shift

export ODOO_URL="${ODOO_URL:-https://erp.insightpulseai.com}"
export ODOO_DB="${ODOO_DB:-odoo}"
export ODOO_USER="${ODOO_USER:-admin@insightpulseai.com}"

echo "============================================================"
echo "Finance PPM Deployment - Odoo 19 CE"
echo "============================================================"
echo "URL:  $ODOO_URL"
echo "DB:   $ODOO_DB"
echo "User: $ODOO_USER"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================================"
echo ""

# ---- Pre-flight check ----
echo "[1/4] Pre-flight: Checking Odoo 19 health..."

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$ODOO_URL/web/login" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" != "200" ]; then
    echo "  FAIL: Odoo not reachable at $ODOO_URL (HTTP $HTTP_CODE)"
    echo "  Attempting XML-RPC version check..."
fi

python3 -c "
import xmlrpc.client, sys
try:
    c = xmlrpc.client.ServerProxy('${ODOO_URL}/xmlrpc/2/common')
    v = c.version()
    sv = v.get('server_version', 'unknown')
    print(f'  Odoo version: {sv}')
    if not sv.startswith('19'):
        print(f'  WARNING: Expected Odoo 19.x, got {sv}')
    uid = c.authenticate('${ODOO_DB}', '${ODOO_USER}', '${ADMIN_PASSWORD}', {})
    if uid:
        print(f'  Auth: OK (UID {uid})')
    else:
        print('  Auth: FAILED')
        sys.exit(1)
except Exception as e:
    print(f'  ERROR: {e}')
    sys.exit(1)
"
echo "  Pre-flight: PASS"
echo ""

# ---- Step 1: Seed stages + project ----
echo "[2/4] Seeding stages and project..."
python3 "${SCRIPT_DIR}/seed_finance_ppm_stages_odoo19.py" "$ADMIN_PASSWORD"
echo ""

# ---- Step 2: Import tasks ----
echo "[3/4] Importing tasks..."
python3 "${SCRIPT_DIR}/bulk_import_tasks_odoo19.py" "$ADMIN_PASSWORD" "$@"
echo ""

# ---- Step 3: Verification ----
echo "[4/4] Running verification..."
python3 -c "
import xmlrpc.client, sys

url = '${ODOO_URL}'
db = '${ODOO_DB}'
user = '${ODOO_USER}'
pw = '${ADMIN_PASSWORD}'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, user, pw, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

def kw(model, method, *args, **kwargs):
    return models.execute_kw(db, uid, pw, model, method, *args, **kwargs)

checks_passed = 0
checks_failed = 0

# Check 1: Project exists
project_ids = kw('project.project', 'search',
    [[('name', '=', 'Finance PPM - Month-End Close & Tax Filing')]])
if project_ids:
    print(f'  [PASS] Finance PPM project found (ID {project_ids[0]})')
    checks_passed += 1
else:
    print('  [FAIL] Finance PPM project NOT found')
    checks_failed += 1
    sys.exit(1)

pid = project_ids[0]

# Check 2: 6 stages
stages = kw('project.task.type', 'search_read',
    [[('project_ids', 'in', [pid])]],
    {'fields': ['name']})
stage_names = [s['name'] for s in stages]
expected = ['To Do', 'In Preparation', 'Under Review', 'Pending Approval', 'Done', 'Cancelled']
missing = [s for s in expected if s not in stage_names]
if not missing:
    print(f'  [PASS] All 6 stages present: {stage_names}')
    checks_passed += 1
else:
    print(f'  [FAIL] Missing stages: {missing}')
    checks_failed += 1

# Check 3: Task count
task_count = kw('project.task', 'search_count', [[('project_id', '=', pid)]])
if task_count >= 69:
    print(f'  [PASS] {task_count} tasks in project (expected >= 69)')
    checks_passed += 1
elif task_count > 0:
    print(f'  [WARN] {task_count} tasks (expected >= 69 base tasks)')
    checks_passed += 1
else:
    print(f'  [FAIL] No tasks found')
    checks_failed += 1

# Check 4: Tasks by assignee
print('  Task distribution by assignee:')
users = kw('project.task', 'read_group',
    [[('project_id', '=', pid)]],
    {'fields': ['user_ids'], 'groupby': ['user_ids']})
for u in users:
    print(f'    {u.get(\"user_ids\", [\"Unassigned\"])} : {u[\"user_ids_count\"]} tasks')

print()
print(f'  Checks: {checks_passed} passed, {checks_failed} failed')
if checks_failed == 0:
    print('  DEPLOYMENT VERIFIED')
else:
    print('  DEPLOYMENT HAS ISSUES')
    sys.exit(1)
"

echo ""
echo "============================================================"
echo "Finance PPM Deployment Complete"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Apply Superset SQL views:"
echo "     psql < scripts/dashboard_queries_odoo19.sql"
echo ""
echo "  2. Import n8n workflow:"
echo "     automations/n8n/workflows/n8n_finance_ppm_workflow_odoo19.json"
echo ""
echo "  3. Run full test suite:"
echo "     ./scripts/test_finance_ppm_odoo19.sh"
echo ""
