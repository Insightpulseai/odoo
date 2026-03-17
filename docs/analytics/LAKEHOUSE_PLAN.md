# Lakehouse/Warehouse Plan for Odoo CE

**Version:** 1.0.0
**Generated:** 2026-01-27
**Purpose:** Self-hosted analytics pipeline for Odoo operational data (Databricks-style architecture)

---

## Executive Summary

This plan implements a **Bronze/Silver/Gold** data lake architecture for Odoo CE, enabling:
- Real-time and batch analytics on operational data
- Self-hosted alternative to cloud BI services
- Data governance with lineage tracking
- Integration with external AI/ML pipelines

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Odoo CE Analytics Lakehouse                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │   Odoo CE    │     │  PostgreSQL  │     │   MinIO      │                 │
│  │  (Source)    │────▶│  (OLTP DB)   │────▶│  (S3 Lake)   │                 │
│  └──────────────┘     └──────────────┘     └──────────────┘                 │
│         │                    │                    │                          │
│         │                    │                    │                          │
│         ▼                    ▼                    ▼                          │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │                         Airbyte / Debezium                      │         │
│  │                    (CDC / ELT Extraction)                       │         │
│  └────────────────────────────────────────────────────────────────┘         │
│                              │                                               │
│                              ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                           Bronze Layer                               │    │
│  │  (Raw data, immutable, full history, Parquet/Delta format)          │    │
│  │  s3://odoo-lake/bronze/{source}/{table}/{partition}                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼ (dbt transformations)                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                           Silver Layer                               │    │
│  │  (Cleaned, deduplicated, typed, incremental models)                 │    │
│  │  s3://odoo-lake/silver/{domain}/{model}                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼ (dbt marts)                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                            Gold Layer                                │    │
│  │  (Business aggregates, KPIs, reporting tables)                      │    │
│  │  s3://odoo-lake/gold/{domain}/{mart}                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                              │                                               │
│         ┌────────────────────┼────────────────────┐                         │
│         ▼                    ▼                    ▼                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐                 │
│  │   Superset   │     │    Trino     │     │   Metabase   │                 │
│  │  (Dashboards)│     │  (SQL Query) │     │  (Self-Serve)│                 │
│  └──────────────┘     └──────────────┘     └──────────────┘                 │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │                     DataHub / OpenMetadata                      │         │
│  │              (Catalog, Lineage, Data Governance)                │         │
│  └────────────────────────────────────────────────────────────────┘         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack (Self-Hosted)

### Primary Stack (Recommended)

| Component | Technology | Purpose | Alternative |
|-----------|------------|---------|-------------|
| **Source DB** | PostgreSQL 15+ | Odoo OLTP database | - |
| **CDC/ELT** | Airbyte OSS | Data extraction & sync | Debezium + Kafka |
| **Object Storage** | MinIO | S3-compatible lake storage | Local FS, Ceph |
| **File Format** | Parquet + Delta Lake | Columnar storage with ACID | Apache Iceberg |
| **Transformation** | dbt-core | SQL-based transformations | Apache Spark |
| **Query Engine** | Trino | Federated SQL queries | DuckDB, ClickHouse |
| **Visualization** | Apache Superset | Dashboards & exploration | Metabase, Redash |
| **Catalog** | DataHub OSS | Metadata & lineage | OpenMetadata |
| **Orchestration** | Dagster | Pipeline scheduling | Airflow, Prefect |

### Lightweight Stack (Minimal Resources)

For smaller deployments:

| Component | Technology |
|-----------|------------|
| **CDC** | pg_dump incremental |
| **Storage** | Local filesystem |
| **Transform** | dbt-duckdb |
| **Query** | DuckDB |
| **Viz** | Metabase |

---

## Data Model Domains

### Bronze Layer (Raw Ingestion)

Source tables from Odoo PostgreSQL:

