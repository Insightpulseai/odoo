---
title: "Year-End Close Procedure"
kb_scope: "finance-close-kb"
group_ids: ["group-guid-placeholder"]
last_updated: "2026-03-15"
---

# Year-End Close Procedure

## Overview

The year-end close is the culmination of 12 monthly closes and includes additional steps for fiscal year rollover, retained earnings computation, audit preparation, and annual BIR compliance. This procedure assumes all monthly closes for the fiscal year have been completed per the Month-End Close Checklist.

**Timeline**: Year-end close should be completed within 30 calendar days of fiscal year end (typically January 31 for a December fiscal year).

**Philippine Regulatory Deadlines**:
- Annual Income Tax Return (BIR Form 1702): April 15 of the following year
- Annual Information Return (BIR Form 1604-CF, 1604-E): January 31
- Audited Financial Statements (for companies with gross sales > PHP 3M): April 15

---

## Prerequisites

Before starting the year-end close:

- [ ] All 12 monthly closes are completed and locked through November
- [ ] December month-end close is in progress or completed
- [ ] All bank accounts are reconciled through December 31
- [ ] Physical inventory count has been performed (if applicable)
- [ ] All payroll for the year has been processed, including 13th month pay
- [ ] All BIR monthly and quarterly returns for the year are filed
- [ ] External auditor engagement letter is signed (if applicable)

---

## Step 1: Complete December Month-End Close

Follow the standard Month-End Close Checklist for December with these additional considerations:

### December-Specific Items

1. **13th Month Pay**
   - Verify 13th month pay has been computed and recorded
   - Philippine law requires payment on or before December 24
   - Post the liability if not yet paid:
     - Debit: 13th Month Pay Expense
     - Credit: 13th Month Pay Payable

2. **Year-End Bonuses**
   - Record performance bonuses and other year-end incentives
   - Accrue if declared but not yet paid

3. **Holiday Pay and Overtime**
   - Ensure December holiday pay differentials are recorded
   - Philippine regular holidays: Dec 25 (Christmas), Dec 30 (Rizal Day), Dec 31 (Last Day of Year — special non-working)

4. **Inventory Count Adjustments**
   - Post adjustments from the annual physical inventory count
   - Investigate and document variances exceeding 1% of category value

---

## Step 2: Year-End Adjusting Entries

### Depreciation True-Up

1. Review the full-year depreciation schedule
2. Verify that 12 months of depreciation have been recorded for each asset
3. For assets acquired mid-year, verify pro-rata depreciation
4. For assets disposed mid-year, verify depreciation through disposal date
5. Reconcile the asset register total to the general ledger:
   - Fixed Asset accounts (gross)
   - Accumulated Depreciation accounts
   - Net Book Value = Gross - Accumulated

### Prepaid Expense True-Up

1. Review all prepaid expense accounts
2. Verify that the correct number of amortization entries have been posted
3. Remaining prepaid balance should represent future periods only
4. Common prepaid items:
   - Insurance (fire, general liability, vehicle)
   - Rent deposits and advance rent
   - Annual software subscriptions
   - Professional membership fees

### Accrued Expense True-Up

1. Review all accrued expense accounts
2. Verify that December accruals are posted:
   - Accrued salaries and wages (for pay periods crossing year-end)
   - Accrued utilities (December bills typically arrive in January)
   - Accrued interest on loans
   - Accrued professional fees (audit, legal, consulting)
   - Accrued property taxes
3. Reverse prior month accruals that have been billed

### Allowance for Doubtful Accounts

1. Run the final aged receivable report as of December 31
2. Apply the allowance percentages per company policy
3. Compare the computed allowance to the existing balance
4. Post the adjusting entry:
   - Debit: Bad Debt Expense
   - Credit: Allowance for Doubtful Accounts
5. Write off any accounts deemed uncollectible per management approval

### Foreign Currency Revaluation

1. Obtain BSP closing rates as of December 31 for all foreign currencies held
2. Revalue foreign currency bank accounts:
   - Debit/Credit: Bank Account (at new rate)
   - Credit/Debit: Foreign Exchange Gain/Loss
