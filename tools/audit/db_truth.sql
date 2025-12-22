-- Database Truth Check Queries
-- Run these against the production database to verify actual state.
--
-- Usage: psql -d $PGDATABASE -f tools/audit/db_truth.sql > db_truth.txt
--
-- Every audit must include this output as evidence.

\echo '=== DATABASE TRUTH CHECK ==='
\echo ''

-- Basic database info
\echo '=== DATABASE INFO ==='
SELECT current_database() as database_name,
       current_user as connected_user,
       version() as postgres_version;

\echo ''
\echo '=== INSTALLED MODULES ==='
-- Show all installed/pending modules
SELECT name,
       state,
       latest_version,
       author,
       CASE WHEN name LIKE 'ipai_%' THEN 'custom'
            WHEN name LIKE 'tbwa_%' THEN 'custom'
            ELSE 'standard' END as module_type
FROM ir_module_module
WHERE state IN ('installed', 'to upgrade', 'to remove', 'to install')
ORDER BY state, module_type DESC, name;

\echo ''
\echo '=== MODULE COUNTS BY STATE ==='
SELECT state, COUNT(*) as count
FROM ir_module_module
GROUP BY state
ORDER BY count DESC;

\echo ''
\echo '=== CUSTOM MODULES (ipai_* / tbwa_*) ==='
SELECT name, state, latest_version, shortdesc
FROM ir_module_module
WHERE name LIKE 'ipai_%' OR name LIKE 'tbwa_%'
ORDER BY name;

\echo ''
\echo '=== PENDING MIGRATIONS ==='
-- Check for modules that need upgrade
SELECT name, state, installed_version, latest_version
FROM ir_module_module
WHERE state = 'to upgrade'
   OR installed_version != latest_version
ORDER BY name;

\echo ''
\echo '=== RECENT MODULE UPDATES ==='
-- Modules updated in last 7 days
SELECT name, state, write_date, latest_version
FROM ir_module_module
WHERE write_date > NOW() - INTERVAL '7 days'
ORDER BY write_date DESC
LIMIT 20;

\echo ''
\echo '=== SYSTEM PARAMETERS ==='
-- Key system configuration
SELECT key, value
FROM ir_config_parameter
WHERE key IN (
    'database.uuid',
    'database.create_date',
    'base.saas_onboarding_survey_frequency',
    'web.base.url',
    'mail.catchall.domain',
    'report.url'
)
ORDER BY key;

\echo ''
\echo '=== SCHEDULED ACTIONS STATUS ==='
-- Cron jobs that might be failing
SELECT name, active, interval_number, interval_type, nextcall, numbercall
FROM ir_cron
WHERE active = true
ORDER BY nextcall
LIMIT 20;

\echo ''
\echo '=== RECENT ERRORS (if ir_logging exists) ==='
-- This table may not exist in all installations
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'ir_logging') THEN
        RAISE NOTICE 'Checking ir_logging table...';
    END IF;
END $$;

-- Try to get recent errors (will fail gracefully if table doesn't exist)
SELECT create_date, name, level, message
FROM ir_logging
WHERE level IN ('ERROR', 'CRITICAL')
ORDER BY create_date DESC
LIMIT 50;

\echo ''
\echo '=== USER COUNTS ==='
SELECT COUNT(*) as total_users,
       SUM(CASE WHEN active THEN 1 ELSE 0 END) as active_users,
       SUM(CASE WHEN share THEN 1 ELSE 0 END) as portal_users
FROM res_users;

\echo ''
\echo '=== COMPANY INFO ==='
SELECT id, name, email
FROM res_company
ORDER BY id;

\echo ''
\echo '=== END DATABASE TRUTH CHECK ==='
