-- Gold Layer: Finance & BIR Compliance Views
-- AI/BI Dashboard source for month-end close and regulatory reporting
-- Depends on: silver.account_move, silver.account_move_line, silver.account_account,
--             silver.hr_expense, silver.res_partner, silver.account_tax
-- Pipeline: Odoo PG → Supabase ETL (CDC) → Iceberg → ADLS Bronze → DLT Silver → Gold

-- =============================================================================
-- 1. Monthly Close Summary
-- =============================================================================
CREATE OR REPLACE VIEW ${catalog}.gold.monthly_close_summary AS
SELECT
    DATE_TRUNC('month', am.date) AS fiscal_period,
    YEAR(am.date) AS fiscal_year,
    MONTH(am.date) AS fiscal_month,
    am.company_id,

    -- Revenue (income accounts have negative balance in Odoo)
    SUM(CASE WHEN aa.internal_group = 'income' THEN -aml.balance ELSE 0 END) AS total_revenue,

    -- Expenses
    SUM(CASE WHEN aa.internal_group = 'expense' THEN aml.balance ELSE 0 END) AS total_expenses,

    -- Net Income
    SUM(CASE WHEN aa.internal_group = 'income' THEN -aml.balance
             WHEN aa.internal_group = 'expense' THEN -aml.balance
             ELSE 0 END) AS net_income,

    -- Counts
    COUNT(DISTINCT am.id) AS journal_entry_count,
    COUNT(DISTINCT CASE WHEN am.state = 'posted' THEN am.id END) AS posted_count,
    COUNT(DISTINCT CASE WHEN am.state = 'draft' THEN am.id END) AS draft_count,

    -- Close readiness
    CASE
        WHEN COUNT(DISTINCT CASE WHEN am.state = 'draft' THEN am.id END) = 0
        THEN 'READY'
        ELSE 'OPEN'
    END AS close_status,

    CURRENT_TIMESTAMP() AS _etl_loaded_at

FROM ${catalog}.silver.account_move_line aml
JOIN ${catalog}.silver.account_move am ON aml.move_id = am.id
JOIN ${catalog}.silver.account_account aa ON aml.account_id = aa.id
WHERE am.date IS NOT NULL
GROUP BY 1, 2, 3, 4;


-- =============================================================================
-- 2. BIR 1601-C Withholding Tax Summary (Monthly)
-- =============================================================================
CREATE OR REPLACE VIEW ${catalog}.gold.bir_withholding_tax_1601c AS
SELECT
    DATE_TRUNC('month', am.date) AS tax_period,
    YEAR(am.date) AS tax_year,
    MONTH(am.date) AS tax_month,
    at.name AS tax_type,
    at.amount AS tax_rate,

    -- Tax base and amounts
    COUNT(DISTINCT aml.id) AS line_count,
    SUM(aml.tax_base_amount) AS taxable_base,
    SUM(CASE WHEN aml.tax_line_id IS NOT NULL THEN aml.balance ELSE 0 END) AS tax_withheld,

    -- Filing status
    CASE
        WHEN CURRENT_DATE() > LAST_DAY(DATE_TRUNC('month', am.date)) + INTERVAL 10 DAY
             AND SUM(CASE WHEN aml.tax_line_id IS NOT NULL THEN aml.balance ELSE 0 END) > 0
        THEN 'DUE'
        ELSE 'PENDING'
    END AS filing_status,

    CURRENT_TIMESTAMP() AS _etl_loaded_at

FROM ${catalog}.silver.account_move_line aml
JOIN ${catalog}.silver.account_move am ON aml.move_id = am.id
LEFT JOIN ${catalog}.silver.account_tax at ON aml.tax_line_id = at.id
WHERE am.state = 'posted'
  AND am.move_type IN ('in_invoice', 'in_refund')
GROUP BY 1, 2, 3, 4, 5;


