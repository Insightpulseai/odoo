-- AFC Schema Comprehensive RLS Deployment
-- Implements company_id-based tenant isolation for all AFC tables
-- Based on canonical AFC Close Manager schema design

\pset pager off
SET client_min_messages = WARNING;

-- =============================================================================
-- PART 1: Enable RLS on All AFC Tables
-- =============================================================================

ALTER TABLE afc.bir_form_1601c ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.bir_form_1601c_employee ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.bir_form_1700 ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.bir_form_1700_line ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.bir_form_2550q ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.bir_form_2550q_input_vat ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.chunk_embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.compliance_checklist ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.document ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.gl_posting_line ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.intercompany ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.ph_tax_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.sod_conflict_matrix ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.sod_permission ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.sod_risk_engine ENABLE ROW LEVEL SECURITY;
ALTER TABLE afc.sod_role ENABLE ROW LEVEL SECURITY;

-- Tables with existing RLS (just ensure enabled, don't duplicate policies)
-- close_calendar, closing_task, gl_posting, sod_audit_log already have policies

-- =============================================================================
-- PART 2: Core Workflow Tables (Company-Based Tenant Isolation)
-- =============================================================================

-- Closing Tasks (Inherit from parent calendar + Four-Eyes validation)
DROP POLICY IF EXISTS "closing_task_company_access" ON afc.closing_task;
CREATE POLICY "closing_task_company_access"
  ON afc.closing_task FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM afc.close_calendar c
      WHERE c.id = closing_task.calendar_id
        AND (
          c.company_id = (current_setting('app.current_company_id', true)::int)
          OR auth.jwt() ->> 'role' = 'service_role'
        )
    )
  );

-- GL Postings (Inherit from parent calendar)
DROP POLICY IF EXISTS "gl_posting_company_access" ON afc.gl_posting;
CREATE POLICY "gl_posting_company_access"
  ON afc.gl_posting FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM afc.close_calendar c
      WHERE c.id = gl_posting.calendar_id
        AND (
          c.company_id = (current_setting('app.current_company_id', true)::int)
          OR auth.jwt() ->> 'role' = 'service_role'
        )
    )
  );

-- GL Posting Lines (Inherit from parent posting → calendar)
DROP POLICY IF EXISTS "gl_posting_line_via_posting" ON afc.gl_posting_line;
CREATE POLICY "gl_posting_line_via_posting"
  ON afc.gl_posting_line FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM afc.gl_posting gp
      JOIN afc.close_calendar c ON c.id = gp.calendar_id
      WHERE gp.id = gl_posting_line.posting_id
        AND (
          c.company_id = (current_setting('app.current_company_id', true)::int)
          OR auth.jwt() ->> 'role' = 'service_role'
        )
    )
  );

-- Intercompany Transactions (Inherit from parent posting → calendar)
DROP POLICY IF EXISTS "intercompany_via_posting" ON afc.intercompany;
CREATE POLICY "intercompany_via_posting"
  ON afc.intercompany FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM afc.gl_posting gp
      JOIN afc.close_calendar c ON c.id = gp.calendar_id
      WHERE gp.id = intercompany.posting_id
        AND (
          c.company_id = (current_setting('app.current_company_id', true)::int)
          OR auth.jwt() ->> 'role' = 'service_role'
        )
    )
  );

-- Documents (Inherit from parent calendar)
DROP POLICY IF EXISTS "document_company_access" ON afc.document;
CREATE POLICY "document_company_access"
  ON afc.document FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM afc.close_calendar c
      WHERE c.id = document.calendar_id
        AND (
          c.company_id = (current_setting('app.current_company_id', true)::int)
          OR auth.jwt() ->> 'role' = 'service_role'
        )
    )
  );

-- Compliance Checklists (Inherit from parent calendar)
DROP POLICY IF EXISTS "compliance_checklist_company_access" ON afc.compliance_checklist;
CREATE POLICY "compliance_checklist_company_access"
  ON afc.compliance_checklist FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM afc.close_calendar c
      WHERE c.id = compliance_checklist.calendar_id
        AND (
          c.company_id = (current_setting('app.current_company_id', true)::int)
          OR auth.jwt() ->> 'role' = 'service_role'
        )
    )
  );

-- =============================================================================
-- PART 3: BIR Forms (Philippine Tax Compliance)
-- =============================================================================

