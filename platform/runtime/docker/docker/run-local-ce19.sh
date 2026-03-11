#!/usr/bin/env bash
# =============================================================================
# Run Local Script: Odoo CE 19 + OCA + ipai_enterprise_bridge (EE Parity)
# =============================================================================
# Runs the EE parity image locally for development and testing.
#
# Usage:
#   ./docker/run-local-ce19.sh
#   ./docker/run-local-ce19.sh --with-postgres  # Also start a local postgres
#
# Environment Variables:
#   REGISTRY_HOST   - Container registry host (default: ghcr.io)
#   REGISTRY_ORG    - Registry organization (default: jgtolentino)
#   IMAGE_NAME      - Full image name (default: ${REGISTRY_HOST}/${REGISTRY_ORG}/odoo-ce)
#   IMAGE_TAG       - Image tag (default: 19.0-ee-parity)
#   HOST_PORT       - Port to expose Odoo on host (default: 8069)
#   DB_HOST         - Database host (default: db or localhost)
#   DB_PORT         - Database port (default: 5432)
#   DB_USER         - Database user (default: odoo)
#   DB_PASSWORD     - Database password (default: odoo)
#   DB_NAME         - Database name (default: odoo_ce19_dev)
# =============================================================================

set -euo pipefail

# Parse arguments
WITH_POSTGRES=false
for arg in "$@"; do
    case $arg in
        --with-postgres)
            WITH_POSTGRES=true
            shift
            ;;
    esac
done

# Configuration with defaults
: "${REGISTRY_HOST:=ghcr.io}"
: "${REGISTRY_ORG:=jgtolentino}"
: "${IMAGE_NAME:=${REGISTRY_HOST}/${REGISTRY_ORG}/odoo-ce}"
: "${IMAGE_TAG:=19.0-ee-parity}"
: "${HOST_PORT:=8069}"
: "${DB_USER:=odoo}"
: "${DB_PASSWORD:=odoo}"
: "${DB_NAME:=odoo_ce19_dev}"
: "${DB_PORT:=5432}"

# Derived values
FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"
CONTAINER_NAME="odoo_ce19_ee_parity_local"
NETWORK_NAME="odoo_ce19_local_network"
PG_CONTAINER_NAME="odoo_ce19_local_postgres"

# Set DB_HOST based on whether we're using local postgres
if [ "${WITH_POSTGRES}" = true ]; then
    DB_HOST="${PG_CONTAINER_NAME}"
else
    : "${DB_HOST:=localhost}"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Cleanup function
cleanup_existing() {
    echo -e "${YELLOW}Cleaning up existing containers...${NC}"
    docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true
    if [ "${WITH_POSTGRES}" = true ]; then
        docker rm -f "${PG_CONTAINER_NAME}" 2>/dev/null || true
        docker network rm "${NETWORK_NAME}" 2>/dev/null || true
    fi
}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Running Odoo CE 19 EE Parity Locally${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Configuration:"
echo "  Image:      ${FULL_IMAGE}"
echo "  Container:  ${CONTAINER_NAME}"
echo "  Host Port:  ${HOST_PORT}"
echo "  Database:   ${DB_HOST}:${DB_PORT}/${DB_NAME}"
echo "  With PG:    ${WITH_POSTGRES}"
echo ""

# Verify image exists
echo -e "${YELLOW}[1/4] Checking image...${NC}"
if ! docker image inspect "${FULL_IMAGE}" > /dev/null 2>&1; then
    echo -e "${YELLOW}  Image not found locally. Attempting to pull...${NC}"
    if ! docker pull "${FULL_IMAGE}" 2>/dev/null; then
        echo -e "${RED}ERROR: Image ${FULL_IMAGE} not found.${NC}"
        echo "Run ./docker/build-ce19.sh first."
        exit 1
    fi
fi
echo -e "${GREEN}  ✓ Image available${NC}"

# Cleanup existing
echo -e "${YELLOW}[2/4] Preparing environment...${NC}"
cleanup_existing

# Start postgres if requested
if [ "${WITH_POSTGRES}" = true ]; then
    echo -e "${YELLOW}[3/4] Starting PostgreSQL...${NC}"

    # Create network
    docker network create "${NETWORK_NAME}" 2>/dev/null || true

    # Start postgres
    docker run -d --name "${PG_CONTAINER_NAME}" \
        --network "${NETWORK_NAME}" \
        -e POSTGRES_USER="${DB_USER}" \
        -e POSTGRES_PASSWORD="${DB_PASSWORD}" \
        -e POSTGRES_DB="${DB_NAME}" \
        -v "odoo_ce19_pgdata:/var/lib/postgresql/data" \
        postgres:16-alpine

    # Wait for postgres
    echo "  Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if docker exec "${PG_CONTAINER_NAME}" pg_isready -U "${DB_USER}" > /dev/null 2>&1; then
            echo -e "${GREEN}  ✓ PostgreSQL is ready${NC}"
            break
        fi
        if [ $i -eq 30 ]; then
            echo -e "${RED}ERROR: PostgreSQL failed to start${NC}"
            exit 1
        fi
        sleep 1
    done
else
    echo -e "${YELLOW}[3/4] Using external database: ${DB_HOST}:${DB_PORT}${NC}"
fi

# Start Odoo
echo -e "${YELLOW}[4/4] Starting Odoo...${NC}"

DOCKER_RUN_ARGS=(
    -d
    --name "${CONTAINER_NAME}"
    -p "${HOST_PORT}:8069"
    -e "HOST=${DB_HOST}"
    -e "PORT=${DB_PORT}"
    -e "USER=${DB_USER}"
    -e "PASSWORD=${DB_PASSWORD}"
    -e "DB=${DB_NAME}"
)

if [ "${WITH_POSTGRES}" = true ]; then
    DOCKER_RUN_ARGS+=(--network "${NETWORK_NAME}")
fi

docker run "${DOCKER_RUN_ARGS[@]}" "${FULL_IMAGE}"

# Wait for Odoo to start
echo ""
echo "  Waiting for Odoo to start..."
for i in {1..60}; do
    if curl -sf "http://localhost:${HOST_PORT}/web/health" > /dev/null 2>&1; then
        echo -e "${GREEN}  ✓ Odoo is running${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${YELLOW}  Odoo is still starting (check logs with: docker logs ${CONTAINER_NAME})${NC}"
    fi
    sleep 2
done

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Odoo CE 19 is Running${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Access Odoo:"
echo "  URL:      http://localhost:${HOST_PORT}"
echo "  Database: ${DB_NAME}"
echo ""
echo "Useful commands:"
echo "  View logs:     docker logs -f ${CONTAINER_NAME}"
echo "  Stop:          docker stop ${CONTAINER_NAME}"
echo "  Remove:        docker rm -f ${CONTAINER_NAME}"
if [ "${WITH_POSTGRES}" = true ]; then
    echo "  Stop all:      docker rm -f ${CONTAINER_NAME} ${PG_CONTAINER_NAME}"
    echo "  Connect to DB: docker exec -it ${PG_CONTAINER_NAME} psql -U ${DB_USER} -d ${DB_NAME}"
fi
echo ""
echo "Install ipai_enterprise_bridge:"
echo "  docker exec -it ${CONTAINER_NAME} odoo -d ${DB_NAME} -i ipai_enterprise_bridge --stop-after-init"
echo ""
