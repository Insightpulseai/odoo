-- 202512071120_2001_ERP_PROJECTS_RATES_PPM.sql
-- Family: 2000 - ERP domains (Projects / PPM / Rates)
-- Purpose:
--   * Define PPM + rate card skeleton aligned to Odoo "Marketing Agency" and
--     "Accounting Firm" industry packs.
-- Safety:
--   * Additive and idempotent only.

BEGIN;

CREATE SCHEMA IF NOT EXISTS projects;
CREATE SCHEMA IF NOT EXISTS rates;
CREATE SCHEMA IF NOT EXISTS ppm;

-- TODO: PROJECTS
--   * projects.projects
--   * projects.project_members
--   * projects.project_budgets
--   * projects.project_budget_lines
--   * projects.tasks

-- TODO: RATES
--   * rates.rate_cards
--   * rates.rate_card_items
--   * rates.client_overrides
--   * rates.rate_inquiries
--   * rates.rate_suggestions
--   * rates.rate_inquiry_feedback

-- TODO: PPM (Accounting-firm style engagements)
--   * ppm.client
--   * ppm.engagement
--   * ppm.work_log
--   * ppm.billing_schedule
--   * ppm.retainer_config
--   * ppm.erp_mapping (Odoo project / invoice / timesheet link)

-- Notes:
--   * All tables must include tenant_id for isolation.
--   * Use UUID PKs by default, with surrogate natural keys where needed.

COMMIT;