3. Revalue foreign currency receivables and payables similarly
4. Use the OCA `currency_rate_update` module to update rates
5. Document the rates used and their source

### Inventory Valuation Adjustment

1. Review inventory for write-down candidates:
   - Items with net realizable value below cost
   - Damaged or obsolete items identified during physical count
   - Slow-moving items (no sales in 12+ months)
2. Post write-down entries:
   - Debit: Inventory Write-Down Expense
   - Credit: Inventory (or Inventory Valuation Allowance)

---

## Step 3: Income Tax Computation

### Regular Corporate Income Tax (RCIT)

1. Compute taxable income:
   - Start with accounting net income before tax
   - Add back non-deductible expenses (entertainment > 0.5% of net revenue, penalties, donations > limits)
   - Subtract non-taxable income (if any)
   - Result: Taxable Income

2. Apply the tax rate:
   - Standard RCIT rate: 25% (for taxable income > PHP 5M and total assets > PHP 100M)
   - Reduced rate: 20% (for net taxable income <= PHP 5M AND total assets <= PHP 100M, excluding land)

3. Compare with Minimum Corporate Income Tax (MCIT):
   - MCIT rate: 1% of gross income (effective from 4th year of operations)
   - Pay the higher of RCIT or MCIT
   - Excess MCIT can be carried forward and credited against RCIT for 3 years

4. Post the income tax provision:
   - Debit: Income Tax Expense (current)
   - Credit: Income Tax Payable
   - Adjust for quarterly payments already made (creditable withholding taxes, quarterly ITR payments)

### Deferred Tax Computation

1. Identify temporary differences:
   - Depreciation timing differences (tax vs. book useful lives)
   - Allowance for doubtful accounts (deductible only when written off for tax)
   - Unrealized foreign exchange gains/losses
   - Accrued expenses not yet paid
2. Compute deferred tax asset/liability at the applicable rate
3. Post the adjustment:
   - Debit: Deferred Tax Asset / Credit: Deferred Tax Benefit (for deductible temporary differences)
   - Debit: Deferred Tax Expense / Credit: Deferred Tax Liability (for taxable temporary differences)

---

## Step 4: Retained Earnings Rollover

### How Odoo Handles Year-End

Odoo CE 19.0 handles the fiscal year rollover automatically:

- **Income and expense accounts** (P&L accounts) are automatically offset to zero when viewing the Balance Sheet for the new fiscal year.
- **The retained earnings account** automatically receives the net income/loss from the prior year.
- **No manual closing entry is required** in the general ledger for P&L accounts.

### What You Must Configure

1. **Fiscal Year Definition**
   - Navigate to Accounting > Configuration > Fiscal Years
   - Verify the current fiscal year dates (January 1 - December 31 for calendar year)
   - Create the new fiscal year if not auto-created

2. **Retained Earnings Account**
   - Navigate to Accounting > Configuration > Settings
   - Verify the "Current Year Earnings" account is set correctly
   - This account must be of type "Current Year Earnings" in the chart of accounts
   - Typically mapped to account code 310100 or similar

3. **Dividends (If Declared)**
   - If dividends are declared, post the entry:
     - Debit: Retained Earnings
     - Credit: Dividends Payable
   - Note: Dividends are subject to 10% final withholding tax (or treaty rate)

### Verification

- Opening balance of Retained Earnings for new year = Prior year closing Retained Earnings + Prior year Net Income - Dividends
- The Balance Sheet as of January 1 of the new year should show zero in income and expense accounts

---

## Step 5: Annual BIR Compliance

### Annual Income Tax Return (Form 1702)

1. Prepare the computation:
   - Gross income from operations
   - Less: Cost of goods sold / Cost of services
   - Gross profit
   - Less: Operating expenses (itemized per BIR schedule)
   - Net income before tax
   - Tax adjustments (non-deductible expenses, non-taxable income)
   - Taxable income
   - Tax due
   - Less: Tax credits (quarterly payments, creditable withholding taxes)
   - Tax payable / (overpayment)

2. Supporting schedules required:
   - Schedule of revenue
   - Schedule of cost of goods sold
   - Schedule of operating expenses (itemized)
   - Schedule of non-operating income
   - Schedule of taxes and licenses
   - Reconciliation of net income per books vs. taxable income

