-- 202512071130_3000_ENGINE_TE_CHEQ.sql
-- Family: 3000 - Engines (TE-Cheq Travel & Expense)
-- Purpose:
--   * Wire TE-Cheq engine tables and functions into the expense/doc/logs schemas.
--   * Provide RPC stubs for submit / upload / evaluate flows.
-- Safety:
--   * Additive; no drops or destructive alters.

BEGIN;

-- Schemas assumed from 2000 family:
--   * expense
--   * doc
--   * logs

CREATE SCHEMA IF NOT EXISTS doc;
CREATE SCHEMA IF NOT EXISTS logs;

-- TODO: TE-CHEQ TABLE DEFINITIONS
--   * expense.expense_reports
--   * expense.expense_lines
--   * expense.cash_advances
--   * expense.receipt_documents      -- or doc.receipt_documents
--   * expense.policy_rules
--   * expense.policy_violations
--   * logs.teq_engine_events

-- TODO: TE-CHEQ FUNCTIONS / RPC (spec only)
--   * teq_submit_expense_report(...)
--   * teq_upload_receipt(...)
--   * teq_evaluate_report(...)
--
-- Implement as SQL or plpgsql RPCs bound to Supabase Edge Functions later.

COMMIT;
