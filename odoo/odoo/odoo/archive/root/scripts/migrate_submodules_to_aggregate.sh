#!/usr/bin/env bash
# =============================================================================
# migrate_submodules_to_aggregate.sh
# =============================================================================
# Removes all stale git submodule entries (18.0) and cleans up the repo
# for the gitaggregate-based OCA dependency model.
#
# WHAT THIS DOES:
#   1. Deinits all submodules under external-src/, vendor/oca/, branding/
#   2. Removes .gitmodules entries
#   3. Removes submodule paths from .git/config
#   4. Removes the empty directories
#   5. Removes .git/modules/<path> cache
#
# SAFE TO RUN: This only removes empty/stale submodule checkouts.
# The replacement is: gitaggregate -c oca-aggregate.yml
#
# Usage:
#   ./scripts/migrate_submodules_to_aggregate.sh          # dry-run
#   ./scripts/migrate_submodules_to_aggregate.sh --apply   # execute
# =============================================================================
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

DRY_RUN=true
if [[ "${1:-}" == "--apply" ]]; then
  DRY_RUN=false
fi

# ---------------------------------------------------------------------------
# Collect all submodule paths from .gitmodules
# ---------------------------------------------------------------------------
if [[ ! -f .gitmodules ]]; then
  echo "No .gitmodules found — nothing to migrate."
  exit 0
fi

SUBMODULE_PATHS=()
while IFS= read -r line; do
  path="${line#*= }"
  SUBMODULE_PATHS+=("$path")
done < <(grep 'path = ' .gitmodules)

echo "Found ${#SUBMODULE_PATHS[@]} submodule entries to remove:"
printf "  %s\n" "${SUBMODULE_PATHS[@]}"
echo ""

if $DRY_RUN; then
  echo "=== DRY RUN === (pass --apply to execute)"
  echo ""
  echo "Would execute:"
  echo "  1. git submodule deinit --force <path>  (for each)"
  echo "  2. git rm --cached <path>               (for each)"
  echo "  3. rm -rf .git/modules/<path>           (for each)"
  echo "  4. rm -rf <path>                        (for each)"
  echo "  5. Remove .gitmodules file"
  echo "  6. git add -A"
  echo ""
  echo "After migration, run:"
  echo "  pip install git-aggregator"
  echo "  gitaggregate -c oca-aggregate.yml -j 4"
  exit 0
fi

echo "Removing submodules..."

for path in "${SUBMODULE_PATHS[@]}"; do
  echo "  [-] $path"

  # Deinit (ignore errors if already deinited)
  git submodule deinit --force "$path" 2>/dev/null || true

  # Remove from index
  git rm --cached "$path" 2>/dev/null || true

  # Remove .git/modules cache
  git_modules_path=".git/modules/$path"
  if [[ -d "$git_modules_path" ]]; then
    rm -rf "$git_modules_path"
  fi

  # Remove the directory
  if [[ -d "$path" ]]; then
    rm -rf "$path"
  fi
done

# Remove .gitmodules entirely
echo ""
echo "Removing .gitmodules..."
git rm -f .gitmodules 2>/dev/null || rm -f .gitmodules

# Clean up empty parent directories
for dir in external-src vendor/oca/OCA vendor/oca vendor branding; do
  if [[ -d "$dir" ]] && [[ -z "$(ls -A "$dir" 2>/dev/null)" ]]; then
    echo "  Removing empty directory: $dir/"
    rmdir "$dir" 2>/dev/null || true
  fi
done

# Also clean nested empties
find external-src vendor branding -type d -empty -delete 2>/dev/null || true

echo ""
echo "=== Migration complete ==="
echo ""
echo "Next steps:"
echo "  1. pip install git-aggregator"
echo "  2. gitaggregate -c oca-aggregate.yml -j 4"
echo "  3. ./scripts/gen_addons_path.sh"
echo "  4. git add -A && git commit -m 'chore(oca): migrate from submodules to gitaggregate'"
