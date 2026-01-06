-- =============================================================================
-- InsightPulse Finance SSC - Superset Virtual Datasets
-- =============================================================================
-- These SQL views power the Finance dashboards in Apache Superset
-- Connect to Odoo PostgreSQL: postgresql://odoo:***@159.223.75.148:5432/odoo
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. BIR Withholding Tax Summary
-- Dashboard: BIR Compliance
-- Purpose: Track withholding taxes by vendor for BIR reporting
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_bir_withholding_summary AS
SELECT
    am.id AS move_id,
    am.name AS invoice_number,
    am.date AS invoice_date,
    am.invoice_date_due AS due_date,
    rp.name AS vendor_name,
    rp.vat AS vendor_tin,
    rc.name AS company_name,
    at.name AS tax_name,
    at.amount AS tax_rate,
    CASE
        WHEN at.name ILIKE '%EWT%' OR at.name ILIKE '%expanded%' THEN 'EWT'
        WHEN at.name ILIKE '%VAT%' THEN 'VAT'
        WHEN at.name ILIKE '%final%' THEN 'FINAL'
        ELSE 'OTHER'
    END AS tax_type,
    SUM(aml.debit) AS gross_amount,
    SUM(aml.debit * at.amount / 100) AS tax_withheld,
    DATE_TRUNC('month', am.date) AS period,
    DATE_TRUNC('quarter', am.date) AS quarter,
    EXTRACT(YEAR FROM am.date) AS fiscal_year
FROM account_move am
JOIN account_move_line aml ON am.id = aml.move_id
JOIN res_partner rp ON am.partner_id = rp.id
JOIN res_company rc ON am.company_id = rc.id
LEFT JOIN account_tax at ON aml.tax_line_id = at.id
WHERE am.state = 'posted'
  AND am.move_type IN ('in_invoice', 'in_refund')
  AND at.type_tax_use = 'purchase'
GROUP BY
    am.id, am.name, am.date, am.invoice_date_due,
    rp.name, rp.vat, rc.name,
    at.name, at.amount;

-- -----------------------------------------------------------------------------
-- 2. Consolidated Trial Balance
-- Dashboard: Executive Summary, Month-End Operations
-- Purpose: Multi-company trial balance for consolidation
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_consolidated_trial_balance AS
SELECT
    rc.name AS company_name,
    aa.code AS account_code,
    aa.name AS account_name,
    aa.account_type,
    CASE aa.account_type
        WHEN 'asset_receivable' THEN 'Assets'
        WHEN 'asset_cash' THEN 'Assets'
        WHEN 'asset_current' THEN 'Assets'
        WHEN 'asset_non_current' THEN 'Assets'
        WHEN 'asset_prepayments' THEN 'Assets'
        WHEN 'asset_fixed' THEN 'Assets'
        WHEN 'liability_payable' THEN 'Liabilities'
        WHEN 'liability_credit_card' THEN 'Liabilities'
        WHEN 'liability_current' THEN 'Liabilities'
        WHEN 'liability_non_current' THEN 'Liabilities'
        WHEN 'equity' THEN 'Equity'
        WHEN 'equity_unaffected' THEN 'Equity'
        WHEN 'income' THEN 'Income'
        WHEN 'income_other' THEN 'Income'
        WHEN 'expense' THEN 'Expenses'
        WHEN 'expense_depreciation' THEN 'Expenses'
        WHEN 'expense_direct_cost' THEN 'Expenses'
        WHEN 'off_balance' THEN 'Off Balance'
        ELSE 'Other'
    END AS account_category,
    DATE_TRUNC('month', am.date) AS period,
    SUM(aml.debit) AS total_debit,
    SUM(aml.credit) AS total_credit,
    SUM(aml.debit - aml.credit) AS balance,
    COUNT(DISTINCT am.id) AS transaction_count
