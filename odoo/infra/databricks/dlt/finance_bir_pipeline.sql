-- =============================================================================
-- Delta Live Tables (DLT) Pipeline: Finance & BIR Compliance
-- Declarative ETL for the Odoo finance data cascade:
--   Bronze (JDBC extract) -> Silver (cleaned) -> Gold (compliance marts)
--
-- Source: Odoo PG → JDBC Extract Job → Parquet on ADLS → DLT Auto Loader
-- Ingestion: notebooks/bronze/jdbc_odoo_extract.py (incremental, watermarked)
-- Deploy via Databricks Asset Bundles (databricks.yml).
-- Workspace: https://adb-7405610347978231.11.azuredatabricks.net
--
-- Note: Supabase ETL CDC was evaluated but is Private Alpha / self-hosted N/A.
--       Using Databricks-native JDBC extract + Auto Loader instead.
-- =============================================================================

-- =============================================================================
-- BRONZE LAYER: Auto Loader ingestion from JDBC extract output
-- Source: abfss://bronze@stipaidev.dfs.core.windows.net/odoo_finance/
-- Fed by: jdbc_odoo_extract.py (scheduled Databricks job, every 15 min)
-- =============================================================================

-- Bronze: Account Moves (Journal Entries)
CREATE OR REFRESH STREAMING TABLE bronze_account_move
COMMENT 'DLT Bronze: Odoo journal entries via JDBC extract'
TBLPROPERTIES ('quality' = 'bronze', 'pipelines.autoOptimize.managed' = 'true')
AS SELECT
    *,
    current_timestamp() AS _dlt_load_timestamp
FROM STREAM read_files(
    '${bronze_path}/account_move/',
    format => 'parquet',
    inferColumnTypes => true
);

-- Bronze: Account Move Lines (Journal Items)
CREATE OR REFRESH STREAMING TABLE bronze_account_move_line
COMMENT 'DLT Bronze: Odoo journal items via JDBC extract'
TBLPROPERTIES ('quality' = 'bronze', 'pipelines.autoOptimize.managed' = 'true')
AS SELECT
    *,
    current_timestamp() AS _dlt_load_timestamp
FROM STREAM read_files(
    '${bronze_path}/account_move_line/',
    format => 'parquet',
    inferColumnTypes => true
);

-- Bronze: Chart of Accounts
CREATE OR REFRESH STREAMING TABLE bronze_account_account
COMMENT 'DLT Bronze: Odoo chart of accounts via JDBC extract'
TBLPROPERTIES ('quality' = 'bronze', 'pipelines.autoOptimize.managed' = 'true')
AS SELECT
    *,
    current_timestamp() AS _dlt_load_timestamp
FROM STREAM read_files(
    '${bronze_path}/account_account/',
    format => 'parquet',
    inferColumnTypes => true
);

-- Bronze: Tax Definitions
CREATE OR REFRESH STREAMING TABLE bronze_account_tax
COMMENT 'DLT Bronze: Odoo tax definitions via JDBC extract'
TBLPROPERTIES ('quality' = 'bronze', 'pipelines.autoOptimize.managed' = 'true')
AS SELECT
    *,
    current_timestamp() AS _dlt_load_timestamp
FROM STREAM read_files(
    '${bronze_path}/account_tax/',
    format => 'parquet',
    inferColumnTypes => true
);

-- Bronze: Partners (Customers/Vendors)
CREATE OR REFRESH STREAMING TABLE bronze_res_partner
COMMENT 'DLT Bronze: Odoo partners (customers, vendors) via JDBC extract'
TBLPROPERTIES ('quality' = 'bronze', 'pipelines.autoOptimize.managed' = 'true')
AS SELECT
    *,
    current_timestamp() AS _dlt_load_timestamp
FROM STREAM read_files(
    '${bronze_path}/res_partner/',
    format => 'parquet',
    inferColumnTypes => true
);

-- Bronze: HR Expenses
CREATE OR REFRESH STREAMING TABLE bronze_hr_expense
COMMENT 'DLT Bronze: Odoo HR expenses via JDBC extract'
TBLPROPERTIES ('quality' = 'bronze', 'pipelines.autoOptimize.managed' = 'true')
AS SELECT
    *,
    current_timestamp() AS _dlt_load_timestamp
FROM STREAM read_files(
    '${bronze_path}/hr_expense/',
    format => 'parquet',
    inferColumnTypes => true
);

