#!/usr/bin/env bash
# =============================================================================
# verify_generated_odoo_artifacts.sh — CI drift gate
# =============================================================================
# Regenerates addons-path artifacts and fails if the committed versions
# don't match the generator output. This makes hand-editing
# infra/odoo/addons-path.* effectively impossible.
#
# Usage:
#   ./scripts/verify_generated_odoo_artifacts.sh
#   make addons-path-check   # equivalent Makefile target
#
# What it checks:
#   1. scripts/gen_addons_path.sh is executable
#   2. Regeneration produces identical output to committed files
#   3. No uncommitted drift in generated artifacts
# =============================================================================
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

GEN_FILES=(
  "infra/odoo/addons-path.txt"
  "infra/odoo/addons-path.env"
)

GENERATOR="scripts/gen_addons_path.sh"

echo "== verify generated Odoo artifacts =="

# --- Preconditions ---
if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git not found"
  exit 1
fi

if [[ ! -x "$GENERATOR" ]]; then
  echo "ERROR: $GENERATOR is not executable"
  echo "Fix: chmod +x $GENERATOR"
  exit 1
fi

# --- Regenerate ---
echo "+ $GENERATOR"
./"$GENERATOR"

# --- Diff ---
echo ""
echo "+ git diff --exit-code -- ${GEN_FILES[*]}"
if ! git diff --exit-code -- "${GEN_FILES[@]}"; then
  echo ""
  echo "ERROR: generated artifacts drift from what the generator produces."
  echo ""
  echo "Fix: run locally, then commit the regenerated files:"
  echo "  ./scripts/gen_addons_path.sh"
  echo "  git add ${GEN_FILES[*]}"
  echo "  git commit --amend  # or new commit"
  exit 1
fi

echo "OK: generated artifacts match regeneration output."
