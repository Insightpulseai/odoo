#!/usr/bin/env bash
# =============================================================================
# WORKOS PRODUCTION DEPLOYMENT SCRIPT
# =============================================================================
# Target: erp.insightpulseai.net
# Branch: claude/notion-clone-odoo-module-LSFan
#
# IMPORTANT: This script must be run ON THE PRODUCTION SERVER.
# It is NOT designed to be run remotely or in a dev environment.
#
# Usage:
#   ssh deploy@erp.insightpulseai.net
#   cd /opt/odoo-ce
#   sudo ./scripts/deploy_workos_prod.sh
#
# Rollback:
#   sudo ./scripts/deploy_workos_prod.sh --rollback
# =============================================================================

set -euo pipefail

# Configuration - ADJUST THESE TO MATCH YOUR PRODUCTION ENVIRONMENT
REPO_DIR="${REPO_DIR:-/opt/odoo-ce}"
DEPLOY_BRANCH="claude/notion-clone-odoo-module-LSFan"
COMPOSE_FILE="deploy/docker-compose.prod.yml"
COMPOSE_OVERRIDE="deploy/docker-compose.workos-deploy.yml"
DB_SERVICE="db"
ODOO_SERVICE="odoo"
DB_NAME="${DB_NAME:-odoo}"
DB_USER="${DB_USER:-odoo}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/odoo}"

# State tracking
STATE_FILE="$REPO_DIR/.deploy_state"
BACKUP_FILE=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} $1"; }
log_ok() { echo -e "${GREEN}[$(date +%H:%M:%S)] ✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}[$(date +%H:%M:%S)] ⚠${NC} $1"; }
log_error() { echo -e "${RED}[$(date +%H:%M:%S)] ✗${NC} $1"; }
die() { log_error "$1"; exit 1; }

# =============================================================================
# PRE-FLIGHT CHECKS
# =============================================================================
preflight_checks() {
    log_info "Running pre-flight checks..."

    # Must be run as root or with sudo
    if [[ $EUID -ne 0 ]]; then
        die "This script must be run as root or with sudo"
    fi

    # Must be in repo directory
    cd "$REPO_DIR" || die "Cannot cd to $REPO_DIR"
    log_ok "Working directory: $(pwd)"

    # Check git repo
    if [[ ! -d .git ]]; then
        die "Not a git repository: $REPO_DIR"
    fi
    log_ok "Git repository detected"

    # Check compose files exist
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        die "Compose file not found: $COMPOSE_FILE"
    fi
    log_ok "Compose file exists: $COMPOSE_FILE"

    # Check docker compose works
    if ! docker compose version &>/dev/null; then
        die "docker compose not available"
    fi
    log_ok "Docker compose available"

    # Check services are running
    if ! docker compose -f "$COMPOSE_FILE" ps --status running | grep -q "$ODOO_SERVICE"; then
        log_warn "Odoo service not currently running - will start after deployment"
    else
        log_ok "Odoo service is running"
    fi

    # Check backup directory
    mkdir -p "$BACKUP_DIR" || die "Cannot create backup directory: $BACKUP_DIR"
    log_ok "Backup directory ready: $BACKUP_DIR"
}

# =============================================================================
# STEP A: SNAPSHOT CURRENT STATE
# =============================================================================
snapshot_state() {
    log_info "=== STEP A: SNAPSHOT CURRENT STATE ==="

    cd "$REPO_DIR"

    # Record git state
    PREVIOUS_SHA=$(git rev-parse HEAD)
    PREVIOUS_BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)

    log_info "Current SHA: $PREVIOUS_SHA"
    log_info "Current branch: $PREVIOUS_BRANCH"

    # Check for uncommitted changes
    if [[ -n "$(git status --porcelain)" ]]; then
        log_warn "Uncommitted changes detected:"
        git status --porcelain
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            die "Aborted due to uncommitted changes"
        fi
    fi

    # Show running containers
    log_info "Running containers:"
    docker compose -f "$COMPOSE_FILE" ps

    # Take database backup
    log_info "Taking database backup..."
    BACKUP_FILE="$BACKUP_DIR/odoo_pre_workos_${TIMESTAMP}.dump"

    docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
        pg_dump -Fc -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE" \
        || die "Database backup failed"

    BACKUP_SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
    BACKUP_MD5=$(md5sum "$BACKUP_FILE" | awk '{print $1}')

    log_ok "Database backup created: $BACKUP_FILE"
    log_ok "Backup size: $BACKUP_SIZE, MD5: $BACKUP_MD5"

    # Save state for rollback
    cat > "$STATE_FILE" << EOF
PREVIOUS_SHA=$PREVIOUS_SHA
PREVIOUS_BRANCH=$PREVIOUS_BRANCH
BACKUP_FILE=$BACKUP_FILE
BACKUP_MD5=$BACKUP_MD5
TIMESTAMP=$TIMESTAMP
EOF

    log_ok "State saved to $STATE_FILE"
}

