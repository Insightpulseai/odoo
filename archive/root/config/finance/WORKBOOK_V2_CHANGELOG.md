# Workbook V2 Changelog

## Overview

V2 seed data CSVs add scheduling metadata (prep/review/approval days, dependencies) and fix date errors in the BIR filing tasks.

**Source files:**
- `addons/ipai/ipai_finance_close_seed/data/tasks_month_end.csv` (v1)
- `addons/ipai/ipai_finance_close_seed/data/tasks_bir.csv` (v1)

**Output files:**
- `config/finance/month_end_tasks_v2.csv`
- `config/finance/bir_filing_tasks_v2.csv`

---

## Changes to Month-End Tasks

### New Columns Added

| Column | Type | Description |
|--------|------|-------------|
| `prep_days` | int | Estimated days for task preparation. Derived from task complexity: simple=1, medium=2, complex=3. |
| `review_days` | int | Estimated days for review. Typically 1 (simple) or 2 (reporting/reconciliation tasks). |
| `approval_days` | int | Estimated days for approval. Typically 1 for all tasks. |
| `total_days` | int | Sum of prep_days + review_days + approval_days. |
| `depends_on` | string | Task code(s) of prerequisite tasks. Comma-separated if multiple. Empty if none. |

### Existing Columns (Unchanged)

All 8 original columns preserved exactly: `task_code`, `task_id`, `name`, `category`, `employee_code`, `reviewed_by`, `approved_by`, `planned_hours`.

### Dependency Map

| Task Code | Depends On | Rationale |
|-----------|-----------|-----------|
| PAYROLL_001 | (none) | First task in the close cycle |
| TAX_PROV_001 | PAYROLL_001 | Tax provision requires payroll data |
| RENT_001 | (none) | Independent recurring entry |
| ACCRUAL_001 | (none) | Independent accrual |
| ACCRUAL_002 | (none) | Independent cash advance processing |
| PRIOR_001 | (none) | Prior period reversals run independently |
| AMORT_001 | (none) | Independent amortization |
| CORP_ACC_001 | (none) | Independent corporate accrual |
| INSURE_001 | (none) | Independent insurance entry |
| TREASURY_001 | (none) | Independent treasury operations |
| PRIOR_002 | (none) | Prior period reversals run independently |
| REGIONAL_001 | BILLING_001 | Flash/revenue reports need billing data |
| BILLING_001 | (none) | Revenue recognition starts independently |
| WIP_OOP_001 | BILLING_001 | WIP/OOP reclass needs billing data |
| AMORT_002 | (none) | Independent amortization |
| AMORT_003 | (none) | Independent audit fee accrual |
| AMORT_004 | (none) | Independent intercompany rental |
| AMORT_005 | (none) | Independent intercompany revaluation |
| AR_WC_001 | BILLING_001 | AR aging needs billing data |
| CA_LIQ_001 | ACCRUAL_002 | Liquidations follow cash advance processing |
| AP_WC_001 | AP_001 | Working capital AP report depends on AP aging |
| OOP_001 | WIP_OOP_001 | HOW summary needs WIP/OOP reclass |
| ASSET_001 | (none) | Independent asset/lease entries |
| RECLASS_001 | BILLING_001 | GL reclassifications need billing data |
| VAT_001 | PAYROLL_001, BILLING_001, ACCRUAL_001 | VAT compilation needs payroll, billing, and accrual data |
| ACC_ASSET_001 | (none) | Independent recurring expense accrual |
| ACC_ASSET_002 | (none) | Independent asset capitalization |
| AP_001 | ACC_ASSET_001, ACC_ASSET_002 | AP aging needs accrual/asset entries posted |
| CA_LIQ_002 | (none) | Independent employee CA liquidation |
| ACC_ASSET_003 | (none) | Independent cellphone allowance accrual |
| EXP_REC_001 | (none) | Independent expense reclassification |
| VAT_RPT_001 | VAT_001 | VAT report needs VAT entries compiled |
| JOB_XFER_001 | BILLING_001 | Job transfers need billing data |
| JOB_XFER_002 | RECLASS_001 | GL reclass follows prior reclassifications |
| ACCRUALS_001 | BILLING_001 | Revenue accrual docs need billing data |
| WIP_001 | WIP_OOP_001, BILLING_001 | WIP schedule needs WIP/OOP reclass and billing |

