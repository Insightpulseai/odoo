#!/usr/bin/env bash
# ===========================================================================
# Odoo Module Upgrade Script
# Idempotent runner for upgrading installed Odoo modules
# ===========================================================================
set -euo pipefail

# Configuration (override via environment)
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-core}"
ODOO_DB="${ODOO_DB:-odoo_core}"
ODOO_CONF="${ODOO_CONF:-/etc/odoo/odoo.conf}"
ADDONS_PATH="${ADDONS_PATH:-/mnt/extra-addons}"

# Modules to upgrade:
# - "all" = upgrade all installed modules (safe but slower)
# - comma-separated list = upgrade only those modules
MODULES="${MODULES:-all}"

# Logging
log() { echo "[odoo-upgrade] $(date '+%Y-%m-%d %H:%M:%S') $*"; }

log "Starting module upgrade..."
log "Container: ${ODOO_CONTAINER}"
log "Database: ${ODOO_DB}"
log "Modules: ${MODULES}"

# Verify container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${ODOO_CONTAINER}$"; then
    log "ERROR: Container ${ODOO_CONTAINER} is not running"
    exit 1
fi

# Build odoo command arguments
ARGS=(-d "${ODOO_DB}" -c "${ODOO_CONF}" --stop-after-init)

if [[ "${MODULES}" == "all" ]]; then
    # Upgrade all currently installed modules
    ARGS+=(-u all)
else
    # Upgrade specific modules
    ARGS+=(-u "${MODULES}")
fi

# Run upgrade
log "Executing: docker exec ${ODOO_CONTAINER} odoo ${ARGS[*]}"
if docker exec -i "${ODOO_CONTAINER}" odoo "${ARGS[@]}"; then
    log "Module upgrade completed successfully"
else
    log "ERROR: Module upgrade failed with exit code $?"
    exit 1
fi

# Optional: verify no pending upgrades
log "Verifying module states..."
docker exec -i "${ODOO_CONTAINER}" odoo -d "${ODOO_DB}" -c "${ODOO_CONF}" --no-http --stop-after-init --shell <<'PY'
pending = env['ir.module.module'].search([('state', 'in', ['to upgrade', 'to install', 'to remove'])])
if pending:
    print(f"[WARNING] {len(pending)} modules still pending:", pending.mapped('name'))
else:
    print("[OK] No pending module operations")
PY

log "Done."