-- Bronze: Projects
CREATE OR REFRESH STREAMING TABLE bronze_project_project
COMMENT 'DLT Bronze: Odoo projects via JDBC extract'
TBLPROPERTIES ('quality' = 'bronze', 'pipelines.autoOptimize.managed' = 'true')
AS SELECT
    *,
    current_timestamp() AS _dlt_load_timestamp
FROM STREAM read_files(
    '${bronze_path}/project_project/',
    format => 'parquet',
    inferColumnTypes => true
);

-- Bronze: Sale Order Lines
CREATE OR REFRESH STREAMING TABLE bronze_sale_order_line
COMMENT 'DLT Bronze: Odoo sale order lines via JDBC extract'
TBLPROPERTIES ('quality' = 'bronze', 'pipelines.autoOptimize.managed' = 'true')
AS SELECT
    *,
    current_timestamp() AS _dlt_load_timestamp
FROM STREAM read_files(
    '${bronze_path}/sale_order_line/',
    format => 'parquet',
    inferColumnTypes => true
);

-- Bronze: Analytic Lines (Timesheets)
CREATE OR REFRESH STREAMING TABLE bronze_account_analytic_line
COMMENT 'DLT Bronze: Odoo timesheet/analytic lines via JDBC extract'
TBLPROPERTIES ('quality' = 'bronze', 'pipelines.autoOptimize.managed' = 'true')
AS SELECT
    *,
    current_timestamp() AS _dlt_load_timestamp
FROM STREAM read_files(
    '${bronze_path}/account_analytic_line/',
    format => 'parquet',
    inferColumnTypes => true
);

-- Bronze: HR Employees
CREATE OR REFRESH STREAMING TABLE bronze_hr_employee
COMMENT 'DLT Bronze: Odoo employees via JDBC extract'
TBLPROPERTIES ('quality' = 'bronze', 'pipelines.autoOptimize.managed' = 'true')
AS SELECT
    *,
    current_timestamp() AS _dlt_load_timestamp
FROM STREAM read_files(
    '${bronze_path}/hr_employee/',
    format => 'parquet',
    inferColumnTypes => true
);

-- =============================================================================
-- BRONZE QUALITY EXPECTATIONS
-- =============================================================================

ALTER STREAMING TABLE bronze_account_move
SET TBLPROPERTIES (
    'pipelines.expectations.id_not_null' = 'EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW',
    'pipelines.expectations.date_not_null' = 'EXPECT (date IS NOT NULL) ON VIOLATION DROP ROW'
);

ALTER STREAMING TABLE bronze_account_move_line
SET TBLPROPERTIES (
    'pipelines.expectations.id_not_null' = 'EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW',
    'pipelines.expectations.move_id_not_null' = 'EXPECT (move_id IS NOT NULL) ON VIOLATION DROP ROW'
);

ALTER STREAMING TABLE bronze_res_partner
SET TBLPROPERTIES (
    'pipelines.expectations.id_not_null' = 'EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW'
);


-- =============================================================================
-- SILVER LAYER: Cleaned, typed, deduplicated
-- CDC dedup via ROW_NUMBER on _dlt_load_timestamp (latest wins)
-- =============================================================================

-- Silver: Account Moves
CREATE OR REFRESH MATERIALIZED VIEW silver_account_move
COMMENT 'DLT Silver: Deduplicated journal entries with typed columns'
TBLPROPERTIES ('quality' = 'silver')
AS
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY _dlt_load_timestamp DESC) AS _rn
    FROM LIVE.bronze_account_move
)
SELECT
    CAST(id AS BIGINT) AS id,
    CAST(name AS STRING) AS name,
    CAST(date AS DATE) AS date,
    CAST(state AS STRING) AS state,
    CAST(move_type AS STRING) AS move_type,
    CAST(company_id AS BIGINT) AS company_id,
    CAST(partner_id AS BIGINT) AS partner_id,
    CAST(journal_id AS BIGINT) AS journal_id,
    CAST(amount_total AS DECIMAL(16,2)) AS amount_total,
    CAST(amount_residual AS DECIMAL(16,2)) AS amount_residual,
    CAST(currency_id AS BIGINT) AS currency_id,
    _dlt_load_timestamp,
    current_timestamp() AS _etl_loaded_at
FROM ranked WHERE _rn = 1;

