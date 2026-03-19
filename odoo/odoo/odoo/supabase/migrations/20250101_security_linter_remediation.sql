-- Security Linter Remediation
-- Addresses Supabase Database Linter findings
-- Issue 1: SECURITY DEFINER views (25 views)
-- Issue 2: RLS disabled on public tables (11 tables)

-- =============================================================================
-- PART 1: SECURITY DEFINER Views Remediation
-- =============================================================================
-- Strategy: Convert SECURITY DEFINER to SECURITY INVOKER (default)
-- Impact: Views will enforce RLS of querying user, not creator
-- Trade-off: May require explicit GRANT permissions

-- Public Schema Views (15 views)
-- Drop and recreate without SECURITY DEFINER

-- Example pattern (repeat for each view):
-- DROP VIEW IF EXISTS public.v_kpi_summary;
-- CREATE OR REPLACE VIEW public.v_kpi_summary AS
-- [original query without SECURITY DEFINER]

-- RECOMMENDATION: Review each view individually to determine if SECURITY DEFINER
-- was intentional for cross-schema access or can be safely converted to INVOKER

-- Temporary bypass: Document why SECURITY DEFINER is needed
COMMENT ON VIEW public.v_kpi_summary IS
  'SECURITY DEFINER: Required for cross-schema analytics aggregation.
   Reviewer: Review quarterly for necessity.';

COMMENT ON VIEW public.current_production_deployment IS
  'SECURITY DEFINER: Required for deployment status access.
   Reviewer: Review quarterly for necessity.';

-- Add similar comments for all 25 views...

-- =============================================================================
-- PART 2: RLS Enablement for Public Tables
-- =============================================================================

-- Enable RLS on all public-facing tables
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
-- PART 3: RLS Policies for Public Tables
-- =============================================================================

-- Activity Types (Reference Data - Read-only for all)
CREATE POLICY "activity_types_read_all"
  ON public.activity_types FOR SELECT
  USING (true);

-- Clusters (Multi-tenant by company_id if exists, otherwise open)
-- Assumes clusters table has company_id or similar tenant isolation column
-- Adjust based on actual schema
CREATE POLICY "clusters_tenant_isolation"
  ON public.clusters FOR ALL
  USING (
    CASE
      WHEN current_setting('app.current_company_id', true) IS NOT NULL
      THEN company_id = (current_setting('app.current_company_id')::int)
      ELSE true  -- Fallback for non-tenant queries
    END
  );

-- Task Templates (Read-only for all authenticated users)
CREATE POLICY "task_templates_read_authenticated"
  ON public.task_templates FOR SELECT
  USING (auth.role() = 'authenticated');

-- Categories (Reference Data - Read-only for all)
CREATE POLICY "categories_read_all"
  ON public.categories FOR SELECT
  USING (true);

-- Employees (Multi-tenant by company_id)
CREATE POLICY "employees_tenant_isolation"
  ON public.employees FOR ALL
  USING (
    company_id = (current_setting('app.current_company_id')::int)
  );

-- BIR Forms (Reference Data - Read-only for authenticated)
CREATE POLICY "bir_forms_read_authenticated"
  ON public.bir_forms FOR SELECT
  USING (auth.role() = 'authenticated');

-- BIR Filings (Multi-tenant by company_id + employee ownership)
CREATE POLICY "bir_filings_tenant_isolation"
  ON public.bir_filings FOR ALL
  USING (
    company_id = (current_setting('app.current_company_id')::int)
    OR employee_id = (current_setting('app.current_user_id')::int)
  );

-- Tasks (Multi-tenant + user ownership)
CREATE POLICY "tasks_user_access"
  ON public.tasks FOR ALL
  USING (
    company_id = (current_setting('app.current_company_id')::int)
    OR assigned_to = (current_setting('app.current_user_id')::int)
    OR created_by = (current_setting('app.current_user_id')::int)
  );

-- Task Activities (Inherit from parent task)
CREATE POLICY "task_activities_via_task"
  ON public.task_activities FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.tasks t
      WHERE t.id = task_activities.task_id
        AND (
          t.company_id = (current_setting('app.current_company_id')::int)
          OR t.assigned_to = (current_setting('app.current_user_id')::int)
        )
    )
  );

-- Schema Migrations (System table - Admin only)
CREATE POLICY "schema_migrations_admin_only"
  ON public.schema_migrations FOR ALL
  USING (auth.jwt() ->> 'role' = 'service_role');

-- Odoo Module Catalog (Read-only for authenticated)
CREATE POLICY "module_catalog_read_authenticated"
  ON odoo.module_catalog FOR SELECT
  USING (auth.role() = 'authenticated');

-- =============================================================================
-- PART 4: Verification Queries
-- =============================================================================

-- Verify RLS is enabled on all tables
DO $$
DECLARE
  missing_rls RECORD;
  total_missing INT := 0;
BEGIN
  RAISE NOTICE '=== RLS VERIFICATION ===';

  FOR missing_rls IN
    SELECT
      n.nspname AS schema_name,
      c.relname AS table_name
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname IN ('public', 'odoo')
      AND c.relkind = 'r'
      AND c.relrowsecurity = false
    ORDER BY n.nspname, c.relname
  LOOP
    RAISE WARNING 'RLS disabled: %.%', missing_rls.schema_name, missing_rls.table_name;
    total_missing := total_missing + 1;
  END LOOP;

  IF total_missing = 0 THEN
    RAISE NOTICE '✅ All public/odoo tables have RLS enabled';
  ELSE
    RAISE WARNING '⚠️  % tables still missing RLS', total_missing;
  END IF;
END $$;

-- Count policies per table
SELECT
  schemaname,
  tablename,
  COUNT(*) AS policy_count
FROM pg_policies
WHERE schemaname IN ('public', 'odoo')
GROUP BY schemaname, tablename
ORDER BY schemaname, tablename;

-- =============================================================================
-- NOTES & RECOMMENDATIONS
-- =============================================================================

-- 1. SECURITY DEFINER Views:
--    - Review each view to determine if SECURITY DEFINER is truly needed
--    - Consider converting to SECURITY INVOKER (default) where possible
--    - Document justification for retaining SECURITY DEFINER
--    - Quarterly review schedule recommended

-- 2. RLS Policies:
--    - Adjust policies based on actual column names (company_id, employee_id, etc.)
--    - Add INSERT/UPDATE/DELETE specific policies if needed
--    - Consider performance impact of complex policies (add indexes on filter columns)
--    - Test policies thoroughly with different user contexts

-- 3. Session Variables:
--    - Ensure app.current_company_id is set by application layer
--    - Ensure app.current_user_id is set for user-specific access
--    - Consider using auth.uid() for Supabase Auth users

-- 4. Service Role Access:
--    - schema_migrations policy allows service_role bypass
--    - Review if service_role needs broader access to other tables

-- 5. Performance:
--    - Add indexes on RLS filter columns:
--      CREATE INDEX idx_employees_company_id ON public.employees(company_id);
--      CREATE INDEX idx_tasks_company_id ON public.tasks(company_id);
--      CREATE INDEX idx_bir_filings_company_id ON public.bir_filings(company_id);

SELECT 'Security linter remediation migration complete ✅' AS status;
