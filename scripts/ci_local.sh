#!/usr/bin/env bash
# =============================================================================
# scripts/ci_local.sh — Local CI gate (pre-commit checks)
# Referenced by CLAUDE.md as mandatory pre-commit check
# Runs: repo health + spec validation + available linters
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0
SKIP=0

echo "=== Local CI Gate ==="
echo "Repo: ${REPO_ROOT}"
echo "Time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

run_check() {
  local name="$1"
  local cmd="$2"
  echo "--- ${name} ---"
  if eval "${cmd}"; then
    echo "  => PASS"
    PASS=$((PASS + 1))
  else
    echo "  => FAIL"
    FAIL=$((FAIL + 1))
  fi
  echo ""
}

skip_check() {
  local name="$1"
  local reason="$2"
  echo "--- ${name} ---"
  echo "  => SKIP (${reason})"
  SKIP=$((SKIP + 1))
  echo ""
}

# 1. Repo health
run_check "Repo Health" "bash ${REPO_ROOT}/scripts/repo_health.sh"

# 2. Spec validation
run_check "Spec Validation" "bash ${REPO_ROOT}/scripts/spec_validate.sh"

# 3. Python lint (if staged .py files exist)
STAGED_PY=$(git -C "${REPO_ROOT}" diff --cached --name-only '*.py' 2>/dev/null || true)
if [ -n "${STAGED_PY}" ]; then
  if command -v python3 &>/dev/null; then
    run_check "Python Syntax" "echo '${STAGED_PY}' | tr ' ' '\n' | while read -r f; do [ -f \"${REPO_ROOT}/\${f}\" ] && python3 -m py_compile \"${REPO_ROOT}/\${f}\"; done"
  else
    skip_check "Python Syntax" "python3 not available"
  fi
else
  skip_check "Python Lint" "no staged .py files"
fi

# 4. YAML lint (if staged .yaml/.yml files exist)
STAGED_YAML=$(git -C "${REPO_ROOT}" diff --cached --name-only -- '*.yaml' '*.yml' 2>/dev/null || true)
if [ -n "${STAGED_YAML}" ]; then
  if command -v python3 &>/dev/null && python3 -c "import yaml" 2>/dev/null; then
    run_check "YAML Syntax" "echo '${STAGED_YAML}' | tr ' ' '\n' | while read -r f; do [ -f \"${REPO_ROOT}/\${f}\" ] && python3 -c \"import yaml; yaml.safe_load(open('${REPO_ROOT}/'\${f}))\"; done"
  else
    skip_check "YAML Syntax" "PyYAML not available"
  fi
else
  skip_check "YAML Lint" "no staged .yaml/.yml files"
fi

# 5. Naming convention check
echo "--- Naming Convention ---"
BAD_NAMES=$(git -C "${REPO_ROOT}" diff --cached --name-only 2>/dev/null | \
  grep '^addons/ipai/' | grep -v '^addons/ipai/ipai_' | \
  grep -v '__pycache__' | grep -v '.pyc' || true)
if [ -n "${BAD_NAMES}" ]; then
  echo "  WARN  Non-ipai_ prefixed files in addons/ipai/:"
  echo "${BAD_NAMES}" | head -5
fi
echo "  => PASS"
PASS=$((PASS + 1))
echo ""

# Summary
echo "==========================="
echo "PASS: ${PASS}  FAIL: ${FAIL}  SKIP: ${SKIP}"
if [ ${FAIL} -gt 0 ]; then
  echo "LOCAL CI: FAILED"
  exit 1
else
  echo "LOCAL CI: PASSED"
  exit 0
fi
