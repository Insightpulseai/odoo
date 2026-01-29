#!/usr/bin/env bash
# =============================================================================
# Full Backup Script - Odoo.sh Multi-DC Parity (GAP 3)
# =============================================================================
# Creates comprehensive backups with S3 cross-region replication support
# Implements 3-datacenter backup strategy equivalent to Odoo.sh
#
# Usage:
#   ./scripts/backup/full_backup.sh [options]
#
# Options:
#   --db-only         Only backup database
#   --files-only      Only backup filestore
#   --region REGION   Upload to specific region (default: auto-detect)
#   --retain DAYS     Retention period in days (default: 30)
#   --dry-run         Show what would be done without executing
#   --verbose         Enable verbose output
# =============================================================================

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

# Script metadata
SCRIPT_VERSION="1.0.0"
SCRIPT_NAME=$(basename "$0")

# Directories
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-/var/backups/odoo}"
ODOO_DATA_DIR="${ODOO_DATA_DIR:-/var/lib/odoo}"
ODOO_FILESTORE="${ODOO_FILESTORE:-${ODOO_DATA_DIR}/filestore}"

# Database
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-odoo}"
DB_NAME="${DB_NAME:-odoo_core}"

# S3/Spaces configuration (multi-region)
PRIMARY_BUCKET="${S3_PRIMARY_BUCKET:-odoo-backups-primary}"
SECONDARY_BUCKET="${S3_SECONDARY_BUCKET:-odoo-backups-secondary}"
TERTIARY_BUCKET="${S3_TERTIARY_BUCKET:-odoo-backups-tertiary}"

# Regions (DigitalOcean Spaces or AWS S3)
PRIMARY_REGION="${PRIMARY_REGION:-sgp1}"      # Singapore
SECONDARY_REGION="${SECONDARY_REGION:-nyc3}"   # New York
TERTIARY_REGION="${TERTIARY_REGION:-ams3}"     # Amsterdam

# Retention
RETENTION_DAYS="${RETENTION_DAYS:-30}"
RETENTION_WEEKLY="${RETENTION_WEEKLY:-12}"     # Keep 12 weekly backups
RETENTION_MONTHLY="${RETENTION_MONTHLY:-6}"    # Keep 6 monthly backups

# Defaults
DB_ONLY=false
FILES_ONLY=false
DRY_RUN=false
VERBOSE=false
SPECIFIC_REGION=""

# =============================================================================
# Helper Functions
# =============================================================================

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case "$level" in
        INFO)  echo -e "[\033[0;32m$level\033[0m] $timestamp - $message" ;;
        WARN)  echo -e "[\033[0;33m$level\033[0m] $timestamp - $message" ;;
        ERROR) echo -e "[\033[0;31m$level\033[0m] $timestamp - $message" >&2 ;;
        DEBUG) [ "$VERBOSE" = true ] && echo -e "[\033[0;36m$level\033[0m] $timestamp - $message" ;;
    esac
}

die() {
    log ERROR "$@"
    exit 1
}

check_dependencies() {
    local deps=(pg_dump gzip aws date)
    local missing=()

    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            # Try s3cmd as fallback for aws
            if [ "$dep" = "aws" ] && command -v s3cmd &> /dev/null; then
                continue
            fi
            # Try doctl for DigitalOcean Spaces
            if [ "$dep" = "aws" ] && command -v doctl &> /dev/null; then
                continue
            fi
            missing+=("$dep")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        die "Missing dependencies: ${missing[*]}"
    fi
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --db-only)
                DB_ONLY=true
                shift
                ;;
            --files-only)
                FILES_ONLY=true
                shift
                ;;
            --region)
                SPECIFIC_REGION="$2"
                shift 2
                ;;
            --retain)
                RETENTION_DAYS="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                die "Unknown option: $1"
                ;;
        esac
    done
}

usage() {
    cat << EOF
Usage: $SCRIPT_NAME [OPTIONS]

Odoo Full Backup Script with Multi-DC Replication (Odoo.sh Parity)

Options:
    --db-only         Only backup database (skip filestore)
    --files-only      Only backup filestore (skip database)
    --region REGION   Upload to specific region only
    --retain DAYS     Retention period in days (default: $RETENTION_DAYS)
    --dry-run         Show what would be done
    --verbose, -v     Enable verbose output
    --help, -h        Show this help

Environment Variables:
    DB_HOST           Database host (default: localhost)
    DB_PORT           Database port (default: 5432)
    DB_USER           Database user (default: odoo)
    DB_NAME           Database name (default: odoo_core)
    PGPASSWORD        Database password (required)

    S3_PRIMARY_BUCKET     Primary S3/Spaces bucket
    S3_SECONDARY_BUCKET   Secondary bucket (different region)
    S3_TERTIARY_BUCKET    Tertiary bucket (third region)

    PRIMARY_REGION    Primary region (default: sgp1)
    SECONDARY_REGION  Secondary region (default: nyc3)
    TERTIARY_REGION   Tertiary region (default: ams3)

Example:
    # Full backup to all regions
    PGPASSWORD=secret ./full_backup.sh

    # Database only to specific region
    PGPASSWORD=secret ./full_backup.sh --db-only --region sgp1

    # Dry run to see what would happen
    ./full_backup.sh --dry-run --verbose

EOF
}

