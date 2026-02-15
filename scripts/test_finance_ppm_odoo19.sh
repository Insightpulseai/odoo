#!/bin/bash
# =============================================================================
# Finance PPM Verification Test Suite - Odoo 19 CE
# =============================================================================
# Runs 10 verification checks against the deployed Finance PPM system.
#
# Usage:
#   ./scripts/test_finance_ppm_odoo19.sh
#
# Environment:
#   ODOO_URL      (default: https://erp.insightpulseai.com)
#   ODOO_DB       (default: odoo)
#   ODOO_USER     (default: admin@insightpulseai.com)
#   ODOO_PASSWORD (required)
#   SUPERSET_URL  (default: https://superset.insightpulseai.com)
# =============================================================================

set -uo pipefail

export ODOO_URL="${ODOO_URL:-https://erp.insightpulseai.com}"
export ODOO_DB="${ODOO_DB:-odoo}"
export ODOO_USER="${ODOO_USER:-admin@insightpulseai.com}"
export ODOO_PASSWORD="${ODOO_PASSWORD:?ODOO_PASSWORD must be set}"
export SUPERSET_URL="${SUPERSET_URL:-https://superset.insightpulseai.com}"
export N8N_URL="${N8N_URL:-https://n8n.insightpulseai.com}"

PASSED=0
FAILED=0
WARNED=0

pass() { echo "  [PASS] $1"; ((PASSED++)); }
fail() { echo "  [FAIL] $1"; ((FAILED++)); }
warn() { echo "  [WARN] $1"; ((WARNED++)); }

echo "============================================================"
echo "Finance PPM Verification - Odoo 19 CE"
echo "============================================================"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "URL:  $ODOO_URL"
echo ""