# =============================================================================
# STEP B: DEPLOY BRANCH
# =============================================================================
deploy_branch() {
    log_info "=== STEP B: DEPLOY BRANCH ==="

    cd "$REPO_DIR"

    # Fetch latest
    log_info "Fetching from origin..."
    git fetch origin || die "git fetch failed"

    # Checkout branch
    log_info "Checking out $DEPLOY_BRANCH..."
    git checkout "$DEPLOY_BRANCH" || die "git checkout failed"

    # Pull latest (fast-forward only)
    log_info "Pulling latest..."
    git pull --ff-only origin "$DEPLOY_BRANCH" || die "git pull failed"

    NEW_SHA=$(git rev-parse HEAD)
    log_ok "Deployed to SHA: $NEW_SHA"

    # Verify modules exist
    log_info "Verifying modules exist..."
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
        if [[ -f "addons/$mod/__manifest__.py" ]]; then
            log_ok "Found: $mod"
        else
            die "Missing module: $mod - deployment aborted"
        fi
    done
}

# =============================================================================
# STEP C: VERIFY CODE VISIBILITY TO CONTAINER
# =============================================================================
verify_code_visibility() {
    log_info "=== STEP C: VERIFY CODE VISIBILITY ==="

    cd "$REPO_DIR"

    # Check if override file exists
    if [[ ! -f "$COMPOSE_OVERRIDE" ]]; then
        die "Compose override not found: $COMPOSE_OVERRIDE"
    fi
    log_ok "Compose override exists"

    # Start services with override (without installing modules yet)
    log_info "Starting services with volume mount..."
    docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" up -d "$ODOO_SERVICE"

    # Wait for container to be ready
    log_info "Waiting for container startup (30s)..."
    sleep 30

    # Verify addons are visible
    log_info "Checking if addons are visible inside container..."
    local test_output
    test_output=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
        exec -T "$ODOO_SERVICE" ls -la /mnt/addons/ipai/ 2>&1) || true

    if echo "$test_output" | grep -q "ipai_workos_affine"; then
        log_ok "Addons are visible inside container:"
        echo "$test_output" | head -15
    else
        log_error "Addons NOT visible inside container!"
        echo "$test_output"
        die "Mount path mismatch - check COMPOSE_OVERRIDE volume mapping"
    fi

    # Verify Odoo can import the module
    log_info "Testing Odoo module discovery..."
    docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
        exec -T "$ODOO_SERVICE" python3 -c \
        "import odoo; print('Odoo path:', odoo.__file__)" || log_warn "Could not verify Odoo import"
}

# =============================================================================
# STEP D: INSTALL/UPGRADE MODULES
# =============================================================================
install_modules() {
    log_info "=== STEP D: INSTALL/UPGRADE MODULES ==="

    cd "$REPO_DIR"

    # Stop main Odoo service first
    log_info "Stopping Odoo service..."
    docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" stop "$ODOO_SERVICE"

    # Run module installation using the init profile
    log_info "Installing WorkOS modules (this may take 2-5 minutes)..."

    docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
        --profile init run --rm odoo-workos-init \
        2>&1 | tee /tmp/odoo_install.log

    # Check for errors in install log
    if grep -iE "error|traceback|failed" /tmp/odoo_install.log | grep -v "ERROR.*odoo.sql_db.*psycopg2"; then
        log_warn "Potential errors in install log - review /tmp/odoo_install.log"
    else
        log_ok "Module installation completed"
    fi

    # Restart Odoo service
    log_info "Starting Odoo service..."
    docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" up -d "$ODOO_SERVICE"

    # Wait for startup
    log_info "Waiting for Odoo to start (60s)..."
    sleep 60
}

