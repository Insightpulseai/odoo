#!/usr/bin/env bash
# =============================================================================
# Odoo Database Backup Script
# =============================================================================
# Creates a backup of the Odoo database with optional filestore.
#
# Usage:
#   ./scripts/backup/create_backup.sh [--full] [--tag TAG] [--keep N]
#
# Options:
#   --full      Include filestore in backup
#   --tag TAG   Add custom tag to backup name
#   --keep N    Keep only last N backups (default: 7)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Defaults
INCLUDE_FILESTORE=false
CUSTOM_TAG=""
KEEP_BACKUPS=7
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-/opt/backups/odoo}"
SOURCE_DB="${ODOO_DB:-odoo_core}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --full)
            INCLUDE_FILESTORE=true
            shift
            ;;
        --tag)
            CUSTOM_TAG="_$2"
            shift 2
            ;;
        --keep)
            KEEP_BACKUPS="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Backup filename
if [[ -n "$CUSTOM_TAG" ]]; then
    BACKUP_NAME="backup${CUSTOM_TAG}_$TIMESTAMP"
else
    BACKUP_NAME="backup_$TIMESTAMP"
fi

# Banner
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Odoo Database Backup${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Database:     ${BLUE}$SOURCE_DB${NC}"
echo -e "  Backup Name:  ${BLUE}$BACKUP_NAME${NC}"
echo -e "  Backup Dir:   ${BLUE}$BACKUP_DIR${NC}"
echo -e "  Filestore:    ${BLUE}$INCLUDE_FILESTORE${NC}"
echo ""

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Check Docker Compose
COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"
if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo -e "${RED}docker-compose.yml not found${NC}"
    exit 1
fi

# =============================================================================
# Create Database Backup
# =============================================================================
echo -e "${BLUE}━━━ Database Backup ━━━${NC}"

BACKUP_FILE="$BACKUP_DIR/${BACKUP_NAME}.sql.gz"

echo -n "  Dumping database... "
if docker compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U odoo "$SOURCE_DB" | gzip > "$BACKUP_FILE" 2>/dev/null; then
    BACKUP_SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
    echo -e "${GREEN}✓ ($BACKUP_SIZE)${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

# Verify backup
echo -n "  Verifying backup... "
if gzip -t "$BACKUP_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

# =============================================================================
# Create Filestore Backup (Optional)
# =============================================================================
if [[ "$INCLUDE_FILESTORE" == "true" ]]; then
    echo ""
    echo -e "${BLUE}━━━ Filestore Backup ━━━${NC}"

    FILESTORE_BACKUP="$BACKUP_DIR/${BACKUP_NAME}_filestore.tar.gz"

    echo -n "  Archiving filestore... "

    # Get filestore path from container
    FILESTORE_PATH=$(docker compose -f "$COMPOSE_FILE" exec -T odoo-core printenv ODOO_DATA_DIR 2>/dev/null || echo "/var/lib/odoo")
    FILESTORE_PATH="${FILESTORE_PATH}/filestore/$SOURCE_DB"

    if docker compose -f "$COMPOSE_FILE" exec -T odoo-core tar czf - -C "$FILESTORE_PATH" . > "$FILESTORE_BACKUP" 2>/dev/null; then
        FILESTORE_SIZE=$(ls -lh "$FILESTORE_BACKUP" | awk '{print $5}')
        echo -e "${GREEN}✓ ($FILESTORE_SIZE)${NC}"
    else
        echo -e "${YELLOW}⚠ (filestore may be empty)${NC}"
        rm -f "$FILESTORE_BACKUP"
    fi
fi

# =============================================================================
# Cleanup Old Backups
# =============================================================================
echo ""
echo -e "${BLUE}━━━ Cleanup ━━━${NC}"

echo -n "  Removing old backups (keeping $KEEP_BACKUPS)... "
REMOVED_COUNT=0

# Remove old database backups
for old_backup in $(ls -t "$BACKUP_DIR"/backup_*.sql.gz 2>/dev/null | tail -n +$((KEEP_BACKUPS + 1))); do
    rm -f "$old_backup"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
done

# Remove old filestore backups
for old_backup in $(ls -t "$BACKUP_DIR"/backup_*_filestore.tar.gz 2>/dev/null | tail -n +$((KEEP_BACKUPS + 1))); do
    rm -f "$old_backup"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
done

echo -e "${GREEN}$REMOVED_COUNT removed${NC}"

# =============================================================================
# Create Latest Symlink
# =============================================================================
echo -n "  Updating latest symlink... "
ln -sf "$BACKUP_FILE" "$BACKUP_DIR/latest.sql.gz"
echo -e "${GREEN}✓${NC}"

# =============================================================================
# Summary
# =============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Backup Complete${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Backup created successfully!${NC}"
echo ""
echo "  Database:   $BACKUP_FILE ($BACKUP_SIZE)"
if [[ "$INCLUDE_FILESTORE" == "true" ]] && [[ -f "$FILESTORE_BACKUP" ]]; then
    echo "  Filestore:  $FILESTORE_BACKUP ($FILESTORE_SIZE)"
fi
echo "  Symlink:    $BACKUP_DIR/latest.sql.gz"
echo ""

# Output backup path for scripting
echo "$BACKUP_FILE"
