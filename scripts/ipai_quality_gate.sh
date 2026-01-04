#!/usr/bin/env bash
set -euo pipefail

ROOT="/workspace"
ART_DIR="${ROOT}/artifacts"
LOG_DIR="${ART_DIR}/logs"
REP_DIR="${ART_DIR}/reports"
mkdir -p "${LOG_DIR}" "${REP_DIR}"

IPAI_DIR="${ROOT}/${IPAI_ADDONS_DIR:-addons/ipai}"
OCA_DIR="${ROOT}/${OCA_ADDONS_DIR:-addons/oca}"

DB_HOST="${DB_HOST:-127.0.0.1}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"
DB_NAME="${DB_NAME:-ipai_qg}"

# Odoo core addons path in official images is typically:
ODOO_CORE="/usr/lib/python3/dist-packages/odoo/addons"

# Build addons-path list (only include dirs that exist)
ADDONS_PATHS=()
[ -d "${ODOO_CORE}" ] && ADDONS_PATHS+=("${ODOO_CORE}")
[ -d "${OCA_DIR}" ] && ADDONS_PATHS+=("${OCA_DIR}")
[ -d "${IPAI_DIR}" ] && ADDONS_PATHS+=("${IPAI_DIR}")

ADDONS_PATH="$(IFS=, ; echo "${ADDONS_PATHS[*]}")"

echo "=== ENV DISCOVERY ===" | tee "${REP_DIR}/env.txt"
echo "Odoo version:" | tee -a "${REP_DIR}/env.txt"
(odoo --version || true) | tee -a "${REP_DIR}/env.txt"
echo "addons_path: ${ADDONS_PATH}" | tee -a "${REP_DIR}/env.txt"
echo "ipai dir: ${IPAI_DIR}" | tee -a "${REP_DIR}/env.txt"
echo "oca  dir: ${OCA_DIR}" | tee -a "${REP_DIR}/env.txt"
echo "db   : ${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}" | tee -a "${REP_DIR}/env.txt"

if [ ! -d "${IPAI_DIR}" ]; then
  echo "FATAL: IPAI addons dir not found: ${IPAI_DIR}"
  exit 2
fi

# Discover ipai_* modules
mapfile -t MODULE_DIRS < <(find "${IPAI_DIR}" -maxdepth 1 -mindepth 1 -type d -name 'ipai_*' -print | sort)
if [ "${#MODULE_DIRS[@]}" -eq 0 ]; then
  echo "FATAL: No ipai_* modules found under ${IPAI_DIR}"
  exit 3
fi

MODULES=()
for d in "${MODULE_DIRS[@]}"; do
  if [ -f "${d}/__manifest__.py" ]; then
    MODULES+=("$(basename "${d}")")
  fi
done

if [ "${#MODULES[@]}" -eq 0 ]; then
  echo "FATAL: Found ipai_* dirs but none contain __manifest__.py"
  exit 4
fi

printf "%s\n" "${MODULES[@]}" > "${REP_DIR}/ipai_modules.txt"

echo "=== MODULES (${#MODULES[@]}) ==="
cat "${REP_DIR}/ipai_modules.txt"

# ---------- Static checks ----------
echo "=== STATIC: python compileall ===" | tee "${LOG_DIR}/static_compileall.log"
python3 -m compileall -q "${IPAI_DIR}" 2>&1 | tee -a "${LOG_DIR}/static_compileall.log"

echo "=== STATIC: XML parse ===" | tee "${LOG_DIR}/static_xml_parse.log"
python3 - <<'PY' 2>&1 | tee -a "${LOG_DIR}/static_xml_parse.log"
import os, sys, glob
from xml.etree import ElementTree as ET

ipai_dir = os.environ.get("IPAI_DIR") or os.environ.get("IPAI_ADDONS_DIR") or "addons/ipai"
root = "/workspace"
base = ipai_dir if ipai_dir.startswith("/") else os.path.join(root, ipai_dir)

bad = []
xmls = glob.glob(os.path.join(base, "**/*.xml"), recursive=True)
for p in xmls:
  try:
    ET.parse(p)
  except Exception as e:
    bad.append((p, str(e)))

if bad:
  print("XML_PARSE_FAIL")
  for p, e in bad:
    print(f"- {p}: {e}")
  sys.exit(10)
print(f"XML_OK ({len(xmls)} files)")
PY

# ---------- DB-backed install/upgrade ----------
echo "=== DB: init base ===" | tee "${LOG_DIR}/odoo_init_base.log"
set +e
odoo \
  --db_host="${DB_HOST}" \
  --db_port="${DB_PORT}" \
  --db_user="${DB_USER}" \
  --db_password="${DB_PASSWORD}" \
  -d "${DB_NAME}" \
  --addons-path "${ADDONS_PATH}" \
  -i base \
  --stop-after-init \
  --log-level=debug \
  2>&1 | tee -a "${LOG_DIR}/odoo_init_base.log"
INIT_RC=${PIPESTATUS[0]}
set -e

