-- 9000_core_tenants_roles_users.sql
-- Family: 9000_core - Core demo seed
-- Purpose:
--   * Seed example companies, tenants, roles and memberships for demos/UAT.
-- Safety:
--   * Intended for non-production or explicitly flagged demo tenants only.

BEGIN;

-- Pattern:
--   1) Insert companies and tenants.
--   2) Insert roles.
--   3) Link auth users to tenants via core.app_user / core.tenant_membership.
--
-- NOTE:
--   * Replace 'DEMO_TENANT' and placeholder emails with real values or
--     parameterized inputs in your deployment scripts.

-- TODO: SAMPLE INSERTS (commented templates)
-- INSERT INTO core.company (id, name)
-- VALUES (gen_random_uuid(), 'TBWA\\SMP Demo Co');
--
-- INSERT INTO core.tenant (id, company_id, name, code)
-- VALUES (gen_random_uuid(), <company_id>, 'Finance Lab', 'FIN_LAB');
--
-- INSERT INTO core.role (id, name, code)
-- VALUES
--   (gen_random_uuid(), 'Finance Admin', 'finance_admin'),
--   (gen_random_uuid(), 'Scout Viewer', 'scout_viewer');
--
-- INSERT INTO core.app_user (id, auth_user_id, email)
-- VALUES (gen_random_uuid(), '<auth_uid>', 'you@example.com');
--
-- INSERT INTO core.tenant_membership (tenant_id, app_user_id, role_id)
-- VALUES (<tenant_id>, <app_user_id>, <role_id>);

COMMIT;