# =============================================================================
# STEP E: RUNTIME VERIFICATION
# =============================================================================
verify_deployment() {
    log_info "=== STEP E: RUNTIME VERIFICATION ==="

    local errors=0

    # HTTP check (use internal port first)
    log_info "Checking HTTP (internal)..."
    local http_code
    http_code=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
        exec -T "$ODOO_SERVICE" curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login 2>/dev/null) || true

    if [[ "$http_code" == "200" ]] || [[ "$http_code" == "303" ]]; then
        log_ok "HTTP internal: $http_code"
    else
        log_error "HTTP internal check failed: $http_code"
        errors=$((errors + 1))
    fi

    # External HTTP check
    log_info "Checking HTTP (external)..."
    http_code=$(curl -s -o /dev/null -w "%{http_code}" -I https://erp.insightpulseai.net/web/login 2>/dev/null) || true

    if [[ "$http_code" == "200" ]] || [[ "$http_code" == "303" ]]; then
        log_ok "HTTP external: $http_code"
    else
        log_warn "HTTP external check: $http_code (may need nginx restart)"
    fi

    # Check logs for errors
    log_info "Checking logs for errors..."
    local error_count
    error_count=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
        logs --tail=200 "$ODOO_SERVICE" 2>&1 | grep -icE "traceback|error|critical" || echo "0")

    if [[ "$error_count" -gt 5 ]]; then
        log_error "Found $error_count potential errors in logs"
        docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
            logs --tail=50 "$ODOO_SERVICE" 2>&1 | grep -iE "traceback|error|critical" | head -10
        errors=$((errors + 1))
    else
        log_ok "Logs look clean ($error_count minor warnings)"
    fi

    # Check module states in DB
    log_info "Checking module states in database..."
    docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
        exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" -c \
        "SELECT name, state, latest_version FROM ir_module_module WHERE name LIKE 'ipai_workos_%' OR name LIKE 'ipai_platform_%' ORDER BY name;"

    # Check for uninstalled modules
    local uninstalled
    uninstalled=$(docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
        exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" -tAc \
        "SELECT count(*) FROM ir_module_module WHERE (name LIKE 'ipai_workos_%' OR name LIKE 'ipai_platform_%') AND state != 'installed';")

    if [[ "$uninstalled" -gt 0 ]]; then
        log_warn "$uninstalled module(s) not in 'installed' state"
    else
        log_ok "All WorkOS modules are installed"
    fi

    # Check for ir_ui_menu entries
    log_info "Checking UI menus..."
    docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
        exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" -c \
        "SELECT name FROM ir_ui_menu WHERE name ILIKE '%workos%' OR name ILIKE '%workspace%' LIMIT 10;"

    # Check for models
    log_info "Checking models..."
    docker compose -f "$COMPOSE_FILE" -f "$COMPOSE_OVERRIDE" \
        exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" -c \
        "SELECT model FROM ir_model WHERE model LIKE 'ipai.workos.%' LIMIT 10;"

    # Summary
    echo ""
    if [[ $errors -gt 0 ]]; then
        log_error "Deployment completed with $errors error(s) - consider rollback"
        return 1
    else
        log_ok "Deployment verification passed!"
        return 0
    fi
}

# =============================================================================
# ROLLBACK
# =============================================================================
rollback() {
    log_info "=== ROLLBACK REQUESTED ==="

    cd "$REPO_DIR"

    if [[ ! -f "$STATE_FILE" ]]; then
        die "No state file found at $STATE_FILE - cannot rollback"
    fi

    source "$STATE_FILE"

    log_info "Rolling back to SHA: $PREVIOUS_SHA"
    log_info "Backup file: $BACKUP_FILE"

    # Stop Odoo
    log_info "Stopping Odoo..."
    docker compose -f "$COMPOSE_FILE" stop "$ODOO_SERVICE" || true

    # Checkout previous SHA
    log_info "Restoring git state..."
    git checkout "$PREVIOUS_SHA"

    # Restore database
    if [[ -f "$BACKUP_FILE" ]]; then
        log_info "Restoring database from backup..."

        # Verify MD5
        local current_md5
        current_md5=$(md5sum "$BACKUP_FILE" | awk '{print $1}')
        if [[ "$current_md5" != "$BACKUP_MD5" ]]; then
            die "Backup file corrupted! MD5 mismatch"
        fi

        # Drop and restore
        docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
            psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME}_restore;"

        docker compose -f "$COMPOSE_FILE" exec -T "$DB_SERVICE" \
            pg_restore -U "$DB_USER" -d postgres -C < "$BACKUP_FILE"

        log_warn "Database restored to ${DB_NAME}_restore - manual swap required"
    else
        log_warn "Backup file not found - skipping database restore"
    fi

    # Restart Odoo (without override)
    log_info "Starting Odoo (original config)..."
    docker compose -f "$COMPOSE_FILE" up -d "$ODOO_SERVICE"

    log_ok "Rollback complete - verify at https://erp.insightpulseai.net/web/login"
}

# =============================================================================
# MAIN
# =============================================================================
main() {
    echo ""
    echo "=========================================="
    echo "  WORKOS PRODUCTION DEPLOYMENT"
    echo "  Target: erp.insightpulseai.net"
    echo "  Branch: $DEPLOY_BRANCH"
    echo "=========================================="
    echo ""

    if [[ "${1:-}" == "--rollback" ]]; then
        rollback
        exit 0
    fi

    preflight_checks
    echo ""
    snapshot_state
    echo ""
    deploy_branch
    echo ""
    verify_code_visibility
    echo ""
    install_modules
    echo ""
    verify_deployment
    local result=$?

    echo ""
    echo "=========================================="
    if [[ $result -eq 0 ]]; then
        log_ok "DEPLOYMENT COMPLETE"
    else
        log_error "DEPLOYMENT COMPLETED WITH ERRORS"
    fi
    echo "=========================================="

    # Print summary
    source "$STATE_FILE" 2>/dev/null || true
    NEW_SHA=$(git rev-parse HEAD)

    echo ""
    echo "Summary:"
    echo "  Previous SHA: ${PREVIOUS_SHA:-unknown}"
    echo "  New SHA:      $NEW_SHA"
    echo "  Backup:       ${BACKUP_FILE:-none}"
    echo ""
    echo "To rollback: sudo $0 --rollback"
    echo ""

    return $result
}

main "$@"
