#!/bin/bash
# =============================================================================
# 05-hydrate-oca.sh — Auto-hydrate OCA repos at container startup (dev only)
# =============================================================================
# Runs BEFORE preflight (90-preflight.sh) and logging (10-log-env.sh by number
# but this script is intentionally 05 to hydrate before anything checks paths).
#
# Gated by environment variable:
#   OCA_HYDRATE=1   Enable auto-hydration at startup (default: disabled)
#
# Behavior:
#   - If OCA_HYDRATE != 1, skip silently.
#   - If addons/oca/ already has repos, skip (idempotent).
#   - If git-aggregator is not installed, warn and continue (non-fatal).
#
# This should be used in DEV only. Production should bake OCA at build time.
# =============================================================================

set -euo pipefail

if [[ "${OCA_HYDRATE:-0}" != "1" ]]; then
    exit 0
fi

echo "[hydrate-oca] OCA_HYDRATE=1 — checking if hydration needed..."

OCA_DIR="${OCA_ADDONS_PATH:-/mnt/oca}"
AGGREGATE_CFG="${OCA_AGGREGATE_CFG:-/opt/odoo/oca-aggregate.yml}"

# Fallback: try repo-relative path if running from mounted source
if [[ ! -f "$AGGREGATE_CFG" ]]; then
    # Try common mount points
    for candidate in /workspaces/odoo/oca-aggregate.yml /opt/odoo/oca-aggregate.yml; do
        if [[ -f "$candidate" ]]; then
            AGGREGATE_CFG="$candidate"
            break
        fi
    done
fi

if [[ ! -f "$AGGREGATE_CFG" ]]; then
    echo "[hydrate-oca] WARN: oca-aggregate.yml not found, skipping hydration"
    exit 0
fi

if ! command -v gitaggregate &>/dev/null; then
    echo "[hydrate-oca] WARN: git-aggregator not installed, skipping hydration"
    echo "[hydrate-oca]   Install: pip install git-aggregator"
    exit 0
fi

# Count existing repos (directories, not files)
EXISTING=$(find "$OCA_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)

if [[ "$EXISTING" -gt 0 ]]; then
    echo "[hydrate-oca] Already hydrated: $EXISTING repo(s) in $OCA_DIR"
    exit 0
fi

echo "[hydrate-oca] Hydrating OCA repos..."
JOBS="${OCA_JOBS:-4}"

if gitaggregate -c "$AGGREGATE_CFG" -j "$JOBS"; then
    FINAL=$(find "$OCA_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
    echo "[hydrate-oca] Done: $FINAL repo(s) hydrated"
else
    echo "[hydrate-oca] WARN: git-aggregator failed (non-fatal, continuing startup)"
fi

exit 0
