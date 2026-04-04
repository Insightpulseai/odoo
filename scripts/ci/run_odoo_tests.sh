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
# Validation status:
#   - Shell syntax: PASS (bash -n)
#   - Local dry-run: PASS (invocation proven)
#   - Azure pipeline execution: NOT YET PROVEN
#
# Required env vars:
#   PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
#   ODOO_BIN, INSTALL_MODULES, TEST_TAGS
#
# Optional env vars:
#   ODOO_HTTP_PORT  (default: 18069)
#   ODOO_DB_SSLMODE (default: require)
#   ADDONS_PATH     (auto-generated if not set)
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
: "${INSTALL_MODULES:?INSTALL_MODULES is required}"
: "${TEST_TAGS:?TEST_TAGS is required}"

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

# Auto-generate addons path if not provided
if [ -z "${ADDONS_PATH:-}" ]; then
  OCA_PATHS=""
  if [ -d "addons/oca" ]; then
    OCA_PATHS=$(find addons/oca -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | tr '\n' ',')
  fi
  ADDONS_PATH="vendor/odoo/addons,addons/ipai"
  if [ -n "$OCA_PATHS" ]; then
    ADDONS_PATH="${ADDONS_PATH},${OCA_PATHS%,}"
  fi
fi

LOG_FILE=".artifacts/test-logs/odoo-test-${PGDATABASE}.log"

echo "============================================="
echo "Odoo Test Runner"
echo "============================================="
echo "PGHOST=${PGHOST}"
echo "PGPORT=${PGPORT}"
echo "PGDATABASE=${PGDATABASE}"
echo "PGUSER=${PGUSER}"
echo "INSTALL_MODULES=${INSTALL_MODULES}"
echo "TEST_TAGS=${TEST_TAGS}"
echo "ODOO_DB_SSLMODE=${ODOO_DB_SSLMODE}"
echo "ODOO_HTTP_PORT=${ODOO_HTTP_PORT}"
echo "ADDONS_PATH=${ADDONS_PATH}"
echo "============================================="

{
  ${ODOO_BIN} \
    -d "${PGDATABASE}" \
    -i "${INSTALL_MODULES}" \
    --test-tags "${TEST_TAGS}" \
    --stop-after-init \
    --without-demo=all \
    --db_host "${PGHOST}" \
    --db_port "${PGPORT}" \
    --db_user "${PGUSER}" \
    --db_password "${PGPASSWORD}" \
    --db_sslmode "${ODOO_DB_SSLMODE}" \
    --addons-path "${ADDONS_PATH}" \
    --http-port "${ODOO_HTTP_PORT}"
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
  echo ""
  echo "============================================="
  echo "RESULT: PASS"
  echo "============================================="
fi