FROM account_move_line aml
JOIN account_move am ON aml.move_id = am.id
JOIN account_account aa ON aml.account_id = aa.id
JOIN res_company rc ON am.company_id = rc.id
WHERE am.state = 'posted'
GROUP BY
    rc.name, aa.code, aa.name, aa.account_type,
    DATE_TRUNC('month', am.date)
ORDER BY
    rc.name, aa.code, period;

-- -----------------------------------------------------------------------------
-- 3. AP Aging Report
-- Dashboard: Month-End Operations
-- Purpose: Track overdue payables by aging bucket
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_ap_aging AS
SELECT
    rp.name AS vendor_name,
    rp.vat AS vendor_tin,
    rc.name AS company_name,
    am.name AS invoice_number,
    am.ref AS vendor_reference,
    am.date AS invoice_date,
    am.invoice_date_due AS due_date,
    am.amount_total AS invoice_amount,
    am.amount_residual AS amount_due,
    aml.currency_id,
    CURRENT_DATE - am.invoice_date_due AS days_overdue,
    CASE
        WHEN am.invoice_date_due >= CURRENT_DATE THEN 'Current'
        WHEN CURRENT_DATE - am.invoice_date_due BETWEEN 1 AND 30 THEN '1-30 Days'
        WHEN CURRENT_DATE - am.invoice_date_due BETWEEN 31 AND 60 THEN '31-60 Days'
        WHEN CURRENT_DATE - am.invoice_date_due BETWEEN 61 AND 90 THEN '61-90 Days'
        WHEN CURRENT_DATE - am.invoice_date_due > 90 THEN '90+ Days'
    END AS aging_bucket
FROM account_move am
JOIN res_partner rp ON am.partner_id = rp.id
JOIN res_company rc ON am.company_id = rc.id
JOIN account_move_line aml ON am.id = aml.move_id
WHERE am.state = 'posted'
  AND am.move_type = 'in_invoice'
  AND am.payment_state IN ('not_paid', 'partial')
  AND aml.account_type = 'liability_payable'
GROUP BY
    rp.name, rp.vat, rc.name,
    am.name, am.ref, am.date, am.invoice_date_due,
    am.amount_total, am.amount_residual, aml.currency_id;

-- -----------------------------------------------------------------------------
-- 4. AR Aging Report
-- Dashboard: Month-End Operations
-- Purpose: Track overdue receivables by aging bucket
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_ar_aging AS
SELECT
    rp.name AS customer_name,
    rp.vat AS customer_tin,
    rc.name AS company_name,
    am.name AS invoice_number,
    am.date AS invoice_date,
    am.invoice_date_due AS due_date,
    am.amount_total AS invoice_amount,
    am.amount_residual AS amount_due,
    CURRENT_DATE - am.invoice_date_due AS days_overdue,
    CASE
        WHEN am.invoice_date_due >= CURRENT_DATE THEN 'Current'
        WHEN CURRENT_DATE - am.invoice_date_due BETWEEN 1 AND 30 THEN '1-30 Days'
        WHEN CURRENT_DATE - am.invoice_date_due BETWEEN 31 AND 60 THEN '31-60 Days'
        WHEN CURRENT_DATE - am.invoice_date_due BETWEEN 61 AND 90 THEN '61-90 Days'
        WHEN CURRENT_DATE - am.invoice_date_due > 90 THEN '90+ Days'
    END AS aging_bucket
FROM account_move am
JOIN res_partner rp ON am.partner_id = rp.id
JOIN res_company rc ON am.company_id = rc.id
WHERE am.state = 'posted'
  AND am.move_type = 'out_invoice'
  AND am.payment_state IN ('not_paid', 'partial');

