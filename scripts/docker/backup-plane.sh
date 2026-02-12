#!/bin/bash
# backup-plane.sh
# Automated backup for Plane stack (PostgreSQL + MinIO)
#
# Portfolio Initiative: PORT-2026-010
# Process: PROC-BACKUP-001
# Control: CTRL-BACKUP-001

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

BACKUP_DIR="backups/plane"
RETENTION_DAYS=7
WEEKLY_RETENTION_WEEKS=4
TIMESTAMP=$(date +%Y%m%d_%H%M)

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

check_container() {
    local container=$1
    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        error "Container ${container} is not running"
        return 1
    fi
    log "✅ Container ${container} is running"
    return 0
}

# ============================================================================
# Pre-flight Checks
# ============================================================================

log "Starting Plane stack backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"
log "✅ Backup directory: $BACKUP_DIR"

# Check if Plane containers are running
if ! check_container "plane-db-1"; then
    error "Plane DB container is not running. Backup aborted."
    exit 1
fi

# ============================================================================
# PostgreSQL Backup
# ============================================================================

log "Backing up Plane PostgreSQL database..."

BACKUP_FILE="${BACKUP_DIR}/plane_pg_${TIMESTAMP}.sql"

if docker exec -t plane-db-1 pg_dumpall -U postgres > "$BACKUP_FILE" 2>/dev/null; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "✅ PostgreSQL backup complete: ${BACKUP_FILE} (${BACKUP_SIZE})"
else
    error "PostgreSQL backup failed"
    exit 1
fi

# Compress backup
log "Compressing backup..."
if gzip "$BACKUP_FILE"; then
    COMPRESSED_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
    log "✅ Compression complete: ${BACKUP_FILE}.gz (${COMPRESSED_SIZE})"
else
    warn "Compression failed, keeping uncompressed backup"
fi

# ============================================================================
# MinIO Backup (Optional)
# ============================================================================

if command -v mc &> /dev/null; then
    log "MinIO CLI (mc) detected, backing up MinIO buckets..."

    # Check if MinIO alias exists
    if mc alias list | grep -q "plane-alias"; then
        MINIO_BACKUP_DIR="${BACKUP_DIR}/minio_${TIMESTAMP}"
        mkdir -p "$MINIO_BACKUP_DIR"

        if mc mirror plane-alias/plane-bucket "$MINIO_BACKUP_DIR" 2>/dev/null; then
            MINIO_SIZE=$(du -sh "$MINIO_BACKUP_DIR" | cut -f1)
            log "✅ MinIO backup complete: ${MINIO_BACKUP_DIR} (${MINIO_SIZE})"
        else
            warn "MinIO backup failed (alias or bucket may not exist)"
        fi
    else
        warn "MinIO alias 'plane-alias' not configured, skipping MinIO backup"
        warn "To configure: mc alias set plane-alias http://localhost:9000 <access-key> <secret-key>"
    fi
else
    warn "MinIO CLI (mc) not installed, skipping MinIO backup"
    warn "Install: brew install minio/stable/mc (macOS) or https://min.io/docs/minio/linux/reference/minio-mc.html"
fi

# ============================================================================
# Cleanup Old Backups
# ============================================================================

log "Cleaning up old backups (retention: ${RETENTION_DAYS} days)..."

# Remove daily backups older than retention period
DELETED_COUNT=$(find "$BACKUP_DIR" -name "plane_pg_*.sql.gz" -mtime +${RETENTION_DAYS} -delete -print | wc -l | tr -d ' ')

if [ "$DELETED_COUNT" -gt 0 ]; then
    log "✅ Deleted ${DELETED_COUNT} old daily backup(s)"
else
    log "No old daily backups to delete"
fi

# Weekly snapshot logic (keep one backup per week for 4 weeks)
log "Maintaining weekly snapshots (retention: ${WEEKLY_RETENTION_WEEKS} weeks)..."

WEEKLY_DIR="${BACKUP_DIR}/weekly"
mkdir -p "$WEEKLY_DIR"

# If today is Sunday (day 0), create weekly snapshot
if [ "$(date +%u)" -eq 7 ]; then
    WEEKLY_BACKUP="${WEEKLY_DIR}/plane_pg_weekly_$(date +%Y%W).sql.gz"

    if [ -f "${BACKUP_FILE}.gz" ]; then
        cp "${BACKUP_FILE}.gz" "$WEEKLY_BACKUP"
        log "✅ Created weekly snapshot: $WEEKLY_BACKUP"
    fi
fi

# Cleanup old weekly snapshots (older than 4 weeks)
DELETED_WEEKLY=$(find "$WEEKLY_DIR" -name "plane_pg_weekly_*.sql.gz" -mtime +$((WEEKLY_RETENTION_WEEKS * 7)) -delete -print | wc -l | tr -d ' ')

if [ "$DELETED_WEEKLY" -gt 0 ]; then
    log "✅ Deleted ${DELETED_WEEKLY} old weekly snapshot(s)"
fi

# ============================================================================
# Backup Summary
# ============================================================================

log "========================================="
log "Backup Summary:"
log "========================================="
log "Timestamp: $TIMESTAMP"
log "Backup Location: $BACKUP_DIR"
log "Total Backup Size: $(du -sh "$BACKUP_DIR" | cut -f1)"
log "Daily Backups: $(find "$BACKUP_DIR" -name "plane_pg_*.sql.gz" -mtime -${RETENTION_DAYS} | wc -l | tr -d ' ')"
log "Weekly Snapshots: $(find "$WEEKLY_DIR" -name "plane_pg_weekly_*.sql.gz" 2>/dev/null | wc -l | tr -d ' ')"
log "========================================="
log "✅ Plane backup complete"

# ============================================================================
# Exit
# ============================================================================

exit 0
