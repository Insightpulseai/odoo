#!/usr/bin/env bash
set -euo pipefail

ODOO_DB="${ODOO_DB:-ipai_oca_full}"
ODOO_COMPOSE_FILE="${ODOO_COMPOSE_FILE:-docker/docker-compose.ce19.yml}"
ODOO_SERVICE="${ODOO_SERVICE:-odoo}"

docker compose -f "${ODOO_COMPOSE_FILE}" exec -T "${ODOO_SERVICE}" \
  odoo shell -d "${ODOO_DB}" << 'PY'
mods = env['ir.module.module'].search([
    ('state', '=', 'installed'),
    ('name', 'ilike', 'ipai_%')
])
print("=== ipai_* modules installed ===")
for m in mods:
    print(m.name)

oca_mods = env['ir.module.module'].search([
    ('state', '=', 'installed'),
    ('name', 'not ilike', 'ipai_%'),
])
print("\n=== OCA / other modules installed ===")
for m in oca_mods:
    print(m.name)
PY