```
bronze/
├── odoo/
│   ├── res_partner/           # Partners (customers, vendors)
│   ├── res_users/             # Users
│   ├── res_company/           # Companies
│   ├── sale_order/            # Sales orders
│   ├── sale_order_line/       # SO lines
│   ├── purchase_order/        # Purchase orders
│   ├── purchase_order_line/   # PO lines
│   ├── account_move/          # Journal entries (invoices)
│   ├── account_move_line/     # Journal entry lines
│   ├── account_payment/       # Payments
│   ├── stock_picking/         # Inventory transfers
│   ├── stock_move/            # Stock movements
│   ├── stock_quant/           # Inventory quantities
│   ├── project_project/       # Projects
│   ├── project_task/          # Tasks
│   ├── hr_employee/           # Employees
│   ├── hr_timesheet/          # Timesheets
│   └── mis_report_instance/   # MIS reports
```

### Silver Layer (Cleaned & Conformed)

```
silver/
├── finance/
│   ├── dim_account/           # Account dimension
│   ├── dim_journal/           # Journal dimension
│   ├── dim_period/            # Period dimension
│   ├── fact_journal_entry/    # Journal entries (cleaned)
│   ├── fact_payment/          # Payments (cleaned)
│   └── fact_bank_statement/   # Bank statements
├── sales/
│   ├── dim_product/           # Product dimension
│   ├── dim_customer/          # Customer dimension
│   ├── fact_sales_order/      # Sales orders (cleaned)
│   └── fact_invoice/          # Invoices (cleaned)
├── procurement/
│   ├── dim_vendor/            # Vendor dimension
│   ├── fact_purchase_order/   # Purchase orders (cleaned)
│   └── fact_receipt/          # Receipts
├── inventory/
│   ├── dim_location/          # Location dimension
│   ├── fact_stock_move/       # Stock movements
│   └── snapshot_inventory/    # Daily inventory snapshots
├── project/
│   ├── dim_project/           # Project dimension
│   ├── fact_task/             # Tasks (cleaned)
│   └── fact_timesheet/        # Timesheets (cleaned)
└── hr/
    ├── dim_employee/          # Employee dimension
    └── dim_department/        # Department dimension
```

### Gold Layer (Business Marts)

```
gold/
├── finance_mart/
│   ├── daily_cash_position/      # Cash balances by day
│   ├── monthly_pnl/              # P&L by month
│   ├── ar_aging/                 # Accounts receivable aging
│   ├── ap_aging/                 # Accounts payable aging
│   ├── budget_vs_actual/         # Budget variance
│   └── kpi_finance_summary/      # Finance KPIs
├── sales_mart/
│   ├── daily_sales/              # Daily sales summary
│   ├── sales_by_customer/        # Customer sales analysis
│   ├── sales_by_product/         # Product sales analysis
│   ├── sales_pipeline/           # Pipeline stages
│   └── kpi_sales_summary/        # Sales KPIs
├── operations_mart/
│   ├── inventory_turns/          # Inventory turnover
│   ├── stock_alerts/             # Low stock alerts
│   ├── fulfillment_metrics/      # Order fulfillment
│   └── kpi_operations_summary/   # Operations KPIs
└── executive_mart/
    ├── company_scorecard/        # Executive dashboard
    └── trend_analysis/           # YoY/MoM trends
```

---

## dbt Project Structure

