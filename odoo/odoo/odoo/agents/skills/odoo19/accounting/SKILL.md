---
name: accounting
description: Full-featured double-entry accounting with invoicing, bank reconciliation, taxes, payments, and financial reporting.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# accounting — Odoo 19.0 Skill Reference

## Overview

Odoo Accounting is a comprehensive double-entry bookkeeping system supporting accrual and cash basis accounting, multi-currency, multi-company, and branch structures. It covers the full lifecycle: chart of accounts setup, customer invoicing, vendor bill management, bank reconciliation, tax management, payment processing, and financial reporting. The standalone Invoicing app provides a subset (invoice/bill creation and payments) without full accounting features. Fiscal localization packages auto-configure country-specific charts of accounts, taxes, and reports.

## Key Concepts

- **Chart of Accounts (COA)**: Hierarchical list of all accounts (assets, liabilities, equity, income, expense) identified by code and type. Determines report placement and fiscal year closing behavior.
- **Journal**: Organized ledger for a transaction category. Six types: Bank, Cash, Credit Card, Sales, Purchase, Miscellaneous. Each has a short code (1-5 chars) used as entry prefix.
- **Journal Entry**: Double-entry record where total debits equal total credits. Every financial document (invoice, bill, payment, expense) produces journal entries.
- **Account Types**: Receivable, Payable, Bank and Cash, Current Assets/Liabilities, Non-current Assets/Liabilities, Fixed Assets, Prepayments, Credit Card, Equity, Current Year Earnings, Income, Other Income, Expense, Depreciation, Cost of Revenue, Off-Balance Sheet.
- **Fiscal Position**: Rules that automatically map taxes and accounts based on customer/vendor location or business type. Can be auto-detected (by VAT/country) or manually assigned.
- **Reconciliation**: Matching journal items (invoices, payments, bank transactions) to validate and mark as paid. Automatic matching uses exact, discounted, tolerance, currency, and label-amount rules.
- **Reconciliation Model**: Custom rules for recurring reconciliation operations (e.g., bank fees). Can be automatic or manual button-triggered.
- **Outstanding Accounts**: Intermediate accounts (receipts/payments) where registered payments sit until reconciled with bank transactions. Configured per payment method on bank/cash journals.
- **Suspense Account**: Temporary holding account for bank transactions until reconciled.
- **Tax Grids**: Tags on journal items linking them to specific lines in the Tax Return report.
- **Payment Terms**: Define installment schedules and due dates for invoices/bills.
- **Analytic Accounting**: Cost/revenue tracking across projects, departments, or other dimensions via analytic accounts organized in analytic plans.
- **Deferred Revenue / Expense**: Spreading income or cost recognition over multiple periods.
- **Lock Date**: Prevents modification of posted entries on or before a given date. "Hard Lock" is irreversible.

## Core Workflows

### 1. Create and Send a Customer Invoice

1. Go to Accounting > Customers > Invoices, click New.
2. Select Customer, set Invoice Date, Due Date/Payment Terms, Journal, Currency.
3. In Invoice Lines tab, add products with Quantity, Price, Taxes.
4. Click Confirm to post (status: Posted, journal entry created, sequence number assigned).
5. Click Send, choose sending method (email, download), click Send/Download.
6. Invoice is delivered; status remains Posted until payment reconciliation marks it Paid.

### 2. Register and Reconcile a Vendor Bill

1. Go to Accounting > Vendors > Bills, click New (or upload PDF / email to alias for OCR digitization).
2. Fill Vendor, Bill Reference, Bill Date, Due Date/Payment Terms, Journal.
3. Add invoice lines (products, quantities, taxes).
4. Click Confirm (status: Posted).
5. Click Pay, select Journal, Payment Method, Amount, click Create Payment (status: In Payment).
6. When bank statement arrives, reconcile the payment with the bank transaction (status: Paid).

### 3. Bank Reconciliation

1. From Accounting Dashboard, click bank journal name or "x to reconcile" button.
2. Bank Matching view shows unreconciled transactions with suggested action buttons.
3. For each transaction: click Reconcile to match with existing invoice/bill/payment, or Set Account to write off manually, or use a reconciliation model button.
4. If partial match, remaining balance stays open for future reconciliation.
5. Fully matched transactions replace the suspense account with the matched counterpart account.

### 4. Configure and Apply Taxes

1. Go to Accounting > Configuration > Taxes. Activate needed pre-configured taxes.
2. Set default Sales Tax and Purchase Tax in Settings > Taxes.
3. Assign taxes on products (Sales Taxes / Purchase Taxes fields).
4. Configure fiscal positions (Accounting > Configuration > Fiscal Positions) with tax mapping rules to auto-swap taxes by customer location.
5. Tax Return report (Accounting > Reporting > Tax Report) aggregates base and tax amounts per period for filing.

### 5. Year-End Closing

