#!/usr/bin/env bash
# =============================================================================
# Apply PostgreSQL IMMUTABLE unaccent wrapper to existing database
# =============================================================================
# Purpose: Fix "functions in index expression must be marked IMMUTABLE" error
#          on databases that already exist (post-initialization).
#
# Usage:
#   ./scripts/db/apply_unaccent_fix.sh [database_name]
#
# Default database: odoo_dev
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

DB_NAME="${1:-odoo_dev}"
SQL_FILE="${REPO_ROOT}/db/sql/apply_unaccent_immutable.sql"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Applying IMMUTABLE unaccent wrapper to database: ${DB_NAME}${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Check if SQL file exists
if [[ ! -f "${SQL_FILE}" ]]; then
    echo -e "${RED}✗ SQL file not found: ${SQL_FILE}${NC}"
    exit 1
fi

# Check if docker-compose is running
if ! docker-compose ps db | grep -q "Up"; then
    echo -e "${RED}✗ Database container is not running${NC}"
    echo -e "${YELLOW}Run: docker-compose up -d db${NC}"
    exit 1
fi

# Apply the SQL script
echo -e "${GREEN}→ Executing SQL script via docker-compose...${NC}"
docker-compose exec -T db psql -U odoo -d "${DB_NAME}" -f /sql/apply_unaccent_immutable.sql

# Verify the fix was applied
echo ""
echo -e "${GREEN}→ Verifying function volatility...${NC}"
docker-compose exec -T db psql -U odoo -d "${DB_NAME}" -c "
SELECT
    p.proname,
    n.nspname,
    pg_get_function_identity_arguments(p.oid) as args,
    CASE p.provolatile
        WHEN 'i' THEN 'IMMUTABLE'
        WHEN 's' THEN 'STABLE'
        WHEN 'v' THEN 'VOLATILE'
    END as volatility
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname = 'public'
  AND p.proname IN ('unaccent', 'unaccent_immutable')
ORDER BY p.proname;
" | grep -E "unaccent|IMMUTABLE"

echo ""
echo -e "${GREEN}✓ IMMUTABLE wrapper applied successfully!${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
