-- 9001_erp_projects_rates_demo.sql
-- Family: 9001_erp - Projects / Rates demo
-- Purpose:
--   * Seed PPM-style projects, budgets and rate cards for agency/accounting demos.
-- Safety:
--   * Non-production demo data only.

BEGIN;

-- TODO: INSERT DEMO PROJECTS & RATE CARDS
--   * projects.projects
--   * projects.project_budgets
--   * rates.rate_cards
--   * rates.rate_card_items
--   * ppm.engagement
--
-- Example pattern (commented):
-- INSERT INTO projects.projects (id, tenant_id, name, code)
-- VALUES (gen_random_uuid(), <tenant_id>, 'Tindahan 2.0 Campaign', 'PROJ_TIND_2');

COMMIT;