-- Silver: Account Move Lines
CREATE OR REFRESH MATERIALIZED VIEW silver_account_move_line
COMMENT 'DLT Silver: Deduplicated journal items with typed columns'
TBLPROPERTIES ('quality' = 'silver')
AS
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY _dlt_load_timestamp DESC) AS _rn
    FROM LIVE.bronze_account_move_line
)
SELECT
    CAST(id AS BIGINT) AS id,
    CAST(move_id AS BIGINT) AS move_id,
    CAST(account_id AS BIGINT) AS account_id,
    CAST(partner_id AS BIGINT) AS partner_id,
    CAST(name AS STRING) AS name,
    CAST(debit AS DECIMAL(16,2)) AS debit,
    CAST(credit AS DECIMAL(16,2)) AS credit,
    CAST(balance AS DECIMAL(16,2)) AS balance,
    CAST(amount_residual AS DECIMAL(16,2)) AS amount_residual,
    CAST(date_maturity AS DATE) AS date_maturity,
    CAST(tax_line_id AS BIGINT) AS tax_line_id,
    CAST(tax_base_amount AS DECIMAL(16,2)) AS tax_base_amount,
    CAST(product_id AS BIGINT) AS product_id,
    _dlt_load_timestamp,
    current_timestamp() AS _etl_loaded_at
FROM ranked WHERE _rn = 1;

-- Silver: Chart of Accounts
CREATE OR REFRESH MATERIALIZED VIEW silver_account_account
COMMENT 'DLT Silver: Deduplicated chart of accounts'
TBLPROPERTIES ('quality' = 'silver')
AS
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY _dlt_load_timestamp DESC) AS _rn
    FROM LIVE.bronze_account_account
)
SELECT
    CAST(id AS BIGINT) AS id,
    CAST(code AS STRING) AS code,
    CAST(name AS STRING) AS name,
    CAST(account_type AS STRING) AS account_type,
    CAST(internal_group AS STRING) AS internal_group,
    CAST(company_id AS BIGINT) AS company_id,
    _dlt_load_timestamp,
    current_timestamp() AS _etl_loaded_at
FROM ranked WHERE _rn = 1;

-- Silver: Tax Definitions
CREATE OR REFRESH MATERIALIZED VIEW silver_account_tax
COMMENT 'DLT Silver: Deduplicated tax definitions'
TBLPROPERTIES ('quality' = 'silver')
AS
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY _dlt_load_timestamp DESC) AS _rn
    FROM LIVE.bronze_account_tax
)
SELECT
    CAST(id AS BIGINT) AS id,
    CAST(name AS STRING) AS name,
    CAST(amount AS DECIMAL(10,4)) AS amount,
    CAST(type_tax_use AS STRING) AS type_tax_use,
    CAST(company_id AS BIGINT) AS company_id,
    _dlt_load_timestamp,
    current_timestamp() AS _etl_loaded_at
FROM ranked WHERE _rn = 1;

-- Silver: Partners
CREATE OR REFRESH MATERIALIZED VIEW silver_res_partner
COMMENT 'DLT Silver: Deduplicated partners with TIN'
TBLPROPERTIES ('quality' = 'silver')
AS
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY _dlt_load_timestamp DESC) AS _rn
    FROM LIVE.bronze_res_partner
)
SELECT
    CAST(id AS BIGINT) AS id,
    CAST(name AS STRING) AS name,
    CAST(vat AS STRING) AS vat,
    CAST(company_id AS BIGINT) AS company_id,
    CAST(is_company AS BOOLEAN) AS is_company,
    CAST(customer_rank AS INT) AS customer_rank,
    CAST(supplier_rank AS INT) AS supplier_rank,
    _dlt_load_timestamp,
    current_timestamp() AS _etl_loaded_at
FROM ranked WHERE _rn = 1;

-- Silver: HR Expenses
CREATE OR REFRESH MATERIALIZED VIEW silver_hr_expense
COMMENT 'DLT Silver: Deduplicated HR expenses'
TBLPROPERTIES ('quality' = 'silver')
AS
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY _dlt_load_timestamp DESC) AS _rn
    FROM LIVE.bronze_hr_expense
)
SELECT
    CAST(id AS BIGINT) AS id,
    CAST(name AS STRING) AS name,
    CAST(date AS DATE) AS date,
    CAST(employee_id AS BIGINT) AS employee_id,
    CAST(product_id AS BIGINT) AS product_id,
    CAST(total_amount AS DECIMAL(16,2)) AS total_amount,
    CAST(total_amount_currency AS DECIMAL(16,2)) AS total_amount_currency,
    CAST(state AS STRING) AS state,
    _dlt_load_timestamp,
    current_timestamp() AS _etl_loaded_at
