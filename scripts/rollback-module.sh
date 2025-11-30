#!/usr/bin/env bash
###############################################################################
# rollback-module.sh
# Emergency rollback script for Odoo module deployments
#
# Features:
# - Restore database from backup
# - Restart Odoo container
# - Verify rollback success
#
# Usage: ./scripts/rollback-module.sh <backup_file>
# Example: ./scripts/rollback-module.sh /tmp/odoo_backup_ipai_finance_ppm_20251127_120000.sql
###############################################################################

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ ${NC}$1"; }
log_success() { echo -e "${GREEN}✅ ${NC}$1"; }
log_warning() { echo -e "${YELLOW}⚠️  ${NC}$1"; }
log_error() { echo -e "${RED}❌ ${NC}$1"; }

###############################################################################
# Configuration
###############################################################################

REMOTE_HOST="erp.insightpulseai.net"
REMOTE_USER="root"
ODOO_CONTAINER="odoo-odoo-1"
ODOO_DB="odoo"

###############################################################################
# Parse Arguments
###############################################################################

BACKUP_FILE=""

if [ $# -eq 0 ]; then
    log_error "Usage: $0 <backup_file>"
    log_info "Example: $0 /tmp/odoo_backup_ipai_finance_ppm_20251127_120000.sql"
    exit 1
fi

BACKUP_FILE="$1"

###############################################################################
# Validation
###############################################################################

validate_backup() {
    log_info "=== Validating Backup File ==="

    # Check if backup file exists on remote server
    if ! ssh ${REMOTE_USER}@${REMOTE_HOST} "test -f ${BACKUP_FILE}"; then
        log_error "Backup file not found on remote server: ${BACKUP_FILE}"
        log_info "Available backups:"
        ssh ${REMOTE_USER}@${REMOTE_HOST} "ls -lh /tmp/odoo_backup_*.sql 2>/dev/null || echo 'No backups found in /tmp/'"
        exit 1
    fi

    # Check backup file size (should be > 0)
    local size=$(ssh ${REMOTE_USER}@${REMOTE_HOST} "stat -c%s ${BACKUP_FILE}")
    if [ "$size" -eq 0 ]; then
        log_error "Backup file is empty: ${BACKUP_FILE}"
        exit 1
    fi

    log_success "Backup file validated: ${BACKUP_FILE} ($(numfmt --to=iec $size))"
}

###############################################################################
# Create Pre-Rollback Backup
###############################################################################

create_pre_rollback_backup() {
    log_info "=== Creating Pre-Rollback Backup ==="

    local timestamp=$(date +%Y%m%d_%H%M%S)
    local pre_rollback_backup="/tmp/odoo_pre_rollback_${timestamp}.sql"

    log_info "Creating safety backup before rollback: $pre_rollback_backup"

    if ! ssh ${REMOTE_USER}@${REMOTE_HOST} \
         "docker exec ${ODOO_CONTAINER} pg_dump -U odoo ${ODOO_DB} > ${pre_rollback_backup}"; then
        log_error "Pre-rollback backup failed"
        log_warning "Proceeding anyway (risky) - you have 5 seconds to Ctrl+C..."
        sleep 5
    else
        log_success "Pre-rollback backup created: $pre_rollback_backup"
    fi
}

###############################################################################
# Stop Odoo Container
###############################################################################

stop_odoo() {
    log_info "=== Stopping Odoo Container ==="

    log_info "Stopping ${ODOO_CONTAINER}..."

    if ! ssh ${REMOTE_USER}@${REMOTE_HOST} \
         "docker stop ${ODOO_CONTAINER}"; then
        log_error "Failed to stop Odoo container"
        exit 1
    fi

    log_success "Odoo container stopped"
}

###############################################################################
# Restore Database
###############################################################################

restore_database() {
    log_info "=== Restoring Database ==="

    log_info "Dropping existing database: ${ODOO_DB}"

    # Drop database
    if ! ssh ${REMOTE_USER}@${REMOTE_HOST} \
         "docker exec odoo-db-1 psql -U odoo -d postgres -c 'DROP DATABASE IF EXISTS ${ODOO_DB};'"; then
        log_error "Failed to drop database"
        exit 1
    fi

    log_info "Creating fresh database: ${ODOO_DB}"

    # Create database
    if ! ssh ${REMOTE_USER}@${REMOTE_HOST} \
         "docker exec odoo-db-1 psql -U odoo -d postgres -c 'CREATE DATABASE ${ODOO_DB} OWNER odoo;'"; then
        log_error "Failed to create database"
        exit 1
    fi

    log_info "Restoring from backup: ${BACKUP_FILE}"

    # Restore from backup
    if ! ssh ${REMOTE_USER}@${REMOTE_HOST} \
         "docker exec -i odoo-db-1 psql -U odoo ${ODOO_DB} < ${BACKUP_FILE}"; then
        log_error "Database restore failed"
        exit 1
    fi

    log_success "Database restored successfully"
}

###############################################################################
# Start Odoo Container
###############################################################################

start_odoo() {
    log_info "=== Starting Odoo Container ==="

    log_info "Starting ${ODOO_CONTAINER}..."

    if ! ssh ${REMOTE_USER}@${REMOTE_HOST} \
         "docker start ${ODOO_CONTAINER}"; then
        log_error "Failed to start Odoo container"
        exit 1
    fi

    # Wait for container to be ready
    log_info "Waiting for Odoo to start (20 seconds)..."
    sleep 20

    log_success "Odoo container started"
}

###############################################################################
# Verify Rollback
###############################################################################

verify_rollback() {
    log_info "=== Verifying Rollback ==="

    # Check container status
    local container_status=$(ssh ${REMOTE_USER}@${REMOTE_HOST} \
        "docker ps --filter name=${ODOO_CONTAINER} --format '{{.Status}}'")

    if [[ ! "$container_status" =~ "Up" ]]; then
        log_error "Odoo container not running: $container_status"
        exit 1
    fi

    log_success "Container status: $container_status"

    # Health check endpoint
    local health_url="https://${REMOTE_HOST}/web/health"

    log_info "Checking health endpoint: $health_url"

    local max_retries=10
    local retry=0

    while [ $retry -lt $max_retries ]; do
        if curl -sf "$health_url" | grep -q '"status": "pass"'; then
            log_success "Health check passed"
            return 0
        fi

        retry=$((retry + 1))
        if [ $retry -lt $max_retries ]; then
            log_warning "Health check attempt $retry/$max_retries failed, retrying..."
            sleep 5
        else
            log_error "Health check failed after $max_retries attempts"
            log_warning "Check Odoo logs:"
            log_info "ssh ${REMOTE_USER}@${REMOTE_HOST} 'docker logs ${ODOO_CONTAINER} --tail=50'"
            exit 1
        fi
    done
}

###############################################################################
# Main Execution
###############################################################################

main() {
    log_info "========================================="
    log_warning "Odoo Module Rollback"
    log_info "========================================="
    log_info "Backup file: ${BACKUP_FILE}"
    log_info "Target: ${REMOTE_USER}@${REMOTE_HOST}"
    log_info "Database: ${ODOO_DB}"
    log_info "========================================="
    echo ""

    # Confirm with user
    log_warning "This will restore the database from backup!"
    log_warning "All changes since backup will be LOST!"
    read -p "Continue? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        log_info "Rollback cancelled"
        exit 0
    fi

    # Execute rollback phases
    validate_backup
    create_pre_rollback_backup
    stop_odoo
    restore_database
    start_odoo
    verify_rollback

    # Success
    echo ""
    log_info "========================================="
    log_success "Rollback Completed Successfully!"
    log_info "========================================="
    log_info "Database restored from: ${BACKUP_FILE}"
    log_info "Odoo URL: https://${REMOTE_HOST}"
    log_info "========================================="
    echo ""
    log_warning "Next Steps:"
    log_info "1. Verify application functionality"
    log_info "2. Check Odoo logs if issues persist:"
    log_info "   ssh ${REMOTE_USER}@${REMOTE_HOST} 'docker logs ${ODOO_CONTAINER} --tail=100'"
    log_info "3. Fix the original deployment issue before redeploying"
}

# Run main function
main "$@"
