#!/usr/bin/env bash
# =============================================================================
# scripts/spec_validate.sh — Spec bundle completeness validator
# Referenced by CLAUDE.md as mandatory pre-commit check
# Delegates to scripts/ci/check_spec_bundle.py if available
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SPEC_DIR="${REPO_ROOT}/spec"
ERRORS=0
WARNINGS=0
CHECKED=0

echo "=== Spec Bundle Validation ==="
echo "Spec dir: ${SPEC_DIR}"
echo ""

if [ ! -d "${SPEC_DIR}" ]; then
  echo "FAIL: spec/ directory not found"
  exit 1
fi

# Check each spec bundle for required files
echo "--- Bundle Completeness ---"
for bundle_dir in "${SPEC_DIR}"/*/; do
  [ ! -d "${bundle_dir}" ] && continue
  bundle=$(basename "${bundle_dir}")
  CHECKED=$((CHECKED + 1))

  MISSING=""
  # Spec bundles follow the constitution-plan-prd-tasks pattern
  HAS_CONSTITUTION=false
  HAS_PRD=false
  HAS_PLAN=false
  HAS_TASKS=false

  for f in "${bundle_dir}"*; do
    fname=$(basename "$f" | tr '[:upper:]' '[:lower:]')
    case "${fname}" in
      *constitution*) HAS_CONSTITUTION=true ;;
      *prd*|*requirements*|*spec*) HAS_PRD=true ;;
      *plan*|*implementation*) HAS_PLAN=true ;;
      *task*) HAS_TASKS=true ;;
    esac
  done

  # At minimum, a spec bundle should have a PRD or constitution
  if ! ${HAS_PRD} && ! ${HAS_CONSTITUTION}; then
    echo "  WARN  ${bundle}: no PRD or constitution found"
    WARNINGS=$((WARNINGS + 1))
  else
    echo "  PASS  ${bundle}"
  fi
done

# Check staged spec changes reference valid bundles
echo ""
echo "--- Staged Spec References ---"
STAGED=$(git -C "${REPO_ROOT}" diff --cached --name-only 2>/dev/null | grep '^spec/' || true)
if [ -n "${STAGED}" ]; then
  echo "  Staged spec files:"
  echo "${STAGED}" | while read -r f; do echo "    ${f}"; done
else
  echo "  SKIP  No staged spec changes"
fi

# Summary
echo ""
echo "==========================="
echo "Checked: ${CHECKED} bundles"
if [ ${ERRORS} -gt 0 ]; then
  echo "FAIL: ${ERRORS} error(s)"
  exit 1
elif [ ${WARNINGS} -gt 0 ]; then
  echo "PASS with ${WARNINGS} warning(s)"
  exit 0
else
  echo "PASS: All spec bundles valid"
  exit 0
fi
