---
title: "Month-End Close Checklist"
kb_scope: "finance-close-kb"
group_ids: ["group-guid-placeholder"]
last_updated: "2026-03-15"
---

# Month-End Close Checklist

## Overview

This document provides a step-by-step procedure for completing the month-end close in Odoo CE 19.0 with OCA accounting modules. The checklist is designed for Philippine-based businesses and includes BIR compliance checkpoints.

The month-end close should be completed within 5 business days after the period end. All steps should be performed by the accounting team and reviewed by the Finance Manager before the period is locked.

---

## Prerequisites

Before starting the month-end close, verify:

- [ ] All transactions for the period have been entered
- [ ] All bank statements for the period have been received
- [ ] All vendor bills for the period have been recorded
- [ ] All sales invoices for the period have been issued
- [ ] Petty cash has been replenished and reconciled
- [ ] Payroll for the period has been processed and posted

---

## Step 1: Revenue Recognition and Cutoff

### Objective
Ensure all revenue earned in the period is recognized, and no revenue from the next period is included.

### Procedure

1. **Review Draft Invoices**
   - Navigate to Accounting > Customers > Invoices
   - Filter: Status = Draft, Invoice Date <= Period End
   - Action: Post all valid draft invoices or cancel invalid ones
   - Every invoice remaining in draft at period end must have a documented reason

2. **Check Revenue Accruals**
   - Review services delivered but not yet invoiced
   - Create manual journal entries for unbilled revenue:
     - Debit: Accrued Revenue (asset)
     - Credit: Service Revenue (income)
   - Reverse these entries on the first day of the next period

3. **Verify Deferred Revenue**
   - Check advance payments received for future services
   - Ensure deferred revenue is not recognized prematurely
   - Use the `account_spread_cost_revenue` OCA module for automated spreading

4. **Review Credit Notes**
   - Confirm all credit notes issued during the period are posted
   - Verify credit notes reference the original invoice

### Verification
- Run the Revenue by Period report (MIS Builder) and compare to prior month
- Variance greater than 15% requires explanation documented in journal entry narration

---

## Step 2: Expense Recognition and Cutoff

### Objective
Ensure all expenses incurred in the period are recorded.

### Procedure

1. **Review Vendor Bills**
   - Navigate to Accounting > Vendors > Bills
   - Filter: Status = Draft, Bill Date <= Period End
   - Post all valid draft bills
   - For bills received but not yet entered, create an expense accrual:
     - Debit: Expense account (appropriate category)
     - Credit: Accrued Expenses (liability)

2. **Prepaid Expense Amortization**
   - Review prepaid expense accounts (insurance, rent, subscriptions)
   - Post monthly amortization entries
   - Use `account_spread_cost_revenue` for automated amortization schedules
   - Verify the remaining prepaid balance is reasonable

3. **Employee Expense Reports**
   - Confirm all expense reports for the period are approved and posted
   - Navigate to Expenses > Expense Reports, filter by date
   - Follow up on submitted but unapproved reports

4. **Utility and Recurring Expenses**
   - Verify recurring journal entries have posted for the period
   - Check: rent, utilities, internet, SaaS subscriptions, insurance
   - If a bill has not been received, accrue based on historical average

### Verification
- Run Expense by Category report and compare to prior months
- Check for missing categories (e.g., no utilities expense would indicate a missed entry)

---

## Step 3: Bank Reconciliation

### Objective
Reconcile all bank accounts to their statements as of period end.

### Procedure

1. **Import Bank Statements**
   - Download statements from each bank (BDO, BPI, Metrobank, etc.)
   - Import via Accounting > Configuration > Bank Statements > Import
   - Supported formats: OFX, CSV (bank-specific templates), MT940

2. **Perform Reconciliation**
   - Navigate to Accounting > Bank > Reconciliation
   - Use the OCA `account_reconcile_oca` module for advanced matching
   - Match transactions using the following priority:
     - Automatic match by reference number
     - Match by amount and date range
     - Manual match for remaining items

3. **Investigate Unmatched Items**
   - Unmatched bank transactions may indicate:
     - Missing vendor bills (record the bill, then match)
     - Unrecorded customer payments (create payment entry)
     - Bank fees or interest (create journal entry)
     - Errors in data entry (correct the original entry)
   - All unmatched items must be resolved or documented before closing

4. **Record Bank Adjustments**
   - Post entries for bank charges, interest income, and FX gains/losses
   - For foreign currency accounts, revalue at BSP closing rate

