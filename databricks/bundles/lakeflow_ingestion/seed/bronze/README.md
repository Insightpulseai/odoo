# Bronze Seed Fixtures — Finance Analytical Control Tower

Deterministic CSV seed data for the finance analytical control tower demo.
All files are internally consistent: IDs cross-reference correctly, GL entries
balance (debits = credits), amounts roll up, and expense reports sum to their
constituent expenses.

Currency: PHP. Date range: 2026-01 through 2026-03.

## Project Scenarios

| Project | ID | Budget | Actual Spend | Margin | Status | Key Signal |
|---------|----|--------|-------------|--------|--------|------------|
| Alpha | 1 | 500,000 | 380,000 | +24.0% | on_track | Healthy. Under budget each month. On-time milestones. Clean expenses. |
| Beta | 2 | 200,000 | 275,000 | -37.5% | over_budget | Over-budget every month. Delayed milestones. Policy violation (business class flight). Unliquidated cash advance (25K outstanding). |
| Gamma | 3 | 150,000 | 45,000 | +25.0% (underspent) | delayed | Severely underspent but delayed. Missing receipts on expenses. Milestones completed late or delayed. Zero activity in Mar. |

## File Map

| File | Rows | Description |
|------|------|-------------|
| `portfolios.csv` | 1 | FY2026 Finance Transformation portfolio containing all 3 projects |
| `projects.csv` | 3 | Project master data with budget, cost center, status, dates |
| `tasks.csv` | 15 | Work items across projects (stages: preparation/in_progress/review/done/cancelled) |
| `milestones.csv` | 6 | 2 per project: completed, late, overdue, in_progress, delayed |
| `employees.csv` | 5 | EMP-001 through EMP-005, cost rates 2,000-5,000 PHP/day |
| `vendors.csv` | 2 | Acme Consulting (net_30), Metro Office Supplies (net_15) |
| `customers.csv` | 3 | PhilTech Industries, Manila Digital Solutions, Visayan Holdings |
| `gl_journal_entries.csv` | 50 | Double-entry GL. Total debits = total credits = 1,550,000. Entry types: revenue/cogs/payroll/advance |
| `vendor_bills.csv` | 4 | Statuses: paid, open, overdue |
| `invoices.csv` | 4 | Statuses: paid, posted_open, overdue |
| `payments.csv` | 6 | Inbound (invoice collections) and outbound (bill payments, advances) |
| `expenses.csv` | 8 | Statuses: draft/submitted/approved/posted/refused. Includes policy violation and missing receipts |
| `expense_reports.csv` | 3 | Statuses: submitted, approved, posted. Totals verified against expense line items |
| `cash_advances.csv` | 2 | CA-001: fully liquidated (50K/50K). CA-002: partially liquidated (15K/40K = 25K outstanding) |
| `budgets.csv` | 9 | 3 projects x 3 months. Planned amounts sum to project budgets. Variances are deterministic |

## Cross-Reference Integrity

- `projects.portfolio_id` -> `portfolios.id`
- `tasks.project_id` -> `projects.id`
- `tasks.assignee_id` -> `employees.id`
- `milestones.project_id` -> `projects.id`
- `gl_journal_entries.project_id` -> `projects.id`
- `vendor_bills.vendor_id` -> `vendors.id`
- `vendor_bills.project_id` -> `projects.id`
- `invoices.customer_id` -> `customers.id`
- `invoices.project_id` -> `projects.id`
- `payments.reference_id` -> `invoices.id` or `vendor_bills.id` or `cash_advances.id`
- `payments.project_id` -> `projects.id`
- `expenses.employee_id` -> `employees.id`
- `expenses.project_id` -> `projects.id`
- `expense_reports.employee_id` -> `employees.id`
- `expense_reports.expense_ids` -> `expenses.id` (comma-separated)
- `cash_advances.employee_id` -> `employees.id`
- `cash_advances.project_id` -> `projects.id`
- `budgets.project_id` -> `projects.id`

## GL Account Chart

| Code | Name | Type |
|------|------|------|
| 1100 | Cash and Cash Equivalents | Asset |
| 1200 | Accounts Receivable | Asset |
| 1300 | Employee Advances Receivable | Asset |
| 2100 | Accounts Payable | Liability |
| 4000 | Service Revenue | Revenue |
| 5100 | Cost of Goods Sold | Expense |
| 5200 | Payroll Expense | Expense |
| 5300 | Operating Expenses | Expense |

## Verification

Run from this directory:

```python
python3 -c "
import csv
d=c=0
with open('gl_journal_entries.csv') as f:
    for r in csv.DictReader(f):
        d+=float(r['debit']); c+=float(r['credit'])
print(f'Debits={d:,.2f} Credits={c:,.2f} Balanced={abs(d-c)<0.01}')
"
```
