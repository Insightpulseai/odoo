#!/usr/bin/env bash
set -euo pipefail

CONTAINER="${ODOO_CONTAINER:-odoo-prod}"
DB="${ODOO_DB:-odoo_prod}"
MODULES="${ODOO_MODULES:-ipai_studio_ai}"
ACTION="${ODOO_ACTION:-upgrade}"

# Map action to Odoo CLI flag: install → -i, upgrade → -u
if [ "$ACTION" = "install" ]; then
  FLAG="-i"
else
  FLAG="-u"
fi

echo "Action: ${ACTION} (${FLAG}) modules: ${MODULES} on DB=${DB} container=${CONTAINER}"

# Pass DB connection env vars through (container has HOST, PORT, USER, PASSWORD).
# Use --no-http to avoid port conflict with running Odoo instance.
docker exec -i "${CONTAINER}" bash -lc "
  set -euo pipefail
  odoo -c /etc/odoo/odoo.conf \
    -d '${DB}' \
    --db_host=\"\$HOST\" --db_port=\"\$PORT\" \
    --db_user=\"\$USER\" --db_password=\"\$PASSWORD\" \
    ${FLAG} '${MODULES}' \
    --no-http \
    --stop-after-init
"

docker restart "${CONTAINER}"
sleep 5
echo ">>> Health check"
docker exec -i "${CONTAINER}" curl -sf http://localhost:8069/web/health || echo "HEALTH_PENDING (container still starting)"
echo ""
echo ">>> Recent logs"
docker logs --tail=30 "${CONTAINER}" 2>&1 | grep -E "Registry loaded|Traceback|ERROR|loaded" || true