# =============================================================================
# Backup Functions
# =============================================================================

backup_database() {
    local timestamp="$1"
    local backup_file="${BACKUP_BASE_DIR}/db/odoo_${DB_NAME}_${timestamp}.sql.gz"

    log INFO "Starting database backup: $DB_NAME"
    log DEBUG "Target: $backup_file"

    if [ "$DRY_RUN" = true ]; then
        log INFO "[DRY-RUN] Would create database backup: $backup_file"
        echo "$backup_file"
        return 0
    fi

    mkdir -p "$(dirname "$backup_file")"

    # Create backup with pg_dump
    pg_dump \
        --host="$DB_HOST" \
        --port="$DB_PORT" \
        --username="$DB_USER" \
        --no-password \
        --format=custom \
        --compress=9 \
        --file="${backup_file%.gz}" \
        "$DB_NAME" 2>/dev/null || {
            # Fallback to plain format with gzip
            pg_dump \
                --host="$DB_HOST" \
                --port="$DB_PORT" \
                --username="$DB_USER" \
                --no-password \
                "$DB_NAME" 2>/dev/null | gzip > "$backup_file"
        }

    local size=$(du -h "$backup_file" 2>/dev/null | cut -f1 || echo "unknown")
    log INFO "Database backup complete: $size"

    echo "$backup_file"
}

backup_filestore() {
    local timestamp="$1"
    local backup_file="${BACKUP_BASE_DIR}/files/odoo_filestore_${timestamp}.tar.gz"

    log INFO "Starting filestore backup: $ODOO_FILESTORE"
    log DEBUG "Target: $backup_file"

    if [ ! -d "$ODOO_FILESTORE" ]; then
        log WARN "Filestore directory not found: $ODOO_FILESTORE"
        return 0
    fi

    if [ "$DRY_RUN" = true ]; then
        log INFO "[DRY-RUN] Would create filestore backup: $backup_file"
        echo "$backup_file"
        return 0
    fi

    mkdir -p "$(dirname "$backup_file")"

    tar -czf "$backup_file" \
        -C "$(dirname "$ODOO_FILESTORE")" \
        "$(basename "$ODOO_FILESTORE")" 2>/dev/null

    local size=$(du -h "$backup_file" 2>/dev/null | cut -f1 || echo "unknown")
    log INFO "Filestore backup complete: $size"

    echo "$backup_file"
}

create_manifest() {
    local timestamp="$1"
    local db_file="$2"
    local files_file="$3"
    local manifest_file="${BACKUP_BASE_DIR}/manifests/backup_${timestamp}.json"

    if [ "$DRY_RUN" = true ]; then
        log INFO "[DRY-RUN] Would create manifest: $manifest_file"
        return 0
    fi

    mkdir -p "$(dirname "$manifest_file")"

    cat > "$manifest_file" << EOF
{
    "version": "$SCRIPT_VERSION",
    "timestamp": "$timestamp",
    "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "hostname": "$(hostname)",
    "database": {
        "name": "$DB_NAME",
        "host": "$DB_HOST",
        "file": "$db_file",
        "size_bytes": $(stat -f%z "$db_file" 2>/dev/null || stat -c%s "$db_file" 2>/dev/null || echo "0")
    },
    "filestore": {
        "path": "$ODOO_FILESTORE",
        "file": "$files_file",
        "size_bytes": $(stat -f%z "$files_file" 2>/dev/null || stat -c%s "$files_file" 2>/dev/null || echo "0")
    },
    "regions": {
        "primary": "$PRIMARY_REGION",
        "secondary": "$SECONDARY_REGION",
        "tertiary": "$TERTIARY_REGION"
    },
    "retention": {
        "daily_days": $RETENTION_DAYS,
        "weekly_weeks": $RETENTION_WEEKLY,
        "monthly_months": $RETENTION_MONTHLY
    }
}
EOF

    log INFO "Manifest created: $manifest_file"
    echo "$manifest_file"
}

# =============================================================================
# S3/Spaces Upload Functions
# =============================================================================

