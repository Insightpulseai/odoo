# Data dictionary

Data architecture reference for InsightPulse AI's Odoo CE 19 deployment. Covers the 10-layer data model, canonical tables, star schema for analytics, BIR compliance tables, and medallion ETL architecture.

## 10-layer architecture

| Layer | Code | Purpose | Examples |
|-------|------|---------|----------|
| L0 | Raw ingestion | Unprocessed external data | Bank feeds, OCR output, API imports |
| L1 | Staging | Validated, typed, deduplicated | `bronze_*` tables in analytics DB |
| L2 | Master data | Reference entities | `res.partner`, `res.company`, `account.account` |
| L3 | Transactional | Business events | `account.move`, `account.move.line`, `hr.payslip` |
| L4 | Derived | Computed from L2+L3 | Tax provisions, depreciation schedules |
| L5 | Aggregated | Pre-computed summaries | Trial balance, aging reports |
| L6 | Compliance | Regulatory outputs | BIR forms, SEC filings |
| L7 | Analytical | Star schema facts and dimensions | `fact_gl_transaction`, `dim_account` |
| L8 | Presentation | Dashboards and reports | Superset dashboards, Odoo reports |
| L9 | Archive | Historical snapshots | 10-year BIR retention, audit trail |

## Canonical fact table: account.move.line

The `account.move.line` table is the central fact table for all financial data in Odoo.

| Field | Type | Description | Index |
|-------|------|-------------|-------|
| `id` | Integer | Primary key | PK |
| `move_id` | Many2one (`account.move`) | Parent journal entry | FK, indexed |
| `account_id` | Many2one (`account.account`) | GL account | FK, indexed |
| `partner_id` | Many2one (`res.partner`) | Business partner | FK, indexed |
| `product_id` | Many2one (`product.product`) | Product/service | FK |
| `journal_id` | Many2one (`account.journal`) | Source journal | FK, indexed |
| `company_id` | Many2one (`res.company`) | Legal entity | FK |
| `currency_id` | Many2one (`res.currency`) | Transaction currency | FK |
| `date` | Date | Transaction date | Indexed |
| `name` | Char | Line description | |
| `ref` | Char | Reference | |
| `debit` | Monetary | Debit amount (company currency) | |
| `credit` | Monetary | Credit amount (company currency) | |
| `balance` | Monetary | Debit - Credit (computed) | |
| `amount_currency` | Monetary | Amount in transaction currency | |
| `quantity` | Float | Quantity | |
| `price_unit` | Float | Unit price | |
| `discount` | Float | Discount percentage | |
| `tax_ids` | Many2many (`account.tax`) | Applied taxes | |
| `tax_line_id` | Many2one (`account.tax`) | Tax that generated this line | FK |
| `tax_tag_ids` | Many2many (`account.account.tag`) | Tax report tags | |
| `analytic_distribution` | JSON | Analytic account distribution | |
| `reconciled` | Boolean | Whether the line is reconciled | |
| `full_reconcile_id` | Many2one (`account.full.reconcile`) | Full reconcile group | FK |
| `move_name` | Char | Journal entry number (related) | |
| `parent_state` | Selection | Journal entry state (related) | |
| `date_maturity` | Date | Due date | Indexed |
| `payment_id` | Many2one (`account.payment`) | Related payment | FK |
| `statement_line_id` | Many2one (`account.bank.statement.line`) | Bank statement line | FK |
| `create_date` | Datetime | Record creation timestamp | |
| `write_date` | Datetime | Last modification timestamp | |
| `create_uid` | Many2one (`res.users`) | Created by | FK |
| `write_uid` | Many2one (`res.users`) | Modified by | FK |

## Master data tables

### account.account

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `code` | Char | Account code (e.g., 1010) |
| `name` | Char | Account name |
| `account_type` | Selection | Asset, liability, equity, revenue, expense |
| `reconcile` | Boolean | Allow reconciliation |
| `deprecated` | Boolean | No new postings allowed |
| `company_id` | Many2one | Legal entity |
| `tag_ids` | Many2many | BIR/SEC reporting tags |
| `group_id` | Many2one | Account group (for reporting hierarchy) |

### res.partner

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `name` | Char | Partner name |
| `vat` | Char | Tax identification number (TIN) |
| `company_type` | Selection | Individual or company |
| `customer_rank` | Integer | Customer indicator |
| `supplier_rank` | Integer | Vendor indicator |
| `property_account_receivable_id` | Many2one | Default AR account |
| `property_account_payable_id` | Many2one | Default AP account |
| `property_payment_term_id` | Many2one | Default payment terms |
| `country_id` | Many2one | Country |
| `industry_id` | Many2one | Industry classification |

