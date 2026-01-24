#!/usr/bin/env bash
# ===========================================================================
# Odoo CI Install/Upgrade Test
# Boots Postgres + Odoo and runs -i/-u for changed modules
# ===========================================================================
set -euo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-ci/odoo/docker-compose.ci.yml}"
DB="${DB:-odoo_ci}"
MODULES_CSV="${MODULES_CSV:-}"
ODOO_IMAGE="${ODOO_IMAGE:-odoo:18.0}"

log() { echo "[odoo-ci] $(date '+%H:%M:%S') $*"; }

if [[ -z "${MODULES_CSV}" ]]; then
    log "No changed modules detected; skipping install test."
    exit 0
fi

log "Modules under test: ${MODULES_CSV}"
log "Odoo image: ${ODOO_IMAGE}"

# Export for docker compose
export ODOO_IMAGE

# Cleanup any existing containers
log "Cleaning up any existing containers..."
docker compose -f "${COMPOSE_FILE}" down -v 2>/dev/null || true

# Start database
log "Starting database..."
docker compose -f "${COMPOSE_FILE}" up -d db

# Wait for database health
log "Waiting for database to be ready..."
for i in $(seq 1 60); do
    if docker compose -f "${COMPOSE_FILE}" exec -T db pg_isready -U odoo -d odoo_ci >/dev/null 2>&1; then
        log "Database is ready"
        break
    fi
    if [[ $i -eq 60 ]]; then
        log "ERROR: Database failed to start"
        docker compose -f "${COMPOSE_FILE}" logs db
        exit 1
    fi
    sleep 2
done

# Define common Odoo args
ODOO_ARGS="--db_host=db --db_port=5432 --db_user=odoo --db_password=odoo -d ${DB} --without-demo=all --stop-after-init"
ADDONS_PATH="--addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/repo/addons,/mnt/repo/oca"

# 1) INSTALL changed modules (fresh database)
log "Step 1: Installing modules on fresh database..."
if ! docker compose -f "${COMPOSE_FILE}" run --rm odoo \
    odoo ${ODOO_ARGS} ${ADDONS_PATH} -i "${MODULES_CSV}"; then
    log "ERROR: Module installation failed"
    docker compose -f "${COMPOSE_FILE}" logs
    docker compose -f "${COMPOSE_FILE}" down -v
    exit 1
fi
log "Installation successful"

# 2) UPGRADE changed modules (idempotency test)
log "Step 2: Upgrading modules (idempotency test)..."
if ! docker compose -f "${COMPOSE_FILE}" run --rm odoo \
    odoo ${ODOO_ARGS} ${ADDONS_PATH} -u "${MODULES_CSV}"; then
    log "ERROR: Module upgrade failed"
    docker compose -f "${COMPOSE_FILE}" logs
    docker compose -f "${COMPOSE_FILE}" down -v
    exit 1
fi
log "Upgrade successful"

# Cleanup
log "Cleaning up..."
docker compose -f "${COMPOSE_FILE}" down -v

log "All tests passed!"
