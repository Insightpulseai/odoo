#!/bin/bash
# =============================================================================
# hydrate_oca.sh — Idempotent OCA module hydration via git-aggregator
# =============================================================================
# SSOT:   oca-aggregate.yml (Odoo 19.0)
# Output: addons/oca/<repo>/ (one directory per OCA repo)
#
# Usage:
#   ./scripts/hydrate_oca.sh              # hydrate (skip if already done)
#   ./scripts/hydrate_oca.sh --force      # re-hydrate even if repos exist
#   OCA_JOBS=8 ./scripts/hydrate_oca.sh   # parallel jobs (default: 4)
#
# Exit Codes:
#   0 — Hydration succeeded (or skipped because already hydrated)
#   1 — git-aggregator not installed or hydration failed
#
# =============================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGGREGATE_CFG="${REPO_ROOT}/oca-aggregate.yml"
OCA_DIR="${REPO_ROOT}/addons/oca"
JOBS="${OCA_JOBS:-4}"
FORCE="${1:-}"

log() { echo "[hydrate-oca] $1"; }

# ── Pre-checks ──────────────────────────────────────────────────────────────

if [[ ! -f "$AGGREGATE_CFG" ]]; then
    log "ERROR: oca-aggregate.yml not found at $AGGREGATE_CFG"
    exit 1
fi

if ! command -v gitaggregate &>/dev/null; then
    log "ERROR: git-aggregator not installed."
    log "  Install: pip install git-aggregator"
    exit 1
fi

# ── Idempotency check ──────────────────────────────────────────────────────

# Count directories in addons/oca/ that are NOT .gitkeep
repo_count() {
    find "$OCA_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l
}

mkdir -p "$OCA_DIR"

EXISTING=$(repo_count)

if [[ "$FORCE" != "--force" && "$EXISTING" -gt 0 ]]; then
    log "Already hydrated: $EXISTING repo(s) in addons/oca/"
    log "  Use --force to re-hydrate."
    exit 0
fi

# ── Hydrate ─────────────────────────────────────────────────────────────────

log "Hydrating OCA repos from oca-aggregate.yml (jobs=$JOBS)..."
START=$(date +%s)

gitaggregate -c "$AGGREGATE_CFG" -j "$JOBS"

END=$(date +%s)
ELAPSED=$(( END - START ))
FINAL=$(repo_count)

log "Done: $FINAL repo(s) hydrated in ${ELAPSED}s"

# ── Summary ─────────────────────────────────────────────────────────────────

log "Repos:"
find "$OCA_DIR" -mindepth 1 -maxdepth 1 -type d -printf "  %f\n" | sort

exit 0
