#!/usr/bin/env bash
# =============================================================================
# Unified Lint Runner
# =============================================================================
# Single entrypoint for all lint checks: Python, YAML, Markdown.
# Delegates to existing tools; adds YAML and Markdown lint on top.
#
# Usage:
#   ./scripts/lint_all.sh          # Run all linters
#   ./scripts/lint_all.sh python   # Python only
#   ./scripts/lint_all.sh yaml     # YAML only
#   ./scripts/lint_all.sh markdown # Markdown only
#   ./scripts/lint_all.sh --ci     # CI mode (strict, non-zero exit on any failure)
#
# Exit Codes:
#   0 - All lints passed
#   1 - Lint errors found
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

CI_MODE=0
COMMAND="${1:-all}"

for arg in "$@"; do
  case "$arg" in
    --ci) CI_MODE=1; shift ;;
  esac
done
COMMAND="${1:-all}"

ERRORS=0

log_section() {
  echo ""
  echo "========================================"
  echo "  $1"
  echo "========================================"
  echo ""
}

# ---------------------------------------------------------------------------
# Python lint (delegates to existing scripts/lint.sh or runs ruff directly)
# ---------------------------------------------------------------------------
run_python_lint() {
  log_section "Python Lint"

  if command -v ruff &>/dev/null; then
    echo "Running ruff check..."
    ruff check "${ROOT_DIR}/addons" "${ROOT_DIR}/scripts" --config "${ROOT_DIR}/pyproject.toml" || ERRORS=$((ERRORS + 1))
  elif [[ -f "${SCRIPT_DIR}/lint.sh" ]]; then
    echo "Delegating to scripts/lint.sh python..."
    "${SCRIPT_DIR}/lint.sh" python || ERRORS=$((ERRORS + 1))
  else
    echo "WARN: No Python linter found (ruff or pre-commit). Skipping."
  fi
}

# ---------------------------------------------------------------------------
# YAML lint
# ---------------------------------------------------------------------------
run_yaml_lint() {
  log_section "YAML Lint"

  if command -v yamllint &>/dev/null; then
    echo "Running yamllint..."
    yamllint -c "${ROOT_DIR}/.yamllint.yml" \
      "${ROOT_DIR}/.github/" \
      "${ROOT_DIR}/docker-compose*.yml" \
      "${ROOT_DIR}/agents/" \
      2>&1 || ERRORS=$((ERRORS + 1))
  else
    echo "WARN: yamllint not found. Install with: pip install yamllint"
    if [[ "$CI_MODE" == "1" ]]; then
      ERRORS=$((ERRORS + 1))
    fi
  fi
}

# ---------------------------------------------------------------------------
# Markdown lint
# ---------------------------------------------------------------------------
run_markdown_lint() {
  log_section "Markdown Lint"

  if command -v markdownlint-cli2 &>/dev/null; then
    echo "Running markdownlint-cli2..."
    cd "${ROOT_DIR}"
    markdownlint-cli2 "**/*.md" 2>&1 || ERRORS=$((ERRORS + 1))
  elif command -v markdownlint &>/dev/null; then
    echo "Running markdownlint..."
    cd "${ROOT_DIR}"
    markdownlint '**/*.md' --ignore node_modules --ignore external-src --ignore addons/oca --ignore vendor 2>&1 || ERRORS=$((ERRORS + 1))
  else
    echo "WARN: markdownlint not found. Install with: npm install -g markdownlint-cli2"
    if [[ "$CI_MODE" == "1" ]]; then
      echo "Skipping markdown lint (not installed in CI)."
    fi
  fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
log_section "Unified Lint Runner"
echo "Mode: $(if [[ "$CI_MODE" == "1" ]]; then echo 'CI (strict)'; else echo 'Local'; fi)"
echo "Scope: ${COMMAND}"

case "$COMMAND" in
  python)   run_python_lint ;;
  yaml)     run_yaml_lint ;;
  markdown) run_markdown_lint ;;
  all)
    run_python_lint
    run_yaml_lint
    run_markdown_lint
    ;;
  *)
    echo "Unknown command: ${COMMAND}"
    echo "Usage: $0 [all|python|yaml|markdown] [--ci]"
    exit 2
    ;;
esac

echo ""
echo "========================================"
if [[ $ERRORS -gt 0 ]]; then
  echo "  LINT FAILED: ${ERRORS} check(s) had errors"
  echo "========================================"
  exit 1
else
  echo "  ALL LINTS PASSED"
  echo "========================================"
  exit 0
fi