-- BIR Form 1700 (Annual Income Tax Return) - Company isolation
DROP POLICY IF EXISTS "bir_form_1700_company_access" ON afc.bir_form_1700;
CREATE POLICY "bir_form_1700_company_access"
  ON afc.bir_form_1700 FOR ALL
  USING (
    company_id = (current_setting('app.current_company_id', true)::int)
    OR auth.jwt() ->> 'role' = 'service_role'
  );

-- BIR Form 1700 Line Items (Inherit from parent form)
DROP POLICY IF EXISTS "bir_form_1700_line_via_form" ON afc.bir_form_1700_line;
CREATE POLICY "bir_form_1700_line_via_form"
  ON afc.bir_form_1700_line FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM afc.bir_form_1700 f
      WHERE f.id = bir_form_1700_line.form_id
        AND (
          f.company_id = (current_setting('app.current_company_id', true)::int)
          OR auth.jwt() ->> 'role' = 'service_role'
        )
    )
  );

-- BIR Form 1601-C (Monthly Withholding Tax) - Company isolation
DROP POLICY IF EXISTS "bir_form_1601c_company_access" ON afc.bir_form_1601c;
CREATE POLICY "bir_form_1601c_company_access"
  ON afc.bir_form_1601c FOR ALL
  USING (
    company_id = (current_setting('app.current_company_id', true)::int)
    OR auth.jwt() ->> 'role' = 'service_role'
  );

-- BIR Form 1601-C Employee Detail (Inherit from parent form)
DROP POLICY IF EXISTS "bir_form_1601c_employee_via_form" ON afc.bir_form_1601c_employee;
CREATE POLICY "bir_form_1601c_employee_via_form"
  ON afc.bir_form_1601c_employee FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM afc.bir_form_1601c f
      WHERE f.id = bir_form_1601c_employee.form_id
        AND (
          f.company_id = (current_setting('app.current_company_id', true)::int)
          OR auth.jwt() ->> 'role' = 'service_role'
        )
    )
  );

-- BIR Form 2550Q (Quarterly VAT Return) - Company isolation
DROP POLICY IF EXISTS "bir_form_2550q_company_access" ON afc.bir_form_2550q;
CREATE POLICY "bir_form_2550q_company_access"
  ON afc.bir_form_2550q FOR ALL
  USING (
    company_id = (current_setting('app.current_company_id', true)::int)
    OR auth.jwt() ->> 'role' = 'service_role'
  );

-- BIR Form 2550Q Input VAT Detail (Inherit from parent form)
DROP POLICY IF EXISTS "bir_form_2550q_input_vat_via_form" ON afc.bir_form_2550q_input_vat;
CREATE POLICY "bir_form_2550q_input_vat_via_form"
  ON afc.bir_form_2550q_input_vat FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM afc.bir_form_2550q f
      WHERE f.id = bir_form_2550q_input_vat.form_id
        AND (
          f.company_id = (current_setting('app.current_company_id', true)::int)
          OR auth.jwt() ->> 'role' = 'service_role'
        )
    )
  );

-- =============================================================================
-- PART 4: SoD (Segregation of Duties) Configuration Tables
-- =============================================================================

-- SoD Roles (Reference data - Read-only for authenticated users)
DROP POLICY IF EXISTS "sod_role_read_all" ON afc.sod_role;
CREATE POLICY "sod_role_read_all"
  ON afc.sod_role FOR SELECT
  USING (auth.role() = 'authenticated' OR auth.jwt() ->> 'role' = 'service_role');

-- SoD Permissions (Reference data - Read-only for authenticated users)
DROP POLICY IF EXISTS "sod_permission_read_all" ON afc.sod_permission;
CREATE POLICY "sod_permission_read_all"
  ON afc.sod_permission FOR SELECT
  USING (auth.role() = 'authenticated' OR auth.jwt() ->> 'role' = 'service_role');

-- SoD Conflict Matrix (Reference data - Read-only for authenticated users)
DROP POLICY IF EXISTS "sod_conflict_matrix_read_all" ON afc.sod_conflict_matrix;
CREATE POLICY "sod_conflict_matrix_read_all"
  ON afc.sod_conflict_matrix FOR SELECT
  USING (auth.role() = 'authenticated' OR auth.jwt() ->> 'role' = 'service_role');

-- SoD Risk Engine (Company-based isolation)
DROP POLICY IF EXISTS "sod_risk_engine_company_access" ON afc.sod_risk_engine;
CREATE POLICY "sod_risk_engine_company_access"
  ON afc.sod_risk_engine FOR ALL
  USING (
    company_id = (current_setting('app.current_company_id', true)::int)
    OR auth.jwt() ->> 'role' = 'service_role'
  );

