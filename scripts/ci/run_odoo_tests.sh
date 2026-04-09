#!/usr/bin/env bash
# =============================================================================
# run_odoo_tests.sh — Odoo module test runner for Azure PostgreSQL
# =============================================================================
# Runs Odoo CLI test execution against a disposable database on pg-ipai-odoo.
# Called by azure-pipelines-odoo-test.yml and local dev.
#
# Safety: Refuses to run against known non-disposable databases (postgres,
#         odoo, odoo_dev, odoo_dev_18, odoo_staging). Exit code 2 on violation.
#
# Required env vars:
#   PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
#   ODOO_BIN, TEST_TAGS
#   INSTALL_MODULES (or INSTALL_MODULE_IDS for backwards compat)
#
# Optional env vars:
#   ODOO_HTTP_PORT   (default: 18069)
#   ODOO_DB_SSLMODE  (default: require)
#   ADDONS_PATH      (default: none — uses Odoo config default)
# =============================================================================

set -euo pipefail

mkdir -p .artifacts/test-logs

# Validate required env vars
: "${PGHOST:?PGHOST is required}"
: "${PGPORT:?PGPORT is required}"
: "${PGDATABASE:?PGDATABASE is required}"
: "${PGUSER:?PGUSER is required}"
: "${PGPASSWORD:?PGPASSWORD is required}"
: "${ODOO_BIN:?ODOO_BIN is required}"
: "${TEST_TAGS:?TEST_TAGS is required}"

# Accept either INSTALL_MODULES or INSTALL_MODULE_IDS (backwards compat)
MODULES="${INSTALL_MODULES:-${INSTALL_MODULE_IDS:?INSTALL_MODULES is required}}"

ODOO_HTTP_PORT="${ODOO_HTTP_PORT:-18069}"
ODOO_DB_SSLMODE="${ODOO_DB_SSLMODE:-require}"

# ---------------------------------------------------------------------------
# Safety guard: refuse to run against known non-disposable databases
# ---------------------------------------------------------------------------
BLOCKED_DBS="postgres odoo odoo_dev odoo_dev_18 odoo_staging"
for blocked in $BLOCKED_DBS; do
  if [ "${PGDATABASE}" = "${blocked}" ]; then
    echo "FATAL: PGDATABASE='${PGDATABASE}' is a known shared/non-disposable database."
    echo "Odoo test execution requires a disposable database (e.g. odoo_test_<buildid>)."
    echo "Aborting to protect production/dev data."
    exit 2
  fi
done

LOG_FILE=".artifacts/test-logs/odoo-test-${PGDATABASE}-$(date +%Y%m%d%H%M%S).log"

# Build optional args
EXTRA_ARGS=()
if [ -n "${ADDONS_PATH:-}" ]; then
  EXTRA_ARGS+=(--addons-path "${ADDONS_PATH}")
fi

{
  echo "=============================================="
  echo "Odoo Test Runner"
  echo "Time:            $(date)"
  echo "PGHOST:          ${PGHOST}"
  echo "PGPORT:          ${PGPORT}"
  echo "PGDATABASE:      ${PGDATABASE}"
  echo "INSTALL_MODULES: ${MODULES}"
  echo "TEST_TAGS:       ${TEST_TAGS}"
  echo "ODOO_DB_SSLMODE: ${ODOO_DB_SSLMODE}"
  echo "ODOO_HTTP_PORT:  ${ODOO_HTTP_PORT}"
  echo "=============================================="

  "${ODOO_BIN}" \
    -d "${PGDATABASE}" \
    -i "${MODULES}" \
    --test-tags "${TEST_TAGS}" \
    --stop-after-init \
    --without-demo=all \
    --db_host "${PGHOST}" \
    --db_port "${PGPORT}" \
    --db_user "${PGUSER}" \
    --db_password "${PGPASSWORD}" \
    --db_sslmode "${ODOO_DB_SSLMODE}" \
    --http-port "${ODOO_HTTP_PORT}" \
    --log-level info \
    --log-handler odoo.tests:DEBUG \
    "${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}"
} 2>&1 | tee "${LOG_FILE}"

# Classify result
if grep -qE "FAIL|CRITICAL|Traceback" "${LOG_FILE}"; then
  echo ""
  echo "============================================="
  echo "RESULT: FAIL — errors detected in test output"
  echo "============================================="
  grep -E "FAIL|CRITICAL|ERROR" "${LOG_FILE}" | tail -20
  exit 1
else
  # Also check structured failure lines
  FAIL_COUNT=$(grep -cE '^\d{4}-\d{2}-\d{2} .*(FAIL|ERROR)' "${LOG_FILE}" || true)
  if [ "${FAIL_COUNT}" -gt 0 ]; then
    echo "Odoo test suite: ${FAIL_COUNT} failure/error lines detected."
    echo "Review: ${LOG_FILE}"
    exit 1
  fi
  echo ""
  echo "============================================="
  echo "RESULT: PASS"
  echo "============================================="
fi
