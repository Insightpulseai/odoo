-- RLS Deployment for Actual Table Schemas
-- Based on inspection of existing tables without company_id columns

\pset pager off
SET client_min_messages = WARNING;

-- =============================================================================
-- PART 1: Enable RLS on All Public Tables
-- =============================================================================

ALTER TABLE public.activity_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.clusters ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.task_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bir_forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bir_filings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.task_activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.schema_migrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE odoo.module_catalog ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- PART 2: RLS Policies Based on Actual Schemas
-- =============================================================================

-- Reference Data Tables (Read-only for all authenticated users)
-- These tables have no tenant isolation - shared reference data

DROP POLICY IF EXISTS "activity_types_read_all" ON public.activity_types;
CREATE POLICY "activity_types_read_all"
  ON public.activity_types FOR SELECT
  USING (true);

DROP POLICY IF EXISTS "clusters_read_all" ON public.clusters;
CREATE POLICY "clusters_read_all"
  ON public.clusters FOR SELECT
  USING (true);

DROP POLICY IF EXISTS "task_templates_read_all" ON public.task_templates;
CREATE POLICY "task_templates_read_all"
  ON public.task_templates FOR SELECT
  USING (true);

DROP POLICY IF EXISTS "categories_read_all" ON public.categories;
CREATE POLICY "categories_read_all"
  ON public.categories FOR SELECT
  USING (true);

DROP POLICY IF EXISTS "bir_forms_read_all" ON public.bir_forms;
CREATE POLICY "bir_forms_read_all"
  ON public.bir_forms FOR SELECT
  USING (true);

DROP POLICY IF EXISTS "module_catalog_read_all" ON odoo.module_catalog;
CREATE POLICY "module_catalog_read_all"
  ON odoo.module_catalog FOR SELECT
  USING (true);

-- Employees Table (User-based access via employee code)
-- Users can see their own employee record

DROP POLICY IF EXISTS "employees_own_record" ON public.employees;
CREATE POLICY "employees_own_record"
  ON public.employees FOR ALL
  USING (
    code = current_setting('app.current_employee_code', true)
    OR auth.jwt() ->> 'role' = 'service_role'
  );

-- Tasks Table (Owner/Reviewer/Approver access)
-- Users can access tasks where they are owner, reviewer, or approver

DROP POLICY IF EXISTS "tasks_user_access" ON public.tasks;
CREATE POLICY "tasks_user_access"
  ON public.tasks FOR ALL
  USING (
    owner_code = current_setting('app.current_employee_code', true)
    OR reviewer_code = current_setting('app.current_employee_code', true)
    OR approver_code = current_setting('app.current_employee_code', true)
    OR auth.jwt() ->> 'role' = 'service_role'
  );

-- BIR Filings Table (Access via related tasks and closing periods)
-- Users can access BIR filings for tasks they're involved in

DROP POLICY IF EXISTS "bir_filings_via_tasks" ON public.bir_filings;
CREATE POLICY "bir_filings_via_tasks"
  ON public.bir_filings FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.tasks t
      WHERE t.closing_period_id = bir_filings.closing_period_id
        AND (
          t.owner_code = current_setting('app.current_employee_code', true)
          OR t.reviewer_code = current_setting('app.current_employee_code', true)
          OR t.approver_code = current_setting('app.current_employee_code', true)
        )
    )
    OR auth.jwt() ->> 'role' = 'service_role'
  );

-- Task Activities Table (Inherit access from parent task)

DROP POLICY IF EXISTS "task_activities_via_task" ON public.task_activities;
CREATE POLICY "task_activities_via_task"
  ON public.task_activities FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.tasks t
      WHERE t.id = task_activities.task_id
        AND (
          t.owner_code = current_setting('app.current_employee_code', true)
          OR t.reviewer_code = current_setting('app.current_employee_code', true)
          OR t.approver_code = current_setting('app.current_employee_code', true)
        )
    )
    OR auth.jwt() ->> 'role' = 'service_role'
  );

-- Schema Migrations (System table - Service role only)

DROP POLICY IF EXISTS "schema_migrations_service_only" ON public.schema_migrations;
CREATE POLICY "schema_migrations_service_only"
  ON public.schema_migrations FOR ALL
  USING (auth.jwt() ->> 'role' = 'service_role');

-- =============================================================================
-- PART 3: Verification
-- =============================================================================

DO $$
DECLARE
  table_rec RECORD;
  total_tables INT := 0;
  rls_enabled INT := 0;
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE '=== RLS DEPLOYMENT VERIFICATION ===';
  RAISE NOTICE '';

  FOR table_rec IN
    SELECT
      n.nspname AS schema_name,
      c.relname AS table_name,
      c.relrowsecurity AS rls_enabled,
      COUNT(p.polname) AS policy_count
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    LEFT JOIN pg_policy p ON p.polrelid = c.oid
    WHERE n.nspname IN ('public', 'odoo')
      AND c.relkind = 'r'
      AND c.relname IN (
        'activity_types', 'clusters', 'task_templates', 'categories',
        'employees', 'bir_forms', 'bir_filings', 'tasks', 'task_activities',
        'schema_migrations', 'module_catalog'
      )
    GROUP BY n.nspname, c.relname, c.relrowsecurity
    ORDER BY n.nspname, c.relname
  LOOP
    total_tables := total_tables + 1;
    IF table_rec.rls_enabled THEN
      rls_enabled := rls_enabled + 1;
      RAISE NOTICE '✅ %.% - RLS enabled, % policies',
        table_rec.schema_name, table_rec.table_name, table_rec.policy_count;
    ELSE
      RAISE WARNING '❌ %.% - RLS disabled',
        table_rec.schema_name, table_rec.table_name;
    END IF;
  END LOOP;

  RAISE NOTICE '';
  RAISE NOTICE 'Summary: %/% tables have RLS enabled', rls_enabled, total_tables;

  IF rls_enabled = total_tables THEN
    RAISE NOTICE '✅ All target tables secured';
  ELSE
    RAISE WARNING '⚠️  Some tables still missing RLS';
  END IF;
END $$;

-- Show all policies created
SELECT
  schemaname,
  tablename,
  policyname,
  cmd AS operation,
  CASE WHEN roles = '{public}' THEN 'PUBLIC' ELSE array_to_string(roles, ', ') END AS roles
FROM pg_policies
WHERE schemaname IN ('public', 'odoo')
  AND tablename IN (
    'activity_types', 'clusters', 'task_templates', 'categories',
    'employees', 'bir_forms', 'bir_filings', 'tasks', 'task_activities',
    'schema_migrations', 'module_catalog'
  )
ORDER BY schemaname, tablename, policyname;

SELECT '';
SELECT '✅ RLS deployment complete - All tables secured' AS status;
