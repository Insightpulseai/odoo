#!/usr/bin/env bash
# =============================================================================
# PostgreSQL Resilience Config Check — scripts/ci/check_pg_resilience.sh
# =============================================================================
# Validates that Odoo and PostgreSQL are configured for transient fault
# resilience: connection pool sizing, timeouts, and health probe paths.
#
# Can run in two modes:
#   1. Config-only (no DB): validates odoo.conf settings
#   2. Full (with DB): also checks PostgreSQL server settings
#
# Required env vars (full mode only):
#   PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
#
# Optional env vars:
#   ODOO_CONF — path to odoo.conf (default: config/azure/odoo.conf)
# =============================================================================

set -euo pipefail

ODOO_CONF="${ODOO_CONF:-config/azure/odoo.conf}"
RESULT=0

echo "=============================================="
echo "PostgreSQL Resilience Config Check"
echo "Time:      $(date)"
echo "Odoo conf: ${ODOO_CONF}"
echo "=============================================="

# --- Check 1: odoo.conf exists ---
if [ ! -f "${ODOO_CONF}" ]; then
  echo "FAIL: ${ODOO_CONF} not found"
  exit 1
fi

# --- Check 2: proxy_mode is enabled ---
if grep -q "^proxy_mode\s*=\s*True" "${ODOO_CONF}"; then
  echo "PASS: proxy_mode = True (required for Front Door)"
else
  echo "FAIL: proxy_mode not set to True — required behind Azure Front Door"
  RESULT=1
fi

# --- Check 3: list_db is disabled ---
if grep -q "^list_db\s*=\s*False" "${ODOO_CONF}"; then
  echo "PASS: list_db = False (database selector blocked)"
else
  echo "FAIL: list_db should be False in production"
  RESULT=1
fi

# --- Check 4: workers configured ---
WORKERS=$(grep "^workers\s*=" "${ODOO_CONF}" | head -1 | sed 's/.*=\s*//' | tr -d ' ')
if [ -n "${WORKERS}" ] && [ "${WORKERS}" -ge 2 ] 2>/dev/null; then
  echo "PASS: workers = ${WORKERS} (multi-process mode)"
else
  echo "WARN: workers not set or < 2 — single-process mode is not production-grade"
fi

# --- Check 5: limit_time_real configured ---
LIMIT_TIME=$(grep "^limit_time_real\s*=" "${ODOO_CONF}" | head -1 | sed 's/.*=\s*//' | tr -d ' ')
if [ -n "${LIMIT_TIME}" ] && [ "${LIMIT_TIME}" -ge 300 ] 2>/dev/null; then
  echo "PASS: limit_time_real = ${LIMIT_TIME}s (sufficient for long operations)"
else
  echo "WARN: limit_time_real not set or < 300s"
fi

# --- Check 6: web.base.url is set to public hostname ---
BASE_URL=$(grep "^web\.base\.url\s*=" "${ODOO_CONF}" | head -1 | sed 's/.*=\s*//' | tr -d ' ')
if echo "${BASE_URL}" | grep -q "insightpulseai.com"; then
  echo "PASS: web.base.url = ${BASE_URL} (public hostname)"
else
  echo "WARN: web.base.url not set to public hostname — may generate wrong URLs"
fi

# --- Full mode: PostgreSQL server checks ---
if [ -n "${PGHOST:-}" ] && [ -n "${PGUSER:-}" ]; then
  echo ""
  echo "--- PostgreSQL server checks ---"
  echo "Host: ${PGHOST}"

  # Check 7: Connection succeeds with timeout
  if PGCONNECT_TIMEOUT=5 psql "host=${PGHOST} port=${PGPORT:-5432} dbname=${PGDATABASE:-odoo} user=${PGUSER} sslmode=require connect_timeout=5" -c "SELECT 1" > /dev/null 2>&1; then
    echo "PASS: PostgreSQL connection successful (5s timeout)"
  else
    echo "FAIL: Cannot connect to PostgreSQL within 5s"
    RESULT=1
  fi

  # Check 8: idle_in_transaction_session_timeout
  IDLE_TIMEOUT=$(PGCONNECT_TIMEOUT=5 psql "host=${PGHOST} port=${PGPORT:-5432} dbname=${PGDATABASE:-odoo} user=${PGUSER} sslmode=require connect_timeout=5" -tAc "SHOW idle_in_transaction_session_timeout" 2>/dev/null || echo "")
  if [ -n "${IDLE_TIMEOUT}" ] && [ "${IDLE_TIMEOUT}" != "0" ]; then
    echo "PASS: idle_in_transaction_session_timeout = ${IDLE_TIMEOUT}"
  else
    echo "WARN: idle_in_transaction_session_timeout is 0 (disabled) — leaked transactions won't be cleaned up"
  fi

  # Check 9: max_connections
  MAX_CONN=$(PGCONNECT_TIMEOUT=5 psql "host=${PGHOST} port=${PGPORT:-5432} dbname=${PGDATABASE:-odoo} user=${PGUSER} sslmode=require connect_timeout=5" -tAc "SHOW max_connections" 2>/dev/null || echo "")
  if [ -n "${MAX_CONN}" ]; then
    echo "INFO: PostgreSQL max_connections = ${MAX_CONN}"
    if [ "${MAX_CONN}" -lt 100 ] 2>/dev/null; then
      echo "WARN: max_connections < 100 — may be insufficient for web + worker + cron"
    fi
  fi
else
  echo ""
  echo "SKIP: PostgreSQL server checks (PGHOST/PGUSER not set — config-only mode)"
fi

echo ""
echo "=============================================="
if [ "${RESULT}" -eq 0 ]; then
  echo "Result: PASS"
else
  echo "Result: FAIL"
fi
echo "=============================================="

exit "${RESULT}"
