#!/bin/bash
# stop-dev-stacks.sh
# Stop development Docker stacks to conserve resources
#
# Portfolio Initiative: PORT-2026-010
# Process: PROC-INFRA-001
# Control: CTRL-SOP-003

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================================================
# Functions
# ============================================================================

log() {
    echo -e "${GREEN}[$(date +%Y-%m-%d\ %H:%M:%S)]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

stop_container() {
    local container=$1
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        log "Stopping ${container}..."
        if docker stop "$container" >/dev/null 2>&1; then
            log "✅ Stopped ${container}"
            return 0
        else
            error "Failed to stop ${container}"
            return 1
        fi
    else
        warn "${container} is not running (skipping)"
        return 0
    fi
}

# ============================================================================
# Main
# ============================================================================

log "Stopping development Docker stacks..."

# ============================================================================
# Odoo Dev Stack
# ============================================================================

log "========================================="
log "Odoo Dev Stack"
log "========================================="

stop_container "odoo-dev" || true
stop_container "odoo-dev-db" || true

# ============================================================================
# IDE Helpers (if running)
# ============================================================================

log "========================================="
log "IDE Helpers (Docker Desktop Extensions)"
log "========================================="

# Check for code-server or openvscode-server containers
IDE_CONTAINERS=$(docker ps --format '{{.Names}}' | grep -E "code-server|openvscode" || true)

if [ -n "$IDE_CONTAINERS" ]; then
    while IFS= read -r container; do
        stop_container "$container" || true
    done <<< "$IDE_CONTAINERS"
else
    warn "No IDE helper containers running"
fi

# ============================================================================
# Summary
# ============================================================================

log "========================================="
log "Summary"
log "========================================="

RUNNING_CONTAINERS=$(docker ps --format "table {{.Names}}\t{{.Status}}" | tail -n +2)

if [ -n "$RUNNING_CONTAINERS" ]; then
    log "Remaining running containers:"
    echo "$RUNNING_CONTAINERS"
else
    warn "No containers running"
fi

log "✅ Development stacks stopped"

exit 0
