# Checklist: Month-End Close

## Pre-Close (Day -5 to -1)

- [ ] All vendor bills for the period entered and posted
- [ ] All customer invoices for the period issued
- [ ] All bank statements imported through end of period
- [ ] All expense reports submitted and approved
- [ ] Intercompany transactions reconciled
- [ ] Foreign currency revaluation run (if applicable)

## Bank Reconciliation (Day 1)

- [ ] Import final bank statement for the period
- [ ] Run auto-reconciliation rules
- [ ] Review and resolve unmatched items
- [ ] Verify reconciliation balance = bank balance
- [ ] Document any outstanding checks or deposits in transit

## Accruals and Adjustments (Day 1-2)

- [ ] Post revenue accruals (earned but not invoiced)
- [ ] Post expense accruals (received but not billed)
- [ ] Post prepayment amortization entries
- [ ] Post depreciation entries (fixed assets)
- [ ] Post payroll accrual if payroll crosses period boundary
- [ ] Review and post any manual journal entries

## Tax (Day 2-3)

- [ ] Verify VAT output tax totals
- [ ] Verify VAT input tax totals
- [ ] Generate withholding tax report (BIR 2307 for PH)
- [ ] Reconcile tax accounts to tax reports
- [ ] Generate SLSP if applicable

## Intercompany (Day 3, if multi-company)

- [ ] Verify all intercompany invoices have matching counterparts
- [ ] Run intercompany reconciliation
- [ ] Post elimination entries (consolidated reporting)
- [ ] Verify intercompany balance = zero

## Review and Validation (Day 3-4)

- [ ] Generate trial balance — verify debits = credits
- [ ] Compare current month to prior month for anomalies
- [ ] Compare current month to budget (MIS Builder)
- [ ] Review aged receivables — investigate >90 day items
- [ ] Review aged payables — verify nothing overdue
- [ ] Verify bank account balances match physical statements

## Close (Day 4-5)

- [ ] Set lock date for non-advisers to end of period
- [ ] Generate Balance Sheet
- [ ] Generate Profit & Loss
- [ ] Generate Cash Flow (if tracked)
- [ ] Archive period reports in `docs/evidence/`
- [ ] Set lock date for advisers to end of period (hard lock)
- [ ] Notify stakeholders of close completion

## Odoo Settings

| Setting | Location | Value |
|---------|----------|-------|
| Lock Date for Non-Advisers | Settings → Accounting → Lock Dates | End of closed month |
| Lock Date for All Users | Settings → Accounting → Lock Dates | End of closed month (after review) |
| Tax Lock Date | Settings → Accounting → Lock Dates | End of closed month |
