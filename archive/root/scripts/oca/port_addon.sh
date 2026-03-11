#!/usr/bin/env bash
set -euo pipefail

# OCA Module Port Automation Script
# Purpose: Thin wrapper around official oca-port CLI (v0.21+)
# Usage: ./scripts/oca/port_addon.sh <module-name> [from-version] [to-version]
#
# Correct oca-port invocation (v0.21):
#   cd addons/oca/<repo>/
#   oca-port oca/<from> oca/<to> <addon-name> --non-interactive --repo-name <repo>

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
echo "From: ${FROM_VERSION} → To: ${TO_VERSION}"
echo "Evidence: ${EVIDENCE_DIR}"
echo ""

# Step 1: Check oca-port installed
if ! command -v oca-port &>/dev/null; then
  echo "Installing oca-port..."
  pip3 install oca-port 2>&1 | tee "${EVIDENCE_DIR}/logs/install-oca-port.log"
fi

# Step 2: Get OCA repo from port_queue.yml
OCA_REPO=$(yq ".priorities[].modules[] | select(.name == \"${MODULE}\") | .oca_repo" config/oca/port_queue.yml | head -1)

if [[ -z "${OCA_REPO}" ]]; then
  echo "ERROR: Module ${MODULE} not found in config/oca/port_queue.yml" >&2
  exit 1
fi

echo "OCA Repo: ${OCA_REPO}"

OCA_REPO_DIR="${REPO_ROOT}/addons/oca/${OCA_REPO}"

if [[ ! -d "${OCA_REPO_DIR}" ]]; then
  echo "ERROR: OCA repo directory not found: ${OCA_REPO_DIR}" >&2
  echo "Clone it first: git clone https://github.com/OCA/${OCA_REPO}.git ${OCA_REPO_DIR}" >&2
  exit 1
fi

# Step 3: Ensure 18.0 and 19.0 branches are fetched
echo "Fetching remote branches..."
cd "${OCA_REPO_DIR}"
git fetch oca "${FROM_VERSION}" "${TO_VERSION}" 2>&1 | tee "${EVIDENCE_DIR}/logs/fetch.log" || true

# Step 4: Run oca-port (correct v0.21 invocation)
# Must run from INSIDE the OCA repo directory
# SOURCE and TARGET are git refs: oca/18.0, oca/19.0
echo "Running oca-port..."
oca-port \
  "oca/${FROM_VERSION}" \
  "oca/${TO_VERSION}" \
  "${MODULE}" \
  --non-interactive \
  --repo-name "${OCA_REPO}" \
  2>&1 | tee "${REPO_ROOT}/${EVIDENCE_DIR}/logs/port.log"

PORT_EXIT_CODE=${PIPESTATUS[0]}
cd "${REPO_ROOT}"

if [[ ${PORT_EXIT_CODE} -ne 0 ]]; then
  echo "ERROR: oca-port failed (exit ${PORT_EXIT_CODE})" >&2
  echo "Log: ${EVIDENCE_DIR}/logs/port.log" >&2
  yq -i ".priorities[].modules[] |= (select(.name == \"${MODULE}\") | .status = \"failed\")" config/oca/port_queue.yml
  exit 1
fi

# Step 5: Smoke tests
echo ""
echo "==== Smoke Tests ===="
MODULE_PATH="${OCA_REPO_DIR}/${MODULE}"

if [[ ! -d "${MODULE_PATH}" ]]; then
  echo "ERROR: Module directory not found after port: ${MODULE_PATH}" >&2
  echo "oca-port may have placed module on a separate branch — check port log" >&2
  exit 1
fi
echo "✓ Module directory: ${MODULE_PATH}"

# Version check
VERSION=$(grep "'version'" "${MODULE_PATH}/__manifest__.py" | grep -o "'[0-9][0-9.]*'" | tr -d "'" | head -1)
if [[ ! "${VERSION}" =~ ^${TO_VERSION} ]]; then
  echo "ERROR: Version mismatch. Expected ${TO_VERSION}.x.y.z, got ${VERSION}" >&2
  exit 1
fi
echo "✓ Version: ${VERSION}"

# Python syntax
echo "Running py_compile..."
find "${MODULE_PATH}" -name "*.py" | xargs python3 -m py_compile 2>&1 | tee "${EVIDENCE_DIR}/logs/syntax.log"
echo "✓ No Python syntax errors"

# Step 6: Evidence STATUS.md
cat > "${EVIDENCE_DIR}/STATUS.md" << EOFSTATUS
# Port Status: ${MODULE}

- **From**: ${FROM_VERSION}
- **To**: ${TO_VERSION}
- **OCA Repo**: ${OCA_REPO}
- **Status**: COMPLETE
- **Timestamp**: ${TIMESTAMP}

## Verification

- [x] Module directory: addons/oca/${OCA_REPO}/${MODULE}
- [x] Version: ${VERSION}
- [x] No Python syntax errors

## Evidence

- fetch.log
- port.log
- syntax.log
EOFSTATUS

# Step 7: Update port_queue.yml
yq -i "(.priorities[].modules[] | select(.name == \"${MODULE}\")).status = \"completed\"" config/oca/port_queue.yml

echo ""
echo "==== Port Complete: ${MODULE} ===="
echo "Evidence: ${EVIDENCE_DIR}"
echo "Next: git add, commit, push"
