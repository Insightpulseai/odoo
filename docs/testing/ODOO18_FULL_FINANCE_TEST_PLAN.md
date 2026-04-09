# Odoo 18 Finance — Complete Production-Grade Test Plan

**Version**: 1.0  
**Date**: 2026-04-09  
**Scope**: Odoo 18 CE Finance domain — full scenario matrix  
**Authors**: QA / Functional Test Design  
**Status**: Production use

---

## Table of Contents

1. Executive Summary
2. Coverage Map
3. Scenario Matrix
   - A. Finance Configuration and Master Data
   - B. Customer Invoices / AR
   - C. Vendor Bills / AP
   - D. Taxes
   - E. Fiscal Positions
   - F. Payments
   - G. Bank Reconciliation
   - H. Expenses
   - I. Reporting and Auditability
   - J. Permissions and Workflow Controls
   - K. Localization-Sensitive Scenarios
   - L. Negative and Failure Scenarios
4. High-Risk Regression Suite
5. Automation Strategy
6. Test Data Design
7. Localization / Compliance Considerations
8. Gaps and Assumptions
9. Top 25 Finance Scenarios Most Likely to Fail in Production

---

## 1. Executive Summary

### Major Finance Risk Zones

The Odoo 18 Finance domain presents seven high-probability failure zones in real deployments:

**Zone 1 — Tax Calculation Correctness**  
Tax logic in Odoo 18 is configuration-driven. Price-included vs price-excluded, rounding method (per-line vs global), tax group ordering, cash basis timing, and fiscal position mappings each produce distinct journal entry patterns. A single misconfigured tax record produces cascading incorrect ledger entries across every invoice that uses it.

**Zone 2 — Reconciliation and Outstanding Accounts**  
The matching of payments to invoices through outstanding accounts (account.account with reconcile=True) is the most operationally fragile area. Partial payments, currency differences, early payment discounts, write-offs, and manual bank statement entries all interact with the same reconciliation engine. Errors here silently produce incorrect open balances on AR/AP aging reports.

**Zone 3 — Fiscal Position Mapping**  
Fiscal positions that map taxes and accounts are applied at invoice creation time. If the fiscal position is changed after line items are added, Odoo does not always recompute taxes automatically depending on version and module state. Deployments with international vendors/customers are highly exposed to stale fiscal position errors.

**Zone 4 — Cash Basis Tax Timing**  
Cash basis taxes (tax_exigibility = on_payment) do not post the tax journal entry at invoice posting time. They post when the payment is reconciled. This creates a window where the invoice is posted but the tax is not yet in the tax report. Testers frequently miss this because the invoice total appears correct.

**Zone 5 — Payment Term and Installment Correctness**  
Payment terms that produce installments create multiple move lines with different due dates against the receivable/payable account. Each installment is reconciled independently. The sum of all installment lines must equal the invoice total. Rounding differences across installments, especially with tax-included pricing and non-round amounts, produce journal imbalance errors.

**Zone 6 — Expense Reimbursement Flow**  
The expense-to-reimbursement pipeline involves hr.expense, hr.expense.sheet, approval, journal entry posting, and a payment from the company to the employee. The reimbursement journal entry must post against the correct expense accounts and the employee payable account. Mismatches between expense product accounts and the company's chart of accounts are common in fresh deployments.

**Zone 7 — Locked Period and Sequence Integrity**  
Odoo 18 enforces fiscal year lock periods. Attempts to post or modify entries in a locked period must be blocked at the application layer. Sequence integrity (invoice numbering) must be validated. Out-of-sequence numbering after a correction or cancellation is a compliance failure in many jurisdictions.

### Highest-Likelihood Production Failure Areas

1. Tax amount rounding differences between line-level and total-level display
2. Reconciliation leaving non-zero residual amounts due to floating-point handling
3. Cash basis tax entries missing from tax report because reconciliation was not performed
4. Fiscal position not applied to imported invoices / EDI flows
5. Payment term installments not summing correctly after rounding
6. Expense reimbursement journal posting to wrong account due to product misconfiguration
7. Bank statement match creating duplicate payments when statement line was already reconciled
8. Credit note applied against wrong invoice in multi-currency environment
9. Withholding tax not deducted correctly when fiscal position maps to withholding account
10. Locked period bypass through back-dated manual journal entries

---

## 2. Coverage Map

| Area | Sub-area | Why It Matters | Risk Level |
|------|----------|----------------|------------|
| Finance Configuration | Chart of accounts baseline | All transactions post to accounts; missing or misconfigured accounts block posting | Critical |
| Finance Configuration | Journal setup | Each transaction type requires a specific journal; wrong type produces incorrect move sequences | Critical |
| Finance Configuration | Tax setup | Tax amounts, accounts, and timing drive all AR/AP/tax-report correctness | Critical |
| Finance Configuration | Fiscal positions | Determines which taxes and accounts are applied per partner/country | High |
| Finance Configuration | Payment terms | Controls due dates, installments, cash discount windows | High |
| Finance Configuration | Currency setup | Multi-currency requires active currency rates; stale rates produce wrong FX gain/loss | High |
| Finance Configuration | Partner master data | Invoice address, VAT number, fiscal position, payment terms all default from partner | High |
| Finance Configuration | Bank accounts / payment methods | Required for payment registration and bank reconciliation | High |
| Finance Configuration | Fiscal localization | Localization installs country-specific accounts, taxes, and reports | Critical |
| Customer Invoices | Draft creation and posting | Core AR flow; posting creates immutable journal entries | Critical |
| Customer Invoices | Invoice from sales order | SO-to-invoice flow must propagate product, qty, price, tax correctly | High |
| Customer Invoices | Tax handling | Price-included, price-excluded, mixed, no-tax all produce different journal entries | Critical |
| Customer Invoices | Payment terms | Installment lines must match invoice total; due dates must be correct | High |
| Customer Invoices | Cash discounts | Early payment discount reduces tax base in some jurisdictions | High |
| Customer Invoices | Credit notes / refunds | Full and partial credit notes must reconcile correctly | High |
| Customer Invoices | Cash rounding | Rounding difference must post to correct account; invoice total must match payment | Medium |
| Customer Invoices | Multi-currency | Exchange rate at invoice date vs payment date creates FX gain/loss | High |
| Vendor Bills | Draft creation and posting | Core AP flow; mirrors AR with vendor-specific rules | Critical |
| Vendor Bills | Bill from purchase order | PO-to-bill flow must match received quantities and prices | High |
| Vendor Bills | Withholding taxes | Withheld amounts reduce payment; withholding account must be credited | Critical |
| Vendor Bills | Partial and full payment | Payment against specific bill lines; residual tracking | High |
| Vendor Bills | Duplicate reference detection | Odoo should prevent duplicate vendor bill references per partner | Medium |
| Taxes | Single and multiple taxes | Each tax must compute and post to its designated account | Critical |
| Taxes | Price-included vs excluded | Different base computation affects both line totals and tax amounts | Critical |
| Taxes | Tax rounding | Per-line vs global rounding produces different totals; must match legal requirement | High |
| Taxes | Cash basis timing | Tax entry posted at payment, not invoice; timing gap must be handled in reporting | Critical |
| Taxes | Withholding taxes | Reduces amount payable; separate account; must appear in tax report | Critical |
| Taxes | Invalid tax accounts | Missing account blocks posting | High |
| Fiscal Positions | Tax mapping | Incoming tax replaced by mapped tax at line level | Critical |
| Fiscal Positions | Account mapping | Income/expense account substituted per fiscal position | High |
| Fiscal Positions | Auto-detection | Country/state/VAT number triggers automatic fiscal position assignment | Medium |
| Fiscal Positions | Post-draft change | Changing fiscal position after lines are added may leave stale taxes | High |
| Payments | Manual payment | Payment creates journal entry; moves invoice to paid/partial state | Critical |
| Payments | Partial payment | Residual remains on invoice; partial reconciliation | High |
| Payments | Overpayment | Creates credit on partner account; must be tracked and applied | Medium |
| Payments | Early payment discount | Discount taken reduces amount paid; tax adjustment may be required | High |
| Payments | Payment reversal | Reversed payment must unreconcile the invoice | High |
| Bank Reconciliation | Statement import and matching | Statement lines matched to payments/invoices | High |
| Bank Reconciliation | Partial reconciliation | Partial match leaves outstanding amount | High |
| Bank Reconciliation | Write-off | Difference written off to specified account | Medium |
| Bank Reconciliation | Multi-currency | Statement in foreign currency requires FX computation | High |
| Expenses | Employee-paid vs company-paid | Different reimbursement flows and posting accounts | High |
| Expenses | Approval flow | Expense sheet must be approved before posting | High |
| Expenses | Reimbursement | Payment from company to employee; reconciliation | High |
| Expenses | Re-invoicing | Expense recharged to customer must produce correct AR entry | Medium |
| Reporting | Tax report | Must reflect all posted entries for the period; cash basis timing matters | Critical |
| Reporting | AR/AP aging | Open balances must match actual unpaid invoices/bills | Critical |
| Reporting | Audit trail | Every posted move must be traceable to source document | High |
| Reporting | Locked period | No entry can be modified or added in a locked period | High |
| Permissions | Role separation | Accountant, billing, manager, employee roles must enforce access boundaries | High |
| Localization | Country-specific tax / account | Localization installs tax accounts and fiscal positions that override defaults | Critical |
| Localization | Withholding regimes | Philippines BIR, Indian TDS, Brazilian ICMS/ISS require specific withholding logic | Critical |
| Negative / Failure | Missing accounts | Posting must fail with clear error; no silent partial posting | Critical |
| Negative / Failure | Locked period violation | Must be blocked; not produce incorrect entries | Critical |

---

## 3. Scenario Matrix

### Group A — Finance Configuration and Master Data

