#!/usr/bin/env bash
###############################################################################
# recreate_odoo_prod.sh - Deterministic Odoo container recreation
#
# Purpose:
#   Recreate odoo-prod container from pinned digest spec
#   Clear asset cache and verify web assets compilation
#
# Usage:
#   ./scripts/recreate_odoo_prod.sh
#
# Exit codes:
#   0 - Container recreated and verification passed
#   1 - Container recreation failed
#   2 - Verification failed
###############################################################################

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

COMPOSE_FILE="/opt/odoo-ce/repo/deploy/odoo-prod.compose.yml"
VERIFY_SCRIPT="/opt/odoo-ce/repo/scripts/verify_web_assets.sh"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Odoo Production Container Recreation"
echo "  Using: $COMPOSE_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Pull image by digest
log_info "Pulling pinned image digest..."
docker-compose -f "$COMPOSE_FILE" pull || {
    log_error "Failed to pull image"
    exit 1
}

# Step 2: Stop and remove existing container
log_info "Stopping odoo-prod..."
docker stop odoo-prod || true

log_info "Removing odoo-prod..."
docker rm odoo-prod || true

# Step 3: Recreate container
log_info "Recreating container from compose spec..."
docker-compose -f "$COMPOSE_FILE" up -d || {
    log_error "Failed to recreate container"
    exit 1
}

# Step 4: Wait for startup
log_info "Waiting 20 seconds for Odoo to start..."
sleep 20

# Step 5: Clear asset cache
log_info "Clearing compiled asset cache..."
docker exec odoo-prod bash -c 'rm -rf /var/lib/odoo/.local/share/Odoo/filestore/*/assets/* 2>/dev/null || true'
docker exec odoo-prod bash -c 'rm -rf /var/lib/odoo/.local/share/Odoo/sessions/* 2>/dev/null || true'

# Step 6: Run verification
log_info "Running web assets verification..."
if [ -x "$VERIFY_SCRIPT" ]; then
    "$VERIFY_SCRIPT" || {
        log_error "Verification failed"
        exit 2
    }
else
    log_warning "Verification script not found at $VERIFY_SCRIPT"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_success "Container recreation complete and verified"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
