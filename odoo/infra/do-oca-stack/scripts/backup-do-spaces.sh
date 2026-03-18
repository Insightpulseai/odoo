#!/usr/bin/env bash
# Backup Odoo database and filestore to DigitalOcean Spaces
# Requires: s3cmd configured with DO Spaces credentials
#
# Usage: ./backup-do-spaces.sh [bucket-name]
#
# Environment variables:
#   DO_SPACES_BUCKET - S3 bucket name (or pass as $1)
#   DO_SPACES_REGION - Region (default: nyc3)
#   COMPOSE_PROJECT_NAME - Docker Compose project name
#   BACKUP_RETENTION_DAYS - Days to keep backups (default: 30)

set -euo pipefail

# Configuration
BUCKET="${DO_SPACES_BUCKET:-${1:-}}"
REGION="${DO_SPACES_REGION:-nyc3}"
PROJECT="${COMPOSE_PROJECT_NAME:-odoo-oca}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
TIMESTAMP="$(date -u +%Y%m%d-%H%M%S)"
BACKUP_DIR="/tmp/odoo-backup-${TIMESTAMP}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $*"; }
warn() { echo -e "${YELLOW}[$(date +%H:%M:%S)] WARN:${NC} $*"; }
error() { echo -e "${RED}[$(date +%H:%M:%S)] ERROR:${NC} $*" >&2; }

cleanup() {
  log "Cleaning up temporary files..."
  rm -rf "${BACKUP_DIR}"
}
trap cleanup EXIT

# Validate
if [[ -z "${BUCKET}" ]]; then
  error "No bucket specified. Set DO_SPACES_BUCKET or pass as argument."
  exit 1
fi

if ! command -v s3cmd &>/dev/null; then
  error "s3cmd not found. Install with: apt install s3cmd"
  exit 1
fi

# Create backup directory
mkdir -p "${BACKUP_DIR}"
log "Starting backup to s3://${BUCKET}/odoo-backups/${TIMESTAMP}/"

# -----------------------------------------
# 1. Database backup
# -----------------------------------------
log "Backing up PostgreSQL database..."
docker compose exec -T db pg_dump -U odoo -Fc odoo > "${BACKUP_DIR}/odoo.dump"
DB_SIZE=$(du -h "${BACKUP_DIR}/odoo.dump" | cut -f1)
log "Database backup: ${DB_SIZE}"

# -----------------------------------------
# 2. Filestore backup
# -----------------------------------------
log "Backing up filestore..."
if docker volume inspect "${PROJECT}_odoo-filestore" &>/dev/null; then
  docker run --rm \
    -v "${PROJECT}_odoo-filestore:/data:ro" \
    -v "${BACKUP_DIR}:/backup" \
    alpine tar czf /backup/filestore.tar.gz -C /data .
  FS_SIZE=$(du -h "${BACKUP_DIR}/filestore.tar.gz" | cut -f1)
  log "Filestore backup: ${FS_SIZE}"
else
  warn "Filestore volume not found, skipping"
fi

# -----------------------------------------
# 3. Create manifest
# -----------------------------------------
cat > "${BACKUP_DIR}/manifest.json" <<EOF
{
  "timestamp": "${TIMESTAMP}",
  "project": "${PROJECT}",
  "database": {
    "file": "odoo.dump",
    "format": "custom",
    "size": "$(stat -f%z "${BACKUP_DIR}/odoo.dump" 2>/dev/null || stat -c%s "${BACKUP_DIR}/odoo.dump")"
  },
  "filestore": {
    "file": "filestore.tar.gz",
    "exists": $(test -f "${BACKUP_DIR}/filestore.tar.gz" && echo true || echo false)
  },
  "git_sha": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

# -----------------------------------------
# 4. Upload to Spaces
# -----------------------------------------
log "Uploading to DigitalOcean Spaces..."
S3_PATH="s3://${BUCKET}/odoo-backups/${TIMESTAMP}"

s3cmd put "${BACKUP_DIR}/odoo.dump" "${S3_PATH}/odoo.dump"
s3cmd put "${BACKUP_DIR}/manifest.json" "${S3_PATH}/manifest.json"

if [[ -f "${BACKUP_DIR}/filestore.tar.gz" ]]; then
  s3cmd put "${BACKUP_DIR}/filestore.tar.gz" "${S3_PATH}/filestore.tar.gz"
fi

# Create "latest" pointer
echo "${TIMESTAMP}" | s3cmd put - "s3://${BUCKET}/odoo-backups/LATEST"

log "Upload complete: ${S3_PATH}"

# -----------------------------------------
# 5. Cleanup old backups
# -----------------------------------------
log "Cleaning up backups older than ${RETENTION_DAYS} days..."
CUTOFF_DATE=$(date -d "${RETENTION_DAYS} days ago" +%Y%m%d 2>/dev/null || \
              date -v-${RETENTION_DAYS}d +%Y%m%d)

s3cmd ls "s3://${BUCKET}/odoo-backups/" | while read -r line; do
  backup_date=$(echo "$line" | grep -oE '[0-9]{8}-[0-9]{6}' | head -1 | cut -d'-' -f1)
  if [[ -n "$backup_date" && "$backup_date" < "$CUTOFF_DATE" ]]; then
    backup_path=$(echo "$line" | awk '{print $NF}')
    if [[ "$backup_path" == s3://* ]]; then
      log "Deleting old backup: $backup_path"
      s3cmd del --recursive "$backup_path" || true
    fi
  fi
done

# -----------------------------------------
# Summary
# -----------------------------------------
echo ""
echo "=========================================="
echo -e "${GREEN}BACKUP COMPLETE${NC}"
echo "=========================================="
echo "Location: ${S3_PATH}"
echo "Database: odoo.dump (${DB_SIZE})"
echo "Filestore: ${FS_SIZE:-skipped}"
echo "Manifest: manifest.json"
echo "=========================================="