```
dbt/
├── dbt_project.yml
├── profiles.yml.example
├── packages.yml
├── models/
│   ├── staging/              # Bronze → staging
│   │   ├── stg_odoo__partners.sql
│   │   ├── stg_odoo__sales_orders.sql
│   │   └── ...
│   ├── intermediate/         # Staging → silver
│   │   ├── int_finance__journal_entries.sql
│   │   ├── int_sales__orders_enriched.sql
│   │   └── ...
│   └── marts/                # Silver → gold
│       ├── finance/
│       │   ├── daily_cash_position.sql
│       │   └── monthly_pnl.sql
│       ├── sales/
│       │   ├── daily_sales.sql
│       │   └── customer_lifetime_value.sql
│       └── executive/
│           └── company_scorecard.sql
├── macros/
│   ├── odoo_helpers.sql
│   └── date_spine.sql
├── seeds/
│   ├── account_types.csv
│   └── fiscal_periods.csv
├── snapshots/
│   └── inventory_snapshot.sql
└── tests/
    └── schema_tests.yml
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)

1. **Deploy MinIO**
   - S3-compatible storage
   - Create buckets: `odoo-lake-bronze`, `odoo-lake-silver`, `odoo-lake-gold`

2. **Deploy Airbyte**
   - Configure PostgreSQL source (Odoo DB)
   - Configure MinIO destination
   - Set up initial sync for core tables

3. **Initialize dbt project**
   - Create project structure
   - Add staging models for core entities

```bash
# Deploy foundation
docker compose -f docker/analytics/docker-compose.yml up -d minio airbyte
```

### Phase 2: Core Transforms (Week 3-4)

1. **Build Silver Layer**
   - Implement staging models
   - Add intermediate transformations
   - Configure incremental loads

2. **Deploy Trino**
   - Configure MinIO catalog
   - Test SQL queries on Parquet files

```bash
# Run dbt models
cd dbt && dbt run --select staging intermediate
```

### Phase 3: Business Marts (Week 5-6)

1. **Build Gold Layer**
   - Implement finance marts
   - Implement sales marts
   - Add KPI calculations

2. **Deploy Superset**
   - Configure Trino connection
   - Create core dashboards

```bash
# Run all models
cd dbt && dbt run
# Validate
cd dbt && dbt test
```

### Phase 4: Governance (Week 7-8)

1. **Deploy DataHub**
   - Configure dbt lineage ingestion
   - Configure PostgreSQL metadata ingestion

2. **Set up Dagster**
   - Schedule dbt runs
   - Add data quality sensors

---

## SQL Examples

### Staging Model (Bronze → Staging)

```sql
-- models/staging/stg_odoo__account_move.sql
{{ config(materialized='incremental', unique_key='id') }}

with source as (
    select * from {{ source('bronze_odoo', 'account_move') }}
    {% if is_incremental() %}
    where _airbyte_extracted_at > (select max(_airbyte_extracted_at) from {{ this }})
    {% endif %}
),

renamed as (
    select
        id,
        name as move_name,
        ref as reference,
        date as move_date,
        state,
        move_type,
        journal_id,
        company_id,
        partner_id,
        amount_total,
        amount_untaxed,
        amount_tax,
        currency_id,
        create_date,
        write_date,
        _airbyte_extracted_at as extracted_at
    from source
)

select * from renamed
```

### Intermediate Model (Staging → Silver)

```sql
-- models/intermediate/int_finance__journal_entries.sql
{{ config(materialized='incremental', unique_key='id') }}

with moves as (
    select * from {{ ref('stg_odoo__account_move') }}
),

lines as (
    select * from {{ ref('stg_odoo__account_move_line') }}
),

accounts as (
    select * from {{ ref('stg_odoo__account_account') }}
),

enriched as (
    select
        m.id as move_id,
        m.move_name,
        m.reference,
        m.move_date,
        m.state,
        m.move_type,
        m.partner_id,
        l.id as line_id,
        l.name as line_description,
        a.code as account_code,
        a.name as account_name,
        a.account_type,
        l.debit,
        l.credit,
        l.balance,
        l.amount_currency,
        m.currency_id,
        m.company_id,
        m.extracted_at
    from moves m
    inner join lines l on m.id = l.move_id
    inner join accounts a on l.account_id = a.id
)

select * from enriched
```

### Mart Model (Silver → Gold)

```sql
-- models/marts/finance/monthly_pnl.sql
{{ config(materialized='table') }}

with journal_entries as (
    select * from {{ ref('int_finance__journal_entries') }}
    where state = 'posted'
),

