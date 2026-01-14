-- ═══════════════════════════════════════════════════════════════════════════════
-- ETL Replication Verification Script
-- ═══════════════════════════════════════════════════════════════════════════════
-- Purpose: Verify Odoo→Supabase logical replication is working
-- Run on: Supabase PostgreSQL (spdtwktxdalcfigzeqrz)
-- Usage: psql "$SUPABASE_URL" -f scripts/verify-etl-replication.sql
-- ═══════════════════════════════════════════════════════════════════════════════

\echo '═══════════════════════════════════════════════════════════════════════════════'
\echo 'ETL Replication Verification'
\echo '═══════════════════════════════════════════════════════════════════════════════'
\echo ''

-- 1) Check base mirror tables are receiving rows
\echo '1. Base Mirror Tables (Row Counts)'
\echo '───────────────────────────────────────────────────────────────────────────────'
SELECT 'account_move' AS table_name, COUNT(*) AS row_count
FROM odoo_mirror.account_move
UNION ALL
SELECT 'account_move_line', COUNT(*)
FROM odoo_mirror.account_move_line
UNION ALL
SELECT 'res_partner', COUNT(*)
FROM odoo_mirror.res_partner
UNION ALL
SELECT 'project_task', COUNT(*)
FROM odoo_mirror.project_task
UNION ALL
SELECT 'hr_expense', COUNT(*)
FROM odoo_mirror.hr_expense
UNION ALL
SELECT 'hr_expense_sheet', COUNT(*)
FROM odoo_mirror.hr_expense_sheet
ORDER BY table_name;

\echo ''
\echo '2. Analytics Views (Populated Check)'
\echo '───────────────────────────────────────────────────────────────────────────────'
SELECT 'v_invoice_summary' AS view_name, COUNT(*) AS row_count
FROM odoo_mirror.v_invoice_summary
UNION ALL
SELECT 'v_expense_summary', COUNT(*)
FROM odoo_mirror.v_expense_summary
UNION ALL
SELECT 'v_task_summary', COUNT(*)
FROM odoo_mirror.v_task_summary
UNION ALL
SELECT 'v_revenue_by_partner', COUNT(*)
FROM odoo_mirror.v_revenue_by_partner
UNION ALL
SELECT 'v_expense_by_employee', COUNT(*)
FROM odoo_mirror.v_expense_by_employee
ORDER BY view_name;

\echo ''
\echo '3. RPC Functions (Smoke Test)'
\echo '───────────────────────────────────────────────────────────────────────────────'
\echo 'Pending Expenses (limit 5):'
SELECT * FROM odoo_mirror.get_pending_expenses(5);

\echo ''
\echo 'Overdue Tasks (limit 5):'
SELECT * FROM odoo_mirror.get_overdue_tasks(5);

\echo ''
\echo 'Revenue Trends (last 3 months):'
SELECT * FROM odoo_mirror.get_revenue_trends(3);

\echo ''
\echo '4. AI Memory Integration (Invoice Signals)'
\echo '───────────────────────────────────────────────────────────────────────────────'
SELECT
    COUNT(*) AS invoice_memory_chunks,
    MAX(created_at) AS last_invoice_signal
FROM ipai_memory.chunks
WHERE topic = 'invoice-created';

\echo ''
\echo '5. Schema Object Verification'
\echo '───────────────────────────────────────────────────────────────────────────────'
\echo 'Tables in odoo_mirror schema:'
SELECT
    schemaname,
    tablename,
    rowsecurity AS rls_enabled
FROM pg_tables
WHERE schemaname = 'odoo_mirror'
ORDER BY tablename;

\echo ''
\echo 'Views in odoo_mirror schema:'
SELECT
    schemaname,
    viewname
FROM pg_views
WHERE schemaname = 'odoo_mirror'
ORDER BY viewname;

\echo ''
\echo 'Functions in odoo_mirror schema:'
SELECT
    routine_schema,
    routine_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'odoo_mirror'
ORDER BY routine_name;

\echo ''
\echo '6. Index Coverage (Performance Check)'
\echo '───────────────────────────────────────────────────────────────────────────────'
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'odoo_mirror'
ORDER BY tablename, indexname;

\echo ''
\echo '7. Role Permissions (Security Check)'
\echo '───────────────────────────────────────────────────────────────────────────────'
SELECT
    grantee,
    privilege_type,
    table_schema,
    table_name
FROM information_schema.table_privileges
WHERE table_schema = 'odoo_mirror'
    AND grantee IN ('superset_readonly', 'n8n_service', 'mcp_agent')
ORDER BY grantee, table_name, privilege_type;

\echo ''
\echo '═══════════════════════════════════════════════════════════════════════════════'
\echo 'Verification Complete'
\echo '═══════════════════════════════════════════════════════════════════════════════'
\echo ''
\echo 'Expected Results:'
\echo '  - All tables should have row_count > 0 (if Odoo has data)'
\echo '  - All views should be populated'
\echo '  - RPC functions should return data without errors'
\echo '  - AI memory chunks should exist if trigger is enabled'
\echo '  - All indexes should be present (15 total)'
\echo '  - superset_readonly should have SELECT on all tables/views'
\echo '  - n8n_service should have EXECUTE on all functions'
\echo ''