1. Reconcile all bank accounts up to year-end; verify ending balances match statements.
2. Confirm all draft invoices/bills are posted or cancelled.
3. Book all depreciation, deferred revenue/expense entries, and loan amortization.
4. Run Tax Report, verify correctness.
5. Set Lock Everything date (Accounting > Accounting > Lock Dates).
6. Allocate current year earnings to equity via miscellaneous entry.
7. Review annual closing checks, validate, and submit.
8. Optionally set Hard Lock date (irreversible).

## Technical Reference

### Key Models

| Model | Purpose |
|-------|---------|
| `account.move` | Invoices, bills, credit notes, journal entries |
| `account.move.line` | Individual journal item lines |
| `account.account` | Chart of accounts entries |
| `account.journal` | Journals (bank, sales, purchase, misc) |
| `account.tax` | Tax definitions |
| `account.tax.group` | Tax grouping for display |
| `account.fiscal.position` | Tax and account mapping rules |
| `account.payment` | Payment records |
| `account.bank.statement` | Imported bank statements |
| `account.bank.statement.line` | Individual bank transactions |
| `account.reconcile.model` | Reconciliation model rules |
| `account.analytic.account` | Analytic accounts |
| `account.analytic.plan` | Analytic plan groupings |
| `account.analytic.distribution.model` | Auto-distribution rules |

### Key Fields on `account.move`

- `move_type`: `entry`, `out_invoice`, `out_refund`, `in_invoice`, `in_refund`, `out_receipt`, `in_receipt`
- `state`: `draft`, `posted`, `cancel`
- `payment_state`: `not_paid`, `in_payment`, `paid`, `partial`, `reversed`
- `journal_id`, `partner_id`, `invoice_date`, `date`, `currency_id`
- `amount_total`, `amount_residual`, `amount_tax`
- `fiscal_position_id`, `invoice_payment_term_id`

### Key Fields on `account.account`

- `code`: Unique account code
- `name`: Account name
- `account_type`: Determines report classification (receivable, payable, asset_current, etc.)
- `reconcile`: Boolean, allows reconciliation
- `deprecated`: Boolean, marks as unusable
- `currency_id`: Forces account to specific currency
- `tag_ids`: Tags for reporting (tax grids)

### Important Menu Paths

- Chart of Accounts: Accounting > Configuration > Chart of Accounts
- Journals: Accounting > Configuration > Journals
- Taxes: Accounting > Configuration > Taxes
- Fiscal Positions: Accounting > Configuration > Fiscal Positions
- Payment Providers: Accounting > Configuration > Payment Providers
- Analytic Accounts: Accounting > Configuration > Analytic Accounts
- Lock Dates: Accounting > Accounting > Lock Dates
- Reconcile: Accounting > Accounting > Reconcile
- All Reports: Accounting > Reporting > (Balance Sheet, Profit and Loss, General Ledger, etc.)

### Reports Available

**Statement**: Balance Sheet, Profit and Loss, Cash Flow Statement, Executive Summary, Tax Return, EC Sales List.
**Audit**: General Ledger, Trial Balance, Journal Audit, Intrastat Report, Check Register.
**Partner**: Partner Ledger, Aged Receivable, Aged Payable.
**Management**: Invoice Analysis, Analytic Report, Audit Trail, Budget Report, Unrealized Currency Gains/Losses, Deferred Revenue, Deferred Expense, Depreciation Schedule, Disallowed Expenses, Loans Analysis, Product Margins, 1099 Report.

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

- **Tax mapping on taxes**: In 19.0, fiscal position tax mapping is configured directly on tax records (via `Fiscal Position` and `Replaces` fields), not on the fiscal position form itself. This is a significant change from prior versions where mapping was defined in the fiscal position's Tax Mapping tab.
- **Annual Closing workflow**: Structured review-and-submit process with automated validation checks (bank reconciliation, draft entries, deferred entries, earnings allocation, fixed assets, loans, overdue receivables/payables).
- **Lock Date exceptions**: Administrators can create time-limited exceptions to lock dates for specific users or all users, with reason logging.
- **Hard Lock date**: New irreversible lock mechanism for inalterability compliance.
- **Invoice sending methods**: Configurable per-customer preferred sending method; batch send-and-print with progress banner.
- **Accounting Firms mode**: Quick encoding option for customer invoices and vendor bills.
- **Shared Accounts**: Cross-company account sharing in multi-company environments.
- **Auto-post bills**: Per-vendor setting (Always / Ask after 3 validations / Never).

## Common Pitfalls

- **Fiscal localization cannot be changed** once a journal entry has been posted. Choose the correct package at database/company creation.
- **Outstanding accounts must be configured** on bank/cash journal payment methods for payment registration to create journal entries. Without them, no journal entry is created and the payment cannot be matched.
- **Secure Posted Entries with Hash** cannot be removed from a journal once any entry has been posted to that journal.
- **Tax mapping only works with active taxes**. Inactive taxes in fiscal position mappings will not apply.
- **Reconciliation models and automatic matching** depend on correct partner assignment on bank transactions. Missing partners cause the system to fall back to label-based matching, which may be less accurate.
