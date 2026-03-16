-- 9001_erp_finance_bir_templates.sql
-- Family: 9001_erp - Finance ERP seeds
-- Purpose:
--   * Seed sample BIR schedule templates, forms and close tasks.
-- Safety:
--   * For demo / UAT tenants only.

BEGIN;

-- TODO: INSERT SAMPLE BIR CONFIG
--   * finance.bir_schedule_template
--   * finance.finance_compliance_status
--   * finance.monthly_close_tracker
--
-- Example pattern (commented):
-- INSERT INTO finance.bir_schedule_template (id, code, description, frequency)
-- VALUES (gen_random_uuid(), 'BIR_2550M', 'Monthly VAT Return 2550M', 'monthly');

COMMIT;
