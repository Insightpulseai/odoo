-- AI/BI Dashboard: Finance & BIR Compliance
-- Databricks SQL queries for AI/BI Dashboard widgets
-- Dashboard: "Month-End Close & BIR Compliance"
-- Genie: Enable conversational analytics on these queries
--
-- To create in Databricks:
--   1. Workspace → SQL Editor → paste each query
--   2. New → Dashboard → AI/BI Dashboard
--   3. Add widgets from saved queries
--   4. Enable Genie for conversational analytics

-- =============================================================================
-- Widget 1: Monthly Close Status (KPI Card)
-- =============================================================================
-- name: Monthly Close Status
-- type: counter
-- description: Current month close readiness
SELECT
    close_status,
    draft_count AS unposted_entries,
    posted_count,
    total_revenue,
    total_expenses,
    net_income
FROM ipai_gold.gold.monthly_close_summary
WHERE fiscal_period = DATE_TRUNC('month', CURRENT_DATE())
LIMIT 1;


-- =============================================================================
-- Widget 2: Revenue vs Expenses Trend (Line Chart)
-- =============================================================================
-- name: Revenue vs Expenses (12 Months)
-- type: line
-- x_axis: fiscal_period
-- y_axis: [total_revenue, total_expenses, net_income]
SELECT
    fiscal_period,
    total_revenue,
    total_expenses,
    net_income
FROM ipai_gold.gold.monthly_close_summary
WHERE fiscal_period >= ADD_MONTHS(DATE_TRUNC('month', CURRENT_DATE()), -12)
ORDER BY fiscal_period;


-- =============================================================================
-- Widget 3: BIR Compliance Status (Table)
-- =============================================================================
-- name: BIR Compliance Tracker
-- type: table
-- conditional_formatting: compliance_status (COMPLIANT=green, ACTION_REQUIRED=red, REVIEW=yellow)
SELECT
    fiscal_period,
    total_revenue,
    total_expenses,
    net_income,
    withholding_tax_total,
    wt_filing_status,
    unposted_entries,
    ar_outstanding,
    ap_outstanding,
    compliance_status
FROM ipai_gold.gold.bir_compliance_tracker
WHERE fiscal_year = YEAR(CURRENT_DATE())
ORDER BY fiscal_period DESC;


-- =============================================================================
-- Widget 4: Withholding Tax Summary (Bar Chart)
-- =============================================================================
-- name: 1601-C Withholding Tax by Month
-- type: bar
-- x_axis: tax_period
-- y_axis: tax_withheld
-- color: filing_status
SELECT
    tax_period,
    tax_type,
    tax_rate,
    taxable_base,
    tax_withheld,
    filing_status
FROM ipai_gold.gold.bir_withholding_tax_1601c
WHERE tax_year = YEAR(CURRENT_DATE())
ORDER BY tax_period;


-- =============================================================================
-- Widget 5: AR Aging Waterfall (Stacked Bar)
-- =============================================================================
-- name: Accounts Receivable Aging
-- type: stacked_bar
-- x_axis: partner_name
-- y_axis: [current_amount, days_1_30, days_31_60, days_61_90, days_over_90]
SELECT
    partner_name,
    tin_number,
    current_amount,
    days_1_30,
    days_31_60,
    days_61_90,
    days_over_90,
    total_outstanding,
    concentration_pct
FROM ipai_gold.gold.aging_receivables
ORDER BY total_outstanding DESC
LIMIT 20;


-- =============================================================================
-- Widget 6: AP Aging (Table)
-- =============================================================================
-- name: Accounts Payable Aging
-- type: table
SELECT
    partner_name,
    tin_number,
    current_amount,
    days_1_30,
    days_31_60,
    days_61_90,
    days_over_90,
    total_outstanding
FROM ipai_gold.gold.aging_payables
ORDER BY total_outstanding DESC
LIMIT 20;


-- =============================================================================
-- Widget 7: Expense by Category (Pie Chart)
-- =============================================================================
-- name: Expense Distribution
-- type: pie
-- label: expense_description
-- value: total_amount
SELECT
    expense_description,
    SUM(total_amount) AS total_amount,
    SUM(expense_count) AS expense_count,
    bir_receipt_requirement
FROM ipai_gold.gold.expense_analytics
WHERE expense_period >= ADD_MONTHS(DATE_TRUNC('month', CURRENT_DATE()), -3)
GROUP BY 1, 4
ORDER BY total_amount DESC
LIMIT 15;


-- =============================================================================
-- Widget 8: Timesheet Utilization (Heatmap)
-- =============================================================================
-- name: Team Utilization
-- type: heatmap
-- x_axis: period
-- y_axis: employee_id
-- value: utilization_pct
SELECT
    period,
    employee_id,
    project_name,
    logged_hours,
    capacity_hours,
    utilization_pct,
    total_cost
FROM ipai_gold.gold.timesheet_utilization
WHERE period >= ADD_MONTHS(DATE_TRUNC('month', CURRENT_DATE()), -6)
ORDER BY period DESC, utilization_pct DESC;


-- =============================================================================
-- Widget 9: Project Profitability (Scatter)
-- =============================================================================
-- name: Project Margin Analysis
-- type: scatter
-- x_axis: total_hours
-- y_axis: margin_pct
-- size: total_revenue
SELECT
    project_name,
    total_hours,
    total_cost,
    total_revenue,
    margin,
    margin_pct
FROM ipai_gold.gold.project_profitability
WHERE total_hours > 0
ORDER BY margin_pct DESC;


-- =============================================================================
-- Widget 10: Close Readiness Checklist (Counter/Detail)
-- =============================================================================
-- name: Close Readiness
-- type: detail
SELECT
    'Unposted Journal Entries' AS check_item,
    CAST(draft_count AS STRING) AS value,
    CASE WHEN draft_count = 0 THEN 'PASS' ELSE 'FAIL' END AS status
FROM ipai_gold.gold.monthly_close_summary
WHERE fiscal_period = DATE_TRUNC('month', CURRENT_DATE())
UNION ALL
SELECT
    'Withholding Tax Filed' AS check_item,
    COALESCE(wt_filing_status, 'N/A') AS value,
    CASE WHEN COALESCE(wt_filing_status, 'PENDING') != 'DUE' THEN 'PASS' ELSE 'FAIL' END AS status
FROM ipai_gold.gold.bir_compliance_tracker
WHERE fiscal_period = DATE_TRUNC('month', CURRENT_DATE())
UNION ALL
SELECT
    'AR Over 90 Days' AS check_item,
    CAST(COALESCE(SUM(days_over_90), 0) AS STRING) AS value,
    CASE WHEN COALESCE(SUM(days_over_90), 0) < 100000 THEN 'PASS' ELSE 'WARN' END AS status
FROM ipai_gold.gold.aging_receivables;