| ID | Area | Scenario | Preconditions | Steps | Expected Result | Accounting Impact | Automation Candidate |
|----|------|----------|---------------|-------|-----------------|-------------------|----------------------|
| A-001 | Chart of Accounts | Verify default chart of accounts installed by localization | Fiscal localization package installed for target country | 1. Navigate to Accounting > Configuration > Chart of Accounts. 2. Verify account types: receivable, payable, bank, cash, income, expense, tax. 3. Confirm each required account type has at least one account. 4. Check that receivable and payable accounts have reconcile=True | All required account types present; receivable and payable marked reconcile=True; no orphan account types | No transaction impact; configuration baseline verification | Y |
| A-002 | Chart of Accounts | Create a new income account manually | Chart of accounts exists; user has Accountant rights | 1. Navigate to Accounting > Configuration > Chart of Accounts. 2. Click New. 3. Enter account code (e.g., 400100), name, type=Income, default taxes. 4. Save | Account created; available in product income account dropdown; visible in P&L reports | No immediate journal impact; used on future invoice lines | Y |
| A-003 | Chart of Accounts | Attempt to delete an account that has journal items | Account has at least one posted journal item | 1. Navigate to chart of accounts. 2. Select account with posted transactions. 3. Attempt delete | System blocks deletion with error message; account remains | No change | Y |
| A-004 | Chart of Accounts | Verify account type enforcement on journal entry | Account of type Receivable exists | 1. Create a manual journal entry. 2. Attempt to assign a Receivable-type account to a line that is not a customer invoice move line | System should warn or block; receivable accounts should only appear in invoice/payment context | No incorrect entry created | N |
| A-005 | Journals | Verify all required journals exist after localization | Localization installed | 1. Navigate to Accounting > Configuration > Journals. 2. Confirm presence of: Customer Invoices, Vendor Bills, Bank, Cash, Miscellaneous | All journal types present; each has correct type field (sale, purchase, bank, cash, general) | Configuration baseline | Y |
| A-006 | Journals | Create a new bank journal and link it to a bank account | Bank account created in system | 1. Navigate to Accounting > Configuration > Journals. 2. Click New. 3. Set type=Bank, select bank account, set default debit/credit accounts to the bank account. 4. Save | Journal created; appears in bank reconciliation menu; payment journal selector shows this journal | No immediate transaction impact | Y |
| A-007 | Journals | Verify journal sequence integrity after cancellation | Customer invoice journal has existing entries | 1. Post an invoice (gets sequence INV/2026/00001). 2. Reset to draft. 3. Post again. 4. Check sequence number | Odoo 18 locks sequences on posting; reset-to-draft behavior depends on lock_posted_entries setting; verify sequence is not reused or skipped unexpectedly | Sequence integrity; auditable numbering | N |
| A-008 | Journals | Attempt to use a purchase journal for a customer invoice | Purchase journal exists | 1. Create customer invoice. 2. Attempt to change journal to a purchase-type journal | System should either block or produce a warning; invoice posted to wrong journal type creates incorrect report grouping | Configuration guard | Y |
| A-009 | Taxes | Create a standard tax-excluded tax (e.g., 12% VAT) | Chart of accounts with tax account exists | 1. Navigate to Accounting > Configuration > Taxes. 2. New tax: name=VAT 12%, type=Sale, computation=Percent, amount=12, price_include=False. 3. Set tax account to VAT Payable account. 4. Set tax group. 5. Save | Tax created; visible in product/invoice line tax selector; computes correctly on invoice | On invoice posting: debit AR, credit Income + credit Tax Payable | Y |
| A-010 | Taxes | Create a price-included tax (e.g., 10% inclusive) | Chart of accounts with tax account exists | 1. Create tax as above but price_include=True. 2. Apply to invoice line with unit price 110. 3. Verify tax base is 100 and tax amount is 10 | Tax base correctly extracted from price-included amount; invoice total = 110; tax amount = 10; subtotal = 100 | Debit AR 110; credit Income 100; credit Tax Payable 10 | Y |
| A-011 | Taxes | Create a withholding tax (purchase, 2% EWT) | Localization supports withholding taxes; withholding account exists | 1. Create purchase tax: name=EWT 2%, type=Purchase, computation=Percent, amount=-2 (negative), tax account=Withholding Payable. 2. Apply to vendor bill. 3. Verify net payment amount | Invoice total 1000; withholding 20; net payment due = 980; withholding line posts to separate account | Debit Expense 1000; debit Withholding Payable 20; credit AP 980 (depends on localization config) | Y |
| A-012 | Taxes | Create a cash basis tax | Cash basis accounting enabled in company settings | 1. Navigate to company settings, enable cash basis. 2. Create tax with tax_exigibility=on_payment, transition account set. 3. Apply to invoice. 4. Post invoice without payment | At invoice posting: tax amount goes to transition account, not to tax payable. Tax payable only posted when payment is reconciled | Debit AR; credit Income; credit Tax Transition (not Tax Payable) | Y |
| A-013 | Taxes | Tax group ordering with two taxes on same line | Two taxes configured: Tax A applies first, Tax B applies on result of Tax A | 1. Create Tax A (10%) and Tax B (5%, include_base_amount=True to apply on A+base). 2. Apply both to invoice line of 1000. 3. Verify amounts | Tax A = 100; Tax B = 55 (5% of 1100); total = 155; if include_base_amount=False, Tax B = 50 | Each tax posts to its own account | Y |
| A-014 | Fiscal Positions | Create fiscal position with tax mapping | Two taxes exist: Domestic VAT 12%, Export Tax 0% | 1. Navigate to Accounting > Configuration > Fiscal Positions. 2. Create fiscal position Export. 3. Add tax mapping: Domestic VAT 12% → Export Tax 0%. 4. Assign to export customer | When invoice is created for customer with this fiscal position, Domestic VAT 12% is automatically replaced by Export Tax 0% | Invoice posts with 0% tax; no tax payable credit | Y |
| A-015 | Fiscal Positions | Create fiscal position with account mapping | Domestic income account 400100; EU income account 400200 | 1. Add account mapping to fiscal position: 400100 → 400200. 2. Create invoice for EU customer with this fiscal position. 3. Check journal entry | Invoice line credit goes to 400200 instead of 400100 | Income credited to mapped account | Y |
| A-016 | Fiscal Positions | Auto-detection by country | Fiscal position has country=Germany; customer partner has country=Germany | 1. Create customer with country=Germany. 2. Create invoice for this customer. 3. Verify fiscal position auto-assigned | Fiscal position for Germany applied automatically; taxes and accounts mapped accordingly | Mapped taxes/accounts used in journal entry | Y |
| A-017 | Payment Terms | Create 30-day net payment term | None | 1. Navigate to Accounting > Configuration > Payment Terms. 2. Create Net 30: balance due in 30 days. 3. Assign to customer. 4. Create invoice | Invoice due date = invoice date + 30 days; single receivable line on journal entry | One receivable move line with due_date = invoice_date + 30 | Y |
| A-018 | Payment Terms | Create installment payment term (50% now, 50% in 30 days) | None | 1. Create payment term with two lines: 50% on invoice date, 50% in 30 days. 2. Apply to invoice of 1000. 3. Post | Two receivable move lines: 500 due today, 500 due in 30 days; both sum to 1000 | Two debit lines on AR account; each independently reconcilable | Y |
| A-019 | Payment Terms | Payment term with cash discount (2/10 net 30) | None | 1. Create payment term: 2% discount if paid within 10 days, full balance due in 30 days. 2. Apply to invoice of 1000. 3. Verify discount amount | Discount amount = 20; if paid within 10 days, only 980 required; discount posting depends on company policy (early payment discount account required) | On early payment: debit AR 1000, credit Bank 980, credit Discount Expense/Income 20 | Y |
| A-020 | Currencies | Activate foreign currency (USD for EUR company) | Company currency is EUR | 1. Navigate to Accounting > Configuration > Currencies. 2. Activate USD. 3. Set exchange rate (e.g., 1 EUR = 1.08 USD). 4. Create invoice in USD for EUR company | Invoice total in USD; converted to EUR at current rate for journal entry; rate stored on invoice | Journal entry in company currency (EUR); invoice shows both currencies | Y |
| A-021 | Currencies | Stale currency rate detection | USD activated; last rate update > 7 days ago | 1. Create invoice in USD. 2. Check if system warns about stale rate | Odoo may warn about outdated rates depending on configuration; invoice should still be createable but rate accuracy is a compliance risk | Rate used may be incorrect; FX gain/loss will be miscalculated | N |
| A-022 | Partner / Customer Master Data | Create customer with full financial data | None | 1. Create customer: name, VAT number, country, fiscal position, payment terms, AR account override (if applicable), bank account. 2. Create invoice | All defaults from customer applied to invoice (fiscal position, payment terms, AR account) | Correct AR account used; correct payment term applied | Y |
| A-023 | Partner / Customer Master Data | Customer with multiple addresses (invoice vs delivery) | Customer has child contacts | 1. Set invoice address and delivery address on customer. 2. Create invoice. 3. Verify invoice address used on invoice, not delivery address | Invoice address appears on posted invoice PDF; journal entry uses customer master AR account | No accounting impact; compliance/legal document correctness | N |
| A-024 | Partner / Vendor Master Data | Create vendor with withholding tax configured | Withholding tax exists | 1. Create vendor with default purchase taxes including withholding tax. 2. Create bill for this vendor | Withholding tax applied automatically to bill; net payment amount reduced | Withholding posted to correct account | Y |
| A-025 | Employee Master Data | Create employee with expense payment method | Employee exists in HR module | 1. Navigate to Expenses > Configuration. 2. Ensure employee linked to a partner with payable account. 3. Check expense journal configured | Employee payable account exists; expense journal points to correct expense accounts | Reimbursement will debit expense payable account for this employee | Y |
| A-026 | Products / Services | Create service product with income account and tax | Income account and sales tax configured | 1. Create product: type=Service, income account=400100, taxes=[VAT 12%]. 2. Add to invoice | Product defaults income account and tax on invoice line; correct accounts used | Invoice line credits 400100; tax credits Tax Payable | Y |
| A-027 | Products / Services | Create expense product with expense account | Expense account configured | 1. Create product: type=Service, expense account=600100, purchase taxes=[VAT 12%]. 2. Add to vendor bill | Product defaults expense account and tax on bill line | Bill line debits 600100; tax posts to Tax Receivable (input VAT) | Y |
| A-028 | Bank Accounts | Link company bank account to bank journal | Bank journal exists | 1. Navigate to Accounting > Configuration > Journals > Bank. 2. Add bank account number. 3. Verify account appears in payment method list | Bank account linked; visible in payment form when bank journal selected | No immediate accounting impact | Y |
| A-029 | Fiscal Localization | Install Philippines localization and verify installed accounts | Odoo 18 CE with l10n_ph module | 1. Install l10n_ph. 2. Verify chart of accounts, taxes (VAT 12%, EWT rates), fiscal positions created. 3. Check BIR-specific account codes | All BIR-mandated accounts present; EWT tax objects created; VAT output/input accounts present | Baseline for all PH-specific scenarios | Y |
| A-030 | Invalid / Missing Setup | Attempt to post invoice when no income account on product | Product with no income account; no default fallback configured | 1. Create invoice line with this product. 2. Attempt to post | System should raise error: missing account; posting blocked | No incomplete entry created | Y |

---

### Group B — Customer Invoices / AR

