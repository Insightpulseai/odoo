#!/usr/bin/env bash
# =============================================================================
# Odoo Database Restore Script
# =============================================================================
# Restores an Odoo database from a backup file.
#
# Usage:
#   ./scripts/backup/restore_backup.sh --file BACKUP_FILE [--target DB] [--force]
#   ./scripts/backup/restore_backup.sh --tag TAG [--target DB] [--force]
#   ./scripts/backup/restore_backup.sh --latest [--target DB] [--force]
#
# Options:
#   --file FILE   Path to backup file (.sql.gz)
#   --tag TAG     Restore backup with specific tag
#   --latest      Restore latest backup
#   --target DB   Target database name (default: odoo_core)
#   --force       Drop existing database before restore
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
BACKUP_FILE=""
TAG=""
USE_LATEST=false
TARGET_DB="${ODOO_DB:-odoo_core}"
FORCE=false
BACKUP_DIR="${BACKUP_DIR:-/opt/backups/odoo}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --file)
            BACKUP_FILE="$2"
            shift 2
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --latest)
            USE_LATEST=true
            shift
            ;;
        --target)
            TARGET_DB="$2"
            shift 2
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Determine backup file
if [[ "$USE_LATEST" == "true" ]]; then
    BACKUP_FILE="$BACKUP_DIR/latest.sql.gz"
    if [[ -L "$BACKUP_FILE" ]]; then
        BACKUP_FILE=$(readlink -f "$BACKUP_FILE")
    fi
elif [[ -n "$TAG" ]]; then
    BACKUP_FILE=$(ls -t "$BACKUP_DIR"/backup_*"$TAG"*.sql.gz 2>/dev/null | head -1 || echo "")
fi

# Validate backup file
if [[ -z "$BACKUP_FILE" ]] || [[ ! -f "$BACKUP_FILE" ]]; then
    echo -e "${RED}Backup file not found: $BACKUP_FILE${NC}"
    echo ""
    echo "Usage:"
    echo "  $0 --file /path/to/backup.sql.gz"
    echo "  $0 --tag pre_golive_20260129"
    echo "  $0 --latest"
    exit 1
fi

# Banner
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Odoo Database Restore${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Backup File:  ${BLUE}$BACKUP_FILE${NC}"
echo -e "  Target DB:    ${BLUE}$TARGET_DB${NC}"
echo -e "  Force:        ${BLUE}$FORCE${NC}"
echo ""

# Verify backup file
echo -e "${BLUE}━━━ Verify Backup ━━━${NC}"

echo -n "  Checking file integrity... "
if gzip -t "$BACKUP_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

BACKUP_SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
echo -e "  Backup size: ${BLUE}$BACKUP_SIZE${NC}"
echo ""

# Check Docker Compose
COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"
if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo -e "${RED}docker-compose.yml not found${NC}"
    exit 1
fi

# =============================================================================
# Pre-Restore Checks
# =============================================================================
echo -e "${BLUE}━━━ Pre-Restore Checks ━━━${NC}"

# Check if target database exists
echo -n "  Checking target database... "
DB_EXISTS=$(docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U odoo -lqt 2>/dev/null | cut -d \| -f 1 | grep -w "$TARGET_DB" | wc -l || echo "0")

if [[ "$DB_EXISTS" -gt 0 ]]; then
    if [[ "$FORCE" == "true" ]]; then
        echo -e "${YELLOW}exists (will be dropped)${NC}"
    else
        echo -e "${RED}exists${NC}"
        echo -e "${RED}Database $TARGET_DB already exists. Use --force to overwrite.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}will be created${NC}"
fi

# Confirm destructive operation
if [[ "$FORCE" == "true" ]] && [[ "$DB_EXISTS" -gt 0 ]]; then
    echo ""
    echo -e "${YELLOW}WARNING: This will delete all data in $TARGET_DB${NC}"
    echo -n "  Type 'yes' to confirm: "
    read -r CONFIRM
    if [[ "$CONFIRM" != "yes" ]]; then
        echo -e "${RED}Aborted${NC}"
        exit 1
    fi
fi

echo ""

# =============================================================================
# Stop Odoo Service
# =============================================================================
echo -e "${BLUE}━━━ Stop Odoo Service ━━━${NC}"

echo -n "  Stopping Odoo... "
if docker compose -f "$COMPOSE_FILE" stop odoo-core 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ (may not be running)${NC}"
fi

# Wait for connections to close
sleep 3

# =============================================================================
# Restore Database
# =============================================================================
echo ""
echo -e "${BLUE}━━━ Restore Database ━━━${NC}"

# Drop existing database if force
if [[ "$FORCE" == "true" ]] && [[ "$DB_EXISTS" -gt 0 ]]; then
    echo -n "  Dropping existing database... "

    # Terminate connections
    docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U odoo -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$TARGET_DB' AND pid <> pg_backend_pid();" &>/dev/null || true

    if docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U odoo -c "DROP DATABASE IF EXISTS $TARGET_DB;" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        exit 1
    fi
fi

# Create database
echo -n "  Creating database... "
if docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U odoo -c "CREATE DATABASE $TARGET_DB;" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

# Restore backup
echo -n "  Restoring backup... "
if zcat "$BACKUP_FILE" | docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U odoo "$TARGET_DB" &>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

# =============================================================================
# Start Odoo Service
# =============================================================================
echo ""
echo -e "${BLUE}━━━ Start Odoo Service ━━━${NC}"

echo -n "  Starting Odoo... "
if docker compose -f "$COMPOSE_FILE" start odoo-core 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

# Wait for startup
echo -n "  Waiting for service... "
RETRIES=30
while [[ $RETRIES -gt 0 ]]; do
    if curl -s -o /dev/null http://localhost:8069/web/health 2>/dev/null || curl -s -o /dev/null http://localhost:8069/ 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        break
    fi
    sleep 2
    RETRIES=$((RETRIES - 1))
done

if [[ $RETRIES -eq 0 ]]; then
    echo -e "${YELLOW}⚠ (timeout)${NC}"
fi

# =============================================================================
# Post-Restore Verification
# =============================================================================
echo ""
echo -e "${BLUE}━━━ Post-Restore Verification ━━━${NC}"

# Check table count
echo -n "  Table count... "
TABLE_COUNT=$(docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U odoo "$TARGET_DB" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
echo -e "${GREEN}$TABLE_COUNT tables${NC}"

# Check record counts for key tables
echo -n "  User records... "
USER_COUNT=$(docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U odoo "$TARGET_DB" -t -c "SELECT count(*) FROM res_users;" 2>/dev/null | tr -d ' ' || echo "0")
echo -e "${GREEN}$USER_COUNT${NC}"

# =============================================================================
# Summary
# =============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Restore Complete${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Database restored successfully!${NC}"
echo ""
echo "  Source:   $BACKUP_FILE"
echo "  Target:   $TARGET_DB"
echo "  Tables:   $TABLE_COUNT"
echo "  Users:    $USER_COUNT"
echo ""