### product.product

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `name` | Char | Product name |
| `default_code` | Char | Internal reference |
| `type` | Selection | Consumable, service, storable |
| `categ_id` | Many2one | Product category |
| `list_price` | Float | Sales price |
| `standard_price` | Float | Cost |
| `taxes_id` | Many2many | Customer taxes |
| `supplier_taxes_id` | Many2many | Vendor taxes |
| `property_account_income_id` | Many2one | Income account override |
| `property_account_expense_id` | Many2one | Expense account override |

## Star schema (analytics)

The analytical layer (L7) uses a star schema for Superset dashboards and ad-hoc reporting.

```
                    ┌──────────────┐
                    │  dim_account  │
                    └──────┬───────┘
                           │
┌──────────────┐    ┌──────┴───────┐    ┌──────────────┐
│  dim_partner  ├────┤ fact_gl_txn  ├────┤   dim_date    │
└──────────────┘    └──────┬───────┘    └──────────────┘
                           │
                    ┌──────┴───────┐
                    │ dim_journal   │
                    └──────────────┘
```

### fact_gl_transaction

| Column | Type | Source |
|--------|------|--------|
| `txn_id` | BIGINT | `account.move.line.id` |
| `move_id` | BIGINT | `account.move.id` |
| `account_key` | INT | FK to `dim_account` |
| `partner_key` | INT | FK to `dim_partner` |
| `date_key` | INT | FK to `dim_date` (YYYYMMDD) |
| `journal_key` | INT | FK to `dim_journal` |
| `debit` | NUMERIC(15,2) | `account.move.line.debit` |
| `credit` | NUMERIC(15,2) | `account.move.line.credit` |
| `balance` | NUMERIC(15,2) | Computed |
| `amount_currency` | NUMERIC(15,2) | Foreign currency amount |
| `quantity` | NUMERIC(12,4) | Line quantity |
| `is_reconciled` | BOOLEAN | Reconciliation status |
| `move_type` | VARCHAR(20) | Entry, invoice, bill, payment |
| `state` | VARCHAR(10) | Posted, draft, cancel |

### dim_account

| Column | Type | Source |
|--------|------|--------|
| `account_key` | INT | Surrogate key |
| `account_code` | VARCHAR(10) | `account.account.code` |
| `account_name` | VARCHAR(256) | `account.account.name` |
| `account_type` | VARCHAR(50) | Asset, liability, equity, revenue, expense |
| `account_group` | VARCHAR(100) | Reporting group |
| `is_reconcilable` | BOOLEAN | Allow reconciliation |

### dim_partner

| Column | Type | Source |
|--------|------|--------|
| `partner_key` | INT | Surrogate key |
| `partner_name` | VARCHAR(256) | `res.partner.name` |
| `tin` | VARCHAR(20) | Tax ID |
| `partner_type` | VARCHAR(20) | Customer, vendor, both |
| `country` | VARCHAR(50) | Country name |
| `industry` | VARCHAR(100) | Industry classification |

### dim_date

| Column | Type | Description |
|--------|------|-------------|
| `date_key` | INT | YYYYMMDD |
| `full_date` | DATE | Calendar date |
| `year` | INT | Fiscal year |
| `quarter` | INT | Fiscal quarter (1-4) |
| `month` | INT | Month (1-12) |
| `month_name` | VARCHAR(20) | January, February, ... |
| `day_of_week` | INT | 1 (Monday) - 7 (Sunday) |
| `is_business_day` | BOOLEAN | Excludes weekends and PH holidays |
| `fiscal_period` | VARCHAR(10) | YYYY-MM |

### dim_journal

| Column | Type | Source |
|--------|------|--------|
| `journal_key` | INT | Surrogate key |
| `journal_code` | VARCHAR(10) | `account.journal.code` |
| `journal_name` | VARCHAR(256) | `account.journal.name` |
| `journal_type` | VARCHAR(20) | Sale, purchase, bank, general |

## BIR compliance tables

### l10n_ph.bir.1601c (Monthly remittance return)

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `period_start` | Date | Tax period start |
| `period_end` | Date | Tax period end |
| `total_compensation` | Monetary | Total taxable compensation |
| `tax_withheld` | Monetary | Total tax withheld |
| `adjustment` | Monetary | Prior period adjustments |
| `tax_due` | Monetary | Net tax due |
| `penalty` | Monetary | Late filing penalty |
| `state` | Selection | Draft, computed, filed |
| `filing_date` | Date | Actual filing date |
| `deadline` | Date | Statutory deadline (10th of following month) |

### withholding.line

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `move_line_id` | Many2one | Source `account.move.line` |
| `partner_id` | Many2one | Payee |
| `tin` | Char | Payee TIN |
| `atc_code` | Char | Alphanumeric tax code (e.g., WC010) |
| `base_amount` | Monetary | Taxable base |
| `tax_rate` | Float | Withholding rate |
| `tax_withheld` | Monetary | Amount withheld |
| `period` | Date | Tax period |
| `bir_form` | Selection | 1601-EQ, 1601-FQ, 2307 |

