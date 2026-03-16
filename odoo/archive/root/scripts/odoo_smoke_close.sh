#!/usr/bin/env bash
# =============================================================================
# Close Orchestration Smoke Test
# =============================================================================
# Verifies that both ipai_ppm_a1 and ipai_close_orchestration modules
# install correctly and core workflows function.
#
# Usage:
#   ./scripts/odoo_smoke_close.sh
#
# Environment variables:
#   ODOO_BIN  - Path to odoo-bin (default: ./odoo-bin)
#   CONF      - Path to odoo.conf (default: ./odoo.conf)
#   DB        - Database name (default: odoo18_ci)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Configuration
ODOO_BIN="${ODOO_BIN:-${ROOT_DIR}/odoo-bin}"
CONF="${CONF:-${ROOT_DIR}/odoo.conf}"
DB="${DB:-odoo18_ci}"

echo "=========================================="
echo "Close Orchestration Smoke Test"
echo "=========================================="
echo "ODOO_BIN: ${ODOO_BIN}"
echo "CONF: ${CONF}"
echo "DB: ${DB}"
echo ""

# Check if odoo-bin exists
if [[ ! -f "${ODOO_BIN}" ]]; then
    echo "WARNING: odoo-bin not found at ${ODOO_BIN}"
    echo "Skipping Odoo execution tests, running syntax checks only..."

    # At minimum, check Python syntax
    echo "Checking Python syntax..."
    find "${ROOT_DIR}/addons/ipai_ppm_a1" -name "*.py" -exec python3 -m py_compile {} \;
    find "${ROOT_DIR}/addons/ipai_close_orchestration" -name "*.py" -exec python3 -m py_compile {} \;
    echo "Python syntax OK"

    # Check XML validity
    echo "Checking XML validity..."
    for xml in $(find "${ROOT_DIR}/addons/ipai_ppm_a1" "${ROOT_DIR}/addons/ipai_close_orchestration" -name "*.xml"); do
        python3 -c "import xml.etree.ElementTree as ET; ET.parse('${xml}')" || {
            echo "ERROR: Invalid XML: ${xml}"
            exit 1
        }
    done
    echo "XML syntax OK"

    echo ""
    echo "=========================================="
    echo "Smoke test passed (syntax only)"
    echo "=========================================="
    exit 0
fi

# Check if conf exists
if [[ ! -f "${CONF}" ]]; then
    echo "ERROR: Config file not found at ${CONF}"
    exit 1
fi

echo "Step 1: Installing modules..."
${ODOO_BIN} -c "${CONF}" -d "${DB}" \
    -i base,mail,project,ipai_ppm_a1,ipai_close_orchestration \
    --stop-after-init \
    --log-level=warn

echo ""
echo "Step 2: Running smoke tests via Odoo shell..."

${ODOO_BIN} -c "${CONF}" -d "${DB}" shell --log-level=warn <<'PYTHON'
import sys
from datetime import date, timedelta

print("=" * 50)
print("Running Close Orchestration Smoke Tests")
print("=" * 50)

errors = []
Company = env.company

# -----------------------------------------------------------------------------
# Test 1: A1 Role Configuration
# -----------------------------------------------------------------------------
print("\n[Test 1] A1 Role Configuration...")
try:
    Role = env["a1.role"]
    # Check seed data loaded
    rim = Role.search([("code", "=", "RIM")], limit=1)
    if rim:
        print(f"  OK: RIM role exists: {rim.name}")
    else:
        print("  INFO: Creating RIM role...")
        rim = Role.create({
            "code": "RIM",
            "name": "RIM - Rent & Leases Manager",
            "company_id": Company.id,
        })
        print(f"  OK: RIM role created")
except Exception as e:
    errors.append(f"Test 1 failed: {e}")
    print(f"  ERROR: {e}")

# -----------------------------------------------------------------------------
# Test 2: A1 Workstream and Template
# -----------------------------------------------------------------------------
print("\n[Test 2] A1 Workstream and Template...")
try:
    Workstream = env["a1.workstream"]
    Template = env["a1.template"]

    # Create workstream
    ws = Workstream.create({
        "code": "FIN_OPS",
        "name": "Finance Operations",
        "phase_code": "CLOSE",
        "company_id": Company.id,
    })
    print(f"  OK: Workstream created: {ws.name}")

    # Create template
    tpl = Template.create({
        "code": "VAT_REPORT",
        "name": "VAT Reporting",
        "workstream_id": ws.id,
        "owner_role": "RIM",
        "reviewer_role": "CKVC",
        "approver_role": "FD",
        "company_id": Company.id,
    })
    print(f"  OK: Template created: {tpl.name}")

    # Check default steps created
    if tpl.step_ids:
        print(f"  OK: {len(tpl.step_ids)} default steps created")
    else:
        print("  WARN: No default steps")
except Exception as e:
    errors.append(f"Test 2 failed: {e}")
    print(f"  ERROR: {e}")

# -----------------------------------------------------------------------------
# Test 3: A1 Tasklist Generation
# -----------------------------------------------------------------------------
print("\n[Test 3] A1 Tasklist Generation...")
try:
    Tasklist = env["a1.tasklist"]

    today = date.today()
    period_start = today.replace(day=1)
    period_end = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    tasklist = Tasklist.create({
        "name": "CI Smoke Test Close",
        "period_start": period_start,
        "period_end": period_end,
        "company_id": Company.id,
    })
    print(f"  OK: Tasklist created: {tasklist.name}")

    # Generate tasks
    tasklist.action_generate_tasks()
    print(f"  OK: Generated {tasklist.task_count} tasks")
