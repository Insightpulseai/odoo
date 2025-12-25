#!/usr/bin/env bash
# =============================================================================
# DEPLOY NOTION WORKOS MODULES TO PRODUCTION
# =============================================================================
# Branch: claude/notion-clone-odoo-module-LSFan
# Target: erp.insightpulseai.net
#
# Usage:
#   ./scripts/deploy_workos_prod.sh [--rollback]
#
# This script:
# 1. Records current state for rollback
# 2. Pulls the deployment branch
# 3. Installs/upgrades WorkOS modules
# 4. Verifies deployment
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Configuration
DEPLOY_BRANCH="claude/notion-clone-odoo-module-LSFan"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
DB_NAME="${DB_NAME:-odoo_core}"
ODOO_SERVICE="${ODOO_SERVICE:-odoo-core}"
UMBRELLA_MODULE="ipai_workos_affine"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# State file for rollback
STATE_FILE="$REPO_ROOT/.deploy_state.json"

# =============================================================================
# STEP 1: SNAPSHOT CURRENT STATE
# =============================================================================
snapshot_state() {
    log_info "Recording current state for rollback..."

    cd "$REPO_ROOT"

    PREVIOUS_SHA=$(git rev-parse HEAD)
    PREVIOUS_BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
    TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    # Save state
    cat > "$STATE_FILE" << EOF
{
    "timestamp": "$TIMESTAMP",
    "previous_sha": "$PREVIOUS_SHA",
    "previous_branch": "$PREVIOUS_BRANCH",
    "deploy_branch": "$DEPLOY_BRANCH",
    "db_name": "$DB_NAME"
}
EOF

    log_ok "State saved to $STATE_FILE"
    log_info "Previous SHA: $PREVIOUS_SHA"

    # Export module states if psql available
    if command -v docker &>/dev/null; then
        log_info "Exporting module states from database..."
        docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U odoo -d "$DB_NAME" -c \
            "SELECT name, state, latest_version FROM ir_module_module WHERE name LIKE 'ipai_%' ORDER BY name;" \
            2>/dev/null || log_warn "Could not export module states (DB may not be running)"
    fi
}

# =============================================================================
# STEP 2: DEPLOY BRANCH
# =============================================================================
deploy_branch() {
    log_info "Deploying branch $DEPLOY_BRANCH..."

    cd "$REPO_ROOT"

    # Fetch and checkout
    git fetch origin "$DEPLOY_BRANCH"
    git checkout "$DEPLOY_BRANCH"
    git pull origin "$DEPLOY_BRANCH"

    NEW_SHA=$(git rev-parse HEAD)
    log_ok "Checked out: $NEW_SHA"

    # Verify modules exist
    log_info "Verifying modules..."
    local modules=(
        "ipai_workos_affine"
        "ipai_workos_core"
        "ipai_workos_blocks"
        "ipai_workos_db"
        "ipai_workos_views"
        "ipai_workos_templates"
        "ipai_workos_collab"
        "ipai_workos_search"
        "ipai_workos_canvas"
        "ipai_platform_permissions"
        "ipai_platform_audit"
    )

    for mod in "${modules[@]}"; do
        if [[ -f "$REPO_ROOT/addons/$mod/__manifest__.py" ]]; then
            log_ok "Found: $mod"
        else
            log_error "Missing: $mod"
            exit 1
        fi
    done
}

# =============================================================================
# STEP 3: INSTALL/UPGRADE MODULES
# =============================================================================
install_modules() {
    log_info "Installing WorkOS modules via umbrella: $UMBRELLA_MODULE"

    cd "$REPO_ROOT"

    # Check if using prod or dev compose
    if [[ -f "deploy/$COMPOSE_FILE" ]]; then
        COMPOSE_PATH="deploy/$COMPOSE_FILE"
    else
        COMPOSE_PATH="$COMPOSE_FILE"
    fi

    log_info "Using compose file: $COMPOSE_PATH"

    # Stop services first
    log_info "Stopping Odoo services..."
    docker compose -f "$COMPOSE_PATH" stop "$ODOO_SERVICE" 2>/dev/null || true

    # Run module installation
    log_info "Running module installation (this may take 2-5 minutes)..."
    docker compose -f "$COMPOSE_PATH" run --rm "$ODOO_SERVICE" \
        odoo -d "$DB_NAME" \
        -i "$UMBRELLA_MODULE" \
        --stop-after-init \
        --log-level=info

    # Restart services
    log_info "Starting Odoo services..."
    docker compose -f "$COMPOSE_PATH" up -d "$ODOO_SERVICE"

    # Wait for startup
    log_info "Waiting for Odoo to start (30s)..."
    sleep 30
}

