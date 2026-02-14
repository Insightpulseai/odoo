#!/usr/bin/env bash
# =============================================================================
# Repo Chore Runner (Idempotent)
# =============================================================================
# Single entrypoint for all repo hygiene tasks:
#   1. Regenerate spec.md repo tree
#   2. Run unified lint checks
#   3. Validate no deprecated addons referenced
#   4. Validate agent registry (if agents/registry/agents.json exists)
#
# Designed to be idempotent: running twice produces zero diff.
#
# Usage:
#   ./scripts/chore_repo.sh           # Run all chores
#   ./scripts/chore_repo.sh --check   # Dry-run: report drift without fixing
#
# Exit Codes:
#   0 - All chores passed
#   1 - Issues found
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

CHECK_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --check) CHECK_ONLY=1 ;;
  esac
done

ERRORS=0

log_section() {
  echo ""
  echo "========================================"
  echo "  $1"
  echo "========================================"
  echo ""
}

# ---------------------------------------------------------------------------
# 1. Regenerate spec.md repo tree
# ---------------------------------------------------------------------------
log_section "1/4 Repo Tree Regen"

if [[ -x "${SCRIPT_DIR}/gen_repo_tree.sh" ]]; then
  "${SCRIPT_DIR}/gen_repo_tree.sh"

  if ! git -C "${ROOT_DIR}" diff --quiet -- spec.md 2>/dev/null; then
    if [[ "$CHECK_ONLY" == "1" ]]; then
      echo "DRIFT DETECTED: spec.md tree is out of date"
      ERRORS=$((ERRORS + 1))
    else
      echo "spec.md tree updated (will need commit)"
    fi
  else
    echo "spec.md tree is up to date."
  fi
else
  echo "WARN: scripts/gen_repo_tree.sh not found or not executable. Skipping."
fi

# ---------------------------------------------------------------------------
# 2. Run lint checks
# ---------------------------------------------------------------------------
log_section "2/4 Lint Checks"

if [[ -x "${SCRIPT_DIR}/lint_all.sh" ]]; then
  "${SCRIPT_DIR}/lint_all.sh" all || ERRORS=$((ERRORS + 1))
else
  echo "WARN: scripts/lint_all.sh not found or not executable. Skipping."
fi

# ---------------------------------------------------------------------------
# 3. Validate deprecated addons
# ---------------------------------------------------------------------------
log_section "3/4 Deprecated Addons Check"

if [[ -x "${SCRIPT_DIR}/validate_no_deprecated_installed.sh" ]]; then
  "${SCRIPT_DIR}/validate_no_deprecated_installed.sh" || ERRORS=$((ERRORS + 1))
else
  echo "WARN: scripts/validate_no_deprecated_installed.sh not found. Skipping."
fi

# ---------------------------------------------------------------------------
# 4. Validate agent registry (optional)
# ---------------------------------------------------------------------------
log_section "4/4 Agent Registry Check"

REGISTRY="${ROOT_DIR}/agents/registry/agents.json"
if [[ -f "${REGISTRY}" ]]; then
  if [[ -f "${SCRIPT_DIR}/agentic/validate_agent_registry.py" ]]; then
    python3 "${SCRIPT_DIR}/agentic/validate_agent_registry.py" || ERRORS=$((ERRORS + 1))
  else
    echo "WARN: scripts/agentic/validate_agent_registry.py not found. Skipping."
  fi

  if [[ -f "${SCRIPT_DIR}/agentic/validate_memory_contracts.py" ]]; then
    python3 "${SCRIPT_DIR}/agentic/validate_memory_contracts.py" || ERRORS=$((ERRORS + 1))
  else
    echo "WARN: scripts/agentic/validate_memory_contracts.py not found. Skipping."
  fi
else
  echo "No agents/registry/agents.json found. Skipping agent validation."
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "========================================"
echo "  CHORE SUMMARY"
echo "========================================"
echo ""
if [[ $ERRORS -gt 0 ]]; then
  echo "FAILED: ${ERRORS} chore check(s) had issues."
  echo ""
  echo "Fix issues and re-run: ./scripts/chore_repo.sh"
  exit 1
else
  echo "ALL CHORES PASSED"
  echo ""
  if [[ "$CHECK_ONLY" == "0" ]]; then
    echo "If spec.md was regenerated, remember to commit:"
    echo "  git add spec.md && git commit -m 'chore(repo): regen spec.md tree'"
  fi
  exit 0
fi
