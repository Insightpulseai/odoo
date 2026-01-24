#!/usr/bin/env bash
# ===========================================================================
# Odoo Post-Upgrade Seed Script
# Applies idempotent seed/reference data after module upgrades
# ===========================================================================
set -euo pipefail

# Configuration (override via environment)
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo-core}"
ODOO_DB="${ODOO_DB:-odoo_core}"
ODOO_CONF="${ODOO_CONF:-/etc/odoo/odoo.conf}"

# Seed marker key (versioned for re-runnability)
SEED_KEY="${SEED_KEY:-seed:core_reference:v1}"

# Environment control
ENVIRONMENT="${ENVIRONMENT:-prod}"
ALLOW_DEMO_DATA="${ALLOW_DEMO_DATA:-false}"

# Logging
log() { echo "[odoo-seed] $(date '+%Y-%m-%d %H:%M:%S') $*"; }

log "Starting post-upgrade seeding..."
log "Container: ${ODOO_CONTAINER}"
log "Database: ${ODOO_DB}"
log "Seed key: ${SEED_KEY}"
log "Environment: ${ENVIRONMENT}"

# Verify container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${ODOO_CONTAINER}$"; then
    log "ERROR: Container ${ODOO_CONTAINER} is not running"
    exit 1
fi

# Run seed script via Odoo shell
docker exec -i "${ODOO_CONTAINER}" odoo -d "${ODOO_DB}" -c "${ODOO_CONF}" --no-http --stop-after-init --shell <<PY
import os
from datetime import datetime

key = "${SEED_KEY}"
environment = "${ENVIRONMENT}"
allow_demo = "${ALLOW_DEMO_DATA}".lower() == "true"

Param = env['ir.config_parameter'].sudo()

# Check if seed already applied
if Param.get_param(key):
    print(f"[odoo-seed] Seed already applied: {key}")
    print(f"[odoo-seed] Applied at: {Param.get_param(key + ':applied_at', 'unknown')}")
else:
    print(f"[odoo-seed] Applying seed: {key}")

    # Record seed application
    Param.set_param(key, "1")
    Param.set_param(key + ":applied_at", datetime.now().isoformat())
    Param.set_param(key + ":environment", environment)

    # ===========================================================================
    # REFERENCE DATA (always applied)
    # ===========================================================================

    # Example: Ensure system parameters are set
    config_params = {
        "ipai.ops.system": "erp.insightpulseai.net",
        "ipai.ops.environment": environment,
        "ipai.ops.ssot.enabled": "1",
    }

    for param_key, param_value in config_params.items():
        if not Param.get_param(param_key):
            Param.set_param(param_key, param_value)
            print(f"[odoo-seed] Set parameter: {param_key}={param_value}")
        else:
            print(f"[odoo-seed] Parameter exists: {param_key}")

    # Example: Ensure default company configuration
    company = env.ref('base.main_company', raise_if_not_found=False)
    if company:
        print(f"[odoo-seed] Main company: {company.name}")

    # ===========================================================================
    # DEMO DATA (only in non-prod environments)
    # ===========================================================================

    if allow_demo and environment != "prod":
        print("[odoo-seed] Applying demo data (non-prod only)...")

        # Example: Create demo partner
        demo_partner = env['res.partner'].search([
            ('name', '=', 'IPAI Demo Partner'),
            ('company_type', '=', 'company')
        ], limit=1)

        if not demo_partner:
            demo_partner = env['res.partner'].sudo().create({
                'name': 'IPAI Demo Partner',
                'company_type': 'company',
                'email': 'demo@insightpulseai.net',
                'comment': 'Created by post-upgrade seed script',
            })
            print(f"[odoo-seed] Created demo partner: {demo_partner.id}")
        else:
            print(f"[odoo-seed] Demo partner exists: {demo_partner.id}")
    else:
        print("[odoo-seed] Skipping demo data (prod or not allowed)")

    print(f"[odoo-seed] Seed complete: {key}")
    env.cr.commit()

print("[odoo-seed] Done.")
PY

log "Done."
