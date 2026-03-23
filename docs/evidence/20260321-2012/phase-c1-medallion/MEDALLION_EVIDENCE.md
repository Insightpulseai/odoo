# Phase C1 -- Analytics Mirroring: Medallion Architecture Evidence

**Date**: 2026-03-21T12:12Z
**Workspace**: adb-7405610347978231.11.azuredatabricks.net
**Catalog**: dbw_ipai_dev
**SQL Warehouse**: e7d89eabce4c330c (RUNNING)

---

## Layer Verification (Row Counts)

| Layer  | Table              | Rows |
|--------|--------------------|------|
| bronze | res_partner        | 51   |
| bronze | account_move       | 12   |
| bronze | project_task       | 179  |
| silver | dim_partner        | 48   |
| silver | fact_invoice       | 12   |
| silver | fact_task          | 179  |
| gold   | finance_summary    | 2    |
| gold   | ppm_close_progress | 17   |
| gold   | client_revenue     | 5    |

## Silver Layer Tables

### dim_partner (48 active partners from 51 total)
Cleansed: filtered `active = true`, selected key business columns.

### fact_invoice (12 invoices: 6 AR + 6 AP)
Enriched: joined with res_partner for partner_name, filtered to invoice move types only.

### fact_task (179 PPM tasks)
Enriched: added `task_phase` classification (Preparation/Review/Approval/Milestone/Parent)
and `deadline_status` (Overdue/Due Today/Due Soon/On Track).

## Gold Layer Aggregates

### finance_summary
| Category            | Docs | Total Amount    | Total Tax      | Outstanding     |
|---------------------|------|-----------------|----------------|-----------------|
| Accounts Payable    | 6    | 5,409,600.00    | 280,600.00     | 5,409,600.00    |
| Accounts Receivable | 6    | 10,024,761.60   | 1,074,081.60   | 10,024,761.60   |

### client_revenue (Top 5)
| Client                      | Invoices | Revenue        |
|-----------------------------|----------|----------------|
| Jollibee Foods Corporation  | 2        | 5,620,641.60   |
| Globe Telecom, Inc.         | 1        | 1,486,520.00   |
| Ayala Land, Inc.            | 1        | 1,176,000.00   |
| SM Investments Corporation  | 1        | 957,600.00     |
| Nestle Philippines, Inc.    | 1        | 784,000.00     |

### ppm_close_progress
17 rows: task counts by project_id, task_phase, deadline_status.
1 overdue item detected in project 5 across Approval/Parent/Preparation/Review phases.

## Dashboard

- **Name**: IPAI-Finance-PPM-Analytics
- **Dashboard ID**: 01f1251f30541fdfbb6a7290ea76e7eb
- **URL**: https://adb-7405610347978231.11.azuredatabricks.net/sql/dashboardsv3/01f1251f30541fdfbb6a7290ea76e7eb
- **Published**: 2026-03-21T12:12:12.322Z
- **Widgets**: Finance Summary (table), Client Revenue (bar chart), PPM Progress (stacked bar)

## Permission Grants Applied

- `GRANT USE SCHEMA ON SCHEMA dbw_ipai_dev.bronze TO account users`
- `GRANT SELECT ON SCHEMA dbw_ipai_dev.bronze TO account users`
- `GRANT USE CATALOG ON CATALOG dbw_ipai_dev TO account users`

Bronze schema owner was `ceo@insightpulseai.com`; SQL warehouse runs as `admin@insightpulseai.com`.
Grants to `account users` resolved the cross-principal permission gap.

## Verification: PASS