| ID | Area | Scenario | Preconditions | Steps | Expected Result | Accounting Impact | Automation Candidate |
|----|------|----------|---------------|-------|-----------------|-------------------|----------------------|
| B-001 | Customer Invoice | Create and post a basic single-line invoice | Customer, product, income account, VAT 12% tax configured | 1. Navigate to Accounting > Customers > Invoices. 2. New invoice. 3. Select customer. 4. Add one line: product, qty=1, price=1000, tax=VAT 12%. 5. Confirm | Invoice status = Posted; sequence number assigned; journal entry created | Debit AR 1120; Credit Income 1000; Credit Tax Payable 120 | Y |
| B-002 | Customer Invoice | Create multi-line invoice with different products | Two products with different income accounts | 1. Create invoice with two lines: Product A (qty=2, price=500, account=400100), Product B (qty=1, price=300, account=400200), same tax. 2. Post | Lines post to respective income accounts; total AR = (1000+300)*1.12 = 1456; tax = 156 | Debit AR 1456; Credit 400100 1000; Credit 400200 300; Credit Tax Payable 156 | Y |
| B-003 | Customer Invoice | Invoice created from confirmed sales order | Sales order with one line confirmed | 1. Confirm sales order for 5 units of product at 200 each. 2. Navigate to invoice from SO. 3. Create invoice. 4. Post | Invoice amount matches SO; product, qty, price, tax propagated correctly; invoice linked to SO | Debit AR; Credit Income; Credit Tax Payable (amounts from SO) | Y |
| B-004 | Customer Invoice | Invoice with tax-excluded pricing (price_include=False) | Tax 12% excluded; product price = 1000 | 1. Create invoice: qty=1, unit_price=1000, tax=12% excluded. 2. Verify amounts | Subtotal=1000; Tax=120; Total=1120 | Debit AR 1120; Credit Income 1000; Credit Tax Payable 120 | Y |
| B-005 | Customer Invoice | Invoice with tax-included pricing (price_include=True) | Tax 10% included; product price = 1100 | 1. Create invoice: qty=1, unit_price=1100, tax=10% included. 2. Verify amounts | Tax base=1000; Tax=100; Total=1100; subtotal shown as 1000 | Debit AR 1100; Credit Income 1000; Credit Tax Payable 100 | Y |
| B-006 | Customer Invoice | Invoice with mixed taxes (one line VAT, one line exempt) | VAT 12% and Tax Exempt (0%) taxes exist | 1. Line 1: product A, price=1000, tax=VAT 12%. 2. Line 2: product B, price=500, tax=Exempt 0%. 3. Post | Tax applies only to line 1; line 2 has no tax; total = 1000*1.12 + 500 = 1620 | Debit AR 1620; Credit Income-A 1000; Credit Income-B 500; Credit Tax Payable 120 | Y |
| B-007 | Customer Invoice | Invoice with no tax | Tax-free product or zero-rate scenario | 1. Create invoice with no tax on any line. 2. Post | No tax move line created; AR = subtotal | Debit AR; Credit Income only | Y |
| B-008 | Customer Invoice | Invoice with line discount | Product with list price; discount % applied | 1. Create invoice line: unit_price=1000, discount=10%. 2. Post | Effective price = 900; tax applied on 900; total = 900*1.12 = 1008 | Debit AR 1008; Credit Income 900; Credit Tax Payable 108 | Y |
| B-009 | Customer Invoice | Invoice with payment terms — 30-day net | Customer has Net 30 payment term | 1. Create and post invoice dated today. 2. Check journal entry due date | Single AR line; due_date = invoice_date + 30 days | AR move line due_date correctly set | Y |
| B-010 | Customer Invoice | Invoice with installment payment terms | 50/50 payment term configured | 1. Create invoice for 2000. 2. Post. 3. Inspect journal entry | Two AR lines: 1000 due today, 1000 due +30 days; both sum to 2000 | Two debit AR lines; each reconcilable independently | Y |
| B-011 | Customer Invoice | Invoice with 3-installment payment term and non-round amount | 33/33/34 split on invoice of 1001 | 1. Create invoice for 1001 with 3-part payment term. 2. Post | Lines approximately: 333.33, 333.33, 334.34 (last carries rounding); total must equal 1001 exactly | Sum of three AR lines = 1001.00 exactly | Y |
| B-012 | Customer Invoice | Invoice in foreign currency | Company currency EUR; invoice in USD; rate=1.08 | 1. Create invoice in USD for 1000. 2. Post | Invoice total 1000 USD; journal entry in EUR = 1000/1.08 = 925.93 EUR; both currencies stored on move | AR debited 925.93 EUR (1000 USD); Income credited 925.93 EUR | Y |
| B-013 | Customer Invoice | Cash rounding on invoice total | Cash rounding rule configured (smallest coin=0.05) | 1. Create invoice with total = 100.03. 2. Enable cash rounding on invoice. 3. Post | Total rounded to 100.05 or 100.00; rounding difference posted to cash rounding account | Extra line posting rounding difference (±0.02) to designated account | Y |
| B-014 | Customer Invoice | Invoice with fiscal position applied | Customer has EU fiscal position; tax mapping 12%→0% | 1. Create invoice for EU customer. 2. Verify tax auto-replaced by mapped tax. 3. Post | Invoice tax = 0%; income account may be remapped; total = 1000 | AR debited 1000; Income credited 1000; no Tax Payable | Y |
| B-015 | Customer Invoice | Invoice reset to draft and re-posted | Invoice in Posted state | 1. Post invoice. 2. Reset to draft (if allowed by period lock). 3. Modify one line. 4. Re-post | New sequence number may be assigned depending on lock settings; journal entry reflects modification | Corrected journal entry; original entry reversed or replaced | N |
| B-016 | Customer Invoice | Full credit note (refund) from posted invoice | Invoice in Posted state | 1. Click Add Credit Note. 2. Select full refund. 3. Post credit note | Credit note created and posted; balances invoice to 0; reconciliation performed automatically | Credit note debits Income, credits AR; reconciliation zeroes both | Y |
| B-017 | Customer Invoice | Partial credit note | Invoice for 1000; partial refund of 300 | 1. Create credit note for 300. 2. Post. 3. Check invoice remaining residual | Invoice residual = 700; credit note reconciled against invoice | Partial match on AR; invoice still open for 700 | Y |
| B-018 | Customer Invoice | Credit note with different reason code and period | Invoice in previous period; credit note in current period | 1. Create credit note with date in current period. 2. Post | Credit note posts in current period; no back-dated entry; tax report impact in current period | Tax reversal in current period; prior period unchanged | N |
| B-019 | Customer Invoice | Verify invoice PDF output | Invoice posted | 1. Generate invoice PDF. 2. Verify: company name, customer name, invoice number, date, line items, subtotal, tax amount, total, payment terms, bank details | All fields correct on PDF; tax amount matches journal entry tax amount | No accounting impact; compliance/legal document verification | N |
| B-020 | Customer Invoice | Invoice payment status transitions | Invoice posted | 1. Post invoice (status=Not paid). 2. Register partial payment. 3. Verify status=In payment or Partial. 4. Register full payment. 5. Verify status=Paid | Status transitions correctly: Not paid → In payment/Partial → Paid | AR fully reconciled after full payment | Y |
| B-021 | Customer Invoice | Two invoices reconciled with one payment | Two open invoices for same customer | 1. Register payment for amount = sum of both invoices. 2. Apply payment to both invoices | Both invoices marked Paid; single payment entry reconciled with both AR lines | Bank debited once; both AR lines cleared | Y |
| B-022 | Customer Invoice | Invoice with early payment cash discount taken | 2/10 net 30 payment term; paid within 10 days | 1. Post invoice for 1000. 2. Register payment for 980. 3. Apply discount. 4. Verify reconciliation | Invoice fully reconciled; discount of 20 posted to early payment discount account | AR cleared; bank 980; discount account 20 | Y |
| B-023 | Customer Invoice | Invoice with early payment cash discount not taken | 2/10 net 30; paid on day 31 | 1. Post invoice for 1000. 2. Register full payment of 1000 on day 31 | Full amount collected; no discount applied; discount window expired | AR 1000 fully cleared by bank 1000 | Y |
| B-024 | Customer Invoice | Invoice with delivery address different from billing | Customer has billing and shipping addresses | 1. Create invoice. 2. Verify invoice address = billing address. 3. Verify delivery fields not shown on invoice | Correct legal address on invoice; no confusion with shipping address | No accounting impact | N |
| B-025 | Customer Invoice | Duplicate invoice prevention | Invoice INV/2026/0001 exists | 1. Attempt to create another invoice with same customer reference | System may allow but should warn; no hard block by default in CE; tested for workflow awareness | Duplicate detection is policy/process-dependent | N |

---

### Group C — Vendor Bills / AP

| ID | Area | Scenario | Preconditions | Steps | Expected Result | Accounting Impact | Automation Candidate |
|----|------|----------|---------------|-------|-----------------|-------------------|----------------------|
| C-001 | Vendor Bill | Create and post basic vendor bill | Vendor, product, expense account, VAT 12% configured | 1. Navigate to Accounting > Vendors > Bills. 2. New. 3. Select vendor. 4. Add line: product, qty=1, price=1000, tax=VAT 12%. 5. Post | Bill posted; journal entry created; AP balance updated | Debit Expense 1000; Debit Tax Receivable 120; Credit AP 1120 | Y |
| C-002 | Vendor Bill | Multi-line bill with different expense accounts | Two products with different expense accounts | 1. Create bill with Product A (600100) and Product B (600200), same tax. 2. Post | Each line posts to respective expense account | Debit 600100; Debit 600200; Debit Tax Receivable; Credit AP (total) | Y |
| C-003 | Vendor Bill | Bill created from purchase order | PO confirmed and received | 1. Confirm and receive PO. 2. Create bill from PO. 3. Verify quantities and prices match receipt | Bill lines match received quantities; price from PO or agreed price; 3-way match verification | Debit Expense (or Inventory); Debit Tax Receivable; Credit AP | Y |
| C-004 | Vendor Bill | Bill with withholding tax (EWT 2%) | EWT 2% purchase tax configured; vendor has EWT applied | 1. Create bill for 1000. 2. Apply EWT 2% (-20). 3. Post. 4. Verify net AP balance | AP balance = 1000 - 20 = 980 (withholding deducted from payment); EWT tax posts to withholding payable account | Debit Expense 1000; Debit Input VAT 120 (if VAT also); Credit EWT Payable 20; Credit AP 1100 (net) | Y |
| C-005 | Vendor Bill | Bill with input VAT (Tax Receivable) | VAT 12% purchase tax | 1. Post bill with VAT 12%. 2. Check Tax Receivable account | Input VAT = 120 on Debit side of Tax Receivable account; eligible for offset against output VAT | Debit Tax Receivable 120 | Y |
| C-006 | Vendor Bill | No-tax bill (e.g., rent, exempt service) | Exempt vendor or zero-rate purchase | 1. Create bill with no tax or zero-rate tax. 2. Post | No tax receivable entry; AP = expense amount | Debit Expense; Credit AP only | Y |
| C-007 | Vendor Bill | Partial payment against bill | Bill for 1000; pay 400 | 1. Post bill. 2. Register payment of 400. 3. Check bill status and residual | Bill status=Partial; residual=600; payment reconciled with one or more AP lines | AP partially cleared; bank debited 400 | Y |
| C-008 | Vendor Bill | Full payment against bill | Bill for 1000; pay 1000 | 1. Post bill. 2. Register full payment. 3. Verify status=Paid | Bill status=Paid; AP fully reconciled | AP cleared; bank debited 1000 | Y |
| C-009 | Vendor Bill | Overpayment on vendor bill | Bill for 1000; pay 1100 | 1. Post bill. 2. Register payment of 1100. 3. Check vendor credit | Bill paid in full; 100 credit remains on vendor account as debit balance on AP | AP cleared (1000); 100 credit balance on AP for this vendor | Y |
| C-010 | Vendor Bill | Bill with fiscal position (tax mapping) | Vendor has Foreign fiscal position; tax mapping: VAT 12%→VAT 0% | 1. Create bill for foreign vendor. 2. Verify tax replaced by 0% | No input VAT claimed; expense = gross amount | Debit Expense 1000; Credit AP 1000 (no tax entry) | Y |
| C-011 | Vendor Bill | Reversal of posted bill (credit note) | Vendor bill in Posted state | 1. Click Reverse. 2. Set reversal date and reason. 3. Post reversal | Reversal entry created; original bill and reversal reconcile; net AP = 0 | Reversal debits AP, credits Expense and Tax Receivable | Y |
| C-012 | Vendor Bill | Duplicate vendor reference detection | Bill from same vendor with same vendor ref already exists | 1. Create bill with vendor_ref=VB-001. 2. Post. 3. Create another bill for same vendor with vendor_ref=VB-001. 4. Post | Odoo should warn about duplicate vendor reference; prevents double-payment risk | Duplicate detection warning; both may be allowed if user overrides | Y |
| C-013 | Vendor Bill | Bill with multiple due dates (installment AP) | Payment term with installments applied to vendor | 1. Create bill for 2000 with 50/50 payment term. 2. Post | Two AP lines: 1000 due today, 1000 due +30 days | Two credit AP lines; each independently payable | Y |
| C-014 | Vendor Bill | Bill in foreign currency | Company EUR; bill in USD | 1. Create bill in USD 1000 at rate 1.08. 2. Post | AP line in EUR = 925.93; both currencies on move | Credit AP 925.93 EUR (1000 USD) | Y |
| C-015 | Vendor Bill | Bill with account-mapped fiscal position | Vendor has fiscal position that remaps expense account | 1. Create bill for vendor with fiscal position mapping 600100→600200. 2. Post | Expense posts to 600200 instead of 600100 | Debit 600200 instead of 600100 | Y |
| C-016 | Vendor Bill | Goods receipt bill — price variance | PO price = 100; actual bill price = 105 | 1. Receive PO at 100. 2. Create bill at 105. 3. Post | Price variance of 5 posted to price variance account (if enabled); stock valuation adjusted | Debit Expense/Variance 5; original posting was at 100 | N |
| C-017 | Vendor Bill | Vendor bill from service PO (no receipt) | Service PO; no stock movement | 1. Create PO for service. 2. Bill against PO directly. 3. Post | No goods receipt required; bill posts directly to expense | Debit Expense; Debit Tax Receivable; Credit AP | Y |
| C-018 | Vendor Bill | AP aging report correctness | Multiple open bills with different due dates | 1. Post 5 bills with different due dates. 2. Run AP aging report. 3. Verify each bill appears in correct aging bucket | Each bill's outstanding amount in correct aging column (current, 1-30, 31-60, 61-90, 90+) | Report reflects posted AP balances | Y |

