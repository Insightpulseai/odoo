#!/usr/bin/env bash
set -euo pipefail

# Gate intent: at least one executable parity slice must exist (module + test or docker runner).
# This forces "shipped code" before scoring improvements.

FOUND=0

# A) ipai module exists (check for actual models, not just skeleton)
if ls addons/ipai/ipai_*/models/*.py >/dev/null 2>&1; then
  echo "Found: ipai modules with models"
  FOUND=1
fi

# B) docker compose / runtime exists
if [ -f docker-compose.yml ] || ls docker/*.yml >/dev/null 2>&1; then
  echo "Found: Docker runtime configuration"
  FOUND=1
fi

# C) CI test runner exists
if ls .github/workflows/*odoo* >/dev/null 2>&1; then
  echo "Found: Odoo CI workflows"
  FOUND=1
fi

# D) Foundation module specifically (Phase 1 marker)
if [ -d addons/ipai/ipai_foundation ] && [ -f addons/ipai/ipai_foundation/__manifest__.py ]; then
  echo "Found: ipai_foundation module (Phase 1 vertical slice)"
  FOUND=1
fi

if [ "$FOUND" -eq 0 ]; then
  echo "ERROR: No runnable parity slice detected."
  echo "Required: ipai addon with models, runtime config, or odoo workflow."
  echo "Add at least one installable module + CI smoke test."
  exit 1
fi

echo "OK: Runnable parity slice detected."
