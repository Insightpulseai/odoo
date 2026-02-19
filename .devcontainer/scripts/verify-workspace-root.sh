#!/usr/bin/env bash
# verify-workspace-root.sh — assert /workspaces/odoo invariants
# Called by: post-start.sh, CI, agents
# Fails fast if the workspace mount or key addon lanes are missing.
set -euo pipefail

ROOT="/workspaces/odoo"

echo "[verify] checking workspace root: ${ROOT}"
test -d "${ROOT}" || { echo "ERROR: ${ROOT} does not exist (bind-mount missing)"; exit 1; }
test -d "${ROOT}/addons" || { echo "ERROR: ${ROOT}/addons not found"; exit 1; }

echo "[verify] checking expected addon lanes"
test -d "${ROOT}/addons/ipai" || { echo "ERROR: ${ROOT}/addons/ipai missing"; exit 1; }
if [ ! -d "${ROOT}/addons/oca" ]; then
  echo "[warn] ${ROOT}/addons/oca missing (may be empty in some setups)"
fi

echo "[verify] checking no legacy /mnt/extra-addons references"
SEARCH_DIRS=()
for d in "${ROOT}/.devcontainer" "${ROOT}/config" "${ROOT}/docker"; do
  [ -d "${d}" ] && SEARCH_DIRS+=("${d}")
done

if [ ${#SEARCH_DIRS[@]} -gt 0 ]; then
  if command -v rg >/dev/null 2>&1; then
    if rg -n "/mnt/extra-addons" "${SEARCH_DIRS[@]}" 2>/dev/null; then
      echo "ERROR: legacy /mnt/extra-addons reference found — use /workspaces/odoo/addons/*"
      exit 1
    fi
  else
    if grep -rn "/mnt/extra-addons" "${SEARCH_DIRS[@]}" 2>/dev/null; then
      echo "ERROR: legacy /mnt/extra-addons reference found — use /workspaces/odoo/addons/*"
      exit 1
    fi
  fi
fi

echo "[ok] workspace root invariant holds"