---

### Group D — Taxes

| ID | Area | Scenario | Preconditions | Steps | Expected Result | Accounting Impact | Automation Candidate |
|----|------|----------|---------------|-------|-----------------|-------------------|----------------------|
| D-001 | Taxes | Single excluded tax on invoice | Tax 12% excluded | 1. Invoice: price=1000, tax=12% excl. 2. Post | Tax=120; Total=1120; journal entry correct | Debit AR 1120; Credit Income 1000; Credit Tax Payable 120 | Y |
| D-002 | Taxes | Single included tax on invoice | Tax 10% included | 1. Invoice: price=1100 (includes 10% tax). 2. Post | Tax=100; Subtotal=1000; Total=1100 | Debit AR 1100; Credit Income 1000; Credit Tax Payable 100 | Y |
| D-003 | Taxes | Two independent taxes on same line | Tax A 10% excl; Tax B 5% excl, both on same line | 1. Invoice: price=1000, taxes=[A, B]. 2. Post | Tax A=100; Tax B=50; Total=1150; each tax posts to own account | Debit AR 1150; Credit Income 1000; Credit Tax-A Payable 100; Credit Tax-B Payable 50 | Y |
| D-004 | Taxes | Tax on tax (include_base_amount=True) | Tax A 10%; Tax B 5% with include_base_amount=True | 1. Invoice: price=1000, taxes=[A, B] where B includes A in base. 2. Post | Tax A=100; Tax B=55 (5% of 1100); Total=1155 | Debit AR 1155; Credit Income 1000; Credit Tax-A 100; Credit Tax-B 55 | Y |
| D-005 | Taxes | Tax rounding per line | 3 lines each with fractional tax amounts | 1. Invoice: line1 price=33.33, line2=33.33, line3=33.34, tax=10%. 2. Post | Per-line rounding: 3.33+3.33+3.33=9.99 or 3.33+3.33+3.34=10.00 depending on rounding method | Total tax in journal entry must match displayed tax total; no off-by-one | Y |
| D-006 | Taxes | Tax rounding global (round globally) | Company tax rounding method = round_globally | 1. Same invoice as D-005 with global rounding. 2. Post | Tax base = 100.00; tax = 10.00 (global round); may differ from per-line method | Global method may produce different total than per-line; verify company setting drives behavior | Y |
| D-007 | Taxes | Cash basis tax — invoice post without payment | Cash basis company; tax marked on_payment | 1. Post invoice with cash basis tax. 2. Do NOT pay. 3. Check tax report | Tax NOT in tax payable account; in transition account; tax report does not show this tax | Debit AR; Credit Income; Credit Tax Transition (not Tax Payable) | Y |
| D-008 | Taxes | Cash basis tax — invoice post then pay | Cash basis invoice | 1. Post invoice. 2. Register payment. 3. Check tax report | At payment: reconciliation triggers cash basis entry; tax moves from transition to Tax Payable | Debit Tax Transition; Credit Tax Payable (on payment reconciliation) | Y |
| D-009 | Taxes | Cash basis tax — partial payment | Cash basis; invoice 1000; pay 500 | 1. Post invoice. 2. Pay 500. 3. Check tax allocation | Only 50% of tax (proportional) moves from transition to Tax Payable | Proportional cash basis entry; remaining 50% stays in transition | Y |
| D-010 | Taxes | Withholding tax on vendor bill | EWT 2% applied to vendor bill | 1. Create bill for 1000. 2. Apply EWT 2%. 3. Post | Withholding = 20; net AP = 980 (or 1100 with VAT - 20 EWT); withholding account credited | EWT credit to withholding payable account | Y |
| D-011 | Taxes | Changed tax after invoice is in draft | Invoice in draft with Tax A; change to Tax B | 1. Create draft invoice with Tax A. 2. Remove Tax A; add Tax B. 3. Post | Journal entry uses Tax B; Tax A not in entry | Tax B account used; Tax A account not used | Y |
| D-012 | Taxes | Missing tax account — posting blocked | Tax configured without tax account | 1. Create tax with no tax account. 2. Apply to invoice. 3. Attempt to post | Error: missing account for tax; posting blocked | No incomplete journal entry created | Y |
| D-013 | Taxes | Tax group display | Two taxes in same tax group on invoice | 1. Create taxes A and B in same tax group. 2. Apply both to invoice | Tax group shown as single line on invoice PDF with combined amount; individual tax lines in journal entry | Individual journal lines per tax; grouped display on document | Y |
| D-014 | Taxes | Zero-rate tax (explicit) | Tax 0% configured explicitly (not no-tax) | 1. Apply 0% tax to invoice line. 2. Post | Tax line in journal entry with amount=0; tax appears in tax report as zero-rated supply | Tax line with 0 amount posted; visible in tax report | Y |
| D-015 | Taxes | Tax report period filtering | Multiple invoices in different periods | 1. Post invoices in Jan and Feb. 2. Run tax report for Jan only | Only Jan taxes appear; Feb excluded | Report filters by accounting date; cash basis uses payment date | Y |
| D-016 | Taxes | Tax report total vs journal items reconciliation | Posted invoices for a period | 1. Run tax report. 2. Run journal items filtered by tax accounts. 3. Compare totals | Tax report totals must match sum of journal items on tax accounts for same period | Mathematical consistency check | Y |
| D-017 | Taxes | Fiscal position tax mapping removes tax | Fiscal position maps Tax A → no tax | 1. Create invoice with fiscal position that maps Tax A to nothing. 2. Post | No tax line in journal entry; total = subtotal | No tax payable credit | Y |
| D-018 | Taxes | Purchase tax — input VAT recoverability | Input VAT 12% on vendor bill | 1. Post vendor bill with 12% input VAT. 2. Check Tax Receivable account | Tax Receivable debited; eligible for VAT return offset | Debit Tax Receivable 120 per 1000 expense | Y |

---

### Group E — Fiscal Positions

| ID | Area | Scenario | Preconditions | Steps | Expected Result | Accounting Impact | Automation Candidate |
|----|------|----------|---------------|-------|-----------------|-------------------|----------------------|
| E-001 | Fiscal Position | Domestic fiscal position — no mapping | Default domestic fiscal position with no tax or account mapping | 1. Assign domestic fiscal position to customer. 2. Create invoice. 3. Post | Taxes and accounts unchanged; fiscal position is informational only | Same as invoice without fiscal position | Y |
| E-002 | Fiscal Position | Tax mapping on customer invoice | Fiscal position maps VAT 12% → Export 0% | 1. Create invoice for customer with this fiscal position. 2. Add product with VAT 12%. 3. Verify tax replaced | Tax on line shows Export 0%; no tax payable | AR debited at subtotal only; no Tax Payable | Y |
| E-003 | Fiscal Position | Account mapping on customer invoice | Fiscal position maps Income 400100 → Export Income 400200 | 1. Create invoice for customer with this fiscal position. 2. Post | Income credited to 400200; not 400100 | Credit 400200 instead of 400100 | Y |
| E-004 | Fiscal Position | Tax and account mapping combined | Fiscal position has both tax and account mapping | 1. Create invoice with fiscal position applying both mappings. 2. Post | Both tax and account replaced; journal entry uses mapped values entirely | Both tax account and income account from mapping used | Y |
| E-005 | Fiscal Position | Auto-detect by country on customer | Fiscal position defined for country=US; customer.country=US | 1. Create invoice for US customer without manually selecting fiscal position. 2. Verify | Fiscal position auto-applied based on country | Mapped taxes/accounts used | Y |
| E-006 | Fiscal Position | Auto-detect by VAT number presence | Fiscal position: auto_apply=True, vat_required=True | 1. Customer with VAT number. 2. Create invoice. 3. Verify fiscal position applied | If customer has VAT number, this fiscal position auto-selected | Mapped taxes used | Y |
| E-007 | Fiscal Position | Manual override of auto-detected fiscal position | Customer has auto-detected fiscal position; user manually changes it | 1. Create invoice. 2. Auto-detect applies FP-A. 3. Manually change to FP-B. 4. Confirm lines update | Tax and account on lines should update to FP-B mappings; may require explicit refresh of lines | FP-B mappings used in journal entry | N |
| E-008 | Fiscal Position | Change fiscal position after lines added | Invoice with two lines; fiscal position changed | 1. Add two lines with Tax A. 2. Change fiscal position that maps Tax A → Tax B. 3. Verify lines updated | Odoo 18 should prompt or auto-update taxes; if not auto-updated, test must catch stale taxes | Stale tax risk: line still shows Tax A but FP says Tax B | N |
| E-009 | Fiscal Position | Fiscal position on vendor bill | Vendor has fiscal position mapping purchase tax | 1. Create bill for vendor with fiscal position. 2. Verify mapped purchase tax applied | Correct purchase tax per fiscal position on bill | Correct input VAT account used | Y |
| E-010 | Fiscal Position | Missing mapping — unmapped tax passes through | Fiscal position has mapping for Tax A only; invoice has Tax A and Tax B | 1. Create invoice with both taxes. 2. Apply fiscal position. 3. Post | Tax A replaced per mapping; Tax B passes through unchanged | Tax A mapped; Tax B as-is | Y |
| E-011 | Fiscal Position | Invalid / missing tax in mapping | Fiscal position maps Tax A → Tax C, but Tax C is archived | 1. Create invoice with fiscal position. 2. Post | Error or warning about archived target tax; posting may produce incorrect result | Risk of silent failure if archived tax has no account | N |
| E-012 | Fiscal Position | Posting impact under mapped account | Normal account vs mapped account produces different P&L category | 1. Post invoice with account mapping. 2. Check P&L report | Revenue reported under mapped account category; not default | P&L grouping follows mapped account type | Y |

---

### Group F — Payments