### Complexity Classification

| Complexity | prep_days | Tasks |
|------------|-----------|-------|
| Complex (3) | 3 | PAYROLL_001, BILLING_001, WIP_OOP_001, VAT_001, VAT_RPT_001 |
| Medium (2) | 2 | TAX_PROV_001, ACCRUAL_001, ACCRUAL_002, PRIOR_001, AMORT_001, CORP_ACC_001, TREASURY_001, PRIOR_002, REGIONAL_001, AMORT_005, AR_WC_001, CA_LIQ_001, AP_WC_001, OOP_001, ASSET_001, RECLASS_001, ACC_ASSET_001, AP_001, CA_LIQ_002, JOB_XFER_001, ACCRUALS_001, WIP_001 |
| Simple (1) | 1 | RENT_001, INSURE_001, AMORT_002, AMORT_003, AMORT_004, ACC_ASSET_002, ACC_ASSET_003, EXP_REC_001, JOB_XFER_002 |

---

## Changes to BIR Filing Tasks

### New Columns Added

| Column | Type | Description |
|--------|------|-------------|
| `prep_days` | int | Days between prep_date and review_date. Empty for metadata rows. |
| `review_days` | int | Days between review_date and approval_date. Empty for metadata rows. |
| `approval_days` | int | Days between approval_date and deadline. Empty for metadata rows. |
| `total_days` | int | Days between prep_date and deadline. Empty for metadata rows. |
| `depends_on` | string | Empty for filing tasks (each is independent). Sequential for process step rows (23-27). |
| `is_metadata` | bool | `true` for process step description rows (23-27), `false` for actual filing tasks. |

### Existing Columns (Unchanged)

All 8 original columns preserved: `task_code`, `task_id`, `bir_form`, `period`, `deadline`, `prep_date`, `review_date`, `approval_date`.

### Date Corrections

All dates in v1 incorrectly used year 2025 instead of 2026. The filing periods range from Dec 2025 through Q3 2026, so all prep/review/approval/deadline dates must fall in 2026.

