# Month-End Closing Checklist

## Timeline Overview

| Day | Phase | Key Activities |
|-----|-------|----------------|
| 1-3 | Pre-Close | Data gathering, reconciliation |
| 4-5 | Close | Journal entries, final adjustments |
| 6-7 | Reporting | Financial statements, management report |

---

## Day 1-3: Pre-Close Phase

### Data Gathering

- [ ] Download all bank statements for the month
- [ ] Verify all vendor invoices are entered
- [ ] Verify all customer invoices are issued
- [ ] Download credit card statements
- [ ] Collect petty cash vouchers

### Reconciliation

- [ ] Reconcile petty cash fund
- [ ] Match intercompany transactions
- [ ] Review open purchase orders
- [ ] Verify payroll data from HR
- [ ] Reconcile withholding tax accounts

### Pre-Close Checks

- [ ] All recurring entries posted
- [ ] Prepaid expense schedules updated
- [ ] Fixed asset register current
- [ ] Inventory counts completed (if applicable)

---

## Day 4-5: Close Phase

### Journal Entries

- [ ] Post accrued expenses
- [ ] Post prepaid expense amortization
- [ ] Run depreciation schedule
- [ ] Post payroll journal entry
- [ ] Post intercompany settlement entries

### Bank Reconciliation

- [ ] Complete bank reconciliation for each account
- [ ] Investigate outstanding items > 30 days
- [ ] Document reconciling items
- [ ] Get approval for write-offs

### Trial Balance Review

- [ ] Generate trial balance
- [ ] Review account balances for reasonableness
- [ ] Investigate variances > 10% from prior month
- [ ] Document variance explanations

### Period Lock

- [ ] Verify all entries posted
- [ ] Run final validation checks
- [ ] Request period lock from Finance Director

---

## Day 6-7: Reporting Phase

### Financial Statements

- [ ] Generate Balance Sheet
- [ ] Generate Income Statement
- [ ] Generate Cash Flow Statement (quarterly)
- [ ] Verify statement tie-out

### Variance Analysis

- [ ] Calculate budget vs actual variances
- [ ] Identify material variances (> ₱50,000 or > 10%)
- [ ] Document variance explanations
- [ ] Prepare management commentary

### Management Report

- [ ] Draft executive summary
- [ ] Include KPI dashboard
- [ ] Highlight significant items
- [ ] Attach supporting schedules

### Submission

- [ ] Review with Finance Manager
- [ ] Submit to Finance Director by Day 7
- [ ] Archive period documents
- [ ] Update status in Mattermost #month-end-closing

---

## Automation Support

The following are automated via n8n workflows:

| Task | Automation | Trigger |
|------|------------|---------|
| Bank statement import | `bank_statement_import.json` | Daily at 6 AM |
| Depreciation calculation | `depreciation_runner.json` | Monthly on Day 4 |
| Deadline reminders | `month_end_reminder.json` | Day 1, 4, 6 |

## Mattermost Integration

- Start closing: Post in #month-end-closing with `/playbook month-end`
- Task updates: Bot posts completion status automatically
- Escalation: Tag @finance-leadership for blockers

## Key Contacts

| Role | Contact | Responsibility |
|------|---------|----------------|
| Finance Director | CKVC | Period lock, final approval |
| Finance Manager | BOM | Review, variance analysis |
| Finance Staff | Team | Task execution |

---

*See also: [Journal Entry Standards](journal-standards.md) | [Bank Reconciliation](bank-recon.md)*
