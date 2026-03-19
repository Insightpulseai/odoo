# CP-4: Cron Fix Validation Evidence

## Date: 2026-03-19
## Target: ipai-odoo-dev-pg / odoo database

## Cron Status

| Field | Value |
|-------|-------|
| ID | 32 |
| Name | IPAI PPM: Sync Project Budgets to Analytic |
| Active | true |
| Interval | 1 day |
| Last call | 2026-03-18 21:41:52 UTC |
| Next call | 2026-03-19 21:41:51 UTC |

## Code location

- Cron definition: `addons/ipai/ipai_finance_ppm/data/ir_cron_ppm_sync.xml`
- Sync method: `addons/ipai/ipai_finance_ppm/models/analytic_account.py` line 22-33
- Project model: `addons/ipai/ipai_finance_ppm/models/project_project.py`

## Assessment

**Status: PASS**

- Cron exists in production database (ID 32)
- Cron is active
- Cron has executed (lastcall is 2026-03-18, not null)
- Next execution is scheduled for 2026-03-19
- 3 analytic accounts exist in the database

## Remaining

- Budget sync from project to analytic account depends on projects having `ipai_ppm_budget_amount` set
- Demo data seeding (95 tasks) was done but budget amounts are 0.00 in demo
- Real budget data would come from CSV import wizard or manual entry