FROM ranked WHERE _rn = 1;

-- Silver: Projects
CREATE OR REFRESH MATERIALIZED VIEW silver_project_project
COMMENT 'DLT Silver: Deduplicated projects'
TBLPROPERTIES ('quality' = 'silver')
AS
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY _dlt_load_timestamp DESC) AS _rn
    FROM LIVE.bronze_project_project
)
SELECT
    CAST(id AS BIGINT) AS id,
    CAST(name AS STRING) AS name,
    CAST(partner_id AS BIGINT) AS partner_id,
    CAST(active AS BOOLEAN) AS active,
    CAST(company_id AS BIGINT) AS company_id,
    _dlt_load_timestamp,
    current_timestamp() AS _etl_loaded_at
FROM ranked WHERE _rn = 1;

-- Silver: Sale Order Lines
CREATE OR REFRESH MATERIALIZED VIEW silver_sale_order_line
COMMENT 'DLT Silver: Deduplicated sale order lines'
TBLPROPERTIES ('quality' = 'silver')
AS
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY _dlt_load_timestamp DESC) AS _rn
    FROM LIVE.bronze_sale_order_line
)
SELECT
    CAST(id AS BIGINT) AS id,
    CAST(order_id AS BIGINT) AS order_id,
    CAST(product_id AS BIGINT) AS product_id,
    CAST(project_id AS BIGINT) AS project_id,
    CAST(price_subtotal AS DECIMAL(16,2)) AS price_subtotal,
    CAST(price_total AS DECIMAL(16,2)) AS price_total,
    CAST(product_uom_qty AS DECIMAL(16,4)) AS product_uom_qty,
    _dlt_load_timestamp,
    current_timestamp() AS _etl_loaded_at
FROM ranked WHERE _rn = 1;

-- Silver: Analytic Lines (Timesheets)
CREATE OR REFRESH MATERIALIZED VIEW silver_account_analytic_line
COMMENT 'DLT Silver: Deduplicated timesheet/analytic lines'
TBLPROPERTIES ('quality' = 'silver')
AS
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY _dlt_load_timestamp DESC) AS _rn
    FROM LIVE.bronze_account_analytic_line
)
SELECT
    CAST(id AS BIGINT) AS id,
    CAST(date AS DATE) AS date,
    CAST(employee_id AS BIGINT) AS employee_id,
    CAST(project_id AS BIGINT) AS project_id,
    CAST(unit_amount AS DECIMAL(16,2)) AS unit_amount,
    CAST(amount AS DECIMAL(16,2)) AS amount,
    CAST(company_id AS BIGINT) AS company_id,
    _dlt_load_timestamp,
    current_timestamp() AS _etl_loaded_at
FROM ranked WHERE _rn = 1;

-- Silver: HR Employees
CREATE OR REFRESH MATERIALIZED VIEW silver_hr_employee
COMMENT 'DLT Silver: Deduplicated employees'
TBLPROPERTIES ('quality' = 'silver')
AS
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY _dlt_load_timestamp DESC) AS _rn
    FROM LIVE.bronze_hr_employee
)
SELECT
    CAST(id AS BIGINT) AS id,
    CAST(name AS STRING) AS name,
    CAST(department_id AS BIGINT) AS department_id,
    CAST(job_id AS BIGINT) AS job_id,
    CAST(company_id AS BIGINT) AS company_id,
    CAST(active AS BOOLEAN) AS active,
    _dlt_load_timestamp,
    current_timestamp() AS _etl_loaded_at
FROM ranked WHERE _rn = 1;


-- =============================================================================
-- GOLD LAYER: Business-ready compliance and analytics views
-- =============================================================================

-- Gold 1: Monthly Close Summary
CREATE OR REFRESH MATERIALIZED VIEW monthly_close_summary
COMMENT 'DLT Gold: Revenue, expenses, net income by fiscal period with close readiness'
TBLPROPERTIES ('quality' = 'gold')
AS
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

    current_timestamp() AS _etl_loaded_at

FROM LIVE.silver_account_move_line aml
JOIN LIVE.silver_account_move am ON aml.move_id = am.id
JOIN LIVE.silver_account_account aa ON aml.account_id = aa.id
WHERE am.date IS NOT NULL
GROUP BY 1, 2, 3, 4;


