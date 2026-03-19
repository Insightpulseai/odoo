#!/usr/bin/env bash
# odoo-module-scaffold-ops: Verify module structure is complete
# Usage: verify-module-structure.sh <module_path>
set -euo pipefail

MODULE_PATH="${1:?Usage: verify-module-structure.sh <module_path>}"

PASS=0
FAIL=0

check_file() {
  if [ -f "${MODULE_PATH}/$1" ]; then
    echo "  OK: $1"
    PASS=$((PASS + 1))
  else
    echo "  MISSING: $1"
    FAIL=$((FAIL + 1))
  fi
}

check_dir() {
  if [ -d "${MODULE_PATH}/$1" ]; then
    echo "  OK: $1/"
    PASS=$((PASS + 1))
  else
    echo "  MISSING: $1/"
    FAIL=$((FAIL + 1))
  fi
}

echo "Verifying module structure: ${MODULE_PATH}"
check_file "__init__.py"
check_file "__manifest__.py"
check_dir "models"
check_file "models/__init__.py"
check_dir "views"
check_dir "security"
check_file "security/ir.model.access.csv"

echo ""
echo "Result: ${PASS} passed, ${FAIL} missing"
[ "${FAIL}" -eq 0 ] && exit 0 || exit 1