5. **Reconciliation Summary**
   - Generate the bank reconciliation report for each account
   - The reconciled balance must match the bank statement balance exactly
   - Sign-off by preparer and reviewer

### Verification
- Bank Reconciliation Report balance = Bank Statement balance (zero difference)
- All bank accounts must be fully reconciled before proceeding

---

## Step 4: Accounts Receivable Review

### Objective
Ensure AR balances are accurate and collectible.

### Procedure

1. **Aged Receivables Report**
   - Navigate to Accounting > Reporting > Partner Ledger
   - Run the Aged Receivable report (OCA `account_financial_report`)
   - Review balances in aging buckets: Current, 1-30, 31-60, 61-90, 90+ days

2. **Follow Up on Overdue Accounts**
   - Generate follow-up letters for accounts 30+ days overdue
   - Document collection actions taken
   - Escalate accounts 90+ days overdue to management

3. **Allowance for Doubtful Accounts**
   - Review accounts 90+ days overdue for potential write-off
   - Calculate allowance based on company policy:
     - 31-60 days: 5% allowance
     - 61-90 days: 15% allowance
     - 91-120 days: 50% allowance
     - 120+ days: 100% allowance (or specific identification)
   - Post adjusting entry:
     - Debit: Bad Debt Expense
     - Credit: Allowance for Doubtful Accounts

4. **Verify Customer Statements**
   - Send customer statements for accounts with significant balances
   - Reconcile any discrepancies reported by customers

### Verification
- Total AR per aged report matches the AR general ledger balance
- Allowance balance is adequate per aging analysis

---

## Step 5: Accounts Payable Review

### Objective
Ensure all liabilities are recorded and AP balances are accurate.

### Procedure

1. **Aged Payables Report**
   - Run the Aged Payable report via Accounting > Reporting > Partner Ledger
   - Review for overdue items that need immediate payment
   - Identify early payment discount opportunities

2. **Vendor Statement Reconciliation**
   - Reconcile vendor statements received against Odoo AP balances
   - Investigate and resolve discrepancies
   - Common issues: missing bills, duplicate entries, payment not recorded

3. **Accrued Liabilities**
   - Review accrual accounts for completeness:
     - Accrued salaries and wages
     - Accrued utilities
     - Accrued professional fees
     - Accrued taxes (BIR withholding, VAT payable)
   - Post adjusting entries for any missing accruals

4. **Verify Payment Schedule**
   - Review upcoming payments for the next 7 days
   - Ensure cash is available for scheduled payments
   - Flag any payments that need management approval

### Verification
- Total AP per aged report matches the AP general ledger balance
- No bills dated in the period remain in draft status

---

## Step 6: Inventory Reconciliation (If Applicable)

### Objective
Ensure inventory balances in Odoo match physical stock.

### Procedure

1. **Run Inventory Valuation Report**
   - Navigate to Inventory > Reporting > Inventory Valuation
   - Review total inventory value by category and warehouse

2. **Investigate Discrepancies**
   - Compare Odoo stock quantities to physical counts (if performed)
   - Process inventory adjustments for any differences found
   - Document the reason for each adjustment

3. **Review Landed Costs**
   - Verify all landed costs (freight, customs, insurance) are allocated to receipts
   - Post any pending landed cost entries

4. **Slow-Moving and Obsolete Stock**
   - Run the stock turnover report
   - Identify items with zero movement in 90+ days
   - Determine if a write-down or provision is needed

### Verification
- Inventory Valuation total matches the Inventory general ledger account
- All inventory adjustments are approved and documented

---

## Step 7: Fixed Asset Depreciation

### Objective
Record monthly depreciation for all fixed assets.

### Procedure

1. **Run Depreciation**
   - Navigate to Accounting > Assets
   - Use the OCA `account_asset_management` module
   - Select the period and click "Create Depreciation Entries"
   - Review the generated entries before posting

2. **New Asset Registration**
   - Verify all assets purchased during the period are registered
   - Confirm asset category, useful life, and salvage value
   - Validate the depreciation method (straight-line is standard for Philippine tax)

3. **Asset Disposals**
   - Process any assets sold or retired during the period
   - Record gain or loss on disposal
   - Remove asset from the register

### Verification
- Total depreciation expense matches the asset schedule total
- Net book values are positive and reasonable
- New assets in the period are properly categorized

---

## Step 8: Tax Computation and Compliance

### Objective
Compute tax liabilities and prepare for BIR filing.

### Procedure