| ID | Area | Scenario | Preconditions | Steps | Expected Result | Accounting Impact | Automation Candidate |
|----|------|----------|---------------|-------|-----------------|-------------------|----------------------|
| F-001 | Payments | Register full payment from customer invoice | Invoice for 1120 posted | 1. Open invoice. 2. Click Register Payment. 3. Select bank journal. 4. Amount=1120. 5. Confirm | Invoice status=Paid; payment entry created; AR reconciled | Debit Bank 1120; Credit Outstanding Receipts 1120 → reconciled against AR | Y |
| F-002 | Payments | Register partial payment from customer invoice | Invoice for 1120 | 1. Register payment of 560. 2. Verify invoice status | Invoice status=In payment or Partial; residual=560 | Debit Bank 560; AR partially cleared | Y |
| F-003 | Payments | Register payment from vendor bill | Bill for 1120 posted | 1. Open bill. 2. Register Payment. 3. Amount=1120. 4. Confirm | Bill status=Paid; AP reconciled | Debit Outstanding Payments; Credit Bank 1120 → reconciled against AP | Y |
| F-004 | Payments | Manual payment not linked to invoice | Standalone customer payment | 1. Navigate to Accounting > Customers > Payments. 2. New payment. 3. Amount=500. 4. Confirm | Payment created; credit on customer AR account; available to match against future invoice | Debit Bank 500; Credit AR (unreconciled) | Y |
| F-005 | Payments | Apply unlinked payment to open invoice | Open invoice; unlinked payment from F-004 | 1. Open invoice. 2. Outstanding credits section shows the 500 credit. 3. Click to apply | Invoice partially reconciled; residual reduced by 500 | AR lines reconciled; no new bank entry | Y |
| F-006 | Payments | Overpayment on customer invoice | Invoice 1000; payment 1100 | 1. Register payment of 1100 against invoice of 1000. 2. Check outcome | Invoice paid in full; 100 credit on customer account; overpayment recorded | Bank 1100; AR cleared 1000; Credit 100 stays on partner account | Y |
| F-007 | Payments | Underpayment with write-off | Invoice 1000; payment 995; 5 written off | 1. Register payment 995. 2. Mark difference as write-off to bad debt account. 3. Confirm | Invoice fully reconciled; 5 posted to write-off account | Bank 995; Write-off 5; AR 1000 cleared | Y |
| F-008 | Payments | Payment via cash journal | Cash payment for small invoice | 1. Register payment using Cash journal. 2. Post | Cash account debited instead of bank; otherwise same as bank payment | Debit Cash; Credit Outstanding Receipts → reconciled | Y |
| F-009 | Payments | Payment reversal | Payment posted and reconciled | 1. Open payment. 2. Click Reverse (if in draft) or use Cancel. 3. Confirm | Payment reversed; original invoice/bill reopened to unpaid; reconciliation undone | Reversal entry mirrors original payment entry | Y |
| F-010 | Payments | Payment in foreign currency | Invoice in USD; payment in USD; company in EUR | 1. Register payment in USD. 2. Verify FX gain/loss if rate changed between invoice and payment date | If rate changed: FX gain or loss entry created on reconciliation | FX Gain/Loss account debited or credited for difference | Y |
| F-011 | Payments | Early payment discount applied | 2/10 net 30 invoice; paid day 5 | 1. Post invoice 1000. 2. Register payment 980. 3. Apply 20 as cash discount. 4. Confirm | Invoice fully reconciled; discount posted to cash discount account | Bank 980; Cash Discount 20; AR 1000 cleared | Y |
| F-012 | Payments | Payment terms — verify due dates on payment | Invoice with installment payment terms | 1. Post invoice with 3 installments. 2. Register payment for first installment only | First installment line reconciled; remaining two still open; no premature full payment | Only first AR line cleared; other two open | Y |
| F-013 | Payments | Batch payment — multiple invoices one payment | Three open invoices for same customer | 1. Select all three invoices. 2. Register batch payment. 3. Confirm | Single payment entry covering all three invoices; all three reconciled | Bank debited once for total; three AR lines cleared | Y |
| F-014 | Payments | Payment journal — wrong journal type selected | User selects purchase journal for customer payment | 1. Attempt to register customer payment using purchase journal | System should restrict journal types for payment; only bank/cash journals available | Incorrect journal type blocked | Y |
| F-015 | Payments | Payment with memo field mapped to invoice | Invoice with specific reference; payment with same reference | 1. Create payment with communication matching invoice number. 2. Reconcile | Statement matching uses memo/reference to suggest invoice match | Automated matching quality tested | Y |

---

### Group G — Bank Reconciliation

| ID | Area | Scenario | Preconditions | Steps | Expected Result | Accounting Impact | Automation Candidate |
|----|------|----------|---------------|-------|-----------------|-------------------|----------------------|
| G-001 | Bank Reconciliation | Import bank statement (CSV/OFX) | Bank journal configured; statement file available | 1. Navigate to Accounting > Bank > Import Statement. 2. Upload file. 3. Verify lines imported with date, description, amount | Statement lines imported; each line shows as unreconciled | No immediate accounting impact; lines pending reconciliation | Y |
| G-002 | Bank Reconciliation | Manual bank statement entry | No import file; manual entry | 1. Navigate to bank journal. 2. New statement. 3. Add lines manually. 4. Confirm | Statement lines created; unreconciled | Same as import | Y |
| G-003 | Bank Reconciliation | Match statement line to existing payment | Payment registered; statement line for same amount | 1. In reconciliation view, select statement line. 2. System suggests matching payment. 3. Confirm match | Statement line reconciled; bank account balanced; outstanding receipts/payments cleared | Outstanding account cleared; bank account = statement | Y |
| G-004 | Bank Reconciliation | Match statement line directly to invoice | Invoice open (no payment registered); bank deposit received | 1. Select statement line. 2. Find open invoice as match. 3. Confirm | Payment auto-created and reconciled; invoice marked paid | Bank debited; AR cleared via auto-created payment | Y |
| G-005 | Bank Reconciliation | Partial reconciliation of statement line | Statement line 1000; matching invoice for 600 | 1. Match statement line to 600 invoice. 2. Handle remaining 400 | Remaining 400 left as outstanding on statement; or split into two lines | 600 reconciled; 400 pending | Y |
| G-006 | Bank Reconciliation | Write-off small difference during reconciliation | Statement line 1000.05; matching invoice 1000.00 | 1. Match statement line to invoice. 2. 0.05 difference remains. 3. Write off to bank charges account. 4. Confirm | Invoice fully reconciled; 0.05 posted to bank charges | Bank charges account debited 0.05 | Y |
| G-007 | Bank Reconciliation | Multi-currency reconciliation | EUR company; USD bank statement | 1. Import USD statement. 2. Match to USD invoice. 3. Confirm reconciliation | FX difference between statement rate and invoice rate posted to FX gain/loss | FX Gain/Loss entry created | N |
| G-008 | Bank Reconciliation | Unmatched statement line — mark as bank charge | Statement line for bank fee with no matching document | 1. Select statement line for bank fee. 2. Create new journal entry on-the-fly. 3. Post to bank charges account | New journal entry created; statement line reconciled | Bank charges account debited | Y |
| G-009 | Bank Reconciliation | Suspense/outstanding account behavior | Outstanding receipts account configured | 1. Register payment (posts to outstanding receipts). 2. Before bank reconciliation, check outstanding account balance. 3. Reconcile. 4. Re-check | Outstanding account goes to zero after reconciliation; bank account shows correct balance | Outstanding receipts cleared; bank balance correct | Y |
| G-010 | Bank Reconciliation | Reconcile multiple payments to one statement line | One deposit covers three customer payments | 1. Statement line for 3000. 2. Match to three 1000-payments. 3. Confirm | Single statement line matched to three payment entries; bank balanced | Three outstanding receipt lines cleared by one statement line | Y |
| G-011 | Bank Reconciliation | Duplicate statement line import | Import same statement file twice | 1. Import statement. 2. Import same file again. 3. Check for duplicates | System should detect or prevent duplicate import; duplicate statement lines would double-count | Duplicate prevention critical for balance correctness | Y |
| G-012 | Bank Reconciliation | Undo reconciliation | Statement line reconciled to payment | 1. Navigate to reconciled statement line. 2. Undo reconciliation. 3. Verify state | Reconciliation undone; invoice/bill reopened; outstanding account re-populated | Outstanding account re-debited; bank still at statement value | Y |
| G-013 | Bank Reconciliation | Closing bank statement balance check | Statement with opening and closing balances | 1. Create statement with opening balance 5000. 2. Add lines (deposits and withdrawals). 3. Close statement. 4. Verify closing balance matches | Closing balance = opening + all credits - all debits; must match bank statement | Bank account balance reflects statement | Y |
| G-014 | Bank Reconciliation | Reconciliation after correction to invoice | Invoice corrected (credit note applied); then reconciled with statement | 1. Post invoice. 2. Apply partial credit note. 3. Reconcile remaining balance via bank statement | Remaining residual correctly reconciled; no over/under | Correct AR/AP clearing | N |

---

### Group H — Expenses

| ID | Area | Scenario | Preconditions | Steps | Expected Result | Accounting Impact | Automation Candidate |
|----|------|----------|---------------|-------|-----------------|-------------------|----------------------|
| H-001 | Expenses | Create expense — employee-paid | Employee exists; expense category configured | 1. Navigate to Expenses. 2. New expense. 3. Category=Travel, amount=500, payment_mode=Own Money. 4. Attach receipt. 5. Submit to report | Expense created in draft; linked to expense report | No accounting impact until posted | Y |
| H-002 | Expenses | Create expense — company-paid | Company payment mode selected | 1. New expense. 2. Category=Office Supplies, amount=200, payment_mode=Company Money. 3. Submit | Expense created; no reimbursement to employee | Posting will debit expense, credit AP/company account | Y |
| H-003 | Expenses | Expense report submission and manager approval | Expense report created | 1. Submit expense report. 2. Manager logs in. 3. Reviews and approves report | Status changes from Submitted to Approved | No accounting impact until posted | N |
| H-004 | Expenses | Expense report posting after approval | Approved expense report | 1. Accountant posts expense report. 2. Verify journal entry created | Journal entry posted to expense accounts; employee payable account credited | Debit Expense Account; Credit Employee Payable (for own-money) | Y |
| H-005 | Expenses | Expense report posting — company-paid | Approved company-paid expense report | 1. Post expense report. 2. Verify journal entry | Debit Expense Account; Credit AP or company credit card account | No employee payable line | Y |
| H-006 | Expenses | Employee reimbursement payment | Expense report posted; employee-paid | 1. Navigate to Accounting > Vendors > Bills (or Expense payments). 2. Create payment to employee. 3. Reconcile with expense payable | Employee payable cleared; bank debited for reimbursement amount | Debit Employee Payable; Credit Bank | Y |
| H-007 | Expenses | Expense with VAT | Expense category has purchase tax VAT 12% | 1. Create expense for 1000 with VAT 12%. 2. Post report | Expense amount=1000; VAT=120 posted to input VAT account; total=1120 | Debit Expense 1000; Debit Input VAT 120; Credit Employee Payable 1120 | Y |
| H-008 | Expenses | Expense re-invoiced to customer | Expense marked as billable to customer project | 1. Create expense, mark billable=True, link to customer. 2. Post report. 3. Navigate to customer invoice. 4. Create invoice from billable expense | Invoice created for customer; expense amount + markup charged | Customer invoice created; expense linked to sales document | N |
| H-009 | Expenses | Expense with wrong expense account | Expense category configured with archived account | 1. Create expense with misconfigured category. 2. Submit and approve. 3. Post | Error at posting: invalid account; posting blocked or posts to wrong account | Risk: silent posting to incorrect account if validation not enforced | Y |
| H-010 | Expenses | Expense report rejected | Report in Submitted state; manager rejects | 1. Submit report. 2. Manager clicks Refuse. 3. Add reason | Report status = Refused; employee notified; no accounting entry | No accounting impact | N |
| H-011 | Expenses | Multiple expenses in one report | Three expenses from one trip | 1. Create 3 expenses. 2. Add all to one expense report. 3. Post | Single journal entry covers all expenses; each line uses correct account | Debit lines per expense account; single Credit Employee Payable | Y |
| H-012 | Expenses | Expense currency different from company | Employee in USD country; company in EUR | 1. Create expense in USD. 2. Post | Expense amount converted to company currency; FX rate stored | Debit Expense in EUR (converted); Credit Employee Payable in EUR | Y |
| H-013 | Expenses | Verify expense does not appear in AR | Expense posted | 1. Post expense. 2. Check AR aging report | Employee payable is in AP/Liabilities; not in AR | Expense payable account is type=Payable | Y |
| H-014 | Expenses | Expense reimbursement reconciliation verification | Expense posted; payment made to employee | 1. Post expense. 2. Make reimbursement payment. 3. Check employee payable account balance | Employee payable balance = 0 after reconciliation | Payable fully cleared | Y |

---

### Group I — Reporting and Auditability

