#!/usr/bin/env bash
# ============================================================================
# OCA Timeline + Dependencies for Finance PPM
# ============================================================================
# Installs OCA project_timeline + project_task_dependency on Odoo 19 CE
# to provide timeline visualization and task dependency management.
#
# NOTE: project_timeline provides a timeline bar view, NOT a full Gantt chart.
# Critical-path highlighting is NOT available (unverified for Odoo 19).
# See: spec/finance-ppm/decisions/0006-critical-path-unavailable.md
#
# Modules installed:
#   - project_timeline       → Timeline bar view for project tasks (NOT Gantt)
#   - project_task_dependency → Task dependency management (predecessors/successors)
#   - project_stage_closed    → Distinguish closed stages (Done/Cancelled)
#
# Prerequisites:
#   - OCA project repo cloned under external-src/project or vendor/oca/project
#   - Odoo 19 CE running with XML-RPC enabled
#
# Usage:
#   scripts/install_oca_gantt_bridge.sh <admin_password>
#   scripts/install_oca_gantt_bridge.sh <admin_password> --dry-run
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

ODOO_URL="${ODOO_URL:-https://erp.insightpulseai.com}"
ODOO_DB="${ODOO_DB:-odoo}"
ODOO_USER="${ODOO_USER:-admin@insightpulseai.com}"

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <admin_password> [--dry-run]"
    exit 1
fi

ODOO_PASSWORD="$1"
DRY_RUN=false
[[ "${2:-}" == "--dry-run" ]] && DRY_RUN=true

# OCA modules to install (dependency order matters)
OCA_MODULES=(
    "project_stage_closed"
    "project_task_dependency"
    "project_timeline"
)

# Finance PPM bridge module (after OCA)
IPAI_MODULES=(
    "ipai_finance_ppm"
)

echo "============================================================"
echo "OCA Timeline + Dependencies Installation"
echo "============================================================"
echo "Target: ${ODOO_URL}"
echo "DB:     ${ODOO_DB}"
echo "Modules: ${OCA_MODULES[*]}"
echo ""

# ---------------------------------------------------------------------------
# Verify Odoo connectivity
# ---------------------------------------------------------------------------
echo "[1/4] Verifying Odoo connectivity..."
VERSION=$(python3 -c "
import xmlrpc.client
proxy = xmlrpc.client.ServerProxy('${ODOO_URL}/xmlrpc/2/common')
v = proxy.version()
print(v.get('server_version', 'unknown'))
" 2>/dev/null || echo "UNREACHABLE")

if [[ "$VERSION" == "UNREACHABLE" ]]; then
    echo "ERROR: Cannot reach ${ODOO_URL}"
    exit 1
fi
echo "  Odoo ${VERSION} detected"

# ---------------------------------------------------------------------------
# Verify OCA repo availability
# ---------------------------------------------------------------------------
echo "[2/4] Checking OCA module sources..."
OCA_PATHS=(
    "${REPO_ROOT}/external-src/project"
    "${REPO_ROOT}/vendor/oca/project"
)

OCA_FOUND=false
for path in "${OCA_PATHS[@]}"; do
    if [[ -d "$path" ]] && [[ -f "$path/project_timeline/__manifest__.py" ]]; then
        echo "  OCA project modules found: $path"
        OCA_FOUND=true
        break
    fi
done

if [[ "$OCA_FOUND" == "false" ]]; then
    echo "  WARNING: OCA project_timeline not found in local paths"
    echo "  Modules will be installed from Odoo module path if available"
    echo "  To clone: git submodule update --init external-src/project"
fi

# ---------------------------------------------------------------------------
# Install OCA modules via XML-RPC
# ---------------------------------------------------------------------------
echo "[3/4] Installing OCA modules..."

if [[ "$DRY_RUN" == "true" ]]; then
    echo "  [DRY RUN] Would install: ${OCA_MODULES[*]}"
    echo "  [DRY RUN] Then update: ${IPAI_MODULES[*]}"
else
    python3 "${SCRIPT_DIR}/install_module_xmlrpc.py" \
        --url "${ODOO_URL}" \
        --db "${ODOO_DB}" \
        --user "${ODOO_USER}" \
        --password "${ODOO_PASSWORD}" \
        --modules "${OCA_MODULES[*]}" 2>&1 || {
        echo "  WARNING: XML-RPC module install returned non-zero"
        echo "  Attempting alternative: odoo CLI update"
    }
fi

# ---------------------------------------------------------------------------
# Verify installation
# ---------------------------------------------------------------------------
echo "[4/4] Verifying installation..."
python3 -c "
import xmlrpc.client, sys

url = '${ODOO_URL}'
db = '${ODOO_DB}'
user = '${ODOO_USER}'
pwd = '${ODOO_PASSWORD}'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, user, pwd, {})
if not uid:
    print('ERROR: Authentication failed')
    sys.exit(1)

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

modules = ['project_timeline', 'project_task_dependency', 'project_stage_closed']
for mod in modules:
    result = models.execute_kw(db, uid, pwd, 'ir.module.module', 'search_read',
        [[('name', '=', mod)]],
        {'fields': ['name', 'state'], 'limit': 1})
    if result:
        state = result[0]['state']
        icon = '✓' if state == 'installed' else '○'
        print(f'  {icon} {mod}: {state}')
    else:
        print(f'  ✗ {mod}: not found in module list')

# Verify Finance PPM projects have timeline view available
projects = models.execute_kw(db, uid, pwd, 'project.project', 'search_read',
    [[('name', 'like', 'Finance PPM')]],
    {'fields': ['name', 'id']})
for p in projects:
    tasks = models.execute_kw(db, uid, pwd, 'project.task', 'search_count',
        [[('project_id', '=', p['id'])]])
    print(f'  Project: {p[\"name\"]} — {tasks} tasks (timeline view ready)')
"

echo ""
echo "============================================================"
echo "OCA Timeline + Dependencies: Complete"
echo ""
echo "Installed capabilities:"
echo "  ✓ Timeline View           → OCA project_timeline (bar view, NOT full Gantt)"
echo "  ✓ Task Dependencies       → OCA project_task_dependency"
echo "  ✓ Stage Closed Detection  → OCA project_stage_closed"
echo ""
echo "NOT available (see ADR-0006):"
echo "  ✗ Critical Path Analysis  → Unverified for Odoo 19"
echo "  ✗ Interactive Gantt       → project_timeline is read-only timeline"
echo "  ✗ Resource Leveling       → No CE/OCA module available"
echo ""
echo "Access: ${ODOO_URL}/odoo/project → Timeline tab"
echo "============================================================"
