---
title: "Bank Reconciliation and Payment Matching Guide"
kb_scope: "finance-close-kb"
group_ids: ["group-guid-placeholder"]
last_updated: "2026-03-15"
---

# Bank Reconciliation and Payment Matching Guide

## Overview

Bank reconciliation is the process of matching transactions recorded in Odoo with transactions on the bank statement. This guide covers the reconciliation workflow in Odoo CE 18.0 using the OCA `account_reconcile_oca` module, including Philippine bank-specific considerations.

Reconciliation should be performed at least monthly, but weekly reconciliation is recommended for high-volume accounts.

---

## Bank Account Setup

### Configuring Bank Accounts in Odoo

Each bank account your company operates must be registered in Odoo:

1. **Create the Bank Journal**
   - Navigate to Accounting > Configuration > Journals
   - Create a new journal with Type = Bank
   - Set the journal code (e.g., BDO1, BPI1, MBK1)

2. **Link the Bank Account**
   - In the journal configuration, set the Bank Account field
   - Enter the account number, bank name, and BIC/SWIFT code
   - For Philippine banks:
     - BDO: BNORPHMM
     - BPI: BABORPHMM
     - Metrobank: MABORPHMM
     - Landbank: TLBPPHM1
     - PNB: PNBMPHMM

3. **Map to General Ledger Account**
   - Each bank journal maps to a GL account (e.g., 101001 - BDO Savings)
   - The GL account type must be "Bank and Cash"
   - Currency: PHP for local accounts, USD/EUR for foreign currency accounts

### Chart of Accounts — Bank Accounts

| Account Code | Account Name | Currency | Bank |
|:-------------|:-------------|:---------|:-----|
| 101001 | BDO Savings - Operating | PHP | BDO |
| 101002 | BDO Savings - Payroll | PHP | BDO |
| 101003 | BPI Current - Operating | PHP | BPI |
| 101004 | Metrobank Savings | PHP | Metrobank |
| 101010 | BDO Dollar Account | USD | BDO |
| 101020 | BPI Dollar Account | USD | BPI |
| 100001 | Petty Cash Fund | PHP | N/A |

---

## Bank Statement Import

### Supported Formats

| Bank | Format | Method |
|------|--------|--------|
| BDO | CSV (custom layout) | Manual download from BDO Corporate Online |
| BPI | CSV | Manual download from BPI Express Online |
| Metrobank | CSV | Manual download from Metrobank Direct |
| Landbank | OFX | Manual download from LBP iAccess |
| Any bank | MT940 | If supported by the bank |
| Any bank | OFX/QFX | Quicken format, widely supported |

### Import Procedure

1. **Download the Statement**
   - Log in to your bank's online portal
   - Download the statement for the reconciliation period
   - Ensure the date range matches your reconciliation period exactly
   - Save in the appropriate format (CSV or OFX)

2. **Import into Odoo**
   - Navigate to Accounting > Bank > Bank Statements
   - Click "Import" and select the downloaded file
   - Map columns if using CSV (date, description, amount, reference)
   - Review the preview and confirm the import
   - Odoo creates statement lines for each transaction

3. **Verify Import**
   - Check the total number of transactions imported
   - Verify the opening balance matches the prior statement's closing balance
   - Verify the closing balance matches the bank statement

### Manual Entry

For banks without electronic statement download, enter statement lines manually:

1. Navigate to Accounting > Bank > Bank Statements
2. Create a new statement
3. Set the date, opening balance, and closing balance
4. Add lines manually with: date, description, partner (if known), amount

---

## Reconciliation Process

### Automatic Matching

The OCA `account_reconcile_oca` module provides intelligent automatic matching:

1. **Navigate to Reconciliation**
   - Accounting > Bank > Reconciliation
   - Select the bank journal to reconcile

2. **Matching Rules**
   - The module attempts to match statement lines to journal items using:
     - **Perfect match**: Reference number matches exactly
     - **Amount match**: Amount matches within tolerance, date within range
     - **Partner match**: Partner name in statement description matches a known partner
     - **Combined match**: Partial reference + amount + partner

3. **Review Matches**
   - Green: High-confidence automatic match (review quickly)
   - Yellow: Partial match (review carefully)
   - Red: No match found (requires manual action)

4. **Accept or Reject**
   - Click "Validate" to accept a proposed match
   - Click "Reset" to reject and try a different match
   - Use bulk validation for high-confidence matches

### Manual Matching

For unmatched statement lines:

1. **Search for the Matching Entry**
   - Use the search panel to find journal items by amount, date, or reference
   - Odoo shows candidate matches from open (unreconciled) journal items

