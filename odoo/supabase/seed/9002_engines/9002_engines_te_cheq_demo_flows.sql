-- 9002_engines_te_cheq_demo_flows.sql
-- Family: 9002_engines - TE-Cheq seed
-- Purpose:
--   * Seed example T&E journeys: cash advance, receipts, expense report, approval.
-- Safety:
--   * Demo tenants only.

BEGIN;

-- TODO: INSERT SAMPLE TE-CHEQ DATA
--   * expense.cash_advances
--   * expense.expense_reports
--   * expense.expense_lines
--   * doc.raw_documents / doc.parsed_documents (linked receipts)
--
-- Example pattern (commented):
-- INSERT INTO expense.expense_reports (id, tenant_id, employee_id, name, status)
-- VALUES (gen_random_uuid(), <tenant_id>, <employee_id>, 'Client Pitch Travel', 'submitted');

COMMIT;
