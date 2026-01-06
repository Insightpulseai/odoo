#!/usr/bin/env bash
# update_task_phase_tags.sh - Apply phase tags to tasks via SQL
#
# Usage:
#   ./scripts/update_task_phase_tags.sh                    # Run on local docker
#   ./scripts/update_task_phase_tags.sh --remote           # Run on remote server
#   ./scripts/update_task_phase_tags.sh --dry-run          # Show SQL without executing
#
# Environment:
#   ODOO_HOST      - Remote server hostname (default: erp.insightpulseai.net)
#   POSTGRES_DB    - Database name (default: odoo)
#   POSTGRES_USER  - Database user (default: odoo)

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
ODOO_HOST="${ODOO_HOST:-erp.insightpulseai.net}"
POSTGRES_DB="${POSTGRES_DB:-odoo}"
POSTGRES_USER="${POSTGRES_USER:-odoo}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SQL_FILE="${SCRIPT_DIR}/sql/update_phase_tags.sql"

# Flags
REMOTE=false
DRY_RUN=false

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --remote     Run on remote server (via SSH)"
    echo "  --dry-run    Show SQL without executing"
    echo "  --help       Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  ODOO_HOST      Remote server hostname (default: erp.insightpulseai.net)"
    echo "  POSTGRES_DB    Database name (default: odoo)"
    echo "  POSTGRES_USER  Database user (default: odoo)"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --remote)
            REMOTE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Check SQL file exists
if [[ ! -f "$SQL_FILE" ]]; then
    log_error "SQL file not found: $SQL_FILE"
    exit 1
fi

log_info "================================================"
log_info "Odoo Task Phase Tags Update"
log_info "================================================"
log_info "SQL File: $SQL_FILE"
log_info "Database: $POSTGRES_DB"
log_info "Mode: $(if $DRY_RUN; then echo 'DRY RUN'; elif $REMOTE; then echo 'REMOTE'; else echo 'LOCAL'; fi)"
echo ""

if $DRY_RUN; then
    log_info "SQL to be executed:"
    echo "----------------------------------------"
    cat "$SQL_FILE"
    echo "----------------------------------------"
    log_warning "Dry run - no changes made"
    exit 0
fi

if $REMOTE; then
    log_info "Running on remote server: $ODOO_HOST"

    # Copy SQL file to remote and execute
    ssh "root@${ODOO_HOST}" << EOF
docker exec -i \$(docker ps -q -f name=db) psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} << 'SQLEOF'
$(cat "$SQL_FILE")
SQLEOF
EOF

    log_success "Remote execution completed"
else
    log_info "Running on local Docker..."

    # Find the postgres container
    CONTAINER=$(docker ps -q -f name=postgres 2>/dev/null || docker ps -q -f name=db 2>/dev/null || echo "")

    if [[ -z "$CONTAINER" ]]; then
        log_error "PostgreSQL container not found. Is Docker running?"
        log_info "Expected container name: postgres or db"
        exit 1
    fi

    log_info "Using container: $CONTAINER"

    # Execute SQL
    docker exec -i "$CONTAINER" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < "$SQL_FILE"

    log_success "Local execution completed"
fi

echo ""
log_success "Phase tags have been assigned to tasks"
