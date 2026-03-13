#!/usr/bin/env bash
# =============================================================================
# sync_oca.sh — Clone/update all OCA repos via gitaggregate
# =============================================================================
# Wrapper around git-aggregator that:
#   1. Ensures addons/oca/ exists and is writable
#   2. Runs gitaggregate to clone/update all OCA repos
#   3. Regenerates the addons-path for Odoo
#
# SSOT: oca-aggregate.yml (root of repo)
# Output: addons/oca/<repo>/ (gitignored, never committed)
#
# Usage:
#   ./scripts/sync_oca.sh            # full sync (parallel)
#   ./scripts/sync_oca.sh --single web  # sync one repo
#   ./scripts/sync_oca.sh --status   # show sync status
#
# Called by:
#   - CI: .github/workflows/prod-odoo-modules.yml
#   - Deploy: .github/workflows/deploy-do-oca.yml
#   - Dev: make oca-aggregate
# =============================================================================
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT"

AGGREGATE_FILE="oca-aggregate.yml"
OCA_DIR="addons/oca"
JOBS="${OCA_SYNC_JOBS:-4}"

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------

if [[ ! -f "$AGGREGATE_FILE" ]]; then
  echo "ERROR: $AGGREGATE_FILE not found in repo root"
  exit 1
fi

if ! command -v gitaggregate &>/dev/null; then
  echo "ERROR: gitaggregate not found. Install with: pip install git-aggregator"
  exit 1
fi

# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

case "${1:-sync}" in
  --status|status)
    echo "OCA Sync Status"
    echo "==============="
    echo ""
    if [[ ! -d "$OCA_DIR" ]]; then
      echo "  addons/oca/ does not exist — run: ./scripts/sync_oca.sh"
      exit 0
    fi
    repo_count=0
    module_count=0
    for repo_dir in "$OCA_DIR"/*/; do
      [[ -d "$repo_dir" ]] || continue
      repo_name="$(basename "$repo_dir")"
      mods=$(find "$repo_dir" -maxdepth 2 -name "__manifest__.py" 2>/dev/null | wc -l)
      if [[ "$mods" -gt 0 ]]; then
        branch=""
        if [[ -d "$repo_dir/.git" ]]; then
          branch="$(git -C "$repo_dir" branch --show-current 2>/dev/null || echo "detached")"
        fi
        printf "  %-30s %3d modules  (%s)\n" "$repo_name" "$mods" "${branch:-no .git}"
        repo_count=$((repo_count + 1))
        module_count=$((module_count + mods))
      fi
    done
    echo ""
    echo "  Total: $repo_count repos, $module_count modules"
    exit 0
    ;;

  --single|single)
    REPO="${2:?Usage: sync_oca.sh --single <repo-name>}"
    echo "Syncing single OCA repo: $REPO"
    gitaggregate -c "$AGGREGATE_FILE" -d "./$OCA_DIR/$REPO"
    echo "Done: $OCA_DIR/$REPO"
    exit 0
    ;;

  sync|--sync|"")
    # Fall through to main sync logic below
    ;;

  *)
    echo "Usage: sync_oca.sh [sync|--single <repo>|--status]"
    exit 1
    ;;
esac

# ---------------------------------------------------------------------------
# Main sync: clone/update all OCA repos
# ---------------------------------------------------------------------------

echo "Syncing OCA repos from $AGGREGATE_FILE..."
echo "  Output: $OCA_DIR/"
echo "  Parallel jobs: $JOBS"
echo ""

# Ensure target directory exists
mkdir -p "$OCA_DIR"

# Run gitaggregate
gitaggregate -c "$AGGREGATE_FILE" -j "$JOBS"

# ---------------------------------------------------------------------------
# Post-sync: regenerate addons path
# ---------------------------------------------------------------------------

if [[ -x scripts/gen_addons_path.sh ]]; then
  echo ""
  echo "Regenerating addons path..."
  ./scripts/gen_addons_path.sh
fi

# Count results
repo_count=0
module_count=0
for repo_dir in "$OCA_DIR"/*/; do
  [[ -d "$repo_dir" ]] || continue
  mods=$(find "$repo_dir" -maxdepth 2 -name "__manifest__.py" 2>/dev/null | wc -l)
  if [[ "$mods" -gt 0 ]]; then
    repo_count=$((repo_count + 1))
    module_count=$((module_count + mods))
  fi
done

echo ""
echo "OCA sync complete: $repo_count repos, $module_count modules available"