monthly_totals as (
    select
        date_trunc('month', move_date) as month,
        company_id,
        account_type,
        sum(credit - debit) as net_amount
    from journal_entries
    group by 1, 2, 3
),

pivoted as (
    select
        month,
        company_id,
        sum(case when account_type = 'income' then net_amount else 0 end) as revenue,
        sum(case when account_type = 'expense' then net_amount else 0 end) as expenses,
        sum(case when account_type in ('income_other', 'expense_depreciation')
                 then net_amount else 0 end) as other_income_expense
    from monthly_totals
    group by 1, 2
)

select
    month,
    company_id,
    revenue,
    expenses,
    other_income_expense,
    revenue + expenses + other_income_expense as net_income,
    round(100.0 * (revenue + expenses) / nullif(revenue, 0), 2) as gross_margin_pct
from pivoted
order by month desc
```

### KPI Dashboard Query

```sql
-- Superset dashboard query
SELECT
    month,
    revenue,
    expenses,
    net_income,
    gross_margin_pct,
    LAG(revenue, 12) OVER (ORDER BY month) as revenue_ly,
    ROUND(100.0 * (revenue - LAG(revenue, 12) OVER (ORDER BY month))
          / NULLIF(LAG(revenue, 12) OVER (ORDER BY month), 0), 1) as revenue_yoy_pct
FROM gold.monthly_pnl
WHERE company_id = 1
ORDER BY month DESC
LIMIT 24
```

---

## Resource Requirements

### Minimum (Small/Dev)

| Component | CPU | Memory | Storage |
|-----------|-----|--------|---------|
| MinIO | 1 | 2 GB | 50 GB |
| Airbyte | 2 | 4 GB | 20 GB |
| dbt | 1 | 2 GB | 5 GB |
| DuckDB | 1 | 2 GB | - |
| Metabase | 1 | 2 GB | 5 GB |
| **Total** | 6 | 12 GB | 80 GB |

### Production (Medium)

| Component | CPU | Memory | Storage |
|-----------|-----|--------|---------|
| MinIO (HA) | 4 | 8 GB | 500 GB |
| Airbyte | 4 | 8 GB | 50 GB |
| dbt | 2 | 4 GB | 10 GB |
| Trino | 4 | 16 GB | 20 GB |
| Superset | 2 | 4 GB | 10 GB |
| DataHub | 4 | 8 GB | 50 GB |
| Dagster | 2 | 4 GB | 10 GB |
| **Total** | 22 | 52 GB | 650 GB |

---

## Security & Governance

### Access Control

- MinIO: IAM policies per bucket
- Trino: Role-based catalog access
- Superset: Row-level security
- dbt: Environment-based profiles

### Data Classification

| Level | Examples | Access |
|-------|----------|--------|
| Public | Product catalog, company info | All users |
| Internal | Sales orders, inventory | Employees |
| Confidential | Payroll, pricing, margins | Restricted |
| Sensitive | PII, payment data | Audit-logged |

### Lineage Tracking

- dbt manifest → DataHub ingestion
- Airbyte logs → DataHub ingestion
- Query logs → DataHub usage tracking

---

## Monitoring & Alerting

### Key Metrics

| Metric | Threshold | Alert |
|--------|-----------|-------|
| Airbyte sync failures | >0 | Critical |
| dbt run failures | >0 | High |
| Data freshness | >4 hours | Warning |
| Query latency (p95) | >10s | Warning |
| Storage usage | >80% | Warning |

### Dashboards

1. **Pipeline Health** - Dagster/Airbyte status
2. **Data Quality** - dbt test results
3. **Usage Analytics** - Query patterns, popular datasets

---

## References

- [dbt Documentation](https://docs.getdbt.com/)
- [Apache Superset](https://superset.apache.org/)
- [Trino Documentation](https://trino.io/docs/current/)
- [MinIO Documentation](https://min.io/docs/)
- [Airbyte Documentation](https://docs.airbyte.com/)
- [DataHub Documentation](https://datahubproject.io/docs/)