| ID | Area | Scenario | Preconditions | Steps | Expected Result | Accounting Impact | Automation Candidate |
|----|------|----------|---------------|-------|-----------------|-------------------|----------------------|
| I-001 | Reporting | Journal items audit — invoice | Invoice posted | 1. Navigate to Accounting > Accounting > Journal Items. 2. Filter by invoice. 3. Verify each move line: account, amount, partner, date | All lines present: AR debit, Income credit, Tax credit; amounts match invoice; partner correct | Verification of journal entry completeness | Y |
| I-002 | Reporting | AR aging report — open invoices | Multiple invoices with different due dates | 1. Run AR Aging report. 2. Verify each open invoice in correct bucket | Each invoice appears in correct aging column; total matches sum of open AR balances | Report aggregates AR move lines | Y |
| I-003 | Reporting | AP aging report — open bills | Multiple bills with different due dates | 1. Run AP Aging report. 2. Verify open bills | Same verification as I-002 for AP | AP move lines aggregated | Y |
| I-004 | Reporting | Tax report — period totals | Invoices and bills posted in a period | 1. Run Tax Report for period. 2. Verify output tax (sales), input tax (purchases), net VAT | Output tax = sum of Tax Payable from invoices; Input = sum of Tax Receivable from bills; net = output - input | Tax accounts cross-checked | Y |
| I-005 | Reporting | Tax report with cash basis | Cash basis company; invoices posted but some unpaid | 1. Post invoices with cash basis tax. 2. Run tax report. 3. Verify only paid invoices show tax | Unpaid invoices absent from tax report; only payment-triggered tax entries included | Cash basis timing correctly reflected | Y |
| I-006 | Reporting | P&L report — income and expense accounts | Multiple invoices and bills posted | 1. Run Profit & Loss report. 2. Verify income totals match sum of income account credits; expense totals match expense account debits | P&L totals match journal items on income/expense accounts | Revenue and cost accounts aggregated | Y |
| I-007 | Reporting | Balance sheet — AR and AP balances | Invoices and bills with various states | 1. Run Balance Sheet. 2. Verify AR = sum of open receivable move lines; AP = sum of open payable move lines | AR and AP on balance sheet match aging report totals | Receivable/Payable account balances | Y |
| I-008 | Reporting | Trial balance cross-check | Period with multiple transactions | 1. Run Trial Balance for period. 2. Verify total debits = total credits | Sum of all debit amounts = sum of all credit amounts; balanced | Mathematical integrity of all entries | Y |
| I-009 | Reporting | Locked period — no new entries | Period locked in company settings | 1. Navigate to Accounting > Accounting > Lock Dates. 2. Set lock date to end of last month. 3. Attempt to post invoice dated in locked period | Error: cannot post in locked period; posting blocked | No entry created in locked period | Y |
| I-010 | Reporting | Audit trail — chatter and history | Invoice modified before posting | 1. Create invoice. 2. Modify amount. 3. Post. 4. Check chatter | Chatter shows creation, modifications, posting events with user and timestamp | Traceability of changes | Y |
| I-011 | Reporting | Source document traceability | Expense report → journal entry | 1. Post expense report. 2. Navigate to journal entry. 3. Verify link back to expense report | Journal entry has reference to source document; navigable link | Audit trail from entry to source | Y |
| I-012 | Reporting | Invoice/bill totals vs journal entry amounts | Posted invoice | 1. Compare invoice total shown on invoice with sum of journal entry amounts | Invoice total = sum of debit on AR line; tax on invoice = credit on tax account; subtotal = credit on income account | Mathematical consistency | Y |
| I-013 | Reporting | Reporting period filter consistency | Different date filters on same data | 1. Run report for Jan. 2. Run for full Q1. 3. Verify Q1 total = Jan + Feb + Mar totals | Additive consistency; no duplicate or missing transactions | Period filter correctness | Y |
| I-014 | Reporting | Sequence integrity audit | Multiple invoices posted in sequence | 1. List all customer invoices ordered by sequence. 2. Verify no gaps in numbering | Sequential numbering with no gaps; canceled invoices leave a trace with reversed sequence entry (Odoo 18 behavior) | Compliance: sequential numbering required in many jurisdictions | Y |
| I-015 | Reporting | Partner statement — AR details | Customer with multiple invoices and payments | 1. Run partner ledger for customer. 2. Verify each invoice, payment, and balance | All transactions present; running balance correct; paid invoices show zero balance | Customer ledger correctness | Y |

---

### Group J — Permissions and Workflow Controls

| ID | Area | Scenario | Preconditions | Steps | Expected Result | Accounting Impact | Automation Candidate |
|----|------|----------|---------------|-------|-----------------|-------------------|----------------------|
| J-001 | Permissions | Billing user cannot post invoices | User has Invoicing/Billing role only (not Accountant) | 1. Log in as billing user. 2. Create invoice. 3. Attempt to click Confirm | Button may be visible but action blocked by access rule; or button not shown | No posting occurs | Y |
| J-002 | Permissions | Accountant can post invoices | User has Accounting/Accountant role | 1. Log in as accountant. 2. Create and post invoice | Posting succeeds | Journal entry created | Y |
| J-003 | Permissions | Employee cannot view accounting entries | User has Employee role (no accounting access) | 1. Log in as employee. 2. Attempt to navigate to Accounting > Journal Items | Access denied; accounting menus not visible or access error | No data exposed | Y |
| J-004 | Permissions | Employee can submit expense but not approve | User is expense submitter | 1. Log in as employee. 2. Create and submit expense report. 3. Attempt to approve own report | Submit succeeds; approve fails or button not available | No accounting impact until manager approves | N |
| J-005 | Permissions | Manager can approve expense report | User has expense manager role | 1. Log in as manager. 2. Navigate to submitted expense report. 3. Approve | Approval succeeds; status changes to Approved | Ready for accounting posting | N |
| J-006 | Permissions | Accountant cannot approve own expenses | Accountant also submitted an expense | 1. Accountant submits expense. 2. Same user attempts to approve own report | Self-approval should be blocked (policy-dependent; may require configuration) | Controls segregation of duties | N |
| J-007 | Permissions | Unauthorized payment attempt | User with read-only accounting access | 1. Log in as read-only user. 2. Open paid invoice. 3. Attempt to register additional payment | Action blocked; no payment created | No accounting change | Y |
| J-008 | Permissions | Workflow state integrity | Invoice in Draft state | 1. Attempt to directly set invoice to Paid state via RPC/UI manipulation | State machine enforces transitions; cannot skip steps | Draft → Posted → Paid only through valid transitions | N |
| J-009 | Permissions | Locked period write attempt | Period locked | 1. User with accountant role attempts to post invoice in locked period | Blocked by lock date validation regardless of user role | No entry in locked period | Y |
| J-010 | Permissions | Administrator can override period lock | Admin with specific override right | 1. Log in as administrator. 2. Change lock date. 3. Post in newly unlocked period | Lock date change permitted for admin; posting succeeds in unlocked period | Entry created; compliance risk if abused | N |

---

### Group K — Localization-Sensitive Scenarios

| ID | Area | Scenario | Preconditions | Steps | Expected Result | Accounting Impact | Automation Candidate |
|----|------|----------|---------------|-------|-----------------|-------------------|----------------------|
| K-001 | Localization | Philippines — VAT 12% on sale | l10n_ph installed; VAT-registered company | 1. Create customer invoice with VAT 12% as per BIR requirement. 2. Post | VAT 12% computed on taxable amount; posted to Output VAT account (BIR-designated) | Debit AR; Credit Income; Credit Output VAT (BIR account) | Y |
| K-002 | Localization | Philippines — EWT on vendor bill | EWT rates per BIR RR 11-2018 configured | 1. Create vendor bill. 2. Apply correct EWT rate (e.g., 2% for professionals). 3. Post | EWT withheld from payment; EWT payable account credited; Form 2307 details captured | Debit Expense; Debit Input VAT; Credit EWT Payable; Credit AP (net) | Y |
| K-003 | Localization | Philippines — zero-rated export | Zero-rated sale; export documentation required | 1. Create invoice for export customer with zero-rated fiscal position. 2. Post | VAT = 0; zero-rated sale reflected in tax report | AR debited at invoice total; no Output VAT | Y |
| K-004 | Localization | Philippines — VAT-exempt transaction | Exempt product or entity | 1. Create invoice with VAT-exempt tax (not zero-rated). 2. Post | Exempt amount in tax report; separate from zero-rated | Tax report shows exempt column populated | Y |
| K-005 | Localization | EU — intra-community supply (zero VAT with report) | EU localization; reverse charge | 1. Create invoice for EU VAT-registered customer. 2. Apply intra-community supply fiscal position. 3. Post | Output VAT = 0; transaction reported in EC Sales List | EC Sales List entry generated; no VAT payable | N |
| K-006 | Localization | EU — reverse charge on purchase | EU localization; purchase from EU VAT vendor | 1. Create bill from EU vendor with reverse charge tax. 2. Post | Both output and input VAT entries created for same amount (self-assessed); net VAT = 0 | Debit Input VAT; Credit Output VAT; net = 0 | N |
| K-007 | Localization | India — TDS withholding on vendor | Indian localization; TDS applicable | 1. Create vendor bill for TDS-applicable service. 2. Apply TDS rate per Income Tax Act. 3. Post | TDS deducted from payment; TDS payable account credited | Debit Expense; Credit TDS Payable; Credit AP (net) | N |
| K-008 | Localization | Tax report — country-specific format | Country localization provides specific tax report format | 1. Run localization tax report (e.g., PH VAT Summary, IN GSTR). 2. Verify all required fields populated | Report format matches legal requirement; all mandatory fields present | Report data sourced from journal entries | N |
| K-009 | Localization | Localization upgrade / config drift | Localization package updated via OCA | 1. Update l10n module. 2. Verify existing taxes and accounts unchanged. 3. Verify new tax rates added if applicable | No regression in existing tax/account configuration; new legal requirements added cleanly | No change to existing posted entries; new config for future | N |
| K-010 | Localization | Multi-company with different localizations | Two companies: one PH, one EU | 1. Switch to PH company; verify PH taxes/reports. 2. Switch to EU company; verify EU taxes/reports. 3. Verify no cross-contamination | Each company uses its own localization; shared partner data but separate accounting | No cross-company ledger contamination | N |

---

### Group L — Negative and Failure Scenarios

| ID | Area | Scenario | Preconditions | Steps | Expected Result | Accounting Impact | Automation Candidate |
|----|------|----------|---------------|-------|-----------------|-------------------|----------------------|
| L-001 | Negative | Post invoice with missing income account | Product has no income account; no company default | 1. Create invoice with this product. 2. Click Confirm | Error: account missing for journal item; posting blocked with clear message | No partial entry created | Y |
| L-002 | Negative | Post invoice with missing tax account | Tax configured without tax account | 1. Apply tax with no account to invoice. 2. Confirm | Error: missing account on tax; posting blocked | No incomplete entry | Y |
| L-003 | Negative | Post invoice with missing AR account | Customer has no receivable account and no default in chart | 1. Create invoice for customer. 2. Confirm | Error: no receivable account found; posting blocked | No entry | Y |
| L-004 | Negative | Post invoice in locked period | Invoice date in locked period | 1. Set lock date = today - 1. 2. Create invoice dated yesterday. 3. Confirm | Error: period locked; posting blocked | No entry in locked period | Y |
| L-005 | Negative | Duplicate vendor bill reference | Same vendor reference submitted twice | 1. Post bill with ref=VB-001. 2. Create second bill same vendor, same ref. 3. Post | Warning or error about duplicate reference; prevents double-payment | Duplicate risk flagged | Y |
| L-006 | Negative | Invalid fiscal position — archived target tax | Fiscal position maps to archived tax | 1. Apply fiscal position with archived target tax to invoice. 2. Post | Error or warning: target tax archived/invalid; posting may be blocked or produce incorrect tax | Risk of silent incorrect tax | Y |
| L-007 | Negative | Stale draft after account deletion | Invoice in draft referencing account that has been archived | 1. Create draft invoice. 2. Archive the income account. 3. Attempt to post | Error: account archived; posting blocked | No incomplete entry | Y |
| L-008 | Negative | Payment term rounding — installments do not sum | 3-way 33/33/34 split on prime number amount | 1. Create invoice for 1003 with 33/33/34 payment term. 2. Post. 3. Verify AR line totals | AR lines sum exactly to 1003; rounding distributed correctly on last installment | Odoo must not produce rounding-induced journal imbalance | Y |
| L-009 | Negative | Invalid currency — no exchange rate | Invoice in currency with no active rate for that date | 1. Create invoice in AED (inactive or no rate). 2. Post | Error: no exchange rate available for date; posting blocked | No entry with undefined rate | Y |
| L-010 | Negative | Back-dated entry in locked period via manual journal | User attempts manual journal entry with date in locked period | 1. Navigate to Accounting > Accounting > Journal Entries. 2. New entry. 3. Set date in locked period. 4. Post | Error: locked period; entry blocked | No entry in locked period | Y |
| L-011 | Negative | Reconcile two invoices with wrong partner | Payment for Customer A applied to Customer B invoice | 1. Register payment for Customer A. 2. Apply to Customer B open invoice | System should block or warn: wrong partner on reconciliation; if allowed, AR incorrectly zeroed for wrong customer | Partner-AR mismatch is a compliance risk | Y |
| L-012 | Negative | Post expense report with no expense lines | Empty expense report | 1. Create expense report with no lines. 2. Post | Error: no expense lines; posting blocked or produces empty entry | No meaningless entry created | Y |
| L-013 | Negative | Tax report filed then invoice back-dated into period | Tax period closed/filed; invoice back-dated into filed period | 1. File tax report for January. 2. Create invoice dated in January (back-date). 3. Post | Warning or block: posting to already-filed period should require override; creates amendment risk | Compliance risk if allowed silently | N |
| L-014 | Negative | Delete payment before reconciliation | Payment in draft state | 1. Create payment. 2. Delete before confirming | Allowed; no accounting impact | No entry created (draft) | Y |
| L-015 | Negative | Reconcile already-reconciled invoice | Fully paid invoice | 1. Attempt to apply another payment to a fully paid (reconciled) invoice | System should show no outstanding credits available; reconciliation complete | No double-payment entry | Y |
| L-016 | Negative | Configuration drift — tax changed after invoices posted | Tax rate changed from 12% to 15% | 1. Post invoices at 12%. 2. Change tax rate to 15%. 3. Post new invoices. 4. Verify old invoices unchanged | Existing posted entries unaffected; new invoices use 15%; historical integrity preserved | Immutability of posted entries | Y |
| L-017 | Negative | Journal deleted after entries exist | Journal has posted entries | 1. Attempt to delete journal with existing entries | Blocked: cannot delete journal with entries | Journal integrity maintained | Y |

