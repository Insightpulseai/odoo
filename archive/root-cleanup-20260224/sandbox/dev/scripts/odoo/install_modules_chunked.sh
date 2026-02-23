#!/usr/bin/env bash
set -euo pipefail

# Chunked Odoo module installer designed to survive short agent timeouts.
# - Installs modules in small batches (default 5)
# - Idempotent: safe to rerun
# - Produces a clear final summary from ir_module_module
#
# Usage:
#   scripts/odoo/install_modules_chunked.sh \
#     --db odoo_dev \
#     --modules "web_responsive,web_environment_ribbon,base_rest,base_rest_datamodel" \
#     --chunk 5

DB=""
MODULES=""
CHUNK=5
ODOO_BIN="${ODOO_BIN:-odoo}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --db) DB="$2"; shift 2;;
    --modules) MODULES="$2"; shift 2;;
    --chunk) CHUNK="$2"; shift 2;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

if [[ -z "${DB}" || -z "${MODULES}" ]]; then
  echo "Missing --db or --modules" >&2
  exit 2
fi

IFS=',' read -r -a MOD_ARR <<< "${MODULES}"

chunk_run() {
  local start="$1"
  local end="$2"
  local batch=("${MOD_ARR[@]:start:end-start}")
  local csv
  csv="$(IFS=, ; echo "${batch[*]}")"

  echo "==> Installing batch: ${csv}"
  # Prefer -u (upgrade) so reruns are safe even if partially installed.
  # --stop-after-init avoids keeping the server running.
  ${ODOO_BIN} -d "${DB}" --stop-after-init -u "${csv}"
}

total="${#MOD_ARR[@]}"
idx=0
while [[ "${idx}" -lt "${total}" ]]; do
  next=$((idx + CHUNK))
  if [[ "${next}" -gt "${total}" ]]; then next="${total}"; fi
  chunk_run "${idx}" "${next}"
  idx="${next}"
done

echo "==> Done. Installed/updated module states (quick summary):"
psql -v ON_ERROR_STOP=1 -U odoo -d "${DB}" -c "
  SELECT state, COUNT(*) AS count
  FROM ir_module_module
  GROUP BY state
  ORDER BY state;"

echo "==> Target modules status:"
psql -v ON_ERROR_STOP=1 -U odoo -d "${DB}" -c "
  SELECT name, state
  FROM ir_module_module
  WHERE name = ANY (string_to_array('${MODULES}', ','))
  ORDER BY name;"