-- =============================================================================
-- 3. Aging Receivables (AR Aging Buckets)
-- =============================================================================
CREATE OR REPLACE VIEW ${catalog}.gold.aging_receivables AS
SELECT
    rp.id AS partner_id,
    rp.name AS partner_name,
    rp.vat AS tin_number,
    am.company_id,

    -- Aging buckets
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) <= 0 THEN aml.amount_residual ELSE 0 END) AS current_amount,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) BETWEEN 1 AND 30 THEN aml.amount_residual ELSE 0 END) AS days_1_30,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) BETWEEN 31 AND 60 THEN aml.amount_residual ELSE 0 END) AS days_31_60,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) BETWEEN 61 AND 90 THEN aml.amount_residual ELSE 0 END) AS days_61_90,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) > 90 THEN aml.amount_residual ELSE 0 END) AS days_over_90,

    -- Total outstanding
    SUM(aml.amount_residual) AS total_outstanding,

    -- Concentration risk
    ROUND(100.0 * SUM(aml.amount_residual) /
        NULLIF((SELECT SUM(amount_residual) FROM ${catalog}.silver.account_move_line
                WHERE account_id IN (SELECT id FROM ${catalog}.silver.account_account WHERE account_type = 'asset_receivable')
                  AND amount_residual > 0), 0), 2) AS concentration_pct,

    CURRENT_TIMESTAMP() AS _etl_loaded_at

FROM ${catalog}.silver.account_move_line aml
JOIN ${catalog}.silver.account_move am ON aml.move_id = am.id
JOIN ${catalog}.silver.account_account aa ON aml.account_id = aa.id
JOIN ${catalog}.silver.res_partner rp ON aml.partner_id = rp.id
WHERE aa.account_type = 'asset_receivable'
  AND aml.amount_residual > 0
  AND am.state = 'posted'
GROUP BY 1, 2, 3, 4;


-- =============================================================================
-- 4. Aging Payables (AP Aging Buckets)
-- =============================================================================
CREATE OR REPLACE VIEW ${catalog}.gold.aging_payables AS
SELECT
    rp.id AS partner_id,
    rp.name AS partner_name,
    rp.vat AS tin_number,
    am.company_id,

    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) <= 0 THEN ABS(aml.amount_residual) ELSE 0 END) AS current_amount,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) BETWEEN 1 AND 30 THEN ABS(aml.amount_residual) ELSE 0 END) AS days_1_30,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) BETWEEN 31 AND 60 THEN ABS(aml.amount_residual) ELSE 0 END) AS days_31_60,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) BETWEEN 61 AND 90 THEN ABS(aml.amount_residual) ELSE 0 END) AS days_61_90,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) > 90 THEN ABS(aml.amount_residual) ELSE 0 END) AS days_over_90,

    SUM(ABS(aml.amount_residual)) AS total_outstanding,

    CURRENT_TIMESTAMP() AS _etl_loaded_at

FROM ${catalog}.silver.account_move_line aml
JOIN ${catalog}.silver.account_move am ON aml.move_id = am.id
JOIN ${catalog}.silver.account_account aa ON aml.account_id = aa.id
JOIN ${catalog}.silver.res_partner rp ON aml.partner_id = rp.id
WHERE aa.account_type = 'liability_payable'
  AND aml.amount_residual < 0
  AND am.state = 'posted'
GROUP BY 1, 2, 3, 4;


-- =============================================================================
-- 5. Expense Analytics (HR Expense → BIR Deductibility)
-- =============================================================================
CREATE OR REPLACE VIEW ${catalog}.gold.expense_analytics AS
SELECT
    DATE_TRUNC('month', he.date) AS expense_period,
    he.employee_id,
    he.product_id,
    he.name AS expense_description,

    COUNT(*) AS expense_count,
    SUM(he.total_amount) AS total_amount,
    SUM(he.total_amount_currency) AS total_amount_currency,

    -- Approval status
    SUM(CASE WHEN he.state = 'approved' THEN he.total_amount ELSE 0 END) AS approved_amount,
    SUM(CASE WHEN he.state = 'draft' THEN he.total_amount ELSE 0 END) AS pending_amount,
    SUM(CASE WHEN he.state = 'refused' THEN he.total_amount ELSE 0 END) AS refused_amount,

    -- BIR deductibility flag
    CASE
        WHEN he.total_amount <= 250 THEN 'BELOW_THRESHOLD'
        WHEN he.total_amount > 250 THEN 'REQUIRES_RECEIPT'
    END AS bir_receipt_requirement,

    CURRENT_TIMESTAMP() AS _etl_loaded_at

FROM ${catalog}.silver.hr_expense he
WHERE he.date IS NOT NULL
GROUP BY 1, 2, 3, 4;


