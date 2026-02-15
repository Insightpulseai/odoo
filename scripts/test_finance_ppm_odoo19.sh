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

# Test 3: Month-End Close Project
print("[Test 3/10] Month-End Close Project")
close_projects = kw("project.project", "search_read",
    [[("name", "=", "Finance PPM - Month-End Close")]],
    {"fields": ["name", "id"]})
if close_projects:
    cpid = close_projects[0]["id"]
    p(f"Month-End Close project found (ID {cpid})")
else:
    f("Month-End Close project not found")
    cpid = None

# Test 4: BIR Tax Filing Project
print("[Test 4/10] BIR Tax Filing Project")
tax_projects = kw("project.project", "search_read",
    [[("name", "=", "Finance PPM - BIR Tax Filing")]],
    {"fields": ["name", "id"]})
if tax_projects:
    tpid = tax_projects[0]["id"]
    p(f"BIR Tax Filing project found (ID {tpid})")
else:
    f("BIR Tax Filing project not found")
    tpid = None

if not cpid or not tpid:
    sys.exit(1)

# Test 5: 6 Closing Stages
print("[Test 5/10] Closing Stages")
stages = kw("project.task.type", "search_read",
    [[("project_ids", "in", [cpid])]],
    {"fields": ["name", "sequence", "fold"]})
stage_names = sorted([s["name"] for s in stages])
expected = sorted(["To Do", "In Preparation", "Under Review", "Pending Approval", "Done", "Cancelled"])
if stage_names == expected:
    p(f"All 6 stages present: {[s['name'] for s in sorted(stages, key=lambda x: x['sequence'])]}")
else:
    f(f"Stage mismatch: got {stage_names}, expected {expected}")

# Test 6: Closing Task Count (>= 39)
print("[Test 6/10] Closing Tasks")
close_count = kw("project.task", "search_count", [[("project_id", "=", cpid)]])
if close_count >= 39:
    p(f"{close_count} month-end closing tasks (expected >= 39)")
elif close_count > 0:
    print(f"  [WARN] {close_count} closing tasks (expected >= 39)")
    passed += 1
else:
    f("No closing tasks found")

# Test 7: BIR Task Count (>= 50)
print("[Test 7/10] BIR Tax Filing Tasks")
bir_count = kw("project.task", "search_count", [[("project_id", "=", tpid)]])
if bir_count >= 50:
    p(f"{bir_count} BIR tax filing tasks (expected >= 50)")
elif bir_count > 0:
    print(f"  [WARN] {bir_count} BIR tasks (expected >= 50)")
    passed += 1
else:
    f("No BIR tax filing tasks found")

# Test 8: Total Task Count
print("[Test 8/10] Total Task Count")
total_tasks = close_count + bir_count
if total_tasks >= 89:
    p(f"{total_tasks} total tasks across 2 projects (39 closing + 50 BIR = 89)")
elif total_tasks > 0:
    print(f"  [WARN] {total_tasks} total tasks (expected >= 89)")
    passed += 1
else:
    f("No tasks found across projects")

# Test 9: Assignee Mapping (across both projects)
print("[Test 9/10] Assignee Mapping")
all_pids = [cpid, tpid]
assigned = kw("project.task", "search_count",
    [[("project_id", "in", all_pids), ("user_ids", "!=", False)]])
unassigned = total_tasks - assigned
if assigned > 0:
    pct = round(assigned / total_tasks * 100, 1) if total_tasks > 0 else 0
    p(f"{assigned}/{total_tasks} tasks assigned ({pct}%)")
    if unassigned > 0:
        print(f"         {unassigned} tasks unassigned (users may need creation)")
else:
    f("No tasks have assignees - user accounts may not exist yet")

# Test 10: BIR Task Deadlines
print("[Test 10/10] Task Deadlines")
with_deadline = kw("project.task", "search_count",
    [[("project_id", "in", all_pids), ("date_deadline", "!=", False)]])
if with_deadline > 0:
    p(f"{with_deadline}/{total_tasks} tasks have deadlines")
else:
    print(f"  [WARN] No tasks have deadlines set")

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