-- Gold 2: BIR 1601-C Withholding Tax Summary
CREATE OR REFRESH MATERIALIZED VIEW bir_withholding_tax_1601c
COMMENT 'DLT Gold: Monthly withholding tax for BIR 1601-C filing'
TBLPROPERTIES ('quality' = 'gold')
AS
SELECT
    DATE_TRUNC('month', am.date) AS tax_period,
    YEAR(am.date) AS tax_year,
    MONTH(am.date) AS tax_month,
    at.name AS tax_type,
    at.amount AS tax_rate,

    COUNT(DISTINCT aml.id) AS line_count,
    SUM(aml.tax_base_amount) AS taxable_base,
    SUM(CASE WHEN aml.tax_line_id IS NOT NULL THEN aml.balance ELSE 0 END) AS tax_withheld,

    CASE
        WHEN CURRENT_DATE() > LAST_DAY(DATE_TRUNC('month', am.date)) + INTERVAL 10 DAY
             AND SUM(CASE WHEN aml.tax_line_id IS NOT NULL THEN aml.balance ELSE 0 END) > 0
        THEN 'DUE'
        ELSE 'PENDING'
    END AS filing_status,

    current_timestamp() AS _etl_loaded_at

FROM LIVE.silver_account_move_line aml
JOIN LIVE.silver_account_move am ON aml.move_id = am.id
LEFT JOIN LIVE.silver_account_tax at ON aml.tax_line_id = at.id
WHERE am.state = 'posted'
  AND am.move_type IN ('in_invoice', 'in_refund')
GROUP BY 1, 2, 3, 4, 5;


-- Gold 3: Aging Receivables (AR Aging Buckets)
CREATE OR REFRESH MATERIALIZED VIEW aging_receivables
COMMENT 'DLT Gold: AR aging buckets with concentration risk'
TBLPROPERTIES ('quality' = 'gold')
AS
SELECT
    rp.id AS partner_id,
    rp.name AS partner_name,
    rp.vat AS tin_number,
    am.company_id,

    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) <= 0 THEN aml.amount_residual ELSE 0 END) AS current_amount,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) BETWEEN 1 AND 30 THEN aml.amount_residual ELSE 0 END) AS days_1_30,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) BETWEEN 31 AND 60 THEN aml.amount_residual ELSE 0 END) AS days_31_60,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) BETWEEN 61 AND 90 THEN aml.amount_residual ELSE 0 END) AS days_61_90,
    SUM(CASE WHEN DATEDIFF(CURRENT_DATE(), aml.date_maturity) > 90 THEN aml.amount_residual ELSE 0 END) AS days_over_90,

    SUM(aml.amount_residual) AS total_outstanding,

    current_timestamp() AS _etl_loaded_at

FROM LIVE.silver_account_move_line aml
JOIN LIVE.silver_account_move am ON aml.move_id = am.id
JOIN LIVE.silver_account_account aa ON aml.account_id = aa.id
JOIN LIVE.silver_res_partner rp ON aml.partner_id = rp.id
WHERE aa.account_type = 'asset_receivable'
  AND aml.amount_residual > 0
  AND am.state = 'posted'
GROUP BY 1, 2, 3, 4;


-- Gold 4: Aging Payables (AP Aging Buckets)
CREATE OR REFRESH MATERIALIZED VIEW aging_payables
COMMENT 'DLT Gold: AP aging buckets by vendor'
TBLPROPERTIES ('quality' = 'gold')
AS
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

    current_timestamp() AS _etl_loaded_at

FROM LIVE.silver_account_move_line aml
JOIN LIVE.silver_account_move am ON aml.move_id = am.id
JOIN LIVE.silver_account_account aa ON aml.account_id = aa.id
JOIN LIVE.silver_res_partner rp ON aml.partner_id = rp.id
WHERE aa.account_type = 'liability_payable'
  AND aml.amount_residual < 0
  AND am.state = 'posted'
GROUP BY 1, 2, 3, 4;