if [ "${INIT_RC}" -ne 0 ]; then
  echo "FATAL: base init failed (rc=${INIT_RC}). See ${LOG_DIR}/odoo_init_base.log"
  exit 20
fi

# Prepare CSV output
CSV="${ART_DIR}/ipai_quality_gate.csv"
JSON="${ART_DIR}/ipai_quality_gate.json"
MD="${ART_DIR}/IPAI_MODULE_QUALITY_GATE.md"

echo "module,status,stage,log_file,error_hint" > "${CSV}"
echo "[" > "${JSON}"

fail=0
first_json=1

run_one() {
  local mod="$1"
  local stage="$2"
  local log="${LOG_DIR}/odoo_${stage}_${mod}.log"

  set +e
  odoo \
    --db_host="${DB_HOST}" \
    --db_port="${DB_PORT}" \
    --db_user="${DB_USER}" \
    --db_password="${DB_PASSWORD}" \
    -d "${DB_NAME}" \
    --addons-path "${ADDONS_PATH}" \
    ${stage} "${mod}" \
    --stop-after-init \
    --log-level=debug \
    2>&1 | tee -a "${log}"
  local rc=${PIPESTATUS[0]}
  set -e

  local status="PASS"
  local hint=""

  if [ "${rc}" -ne 0 ]; then
    status="FAIL"
    hint="odoo exit ${rc}"
  elif grep -q "Traceback (most recent call last)" "${log}"; then
    status="FAIL"
    hint="traceback in log"
  elif grep -qE "ERROR\s+odoo\." "${log}"; then
    # strict: treat any logged ERROR as fail (common UI/view errors show here)
    status="FAIL"
    hint="ERROR lines in log"
  fi

  echo "${mod},${status},${stage},$(basename "${log}"),${hint}" >> "${CSV}"

  if [ "${first_json}" -eq 0 ]; then
    echo "," >> "${JSON}"
  fi
  first_json=0
  cat >> "${JSON}" <<EOF
  {"module":"${mod}","status":"${status}","stage":"${stage}","log_file":"$(basename "${log}")","error_hint":"${hint}"}
EOF

  if [ "${status}" = "FAIL" ]; then
    fail=1
  fi
}

# Install each module
for mod in "${MODULES[@]}"; do
  echo "=== INSTALL: ${mod} ==="
  run_one "${mod}" "-i"
done

# Upgrade all modules in one pass
ALL_MODS="$(IFS=, ; echo "${MODULES[*]}")"
echo "=== UPGRADE ALL: ${ALL_MODS} ===" | tee "${LOG_DIR}/odoo_upgrade_all.log"
set +e
odoo \
  --db_host="${DB_HOST}" \
  --db_port="${DB_PORT}" \
  --db_user="${DB_USER}" \
  --db_password="${DB_PASSWORD}" \
  -d "${DB_NAME}" \
  --addons-path "${ADDONS_PATH}" \
  -u "${ALL_MODS}" \
  --stop-after-init \
  --log-level=debug \
  2>&1 | tee -a "${LOG_DIR}/odoo_upgrade_all.log"
UP_RC=${PIPESTATUS[0]}
set -e

UP_STATUS="PASS"
UP_HINT=""
if [ "${UP_RC}" -ne 0 ]; then
  UP_STATUS="FAIL"
  UP_HINT="odoo exit ${UP_RC}"
elif grep -q "Traceback (most recent call last)" "${LOG_DIR}/odoo_upgrade_all.log"; then
  UP_STATUS="FAIL"
  UP_HINT="traceback in log"
elif grep -qE "ERROR\s+odoo\." "${LOG_DIR}/odoo_upgrade_all.log"; then
  UP_STATUS="FAIL"
  UP_HINT="ERROR lines in log"
fi

echo "ALL,${UP_STATUS},-u,odoo_upgrade_all.log,${UP_HINT}" >> "${CSV}"
if [ "${first_json}" -eq 0 ]; then echo "," >> "${JSON}"; fi
cat >> "${JSON}" <<EOF
  {"module":"ALL","status":"${UP_STATUS}","stage":"-u","log_file":"odoo_upgrade_all.log","error_hint":"${UP_HINT}"}
EOF

if [ "${UP_STATUS}" = "FAIL" ]; then
  fail=1
fi

echo "]" >> "${JSON}"

# Markdown summary
{
  echo "# IPAI Module Quality Gate"
  echo
  echo "## Environment"
  echo
  echo '```'
  cat "${REP_DIR}/env.txt"
  echo '```'
  echo
  echo "## Modules"
  echo
  echo '```'
  cat "${REP_DIR}/ipai_modules.txt"
  echo '```'
  echo
  echo "## Results (CSV)"
  echo
  echo '```'
  cat "${CSV}"
  echo '```'
  echo
  echo "## Logs"
  echo "- ${LOG_DIR}"
} > "${MD}"

# Fail the job if any module failed
if [ "${fail}" -ne 0 ]; then
  echo "QUALITY GATE: FAIL (see artifacts/logs + artifacts/IPAI_MODULE_QUALITY_GATE.md)"
  exit 50
fi

echo "QUALITY GATE: PASS"