except Exception as e:
    errors.append(f"Test 3 failed: {e}")
    print(f"  ERROR: {e}")

# -----------------------------------------------------------------------------
# Test 4: Close Cycle Creation
# -----------------------------------------------------------------------------
print("\n[Test 4] Close Cycle Creation...")
try:
    Cycle = env["close.cycle"]

    cycle = Cycle.create({
        "name": "CI Smoke Close Cycle",
        "company_id": Company.id,
        "period_start": period_start,
        "period_end": period_end,
    })
    print(f"  OK: Close cycle created: {cycle.name}")

    # Create template for close
    CloseTemplate = env["close.task.template"]
    close_tpl = CloseTemplate.create({
        "code": "VAT_CLOSE",
        "name": "VAT Close Task",
        "preparer_role": "rim",
        "reviewer_role": "ckvc",
        "approver_role": "fd",
        "company_id": Company.id,
    })
    print(f"  OK: Close template created: {close_tpl.name}")

    # Generate tasks
    if hasattr(cycle, "action_generate_tasks"):
        cycle.action_generate_tasks()
        print(f"  OK: Generated {cycle.task_count} close tasks")
except Exception as e:
    errors.append(f"Test 4 failed: {e}")
    print(f"  ERROR: {e}")

# -----------------------------------------------------------------------------
# Test 5: Close Task Workflow
# -----------------------------------------------------------------------------
print("\n[Test 5] Close Task Workflow...")
try:
    tasks = env["close.task"].search([("cycle_id", "=", cycle.id)])
    if tasks:
        task = tasks[0]
        print(f"  Testing task: {task.name}")

        # Start prep
        if hasattr(task, "action_start_prep"):
            task.action_start_prep()
            print(f"  OK: Started prep (state: {task.state})")

        # Mark checklist items done (if any)
        for item in task.checklist_ids:
            item.is_done = True

        # Submit for review
        if hasattr(task, "action_submit_prep"):
            task.action_submit_prep()
            print(f"  OK: Submitted for review (state: {task.state})")

        # Submit for approval
        if hasattr(task, "action_submit_review"):
            task.action_submit_review()
            print(f"  OK: Submitted for approval (state: {task.state})")

        # Approve
        if hasattr(task, "action_approve"):
            task.action_approve()
            print(f"  OK: Approved (state: {task.state})")
    else:
        print("  INFO: No tasks to test workflow")
except Exception as e:
    errors.append(f"Test 5 failed: {e}")
    print(f"  ERROR: {e}")

# -----------------------------------------------------------------------------
# Test 6: Close Exception
# -----------------------------------------------------------------------------
print("\n[Test 6] Close Exception...")
try:
    Exception_ = env["close.exception"]

    exc = Exception_.create({
        "name": "Test Exception",
        "cycle_id": cycle.id,
        "exception_type": "data",
        "severity": "medium",
    })
    print(f"  OK: Exception created: {exc.name}")

    exc.action_start_investigation()
    print(f"  OK: Investigation started (state: {exc.state})")

    exc.action_resolve()
    print(f"  OK: Resolved (state: {exc.state})")
except Exception as e:
    errors.append(f"Test 6 failed: {e}")
    print(f"  ERROR: {e}")

# -----------------------------------------------------------------------------
# Test 7: Close Approval Gate
# -----------------------------------------------------------------------------
print("\n[Test 7] Close Approval Gate...")
try:
    Gate = env["close.approval.gate"]

    gate = Gate.create({
        "name": "Final Signoff Gate",
        "cycle_id": cycle.id,
        "gate_type": "manual",
    })
    print(f"  OK: Gate created: {gate.name}")

    gate.action_mark_ready()
    print(f"  OK: Gate marked ready (state: {gate.state})")

    gate.action_pass()
    print(f"  OK: Gate passed (state: {gate.state})")
except Exception as e:
    errors.append(f"Test 7 failed: {e}")
    print(f"  ERROR: {e}")

# -----------------------------------------------------------------------------
# Test 8: Cron Methods Don't Crash
# -----------------------------------------------------------------------------
print("\n[Test 8] Cron Methods...")
try:
    # Task reminders
    if hasattr(env["close.task"], "_cron_send_due_reminders"):
        env["close.task"]._cron_send_due_reminders()
        print("  OK: _cron_send_due_reminders executed")

    # Exception auto-escalate
    if hasattr(env["close.exception"], "_cron_auto_escalate"):
        env["close.exception"]._cron_auto_escalate()
        print("  OK: _cron_auto_escalate executed")

    # Gate checks
    if hasattr(env["close.approval.gate"], "_cron_check_gates"):
        env["close.approval.gate"]._cron_check_gates()
        print("  OK: _cron_check_gates executed")
except Exception as e:
    errors.append(f"Test 8 failed: {e}")
    print(f"  ERROR: {e}")

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
print("\n" + "=" * 50)
if errors:
    print(f"FAILED: {len(errors)} error(s)")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)
else:
    print("SUCCESS: All smoke tests passed")
    print("=" * 50)
    sys.exit(0)
PYTHON

echo ""
echo "=========================================="
echo "Smoke test completed successfully!"
echo "=========================================="