1. **VAT Computation**
   - Run the Tax Balance report (OCA `account_tax_balance`)
   - Verify output VAT from sales and input VAT from purchases
   - Calculate net VAT payable or creditable
   - Prepare BIR Form 2550M data (monthly VAT return)

2. **Withholding Tax**
   - Review all payments made with withholding tax
   - Verify EWT and FWT deductions are correctly computed
   - Prepare BIR Form 1601-EQ data (quarterly remittance)
   - For compensation: verify 1601-C data (monthly)

3. **Income Tax Provision**
   - Calculate estimated quarterly income tax
   - Post provision entry:
     - Debit: Income Tax Expense
     - Credit: Income Tax Payable

4. **Tax Account Reconciliation**
   - Reconcile all tax-related accounts:
     - VAT Payable
     - Input VAT
     - Withholding Tax Payable
     - Income Tax Payable
   - Balances must tie to supporting schedules

### Verification
- VAT payable per books matches Form 2550M computation
- Withholding tax payable per books matches Form 1601-C / 1601-EQ totals
- All tax accounts have supporting detail schedules

---

## Step 9: Inter-Company Eliminations (Multi-Company)

### Objective
Eliminate inter-company transactions for consolidated reporting.

### Procedure

1. **Identify Inter-Company Transactions**
   - Run partner ledger filtered by inter-company partners
   - Verify that each inter-company transaction has a matching entry in both companies

2. **Reconcile Inter-Company Balances**
   - IC receivable in Company A must equal IC payable in Company B
   - Investigate and resolve any mismatches

3. **Post Elimination Entries** (for consolidated reporting only)
   - Eliminate inter-company revenue and expense
   - Eliminate inter-company receivable and payable
   - Eliminate inter-company profit on inventory transfers

### Verification
- Net inter-company balance across all companies is zero
- Elimination journal entries are balanced

---

## Step 10: Financial Report Generation

### Objective
Generate final financial reports for the period.

### Procedure

1. **Trial Balance**
   - Run via OCA `account_financial_report`
   - Verify total debits equal total credits
   - Review for unusual balances or unexpected accounts

2. **Income Statement**
   - Generate via MIS Builder or financial report module
   - Compare to prior period and budget
   - Document significant variances (>10%)

3. **Balance Sheet**
   - Generate as of period end date
   - Verify balance sheet equation: Assets = Liabilities + Equity
   - Review for classification accuracy

4. **Cash Flow Statement**
   - Generate from journal entries (indirect method)
   - Verify opening cash + net cash flow = closing cash
   - Closing cash must match reconciled bank balances

### Verification
- Trial balance is balanced (debits = credits)
- Balance sheet balances (A = L + E)
- Cash flow ending balance matches bank reconciliation

---

## Step 11: Period Lock

### Objective
Prevent further changes to the closed period.

### Procedure

1. **Final Review**
   - Finance Manager reviews all reports and reconciliations
   - All outstanding items from the checklist above are resolved

2. **Lock the Period**
   - Navigate to Accounting > Configuration > Settings
   - Use OCA `account_journal_lock_date` to lock individual journals
   - Set the Lock Date for Non-Advisors to the period end date
   - Set the Lock Date for All Users to the period end date (after all adjustments)

3. **Archive Documentation**
   - Save PDF copies of all financial reports to the document management system
   - Attach bank reconciliation reports
   - Archive the completed checklist with sign-offs

### Verification
- Period lock date is set correctly
- Attempting to post an entry in the locked period returns an error
- All reports are archived and accessible

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Preparer | _____________ | _____________ | _____________ |
| Reviewer | _____________ | _____________ | _____________ |
| Finance Manager | _____________ | _____________ | _____________ |

---

## Appendix: Odoo Navigation Quick Reference

| Action | Navigation Path |
|--------|----------------|
| Post draft invoices | Accounting > Customers > Invoices > Filter: Draft |
| Bank reconciliation | Accounting > Bank > Reconciliation |
| Aged receivable | Accounting > Reporting > Aged Receivable |
| Aged payable | Accounting > Reporting > Aged Payable |
| Trial balance | Accounting > Reporting > Trial Balance |
| Tax balance | Accounting > Reporting > Tax Balance |
| Asset depreciation | Accounting > Assets > Run Depreciation |
| Lock period | Accounting > Configuration > Settings > Lock Dates |
| Journal entries | Accounting > Accounting > Journal Entries |
| MIS Report | Accounting > Reporting > MIS Reports |
