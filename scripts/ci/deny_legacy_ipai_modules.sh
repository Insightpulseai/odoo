#!/usr/bin/env bash
# scripts/ci/deny_legacy_ipai_modules.sh
#
# CI gate: Only allow the new IPAI module trio (enterprise_bridge, scout_bundle, ces_bundle)
# Blocks any legacy ipai_* modules from being committed to the repo

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Canonical allowed modules (new model only)
ALLOWED=(
  "ipai_enterprise_bridge"
  "ipai_scout_bundle"
  "ipai_ces_bundle"
)

echo "=== IPAI Module Gate ==="
echo "Checking for legacy ipai_* modules..."
echo "Allowed: ${ALLOWED[*]}"
echo

found_legacy=0

for d in "${ROOT}/addons"/*; do
  [[ -d "$d" ]] || continue
  name="$(basename "$d")"
  
  # Only check ipai_* modules
  if [[ "$name" == ipai_* ]]; then
    allowed=0
    for a in "${ALLOWED[@]}"; do
      [[ "$name" == "$a" ]] && allowed=1
    done
    
    if [[ "$allowed" -eq 0 ]]; then
      echo "❌ BLOCKED legacy module: $name"
      found_legacy=1
    else
      echo "✅ Allowed: $name"
    fi
  fi
done

echo

if [[ "$found_legacy" -eq 1 ]]; then
  echo "🚨 Legacy IPAI modules detected!"
  echo "Only these modules are allowed: ${ALLOWED[*]}"
  echo
  echo "To fix:"
  echo "  1. Remove legacy module: rm -rf addons/legacy_module_name"
  echo "  2. If installed in DB, mark as uninstalled first"
  exit 1
fi

echo "✅ OK: No legacy IPAI modules detected"
echo "All ipai_* modules comply with new architecture (enterprise_bridge, scout_bundle, ces_bundle)"