# =============================================================================
# STEP 4: VERIFY DEPLOYMENT
# =============================================================================
verify_deployment() {
    log_info "Verifying deployment..."

    local errors=0

    # HTTP health check
    log_info "Checking HTTP health..."
    if curl -sf http://localhost:8069/web/health >/dev/null 2>&1; then
        log_ok "HTTP health check passed"
    else
        log_error "HTTP health check failed"
        errors=$((errors + 1))
    fi

    # Check for tracebacks in recent logs
    log_info "Checking logs for errors..."
    if docker compose -f "$COMPOSE_PATH" logs --tail=100 "$ODOO_SERVICE" 2>&1 | grep -i "traceback\|error" | head -5; then
        log_warn "Found potential errors in logs (check above)"
    else
        log_ok "No obvious errors in recent logs"
    fi

    # Verify module states in DB
    log_info "Verifying module states in database..."
    docker compose -f "$COMPOSE_PATH" exec -T postgres psql -U odoo -d "$DB_NAME" -c \
        "SELECT name, state FROM ir_module_module WHERE name LIKE 'ipai_workos%' OR name LIKE 'ipai_platform%' ORDER BY name;" \
        2>/dev/null || log_warn "Could not query module states"

    # Final status
    if [[ $errors -gt 0 ]]; then
        log_error "Deployment verification failed with $errors error(s)"
        log_warn "Consider running: $0 --rollback"
        return 1
    else
        log_ok "Deployment verification passed!"
    fi
}

# =============================================================================
# ROLLBACK
# =============================================================================
rollback() {
    log_warn "ROLLBACK requested"

    if [[ ! -f "$STATE_FILE" ]]; then
        log_error "No state file found at $STATE_FILE - cannot rollback"
        exit 1
    fi

    PREVIOUS_SHA=$(grep '"previous_sha"' "$STATE_FILE" | cut -d'"' -f4)

    log_info "Rolling back to SHA: $PREVIOUS_SHA"

    cd "$REPO_ROOT"
    git checkout "$PREVIOUS_SHA"

    # Restart services
    docker compose -f "$COMPOSE_PATH" restart "$ODOO_SERVICE"

    log_ok "Rollback complete. Previous SHA restored."
    log_warn "If database migrations occurred, you may need to restore from backup."
}

# =============================================================================
# MAIN
# =============================================================================
main() {
    echo ""
    echo "=========================================="
    echo "  WORKOS PRODUCTION DEPLOYMENT SCRIPT"
    echo "=========================================="
    echo ""

    if [[ "${1:-}" == "--rollback" ]]; then
        rollback
        exit 0
    fi

    # Execute deployment
    snapshot_state
    echo ""
    deploy_branch
    echo ""
    install_modules
    echo ""
    verify_deployment

    echo ""
    echo "=========================================="
    echo "  DEPLOYMENT COMPLETE"
    echo "=========================================="
    echo ""

    # Print summary
    PREVIOUS_SHA=$(grep '"previous_sha"' "$STATE_FILE" 2>/dev/null | cut -d'"' -f4 || echo "unknown")
    NEW_SHA=$(git rev-parse HEAD)

    echo "Previous SHA: $PREVIOUS_SHA"
    echo "New SHA:      $NEW_SHA"
    echo ""
    echo "Modules installed:"
    echo "  - ipai_workos_affine (umbrella)"
    echo "  - ipai_workos_core, blocks, db, views"
    echo "  - ipai_workos_templates, collab, search, canvas"
    echo "  - ipai_platform_permissions, audit"
    echo ""
    echo "To rollback: $0 --rollback"
    echo ""
}

main "$@"