-- -----------------------------------------------------------------------------
-- 5. Expense Analytics
-- Dashboard: Expense Analytics
-- Purpose: Track expenses by category, employee, and policy compliance
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_expense_analytics AS
SELECT
    he.id AS expense_id,
    he.name AS expense_description,
    he.date AS expense_date,
    emp.name AS employee_name,
    emp.work_email AS employee_email,
    pp.name AS expense_category,
    he.unit_amount AS amount,
    he.quantity,
    he.total_amount,
    rc.name AS company_name,
    he.state AS expense_state,
    he.payment_mode,
    CASE
        WHEN he.total_amount <= 5000 THEN 'Within Policy'
        WHEN he.total_amount <= 25000 THEN 'Manager Approval'
        WHEN he.total_amount <= 100000 THEN 'Dept Head Approval'
        ELSE 'CFO Approval'
    END AS approval_level,
    CASE
        WHEN he.total_amount > 5000 AND he.state = 'approved' THEN TRUE
        ELSE FALSE
    END AS required_escalation,
    DATE_TRUNC('month', he.date) AS period,
    DATE_TRUNC('week', he.date) AS week
FROM hr_expense he
JOIN hr_employee emp ON he.employee_id = emp.id
JOIN res_company rc ON he.company_id = rc.id
LEFT JOIN product_product pp ON he.product_id = pp.id
WHERE he.state != 'draft';

-- -----------------------------------------------------------------------------
-- 6. Cash Position Summary
-- Dashboard: Executive Summary
-- Purpose: Real-time cash position across bank accounts
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_cash_position AS
SELECT
    rc.name AS company_name,
    aj.name AS bank_account,
    aj.bank_account_id,
    rba.acc_number AS account_number,
    rb.name AS bank_name,
    SUM(aml.balance) AS current_balance,
    MAX(am.date) AS last_transaction_date,
    COUNT(DISTINCT am.id) AS transaction_count_mtd
FROM account_journal aj
JOIN res_company rc ON aj.company_id = rc.id
LEFT JOIN res_partner_bank rba ON aj.bank_account_id = rba.id
LEFT JOIN res_bank rb ON rba.bank_id = rb.id
LEFT JOIN account_move_line aml ON aml.journal_id = aj.id
LEFT JOIN account_move am ON aml.move_id = am.id AND am.state = 'posted'
WHERE aj.type = 'bank'
GROUP BY
    rc.name, aj.name, aj.bank_account_id,
    rba.acc_number, rb.name;

-- -----------------------------------------------------------------------------
-- 7. Month-End Task Progress
-- Dashboard: Month-End Operations
-- Purpose: Track month-end closing task completion (if ipai_tbwa_finance installed)
-- -----------------------------------------------------------------------------
-- Note: This requires the ipai_tbwa_finance module to be installed
-- CREATE OR REPLACE VIEW vw_month_end_progress AS
-- SELECT
--     cp.name AS period_name,
--     cp.date_start,
--     cp.date_end,
--     cp.state AS period_state,
--     ft.name AS task_name,
--     ft.phase,
--     ft.state AS task_state,
--     ft.due_date,
--     ru.login AS assigned_to,
--     CASE
--         WHEN ft.state = 'done' THEN 100
--         WHEN ft.state = 'review' THEN 75
--         WHEN ft.state = 'in_progress' THEN 50
--         ELSE 0
--     END AS completion_pct
-- FROM closing_period cp
-- LEFT JOIN finance_task ft ON cp.id = ft.period_id
-- LEFT JOIN res_users ru ON ft.assigned_user_id = ru.id;

-- -----------------------------------------------------------------------------
-- 8. Intercompany Transactions (if multi-company)
-- Dashboard: Month-End Operations
-- Purpose: Track intercompany balances for elimination
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_intercompany_balances AS
SELECT
    rc_from.name AS from_company,
    rc_to.name AS to_company,
    aa.code AS account_code,
    aa.name AS account_name,
    DATE_TRUNC('month', am.date) AS period,
    SUM(aml.debit) AS total_debit,
    SUM(aml.credit) AS total_credit,
    SUM(aml.debit - aml.credit) AS net_balance
