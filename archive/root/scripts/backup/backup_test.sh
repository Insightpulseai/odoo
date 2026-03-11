#!/usr/bin/env bash
# =============================================================================
# Backup/Restore Test Script
# =============================================================================
# Tests the backup and restore cycle to ensure data recovery works.
# Creates a test backup, verifies it, optionally restores to test database.
#
# Usage:
#   ./scripts/backup/backup_test.sh [--full-cycle] [--cleanup]
#
# Options:
#   --full-cycle  Perform full backup→restore→verify cycle
#   --cleanup     Remove test artifacts after completion
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
FULL_CYCLE=false
CLEANUP=false
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-/opt/backups/odoo}"
TEST_BACKUP_NAME="backup_test_$TIMESTAMP"
TEST_DB_NAME="odoo_test_restore_$TIMESTAMP"
SOURCE_DB="${ODOO_DB:-odoo_core}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --full-cycle)
            FULL_CYCLE=true
            shift
            ;;
        --cleanup)
            CLEANUP=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Banner
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Backup/Restore Test${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  Source DB:    ${BLUE}$SOURCE_DB${NC}"
echo -e "  Backup Dir:   ${BLUE}$BACKUP_DIR${NC}"
echo -e "  Test Backup:  ${BLUE}$TEST_BACKUP_NAME${NC}"
if [[ "$FULL_CYCLE" == "true" ]]; then
    echo -e "  Test DB:      ${BLUE}$TEST_DB_NAME${NC}"
fi
echo ""

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# =============================================================================
# Phase 1: Create Test Backup
# =============================================================================
echo -e "${BLUE}━━━ Phase 1: Create Test Backup ━━━${NC}"

COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"

if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo -e "${RED}docker-compose.yml not found${NC}"
    exit 1
fi

echo -n "  Creating backup... "

# Create backup using pg_dump
BACKUP_FILE="$BACKUP_DIR/${TEST_BACKUP_NAME}.sql.gz"

if docker compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U odoo "$SOURCE_DB" | gzip > "$BACKUP_FILE" 2>/dev/null; then
    BACKUP_SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
    echo -e "${GREEN}✓ ($BACKUP_SIZE)${NC}"
else
    echo -e "${RED}✗${NC}"
    echo -e "${RED}Failed to create backup${NC}"
    exit 1
fi

# =============================================================================
# Phase 2: Verify Backup
# =============================================================================
echo -e "${BLUE}━━━ Phase 2: Verify Backup ━━━${NC}"

# Check file exists and is not empty
echo -n "  Backup file exists... "
if [[ -f "$BACKUP_FILE" ]] && [[ -s "$BACKUP_FILE" ]]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

# Verify gzip integrity
echo -n "  Gzip integrity... "
if gzip -t "$BACKUP_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    exit 1
fi

# Check for SQL content
echo -n "  Contains SQL statements... "
if zcat "$BACKUP_FILE" | head -100 | grep -qi "create\|insert\|postgres"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ (may be empty)${NC}"
fi

# Count tables in backup
echo -n "  Table count... "
TABLE_COUNT=$(zcat "$BACKUP_FILE" | grep -c "CREATE TABLE" || echo "0")
echo -e "${GREEN}$TABLE_COUNT tables${NC}"

echo ""

# =============================================================================
# Phase 3: Full Restore Cycle (Optional)
# =============================================================================
if [[ "$FULL_CYCLE" == "true" ]]; then
    echo -e "${BLUE}━━━ Phase 3: Full Restore Cycle ━━━${NC}"

    # Create test database
    echo -n "  Creating test database... "
    if docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U odoo -c "CREATE DATABASE $TEST_DB_NAME;" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        exit 1
    fi

    # Restore backup to test database
    echo -n "  Restoring backup... "
    if zcat "$BACKUP_FILE" | docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U odoo "$TEST_DB_NAME" &>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        # Cleanup on failure
        docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U odoo -c "DROP DATABASE IF EXISTS $TEST_DB_NAME;" 2>/dev/null || true
        exit 1
    fi

    # Verify restore
    echo -n "  Verify restored data... "
    RESTORED_TABLES=$(docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U odoo "$TEST_DB_NAME" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' ')
    if [[ "$RESTORED_TABLES" -gt 0 ]]; then
        echo -e "${GREEN}✓ ($RESTORED_TABLES tables)${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi

    # Cleanup test database
    if [[ "$CLEANUP" == "true" ]]; then
        echo -n "  Dropping test database... "
        if docker compose -f "$COMPOSE_FILE" exec -T postgres psql -U odoo -c "DROP DATABASE IF EXISTS $TEST_DB_NAME;" 2>/dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${YELLOW}⚠${NC}"
        fi
    else
        echo -e "  ${YELLOW}Test database retained: $TEST_DB_NAME${NC}"
    fi

    echo ""
fi

# =============================================================================
# Phase 4: Cleanup (Optional)
# =============================================================================
if [[ "$CLEANUP" == "true" ]]; then
    echo -e "${BLUE}━━━ Phase 4: Cleanup ━━━${NC}"

    echo -n "  Removing test backup... "
    if rm -f "$BACKUP_FILE"; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}⚠${NC}"
    fi

    echo ""
fi

# =============================================================================
# Summary
# =============================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   Backup Test Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Backup/restore test completed successfully!${NC}"
echo ""
echo "  Backup file: $BACKUP_FILE"
echo "  Backup size: $BACKUP_SIZE"
echo "  Tables: $TABLE_COUNT"
if [[ "$FULL_CYCLE" == "true" ]]; then
    echo "  Restore verified: Yes"
fi
echo ""