-- =============================================================================
-- 6. BIR Compliance Tracker (Cross-Form Status)
-- =============================================================================
CREATE OR REPLACE VIEW ${catalog}.gold.bir_compliance_tracker AS
SELECT
    period.fiscal_period,
    period.fiscal_year,
    period.fiscal_month,

    -- 1601-C status
    wt.tax_withheld AS withholding_tax_total,
    wt.filing_status AS wt_filing_status,

    -- Monthly close status
    period.close_status,
    period.draft_count AS unposted_entries,

    -- Revenue/expense summary
    period.total_revenue,
    period.total_expenses,
    period.net_income,

    -- AR/AP totals (current period invoices)
    COALESCE(ar.total_outstanding, 0) AS ar_outstanding,
    COALESCE(ap.total_outstanding, 0) AS ap_outstanding,

    -- Overall compliance score
    CASE
        WHEN period.close_status = 'READY'
             AND COALESCE(wt.filing_status, 'PENDING') != 'DUE'
             AND period.draft_count = 0
        THEN 'COMPLIANT'
        WHEN period.draft_count > 0
        THEN 'ACTION_REQUIRED'
        ELSE 'REVIEW'
    END AS compliance_status,

    CURRENT_TIMESTAMP() AS _etl_loaded_at

FROM ${catalog}.gold.monthly_close_summary period

LEFT JOIN (
    SELECT tax_period AS fiscal_period,
           SUM(tax_withheld) AS tax_withheld,
           MAX(filing_status) AS filing_status
    FROM ${catalog}.gold.bir_withholding_tax_1601c
    GROUP BY 1
) wt ON period.fiscal_period = wt.fiscal_period

LEFT JOIN (
    SELECT SUM(total_outstanding) AS total_outstanding
    FROM ${catalog}.gold.aging_receivables
) ar ON TRUE

LEFT JOIN (
    SELECT SUM(total_outstanding) AS total_outstanding
    FROM ${catalog}.gold.aging_payables
) ap ON TRUE;


-- =============================================================================
-- 7. Timesheet Utilization (Services → Gold)
-- =============================================================================
CREATE OR REPLACE VIEW ${catalog}.gold.timesheet_utilization AS
SELECT
    DATE_TRUNC('month', aal.date) AS period,
    aal.employee_id,
    pp.name AS project_name,

    SUM(aal.unit_amount) AS logged_hours,
    160.0 AS capacity_hours,
    ROUND(100.0 * SUM(aal.unit_amount) / 160.0, 1) AS utilization_pct,
    SUM(ABS(aal.amount)) AS total_cost,

    CURRENT_TIMESTAMP() AS _etl_loaded_at

FROM ${catalog}.silver.account_analytic_line aal
LEFT JOIN ${catalog}.silver.project_project pp ON aal.project_id = pp.id
WHERE aal.project_id IS NOT NULL
  AND aal.date IS NOT NULL
GROUP BY 1, 2, 3;


-- =============================================================================
-- 8. Project Profitability (Services → Gold)
-- =============================================================================
CREATE OR REPLACE VIEW ${catalog}.gold.project_profitability AS
SELECT
    pp.id AS project_id,
    pp.name AS project_name,
    pp.partner_id,

    SUM(aal.unit_amount) AS total_hours,
    SUM(ABS(aal.amount)) AS total_cost,
    COALESCE(rev.total_revenue, 0) AS total_revenue,
    COALESCE(rev.total_revenue, 0) - SUM(ABS(aal.amount)) AS margin,
    CASE
        WHEN COALESCE(rev.total_revenue, 0) > 0
        THEN ROUND(100.0 * (COALESCE(rev.total_revenue, 0) - SUM(ABS(aal.amount))) / rev.total_revenue, 1)
        ELSE 0
    END AS margin_pct,

    CURRENT_TIMESTAMP() AS _etl_loaded_at

FROM ${catalog}.silver.project_project pp
LEFT JOIN ${catalog}.silver.account_analytic_line aal ON aal.project_id = pp.id
LEFT JOIN (
    SELECT sol.project_id, SUM(sol.price_subtotal) AS total_revenue
    FROM ${catalog}.silver.sale_order_line sol
    WHERE sol.project_id IS NOT NULL
    GROUP BY 1
) rev ON rev.project_id = pp.id
WHERE pp.active = TRUE
GROUP BY 1, 2, 3, rev.total_revenue;
