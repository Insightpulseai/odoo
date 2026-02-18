#!/usr/bin/env bash
# check_root_moves_backcompat.sh
#
# Fail if any code references the OLD root filenames that were moved in the
# root-hygiene PR (chore(repo): root cleanup 2026-02-17).
#
# Old path → New path
#   figma.config.json          → figma/figma.config.json
#   figma-make-dev.yaml        → figma/figma-make-dev.yaml
#   aiux_ship_manifest.yml     → config/aiux_ship_manifest.yml
#   devserver.config.json      → config/devserver.config.json
#   branch_protection.json     → docs/architecture/branch_protection.json
#   superclaude_bridge.yaml    → .claude/superclaude_bridge.yaml
#
# Usage: ./scripts/ci/check_root_moves_backcompat.sh
# Exit 0 = clean, Exit 1 = stale references found.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Directories/files to exclude from the search (the canonical destinations
# themselves, manifests that document the moves, and this script).
EXCLUDE_ARGS=(
  "--glob=!figma/figma.config.json"
  "--glob=!figma/figma-make-dev.yaml"
  "--glob=!config/aiux_ship_manifest.yml"
  "--glob=!config/devserver.config.json"
  "--glob=!docs/architecture/branch_protection.json"
  "--glob=!.claude/superclaude_bridge.yaml"
  "--glob=!docs/architecture/ROOT_ALLOWLIST.md"
  "--glob=!docs/architecture/REPO_HYGIENE_ROOT_CLEANUP.md"
  "--glob=!reports/repo_hygiene/"
  "--glob=!scripts/ci/check_root_moves_backcompat.sh"
  "--glob=!.git/"
  "--glob=!node_modules/"
  "--glob=!.venv/"
  "--glob=!__pycache__/"
)

# Pattern: bare filename references that would resolve to the old root location.
# The negative lookahead for slashes prevents matching the new canonical paths.
PATTERN='(^|[^/a-zA-Z0-9_.-])(figma\.config\.json|figma-make-dev\.yaml|aiux_ship_manifest\.yml|devserver\.config\.json|branch_protection\.json|superclaude_bridge\.yaml)([^/]|$)'

echo "Checking for stale references to moved root files..."

if rg --hidden --no-heading -n "${EXCLUDE_ARGS[@]}" "$PATTERN" "$REPO_ROOT" 2>/dev/null; then
  echo ""
  echo "ERROR: References to old root filenames found."
  echo "Update these references to use the new canonical paths:"
  echo "  figma.config.json        → figma/figma.config.json"
  echo "  figma-make-dev.yaml      → figma/figma-make-dev.yaml"
  echo "  aiux_ship_manifest.yml   → config/aiux_ship_manifest.yml"
  echo "  devserver.config.json    → config/devserver.config.json"
  echo "  branch_protection.json   → docs/architecture/branch_protection.json"
  echo "  superclaude_bridge.yaml  → .claude/superclaude_bridge.yaml"
  exit 1
fi

echo "✅ No stale root-move references found."