---

## 4. High-Risk Regression Suite

This suite must pass before every production release or significant configuration change. It covers the minimum viable set of scenarios that validate end-to-end finance correctness.

| Reg ID | Test ID | Scenario | Pass Criteria |
|--------|---------|----------|---------------|
| REG-001 | B-001 | Standard customer invoice — post and verify journal entry | AR debit + Income credit + Tax Payable credit; amounts match; status=Posted |
| REG-002 | C-001 | Standard vendor bill — post and verify journal entry | Expense debit + Tax Receivable debit + AP credit; amounts match; status=Posted |
| REG-003 | B-005 | Tax-included invoice — price extraction correct | Tax base correctly extracted; total = price as entered; journal entry balanced |
| REG-004 | B-004 | Tax-excluded invoice — amounts correct | Subtotal + tax = total; journal entry balanced; tax on correct account |
| REG-005 | C-004 | Withholding tax on vendor bill — AP net correct | EWT deducted from AP; EWT payable account credited; net payment = invoice - withholding |
| REG-006 | D-007, D-008 | Cash basis tax — invoice post vs payment post timing | At invoice: tax in transition. At payment: tax in tax payable. Tax report correct at both stages |
| REG-007 | F-001, G-003 | Payment registration + bank reconciliation | Invoice paid; outstanding account cleared; bank reconciled; zero residual |
| REG-008 | H-004, H-006 | Expense report — post and reimburse | Expense account debited; employee payable credited; reimbursement clears payable |
| REG-009 | B-016 | Full credit note against posted invoice | Credit note reconciles invoice to zero; AR net = 0; income and tax reversed |
| REG-010 | L-001 | Missing income account blocks posting | Error raised; no partial entry; clear message |
| REG-011 | L-004 | Locked period blocks posting | Error raised; no entry in locked period |
| REG-012 | I-008 | Trial balance — debits = credits | Sum of all debit move lines = sum of all credit move lines for period |
| REG-013 | E-002 | Fiscal position tax mapping applied on invoice | Mapped tax used; original tax absent from journal entry |
| REG-014 | B-010 | Installment payment terms — AR lines sum to invoice total | Sum of installment AR lines = invoice total exactly; due dates correct |
| REG-015 | I-001 | Journal items audit for posted invoice | All expected lines present: AR, Income, Tax; no orphan lines |

---

## 5. Automation Strategy

### Must Automate

These scenarios are deterministic, repeatable, and high-volume. Manual testing is insufficient at scale.

| Scenario Group | Reason |
|----------------|--------|
| B-001 to B-008 (basic invoice creation and tax) | Core AR correctness; runs on every release; deterministic accounting outcomes |
| C-001 to C-007 (basic bill creation and payment) | Core AP correctness; same rationale |
| D-001 to D-006 (tax computation variants) | Tax calculation is purely algorithmic; automation can verify journal entry amounts precisely |
| D-007 to D-009 (cash basis timing) | Timing-sensitive; automation can control payment dates and verify transition account state |
| F-001 to F-003 (payment registration) | Core payment flows; deterministic reconciliation outcomes |
| G-003, G-004 (reconciliation match) | Reconciliation is mechanical once data is known; automation can verify outstanding account clearing |
| H-004, H-006 (expense posting and reimbursement) | Deterministic posting and payable clearing |
| I-008 (trial balance check) | Mathematical check; always automatable |
| L-001 to L-004 (negative path — missing config) | Negative paths are precise and repeatable |
| REG-001 to REG-015 (full regression suite) | Full regression must run in CI on every push |

**Automation Framework Recommendation**: Odoo test runner (unittest via `odoo-bin -d test_finance --test-tags finance`) with custom test module `ipai_finance_tests`. Use `TransactionCase` for isolated tests and `SavepointCase` for multi-step scenarios requiring rollback.

### Good to Automate

These have deterministic core logic but require more setup or have UI-dependent steps.

| Scenario Group | Reason |
|----------------|--------|
| E-001 to E-006 (fiscal position tax/account mapping) | Mapping logic is deterministic; setup is the complexity |
| B-009 to B-011 (payment terms and installments) | Due date calculation is algorithmic; installment summing is verifiable |
| K-001, K-002 (PH VAT and EWT) | Localization-specific but deterministic once configured |
| I-001 to I-007 (reporting checks) | Report output can be compared against expected journal item aggregates |
| L-008 (installment rounding) | Mathematical precision test; automation preferred |
| D-015, D-016 (tax report period filter) | Filter behavior deterministic given known data |

### Keep Manual

These require human judgment, external system verification, or are exploratory in nature.

| Scenario Group | Reason |
|----------------|--------|
| B-019 (invoice PDF content) | PDF rendering, font, layout, and legal field placement require visual/human review |
| B-023, B-024 (delivery address, discount window) | Policy-dependent and UI-flow-dependent |
| H-003, H-005 (approval flow UX) | Multi-user approval involves human-in-the-loop role testing |
| J-001 to J-010 (permissions) | Role matrix testing in Odoo is partially automatable but full access control testing requires dedicated security test framework; start manual |
| K-005 to K-010 (EU reverse charge, India TDS, multi-localization) | Legal interpretation and external report format validation; requires compliance review |
| L-013 (back-dated to filed period) | Policy-and-jurisdiction-dependent; human override decision involved |
| G-007 (multi-currency reconciliation) | FX variance judgment; rate freshness validation |
| N/A (localization compliance sign-off) | Any localization output for legal submission requires human sign-off by accountant or tax counsel |

---

## 6. Test Data Design

The following test data set is the minimum required to execute all scenarios in this plan. It must be provisioned in the `test_finance` database before test execution.

### Companies

| Name | Currency | Localization | Tax Period | Notes |
|------|----------|-------------|------------|-------|
| IPAI PH Test | PHP | l10n_ph | Monthly VAT | Primary test company; Philippines BIR-registered |
| IPAI EU Test | EUR | l10n_generic (or l10n_de) | Quarterly VAT | For EU-specific and multi-company tests |

### Customers

| Name | Country | VAT Number | Fiscal Position | Payment Terms | Notes |
|------|---------|------------|----------------|---------------|-------|
| Domestic Customer A | PH | None | Domestic | Net 30 | Standard AR test customer |
| Export Customer B | US | US-EIN | Export Zero-Rate | Net 60 | Triggers export fiscal position |
| EU Customer C | DE | DE123456789 | Intra-EU | Net 30 | EU reverse charge scenarios |
| Installment Customer D | PH | None | Domestic | 50/50 Split | Payment term installment tests |
| Discount Customer E | PH | None | Domestic | 2/10 Net 30 | Cash discount tests |

### Vendors

| Name | Country | VAT Number | Fiscal Position | Default Taxes | Notes |
|------|---------|------------|----------------|---------------|-------|
| Local Vendor A | PH | VAT registered | Domestic | VAT 12%, EWT 2% | Standard AP test vendor |
| Foreign Vendor B | US | None | Import | Import taxes | Foreign vendor; no local VAT reclaim |
| Professional Vendor C | PH | VAT registered | Domestic | VAT 12%, EWT 10% | Higher EWT rate for professionals |
| Exempt Vendor D | PH | VAT exempt | VAT Exempt | None | Zero-tax vendor |

### Employees

| Name | Role | Expense Payment | Notes |
|------|------|-----------------|-------|
| Test Employee A | Staff | Own Money | Standard expense submitter |
| Test Employee B | Manager | Company Money | Can approve expense reports |
| Test Accountant | Accountant | Own Money | Posts expense reports; cannot self-approve |

### Products / Services

| Name | Type | Income Account | Expense Account | Default Sales Tax | Default Purchase Tax | Notes |
|------|------|---------------|-----------------|-------------------|----------------------|-------|
| Service A | Service | 400100 Revenue | 600100 Expense | VAT 12% | VAT 12% | Standard service |
| Service B | Service | 400200 Export Revenue | 600100 Expense | Export 0% | None | Zero-rated service |
| Product C | Storable | 400100 Revenue | 600200 COGS | VAT 12% | VAT 12% | Physical product |
| Exempt Service D | Service | 400300 Exempt Revenue | 600100 Expense | VAT Exempt | None | Exempt service |
| Expense Travel | Service | N/A | 600300 Travel | None | VAT 12% | Expense category product |
| Expense Meals | Service | N/A | 600400 Meals | None | None | Non-VAT expense |

### Taxes

| Name | Type | Rate | Price Include | Tax Account | Notes |
|------|------|------|---------------|-------------|-------|
| VAT 12% Output | Sale | 12% | No | Output VAT Payable | Standard PH output VAT |
| VAT 12% Input | Purchase | 12% | No | Input VAT Recoverable | Standard PH input VAT |
| VAT 10% Included | Sale | 10% | Yes | Output VAT Payable | Price-included test |
| Export Zero-Rate | Sale | 0% | No | N/A (no tax account) | Export zero-rate |
| VAT Exempt | Sale | 0% | No | Exempt account | Exempt (different from zero-rate in reporting) |
| EWT 2% | Purchase | -2% | No | EWT Payable | Expanded withholding tax |
| EWT 10% | Purchase | -10% | No | EWT Payable | Professional services EWT |
| Cash Basis VAT | Sale | 12% | No | Tax Transition → Output VAT | on_payment exigibility |

### Fiscal Positions

| Name | Auto-Apply | Country | Tax Mappings | Account Mappings |
|------|-----------|---------|-------------|------------------|
| Domestic PH | Yes | PH | None | None |
| Export Zero-Rate | Yes | non-PH | VAT 12% → Export 0% | 400100 → 400200 |
| VAT Exempt | Manual | N/A | VAT 12% → VAT Exempt | 400100 → 400300 |
| EU Intra-Community | Yes | EU states | VAT 12% → 0% | None |

### Journals