upload_to_region() {
    local file="$1"
    local region="$2"
    local bucket="$3"

    local filename=$(basename "$file")
    local date_prefix=$(date +%Y/%m/%d)
    local s3_path="s3://${bucket}/${date_prefix}/${filename}"

    log INFO "Uploading to $region: $filename"
    log DEBUG "Target: $s3_path"

    if [ "$DRY_RUN" = true ]; then
        log INFO "[DRY-RUN] Would upload $file to $s3_path"
        return 0
    fi

    # Try AWS CLI first
    if command -v aws &> /dev/null; then
        aws s3 cp "$file" "$s3_path" \
            --region "$region" \
            --storage-class STANDARD_IA \
            --only-show-errors
    # Try s3cmd
    elif command -v s3cmd &> /dev/null; then
        s3cmd put "$file" "$s3_path" \
            --storage-class=STANDARD_IA \
            --no-progress
    # Try doctl for DigitalOcean Spaces
    elif command -v doctl &> /dev/null; then
        doctl compute cdn flush "$bucket" 2>/dev/null || true
        # Use s3cmd with DO Spaces endpoint
        s3cmd --host="${region}.digitaloceanspaces.com" \
              --host-bucket="%(bucket)s.${region}.digitaloceanspaces.com" \
              put "$file" "$s3_path" \
              --no-progress 2>/dev/null || {
            log WARN "Upload to $region failed, trying fallback..."
            return 1
        }
    else
        log ERROR "No S3-compatible CLI found"
        return 1
    fi

    log INFO "Upload complete: $region"
    return 0
}

upload_multi_region() {
    local file="$1"

    local success_count=0
    local regions_to_upload=()

    # Determine which regions to upload to
    if [ -n "$SPECIFIC_REGION" ]; then
        regions_to_upload=("$SPECIFIC_REGION:$PRIMARY_BUCKET")
    else
        regions_to_upload=(
            "$PRIMARY_REGION:$PRIMARY_BUCKET"
            "$SECONDARY_REGION:$SECONDARY_BUCKET"
            "$TERTIARY_REGION:$TERTIARY_BUCKET"
        )
    fi

    for region_bucket in "${regions_to_upload[@]}"; do
        local region="${region_bucket%%:*}"
        local bucket="${region_bucket##*:}"

        if upload_to_region "$file" "$region" "$bucket"; then
            success_count=$((success_count + 1))
        fi
    done

    if [ $success_count -eq 0 ]; then
        log ERROR "Failed to upload to any region"
        return 1
    fi

    log INFO "Successfully uploaded to $success_count region(s)"
    return 0
}

# =============================================================================
# Cleanup Functions
# =============================================================================

cleanup_old_backups() {
    log INFO "Cleaning up old backups (retention: $RETENTION_DAYS days)"

    if [ "$DRY_RUN" = true ]; then
        log INFO "[DRY-RUN] Would clean up backups older than $RETENTION_DAYS days"
        return 0
    fi

    # Local cleanup
    find "$BACKUP_BASE_DIR" -type f -mtime +"$RETENTION_DAYS" -name "*.gz" -delete 2>/dev/null || true
    find "$BACKUP_BASE_DIR" -type f -mtime +"$RETENTION_DAYS" -name "*.json" -delete 2>/dev/null || true

    # Clean empty directories
    find "$BACKUP_BASE_DIR" -type d -empty -delete 2>/dev/null || true

    log INFO "Local cleanup complete"

    # S3 cleanup (if lifecycle rules not configured)
    # This is typically handled by S3 lifecycle policies
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    log INFO "=== Odoo Full Backup Script v$SCRIPT_VERSION ==="
    log INFO "Multi-DC Replication (Odoo.sh Parity)"

    # Parse command line arguments
    parse_args "$@"

    # Check dependencies
    check_dependencies

    # Generate timestamp
    local timestamp=$(date +%Y%m%d_%H%M%S)
    log INFO "Backup timestamp: $timestamp"

    # Create backup directory
    mkdir -p "$BACKUP_BASE_DIR"/{db,files,manifests}

    local db_backup=""
    local files_backup=""

    # Database backup
    if [ "$FILES_ONLY" = false ]; then
        db_backup=$(backup_database "$timestamp")
    fi

    # Filestore backup
    if [ "$DB_ONLY" = false ]; then
        files_backup=$(backup_filestore "$timestamp")
    fi

    # Create manifest
    local manifest=$(create_manifest "$timestamp" "$db_backup" "$files_backup")

    # Upload to multi-region storage
    log INFO "Starting multi-region upload..."

    local upload_failed=false

    if [ -n "$db_backup" ] && [ -f "$db_backup" ]; then
        upload_multi_region "$db_backup" || upload_failed=true
    fi

    if [ -n "$files_backup" ] && [ -f "$files_backup" ]; then
        upload_multi_region "$files_backup" || upload_failed=true
    fi

    if [ -n "$manifest" ] && [ -f "$manifest" ]; then
        upload_multi_region "$manifest" || upload_failed=true
    fi

    # Cleanup old backups
    cleanup_old_backups

    # Summary
    log INFO "=== Backup Summary ==="
    log INFO "Timestamp: $timestamp"
    [ -n "$db_backup" ] && log INFO "Database: $db_backup"
    [ -n "$files_backup" ] && log INFO "Filestore: $files_backup"
    [ -n "$manifest" ] && log INFO "Manifest: $manifest"

    if [ "$upload_failed" = true ]; then
        log WARN "Some uploads failed, check logs for details"
        exit 1
    fi

    log INFO "=== Backup Complete ==="
}

# Run main
main "$@"
