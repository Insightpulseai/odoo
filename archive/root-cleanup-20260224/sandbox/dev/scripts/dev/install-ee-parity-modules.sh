#!/usr/bin/env bash
# scripts/dev/install-ee-parity-modules.sh
#
# Install/upgrade OCA + IPAI EE-parity modules to Odoo database
#
# Usage:
#   ./scripts/dev/install-ee-parity-modules.sh
#
# Environment variables (from .env):
#   ODOO_DB_NAME                  - Database name
#   ODOO_EE_PARITY_OCA_MODULES    - Comma-separated OCA modules
#   ODOO_EE_PARITY_IPAI_MODULES   - Comma-separated IPAI modules
#   ODOO_CONTAINER                - Docker container name (default: odoo-dev)

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════════════
# 1. VALIDATE ENVIRONMENT
# ═══════════════════════════════════════════════════════════════════════════════

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT_DIR"

if [ ! -f .env ]; then
  echo "ERROR: .env not found at $ROOT_DIR/.env" >&2
  echo "Create one from .env.example first:" >&2
  echo "  cp .env.example .env" >&2
  exit 1
fi

# Load environment variables
set -a
# shellcheck source=/dev/null
. .env
set +a

# Required variables
: "${ODOO_DB_NAME:?ODOO_DB_NAME must be set in .env}"
: "${ODOO_EE_PARITY_OCA_MODULES:?ODOO_EE_PARITY_OCA_MODULES must be set in .env}"
: "${ODOO_EE_PARITY_IPAI_MODULES:?ODOO_EE_PARITY_IPAI_MODULES must be set in .env}"

# Optional with default
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-dev}"

# ═══════════════════════════════════════════════════════════════════════════════
# 2. NORMALIZE MODULE LIST
# ═══════════════════════════════════════════════════════════════════════════════

# Concatenate OCA + IPAI modules
ALL_MODULES_RAW="${ODOO_EE_PARITY_OCA_MODULES},${ODOO_EE_PARITY_IPAI_MODULES}"

# Strip spaces, collapse multiple commas, trim leading/trailing commas
ALL_MODULES="$(echo "$ALL_MODULES_RAW" | tr -d '[:space:]' | sed 's/,,*/,/g;s/^,//;s/,$//')"

# ═══════════════════════════════════════════════════════════════════════════════
# 3. DISPLAY INSTALLATION PLAN
# ═══════════════════════════════════════════════════════════════════════════════

echo "╔════════════════════════════════════════════╗"
echo "║   Installing EE Parity OCA + IPAI Modules  ║"
echo "╚════════════════════════════════════════════╝"
echo
echo "Root directory   : $ROOT_DIR"
echo "Odoo container   : $ODOO_CONTAINER"
echo "Database         : $ODOO_DB_NAME"
echo
echo "Modules to install/update:"
echo "  $ALL_MODULES" | fold -w 70 -s | sed 's/^/  /'
echo

# ═══════════════════════════════════════════════════════════════════════════════
# 4. CONFIRM BEFORE PROCEEDING
# ═══════════════════════════════════════════════════════════════════════════════

read -rp "Proceed with installation on DB [$ODOO_DB_NAME]? [y/N] " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo "Aborted by user."
  exit 0
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 5. VERIFY CONTAINER IS RUNNING
# ═══════════════════════════════════════════════════════════════════════════════

if ! docker compose ps "$ODOO_CONTAINER" --services --filter "status=running" | grep -q "$ODOO_CONTAINER"; then
  echo "ERROR: Container '$ODOO_CONTAINER' is not running" >&2
  echo "Start it with: docker compose up -d $ODOO_CONTAINER" >&2
  exit 1
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 6. INSTALL/UPGRADE MODULES
# ═══════════════════════════════════════════════════════════════════════════════

echo
echo "Starting installation/upgrade (this may take several minutes)..."
echo

docker compose exec "$ODOO_CONTAINER" \
  odoo -d "$ODOO_DB_NAME" \
  -u "$ALL_MODULES" \
  --stop-after-init

# ═══════════════════════════════════════════════════════════════════════════════
# 7. POST-INSTALL HEALTHCHECK
# ═══════════════════════════════════════════════════════════════════════════════

echo
echo "Running post-install healthcheck..."
echo

if ./scripts/dev/ee-parity-healthcheck.sh; then
  echo
  echo "✅ EE parity modules installation/upgrade completed successfully"
  echo "✅ All modules verified as installed and up-to-date"
else
  HEALTHCHECK_EXIT=$?
  echo
  echo "⚠️  Installation completed but healthcheck failed (exit code: $HEALTHCHECK_EXIT)"
  echo
  if [ "$HEALTHCHECK_EXIT" -eq 10 ]; then
    echo "Some modules are still uninstalled. This may indicate:"
    echo "  - Missing dependencies in oca-addons/"
    echo "  - Module names in .env don't match actual module names"
    echo "  - Modules failed to install (check Odoo logs)"
  elif [ "$HEALTHCHECK_EXIT" -eq 11 ]; then
    echo "Some modules are in 'to upgrade' state. Re-run installer to complete upgrade."
  fi
  echo
  echo "Run healthcheck manually: ./scripts/dev/ee-parity-healthcheck.sh"
  exit 12
fi
