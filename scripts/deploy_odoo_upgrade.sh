#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${ODOO_CONTAINER:-odoo-erp-prod}"
DB="${ODOO_DB:-odoo}"
MODULES="${ODOO_MODULES:-ipai_studio_ai}"

echo "Upgrading modules: ${MODULES} on DB=${DB} container=${CONTAINER}"

docker exec -i "${CONTAINER}" bash -lc "
  set -euo pipefail
  odoo -c /etc/odoo/odoo.conf -d '${DB}' -u '${MODULES}' --stop-after-init
"

docker restart "${CONTAINER}"
docker logs --tail=200 "${CONTAINER}"