FROM account_move_line aml
JOIN account_move am ON aml.move_id = am.id
JOIN account_account aa ON aml.account_id = aa.id
JOIN res_company rc_from ON am.company_id = rc_from.id
JOIN res_partner rp ON aml.partner_id = rp.id
LEFT JOIN res_company rc_to ON rp.id = rc_to.partner_id
WHERE am.state = 'posted'
  AND aa.code LIKE '1%'  -- Adjust based on your intercompany account prefix
  AND rc_to.id IS NOT NULL
GROUP BY
    rc_from.name, rc_to.name, aa.code, aa.name,
    DATE_TRUNC('month', am.date)
HAVING SUM(aml.debit - aml.credit) != 0;

-- -----------------------------------------------------------------------------
-- 9. Revenue by Period
-- Dashboard: Executive Summary
-- Purpose: Monthly/quarterly revenue trends
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_revenue_summary AS
SELECT
    rc.name AS company_name,
    DATE_TRUNC('month', am.date) AS period,
    DATE_TRUNC('quarter', am.date) AS quarter,
    EXTRACT(YEAR FROM am.date) AS fiscal_year,
    COUNT(DISTINCT am.id) AS invoice_count,
    SUM(am.amount_untaxed) AS gross_revenue,
    SUM(am.amount_tax) AS total_tax,
    SUM(am.amount_total) AS total_revenue,
    AVG(am.amount_total) AS avg_invoice_value
FROM account_move am
JOIN res_company rc ON am.company_id = rc.id
WHERE am.state = 'posted'
  AND am.move_type = 'out_invoice'
GROUP BY
    rc.name,
    DATE_TRUNC('month', am.date),
    DATE_TRUNC('quarter', am.date),
    EXTRACT(YEAR FROM am.date)
ORDER BY period DESC;

-- -----------------------------------------------------------------------------
-- 10. Vendor Payment Summary
-- Dashboard: Month-End Operations
-- Purpose: Track vendor payments and payment terms compliance
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_vendor_payment_summary AS
SELECT
    rp.name AS vendor_name,
    rp.vat AS vendor_tin,
    rc.name AS company_name,
    COUNT(DISTINCT am.id) AS total_invoices,
    SUM(am.amount_total) AS total_invoiced,
    SUM(CASE WHEN am.payment_state = 'paid' THEN am.amount_total ELSE 0 END) AS total_paid,
    SUM(CASE WHEN am.payment_state != 'paid' THEN am.amount_residual ELSE 0 END) AS outstanding_balance,
    AVG(CASE WHEN am.payment_state = 'paid'
        THEN (SELECT MAX(ap.date) FROM account_payment ap WHERE ap.ref = am.name) - am.invoice_date_due
        ELSE NULL END) AS avg_days_to_pay,
    DATE_TRUNC('month', am.date) AS period
FROM account_move am
JOIN res_partner rp ON am.partner_id = rp.id
JOIN res_company rc ON am.company_id = rc.id
WHERE am.state = 'posted'
  AND am.move_type = 'in_invoice'
GROUP BY
    rp.name, rp.vat, rc.name,
    DATE_TRUNC('month', am.date);

-- =============================================================================
-- SUPERSET CONFIGURATION NOTES
-- =============================================================================
--
-- 1. After creating these views, add them as datasets in Superset:
--    - Go to Data → Datasets → + Dataset
--    - Select the Odoo PostgreSQL connection
--    - Select the view (e.g., public.vw_bir_withholding_summary)
--
-- 2. Recommended Chart Types per Dataset:
--    - vw_bir_withholding_summary: Table, Pivot Table, Bar Chart by tax_type
--    - vw_consolidated_trial_balance: Pivot Table, Tree Map
--    - vw_ap_aging / vw_ar_aging: Pie Chart by aging_bucket, Table
--    - vw_expense_analytics: Bar Chart, Table with filters
--    - vw_cash_position: Big Number, Table
--    - vw_revenue_summary: Time Series, Bar Chart
--
-- 3. Row-Level Security (for multi-tenant):
--    - Create RLS filter: company_name IN ({{ current_user_companies() }})
--    - Apply to all Finance dashboards
--
-- =============================================================================
