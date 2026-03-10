#!/bin/bash
# Promote Development to Staging
# Usage: ./scripts/promote-dev-to-stage.sh [--modules-only|--full-restore]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
DB_HOST="odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com"
DB_PORT="25060"
DB_USER="odoo_app"
DB_PASSWORD="OdooAppDev2026"
BACKUP_DIR="/tmp/odoo-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

MODE="${1:---modules-only}"

echo -e "${YELLOW}=== Dev → Stage Promotion ===${NC}"
echo "Mode: ${MODE}"
echo "Timestamp: ${TIMESTAMP}"
echo ""

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Step 1: Backup current staging (safety)
echo -e "${GREEN}[1/6] Backing up current staging...${NC}"
ssh root@178.128.112.214 "PGPASSWORD='${DB_PASSWORD}' pg_dump \
  -h ${DB_HOST} \
  -p ${DB_PORT} \
  -U ${DB_USER} \
  -d odoo_stage \
  -Fc" > ${BACKUP_DIR}/odoo_stage_before_promotion_${TIMESTAMP}.dump
echo "✓ Staging backup saved: ${BACKUP_DIR}/odoo_stage_before_promotion_${TIMESTAMP}.dump"

# Step 2: Extract module list from dev
echo -e "${GREEN}[2/6] Extracting installed modules from dev...${NC}"
MODULES=$(ssh root@178.128.112.214 "PGPASSWORD='${DB_PASSWORD}' psql \
  -h ${DB_HOST} \
  -p ${DB_PORT} \
  -U ${DB_USER} \
  -d odoo_dev \
  -t \
  -c \"SELECT string_agg(name, ',') FROM ir_module_module WHERE state='installed' AND name NOT IN ('base', 'web');\"" | tr -d ' ')
echo "✓ Modules to install: ${MODULES}"

if [[ "$MODE" == "--full-restore" ]]; then
    # Step 3: Full database restore
    echo -e "${GREEN}[3/6] Creating full dev backup...${NC}"
    ssh root@178.128.112.214 "PGPASSWORD='${DB_PASSWORD}' pg_dump \
      -h ${DB_HOST} \
      -p ${DB_PORT} \
      -U ${DB_USER} \
      -d odoo_dev \
      -Fc" > ${BACKUP_DIR}/odoo_dev_${TIMESTAMP}.dump
    echo "✓ Dev backup created: ${BACKUP_DIR}/odoo_dev_${TIMESTAMP}.dump"

    echo -e "${GREEN}[4/6] Dropping staging database...${NC}"
    ssh root@178.128.112.214 "PGPASSWORD='REDACTED_DO_DB_PASSWORD' psql \
      -h ${DB_HOST} \
      -p ${DB_PORT} \
      -U doadmin \
      -d postgres \
      -c 'SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='\''odoo_stage'\'' AND pid <> pg_backend_pid();' \
      -c 'DROP DATABASE odoo_stage;' \
      -c 'CREATE DATABASE odoo_stage ENCODING '\''UTF8'\'' LC_COLLATE '\''en_US.UTF-8'\'' LC_CTYPE '\''en_US.UTF-8'\'';' \
      -c 'GRANT ALL PRIVILEGES ON DATABASE odoo_stage TO odoo_app;'"
    echo "✓ Staging database recreated"

    echo -e "${GREEN}[5/6] Restoring dev backup to staging...${NC}"
    ssh root@178.128.112.214 "cat > /tmp/dev_backup.dump" < ${BACKUP_DIR}/odoo_dev_${TIMESTAMP}.dump
    ssh root@178.128.112.214 "PGPASSWORD='${DB_PASSWORD}' pg_restore \
      -h ${DB_HOST} \
      -p ${DB_PORT} \
      -U ${DB_USER} \
      -d odoo_stage \
      --no-owner \
      --no-acl \
      /tmp/dev_backup.dump && rm /tmp/dev_backup.dump"
    echo "✓ Database restored to staging"
else
    # Step 3: Module-only sync
    echo -e "${GREEN}[3/6] Installing modules in staging...${NC}"
    echo "This will take several minutes..."
    # TODO: Add Odoo module installation command
    echo "⚠️  Module installation script not implemented yet"
    echo "    Manually install modules: ${MODULES}"
fi

# Step 6: Remove demo data from staging
echo -e "${GREEN}[6/6] Removing demo data from staging...${NC}"
ssh root@178.128.112.214 "PGPASSWORD='${DB_PASSWORD}' psql \
  -h ${DB_HOST} \
  -p ${DB_PORT} \
  -U ${DB_USER} \
  -d odoo_stage \
  << EOF
-- Remove demo data
DELETE FROM ir_demo;

-- Update base URL
UPDATE ir_config_parameter SET value = 'https://stage.insightpulseai.com' WHERE key = 'web.base.url';

-- Set test mode flag
UPDATE ir_config_parameter SET value = 'True' WHERE key = 'test_mode';
EOF
"
echo "✓ Demo data removed and staging configured"

echo ""
echo -e "${GREEN}=== Promotion Complete ===${NC}"
echo "Staging database updated from dev"
echo ""
echo "Next steps:"
echo "1. Run integration tests: ./scripts/run-stage-tests.sh"
echo "2. Perform UAT on staging environment"
echo "3. If validated, promote to production: ./scripts/promote-stage-to-prod.sh"
echo ""
echo "Rollback command (if needed):"
echo "pg_restore -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d odoo_stage -c ${BACKUP_DIR}/odoo_stage_before_promotion_${TIMESTAMP}.dump"
