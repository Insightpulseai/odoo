#!/usr/bin/env bash
set -euo pipefail

# === Config (override via env) ================================================
ODOO_DB="${ODOO_DB:-ipai_oca_full}"
ODOO_COMPOSE_FILE="${ODOO_COMPOSE_FILE:-}"  # auto-detected via preflight if empty
ODOO_SERVICE="${ODOO_SERVICE:-}"            # auto-detected via preflight if empty

# OCA module list (seed) – safe, minimal must-haves; extend as needed.
# You can later swap this to parse config/addons_manifest.oca_ipai.json via jq.
OCA_MODULES="${OCA_MODULES:-\
queue_job,queue_job_cron_jobrunner,\
mass_editing,auditlog,base_tier_validation,\
web_responsive,web_m2x_options,web_export_view,\
report_xlsx,report_xlsx_helper,\
account_asset_management,account_financial_report,\
account_move_base_import,\
account_bank_statement_import,account_reconcile}"

# ============================================================================

echo "=== [0/5] Running preflight checks ==="
if [ -x scripts/ocadev/preflight.sh ]; then
  eval "$(./scripts/ocadev/preflight.sh | awk -F= '/^(ODOO_COMPOSE_FILE|ODOO_SERVICE)=/ {print "export "$1"=\""$2"\""}')"
fi

if [ -z "${ODOO_COMPOSE_FILE}" ] || [ -z "${ODOO_SERVICE}" ]; then
  echo "ERROR: Missing ODOO_COMPOSE_FILE or ODOO_SERVICE. Run scripts/ocadev/preflight.sh." >&2
  exit 1
fi

echo "Detected configuration:"
echo "  ODOO_COMPOSE_FILE=${ODOO_COMPOSE_FILE}"
echo "  ODOO_SERVICE=${ODOO_SERVICE}"
echo "  ODOO_DB=${ODOO_DB}"
echo ""

echo "=== [1/5] Starting Odoo stack (if not already running) ==="
docker compose -f "${ODOO_COMPOSE_FILE}" up -d "${ODOO_SERVICE}"

echo "=== [2/5] Creating fresh DB '${ODOO_DB}' with base only ==="
docker compose -f "${ODOO_COMPOSE_FILE}" exec -T "${ODOO_SERVICE}" \
  odoo -d "${ODOO_DB}" -i base --stop-after-init --without-demo=all

echo "=== [3/5] Computing ipai_* modules from addons/ipai ==="
if [ ! -d addons/ipai ]; then
  echo "ERROR: addons/ipai directory not found. Run from repo root." >&2
  exit 1
fi

IPAI_MODULES="$(
  find addons/ipai -maxdepth 1 -mindepth 1 -type d -printf '%f\n' \
    | sort \
    | paste -sd ',' -
)"

if [ -z "${IPAI_MODULES}" ]; then
  echo "WARNING: No ipai_* modules detected; skipping ipai install."
fi

echo "ipai modules to install: ${IPAI_MODULES}"

echo "=== [4/5] Installing ipai modules into '${ODOO_DB}' ==="
if [ -n "${IPAI_MODULES}" ]; then
  docker compose -f "${ODOO_COMPOSE_FILE}" exec -T "${ODOO_SERVICE}" \
    odoo -d "${ODOO_DB}" -i "${IPAI_MODULES}" --stop-after-init --without-demo=all
fi

echo "=== [5/5] Installing core OCA modules into '${ODOO_DB}' ==="
echo "OCA modules to install: ${OCA_MODULES}"

docker compose -f "${ODOO_COMPOSE_FILE}" exec -T "${ODOO_SERVICE}" \
  odoo -d "${ODOO_DB}" -i "${OCA_MODULES}" --stop-after-init --without-demo=all

echo "=== DONE ==="
echo "DB: ${ODOO_DB}"
echo "Installed groups:"
echo "  - ipai_* modules from addons/ipai"
echo "  - OCA modules: ${OCA_MODULES}"
