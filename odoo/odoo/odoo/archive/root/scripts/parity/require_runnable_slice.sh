#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# require_runnable_slice.sh - Gate for EE parity runnable artifacts
# =============================================================================
# Gate intent: at least one executable parity slice must exist:
#   - Module with models (not just skeleton)
#   - Docker runtime config
#   - CI workflow
#   - PARITY_MATRIX.yaml
# This forces "shipped code" before scoring improvements.
# =============================================================================

FOUND=0
WARNINGS=""

echo "==> Running Runnable Slice Gate"
echo ""

# A) ipai module exists (check for actual models, not just skeleton)
if ls addons/ipai/ipai_*/models/*.py >/dev/null 2>&1; then
  echo "[OK] Found: ipai modules with models"
  FOUND=$((FOUND + 1))
else
  WARNINGS="$WARNINGS\n[WARN] No ipai modules with models found"
fi

# B) docker compose / runtime exists
if [ -f docker-compose.yml ] || [ -f docker-compose.dev.yml ] || ls docker/*.yml >/dev/null 2>&1; then
  echo "[OK] Found: Docker runtime configuration"
  FOUND=$((FOUND + 1))
else
  WARNINGS="$WARNINGS\n[WARN] No Docker runtime configuration found"
fi

# C) CI test runner exists
if ls .github/workflows/*odoo* >/dev/null 2>&1; then
  echo "[OK] Found: Odoo CI workflows"
  FOUND=$((FOUND + 1))
else
  WARNINGS="$WARNINGS\n[WARN] No Odoo CI workflows found"
fi

# D) Foundation module specifically (Phase 1 marker)
if [ -d addons/ipai/ipai_foundation ] && [ -f addons/ipai/ipai_foundation/__manifest__.py ]; then
  echo "[OK] Found: ipai_foundation module (Phase 1 vertical slice)"
  FOUND=$((FOUND + 1))
else
  WARNINGS="$WARNINGS\n[WARN] ipai_foundation module not found"
fi

# E) PARITY_MATRIX.yaml exists (overlay repo SSOT)
if [ -f docs/parity/PARITY_MATRIX.yaml ]; then
  echo "[OK] Found: PARITY_MATRIX.yaml (parity SSOT)"
  FOUND=$((FOUND + 1))
else
  WARNINGS="$WARNINGS\n[WARN] docs/parity/PARITY_MATRIX.yaml not found"
fi

# F) Dockerfile.odoo exists (overlay image)
if [ -f docker/Dockerfile.odoo ]; then
  echo "[OK] Found: Dockerfile.odoo (overlay image)"
  FOUND=$((FOUND + 1))
else
  WARNINGS="$WARNINGS\n[WARN] docker/Dockerfile.odoo not found"
fi

echo ""

# Require at least 3 of 6 checks to pass
MIN_REQUIRED=3
if [ "$FOUND" -lt "$MIN_REQUIRED" ]; then
  echo "ERROR: Insufficient runnable parity artifacts detected."
  echo "Found: $FOUND / 6 (minimum required: $MIN_REQUIRED)"
  echo ""
  echo "Required artifacts (choose at least $MIN_REQUIRED):"
  echo "  1. addons/ipai/ipai_*/models/*.py - ipai module with models"
  echo "  2. docker-compose*.yml or docker/*.yml - Docker runtime"
  echo "  3. .github/workflows/*odoo*.yml - CI workflows"
  echo "  4. addons/ipai/ipai_foundation/ - Phase 1 vertical slice"
  echo "  5. docs/parity/PARITY_MATRIX.yaml - Parity SSOT"
  echo "  6. docker/Dockerfile.odoo - Overlay image"
  echo ""
  if [ -n "$WARNINGS" ]; then
    echo "Warnings:"
    echo -e "$WARNINGS"
  fi
  exit 1
fi

echo "OK: Runnable parity slice detected ($FOUND / 6 artifacts found)"
echo ""

# Print warnings if any
if [ -n "$WARNINGS" ]; then
  echo "Warnings (non-blocking):"
  echo -e "$WARNINGS"
fi
