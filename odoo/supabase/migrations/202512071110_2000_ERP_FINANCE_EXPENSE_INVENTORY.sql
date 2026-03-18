-- 202512071110_2000_ERP_FINANCE_EXPENSE_INVENTORY.sql
-- Family: 2000 - ERP domains (Finance, Expense/T&E, Inventory/Assets)
-- Purpose:
--   * Reserve schemas and table stubs for Odoo CE/OCA 18–aligned ERP core.
--   * Map TE-Cheq engine tables into expense schema.
-- Safety:
--   * Additive and idempotent.
--   * No destructive DDL.

BEGIN;

-- Domain schemas --------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS finance;
CREATE SCHEMA IF NOT EXISTS expense;
CREATE SCHEMA IF NOT EXISTS inventory;
CREATE SCHEMA IF NOT EXISTS maintenance;

-- TODO: FINANCE (Odoo account / analytic equivalents)
--   * finance.account
--   * finance.journal_entry           -- Odoo account.move
--   * finance.journal_line            -- Odoo account.move.line
--   * finance.tax_code
--   * finance.tax_mapping             -- BIR tax code / Odoo tax
--   * finance.cost_center             -- analytic accounts
--   * finance.analytic_tag
--   * finance.bir_filing_audit
--   * finance.monthly_close_tracker
--   * finance.bir_schedule_template

-- TODO: EXPENSE / T&E (TE-Cheq engine canonical tables)
--   * expense.expense_reports         -- header
--   * expense.expense_lines           -- lines
--   * expense.cash_advances
--   * expense.policy_rules
--   * expense.policy_violations
--   * expense.erp_mapping             -- link to Odoo hr.expense

-- TODO: INVENTORY / ASSETS
--   * inventory.assets
--   * inventory.asset_categories
--   * inventory.asset_locations
--   * inventory.asset_checkouts

-- TODO: MAINTENANCE (align with Odoo maintenance)
--   * maintenance.plans
--   * maintenance.jobs
--   * maintenance.plan_assets

-- When filling this file:
--   * Keep all CREATE TABLE statements under these schemas.
--   * Add tenant_id, company_id, created_at, updated_at consistently.
--   * Do NOT drop or rename existing production tables without a separate,
--     reviewed migration.

COMMIT;