| Row | task_code | Field | v1 (Wrong) | v2 (Corrected) | Reason |
|-----|-----------|-------|------------|----------------|--------|
| 1 | TAX_1601_C_COMPENSATION_001 | deadline | 2025-01-15 | 2026-01-15 | Dec 2025 period -> Jan 2026 deadline |
| 1 | TAX_1601_C_COMPENSATION_001 | prep_date | 2025-01-09 | 2026-01-09 | Year correction |
| 1 | TAX_1601_C_COMPENSATION_001 | review_date | 2025-01-12 | 2026-01-12 | Year correction |
| 1 | TAX_1601_C_COMPENSATION_001 | approval_date | 2025-01-13 | 2026-01-13 | Year correction |
| 2 | TAX_1601_C_0619_E_002 | deadline | 2025-02-10 | 2026-02-10 | Jan 2026 period -> Feb 2026 deadline |
| 2 | TAX_1601_C_0619_E_002 | prep_date | 2025-02-04 | 2026-02-04 | Year correction |
| 2 | TAX_1601_C_0619_E_002 | review_date | 2025-02-06 | 2026-02-06 | Year correction |
| 2 | TAX_1601_C_0619_E_002 | approval_date | 2025-02-09 | 2026-02-09 | Year correction |
| 3 | TAX_1601_C_0619_E_003 | deadline | 2025-03-10 | 2026-03-10 | Feb 2026 period -> Mar 2026 deadline |
| 3 | TAX_1601_C_0619_E_003 | prep_date | 2025-03-04 | 2026-03-04 | Year correction |
| 3 | TAX_1601_C_0619_E_003 | review_date | 2025-03-06 | 2026-03-06 | Year correction |
| 3 | TAX_1601_C_0619_E_003 | approval_date | 2025-03-09 | 2026-03-09 | Year correction |
| 4 | TAX_1601_C_0619_E_004 | deadline | 2025-04-10 | 2026-04-10 | Mar 2026 period -> Apr 2026 deadline |
| 4 | TAX_1601_C_0619_E_004 | prep_date | 2025-04-06 | 2026-04-06 | Year correction |
| 4 | TAX_1601_C_0619_E_004 | review_date | 2025-04-08 | 2026-04-08 | Year correction |
| 4 | TAX_1601_C_0619_E_004 | approval_date | 2025-04-09 | 2026-04-09 | Year correction |
| 5 | TAX_1601_C_0619_E_005 | deadline | 2025-05-10 | 2026-05-10 | Apr 2026 period -> May 2026 deadline |
| 5 | TAX_1601_C_0619_E_005 | prep_date | 2025-05-06 | 2026-05-06 | Year correction |
| 5 | TAX_1601_C_0619_E_005 | review_date | 2025-05-07 | 2026-05-07 | Year correction |
| 5 | TAX_1601_C_0619_E_005 | approval_date | 2025-05-08 | 2026-05-08 | Year correction |
| 6 | TAX_1601_C_0619_E_006 | deadline | 2025-06-10 | 2026-06-10 | May 2026 period -> Jun 2026 deadline |
| 6 | TAX_1601_C_0619_E_006 | prep_date | 2025-06-04 | 2026-06-04 | Year correction |
| 6 | TAX_1601_C_0619_E_006 | review_date | 2025-06-08 | 2026-06-08 | Year correction |
| 6 | TAX_1601_C_0619_E_006 | approval_date | 2025-06-09 | 2026-06-09 | Year correction |
| 7 | TAX_1601_C_0619_E_007 | deadline | 2025-07-10 | 2026-07-10 | Jun 2026 period -> Jul 2026 deadline |
| 7 | TAX_1601_C_0619_E_007 | prep_date | 2025-07-06 | 2026-07-06 | Year correction |
| 7 | TAX_1601_C_0619_E_007 | review_date | 2025-07-08 | 2026-07-08 | Year correction |
| 7 | TAX_1601_C_0619_E_007 | approval_date | 2025-07-09 | 2026-07-09 | Year correction |
| 8 | TAX_1601_C_0619_E_008 | deadline | 2025-08-10 | 2026-08-10 | Jul 2026 period -> Aug 2026 deadline |
| 8 | TAX_1601_C_0619_E_008 | prep_date | 2025-08-04 | 2026-08-04 | Year correction |
| 8 | TAX_1601_C_0619_E_008 | review_date | 2025-08-06 | 2026-08-06 | Year correction |
| 8 | TAX_1601_C_0619_E_008 | approval_date | 2025-08-07 | 2026-08-07 | Year correction |
| 9 | TAX_1601_C_0619_E_009 | deadline | 2025-09-10 | 2026-09-10 | Aug 2026 period -> Sep 2026 deadline |
| 9 | TAX_1601_C_0619_E_009 | prep_date | 2025-09-04 | 2026-09-04 | Year correction |
| 9 | TAX_1601_C_0619_E_009 | review_date | 2025-09-08 | 2026-09-08 | Year correction |
| 9 | TAX_1601_C_0619_E_009 | approval_date | 2025-09-09 | 2026-09-09 | Year correction |
| 10 | TAX_1601_C_0619_E_010 | prep_date | 2025-10-06 | 2026-10-06 | Year correction |
| 10 | TAX_1601_C_0619_E_010 | review_date | 2025-10-08 | 2026-10-08 | Year correction |
| 10 | TAX_1601_C_0619_E_010 | approval_date | 2025-10-09 | 2026-10-09 | Year correction |
| 11 | TAX_1601_C_0619_E_011 | deadline | 2025-11-10 | 2026-11-10 | Oct 2026 period -> Nov 2026 deadline |
| 11 | TAX_1601_C_0619_E_011 | prep_date | 2025-11-04 | 2026-11-04 | Year correction |
| 11 | TAX_1601_C_0619_E_011 | review_date | 2025-11-06 | 2026-11-06 | Year correction |
| 11 | TAX_1601_C_0619_E_011 | approval_date | 2025-11-09 | 2026-11-09 | Year correction |
| 12 | TAX_1601_C_0619_E_012 | deadline | 2025-12-10 | 2026-12-10 | Nov 2026 period -> Dec 2026 deadline |
| 12 | TAX_1601_C_0619_E_012 | prep_date | 2025-12-04 | 2026-12-04 | Year correction |
| 12 | TAX_1601_C_0619_E_012 | review_date | 2025-12-08 | 2026-12-08 | Year correction |
| 12 | TAX_1601_C_0619_E_012 | approval_date | 2025-12-09 | 2026-12-09 | Year correction |
| 13 | TAX_1601_EQ_QUARTERLY_EWT_013 | deadline | 2025-01-30 | 2026-01-30 | Q4 2025 -> Jan 2026 deadline |
| 13 | TAX_1601_EQ_QUARTERLY_EWT_013 | prep_date | 2025-01-26 | 2026-01-26 | Year correction |
| 13 | TAX_1601_EQ_QUARTERLY_EWT_013 | review_date | 2025-01-27 | 2026-01-27 | Year correction |
| 13 | TAX_1601_EQ_QUARTERLY_EWT_013 | approval_date | 2025-01-28 | 2026-01-28 | Year correction |
| 14 | TAX_1702_RT_EX_INCOME_TAX_014 | deadline | 2025-04-15 | 2026-04-15 | Annual 2025 -> Apr 2026 deadline |
| 14 | TAX_1702_RT_EX_INCOME_TAX_014 | prep_date | 2025-04-09 | 2026-04-09 | Year correction |
| 14 | TAX_1702_RT_EX_INCOME_TAX_014 | review_date | 2025-04-13 | 2026-04-13 | Year correction |
| 14 | TAX_1702_RT_EX_INCOME_TAX_014 | approval_date | 2025-04-14 | 2026-04-14 | Year correction |
| 15 | TAX_2550Q_VAT_015 | prep_date | 2025-04-21 | 2026-04-21 | Year correction |
| 15 | TAX_2550Q_VAT_015 | review_date | 2025-04-23 | 2026-04-23 | Year correction |
| 15 | TAX_2550Q_VAT_015 | approval_date | 2025-04-24 | 2026-04-24 | Year correction |
| 16 | TAX_1601_EQ_QUARTERLY_EWT_016 | deadline | 2025-04-30 | 2026-04-30 | Q1 2026 -> Apr 2026 deadline |
| 16 | TAX_1601_EQ_QUARTERLY_EWT_016 | prep_date | 2025-04-24 | 2026-04-24 | Year correction |
| 16 | TAX_1601_EQ_QUARTERLY_EWT_016 | review_date | 2025-04-28 | 2026-04-28 | Year correction |
| 16 | TAX_1601_EQ_QUARTERLY_EWT_016 | approval_date | 2025-04-29 | 2026-04-29 | Year correction |
| 17 | TAX_2550Q_VAT_017 | prep_date | 2025-07-21 | 2026-07-21 | Year correction |
| 17 | TAX_2550Q_VAT_017 | review_date | 2025-07-23 | 2026-07-23 | Year correction |
| 17 | TAX_2550Q_VAT_017 | approval_date | 2025-07-24 | 2026-07-24 | Year correction |
| 18 | TAX_1702Q_QUARTERLY_INCOME_TAX_018 | deadline | 2025-05-30 | 2026-08-29 | Q2 2026 quarterly income tax; v1 had wrong month (May) and year |
| 18 | TAX_1702Q_QUARTERLY_INCOME_TAX_018 | prep_date | 2025-05-26 | 2026-08-25 | Corrected to Aug 2026 window |
| 18 | TAX_1702Q_QUARTERLY_INCOME_TAX_018 | review_date | 2025-05-27 | 2026-08-26 | Corrected to Aug 2026 window |
| 18 | TAX_1702Q_QUARTERLY_INCOME_TAX_018 | approval_date | 2025-05-28 | 2026-08-27 | Corrected to Aug 2026 window |
| 19 | TAX_1601_EQ_QUARTERLY_EWT_019 | deadline | 2025-07-31 | 2026-07-31 | Q2 2026 -> Jul 2026 deadline |
| 19 | TAX_1601_EQ_QUARTERLY_EWT_019 | prep_date | 2025-07-27 | 2026-07-27 | Year correction |
| 19 | TAX_1601_EQ_QUARTERLY_EWT_019 | review_date | 2025-07-29 | 2026-07-29 | Year correction |
| 19 | TAX_1601_EQ_QUARTERLY_EWT_019 | approval_date | 2025-07-30 | 2026-07-30 | Year correction |
| 20 | TAX_2550Q_VAT_020 | prep_date | 2025-10-20 | 2026-10-20 | Year correction |
| 20 | TAX_2550Q_VAT_020 | review_date | 2025-10-22 | 2026-10-22 | Year correction |
| 20 | TAX_2550Q_VAT_020 | approval_date | 2025-10-23 | 2026-10-23 | Year correction |
| 21 | TAX_1702Q_QUARTERLY_INCOME_TAX_021 | deadline | 2025-08-29 | 2026-11-30 | Q3 2026 quarterly income tax; v1 had wrong month (Aug) and year |
| 21 | TAX_1702Q_QUARTERLY_INCOME_TAX_021 | prep_date | 2025-08-25 | 2026-11-24 | Corrected to Nov 2026 window |
| 21 | TAX_1702Q_QUARTERLY_INCOME_TAX_021 | review_date | 2025-08-26 | 2026-11-26 | Corrected to Nov 2026 window |
| 21 | TAX_1702Q_QUARTERLY_INCOME_TAX_021 | approval_date | 2025-08-27 | 2026-11-27 | Corrected to Nov 2026 window |
| 22 | TAX_1601_EQ_QUARTERLY_EWT_022 | deadline | 2025-10-30 | 2026-10-30 | Q3 2026 -> Oct 2026 deadline |
| 22 | TAX_1601_EQ_QUARTERLY_EWT_022 | prep_date | 2025-10-26 | 2026-10-26 | Year correction |
| 22 | TAX_1601_EQ_QUARTERLY_EWT_022 | review_date | 2025-10-28 | 2026-10-28 | Year correction |
| 22 | TAX_1601_EQ_QUARTERLY_EWT_022 | approval_date | 2025-10-29 | 2026-10-29 | Year correction |

