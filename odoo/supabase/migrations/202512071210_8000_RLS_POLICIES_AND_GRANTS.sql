-- 202512071210_8000_RLS_POLICIES_AND_GRANTS.sql
-- Family: 8000 - RBAC / RLS templates & grants
-- Purpose:
--   * Central place for DB roles, GRANTs and RLS policy templates.
-- Safety:
--   * THIS FILE SHOULD INITIALLY CONTAIN TEMPLATES ONLY.
--   * Enable RLS policies explicitly, in a reviewed PR, once patterns are final.

BEGIN;

-- TODO: DEFINE DATABASE ROLES (EXAMPLES)
--   * CREATE ROLE scout_admin;
--   * CREATE ROLE scout_viewer;
--   * CREATE ROLE finance_admin;
--   * CREATE ROLE finance_user;
--   * CREATE ROLE creative_lead;
--   * CREATE ROLE store_owner;
--   * CREATE ROLE brand_sponsor;

-- TODO: GRANTS (TEMPLATE)
--   * GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA scout_fact TO scout_admin;
--   * GRANT SELECT ON ALL TABLES IN SCHEMA scout_gold TO scout_viewer;
--   * ...

-- TODO: RLS POLICY TEMPLATES
--   * Policy pattern using auth.jwt() ->> 'tenant_id'
--   * Policy pattern using core.tenant_membership
--
-- Example template (commented out):
--   -- ALTER TABLE scout_fact.transactions ENABLE ROW LEVEL SECURITY;
--   -- CREATE POLICY tenant_isolation ON scout_fact.transactions
--   --   USING (tenant_id::text = current_setting('app.tenant_id', true));

COMMIT;