### l10n_ph.bir.2550q (Quarterly VAT return)

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `quarter` | Selection | Q1, Q2, Q3, Q4 |
| `year` | Integer | Tax year |
| `output_vat_sales` | Monetary | VAT on sales of goods |
| `output_vat_services` | Monetary | VAT on services |
| `total_output_vat` | Monetary | Total output VAT |
| `input_vat_purchases` | Monetary | Input VAT on purchases |
| `input_vat_capital` | Monetary | Input VAT on capital goods |
| `total_input_vat` | Monetary | Total input VAT |
| `net_vat_payable` | Monetary | Output - Input VAT |
| `state` | Selection | Draft, computed, filed |
| `filing_date` | Date | Actual filing date |
| `deadline` | Date | 25th of month following quarter end |

## Medallion ETL tables

The ETL pipeline follows the medallion architecture (Bronze, Silver, Gold) for data flowing from Odoo to the analytics layer.

### Bronze (raw extraction)

| Table | Source | Refresh | Description |
|-------|--------|---------|-------------|
| `bronze_account_move` | `account.move` | Hourly | Raw journal entries |
| `bronze_account_move_line` | `account.move.line` | Hourly | Raw journal entry lines |
| `bronze_res_partner` | `res.partner` | Daily | Raw partner data |
| `bronze_account_account` | `account.account` | Daily | Raw chart of accounts |
| `bronze_hr_payslip` | `hr.payslip` | Daily | Raw payslip data |
| `bronze_account_payment` | `account.payment` | Hourly | Raw payment records |

### Silver (cleansed and conformed)

| Table | Source | Transformations |
|-------|--------|-----------------|
| `silver_gl_entries` | `bronze_account_move_line` | Deduplicated, null-handled, currency-normalized |
| `silver_partners` | `bronze_res_partner` | TIN validated, duplicates merged, type classified |
| `silver_accounts` | `bronze_account_account` | Hierarchy resolved, groups assigned |
| `silver_payroll` | `bronze_hr_payslip` | Components exploded, contributions validated |

### Gold (business-ready)

| Table | Source | Purpose |
|-------|--------|---------|
| `gold_trial_balance` | `silver_gl_entries` | Period-end trial balance snapshot |
| `gold_ar_aging` | `silver_gl_entries` + `silver_partners` | AR aging buckets (current, 30, 60, 90, 120+) |
| `gold_ap_aging` | `silver_gl_entries` + `silver_partners` | AP aging buckets |
| `gold_vat_summary` | `silver_gl_entries` | Output vs. input VAT for BIR reporting |
| `gold_payroll_summary` | `silver_payroll` | Department-level payroll costs |
| `gold_cashflow` | `silver_gl_entries` | Cash flow statement data |

## OCA extension mapping

| OCA module | Tables added/modified | Purpose |
|------------|----------------------|---------|
| `account_financial_report` | View models for reports | Enhanced financial reporting |
| `account_fiscal_year` | `account.fiscal.year` | Explicit fiscal year management |
| `account_fiscal_month` | `account.fiscal.month` | Monthly period management |
| `account_move_line_tax_editable` | Modified `account.move.line` | Editable tax lines |
| `account_asset_management` | `account.asset`, `account.asset.line` | Fixed asset lifecycle |
| `hr_employee_document` | `hr.employee.document` | Employee document storage |

## Data governance

### Quality metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Completeness | >= 99.5% | % of required fields populated |
| Accuracy | >= 99.9% | % of entries matching source documents |
| Timeliness | < 1 hour | Lag between transaction and data availability |
| Consistency | 100% | Debit = Credit for all posted entries |
| Uniqueness | 100% | No duplicate journal entry numbers per journal |

### Retention policy

| Data category | Retention period | Legal basis | Storage tier |
|---------------|-----------------|-------------|-------------|
| Financial records (GL, AP, AR) | 10 years | BIR NIRC Section 235 | L9 Archive |
| Tax records and BIR forms | 10 years | BIR NIRC Section 235 | L9 Archive |
| Payroll records | 5 years | DOLE Department Order 174-17 | L9 Archive |
| Employee records | 5 years after separation | Data Privacy Act (RA 10173) | L9 Archive |
| Audit trail / change logs | 10 years | SEC SRC Rule 68 | L9 Archive |
| Transient analytics (bronze) | 90 days | Internal policy | L1 Staging |
| Aggregated analytics (gold) | 3 years | Internal policy | L7 Analytical |

!!! info "Archive strategy"
    Data exceeding the active retention window migrates to cold storage (Azure Blob Archive tier) with indexed metadata for retrieval. The `ir.logging` and `mail.message` tables are the primary audit trail sources in Odoo.