2. **Match to Existing Entry**
   - Select the matching journal item(s)
   - If the amounts differ (e.g., bank charges deducted), add a write-off line
   - Validate the match

3. **Create New Entry**
   - If no matching journal item exists, create one directly:
     - For bank charges: create an expense entry
     - For interest income: create an income entry
     - For unidentified deposits: create a suspense entry and investigate
     - For returned checks: reverse the original payment entry

### Common Reconciliation Scenarios

#### Scenario 1: Customer Payment Received

**Bank statement**: "DEPOSIT - ABC CORP - REF 20260315 - PHP 50,000.00"

**Action**: Match to the customer payment registered in Odoo for invoice INV/2026/0042.

If the payment was not registered:
1. Create a payment from the reconciliation screen
2. Select partner: ABC Corp
3. Odoo will propose open invoices to apply the payment to
4. Select the invoice(s) and validate

#### Scenario 2: Vendor Payment Cleared

**Bank statement**: "CHECK 001234 - PHP 25,000.00"

**Action**: Match to the vendor payment journal entry created when the check was issued.

If the check number is in the payment reference, automatic matching should work. If not, search by amount and date range.

#### Scenario 3: Bank Service Charges

**Bank statement**: "SERVICE CHARGE - PHP 500.00"

**Action**: No matching entry exists. Create a new journal entry:
- Debit: Bank Charges (expense account, e.g., 641001)
- Credit: Bank Account (automatic, as it is a bank statement line)

#### Scenario 4: Payroll Debit

**Bank statement**: "PAYROLL BATCH 2026-03-15 - PHP 1,200,000.00"

**Action**: Match to the payroll journal entry. If payroll is posted to a payroll clearing account, match the bank line to the clearing account transfer.

#### Scenario 5: Foreign Currency Transaction

**Bank statement (USD account)**: "WIRE TRANSFER IN - USD 10,000.00"

**Action**: Match to the expected receipt. Odoo will compute the exchange rate difference and post a gain/loss entry automatically if the rate at payment differs from the rate at invoice.

#### Scenario 6: Partial Payment

**Bank statement**: "TRANSFER - XYZ INC - PHP 30,000.00" (invoice is PHP 50,000)

**Action**: Register a partial payment against the invoice. The remaining PHP 20,000 stays as an open balance on the invoice.

#### Scenario 7: GCash/Maya Transfers

**Bank statement**: "GCASH TRANSFER - PHP 15,000.00"

**Action**: Match to the GCash collection journal entry. If using the `ipai_finance_ppm` module, GCash collections are tracked in a separate journal and settled to the bank account.

---

## Aging Reports

### Accounts Receivable Aging

The AR aging report shows outstanding customer invoices grouped by how overdue they are.

**Running the Report:**
1. Navigate to Accounting > Reporting > Aged Receivable
2. Set the "As of" date (typically period end)
3. Select aging buckets: Current, 1-30, 31-60, 61-90, 90+ days
4. Choose grouping: by partner, by salesperson, by customer category

**Interpreting the Report:**

| Bucket | Meaning | Action |
|--------|---------|--------|
| Current | Not yet due | Monitor |
| 1-30 days | Recently overdue | Send reminder |
| 31-60 days | Significantly overdue | Follow up call + formal letter |
| 61-90 days | Seriously overdue | Escalate to management |
| 90+ days | Critically overdue | Consider legal action, assess for write-off |

**Philippine Considerations:**
- Prescription period for collection of debts: 10 years (written contracts), 6 years (oral contracts)
- Bad debts are deductible for BIR purposes only when:
  - The debt is actually ascertained to be worthless
  - It has been charged off during the taxable year
  - The taxpayer has exerted efforts to collect

### Accounts Payable Aging

The AP aging report shows outstanding vendor bills grouped by how overdue they are.

**Running the Report:**
1. Navigate to Accounting > Reporting > Aged Payable
2. Set the "As of" date
3. Select aging buckets and grouping

**Prioritization:**
- Identify bills eligible for early payment discounts (e.g., 2/10 net 30)
- Flag critically overdue items that may affect vendor relationships
- Ensure BIR withholding taxes are remitted on time (or the expense becomes non-deductible)

---

## Payment Matching

### Customer Payment Application

When a customer payment is received, it must be applied to specific invoices:

1. **Register Payment**
   - Open the customer invoice
   - Click "Register Payment"
   - Enter the payment amount, date, and journal (bank account)
   - If the payment covers multiple invoices, use the batch payment feature

2. **Batch Payment Application**
   - Navigate to Accounting > Customers > Payments
   - Create a new payment for the partner
   - Select all invoices to apply the payment to
   - Odoo distributes the payment across invoices (oldest first by default)

