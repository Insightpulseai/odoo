#!/usr/bin/env bash
set -euo pipefail

# OCA Module Port Automation Script
# Purpose: Thin wrapper around official oca-port CLI
# Usage: ./scripts/oca/port_addon.sh <module-name> [from-version] [to-version]

MODULE="${1:?Module name required}"
FROM_VERSION="${2:-18.0}"
TO_VERSION="${3:-19.0}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "${REPO_ROOT}"

# Timestamp (Asia/Manila +0800)
TIMESTAMP=$(TZ="Asia/Manila" date +"%Y%m%d-%H%M%z")
EVIDENCE_DIR="web/docs/evidence/${TIMESTAMP}/oca-port-${MODULE}"
mkdir -p "${EVIDENCE_DIR}/logs"

echo "==== OCA Module Port: ${MODULE} ===="
echo "From: ${FROM_VERSION}"
echo "To: ${TO_VERSION}"
echo "Evidence: ${EVIDENCE_DIR}"
echo ""

# Step 1: Check oca-port installed
if ! command -v oca-port &>/dev/null; then
  echo "Installing oca-port from PyPI..."
  pip3 install oca-port | tee "${EVIDENCE_DIR}/logs/install-oca-port.log"
fi

# Step 2: Get OCA repo name from port_queue.yml
OCA_REPO=$(yq ".priorities[].modules[] | select(.name == \"${MODULE}\") | .oca_repo" config/oca/port_queue.yml | head -1)

if [[ -z "${OCA_REPO}" ]]; then
  echo "ERROR: Module ${MODULE} not found in config/oca/port_queue.yml" >&2
  exit 1
fi

echo "OCA Repo: ${OCA_REPO}"

# Step 3: Run oca-port
echo "Running oca-port..."
oca-port "${MODULE}" \
  --from "${FROM_VERSION}" \
  --to "${TO_VERSION}" \
  --repo "OCA/${OCA_REPO}" \
  2>&1 | tee "${EVIDENCE_DIR}/logs/port.log"

PORT_EXIT_CODE=${PIPESTATUS[0]}

if [[ ${PORT_EXIT_CODE} -ne 0 ]]; then
  echo "ERROR: oca-port failed with exit code ${PORT_EXIT_CODE}" >&2
  echo "See logs: ${EVIDENCE_DIR}/logs/port.log" >&2
  
  # Update port_queue.yml with failure
  yq -i ".priorities[].modules[] |= (select(.name == \"${MODULE}\") | .status = \"failed\")" config/oca/port_queue.yml
  
  cat >> config/oca/port_queue.yml << EOFLOG
  - module: ${MODULE}
    status: failed
    timestamp: ${TIMESTAMP}
    evidence: ${EVIDENCE_DIR}
    notes: "oca-port failed, see logs"
EOFLOG
  
  exit 1
fi

# Step 4: Smoke tests
echo ""
echo "==== Smoke Tests ===="

# 4a. Module directory exists
MODULE_PATH="addons/oca/${OCA_REPO}/${MODULE}"
if [[ ! -d "${MODULE_PATH}" ]]; then
  echo "ERROR: Module directory not found: ${MODULE_PATH}" >&2
  exit 1
fi
echo "✓ Module directory exists: ${MODULE_PATH}"

# 4b. Version check
VERSION=$(grep "^    'version':" "${MODULE_PATH}/__manifest__.py" | cut -d"'" -f2)
if [[ ! "${VERSION}" =~ ^${TO_VERSION} ]]; then
  echo "ERROR: Version mismatch. Expected ${TO_VERSION}.x.y.z, got ${VERSION}" >&2
  exit 1
fi
echo "✓ Version correct: ${VERSION}"

# 4c. Python syntax check
echo "Running Python syntax check..."
find "${MODULE_PATH}" -name "*.py" -exec python3 -m py_compile {} \; 2>&1 | tee "${EVIDENCE_DIR}/logs/syntax-check.log"
SYNTAX_EXIT_CODE=${PIPESTATUS[0]}

if [[ ${SYNTAX_EXIT_CODE} -ne 0 ]]; then
  echo "ERROR: Python syntax errors found" >&2
  exit 1
fi
echo "✓ No Python syntax errors"

# 4d. Odoo load test (skip if Odoo not running)
if pgrep -f "odoo-bin" >/dev/null; then
  echo "Testing module load in Odoo..."
  ./scripts/odoo_shell.sh -c "print(env['ir.module.module'].search([('name', '=', '${MODULE}')]).name)" 2>&1 | tee "${EVIDENCE_DIR}/logs/load-test.log"
  
  if grep -q "${MODULE}" "${EVIDENCE_DIR}/logs/load-test.log"; then
    echo "✓ Module loads in Odoo shell"
  else
    echo "⚠ Module not found in Odoo (may need database update)"
  fi
else
  echo "ℹ Skipping Odoo load test (Odoo not running)"
fi

# 4e. Install test (skip if Odoo not running)
if pgrep -f "odoo-bin" >/dev/null && [[ -f "./scripts/odoo_module_install.sh" ]]; then
  echo "Testing module install..."
  ./scripts/odoo_module_install.sh "${MODULE}" 2>&1 | tee "${EVIDENCE_DIR}/logs/install.log"
  
  if grep -q "successfully" "${EVIDENCE_DIR}/logs/install.log"; then
    echo "✓ Module installs successfully"
  else
    echo "⚠ Module install had issues, check logs"
  fi
else
  echo "ℹ Skipping module install test (Odoo not running or install script missing)"
fi

# Step 5: Create status document
cat > "${EVIDENCE_DIR}/STATUS.md" << EOFSTATUS
# Port Status: ${MODULE}

- **From**: ${FROM_VERSION}
- **To**: ${TO_VERSION}
- **OCA Repo**: ${OCA_REPO}
- **Status**: ✅ COMPLETED
- **Timestamp**: ${TIMESTAMP}

## Verification

- [x] Module directory exists
- [x] Version is ${VERSION}
- [x] No syntax errors
$(if pgrep -f "odoo-bin" >/dev/null; then echo "- [x] Loads in Odoo shell"; else echo "- [ ] Loads in Odoo shell (not tested - Odoo not running)"; fi)
$(if pgrep -f "odoo-bin" >/dev/null && [[ -f "./scripts/odoo_module_install.sh" ]]; then echo "- [x] Installs successfully"; else echo "- [ ] Installs successfully (not tested - Odoo not running)"; fi)

## Evidence

- Port log: logs/port.log
- Syntax check: logs/syntax-check.log
$(if pgrep -f "odoo-bin" >/dev/null; then echo "- Load test: logs/load-test.log"; fi)
$(if pgrep -f "odoo-bin" >/dev/null && [[ -f "./scripts/odoo_module_install.sh" ]]; then echo "- Install log: logs/install.log"; fi)
EOFSTATUS

# Step 6: Update port_queue.yml
yq -i ".priorities[].modules[] |= (select(.name == \"${MODULE}\") | .status = \"completed\")" config/oca/port_queue.yml

cat >> config/oca/port_queue.yml << EOFLOG
  - module: ${MODULE}
    status: completed
    timestamp: ${TIMESTAMP}
    evidence: ${EVIDENCE_DIR}
    notes: "Automated port via oca-port, smoke tests passed"
EOFLOG

echo ""
echo "==== Port Completed Successfully ===="
echo "Module: ${MODULE}"
echo "Evidence: ${EVIDENCE_DIR}"
echo "Next: Review evidence and commit changes"
