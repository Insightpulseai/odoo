# Process Map: Record-to-Report (R2R)

## End-to-End Flow

```
[Transactions]         [Reconciliation]      [Close]              [Reporting]
Daily Postings         Bank Matching         Period Lock          Financial Stmts
  │                       │                     │                     │
  ▼                       ▼                     ▼                     ▼
Post → Reconcile → Accrue → Adjust → Lock Period → Generate Reports → Analyze
  │                       │                     │                     │
account.move         account.bank           res.company          mis.report
                     .statement             (lock dates)         (OCA)
```

## Step Details

| Step | Odoo Model | Action | Frequency |
|------|-----------|--------|-----------|
| Transaction posting | account.move | Create and post journal entries | Daily |
| Bank import | account.bank.statement | Import bank feeds (CAMT, OFX) | Daily/Weekly |
| Auto-reconciliation | account.reconcile.model | Match bank lines to invoices/payments | On import |
| Manual reconciliation | account.bank.statement.line | Resolve unmatched items | Weekly |
| Accruals | account.move | Post period-end accrual entries | Monthly |
| Depreciation | account.asset (OCA) | Run depreciation schedule | Monthly |
| Foreign currency reval | account.move | Revalue open items at period-end rate | Monthly |
| Intercompany elimination | account.move | Post elimination entries | Monthly |
| Period lock | res.company | Set lock_date fields | Monthly |
| Trial balance | account_financial_report (OCA) | Generate TB report | Monthly |
| Balance sheet | account_financial_report (OCA) | Generate BS report | Monthly |
| Profit & loss | account_financial_report (OCA) | Generate P&L report | Monthly |
| Management reports | mis.report (OCA) | Generate custom management reports | Monthly |

## Reconciliation Types

| Type | What is matched | Odoo Implementation |
|------|----------------|---------------------|
| Bank reconciliation | Bank statement vs Odoo payments | account.bank.statement.line matching |
| Customer reconciliation | Invoices vs customer payments | account.move.line partial reconcile |
| Vendor reconciliation | Bills vs vendor payments | account.move.line partial reconcile |
| Intercompany | IC invoices vs IC payments | Manual matching across companies |

## Period Close Sequence

```
1. All transactions posted for the period
2. Bank statements imported and reconciled
3. Accrual entries posted
4. Depreciation run
5. Foreign currency revaluation
6. Intercompany reconciliation
7. Generate trial balance — verify debits = credits
8. Lock period (non-advisers)
9. Generate financial statements
10. Management review
11. Hard lock (all users)
```

## Reports

| Report | OCA Module | SAP Equivalent |
|--------|-----------|----------------|
| Trial Balance | account_financial_report | S_ALR_87012277 |
| Balance Sheet | account_financial_report | S_ALR_87012284 |
| Profit & Loss | account_financial_report | S_ALR_87012289 |
| Aged Receivable | account_financial_report | FBL5N |
| Aged Payable | account_financial_report | FBL1N |
| General Ledger | account_financial_report | FBL3N |
| Cash Flow | Custom / mis_builder | - |
| Budget vs Actual | mis_builder | S_ALR_87013611 |
| Cost Center Report | mis_builder + analytic | KSB1 |

## KPIs

| KPI | Target | Source |
|-----|--------|--------|
| Close cycle time | < 5 working days | Close start → hard lock date |
| Reconciliation rate | > 95% auto-matched | Matched / total bank lines |
| Unreconciled items | < 10 per period | Open bank statement lines |
| Report accuracy | 0 adjustments after close | Post-close journal entries |
