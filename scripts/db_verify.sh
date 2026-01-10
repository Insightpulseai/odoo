#!/bin/bash
# ============================================================================
# Database Verification Script for Claude Code Web Sandbox
# ============================================================================
# Usage:
#   ./scripts/db_verify.sh                     # Run against Docker PostgreSQL
#   ./scripts/db_verify.sh --sql               # Output SQL only (for copy/paste)
#   ./scripts/db_verify.sh --direct "psql..." # Run with custom psql command
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

MODE="${1:-docker}"

# SQL verification queries
SQL_SCRIPT=$(cat <<'ENDSQL'
-- ============================================================================
-- Database Verification Report
-- ============================================================================

\echo ''
\echo '=============================================='
\echo 'Database Verification Report'
\echo '=============================================='
\echo ''

-- 1. Connection & Database Info
\echo '1. CONNECTION INFO'
\echo '------------------'
SELECT
    current_database() AS database,
    current_user AS "user",
    version() AS pg_version;

\echo ''

-- 2. Schema Overview
\echo '2. SCHEMA OVERVIEW'
\echo '------------------'
SELECT
    schema_name,
    COUNT(*) FILTER (WHERE obj_type = 'table') AS tables,
    COUNT(*) FILTER (WHERE obj_type = 'view') AS views
FROM (
    SELECT schemaname AS schema_name, 'table' AS obj_type FROM pg_tables
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    UNION ALL
    SELECT schemaname, 'view' FROM pg_views
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
) sub
GROUP BY schema_name
ORDER BY schema_name;

\echo ''

-- 3. IPAI Module Tables
\echo '3. IPAI MODULE TABLES (ipai_* pattern)'
\echo '---------------------------------------'
SELECT
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
AND table_name LIKE 'ipai_%'
ORDER BY table_schema, table_name
LIMIT 30;

\echo ''

-- 4. Odoo Core Tables Check
\echo '4. ODOO CORE TABLES (Critical)'
\echo '-------------------------------'
SELECT
    table_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.tables t2
        WHERE t2.table_name = t.table_name AND t2.table_schema = 'public'
    ) THEN 'EXISTS' ELSE 'MISSING' END AS status
FROM (VALUES
    ('res_users'),
    ('res_partner'),
    ('res_company'),
    ('ir_module_module'),
    ('ir_model'),
    ('ir_model_fields'),
    ('ir_ui_view'),
    ('ir_ui_menu'),
    ('ir_attachment'),
    ('ir_cron')
) AS t(table_name);

\echo ''

-- 5. Module Installation Status
\echo '5. IPAI MODULES STATUS (if table exists)'
\echo '-----------------------------------------'
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ir_module_module') THEN
        RAISE NOTICE 'Querying ir_module_module...';
    END IF;
END $$;

SELECT
    name,
    state,
    latest_version
FROM ir_module_module
WHERE name LIKE 'ipai_%'
ORDER BY name
LIMIT 20;

\echo ''

-- 6. Database Size
\echo '6. DATABASE SIZE'
\echo '----------------'
SELECT
    pg_database.datname AS database,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = current_database();

\echo ''

-- 7. Connection Stats
\echo '7. CONNECTION STATS'
\echo '-------------------'
SELECT
    max_conn,
    used,
    max_conn - used AS available,
    ROUND(100.0 * used / max_conn, 1) AS pct_used
FROM (
    SELECT setting::int AS max_conn FROM pg_settings WHERE name = 'max_connections'
) settings,
(SELECT COUNT(*) AS used FROM pg_stat_activity) activity;

\echo ''
\echo '=============================================='
\echo 'Verification Complete'
\echo '=============================================='
ENDSQL
)

# Output modes
case "$MODE" in
    --sql|-s)
        echo "$SQL_SCRIPT"
        exit 0
        ;;
    --direct)
        shift
        echo "$SQL_SCRIPT" | "$@"
        exit $?
        ;;
    docker|--docker)
        echo -e "${BLUE}Running database verification via Docker...${NC}"
        echo ""

        if ! command -v docker &> /dev/null; then
            echo -e "${RED}Error: Docker not available${NC}"
            echo "Use './scripts/db_verify.sh --sql' to get SQL for manual execution"
            exit 1
        fi

        if ! docker compose ps 2>/dev/null | grep -q "postgres\|db"; then
            echo -e "${YELLOW}Warning: PostgreSQL container may not be running${NC}"
            echo "Attempting anyway..."
        fi

        echo "$SQL_SCRIPT" | docker compose exec -T postgres psql -U odoo -d odoo_core 2>/dev/null || \
        echo "$SQL_SCRIPT" | docker compose exec -T db psql -U odoo -d odoo_core 2>/dev/null || \
        {
            echo -e "${RED}Failed to connect to database${NC}"
            echo ""
            echo "Try one of these alternatives:"
            echo "  1. Ensure Docker stack is running: docker compose up -d"
            echo "  2. Get SQL to run manually: ./scripts/db_verify.sh --sql"
            echo "  3. Run with custom psql: ./scripts/db_verify.sh --direct psql -U odoo -d odoo_core"
            exit 1
        }
        ;;
    *)
        echo "Usage: ./scripts/db_verify.sh [--docker|--sql|--direct PSQL_CMD]"
        echo ""
        echo "Options:"
        echo "  --docker, docker  Run against Docker PostgreSQL (default)"
        echo "  --sql, -s         Output SQL only for copy/paste"
        echo "  --direct CMD      Run with custom psql command"
        echo ""
        echo "Examples:"
        echo "  ./scripts/db_verify.sh"
        echo "  ./scripts/db_verify.sh --sql > verify.sql"
        echo "  ./scripts/db_verify.sh --direct 'psql -h localhost -U odoo -d odoo_core'"
        exit 0
        ;;
esac