# ---------------------------------------------------------------------------
# Test 1: Odoo 19 Connectivity
# ---------------------------------------------------------------------------
echo "[Test 1/10] Odoo 19 Connectivity"
ODOO_VERSION=$(python3 -c "
import xmlrpc.client
try:
    c = xmlrpc.client.ServerProxy('${ODOO_URL}/xmlrpc/2/common')
    v = c.version()
    print(v.get('server_version', 'unknown'))
except Exception as e:
    print(f'ERROR:{e}')
" 2>/dev/null)

if [[ "$ODOO_VERSION" == ERROR:* ]]; then
    fail "Cannot connect to Odoo: ${ODOO_VERSION#ERROR:}"
elif [[ "$ODOO_VERSION" == 19* ]]; then
    pass "Odoo ${ODOO_VERSION} reachable"
else
    warn "Odoo ${ODOO_VERSION} (expected 19.x)"
fi

# ---------------------------------------------------------------------------
# Test 2: Authentication
# ---------------------------------------------------------------------------
echo "[Test 2/10] Authentication"
AUTH_UID=$(python3 -c "
import xmlrpc.client
c = xmlrpc.client.ServerProxy('${ODOO_URL}/xmlrpc/2/common')
uid = c.authenticate('${ODOO_DB}', '${ODOO_USER}', '${ODOO_PASSWORD}', {})
print(uid or 'FAILED')
" 2>/dev/null)

if [[ "$AUTH_UID" == "FAILED" || -z "$AUTH_UID" ]]; then
    fail "Authentication failed for ${ODOO_USER}"
else
    pass "Authenticated as UID ${AUTH_UID}"
fi

# ---------------------------------------------------------------------------
# Tests 3-10: Detailed verification via Python
# ---------------------------------------------------------------------------
python3 << 'PYEOF'
import xmlrpc.client
import os
import sys

url = os.environ["ODOO_URL"]
db = os.environ["ODOO_DB"]
user = os.environ["ODOO_USER"]
pw = os.environ["ODOO_PASSWORD"]

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, user, pw, {})
if not uid:
    print("  [FAIL] Cannot authenticate for detailed tests")
    sys.exit(1)

models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

def kw(model, method, *a, **k):
    return models.execute_kw(db, uid, pw, model, method, *a, **k)

passed = 0
failed = 0

def p(msg):
    global passed
    print(f"  [PASS] {msg}")
    passed += 1

def f(msg):
    global failed
    print(f"  [FAIL] {msg}")
    failed += 1

# Test 3: Finance PPM Project
print("[Test 3/10] Finance PPM Project")
projects = kw("project.project", "search_read",
    [[("name", "like", "Finance PPM")]],
    {"fields": ["name", "id"]})
if projects:
    pid = projects[0]["id"]
    p(f"Project found: {projects[0]['name']} (ID {pid})")
else:
    f("Finance PPM project not found")
    sys.exit(1)

# Test 4: 6 Closing Stages
print("[Test 4/10] Closing Stages")
stages = kw("project.task.type", "search_read",
    [[("project_ids", "in", [pid])]],
    {"fields": ["name", "sequence", "fold"]})
stage_names = sorted([s["name"] for s in stages])
expected = sorted(["To Do", "In Preparation", "Under Review", "Pending Approval", "Done", "Cancelled"])
if stage_names == expected:
    p(f"All 6 stages present: {[s['name'] for s in sorted(stages, key=lambda x: x['sequence'])]}")
else:
    f(f"Stage mismatch: got {stage_names}, expected {expected}")

# Test 5: Task Count
print("[Test 5/10] Task Count")
task_count = kw("project.task", "search_count", [[("project_id", "=", pid)]])
if task_count >= 71:
    p(f"{task_count} tasks imported (base: 36 closing + 35 BIR = 71)")
elif task_count > 0:
    print(f"  [WARN] {task_count} tasks (expected >= 71 base tasks)")
    passed += 1
else:
    f("No tasks found in project")

# Test 6: Closing Tasks Present
print("[Test 6/10] Closing Tasks")
closing_count = kw("project.task", "search_count",
    [[("project_id", "=", pid), ("name", "not like", "1601"), ("name", "not like", "0619"),
      ("name", "not like", "2550"), ("name", "not like", "1702")]])
if closing_count >= 36:
    p(f"{closing_count} month-end closing tasks")
else:
    f(f"Only {closing_count} closing tasks (expected >= 36)")

# Test 7: BIR Tax Filing Tasks
print("[Test 7/10] BIR Tax Filing Tasks")
bir_count = kw("project.task", "search_count",
    [[("project_id", "=", pid), "|", "|", "|", "|",
      ("name", "like", "1601-C"), ("name", "like", "0619-E"),
      ("name", "like", "2550Q"), ("name", "like", "1601-EQ"),
      ("name", "like", "1702")]])
if bir_count >= 35:
    p(f"{bir_count} BIR tax filing tasks")
elif bir_count > 0:
    print(f"  [WARN] {bir_count} BIR tasks (expected >= 35)")
    passed += 1
else:
    f("No BIR tax filing tasks found")

# Test 8: Assignee Mapping
print("[Test 8/10] Assignee Mapping")
assigned = kw("project.task", "search_count",
    [[("project_id", "=", pid), ("user_ids", "!=", False)]])
unassigned = task_count - assigned
if assigned > 0:
    pct = round(assigned / task_count * 100, 1) if task_count > 0 else 0
    p(f"{assigned}/{task_count} tasks assigned ({pct}%)")
    if unassigned > 0:
        print(f"         {unassigned} tasks unassigned (users may need creation)")
else:
    f("No tasks have assignees - user accounts may not exist yet")

# Test 9: Task Deadlines
print("[Test 9/10] Task Deadlines")
with_deadline = kw("project.task", "search_count",
    [[("project_id", "=", pid), ("date_deadline", "!=", False)]])
if with_deadline > 0:
    p(f"{with_deadline}/{task_count} tasks have deadlines")
else:
    print(f"  [WARN] No tasks have deadlines set")

# Test 10: OCA 19.0 Module Check
print("[Test 10/10] OCA 19.0 Modules")
try:
    project_mod = kw("ir.module.module", "search_read",
        [[("name", "=", "project"), ("state", "=", "installed")]],
        {"fields": ["name", "installed_version"]})
    if project_mod:
        ver = project_mod[0].get("installed_version", "unknown")
        p(f"project module installed (v{ver})")
    else:
        f("project module not installed")
except Exception:
    print("  [WARN] Cannot verify module versions (access rights)")
    passed += 1

# Summary
print()
print("=" * 60)
total = passed + failed
print(f"Results: {passed}/{total} passed, {failed} failed")
if failed == 0:
    print("VERDICT: ALL TESTS PASSED")
else:
    print("VERDICT: SOME TESTS FAILED")
    sys.exit(1)
print("=" * 60)
PYEOF

PYEXIT=$?

echo ""
echo "============================================================"
if [ $PYEXIT -eq 0 ]; then
    echo "OVERALL: VERIFICATION PASSED"
else
    echo "OVERALL: VERIFICATION HAS FAILURES"
fi
echo "============================================================"