3. **Overpayment Handling**
   - If the customer pays more than the invoice amount:
     - Option A: Apply as advance payment (credit on account)
     - Option B: Refund the excess amount
   - Advance payments appear as credit in the partner's account

4. **Underpayment Handling**
   - If the customer pays less than the invoice amount:
     - Option A: Partial payment, invoice remains partially open
     - Option B: Write off the difference (for small amounts within tolerance)
   - Write-off threshold should be defined in company policy (e.g., PHP 100)

### Vendor Payment Processing

1. **Schedule Payments**
   - Navigate to Accounting > Vendors > Bills
   - Select bills due for payment
   - Use "Register Payment" for individual bills
   - Use batch payment for multiple bills to the same vendor

2. **Payment Methods**
   - Check: Create check entry, print check, record check number
   - Bank transfer: Create transfer entry with bank reference
   - GCash/Maya: Record digital payment with transaction reference

3. **Withholding Tax on Payments**
   - When paying a vendor, apply the appropriate withholding tax:
     - 1% EWT on goods
     - 2% EWT on services
     - 5% EWT on professionals (lawyers, CPAs, etc.)
     - 10% EWT on professionals (if income > PHP 3M/year)
     - 15% FWT on non-resident foreign corporations
   - The withheld amount reduces the payment to the vendor
   - Odoo records the withholding as a liability (Withholding Tax Payable)
   - Issue BIR Form 2307 to the vendor

---

## Reconciliation Best Practices

### Frequency

| Account Type | Recommended Frequency |
|-------------|----------------------|
| Operating checking account | Weekly |
| Payroll account | Per payroll cycle |
| Savings accounts | Monthly |
| Petty cash | Weekly |
| Foreign currency accounts | Monthly |
| Credit card statements | Monthly |

### Common Reconciliation Issues

| Issue | Cause | Resolution |
|-------|-------|-----------|
| Timing difference | Check issued but not yet cleared | Normal — will clear in next period |
| Missing deposit | Customer payment not recorded | Create payment entry and match |
| Duplicate entry | Same transaction entered twice | Reverse the duplicate |
| Wrong amount | Data entry error | Correct the journal entry |
| Unknown transaction | Unidentified bank debit or credit | Investigate with bank, post to suspense if needed |
| Currency rounding | Small FX differences on conversion | Write off to FX gain/loss (if within tolerance) |

### Reconciliation Controls

1. **Segregation of Duties**: The person who records payments should not perform reconciliation
2. **Timeliness**: Reconcile within 5 business days of period end
3. **Review**: All reconciliations reviewed by a supervisor
4. **Documentation**: Save reconciliation reports with reviewer sign-off
5. **Outstanding Items**: Items outstanding for more than 90 days require investigation and management approval
6. **Suspense Account**: Balance should be zero at period end. Any remaining items need documented resolution plans.

---

## Petty Cash Reconciliation

### Procedure

1. **Count Physical Cash**
   - Count all bills and coins in the petty cash fund
   - Record the count on the petty cash count sheet

2. **List Outstanding Vouchers**
   - Collect all petty cash vouchers not yet reimbursed
   - Total the voucher amounts

3. **Reconcile**
   - Fund Amount = Physical Cash + Outstanding Vouchers + Unreplenished Expenses
   - Any difference is a shortage (or overage)

4. **Replenish**
   - Submit vouchers for replenishment
   - Post the replenishment entry:
     - Debit: Various expense accounts (per vouchers)
     - Credit: Cash in Bank (replenishment check/transfer)

5. **Record Shortages**
   - If physical cash + vouchers < fund amount:
     - Debit: Cash Shortage Expense
     - Credit: Petty Cash

### Petty Cash Controls

- Maximum single disbursement: PHP 5,000 (or per company policy)
- All disbursements require a signed voucher with receipt
- Fund custodian is personally accountable
- Surprise counts at least quarterly
- Replenish when fund reaches 30% of total

---

## Month-End Reconciliation Checklist

- [ ] All bank statements downloaded and imported
- [ ] Automatic matching run for all bank journals
- [ ] All matched items reviewed and validated
- [ ] Unmatched items investigated and resolved
- [ ] Bank charges and interest recorded
- [ ] Foreign currency accounts revalued (if applicable)
- [ ] Petty cash reconciled and replenished
- [ ] Reconciliation reports generated and saved
- [ ] Reconciliation reviewed by supervisor
- [ ] Outstanding items from prior month resolved
- [ ] Bank GL balance = Reconciled statement balance (zero difference)