3. Filing deadline: April 15 of the following year
4. Payment: with the return, via eFPS or authorized agent bank

### Annual Information Returns

**Form 1604-CF (Compensation)**
- Summary of all compensation paid and taxes withheld during the year
- Accompanied by alphabetical list of employees (BIR Form 2316)
- Filing deadline: January 31

**Form 1604-E (Expanded Withholding Tax)**
- Summary of all EWT remittances during the year
- Accompanied by alphabetical list of payees
- Filing deadline: March 1

### Withholding Tax Certificates

1. Generate BIR Form 2307 (Certificate of Creditable Tax Withheld) for all vendors
2. Generate BIR Form 2316 (Certificate of Compensation) for all employees
3. Distribute certificates by:
   - 2307: To vendors, on or before the 20th of the month following the quarter
   - 2316: To employees, on or before January 31

---

## Step 6: Audit Preparation (If Applicable)

### Required by Law When:
- Gross quarterly sales exceed PHP 3,000,000 (for VAT registration)
- SEC-registered corporations (annual audited FS)
- Cooperatives, foundations, and other regulated entities

### Audit Working Papers

Prepare the following for the external auditor:

1. **Trial Balance** — Year-end trial balance with prior year comparison
2. **Bank Reconciliations** — All accounts, December 31
3. **AR Aging** — With allowance computation
4. **AP Aging** — With accrual listing
5. **Inventory Listing** — With valuation and count sheets
6. **Fixed Asset Schedule** — Additions, disposals, depreciation
7. **Prepaid Schedule** — All prepaid accounts with amortization
8. **Loan Schedule** — All borrowings with payment terms and balances
9. **Equity Rollforward** — Capital stock, APIC, retained earnings, dividends
10. **Tax Computation** — RCIT/MCIT computation with supporting schedules
11. **Related Party Transactions** — All inter-company balances and transactions
12. **Subsequent Events** — Significant events between year-end and audit date

### Audit Adjustments

- External auditors may propose adjusting entries
- All audit adjustments must be reviewed and approved by the Finance Manager
- Post approved adjustments as a separate batch with journal reference "Audit Adj YYYY"
- Re-run financial reports after audit adjustments

---

## Step 7: Lock the Fiscal Year

### Procedure

1. **Final Verification**
   - All adjusting entries posted (including audit adjustments)
   - All reports generated and archived
   - All BIR returns prepared
   - Finance Manager and auditor sign-off obtained

2. **Lock the Period**
   - Set the Fiscal Year Lock Date to December 31
   - Navigate to Accounting > Configuration > Settings
   - Set "Lock Date for Non-Advisors" to December 31
   - Set "Lock Date for All Users" to December 31 (only after all audit adjustments)

3. **Archive**
   - Save final financial statements (PDF and Excel)
   - Save all supporting schedules
   - Save BIR return computations
   - Archive the completed checklist with sign-offs
   - Store in the document management system: `Finance > Year-End > YYYY`

### Verification
- No entries can be posted to the locked fiscal year
- Financial reports for the closed year are finalized
- New fiscal year is open and accepting entries

---

## Year-End Close Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Preparer | _____________ | _____________ | _____________ |
| Senior Accountant | _____________ | _____________ | _____________ |
| Finance Manager | _____________ | _____________ | _____________ |
| External Auditor | _____________ | _____________ | _____________ |
| CFO / CEO | _____________ | _____________ | _____________ |

---

## Timeline Summary

| Deadline | Task |
|----------|------|
| Jan 5 | December month-end close completed |
| Jan 15 | Year-end adjusting entries posted |
| Jan 20 | Income tax computation completed |
| Jan 31 | Form 1604-CF filed, Form 2316 distributed |
| Feb 15 | Audit field work begins (if applicable) |
| Mar 1 | Form 1604-E filed |
| Mar 15 | Audit completed, adjustments posted |
| Mar 31 | Fiscal year locked |
| Apr 15 | Annual ITR (Form 1702) filed, Audited FS submitted to BIR/SEC |