| Name | Type | Currency | Notes |
|------|------|----------|-------|
| Customer Invoices | Sale | PHP | Primary AR journal |
| Vendor Bills | Purchase | PHP | Primary AP journal |
| Bank PH — BDO | Bank | PHP | Primary bank journal |
| Bank USD | Bank | USD | Foreign currency bank |
| Cash (Petty Cash) | Cash | PHP | Petty cash journal |
| Miscellaneous | General | PHP | Manual journal entries |
| Expense Journal | Purchase | PHP | For expense report postings |

### Payment Terms

| Name | Description |
|------|-------------|
| Immediate | Due on invoice date |
| Net 30 | Balance due in 30 days |
| Net 60 | Balance due in 60 days |
| 50/50 30 Days | 50% now, 50% in 30 days |
| 33/33/34 | Three installments |
| 2/10 Net 30 | 2% discount if paid within 10 days; full balance due in 30 |

### Currencies

| Code | Active | Notes |
|------|--------|-------|
| PHP | Yes | Company currency for PH company |
| EUR | Yes | Company currency for EU company; foreign for PH company |
| USD | Yes | Common foreign currency |
| JPY | Yes | High-volume, no-decimal currency (edge case) |

### Banks / Payment Methods

| Bank | Account Number | Journal |
|------|---------------|---------|
| BDO | 1234-5678-9012 | Bank PH — BDO |
| Virtual USD Account | USD-001 | Bank USD |

### Expense Categories

| Category | Product | Account | Tax |
|----------|---------|---------|-----|
| Travel | Expense Travel | 600300 | VAT 12% |
| Meals | Expense Meals | 600400 | None |
| Office Supplies | Expense Supplies | 600500 | VAT 12% |

---

## 7. Localization / Compliance Considerations

### VAT vs Non-VAT Regimes

Odoo 18 Finance behavior differs fundamentally between VAT-registered and non-VAT-registered company configurations:

- **VAT-registered companies** use output VAT accounts (payable) and input VAT accounts (recoverable). Tax reports produce VAT return filings. Zero-rated and exempt transactions must be separately tracked in the tax report.
- **Non-VAT regimes** (e.g., small business exemptions in some jurisdictions) use simpler tax structures. The fiscal localization may install taxes but the company may not be legally required to collect or remit VAT.
- **Test implication**: All tax scenarios must be run against a VAT-registered company. Non-VAT scenarios must be run separately if applicable to the deployment.

### Withholding-Sensitive Regimes

The following country-specific withholding behaviors require dedicated test coverage beyond the generic scenarios in this plan:

**Philippines (BIR)**:
- Expanded Withholding Tax (EWT) per RR 11-2018: rates vary by income type (professional services 10%, goods 1-2%, rent 5%, etc.)
- Creditable Withholding Tax: must appear in Form 2307 per transaction
- VAT Withholding (5%): applicable to government entities purchasing from VAT-registered suppliers
- Final Withholding Tax: for non-resident foreign corporations
- BIR quarterly filing: alphalist of payees, Form 1601-EQ

**India**:
- TDS (Tax Deducted at Source): section-specific rates under Income Tax Act
- TCS (Tax Collected at Source): applicable on specific goods/services
- GST (IGST/CGST/SGST): multi-level GST requires separate component tracking

**Brazil**:
- ICMS/ISS/PIS/COFINS: multiple federal and state-level taxes on single transaction
- Nota Fiscal: legal electronic invoice document with specific format requirements

**Test implication**: For any deployment in a withholding-sensitive jurisdiction, the EWT/TDS/withholding scenarios (C-004, D-010, K-002) are critical-priority and must be validated by a local tax professional in addition to QA.

### Fiscal Position Localization

Each country's localization package installs its own fiscal positions. These must be validated after installation:
- Tax mappings match local legal requirements
- Account mappings use the correct COA accounts from the localization
- Auto-detection rules match the correct partner attributes (country, VAT status, etc.)

### Localization-Specific Accounting/Legal Outputs

| Jurisdiction | Required Output | Odoo 18 Mechanism | Validation Required |
|-------------|-----------------|-------------------|---------------------|
| Philippines | BIR Form 2307 (CWT certificate) | l10n_ph module | Per-transaction EWT amount and payee data |
| Philippines | Monthly VAT Return | Tax report with VAT format | Output/Input VAT totals by period |
| EU | EC Sales List | l10n_eu_oss or country module | Intra-community supply amounts per country |
| EU | VAT Return | Tax report | Box-level amounts per jurisdiction |
| India | GSTR-1/3B | l10n_in module | HSN-wise sales summary |
| Generic | Audit trail | Chatter + journal items | All changes traceable to user + timestamp |

### Documentation / Evidence Expectations

For production deployment sign-off, the following evidence must be collected and stored in `docs/evidence/`:
1. Posted journal entry for each scenario showing all move lines
2. Tax report screenshot or export for each test period
3. Bank reconciliation summary showing zero outstanding
4. Expense report with attached receipts (for reimbursement scenarios)
5. Role access verification: screenshot of blocked action for unauthorized user
6. Trial balance showing zero difference for test period

---

## 8. Gaps and Assumptions

### Company Policy Unknowns

| Topic | Gap | Resolution Required |
|-------|-----|---------------------|
| Cash discount accounting | Odoo 18 offers two methods: write-off at payment vs separate discount account. Company policy must specify which method. | Finance team decision; impacts G/L account for discount |
| Expense approval threshold | Does the approval flow require manager approval for all expenses or only above a threshold? | HR policy document |
| Withholding tax remittance | When is EWT remitted to BIR? Monthly? Quarterly? This affects cash flow reporting. | Tax policy document |
| Invoice numbering format | Does the company require a specific invoice number prefix per journal or per year? | Accounting policy |
| Foreign exchange gain/loss account | Which account captures FX gain/loss on multi-currency reconciliation? Must be configured. | Chart of accounts decision |

### Localization Package Gaps

| Topic | Gap | Resolution Required |
|-------|-----|---------------------|
| l10n_ph EWT coverage | OCA l10n_ph may not cover all BIR EWT income codes; delta module `ipai_ph_ewt` may be needed | Verify BIR RR 11-2018 coverage against installed module |
| l10n_ph Form 2307 generation | Automatic Form 2307 PDF generation may require custom module | Verify if l10n_ph includes this or if ipai_* delta needed |
| Cash basis VAT and PH compliance | PH BIR requires accrual VAT reporting for VAT-registered entities; cash basis VAT may not be BIR-compliant | Legal review required |
| Multi-company consolidation | Odoo CE does not include enterprise-grade intercompany consolidation; behavior of AR/AP between companies must be verified | Scope limitation acknowledgment |

### Tax / Legal Interpretation Gaps

| Topic | Gap |
|-------|-----|
| Zero-rated vs exempt in PH tax report | BIR requires separate reporting columns; test must verify Odoo tax report separates these correctly |
| EWT certificate timing | BIR requires Form 2307 issued per payment; Odoo may issue per bill; reconcile this gap |
| Late payment interest | Odoo CE does not automatically compute late payment interest; if applicable, manual journal is required |
| Cross-period credit note | Credit note in current period against invoice in prior period has different treatment in some jurisdictions; verify localization handles this |

### Accounting Controls Gaps

| Topic | Gap |
|-------|-----|
| Four-eyes principle on payments | Odoo CE does not enforce dual-approval for payments by default; this is a policy gap if required |
| Expense receipt validation | Odoo stores receipts as attachments but does not validate receipt authenticity; human review required |
| Bank statement matching quality | Auto-match confidence thresholds in Odoo 18 reconciliation are not always documented; test matching precision |

---

## 9. Top 25 Finance Scenarios Most Likely to Fail in Production

Ranked by operational risk (probability of failure × business impact):

| Rank | Scenario ID | Description | Why It Fails in Production |
|------|-------------|-------------|---------------------------|
| 1 | D-007, D-008 | Cash basis tax — invoice posts but tax not in tax report until payment | Accountants expect tax at invoice time; cash basis timing misunderstood; tax report gaps discovered only at filing |
| 2 | C-004, D-010 | Withholding tax (EWT) — net AP amount incorrect | EWT rate misconfigured or applied to wrong income type; BIR compliance failure; audited and penalized |
| 3 | L-001 | Missing income account blocks invoice posting | Deployed with incomplete product setup; invoicing halted in production |
| 4 | E-008 | Fiscal position changed after lines added — stale taxes | Tax lines not refreshed when fiscal position changed; wrong tax posted; requires manual correction of posted entries |
| 5 | B-011, L-008 | Installment payment terms — rounding error on non-round amounts | Three-way split produces journal imbalance; Odoo blocked from posting or produces 0.01 discrepancy |
| 6 | G-003, G-009 | Bank reconciliation — outstanding account not cleared | Payment registered but not matched to bank statement; outstanding account grows indefinitely; bank balance never reconciles |
| 7 | F-010 | Multi-currency payment — FX gain/loss account not configured | Payment in foreign currency triggers FX entry; FX account missing; posting blocked or goes to undefined account |
| 8 | B-016, B-017 | Credit note reconciliation — partial refund leaves wrong residual | Partial credit note applied incorrectly; AR residual incorrect; AR aging overstated or understated |
| 9 | I-009, L-004 | Locked period — back-dated entries | Year-end close followed by back-dated invoice from operations team; locked period not enforced or bypassed |
| 10 | H-009 | Expense posted to wrong account | Expense category product misconfigured; expense hits wrong G/L; P&L incorrect; discovered in audit |
| 11 | K-002 | Philippines EWT rate misapplied | Wrong EWT rate for income type; under or over-withheld; BIR penalty risk; Form 2307 incorrect |
| 12 | C-012, L-005 | Duplicate vendor bill — double payment | Duplicate reference not caught; vendor paid twice; AP overstated; cash flow impact |
| 13 | D-005, D-006 | Tax rounding mismatch — per-line vs global | Company switches rounding method; existing invoices inconsistent with new method; tax report line totals differ from journal entries |
| 14 | A-016, E-007 | Auto-detected fiscal position not updated when partner country changes | Partner updated to new country; fiscal position not refreshed; wrong taxes on future invoices until caught |
| 15 | B-022 | Cash discount — discount account not configured | Payment with discount registered; discount account missing; posting fails or hits wrong account |
| 16 | G-007 | Multi-currency bank reconciliation — FX difference posted to wrong account | FX gain/loss account not set on bank journal; reconciliation posts difference to suspense or undefined account |
| 17 | H-004 | Expense journal entry — employee payable account missing | Employee not linked to partner with payable account; expense posting fails silently or hits wrong account |
| 18 | L-016 | Tax rate changed — historical invoices appear incorrect | Tax reconfigured; old invoices seem wrong but are correct at historical rate; confusion in audit |
| 19 | I-014 | Invoice sequence gaps after cancellation | Sequence skipped after reset-to-draft; auditor flags non-sequential numbering as compliance issue |
| 20 | B-010, F-012 | Installment reconciliation — wrong installment line cleared | Payment matched to wrong installment due date; incorrect aging; customer dispute |
| 21 | K-001 | PH VAT 12% — zero-rated vs exempt distinction in tax report | Both use 0% on invoice but must be in separate BIR reporting columns; misconfigured tax type conflates them |
| 22 | L-009 | No exchange rate for invoice currency on invoice date | Finance team creates USD invoice; no rate loaded for that specific date; posting blocked; invoice delayed |
| 23 | J-001, J-003 | Role misconfiguration — billing user can post | Access rights not fully configured post-deployment; billing staff posting invoices without accountant review |
| 24 | G-011 | Duplicate bank statement import | Statement imported twice; bank account overstated; reconciliation impossible until manually corrected |
| 25 | A-007 | Invoice sequence reuse after reset-to-draft | Invoice reset to draft in certain configurations; re-posted with different sequence; legal document numbering gap |

---

*End of Odoo 18 Finance Test Plan — Version 1.0*  
*File: /Users/tbwa/Documents/GitHub/Insightpulseai/odoo/docs/testing/ODOO18_FULL_FINANCE_TEST_PLAN.md*