-- Gold 5: Expense Analytics (BIR Deductibility)
CREATE OR REFRESH MATERIALIZED VIEW expense_analytics
COMMENT 'DLT Gold: HR expenses with BIR deductibility classification'
TBLPROPERTIES ('quality' = 'gold')
AS
SELECT
    DATE_TRUNC('month', he.date) AS expense_period,
    he.employee_id,
    he.product_id,
    he.name AS expense_description,

    COUNT(*) AS expense_count,
    SUM(he.total_amount) AS total_amount,
    SUM(he.total_amount_currency) AS total_amount_currency,

    SUM(CASE WHEN he.state = 'approved' THEN he.total_amount ELSE 0 END) AS approved_amount,
    SUM(CASE WHEN he.state = 'draft' THEN he.total_amount ELSE 0 END) AS pending_amount,
    SUM(CASE WHEN he.state = 'refused' THEN he.total_amount ELSE 0 END) AS refused_amount,

    CASE
        WHEN he.total_amount <= 250 THEN 'BELOW_THRESHOLD'
        WHEN he.total_amount > 250 THEN 'REQUIRES_RECEIPT'
    END AS bir_receipt_requirement,

    current_timestamp() AS _etl_loaded_at

FROM LIVE.silver_hr_expense he
WHERE he.date IS NOT NULL
GROUP BY 1, 2, 3, 4;


-- Gold 6: BIR Compliance Tracker
CREATE OR REFRESH MATERIALIZED VIEW bir_compliance_tracker
COMMENT 'DLT Gold: Cross-form BIR compliance status per fiscal period'
TBLPROPERTIES ('quality' = 'gold')
AS
SELECT
    period.fiscal_period,
    period.fiscal_year,
    period.fiscal_month,

    wt.tax_withheld AS withholding_tax_total,
    wt.filing_status AS wt_filing_status,

    period.close_status,
    period.draft_count AS unposted_entries,

    period.total_revenue,
    period.total_expenses,
    period.net_income,

    COALESCE(ar.total_outstanding, 0) AS ar_outstanding,
    COALESCE(ap.total_outstanding, 0) AS ap_outstanding,

    CASE
        WHEN period.close_status = 'READY'
             AND COALESCE(wt.filing_status, 'PENDING') != 'DUE'
             AND period.draft_count = 0
        THEN 'COMPLIANT'
        WHEN period.draft_count > 0
        THEN 'ACTION_REQUIRED'
        ELSE 'REVIEW'
    END AS compliance_status,

    current_timestamp() AS _etl_loaded_at

FROM LIVE.monthly_close_summary period

LEFT JOIN (
    SELECT tax_period AS fiscal_period,
           SUM(tax_withheld) AS tax_withheld,
           MAX(filing_status) AS filing_status
    FROM LIVE.bir_withholding_tax_1601c
    GROUP BY 1
) wt ON period.fiscal_period = wt.fiscal_period

LEFT JOIN (
    SELECT SUM(total_outstanding) AS total_outstanding
    FROM LIVE.aging_receivables
) ar ON TRUE

LEFT JOIN (
    SELECT SUM(total_outstanding) AS total_outstanding
    FROM LIVE.aging_payables
) ap ON TRUE;


-- Gold 7: Timesheet Utilization
CREATE OR REFRESH MATERIALIZED VIEW timesheet_utilization
COMMENT 'DLT Gold: Team utilization % by project and period'
TBLPROPERTIES ('quality' = 'gold')
AS
SELECT
    DATE_TRUNC('month', aal.date) AS period,
    aal.employee_id,
    pp.name AS project_name,

    SUM(aal.unit_amount) AS logged_hours,
    160.0 AS capacity_hours,
    ROUND(100.0 * SUM(aal.unit_amount) / 160.0, 1) AS utilization_pct,
    SUM(ABS(aal.amount)) AS total_cost,

    current_timestamp() AS _etl_loaded_at

FROM LIVE.silver_account_analytic_line aal
LEFT JOIN LIVE.silver_project_project pp ON aal.project_id = pp.id
WHERE aal.project_id IS NOT NULL
  AND aal.date IS NOT NULL
GROUP BY 1, 2, 3;


-- Gold 8: Project Profitability
CREATE OR REFRESH MATERIALIZED VIEW project_profitability
COMMENT 'DLT Gold: Project margin analysis (revenue vs cost)'
TBLPROPERTIES ('quality' = 'gold')
AS
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

    current_timestamp() AS _etl_loaded_at

FROM LIVE.silver_project_project pp
LEFT JOIN LIVE.silver_account_analytic_line aal ON aal.project_id = pp.id
LEFT JOIN (
    SELECT sol.project_id, SUM(sol.price_subtotal) AS total_revenue
    FROM LIVE.silver_sale_order_line sol
    WHERE sol.project_id IS NOT NULL
    GROUP BY 1
) rev ON rev.project_id = pp.id
WHERE pp.active = TRUE
GROUP BY 1, 2, 3, rev.total_revenue;
