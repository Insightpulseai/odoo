#!/bin/bash
# Database Cleanup Script - Remove Legacy Databases
# DANGER: This permanently deletes databases. Review carefully before execution.
# Usage: ./scripts/db-cleanup-legacy.sh [--dry-run|--execute]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Database connection details
DB_HOST="odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com"
DB_PORT="25060"
ADMIN_USER="doadmin"
ADMIN_PASSWORD="REDACTED_DO_DB_PASSWORD"

# Legacy databases to remove (SSOT violators)
LEGACY_DBS=(
    "odoo"
    "odoo-prod"
    "odoo19"
    "n8n"
    "plane"
    "superset"
)

# Canonical databases to KEEP (DO NOT DELETE)
CANONICAL_DBS=(
    "defaultdb"
    "postgres"
    "odoo_dev"
    "odoo_stage"
    "_dodb"
    "template0"
    "template1"
)

MODE="${1:---dry-run}"

echo -e "${YELLOW}=== Database Cleanup Script ===${NC}"
echo ""
echo "Target: ${DB_HOST}:${DB_PORT}"
echo "Mode: ${MODE}"
echo ""

if [[ "$MODE" != "--dry-run" && "$MODE" != "--execute" ]]; then
    echo -e "${RED}ERROR: Invalid mode. Use --dry-run or --execute${NC}"
    exit 1
fi

# Function to check active connections
check_connections() {
    local db_name=$1
    ssh root@178.128.112.214 "PGPASSWORD='${ADMIN_PASSWORD}' psql -h ${DB_HOST} -p ${DB_PORT} -U ${ADMIN_USER} -d postgres -t -c \"SELECT COUNT(*) FROM pg_stat_activity WHERE datname='${db_name}' AND pid <> pg_backend_pid();\"" | tr -d ' '
}

# Function to terminate connections
terminate_connections() {
    local db_name=$1
    echo -e "${YELLOW}  Terminating active connections...${NC}"
    ssh root@178.128.112.214 "PGPASSWORD='${ADMIN_PASSWORD}' psql -h ${DB_HOST} -p ${DB_PORT} -U ${ADMIN_USER} -d postgres -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='${db_name}' AND pid <> pg_backend_pid();\""
}

# Function to drop database
drop_database() {
    local db_name=$1
    ssh root@178.128.112.214 "PGPASSWORD='${ADMIN_PASSWORD}' psql -h ${DB_HOST} -p ${DB_PORT} -U ${ADMIN_USER} -d postgres -c \"DROP DATABASE IF EXISTS \\\"${db_name}\\\";\""
}

# List all current databases
echo -e "${GREEN}Current databases on cluster:${NC}"
ssh root@178.128.112.214 "PGPASSWORD='${ADMIN_PASSWORD}' psql -h ${DB_HOST} -p ${DB_PORT} -U ${ADMIN_USER} -d postgres -c '\l'" | grep -E "Name|----|----|odoo|n8n|plane|superset"
echo ""

# Process each legacy database
echo -e "${YELLOW}=== Legacy Databases to Remove ===${NC}"
for db in "${LEGACY_DBS[@]}"; do
    echo ""
    echo -e "${YELLOW}Processing: ${db}${NC}"

    # Check if database exists
    exists=$(ssh root@178.128.112.214 "PGPASSWORD='${ADMIN_PASSWORD}' psql -h ${DB_HOST} -p ${DB_PORT} -U ${ADMIN_USER} -d postgres -t -c \"SELECT 1 FROM pg_database WHERE datname='${db}';\"" | tr -d ' ')

    if [[ -z "$exists" ]]; then
        echo -e "  ${GREEN}✓ Database does not exist (already clean)${NC}"
        continue
    fi

    # Check active connections
    connections=$(check_connections "$db")
    echo -e "  Active connections: ${connections}"

    # Get database size
    size=$(ssh root@178.128.112.214 "PGPASSWORD='${ADMIN_PASSWORD}' psql -h ${DB_HOST} -p ${DB_PORT} -U ${ADMIN_USER} -d postgres -t -c \"SELECT pg_size_pretty(pg_database_size('${db}'));\"" | tr -d ' ')
    echo -e "  Size: ${size}"

    if [[ "$MODE" == "--execute" ]]; then
        echo -e "${RED}  ⚠️  DELETING DATABASE: ${db}${NC}"

        if [[ "$connections" -gt 0 ]]; then
            terminate_connections "$db"
            sleep 2
        fi

        drop_database "$db"
        echo -e "  ${GREEN}✓ Database deleted${NC}"
    else
        echo -e "  ${YELLOW}[DRY RUN] Would delete database: ${db}${NC}"
    fi
done

echo ""
echo -e "${GREEN}=== Canonical Databases (KEEP) ===${NC}"
for db in "${CANONICAL_DBS[@]}"; do
    exists=$(ssh root@178.128.112.214 "PGPASSWORD='${ADMIN_PASSWORD}' psql -h ${DB_HOST} -p ${DB_PORT} -U ${ADMIN_USER} -d postgres -t -c \"SELECT 1 FROM pg_database WHERE datname='${db}';\"" | tr -d ' ')

    if [[ -n "$exists" ]]; then
        echo -e "  ${GREEN}✓ ${db}${NC}"
    else
        echo -e "  ${RED}✗ ${db} (missing - should exist)${NC}"
    fi
done

echo ""
echo -e "${YELLOW}=== Summary ===${NC}"
if [[ "$MODE" == "--execute" ]]; then
    echo -e "${GREEN}Cleanup executed. Cluster now matches canonical state.${NC}"
else
    echo -e "${YELLOW}Dry run complete. Use --execute to perform cleanup.${NC}"
fi

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Verify canonical databases: odoo_dev, odoo_stage"
echo "2. Initialize odoo_dev: python3 odoo-bin -c odoo-tunnel.conf -d odoo_dev -i base --stop-after-init"
echo "3. Create odoo_prod when ready for production"
