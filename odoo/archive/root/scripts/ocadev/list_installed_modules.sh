#!/usr/bin/env bash
set -euo pipefail

ODOO_DB="${ODOO_DB:-ipai_oca_full}"
ODOO_COMPOSE_FILE="${ODOO_COMPOSE_FILE:-}"
ODOO_SERVICE="${ODOO_SERVICE:-}"

# Run preflight to detect compose file and service
if [ -x scripts/ocadev/preflight.sh ]; then
  eval "$(./scripts/ocadev/preflight.sh | awk -F= '/^(ODOO_COMPOSE_FILE|ODOO_SERVICE)=/ {print "export "$1"=\""$2"\""}')"
fi

if [ -z "${ODOO_COMPOSE_FILE}" ] || [ -z "${ODOO_SERVICE}" ]; then
  echo "ERROR: Missing ODOO_COMPOSE_FILE or ODOO_SERVICE. Run scripts/ocadev/preflight.sh." >&2
  exit 1
fi

echo "Querying DB: ${ODOO_DB}"
echo "Using: ${ODOO_COMPOSE_FILE} / ${ODOO_SERVICE}"
echo ""

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
