#!/bin/bash
# =============================================================================
# Production Backup Script for InsightPulse ERP
# =============================================================================
# This script creates comprehensive backups of:
# - PostgreSQL database
# - Odoo filestore (documents, attachments)
# - Configuration files
#
# Usage:
#   ./ops/backup-production.sh              # Full backup
#   ./ops/backup-production.sh --db-only    # Database only
#   ./ops/backup-production.sh --verify     # Verify latest backup
#
# Schedule with cron:
#   0 2 * * * /opt/odoo-ce/ops/backup-production.sh >> /var/log/odoo_backup.log 2>&1
# =============================================================================

set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups/odoo}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
DATE=$(date +%Y%m%d_%H%M%S)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}/.."

# Container/service names (adjust as needed)
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-db}"
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo}"
DB_USER="${DB_USER:-odoo}"
DB_NAME="${DB_NAME:-odoo}"

# S3 configuration (optional)
S3_BUCKET="${S3_BUCKET:-}"
AWS_REGION="${AWS_REGION:-ap-southeast-1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging
log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running in Docker context
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi

    if ! docker compose ps &> /dev/null; then
        log_warning "Docker Compose not running. Using direct commands."
        return 1
    fi
    return 0
}

# Create backup directory
setup_backup_dir() {
    mkdir -p "$BACKUP_DIR"
    log "Backup directory: $BACKUP_DIR"
}

# Database backup
backup_database() {
    log "Starting database backup..."

    local db_backup="$BACKUP_DIR/odoo_db_${DATE}.sql.gz"

    if check_docker; then
        # Docker-based backup
        docker compose exec -T "$POSTGRES_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$db_backup"
    else
        # Direct PostgreSQL backup
        pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$db_backup"
    fi

    # Verify backup integrity
    if gzip -t "$db_backup" 2>/dev/null; then
        local size=$(du -h "$db_backup" | cut -f1)
        log_success "Database backup complete: $db_backup ($size)"
        echo "$db_backup"
    else
        log_error "Database backup verification failed!"
        rm -f "$db_backup"
        exit 1
    fi
}

# Filestore backup
backup_filestore() {
    log "Starting filestore backup..."

    local filestore_backup="$BACKUP_DIR/odoo_filestore_${DATE}.tar.gz"

    # Common filestore locations
    local filestore_paths=(
        "/opt/odoo-ce/.local/share/Odoo/filestore"
        "/var/lib/odoo/filestore"
        "./data/filestore"
    )

    local found_path=""
    for path in "${filestore_paths[@]}"; do
        if [ -d "$path" ]; then
            found_path="$path"
            break
        fi
    done

    if [ -n "$found_path" ]; then
        tar -czf "$filestore_backup" -C "$(dirname "$found_path")" "$(basename "$found_path")" 2>/dev/null || true
        local size=$(du -h "$filestore_backup" 2>/dev/null | cut -f1 || echo "0")
        log_success "Filestore backup complete: $filestore_backup ($size)"
        echo "$filestore_backup"
    else
        log_warning "Filestore not found at common locations. Skipping."
    fi
}

# Configuration backup
backup_config() {
    log "Starting configuration backup..."

    local config_backup="$BACKUP_DIR/odoo_config_${DATE}.tar.gz"

    # Configuration files to backup
    local config_files=(
        "$PROJECT_DIR/deploy/odoo.conf"
        "$PROJECT_DIR/deploy/.env"
        "$PROJECT_DIR/deploy/docker-compose.prod.yml"
        "$PROJECT_DIR/docker-compose.yml"
    )

    local files_to_backup=""
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            files_to_backup="$files_to_backup $file"
        fi
    done

    if [ -n "$files_to_backup" ]; then
        tar -czf "$config_backup" $files_to_backup 2>/dev/null || true
        log_success "Configuration backup complete: $config_backup"
        echo "$config_backup"
    else
        log_warning "No configuration files found to backup"
    fi
}

# Upload to S3 (if configured)
upload_to_s3() {
    if [ -z "$S3_BUCKET" ]; then
        log "S3 upload not configured. Skipping."
        return
    fi

    if ! command -v aws &> /dev/null; then
        log_warning "AWS CLI not installed. Skipping S3 upload."
        return
    fi

    log "Uploading backups to S3: $S3_BUCKET"

    aws s3 cp "$BACKUP_DIR/" "s3://$S3_BUCKET/$(date +%Y/%m)/" \
        --recursive \
        --include "*_${DATE}*" \
        --region "$AWS_REGION"

    log_success "S3 upload complete"
}

# Cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."

    local deleted=0
    while IFS= read -r -d '' file; do
        rm -f "$file"
        ((deleted++))
    done < <(find "$BACKUP_DIR" -type f -mtime +"$RETENTION_DAYS" -print0 2>/dev/null)

    if [ $deleted -gt 0 ]; then
        log_success "Deleted $deleted old backup file(s)"
    else
        log "No old backups to delete"
    fi
}

# Verify backup
verify_backup() {
    log "Verifying latest backup..."

    local latest_db=$(ls -t "$BACKUP_DIR"/odoo_db_*.sql.gz 2>/dev/null | head -1)

    if [ -z "$latest_db" ]; then
        log_error "No database backups found!"
        exit 1
    fi

    # Check file exists and has content
    if [ ! -s "$latest_db" ]; then
        log_error "Latest backup is empty: $latest_db"
        exit 1
    fi

    # Verify gzip integrity
    if ! gzip -t "$latest_db" 2>/dev/null; then
        log_error "Latest backup is corrupted: $latest_db"
        exit 1
    fi

    local size=$(du -h "$latest_db" | cut -f1)
    local date=$(stat -c %y "$latest_db" 2>/dev/null || stat -f %Sm "$latest_db")

    log_success "Latest backup verified:"
    echo "  File: $latest_db"
    echo "  Size: $size"
    echo "  Date: $date"
}

# Send notification (placeholder for webhook/email)
send_notification() {
    local status="$1"
    local message="$2"

    # Placeholder for webhook notification
    # curl -X POST "${NOTIFICATION_WEBHOOK}" -d "{\"status\": \"$status\", \"message\": \"$message\"}"

    log "Notification: $status - $message"
}

# Main execution
main() {
    local mode="${1:-full}"

    log "======================================"
    log "InsightPulse ERP Backup - $DATE"
    log "======================================"

    setup_backup_dir

    case "$mode" in
        --db-only)
            backup_database
            ;;
        --verify)
            verify_backup
            exit 0
            ;;
        *)
            backup_database
            backup_filestore
            backup_config
            upload_to_s3
            cleanup_old_backups
            ;;
    esac

    log "======================================"
    log_success "Backup completed successfully!"

    # Send success notification
    send_notification "success" "Daily backup completed - $DATE"
}

# Error handling
trap 'log_error "Backup failed at line $LINENO"; send_notification "failed" "Backup failed at $(date)"' ERR

# Run
main "$@"