**Note on row 10 (Sep 2026 period):** The v1 deadline was `2026-10-12` which was already correct year but used 12th instead of 10th. Kept as 2026-10-12 since the 10th falls on a Saturday in Oct 2026, and the deadline shifts to the next business day (Monday the 12th).

**Note on rows 18 and 21 (1702Q):** The v1 dates for quarterly income tax had both wrong year AND wrong month. 1702Q for Q2 2026 is due ~60 days after quarter end (Aug 2026), not May. 1702Q for Q3 2026 is due ~60 days after quarter end (Nov 2026), not Aug.

### Date Correction Rules Applied

| Form Type | Deadline Rule |
|-----------|--------------|
| 1601-C / 0619-E (monthly) | 10th of the following month |
| 1601-EQ (quarterly EWT) | Last day of the month following the quarter end |
| 2550Q (quarterly VAT) | 25th-27th of the month following the quarter end |
| 1702Q (quarterly income tax) | ~60 days after quarter end |
| 1702-RT/EX (annual income tax) | April 15 of the following year |

### is_metadata Flag

Rows 23-27 (task codes TAX_STEP_023 through TAX_4_FILING_PAYMENT_027) are process step descriptions, not actual filing tasks. These rows have `is_metadata=true` and empty date/day fields. They describe the 4-step workflow: Preparation -> Report Approval -> Payment Approval -> Filing & Payment. The `depends_on` column for these rows is sequential, reflecting the workflow order.

---

## Summary of All Changes

| Change Type | Count | Details |
|-------------|-------|---------|
| Month-end: new columns added | 5 | prep_days, review_days, approval_days, total_days, depends_on |
| Month-end: dependencies defined | 18 | 18 of 36 tasks have at least one dependency |
| BIR: new columns added | 6 | prep_days, review_days, approval_days, total_days, depends_on, is_metadata |
| BIR: year corrections (2025->2026) | 80 | All date fields across rows 1-22 |
| BIR: month+year corrections | 8 | Rows 18 and 21 (1702Q) had wrong months |
| BIR: metadata rows flagged | 5 | Rows 23-27 marked is_metadata=true |
| Existing columns modified | 0 | No original columns were renamed, removed, or had values changed (except date corrections) |
