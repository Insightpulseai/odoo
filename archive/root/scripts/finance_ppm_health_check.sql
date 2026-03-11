-- Finance PPM Health Check
-- Purpose: Verify canonical Finance PPM deployment integrity
-- Expected: 8 / 12 / 144 / 36 / 36 (employees / logframe / BIR / tasks / logframe_links)
--
-- Usage:
--   ssh root@159.223.75.148 "docker exec -i odoo-db-1 psql -U odoo -d odoo" < scripts/finance_ppm_health_check.sql
--

\echo '=== Finance PPM Health Check ==='
\echo ''

\echo '1. Employees with codes:'
SELECT COUNT(*) AS employee_count
FROM res_users
WHERE x_employee_code IS NOT NULL;

\echo ''
\echo '2. Logframe entries:'
SELECT COUNT(*) AS logframe_count
FROM ipai_finance_logframe;

\echo ''
\echo '3. BIR schedule records:'
SELECT COUNT(*) AS bir_count
FROM ipai_finance_bir_schedule;

\echo ''
\echo '4. Active projects (should be 1 - ID 30):'
SELECT
    id,
    name::text AS project_name,
    (SELECT COUNT(*) FROM project_task WHERE project_id = project_project.id) AS task_count
FROM project_project
WHERE active = TRUE
  AND name::text LIKE '%Month-End Closing%'
ORDER BY id;

\echo ''
\echo '5. Closing tasks linked to logframe:'
SELECT COUNT(*) AS linked_task_count
FROM project_task
WHERE finance_logframe_id IS NOT NULL
  AND project_id = 30;

\echo ''
\echo '6. Summary (expected: 8 / 12 / 144 / 36 / 36):'
SELECT
    (SELECT COUNT(*) FROM res_users WHERE x_employee_code IS NOT NULL) AS employees,
    (SELECT COUNT(*) FROM ipai_finance_logframe) AS logframe,
    (SELECT COUNT(*) FROM ipai_finance_bir_schedule) AS bir_records,
    (SELECT COUNT(*) FROM project_task WHERE project_id = 30) AS tasks,
    (SELECT COUNT(*) FROM project_task WHERE finance_logframe_id IS NOT NULL AND project_id = 30) AS logframe_links;

\echo ''
\echo '=== Health Check Complete ==='