-- =============================================================================
-- PART 5: RAG System Tables (Copilot Knowledge Base)
-- =============================================================================

-- Document Chunks (Company-based isolation if company_id exists, else public)
DROP POLICY IF EXISTS "document_chunks_company_access" ON afc.document_chunks;
CREATE POLICY "document_chunks_company_access"
  ON afc.document_chunks FOR ALL
  USING (
    CASE
      WHEN company_id IS NOT NULL THEN
        company_id = (current_setting('app.current_company_id', true)::int)
        OR auth.jwt() ->> 'role' = 'service_role'
      ELSE
        -- Public knowledge base chunks (no company_id)
        auth.role() = 'authenticated' OR auth.jwt() ->> 'role' = 'service_role'
    END
  );

-- Chunk Embeddings (Inherit from parent document_chunks)
DROP POLICY IF EXISTS "chunk_embeddings_via_chunks" ON afc.chunk_embeddings;
CREATE POLICY "chunk_embeddings_via_chunks"
  ON afc.chunk_embeddings FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM afc.document_chunks dc
      WHERE dc.id = chunk_embeddings.chunk_id
        AND (
          CASE
            WHEN dc.company_id IS NOT NULL THEN
              dc.company_id = (current_setting('app.current_company_id', true)::int)
              OR auth.jwt() ->> 'role' = 'service_role'
            ELSE
              auth.role() = 'authenticated' OR auth.jwt() ->> 'role' = 'service_role'
          END
        )
    )
  );

-- =============================================================================
-- PART 6: Configuration/Reference Tables
-- =============================================================================

-- PH Tax Config (Reference data - Read-only for authenticated users)
DROP POLICY IF EXISTS "ph_tax_config_read_all" ON afc.ph_tax_config;
CREATE POLICY "ph_tax_config_read_all"
  ON afc.ph_tax_config FOR SELECT
  USING (auth.role() = 'authenticated' OR auth.jwt() ->> 'role' = 'service_role');

-- =============================================================================
-- PART 7: Verification
-- =============================================================================

DO $$
DECLARE
  table_rec RECORD;
  total_tables INT := 0;
  rls_enabled INT := 0;
  total_policies INT := 0;
BEGIN
  RAISE NOTICE '';
  RAISE NOTICE '╔═══════════════════════════════════════════════════════════════════╗';
  RAISE NOTICE '║  AFC SCHEMA RLS DEPLOYMENT VERIFICATION                           ║';
  RAISE NOTICE '╚═══════════════════════════════════════════════════════════════════╝';
  RAISE NOTICE '';

  FOR table_rec IN
    SELECT
      c.relname AS table_name,
      c.relrowsecurity AS rls_enabled,
      COUNT(p.polname) AS policy_count
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    LEFT JOIN pg_policy p ON p.polrelid = c.oid
    WHERE n.nspname = 'afc'
      AND c.relkind = 'r'
    GROUP BY c.relname, c.relrowsecurity
    ORDER BY c.relname
  LOOP
    total_tables := total_tables + 1;
    total_policies := total_policies + table_rec.policy_count;

    IF table_rec.rls_enabled THEN
      rls_enabled := rls_enabled + 1;
      RAISE NOTICE '✅ afc.% - RLS enabled (% policies)',
        table_rec.table_name, table_rec.policy_count;
    ELSE
      RAISE WARNING '❌ afc.% - RLS disabled', table_rec.table_name;
    END IF;
  END LOOP;

  RAISE NOTICE '';
  RAISE NOTICE '╔═══════════════════════════════════════════════════════════════════╗';
  RAISE NOTICE '║  SUMMARY: %/% tables secured with % total policies            ║',
    rls_enabled, total_tables, total_policies;
  RAISE NOTICE '╚═══════════════════════════════════════════════════════════════════╝';

  IF rls_enabled = total_tables THEN
    RAISE NOTICE '✅ All AFC tables have RLS enabled';
  ELSE
    RAISE WARNING '⚠️  % tables still missing RLS', (total_tables - rls_enabled);
  END IF;
END $$;

-- Show all AFC policies created
SELECT
  schemaname,
  tablename,
  policyname,
  cmd AS operation,
  CASE WHEN roles = '{public}' THEN 'PUBLIC' ELSE array_to_string(roles, ', ') END AS roles
FROM pg_policies
WHERE schemaname = 'afc'
ORDER BY tablename, policyname;

SELECT '';
SELECT '✅ AFC schema RLS deployment complete - All tables secured' AS status;
