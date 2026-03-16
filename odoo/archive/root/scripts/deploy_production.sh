#!/bin/bash
# =============================================================================
# Production Deployment Script
# =============================================================================
# Usage: ./scripts/deploy_production.sh [IMAGE_TAG]
#
# This script deploys the Odoo CE application to production.
# Can be run manually or via CI/CD.
#
# Requirements:
#   - Docker and docker-compose installed
#   - Access to ghcr.io/jgtolentino/odoo-ce
#   - Running from /opt/odoo-ce or similar repo directory
# =============================================================================

set -euo pipefail

# Configuration
REGISTRY="${REGISTRY:-ghcr.io}"
IMAGE_NAME="${IMAGE_NAME:-jgtolentino/odoo-ce}"
IMAGE_TAG="${1:-latest}"
COMPOSE_FILE="${COMPOSE_FILE:-deploy/docker-compose.prod.yml}"
HEALTH_ENDPOINT="${HEALTH_ENDPOINT:-http://localhost:8069/web/health}"
MAX_HEALTH_RETRIES=10
HEALTH_WAIT=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Header
echo "============================================="
echo "  Odoo CE Production Deployment"
echo "============================================="
echo "Image: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
echo "Compose: ${COMPOSE_FILE}"
echo "============================================="
echo ""

# Step 1: Pull latest code
log_info "Pulling latest code from main..."
git fetch origin main
git checkout main
git pull origin main --ff-only

# Step 2: Update submodules
log_info "Updating submodules..."
git submodule update --init --recursive

# Step 3: Pull new image
log_info "Pulling Docker image..."
docker pull "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

# Step 4: Tag as latest for compose compatibility
if [ "${IMAGE_TAG}" != "latest" ]; then
  log_info "Tagging as latest..."
  docker tag "${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}" "${REGISTRY}/${IMAGE_NAME}:latest"
fi

# Step 5: Get current container state for rollback
CURRENT_CONTAINERS=$(docker compose -f "${COMPOSE_FILE}" ps -q 2>/dev/null || true)
if [ -n "$CURRENT_CONTAINERS" ]; then
  log_info "Backing up current container state..."
  docker compose -f "${COMPOSE_FILE}" ps > /tmp/deploy_rollback_state.txt
fi

# Step 6: Recreate containers
log_info "Recreating containers..."
docker compose -f "${COMPOSE_FILE}" up -d --force-recreate

# Step 7: Wait for initialization
log_info "Waiting for Odoo to initialize (45s)..."
sleep 45

# Step 8: Health check with retries
log_info "Running health checks..."
HEALTHY=false

for i in $(seq 1 $MAX_HEALTH_RETRIES); do
  HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "${HEALTH_ENDPOINT}" 2>/dev/null || echo "000")

  if [ "$HTTP_CODE" == "200" ]; then
    HEALTHY=true
    log_info "Health check passed! (HTTP ${HTTP_CODE})"
    break
  fi

  log_warn "Health check attempt ${i}/${MAX_HEALTH_RETRIES}: HTTP ${HTTP_CODE}"

  if [ "$i" -lt "$MAX_HEALTH_RETRIES" ]; then
    sleep $HEALTH_WAIT
  fi
done

# Step 9: Report result
echo ""
echo "============================================="
if [ "$HEALTHY" = true ]; then
  log_info "Deployment successful!"
  echo ""
  echo "  Image: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
  echo "  Status: Running"
  echo "  Health: OK"
  echo ""

  # Show container status
  docker compose -f "${COMPOSE_FILE}" ps

  echo "============================================="
  exit 0
else
  log_error "Deployment failed - health check unsuccessful"
  echo ""

  # Show logs for debugging
  log_warn "Last 30 lines of Odoo logs:"
  docker compose -f "${COMPOSE_FILE}" logs --tail 30 odoo || true

  echo ""
  log_error "Consider rolling back with:"
  echo "  docker compose -f ${COMPOSE_FILE} down"
  echo "  git checkout HEAD~1"
  echo "  ./scripts/deploy_production.sh"

  echo "============================================="
  exit 1
fi
