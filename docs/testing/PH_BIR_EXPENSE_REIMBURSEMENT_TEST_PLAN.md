# PH/BIR Expense, Reimbursement, Withholding, and VAT Test Plan
## Odoo 18 CE — Philippines Deployment — Production-Grade

**Version**: 1.0.0
**Date**: 2026-04-09
**Scope**: Expenses, Expense Reports, Reimbursements, Company-Paid Expenses, Customer Re-invoicing, VAT Treatment, Withholding Tax, BIR Compliance
**Compliance anchors**: BIR Form 2307, BIR Form 1601-C, BIR Form 2550Q, RMC 36-2021

---

## 1. Executive Summary

### Major PH/BIR-Sensitive Risk Zones

**Risk Zone 1 — VAT treatment misconfiguration on expense categories.**
Odoo 18 CE expense categories carry tax configurations that drive input VAT posting. In a PH deployment, the distinction between VATable expenses (12% VAT), VAT-exempt expenses, and expenses from non-VAT-registered suppliers is operationally critical. Misconfigured categories silently post incorrect input VAT amounts, corrupting the 2550Q support schedule. This is the single highest-volume silent failure mode.

**Risk Zone 2 — Withholding tax boundary confusion between compensation and vendor/service income.**
BIR Form 1601-C covers withholding on compensation. Withholding on supplier/service payments uses different ATCs and flows through accounts payable, not payroll. Odoo's expense module straddles both domains: employee reimbursements can be confused with compensation, and company-paid expenses with supplier invoices. Misclassification produces incorrect withholding certificates and incorrect BIR return allocations.

**Risk Zone 3 — BIR Form 2307 generation and traceability.**
Under RMC 36-2021, government entities withholding creditable VAT must issue 2307 using VAT-withholding ATCs, which serves as proof for the vendor's VAT credit claim on 2550Q. In Odoo CE, 2307 generation is not native — it depends on PH localization modules (OCA l10n_ph or ipai equivalents). If the underlying journal entries do not carry the correct ATC, tax base, and withheld amount, downstream certificate generation fails silently or produces an incorrect certificate.

**Risk Zone 4 — Employee-paid vs. company-paid flow divergence.**
These two flows post to different liability accounts (employee payable vs. accounts payable), involve different counterparties, and have different withholding implications. A configuration error that routes a company-paid expense through the employee reimbursement payable silently creates reconciliation failures and incorrect withholding output.

**Risk Zone 5 — Re-invoicing to customers with fiscal position mismatch.**
When expenses are re-invoiced to customers, Odoo applies the customer's fiscal position, which may remap taxes. For government customers, this may trigger VAT withholding rules. Failure to configure fiscal positions correctly causes incorrect tax on the customer invoice, which in turn affects the VAT return and any 2307 that the government customer must issue.

**Risk Zone 6 — Audit trail gaps from expense to BIR return.**
A production BIR audit requires traceability from the expense receipt/OR through the expense line, journal entry, tax line, and finally into the VAT return or withholding return. Odoo's standard audit trail is sufficient if correctly configured, but broken attachment links, missing TIN/VAT registration data on suppliers, or incorrect account mappings break this chain at any point.

**Most Likely Production Failure Areas (in order):**
1. Input VAT account not set on expense tax, causing blocked posting
2. Withholding tax ATC not mapped, producing certificates with blank ATC
3. Government customer re-invoicing applying wrong tax / no 2307 output
4. Employee reimbursement liability account shared with AP, making reconciliation ambiguous
5. Mixed-tax expense report with rounding differences causing journal imbalance
6. Expense posted in locked period because approval delayed
7. Company-paid expense not linked to supplier bill, breaking withholding traceability
8. Duplicate reimbursement payment due to missing reconciliation check
9. VAT-exempt expense wrongly claiming input VAT due to category misconfiguration
10. Stale draft expense picking up new tax configuration after approval-chain delay

---

## 2. Coverage Map

| Area | Sub-area | Why it matters | PH/BIR sensitivity | Risk level |
|------|----------|----------------|--------------------|------------|
| A. Master data | Expense category tax config | Drives all downstream VAT and withholding | HIGH — wrong taxes corrupt 2550Q | CRITICAL |
| A. Master data | Account mapping | Determines ledger posting | HIGH — wrong accounts cause imbalance | CRITICAL |
| A. Master data | ATC mapping on withholding tax | Needed for 2307 and return filing | HIGH — blank ATC = unusable certificate | CRITICAL |
| B. Expense capture | Source document / OR support | BIR requires OR/SI for valid input VAT | HIGH — no OR = disallowed input VAT | HIGH |
| B. Expense capture | Supplier TIN/VAT registration | Required for withholding and VAT input | HIGH — missing TIN = cannot generate 2307 | HIGH |
| B. Expense capture | Multi-currency | Exchange rate differences affect tax base | MEDIUM — base amount must be in PHP for BIR | MEDIUM |
| C. Expense report | Mixed tax treatment in one report | Rounding and line-level consistency | MEDIUM — affects 2550Q input amounts | HIGH |
| C. Expense report | Workflow state transitions | Approval chain integrity | LOW direct BIR, HIGH operational | MEDIUM |
| D. Approval / SOD | Role boundaries | Prevents unauthorized financial postings | LOW direct BIR, HIGH audit | MEDIUM |
| E. Employee reimbursement | VAT on reimbursable expense | Input VAT creditable only if compliant | HIGH — directly feeds 2550Q | CRITICAL |
| E. Employee reimbursement | Partial reimbursement | Reconciliation integrity | MEDIUM — affects payable aging | MEDIUM |
| F. Company-paid | Withholding on supplier/service | Supplier withholding must be correct ATC | HIGH — feeds 2307 and 1601-EQ | CRITICAL |
| F. Company-paid | Liability account routing | Must not mix with employee payable | MEDIUM — reconciliation failure | HIGH |
| G. VAT treatment | Input VAT creditable vs non-creditable | Directly affects 2550Q claim | CRITICAL | CRITICAL |
| G. VAT treatment | VAT rounding | BIR expects specific rounding treatment | HIGH — rounding errors in return | HIGH |
| G. VAT treatment | Price-included vs excluded VAT | Affects tax base computation | HIGH — incorrect base in 2550Q | HIGH |
| H. Withholding | Compensation vs vendor/service boundary | 1601-C vs 1601-EQ/1601-FQ scope | CRITICAL — wrong return = BIR penalty | CRITICAL |
| H. Withholding | ATC correctness | Drives certificate content | CRITICAL | CRITICAL |
| H. Withholding | Government vs private sector | Government must withhold; rules differ | HIGH — RMC 36-2021 applies | HIGH |
| I. BIR documents | 2307 traceability | Certificate of creditable tax withheld | CRITICAL | CRITICAL |
| I. BIR documents | 2550Q input VAT support | Input VAT schedule accuracy | CRITICAL | CRITICAL |
| I. BIR documents | 1601-C boundary | Must not include vendor withholding | CRITICAL | CRITICAL |
| J. Re-invoicing | Fiscal position for government customer | VAT withholding rules for government | HIGH — RMC 36-2021 applies | HIGH |
| J. Re-invoicing | Double-counting prevention | Expense and invoice must not both claim VAT | HIGH | HIGH |
| K. Journal integrity | Correct accounts per flow type | Ledger accuracy | HIGH — audit trail | HIGH |
| K. Journal integrity | Locked period | Posting date control | MEDIUM | MEDIUM |
| L. Reimbursement payment | Reconciliation | Payable clearance | MEDIUM — aging accuracy | HIGH |
| L. Reimbursement payment | Duplicate prevention | Financial control | MEDIUM | HIGH |
| M. Reporting | Audit trail completeness | BIR audit support | CRITICAL | CRITICAL |
| M. Reporting | VAT/withholding report totals | Reconcile to returns | CRITICAL | CRITICAL |
| N. Negative / failure | Missing tax account | Blocked posting | HIGH — operational | HIGH |
| N. Negative / failure | Deleted tax after approval | Silent miscalculation | HIGH | HIGH |

---

## 3. Scenario Matrix

### A. Expense Category and Master Data Setup

| ID | Area | Scenario | Preconditions | Steps | Expected result | Accounting impact | BIR/compliance impact | Auto (Y/N) |
|----|------|----------|---------------|-------|-----------------|-------------------|-----------------------|------------|
| A-001 | Category setup | Create expense category with no taxes configured | Company is VAT-registered; category intended for non-VAT items | 1. Create category "Meals - Non-VAT Supplier". 2. Set product account to meals expense GL. 3. Leave tax field empty. 4. Create expense using this category. 5. Submit, approve, post. | Expense posts with zero VAT. No input VAT line appears in journal entry. Report shows zero VAT on this line. | DR Meals Expense (full amount), CR Employee Payable (full amount). No tax line. | Correct for non-VAT supplier expenses. Does not feed 2550Q input VAT schedule. Auditor can verify no input VAT was claimed. | Y |
| A-002 | Category setup | Create expense category with 12% VAT (price-excluded) | Company is VAT-registered; VAT-registered supplier expected | 1. Create category "Transportation - VATable". 2. Assign 12% input VAT tax (price-excluded). 3. Map input tax account to "Input VAT - Local Purchases". 4. Create expense for PHP 1,120 (PHP 1,000 base + PHP 120 VAT). 5. Post. | Journal entry shows: DR Transportation PHP 1,000, DR Input VAT PHP 120, CR Employee Payable PHP 1,120. | Three-line journal: expense account, input VAT account, employee payable. Correct split. | Input VAT PHP 120 feeds 2550Q Box 8B (Local Purchases of Services) or appropriate box. Tax base PHP 1,000 traceable. | Y |
| A-003 | Category setup | Create expense category with multiple taxes (VAT + municipal tax) | Company in LGU with local business tax on services | 1. Create category with 12% VAT + 3% local tax. 2. Create expense. 3. Post. | Both taxes computed and posted to separate tax accounts. Total payable = base + VAT + local tax. | Journal has expense line, VAT line, local tax line, payable line. All must balance. | VAT portion feeds 2550Q; local tax does not. Separate accounts required for clean separation. | Y |
| A-004 | Category setup | Expense category with VAT configured but wrong input tax account (maps to output VAT account) | Misconfigured chart of accounts | 1. Create category with 12% VAT, but input tax account set to "Output VAT Payable" by mistake. 2. Create expense. 3. Attempt to post. | System should post (Odoo does not validate account type here by default), but resulting entry is incorrect: DR Output VAT Payable (wrong). Finance must catch via reconciliation review. | Incorrect posting: output VAT account debited instead of input VAT account. Balance sheet impact is wrong. | Input VAT will not appear correctly in 2550Q input schedule. Must be caught before filing. | N — requires human chart review |
| A-005 | Category setup | Expense category with withholding-sensitive configuration | Category for professional fees subject to 2% EWT (ATC WC158) | 1. Create category "Professional Fees". 2. Assign withholding tax rule: 2% on gross amount, ATC WC158. 3. Mark as "company-paid" type. 4. Create expense linked to external service provider. 5. Post. | Withholding tax line appears: DR Professional Fees (gross), CR AP Payable (net), CR Withholding Tax Payable (2% of gross). ATC WC158 stored on tax line. | Three-line company-paid journal. AP = gross minus withholding. Withholding payable = 2%. | ATC WC158 drives 2307 certificate generation. Must be present and correct in journal move. Feeds 1601-EQ return. | Y |
| A-006 | Category setup | Expense category for employee reimbursement only, no withholding | Category for meal allowances reimbursed per diems | 1. Create category "Per Diem - Meal Allowance". 2. Set as employee reimbursement. 3. No withholding tax. 4. Create and post expense. | Posts to employee payable, no withholding line. No 2307 generated. | DR Meal Allowance Expense, CR Employee Payable. | Per diems subject to de minimis rules may be non-taxable. No withholding on reimbursement of actual costs — this must be policy-confirmed. Not a 1601-C line unless it is disguised compensation. | N — policy-dependent |
| A-007 | Category setup | Category eligible for customer re-invoicing | Sales project — travel recharged to client | 1. Create category "Project Travel - Rechargeable". 2. Enable "Re-Invoice Expenses" on category. 3. Link expense to sale order/project. 4. Create and post expense. 5. Generate customer invoice from expense. | Customer invoice created with expense line. Tax on customer invoice driven by customer fiscal position. | Expense DR + employee payable CR for expense side. Customer invoice: DR Receivable, CR Revenue/Expense Recovery, CR Output VAT if applicable. | Customer invoice taxes must be correct. If government customer, they withhold from payment; 2307 expected from them. Revenue recognition must not double-count. | Y |
| A-008 | Category setup | Category mapped to wrong expense account (maps to asset instead of expense) | GL misconfiguration | 1. Create category with account set to a fixed asset GL. 2. Create and post expense. | Expense posts to asset account instead of P&L. Period expenses understated. | DR Fixed Asset (wrong), CR Payable. P&L not hit. | BIR audit will question asset treatment for an operating expense. De minimis threshold applies for capitalization. | N — requires human GL review |
| A-009 | Category setup | Inactive/deprecated expense category | Category was used historically; now marked inactive | 1. Mark category as inactive. 2. Attempt to create new expense using this category. | System prevents selection of inactive category on new expense. Existing posted expenses retain historical data. | No new postings. Historical entries unaffected. | Audit trail on historical entries remains. No new entries created under deprecated category. | Y |
| A-010 | Category setup | Category with PH/BIR reporting tag configured | OCA l10n_ph or ipai module assigns ATC or VAT schedule tag | 1. Create category with BIR tag = "Local Purchase of Services". 2. Create expense. 3. Run VAT return support schedule. | Expense appears in correct BIR schedule section. | Normal posting. | Critical: if tag is wrong, expense appears in wrong 2550Q box. | Y |

---

### B. Expense Capture and Source Documents

| ID | Area | Scenario | Preconditions | Steps | Expected result | Accounting impact | BIR/compliance impact | Auto (Y/N) |
|----|------|----------|---------------|-------|-----------------|-------------------|-----------------------|------------|
| B-001 | Expense capture | Employee-paid expense with valid OR (Official Receipt) attached | Employee has receipt from VAT-registered supplier with OR number, date, TIN, amount | 1. Employee creates expense. 2. Attaches scanned OR. 3. Fills in OR number, supplier TIN. 4. Submits. | Expense accepted with attachment. OR number and supplier TIN visible in expense record. | Pending posting — no accounting impact until approved and posted. | OR is the BIR-required source document for creditable input VAT. Absence of OR = disallowed input VAT claim. OR number should appear in journal entry narration for audit trail. | Y — create, N — attachment quality review |
| B-002 | Expense capture | Employee-paid expense without any receipt | Policy requires receipt for all expenses above PHP 500 | 1. Employee creates expense for PHP 1,500 with no attachment. 2. Submits. | If policy enforcement is active, system rejects or flags missing attachment. If not enforced by system, it reaches approver with warning. Manager must enforce. | No accounting impact. | Without OR, input VAT is not creditable by BIR even if amount is posted. Systematic enforcement must either block or flag for manual review. | Y — flag; N — block (policy dependent) |
| B-003 | Expense capture | Company-paid expense with formal supplier invoice (SI) | AP department pays supplier directly; expense linked to SI | 1. Create expense record linked to company-paid flow. 2. Attach supplier invoice with SI number, TIN, VAT amount. 3. Process through approval. 4. Post. | SI number and supplier TIN carried through to journal entry. Input VAT posted from SI, not from employee receipt. | DR Expense, DR Input VAT, CR AP Payable. No employee payable. | SI is primary BIR source document for purchases from VAT-registered supplier. SI number must appear in BIR purchase schedule (SLS/SLP for VAT return). | Y |
| B-004 | Expense capture | Expense with OR/SI showing incomplete supplier tax information (no TIN on document) | Supplier is informal sector or TIN not printed on receipt | 1. Create expense. 2. Attach receipt without supplier TIN. 3. Mark TIN field as blank. 4. Submit. | System should warn that supplier TIN is missing. Approver sees flag. Finance notes that input VAT from this expense is potentially disallowed. | Expense can still be posted as an operating expense. Input VAT may be posted but is at risk of disallowance. | BIR disallows input VAT where supplier TIN cannot be verified. Finance must decide: post without VAT or accept disallowance risk. | N — requires human judgment |
| B-005 | Expense capture | Expense with TIN and VAT data fully present on source document | VAT-registered supplier, complete OR with TIN, amount, VAT breakdown | 1. Create expense. 2. Enter supplier TIN, OR number, base amount, VAT amount. 3. Submit, approve, post. | All tax data carried through. Journal entry reflects correct amounts. Supplier TIN stored against move. | Standard three-line entry: expense + input VAT + payable. | Fully traceable to 2550Q input schedule. Supports BIR audit. Supplier's TIN linkage enables SLS/SLP reconciliation. | Y |
| B-006 | Expense capture | Single-line expense, single tax, straightforward case | Employee transportation, PHP 560 (PHP 500 base + PHP 60 VAT) | 1. Create expense with one line. 2. Tax auto-applies from category. 3. Post. | DR Transportation PHP 500, DR Input VAT PHP 60, CR Employee Payable PHP 560. Balanced. | Simple three-line journal. | PHP 60 feeds 2550Q input VAT. PHP 500 is the expense base. | Y |
| B-007 | Expense capture | Multi-line expense in one expense record (different categories on same form) | Note: Odoo 18 expense forms are one expense per product/category; reports aggregate multiple expenses. This scenario tests an expense report aggregating multiple lines. See also C-group. | 1. Employee creates three separate expenses: meals (no VAT), transport (12% VAT), hotel (12% VAT). 2. Groups into one expense report. 3. Posts. | Three separate journal entries or one consolidated entry per posting behavior. VAT lines present only for VATable items. | Meals: two-line entry (expense + payable). Transport and hotel: three-line entries each. | Mixed-tax report is the most common real-world scenario. Each line must correctly flow to 2550Q or non-VAT schedules as appropriate. | Y |
| B-008 | Expense capture | Expense with mixed taxable and non-taxable lines in one report | Same report: one VATable item, one VAT-exempt item, one non-VAT-supplier item | 1. Create expenses: one with 12% VAT, one with VAT-exempt tax, one with no tax. 2. Combine in report. 3. Post. | Each line posts with its own tax treatment. No cross-contamination. Total payable = sum of individual amounts. | Multiple journal entries. Input VAT only appears for the VATable line. | 2550Q input schedule only includes VATable line's input VAT. VAT-exempt and non-VAT lines go to non-creditable or no-VAT schedule. | Y |
| B-009 | Expense capture | Multi-currency expense (employee paid in USD, company reports in PHP) | Employee travels internationally, pays in USD | 1. Create expense in USD. 2. System applies exchange rate (BSP rate or company-configured rate). 3. Convert to PHP. 4. Post. | PHP equivalent computed from USD amount using configured rate. Journal entry in PHP. Exchange rate difference visible if rate changes between expense date and posting date. | Expense and payable in PHP. If rate differs at payment date, exchange gain/loss posted. | BIR returns are in PHP. Exchange rate used must be documented for audit. Rate source (BSP) must be traceable. Input VAT base is the PHP-converted amount. | N — rate sourcing requires human verification |
| B-010 | Expense capture | Expense with unreadable/corrupted attachment | File attached but cannot be opened | 1. Employee attaches a corrupted PDF as receipt. 2. Submits. | System accepts file (Odoo does not validate content). Approver must manually verify attachment is readable. If policy enforcement exists (ipai module), flag raised. | No accounting impact. | BIR requires legible source documents. A corrupted attachment does not satisfy OR requirement. Must be caught at approval stage. | N — requires human review |
| B-011 | Expense capture | Expense with amount of zero | Edge case: expense created with zero amount | 1. Employee creates expense with amount = 0. 2. Submits. | Odoo should warn or block zero-amount expense. If allowed, posts with zero amounts — no financial impact. | Zero-amount journal entry or blocked posting. | No BIR impact, but zero-amount expenses pollute audit trail and should be prevented. | Y |
| B-012 | Expense capture | Expense with negative amount | Employee tries to enter negative expense as a "credit" | 1. Employee enters negative amount in expense field. 2. Submits. | Odoo 18 should prevent negative expense amounts at the UI validation level. Check if this is enforced. | If allowed: reversed journal lines. Payable becomes receivable — unexpected. | Negative expense amounts can manipulate reported expense totals. Must be prevented or controlled. | Y |
| B-013 | Expense capture | Expense with invalid quantity (zero or negative units) | Expense uses quantity × unit price (e.g., 0 units of hotel night) | 1. Create expense with quantity = 0. 2. Submit. | System should warn: total = 0. | Same as zero amount. | Same as B-011. | Y |

---

### C. Expense Report Workflow

| ID | Area | Scenario | Preconditions | Steps | Expected result | Accounting impact | BIR/compliance impact | Auto (Y/N) |
|----|------|----------|---------------|-------|-----------------|-------------------|-----------------------|------------|
| C-001 | Report workflow | Create expense report from a single expense | One approved expense exists | 1. Employee selects expense. 2. Creates report. 3. Submits. | Report in "Submitted" state. One expense line. Total matches expense amount. | No accounting impact yet. | Source document reference (OR/SI) accessible from report. | Y |
| C-002 | Report workflow | Create expense report from multiple expenses of same category | Five transport expenses from one trip | 1. Employee selects all five transport expenses. 2. Creates single report. 3. Submits. | Report shows five lines, total is sum. Single category, consistent tax treatment. | Upon posting: one journal entry per report or one per expense line depending on configuration. | All five OR references traceable from one report. Simplified audit trail. | Y |
| C-003 | Report workflow | Expense report with mixed categories | One hotel (12% VAT), one meals (no VAT), one registration fee (VAT-exempt) | 1. Create report with three different category types. 2. Submit. 3. Approve. 4. Post. | Three separate tax treatments preserved. Journal entries correctly segregated. | Hotel: DR Expense + DR Input VAT + CR Payable. Meals: DR Expense + CR Payable. Registration: DR Expense + CR Payable (VAT-exempt, no input VAT credit). | 2550Q: only hotel input VAT included. Critical that VAT-exempt is not mistakenly included in creditable input VAT schedule. | Y |
| C-004 | Report workflow | Expense report with mixed tax treatment in one category (some lines have OR, some do not) | Same category but different supplier VAT statuses | 1. Create report where some lines from VAT-registered suppliers (with input VAT), others from non-VAT suppliers (no input VAT). 2. Post. | Lines correctly reflect their individual tax setups. No blanket VAT application across all lines. | Two types of journal entries within one report posting. | Auditor can trace which lines claimed input VAT and which did not. | N — requires line-level review |
| C-005 | Report workflow | Expense report with mixed currencies | PHP and USD expenses combined | 1. Create one PHP expense and one USD expense. 2. Combine in one report. 3. Post. | All amounts converted to company currency (PHP). Report total in PHP. Exchange rates applied per-line using expense date rate. | Each currency line converted independently. No cross-currency netting. | BIR amounts are PHP. Rate documentation required per line. | Y |
| C-006 | Report workflow | Submit draft report | Employee creates report and submits | 1. Create report in draft. 2. Click Submit. 3. Verify state = "Submitted" and manager is notified. | State transitions correctly. Cannot be edited after submission without rejection. | No accounting impact. | Submission timestamp is audit trail anchor. | Y |
| C-007 | Report workflow | Manager rejects report | Report submitted; manager finds policy violation | 1. Manager opens submitted report. 2. Clicks Refuse. 3. Provides reason. 4. Employee notified. | Report returns to "Draft" or "Refused" state. Employee can see rejection reason. | No accounting impact. | Rejection reason is part of audit trail. Must be preserved. | Y |
| C-008 | Report workflow | Employee modifies report after rejection and resubmits | Report refused; employee corrects amount and reattaches OR | 1. Employee opens refused report. 2. Modifies expense line (corrects amount). 3. Reattaches correct OR. 4. Resubmits. | Report moves to Submitted state again. History of previous submission and rejection visible. | No accounting impact. | Revision history important for BIR audit. Previous version should not be deleted. | N — revision trail requires manual verification |
| C-009 | Report workflow | Stale draft report after expense category tax configuration changes | Report created in draft with old tax; admin changes tax on category before report is approved | 1. Employee creates expense report in draft with 12% VAT. 2. Admin changes category to VAT-exempt. 3. Employee submits without re-checking. 4. Approver approves. 5. Accountant posts. | Odoo applies tax at time of posting from the expense line as recorded at draft time. Must verify whether category change propagates to existing draft expenses. If it does, the draft report now has incorrect tax. | If tax was changed on category and propagated: journal entry posts with updated (wrong for this period) tax. If not propagated: original tax preserved on draft line. | Silent tax change on draft is a major BIR risk. The expense may post with a tax that no longer matches the OR in hand. Must be verified against Odoo 18 behavior. | Y — verify behavior; N — remediation |
| C-010 | Report workflow | Empty report (no expense lines) | Employee creates report shell without adding expenses | 1. Create report with no expense lines. 2. Attempt to submit. | Odoo should prevent submission of empty report. Validation error expected. | No accounting impact. | No BIR impact. | Y |
| C-011 | Report workflow | Report with duplicate expense (same OR, same amount, same date submitted twice) | Employee accidentally creates two expenses from the same receipt | 1. Create two expenses with identical OR number, supplier, amount, date. 2. Add both to one report. 3. Submit. | System should warn or flag potential duplicate. If no deduplication logic: both lines are accepted, both are posted, input VAT is claimed twice. | Double-posting of expense and input VAT. | Double input VAT claim is a 2550Q error. BIR will identify this via SLS/SLP reconciliation. Duplicate OR number detection is critical. | N — requires deduplication logic check |

---

### D. Approval and Segregation of Duties

| ID | Area | Scenario | Preconditions | Steps | Expected result | Accounting impact | BIR/compliance impact | Auto (Y/N) |
|----|------|----------|---------------|-------|-----------------|-------------------|-----------------------|------------|
| D-001 | SOD | Employee submits own report — does not approve own report | Default Odoo SOD: submitter cannot approve | 1. Employee submits report. 2. Same employee attempts to approve. | System blocks self-approval. Manager or designated approver required. | No accounting impact until proper approval. | SOD compliance is auditable. BIR or external auditor will check approval chain. | Y |
| D-002 | SOD | Manager approves report | Manager has "Expenses > Approve" permission | 1. Manager reviews submitted report. 2. Approves. 3. Report moves to "Approved" state. | State = Approved. Accountant can now post. | No accounting impact yet (approval stage, not posting). | Approval timestamp and approver identity captured. Audit trail anchor for manager authorization. | Y |
| D-003 | SOD | Accountant posts approved expense | Accountant has "Accounting > Post" permission | 1. Accountant opens approved report. 2. Posts journal entry. 3. Verifies entry is in Posted state. | Journal entry posted. Report state = "Posted". GL accounts updated. | DR/CR entries now permanent in ledger (unless reversed). | Posting timestamp and poster identity captured. Journal entry number is BIR audit reference. | Y |
| D-004 | SOD | Finance role processes reimbursement payment | Finance user has payment permission | 1. Finance opens posted report. 2. Registers reimbursement payment. 3. Employee payable cleared. | Payment posted. Employee payable reconciled to zero. | DR Employee Payable, CR Bank/Cash. Payable cleared. | Payment date and reference captured. Relevant for BIR audit of cash disbursements. | Y |
| D-005 | SOD | Unauthorized user attempts to approve expense report | Regular employee without approve permission | 1. Employee A submits expense. 2. Employee B (no approval role) opens the report. 3. Attempts to approve. | Approve button not visible or system shows "Access Denied" error. | No accounting impact. | SOD control preserved. Access control log records the attempt if audit logging is enabled. | Y |
| D-006 | SOD | Unauthorized user attempts to post journal entry from expense | Employee or non-accountant attempts to post | 1. Non-accountant opens approved expense report. 2. Attempts to post. | Post button not available. Access Denied if attempted via URL bypass. | No accounting impact. | Unauthorized posting attempt is an audit event. | Y |
| D-007 | SOD | Manager who is also an accountant approves AND posts own employee's expense — role conflict review | Single user has both manager and accountant roles in small organization | 1. Expense submitted by employee. 2. Manager-accountant approves. 3. Same user posts. | Technically allowed in Odoo if roles are combined. This is a company policy SOD issue, not a system control. Document that Odoo does not prevent this by default. | Accounting impact is correct if amounts are right. The risk is reduced oversight. | BIR audit or internal audit may question dual-role approval-posting without compensating control. Must be documented in policy. | N — policy documentation required |
| D-008 | SOD | Approval bypass — direct URL access to post without approval | Technically sophisticated user knows journal entry URL | 1. Expense in Submitted state. 2. User navigates directly to draft journal entry. 3. Attempts to post journal entry directly. | Odoo 18 links expense state to journal entry state. Posting journal entry directly should be blocked until expense is in Approved state. Verify this control exists. | If bypass succeeds: entry posted without manager approval. | Approval bypass is a financial control failure. BIR audit expects sequential approval. | Y — verify control; N — full bypass scenario |
| D-009 | SOD | Attachment requirement enforcement | Company policy: receipts required for all expenses over PHP 1,000 | 1. Employee submits expense for PHP 1,500 without attachment. 2. Submission proceeds (Odoo does not enforce this natively). 3. Manager reviews. 4. Manager must manually reject if no receipt. | Without custom enforcement module: system does not block. Manager is the control. With ipai policy module: system blocks submission. | No accounting impact. | Receipt-less input VAT claims are disallowed by BIR. Control must exist either at system or manual review level. | Y — test policy module enforcement |

---

### E. Employee-Paid Reimbursement Scenarios

| ID | Area | Scenario | Preconditions | Steps | Expected result | Accounting impact | BIR/compliance impact | Auto (Y/N) |
|----|------|----------|---------------|-------|-----------------|-------------------|-----------------------|------------|
| E-001 | Employee reimbursement | Reimbursable expense, no tax complication | Non-VAT supplier, no withholding applicable | 1. Employee creates transport expense from non-VAT taxi (no OR with VAT). 2. Submits. 3. Approved. 4. Posted. 5. Reimbursement payment created. | DR Transport Expense (full amount), CR Employee Payable. Payment: DR Employee Payable, CR Bank. Payable cleared to zero. | Two-line expense entry plus two-line payment entry. Payable fully reconciled. | Expense amount only in P&L. No input VAT claimed. No 2307 applicable. Clean audit trail. | Y |
| E-002 | Employee reimbursement | Reimbursable VATable expense — employee paid from personal funds | Employee paid PHP 2,240 to VAT-registered hotel (PHP 2,000 base + PHP 240 VAT). Has valid OR. | 1. Create expense PHP 2,240. 2. Category has 12% input VAT (price-excluded). 3. Enter OR number and supplier TIN. 4. Post. 5. Reimburse PHP 2,240. | DR Hotel Expense PHP 2,000, DR Input VAT PHP 240, CR Employee Payable PHP 2,240. Reimbursement: DR Employee Payable PHP 2,240, CR Bank PHP 2,240. | Payable cleared. Input VAT PHP 240 sits in Input VAT account until 2550Q is prepared and filed. | Input VAT PHP 240 feeds 2550Q Box 8B or applicable local purchases of services box. OR number traceable from journal entry. Employee reimbursed full amount including VAT. | Y |
| E-003 | Employee reimbursement | Reimbursable expense with non-creditable VAT treatment | Employee paid for entertainment; entertainment input VAT is non-creditable per NIRC | 1. Create expense category "Entertainment" with input VAT tax marked as non-creditable. 2. Create expense. 3. Post. | DR Entertainment Expense (full amount including non-creditable VAT), CR Employee Payable (full amount). No input VAT account debit — the VAT is absorbed into the expense. | Two-line entry. The PHP equivalent of VAT is part of the entertainment expense line, not Input VAT account. | Non-creditable input VAT must NOT appear in 2550Q input schedule. If it does, company is over-claiming. This is a high-risk misconfiguration. | Y |
| E-004 | Employee reimbursement | Reimbursable expense with incorrect VAT setup (VAT claimed on non-VAT purchase) | Category incorrectly configured with 12% VAT; actual purchase was from non-VAT supplier | 1. Create expense using misconfigured category. 2. Expense amount PHP 1,000 but no VAT was actually charged. 3. System computes PHP 107.14 input VAT (if price-included) or PHP 120 (if price-excluded). 4. Post. | Journal entry incorrectly shows input VAT. Finance must catch and correct before 2550Q filing. | Overclaiming of input VAT. DR Input VAT (incorrect), CR Employee Payable (inflated). Payable amount is wrong if employee only actually paid PHP 1,000. | Direct 2550Q exposure: input VAT overclaimed. BIR will disallow. This scenario must be caught by pre-posting review. | N — requires human cross-check of OR against category tax setup |
| E-005 | Employee reimbursement | Reimbursable expense paid in foreign currency | Employee paid USD 100 hotel in US trip; company rate: USD 1 = PHP 57.50; input VAT not applicable (international) | 1. Create expense in USD 100. 2. System converts to PHP 5,750. 3. No input VAT (international purchase). 4. Post. 5. Reimburse at PHP 5,750. | DR Hotel Expense PHP 5,750, CR Employee Payable PHP 5,750. Payment at same rate: balanced. If rate changes at payment date: exchange difference entry. | If rate at payment = PHP 56.80, payment is DR Employee Payable PHP 5,750, CR Bank PHP 5,680, CR FX Gain PHP 70. | BIR: no input VAT on foreign purchases. FX gain/loss may be taxable income. Exchange rate documentation required. | Y — rate check; N — FX gain/loss tax treatment requires human judgment |
| E-006 | Employee reimbursement | Partial reimbursement approved | Policy: only 80% of entertainment is reimbursable | 1. Employee submits PHP 5,000 entertainment expense. 2. Manager approves only PHP 4,000 (80%). 3. Post for PHP 4,000. 4. Reimburse PHP 4,000. | Report or expense amount adjusted to PHP 4,000. Employee absorbs PHP 1,000 difference. Payable = PHP 4,000. Payment = PHP 4,000. Reconciled to zero. | DR Entertainment PHP 4,000, CR Employee Payable PHP 4,000. Payment clears payable. PHP 1,000 difference is not recorded — it was never approved. | Only approved amount is in books. Non-reimbursed portion not expensed by company. No BIR exposure on the non-reimbursed PHP 1,000. | Y |
| E-007 | Employee reimbursement | Full reimbursement — multiple expenses in one payment | Employee has three approved posted reports totalling PHP 8,750 | 1. All three reports approved and posted. 2. Finance creates single payment for PHP 8,750. 3. Payment matched against all three payable lines. | All three payable lines cleared. Bank debited once for PHP 8,750. | DR Employee Payable x3 lines, CR Bank PHP 8,750 (lump). Reconciliation links payment to all three reports. | Audit trail must show which reports were cleared by which payment. Single-payment multi-report reconciliation is an audit requirement. | Y |
| E-008 | Employee reimbursement | Duplicate reimbursement prevention | Report was paid; someone attempts to pay again | 1. Report is approved, posted, and paid. Employee payable is fully reconciled (zero). 2. Finance user opens the same report and attempts to register another payment. | System should not allow second payment if payable is already fully reconciled. Outstanding balance = 0 should be visible and block new payment registration. | No accounting impact if blocked. If not blocked: DR Employee Payable (goes negative), CR Bank. Creates overpayment. | Duplicate payments are a cash disbursement fraud risk and a BIR cash expense record issue. | Y |
| E-009 | Employee reimbursement | Reimbursement after report correction (amount was wrong in posted version) | Report was posted with wrong amount; reset to draft, corrected, re-posted | 1. Report posted with PHP 1,500. 2. Correction needed: amount should be PHP 1,200. 3. Reset report to draft. 4. Edit expense amount. 5. Repost. 6. Reimburse PHP 1,200. | Corrected journal entry: DR Expense PHP 1,200, CR Employee Payable PHP 1,200. Reimbursement pays PHP 1,200 and clears payable. | Reversal of original PHP 1,500 entry plus new PHP 1,200 entry. Clean payable of PHP 1,200. | Correction trail must show original and corrected entries. BIR audit may require explanation of the reversal. | N — requires correction verification |
| E-010 | Employee reimbursement | Wrong employee on expense (expense created under wrong employee profile) | Expense accidentally assigned to Employee A but should be Employee B | 1. Post expense under Employee A. 2. Finance discovers error. 3. Reverse entry. 4. Recreate under Employee B. 5. Post. | Original posting reversed. New posting to Employee B's payable. Employee A's payable unaffected. | Two entries: reversal of A's payable, new entry to B's payable. | Name on reimbursement must match employee receiving payment. Wrong name = financial control failure. | N — requires human verification |

---

### F. Company-Paid Expense Scenarios

| ID | Area | Scenario | Preconditions | Steps | Expected result | Accounting impact | BIR/compliance impact | Auto (Y/N) |
|----|------|----------|---------------|-------|-----------------|-------------------|-----------------------|------------|
| F-001 | Company-paid | Company card / company-paid purchase, no employee liability | Company credit card used directly for employee's hotel stay | 1. Create expense with "Company" payment mode. 2. Category: Hotel, 12% VAT. 3. Supplier invoice attached. 4. Post. | DR Hotel Expense, DR Input VAT, CR Accounts Payable (credit card company or hotel). No employee payable created. | Standard three-line AP entry. Employee has zero liability. | Input VAT creditable. No employee reimbursement. AP settled via payment to credit card issuer or hotel. | Y |
| F-002 | Company-paid | Company-paid VATable expense — supplier is VAT-registered | Company pays directly for conference registration with VAT | 1. Expense mode = Company. 2. Conference registration PHP 11,200 (PHP 10,000 + PHP 1,200 VAT). 3. Supplier TIN and SI attached. 4. Post. | DR Conference Expense PHP 10,000, DR Input VAT PHP 1,200, CR AP Payable PHP 11,200. | AP created for full amount. Input VAT PHP 1,200 in creditable input VAT account. | PHP 1,200 feeds 2550Q. Supplier SI number must be in journal narration. | Y |
| F-003 | Company-paid | Company-paid non-VATable expense — non-VAT supplier | Company pays printing shop not VAT-registered | 1. Expense mode = Company. 2. Category: Printing, no VAT. 3. OR attached from non-VAT supplier. 4. Post. | DR Printing Expense (full amount), CR AP Payable (full amount). No VAT line. | Two-line entry. | No input VAT claimed. 3% percentage tax from non-VAT supplier is borne by supplier, not company's input VAT. | Y |
| F-004 | Company-paid | Company-paid expense from supplier subject to creditable withholding tax | IT consultant engaged by company; PHP 50,000 fee, subject to 2% EWT (ATC WC158) | 1. Expense mode = Company. 2. Supplier = IT consultant with TIN on file. 3. Withholding tax rule: 2% EWT, ATC WC158, active on this expense category. 4. Post. | DR Professional Fees PHP 50,000, CR AP Payable PHP 49,000 (net), CR EWT Payable PHP 1,000 (2% of PHP 50,000). ATC WC158 on withholding line. | Three-line entry. AP is net; EWT payable must be remitted to BIR. | EWT PHP 1,000 must generate 2307 certificate for supplier. ATC WC158 must appear on certificate. Feeds 1601-EQ monthly remittance return. | Y |
| F-005 | Company-paid | Company-paid expense that should NOT create employee liability | Company buys office supplies using petty cash; expense assigned to an employee as expense manager but company bears cost | 1. Expense mode = Company. 2. Category: Office Supplies. 3. Post. | AP Payable or petty cash credit — no employee payable created. | DR Office Supplies, CR AP Payable (or petty cash account). | Employee should not receive a reimbursement claim for a company-paid expense. System must enforce payment mode. | Y |
| F-006 | Company-paid | Company-paid expense incorrectly routed to employee payable account (misconfiguration) | Company-paid category accidentally uses employee payable account | 1. Expense mode = Company. 2. Category has account mapping pointing to employee payable (wrong). 3. Post. | Journal entry DR Expense, CR Employee Payable (incorrect). This creates an employee payable balance where none should exist. Reimbursement flow becomes available incorrectly. | Incorrect liability account used. Employee payable aging is corrupted. | If reimbursement is then processed, company pays employee for something the company already paid. Double disbursement. Financial fraud risk. | Y — detect misconfiguration |
| F-007 | Company-paid | Supplier invoice document linkage for company-paid expense | Company-paid expense with AP journal entry must link back to supplier invoice | 1. Company-paid expense posted to AP. 2. Supplier invoice received separately and posted in AP. 3. Match AP entries for reconciliation. | AP payable from expense and supplier invoice payable reconcile against each other. Net AP = 0 after matching. | Reconciliation clears both AP entries. | Withholding certificate (2307) is generated against the supplier invoice. The linking of expense to supplier invoice is the withholding traceability chain. | N — reconciliation matching requires human or automated matching review |
| F-008 | Company-paid | Payment and reconciliation for company-paid AP | AP payable from company-paid expense settled via bank payment | 1. Post payment from bank to AP. 2. Reconcile. 3. Verify AP cleared. | DR AP Payable, CR Bank. AP entry reconciled and closed. | Bank account debited; AP cleared. | Cash disbursement traceable from expense to AP to bank payment. BIR audit trail complete. | Y |

---

### G. VAT Treatment on Expenses

| ID | Area | Scenario | Preconditions | Steps | Expected result | Accounting impact | BIR/compliance impact | Auto (Y/N) |
|----|------|----------|---------------|-------|-----------------|-------------------|-----------------------|------------|
| G-001 | VAT treatment | VATable expense with valid input VAT (price-excluded) | VAT-registered supplier, valid OR, 12% VAT not included in base | 1. Create expense: base PHP 1,000, 12% VAT = PHP 120, total PHP 1,120. 2. Category has 12% price-excluded tax. 3. Post. | DR Expense PHP 1,000, DR Input VAT PHP 120, CR Payable PHP 1,120. | Balanced three-line entry. Input VAT in correct account. | PHP 120 creditable input VAT feeds 2550Q. Tax base PHP 1,000 is the expense deduction. | Y |
| G-002 | VAT treatment | VAT-exempt expense | Supplier provides VAT-exempt services (e.g., educational services) | 1. Create expense. 2. Category has VAT-exempt tax code. 3. Post. | DR Expense (full amount), CR Payable (full amount). No input VAT credit. | Two-line entry. No input VAT account involved. | VAT-exempt must appear in 2550Q purchase schedule as VAT-exempt purchases — not as creditable input VAT. | Y |
| G-003 | VAT treatment | Zero-rated purchase (if applicable) | Company purchases from PEZA-registered or export-oriented supplier at 0% VAT | 1. Create expense with 0% VAT tax code. 2. Post. | DR Expense (full amount), CR Payable. VAT = PHP 0. | Two-line entry with zero-rated VAT code recorded. | Zero-rated must appear in 2550Q at zero rate — different from exempt. Incorrect classification (exempt vs zero-rated) is a 2550Q filing error. | Y |
| G-004 | VAT treatment | Expense from non-VAT-registered supplier | Supplier is non-VAT (subject to 3% percentage tax, not 12% VAT) | 1. Create expense from non-VAT supplier. 2. Category has no VAT tax. 3. Post. | DR Expense (full amount), CR Payable. No input VAT. | Two-line entry. | No input VAT to claim. If the company incorrectly claims input VAT from a non-VAT supplier, this is a false claim. | Y |
| G-005 | VAT treatment | Mixed VATable and non-VATable lines in one expense report | Hotel (12% VAT) + taxi (non-VAT) in same report | 1. Create report with two expense lines: hotel with VAT tax, taxi with no tax. 2. Post. | Hotel line: DR Hotel PHP X, DR Input VAT PHP Y, CR Payable PHP X+Y. Taxi line: DR Taxi PHP Z, CR Payable PHP Z. No cross-contamination of taxes. | Four journal lines (two per expense). | 2550Q input: only hotel input VAT. Taxi does not contribute. | Y |
| G-006 | VAT treatment | VAT price-included (tax included in total amount) | Supplier's OR shows total PHP 1,120 with VAT included (not separately stated) | 1. Create expense category with 12% VAT (price-included). 2. Enter expense amount as PHP 1,120 (total). 3. System computes: base = PHP 1,120/1.12 = PHP 1,000, VAT = PHP 120. 4. Post. | DR Expense PHP 1,000, DR Input VAT PHP 120, CR Payable PHP 1,120. | Correct split. Same result as price-excluded but computed differently by system. | Tax base PHP 1,000 is correct. Input VAT PHP 120 correct. Price-included computation must be verified. | Y |
| G-007 | VAT treatment | VAT price-excluded — verify base and VAT amounts match OR exactly | OR shows: "Total Taxable Sales PHP 5,000; VAT PHP 600; Total PHP 5,600" | 1. Enter expense with price-excluded VAT. 2. Base = PHP 5,000, VAT = PHP 600. 3. System computes PHP 5,000 x 12% = PHP 600. 4. Post. | DR Expense PHP 5,000, DR Input VAT PHP 600, CR Payable PHP 5,600. | Exact match to OR amounts. | If system computes PHP 5,600/1.12 instead of PHP 5,000 x 0.12, wrong base. Verify price-excluded computation. | Y |
| G-008 | VAT treatment | VAT rounding edge case — line-level vs report-level rounding | Expense report with 5 lines, each computing fractional VAT amounts | 1. Create 5 expense lines with amounts that produce fractional VAT (e.g., PHP 1,003 x 12% = PHP 120.36). 2. Post. 3. Compare sum of line-level VAT amounts vs report-level total VAT. | Rounding must be consistent with BIR requirements: round to the nearest centavo per line, then sum. No penny-level discrepancy in report total vs sum of line totals. | Journal must balance. | 2550Q requires accurate totals. Systematic rounding errors across many reports accumulate into filing discrepancies. | Y |
| G-009 | VAT treatment | Changed VAT tax on expense after draft state, before posting | Tax was 12%; admin changes category to exempt; expense in "Submitted" state | 1. Expense in submitted state with 12% VAT. 2. Admin changes category tax to exempt. 3. Accountant posts. 4. Verify which tax was applied. | Must determine: does Odoo 18 recompute tax on posting using current category config, or does it use the tax captured at expense creation time? If recomputed: posted entry may not match the OR in hand. | Journal entry reflects whatever tax state was active at posting. | This is a critical compliance risk: if tax is recomputed from current config, the journal entry does not match the source OR. | N — requires system behavior verification and process control |
| G-010 | VAT treatment | Deleted VAT configuration after expense draft created | Tax was configured; then deleted/archived; expense still references it | 1. Expense created with tax T1. 2. T1 is archived/deleted. 3. Expense report submitted. 4. Accountant attempts to post. | Odoo should raise an error if a referenced tax is no longer active/available. If it silently drops the tax line: input VAT is not posted. | If tax silently dropped: expense posts without input VAT, underreporting input VAT credit. | Input VAT on the OR cannot be claimed if not posted. Systematic loss of creditable input VAT. | Y — test error handling |
| G-011 | VAT treatment | Incorrect input-tax account setup — input VAT posts to revenue account | Chart of accounts error: input VAT mapped to sales revenue | 1. Configure input VAT tax with incorrect tax account (revenue). 2. Create expense. 3. Post. | DR Expense, CR Payable — but the input VAT line posts to a revenue account (wrong). Revenue is overstated. | Silent misposting. Balance sheet looks correct but P&L is wrong. | 2550Q input VAT schedule will be incorrect if it pulls from the wrong account. | N — requires account mapping audit |
| G-012 | VAT treatment | Blocked posting due to completely missing tax account | Tax configured but tax account field left blank | 1. Configure 12% VAT tax with no tax account. 2. Create expense using this category. 3. Attempt to post. | Odoo 18 should raise an error "Tax account is required" and block posting. | No accounting impact — posting blocked. | Correct behavior. Input VAT cannot be recorded without a tax account. | Y |

---

### H. Withholding on Expense-Related Flows

| ID | Area | Scenario | Preconditions | Steps | Expected result | Accounting impact | BIR/compliance impact | Auto (Y/N) |
|----|------|----------|---------------|-------|-----------------|-------------------|-----------------------|------------|
| H-001 | Withholding | Expense linked to supplier/service subject to EWT — correct withholding base | Professional services PHP 100,000; 2% EWT (ATC WC158) on gross | 1. Company-paid expense for professional services. 2. Withholding tax rule: 2% on gross, ATC WC158. 3. Post. 4. Verify withholding base = PHP 100,000, EWT = PHP 2,000. | DR Professional Fees PHP 100,000, CR AP Payable PHP 98,000, CR EWT Payable PHP 2,000. EWT base = PHP 100,000. ATC = WC158. | Three-line entry. AP is net. EWT payable awaits remittance. | 2307 certificate: base PHP 100,000, EWT PHP 2,000, ATC WC158. Supplier uses 2307 to credit tax withheld against income tax. Feeds 1601-EQ. | Y |
| H-002 | Withholding | Withholding base computed on VAT-exclusive amount (correct) | Gross professional fee PHP 112,000 (PHP 100,000 + PHP 12,000 VAT); EWT should be on PHP 100,000 only | 1. Create company-paid expense PHP 112,000 (price-excluded VAT). 2. EWT rule: 2% on net of VAT amount. 3. Post. 4. Verify EWT base = PHP 100,000, not PHP 112,000. | DR Professional Fees PHP 100,000, DR Input VAT PHP 12,000, CR AP Payable PHP 110,000 (PHP 112,000 minus PHP 2,000 EWT), CR EWT Payable PHP 2,000. | Four-line entry. VAT and EWT both present. AP is net of EWT only. Input VAT is on full PHP 12,000. | EWT on gross-of-VAT base is a common misconfiguration. BIR requires withholding on income payment, not on the VAT portion. If EWT applied to PHP 112,000, EWT = PHP 2,240 (overcalculated). Supplier gets over-withheld on 2307. | Y — critical: verify base computation |
| H-003 | Withholding | Withholding combined with VAT — verify journal balance | Scenario from H-002 | Verify journal entry balances: DR side = PHP 100,000 + PHP 12,000 = PHP 112,000. CR side = PHP 110,000 AP + PHP 2,000 EWT = PHP 112,000. | Journal balanced. DR PHP 112,000 = CR PHP 112,000. | Correct journal balance. | Journal balance is a fundamental accounting control. EWT + VAT combined entries are a frequent source of unbalanced journals if not configured correctly. | Y — critical balance check |
| H-004 | Withholding | Withholding omitted when required | Professional services expense; withholding tax rule exists but is not assigned to the expense category | 1. Company-paid professional services PHP 50,000. 2. EWT rule exists in system but not linked to category. 3. Post. | Journal shows DR Professional Fees PHP 50,000, CR AP Payable PHP 50,000. No EWT deducted. | No withholding. AP is gross. | Company fails to withhold EWT. BIR penalizes the company (not the supplier) for failure to withhold and remit. High-risk compliance failure. | Y — detect missing withholding rule on category |
| H-005 | Withholding | Withholding applied when not required — pure expense reimbursement | Employee reimbursement for out-of-pocket meals; withholding tax rule accidentally assigned to meals category | 1. Employee reimbursement expense for meals PHP 1,000. 2. Withholding rule applied by mistake. 3. Post. | System computes EWT on a pure reimbursement to an employee. This is incorrect: employee reimbursement of actual expenses is not income. | DR Meals PHP 1,000, CR Employee Payable PHP 990, CR EWT Payable PHP 10. Employee receives PHP 10 less than they paid. | Applying vendor/supplier EWT to an employee reimbursement is a classification error. EWT Payable is a liability the company should not have incurred. Must reverse and correct. | Y — detect rule mismatch |
| H-006 | Withholding | Incorrect ATC mapping — ATC WC157 used instead of WC158 | Wrong ATC causes incorrect certificate and incorrect 1601-EQ box | 1. Professional services expense. 2. EWT rule configured with ATC WC157 (wrong) instead of WC158. 3. Post. 4. Generate 2307. | 2307 certificate shows ATC WC157. Supplier's tax return will use wrong ATC to claim tax credit. 1601-EQ return will have wrong ATC allocation. | Accounting entries are mathematically correct but ATC is wrong. | BIR requires specific ATC per income payment classification. Wrong ATC = invalid 2307. Supplier cannot validly claim the credit. | Y — verify ATC value stored on move line |
| H-007 | Withholding | Missing ATC mapping — ATC field blank | Withholding tax rule created without ATC code | 1. Create withholding tax rule without ATC. 2. Apply to expense. 3. Post. 4. Generate 2307. | 2307 shows blank ATC. Certificate is invalid. Supplier cannot use it. | EWT amount posted but ATC not recorded. | Blank ATC = unusable 2307. Company remits EWT but supplier has no valid certificate. Data quality failure. | Y |
| H-008 | Withholding | Private sector supplier — standard EWT scenario | All private sector suppliers: standard EWT rules apply | 1. Company-paid expense to private sector supplier. 2. Applicable EWT rule and ATC. 3. Post and generate 2307. | Standard EWT processing. 2307 generated with correct ATC, base, and amount. | Standard withholding entries. | Normal private sector withholding. Baseline scenario. | Y |
| H-009 | Withholding | Government entity as payer — withholds from company | Company is the VENDOR; government customer pays company and withholds EWT from payment | 1. Company invoices government customer. 2. Government remits net payment. 3. Company receives 2307 from government. 4. Company records the 2307 as creditable tax withheld (asset). | Company posts: DR Bank (net received), DR Creditable Tax Withheld (asset), CR Receivable (full invoice amount). | 2307 received from government is the company's tax asset. Must be recorded and claimed in company's income tax return. | RMC 36-2021: government entities also withhold creditable VAT (VAT withholding) in addition to income tax withholding. Both 2307s may be issued. | N — requires human posting of received 2307 |
| H-010 | Withholding | Government-related VAT withholding scenario (RMC 36-2021) | Government customer required to withhold 5% of 12% VAT on purchases from the company | 1. Company invoices government for PHP 112,000 (PHP 100,000 + PHP 12,000 VAT). 2. Government pays PHP 106,400 (PHP 112,000 minus PHP 5,600 VAT withholding). 3. Government issues 2307 with VAT-withholding ATC for PHP 5,600. 4. Company records receipt and 2307. | Company's output VAT posting for PHP 12,000. PHP 5,600 withheld by government. PHP 6,400 remitted by company to BIR. 2307 received is proof for 2550Q credit. | DR Bank PHP 106,400, DR Creditable VAT PHP 5,600, CR Output VAT PHP 12,000, CR Revenue PHP 100,000 (simplified). | 2307 from government (VAT-withholding ATC) is used by company on 2550Q to claim credit for VAT already withheld. RMC 36-2021 compliance is critical. | N — complex multi-document flow |
| H-011 | Withholding | Partial payment/partial reimbursement — withholding treatment at each payment | Supplier partially paid; withholding deducted on each payment proportionally | 1. Company-paid expense/bill PHP 100,000. EWT 2% = PHP 2,000 total. 2. Company pays PHP 60,000 gross (first payment). Proportional EWT on first payment = PHP 1,200. Net paid = PHP 58,800. 3. Second payment PHP 40,000 gross. Proportional EWT = PHP 800. Net paid = PHP 39,200. | Two payment entries each with proportional EWT. Total EWT = PHP 2,000. Total AP cleared = PHP 100,000. | Two payment entries. EWT applied proportionally at each payment event. | BIR RR 11-2018: EWT deducted at time of payment. Withholding entire EWT on first payment and none on second is a common misconfiguration. Must verify Odoo's withholding treatment on partial payment. | N — requires detailed partial-payment testing |
| H-012 | Withholding | Compensation withholding boundary — employee expense vs salary | Employee receives travel allowance treated as income (added to payroll), not as expense reimbursement | 1. HR processes travel allowance as a payroll component. 2. Withholding on compensation (1601-C scope) applies via payroll. 3. This is NOT processed through the expense module. | Expense module should NOT be used for compensation/salary. If it is: EWT (vendor withholding ATC) would be incorrectly applied to what should be 1601-C compensation withholding. | Wrong return if processed through expense module: 1601-EQ credit instead of 1601-C. | Misclassifying compensation benefits in the expense module causes: wrong withholding ATC, wrong return, wrong certificate to employee (should be BIR Form 2316, not 2307). Critical compliance error. | N — boundary documentation required |
| H-013 | Withholding | Incorrect certificate generation — 2307 shows wrong period | EWT posted in Q1 but certificate shows Q2 due to posting date error | 1. Expense with EWT posted 2025-03-31 (Q1). 2. Posting date accidentally set to 2025-04-01 (Q2). 3. Generate 2307 for Q1. 4. Verify period shown on certificate. | 2307 should reflect the actual period of the withholding. If posting date = Q2, 2307 may show Q2 period. Supplier expects Q1 certificate for Q1 1701 claim. | No accounting impact — the entry is in Q2. | Period mismatch on 2307: supplier claims Q1 credit but certificate shows Q2. BIR matching failure. Company remits Q1 but reports Q2 — allocation error. | Y — verify posting date vs period |

---

### I. PH/BIR Document and Output Sensitivity

| ID | Area | Scenario | Preconditions | Steps | Expected result | Accounting impact | BIR/compliance impact | Auto (Y/N) |
|----|------|----------|---------------|-------|-----------------|-------------------|-----------------------|------------|
| I-001 | BIR documents | Expense report data sufficient to support 2307-related downstream processing | Company-paid expense with EWT applied | 1. Post company-paid expense with EWT. 2. Verify that journal move lines contain: supplier TIN, tax base amount, withheld amount, ATC code, posting date. | All five data elements present on the withholding tax line of the journal entry. | Journal move has complete EWT data. | All five elements are required to generate a valid 2307. Missing any one element = invalid certificate. This is the primary data-completeness check. | Y |
| I-002 | BIR documents | Expense postings correctly feed VAT return support schedules | Multiple expense reports with input VAT posted in a quarter | 1. Post multiple expense reports with varying input VAT amounts. 2. Run VAT return report for the quarter. 3. Verify input VAT schedule matches sum of individual expense input VAT amounts. | VAT return input schedule total = sum of all expense input VAT journal lines for the period. No double-counting; no omissions. | Aggregate of tax move lines per account per period. | 2550Q Box 8B (Local Purchases of Services) or equivalent must match the input VAT total from expense postings. Discrepancy = incorrect return. | Y |
| I-003 | BIR documents | Supporting details traceable to 2550Q-relevant input VAT positions | Individual expense report traced to 2550Q line | 1. Select one posted expense report with input VAT. 2. Trace: expense report → journal entry → tax line → input VAT account → 2550Q period aggregation. | Every step in the chain is traceable with journal entry number, move line ID, and tax code. | Drill-down from 2550Q total to source expense report is possible. | BIR audit requires ability to trace from the return to source documents. If any link in the chain is broken, the audit fails. | N — manual drill-down trace; Y — automated link check |
| I-004 | BIR documents | Compensation-related expense/reimbursement does not get misclassified into 1601-C logic | Employee reimbursement for business expenses vs compensation benefit | 1. Post employee expense reimbursement for business travel (not compensation). 2. Verify that the posting does not appear in 1601-C compensation withholding report. | Expense reimbursement journal entry is in operating expense accounts, not payroll accounts. 1601-C report excludes expense reimbursements. | Correct account classification: expense account, not payroll account. | 1601-C overcounting if reimbursements are included. Company remits excess withholding on non-compensation items. | Y — verify account classification |
| I-005 | BIR documents | Employee reimbursement does not incorrectly generate supplier withholding output | Reimbursement flow must not trigger EWT as if employee is a vendor | 1. Post employee reimbursement. 2. Verify that no EWT Payable line is created. 3. Verify that no 2307 is generated for the employee from the expense module. | No EWT lines on employee reimbursement journal entries. No 2307 generated for employee from expense module. | Employee payable only. No withholding payable. | Employee reimbursements are not taxable income via the expense module. Generating a 2307 for an employee reimbursement is incorrect and would confuse the employee's income tax computation. | Y |
| I-006 | BIR documents | Government withholding scenarios use correct proof/certificate assumptions | Company selling to government entity; government withholds both EWT and VAT | 1. Invoice government customer. 2. Government pays net of EWT and VAT withholding. 3. Two 2307 certificates received: one for EWT, one for VAT withholding. 4. Company records both as assets. | Both 2307s recorded as creditable tax assets. EWT 2307 applied against income tax. VAT withholding 2307 applied against 2550Q output VAT. | DR CWT Asset (income), DR Creditable VAT (VAT withholding), CR Receivable (full amount). | If only one 2307 is received (EWT), the company may overlook the VAT withholding 2307 entitlement. Both must be tracked and claimed separately. | N — requires human documentation and follow-up with government customer |
| I-007 | BIR documents | Audit trail supports later compliance review | Posted expense report undergoes internal audit 6 months later | 1. Select a posted expense report from a prior period. 2. Open the chatter/audit trail. 3. Verify: who created, who submitted, who approved, who posted, when each step occurred. 4. Verify attachment link is still intact and document is readable. | Complete chain: creator, submitter, approver, poster, each with timestamp. Attachment still readable. Journal entry number visible. | Immutable posted journal entry. Chatter history preserved. | BIR audit can span 3-5 years. Audit trail must be intact and readable for that duration. Odoo chatter + attachment storage is the primary mechanism. | N — long-duration audit trail verification |

---

### J. Re-invoicing Expenses to Customers

| ID | Area | Scenario | Preconditions | Steps | Expected result | Accounting impact | BIR/compliance impact | Auto (Y/N) |
|----|------|----------|---------------|-------|-----------------|-------------------|-----------------------|------------|
| J-001 | Re-invoicing | Reinvoice employee-paid expense to customer | Employee paid for travel for a client project; expense marked "Re-Invoice Expense" | 1. Create employee-paid expense linked to sale order or project. 2. Post expense. 3. From sale order or project, generate customer invoice. 4. Verify expense appears as invoice line. | Customer invoice created with expense line. Amount = expense amount. Tax on customer invoice driven by customer's fiscal position. | Expense entry (employee payable) plus customer invoice entry (receivable + revenue). No double-counting of expense: cost is on expense side; revenue/recovery is on invoice side. | Output VAT on customer invoice must be correct per customer's classification. No double input VAT claim for the same expense. | Y |
| J-002 | Re-invoicing | Reinvoice company-paid expense to customer | Company paid directly for a client-specific expense; to be recharged | 1. Create company-paid expense linked to sale order. 2. Post expense. 3. Generate customer invoice from sale order. | Customer invoice created. AP remains on company books (company paid supplier). Customer owes company for the recharged cost. | AP on expense side; Receivable on customer invoice side. Revenue = cost recovery. | Output VAT computed on the customer invoice at the customer's applicable rate. Must not omit VAT if customer is private sector. | Y |
| J-003 | Re-invoicing | Reinvoice VATable expense — verify output VAT on customer invoice | Travel expense at 12% input VAT; to be reinvoiced with 12% output VAT to customer | 1. Expense posted with 12% input VAT. 2. Reinvoice to customer. 3. Customer invoice line = same amount. 4. Output VAT 12% applied on customer invoice. | Customer invoice: DR Receivable (amount + output VAT), CR Revenue, CR Output VAT PHP Y. Input VAT (from expense) and Output VAT (on invoice) are independent and both correctly posted. | Input VAT on expense side: cost recovery. Output VAT on invoice side: collected from customer. Both are correct and not double-counted. | Output VAT PHP Y must be remitted to BIR via 2550Q. Input VAT PHP X is creditable on 2550Q. Net = Output VAT minus Input VAT. | Y |
| J-004 | Re-invoicing | Reinvoice expense with customer fiscal position differences | Customer is PEZA-registered and purchases at 0% VAT | 1. Expense has 12% input VAT (company's input). 2. Customer is PEZA entity with 0% fiscal position mapped for services. 3. Reinvoice to customer. | Customer invoice applies 0% VAT due to fiscal position. Output VAT = PHP 0. Company still has PHP X input VAT from the expense. | Expense: input VAT DR. Customer invoice: 0% output VAT (zero). Company effectively absorbs the VAT cost if not recovered. | Company's input VAT from expense is creditable. Customer's invoice at 0% does not generate output VAT for company. Net input VAT position improves. Must be deliberate and correctly configured via fiscal position. | Y |
| J-005 | Re-invoicing | Reinvoice to government customer — VAT withholding considerations | Government customer will withhold from payment per RMC 36-2021 | 1. Create customer invoice for government entity. 2. Amount = PHP 112,000 (PHP 100,000 + PHP 12,000 VAT). 3. Government pays PHP 106,400 (net of 5% VAT withholding = PHP 5,600). 4. Government issues 2307 VAT-withholding ATC. | Company receives PHP 106,400 + 2307 for PHP 5,600. Company records: DR Bank PHP 106,400, DR Creditable VAT PHP 5,600, CR Receivable PHP 112,000. | Receivable cleared. Creditable VAT asset recorded for use in 2550Q. | If company fails to follow up on the 2307, the PHP 5,600 creditable VAT is lost. Government must issue the certificate; company must record it. | N — requires human follow-up |
| J-006 | Re-invoicing | Reinvoice with wrong tax mapping — no output VAT on customer invoice | Fiscal position misconfigured: maps 12% VAT to "no tax" for a private-sector customer | 1. Private-sector customer has incorrect fiscal position that removes VAT. 2. Expense reinvoiced. 3. Customer invoice created with no output VAT. | Customer invoice shows zero VAT. Company collects no output VAT from customer. Company's output VAT return will be understated. | Revenue posted without output VAT. 2550Q output side understated. | Under-reporting output VAT is a BIR compliance violation. Must be caught before invoice is issued. | Y — verify fiscal position output |
| J-007 | Re-invoicing | Reinvoice with margin/markup (if configured) | Company charges 10% markup on recharged expenses | 1. Expense = PHP 10,000. 2. Customer invoice = PHP 11,000 (PHP 10,000 + 10% markup). 3. Output VAT = 12% on PHP 11,000 = PHP 1,320. | Customer invoice: DR Receivable PHP 12,320, CR Revenue PHP 11,000, CR Output VAT PHP 1,320. Expense side: DR Expense PHP 10,000 (or PHP 10,000 + PHP 1,200 input VAT if VATable). | Revenue = PHP 11,000 (cost + markup). Output VAT = PHP 1,320 (on full invoice amount). | Output VAT on the markup is required. If markup is added but not subject to VAT, this is incorrect. VAT applies to the full invoice amount in most cases. | Y |
| J-008 | Re-invoicing | Reinvoice exact-cost flow (no markup) | Company recharges at exact cost, no margin | 1. Expense = PHP 10,000. 2. Customer invoice = PHP 10,000 (exact cost). 3. Output VAT at 12% if VATable. | Customer invoice = expense amount. Revenue = cost recovery (zero margin). | DR Receivable PHP 11,200, CR Revenue PHP 10,000, CR Output VAT PHP 1,200. Expense side: DR Expense PHP 10,000, DR Input VAT PHP 1,200 (if applicable), CR Payable PHP 11,200. | Net impact: input VAT and output VAT offset each other in 2550Q. Revenue = cost, zero profit margin. | Y |
| J-009 | Re-invoicing | Customer invoice journal lines and taxes verified correct | Any reinvoice scenario | 1. Generate customer invoice from reinvoiced expense. 2. Open customer invoice journal entry. 3. Verify: receivable line, revenue/recovery line, output VAT line (if applicable). 4. Verify tax amounts match expected computation. | Journal entry balanced. Output VAT amount mathematically correct. Receivable = revenue + output VAT. | Correct three-line customer invoice entry. | Output VAT is reported on 2550Q. Incorrect output VAT line = incorrect return. | Y |
| J-010 | Re-invoicing | No double-counting between expense and customer invoice | Expense input VAT and customer invoice output VAT must be independent | 1. Post expense with input VAT. 2. Reinvoice to customer with output VAT. 3. Verify input VAT account balance is not affected by the customer invoice. 4. Verify output VAT account balance is not affected by the expense. | Input VAT account balance increases by expense input VAT only. Output VAT account balance increases by customer invoice output VAT only. They do not cross. | Two independent tax account movements. No offsetting within a single entry. | 2550Q: input and output VAT are reported separately and then netted. If the system nets them prematurely (wrong account mapping), the return will be incorrect. | Y |
| J-011 | Re-invoicing | BIR-sensitive tax treatment preserved on customer invoice | Expense to government customer; BIR-specific tax codes must carry through to invoice | 1. Expense created with BIR tax code (e.g., PH-specific input VAT code). 2. Reinvoice to customer. 3. Customer invoice tax code must reflect customer's applicable rate (not blindly inherit expense tax). | Customer invoice tax = customer's fiscal position result. BIR output tax code on invoice is the one relevant to the customer, not the vendor. | Expense and invoice use independent tax codes appropriate to each counterparty. | Tax code on customer invoice must be BIR-recognizable output VAT code. If wrong code used, 2550Q classification may be wrong. | Y |

---

### K. Posting, Journal, and Ledger Integrity

| ID | Area | Scenario | Preconditions | Steps | Expected result | Accounting impact | BIR/compliance impact | Auto (Y/N) |
|----|------|----------|---------------|-------|-----------------|-------------------|-----------------------|------------|
| K-001 | Journal integrity | Draft to posted state transition | Approved expense report | 1. Open approved expense report. 2. Post. 3. Verify state = "Posted". 4. Open journal entry and verify state = "Posted". | Expense report state and journal entry state both = Posted. Journal entry number assigned. | Permanent ledger impact. | Journal entry number is the primary BIR audit reference. It must be assigned and immutable after posting. | Y |
| K-002 | Journal integrity | Correct journal selected for expense posting | Company has multiple journals: bank, cash, expense, AP | 1. Post employee expense. 2. Verify journal = "Employee Expenses Journal" (or equivalent). 3. Post company-paid expense. 4. Verify journal = "Purchase Journal" or "AP Journal". | Each flow uses the correct journal. Employee reimbursement does not use AP journal. Company-paid expense does not use employee expense journal. | Correct journal assignment ensures correct account series and statement grouping. | Incorrect journal = entries appear in wrong section of financial reports. Expense account balances may be missed in P&L review. | Y |
| K-003 | Journal integrity | Correct expense accounts used | Category mapped to correct P&L account | 1. Post expense. 2. Open journal entry. 3. Verify expense line account = the account configured on the expense category. | Expense line account matches category configuration. No fallback to a generic expense account unless intentionally configured. | Correct expense account used. P&L account balance updated correctly. | Account classification determines which P&L line the expense appears on. Incorrect classification misrepresents expenses in financial statements used for BIR income tax filing. | Y |
| K-004 | Journal integrity | Correct tax accounts used | Input VAT account and EWT payable account configured correctly | 1. Post expense with input VAT. 2. Verify input VAT line account = "Input VAT - Local Purchases" (or equivalent). 3. Post expense with EWT. 4. Verify EWT Payable line account = "Withholding Tax Payable - EWT" (or equivalent). | Tax lines use correct accounts. No tax line posts to expense or liability accounts by mistake. | Tax accounts correctly carry VAT and withholding balances for period-end returns. | Input VAT account feeds 2550Q. EWT Payable account feeds 1601-EQ. Wrong accounts = wrong return data. | Y |
| K-005 | Journal integrity | Correct payable/liability lines used | Employee reimbursement uses employee payable; company-paid uses AP payable | 1. Post employee expense. 2. Verify credit line account = employee payable (not AP). 3. Post company-paid expense. 4. Verify credit line account = AP payable (not employee payable). | Correct liability accounts for each flow. | Employee payable and AP payable are separate accounts. Reconciliation is per-account. | Mixing employee payable and AP payable corrupts aging reports and makes reconciliation ambiguous. AP aging may show incorrect supplier balances. | Y |
| K-006 | Journal integrity | Correct employee payable vs supplier payable distinction | Verify account-level separation in chart of accounts | 1. Review chart of accounts. 2. Confirm employee payable account is distinct from AP payable account. 3. Post both types of expenses. 4. Verify each uses correct account. | Two distinct payable accounts. Employee reimbursement claims are visible separately from supplier AP. | Separate payable sub-ledgers for employees and suppliers. | Audit requires clear distinction between amounts owed to employees vs amounts owed to suppliers. Withholding certificates apply only to suppliers, not employees (from the expense module). | Y |
| K-007 | Journal integrity | Correct receivable if expense is reinvoiced | Customer invoice from reinvoiced expense | 1. Post reinvoiced customer invoice. 2. Verify receivable line account = AR receivable for that customer. | Receivable line uses customer's receivable account. Not employee payable or AP payable. | AR balance increases for the customer. | Correct AR account drives customer statement and aging. Incorrect account causes missed collections follow-up. | Y |
| K-008 | Journal integrity | Locked period — posting date edge case | Accounting period for last month is locked/closed | 1. Create expense with receipt date in prior month. 2. Attempt to post with prior-month date. 3. Period is locked. | Odoo should block posting to a locked period and prompt for a current-period date. | Posting must occur in an open period. | BIR returns are filed per period. Posting in a closed period after filing the return creates a discrepancy between the return and the ledger. This is a high-risk control. | Y |
| K-009 | Journal integrity | Reset/cancel/reverse behavior | Posted expense needs to be reversed | 1. Post expense. 2. Open journal entry. 3. Reverse the entry. 4. Verify that the expense report status returns to an editable state. 5. Verify that the reversal journal entry is created and posted in the correct period. | Reversal entry posted. Original entry and reversal entry net to zero. Expense report returns to appropriate state for correction. | Net ledger impact = zero after reversal. | Reversals must be in the same period as the original for correct period-end reporting. If reversal is in a different period, both periods are affected and 2550Q for both periods may need adjustment. | N — requires period-specific review |
| K-010 | Journal integrity | Duplicate posting prevention | Accountant accidentally clicks "Post" twice | 1. Post expense report. 2. Attempt to post the same report again. | Second post attempt is blocked because report state is already "Posted". Journal entry already exists. | No duplicate journal entry. | Duplicate posting = double expense and double payable or double input VAT. Must be prevented. | Y |
| K-011 | Journal integrity | Auditability and traceability | Posted journal entry traced back to expense report | 1. Open a posted journal entry from an expense. 2. Verify the source document link (expense report reference) is visible. 3. Navigate from journal entry to expense report. 4. Navigate from expense report to journal entry. | Bidirectional traceability: journal entry shows expense report reference; expense report shows journal entry number. | Source document linkage on journal entry. | BIR audit requires ability to navigate from ledger entry to source document and vice versa. Broken links = incomplete audit trail. | Y |

---

### L. Reimbursement Payment and Reconciliation

| ID | Area | Scenario | Preconditions | Steps | Expected result | Accounting impact | BIR/compliance impact | Auto (Y/N) |
|----|------|----------|---------------|-------|-----------------|-------------------|-----------------------|------------|
| L-001 | Payment and reconciliation | Reimbursement payment posted correctly | Posted expense report; employee payable outstanding | 1. Open posted expense report. 2. Register payment: amount = PHP X, date = today, journal = bank. 3. Post payment. | Payment journal entry: DR Employee Payable PHP X, CR Bank PHP X. Payment state = "Paid". | Employee payable cleared. Bank balance reduced. | Cash disbursement date and amount are BIR audit items. Payment journal entry number is the disbursement reference. | Y |
| L-002 | Payment and reconciliation | Outstanding employee liability cleared correctly | Payment matched to payable | 1. Verify employee payable balance before payment. 2. Post payment. 3. Verify employee payable balance = 0 after reconciliation. | Payable account reconciled to zero. Reconciliation entry links payment to original expense payable. | No residual payable balance. | Clean payable aging: no phantom outstanding amounts for paid expense reports. | Y |
| L-003 | Payment and reconciliation | Partial reimbursement reconciliation | Employee is to be partially reimbursed (PHP 3,000 of PHP 5,000) | 1. Post expense for PHP 5,000. 2. Pay PHP 3,000. 3. Reconcile partial payment against payable. | Employee payable: original PHP 5,000, minus PHP 3,000 payment = PHP 2,000 outstanding. Reconciliation matches payment against payable, leaving PHP 2,000 open. | Partial reconciliation. Payable aging shows PHP 2,000 still outstanding. | Outstanding partial reimbursement must be tracked and paid in a subsequent period. PHP 2,000 remains on employee's payable aging. | Y |
| L-004 | Payment and reconciliation | Full reimbursement reconciliation | Multiple partial payments total the full payable | 1. Post expense for PHP 5,000. 2. First payment PHP 3,000. 3. Second payment PHP 2,000. 4. Both reconciled against payable. | Payable fully cleared after both payments. Reconciliation shows two payments netting to PHP 5,000. | Full payable cleared. Two payment journal entries. | Audit trail shows payment in two installments. Both dates, amounts, and journal entry numbers traceable. | Y |
| L-005 | Payment and reconciliation | Reimbursement after corrected report | Report was reset to draft, corrected, reposted; then paid | 1. Original report posted for PHP 1,500. 2. Report corrected to PHP 1,200 via reset and repost. 3. Payment of PHP 1,200 registered. 4. Payable cleared. | Payment of PHP 1,200 clears the corrected payable. Original PHP 1,500 payable was cleared when report was reset. No orphaned payable balances. | Corrected payable cleared. No residual balance. | Correction trail: original entry, reversal (from reset), new entry, payment. All four entries visible and traceable. | N — requires correction flow verification |
| L-006 | Payment and reconciliation | Reimbursement after tax correction | Report was posted with wrong tax; reset, corrected, reposted with correct tax; then paid | 1. Report posted with 12% VAT (wrong: purchase was from non-VAT supplier). 2. Reset to draft. 3. Remove VAT tax. 4. Repost. 5. Pay corrected amount (no VAT component). | Original VAT claim reversed. Corrected amount (no VAT) posted and paid. Input VAT account no longer has an erroneous balance for this expense. | Correct expense entry (no VAT), correct payable (no VAT component), correct payment. | Corrected input VAT position is accurate for 2550Q. Reversal entries ensure the prior-period overstatement is corrected. | N — requires full correction cycle verification |
| L-007 | Payment and reconciliation | Wrong journal/payment method used | Finance accidentally uses cash journal instead of bank journal | 1. Post reimbursement payment via cash journal instead of bank journal. 2. Detect error. 3. Reverse payment. 4. Re-register payment with correct bank journal. | Reversal of incorrect cash payment. New correct bank payment. Employee payable cleared by bank payment. | Cash account incorrectly debited in error; corrected by reversal. Bank account debited in corrected entry. | Cash journal vs bank journal distinction matters for bank reconciliation and financial statements. Must be corrected. | N — requires human detection of journal error |
| L-008 | Payment and reconciliation | Cash/bank journal interaction — bank reconciliation impact | Reimbursement payment made via bank; bank statement must reconcile | 1. Post reimbursement via bank journal. 2. Import bank statement. 3. Reconcile bank statement line against the reimbursement payment. | Bank statement line matched to payment journal entry. Bank account reconciled. | Bank account reconciliation clears both the bank statement line and the journal entry. | Clean bank reconciliation supports cash position accuracy for BIR audit. Unreconciled bank entries raise questions about disbursement completeness. | Y |
| L-009 | Payment and reconciliation | Reversal/correction after payment — payment already made | Employee was overpaid; correction required after payment was already posted | 1. Expense posted for PHP 2,000. 2. Employee paid PHP 2,000. 3. Discovery: actual expense was PHP 1,500. 4. Reverse original expense entry. 5. Post corrected expense entry PHP 1,500. 6. Record recovery of overpayment PHP 500 from employee (or post a receivable from employee). | Original entries reversed. Corrected entries posted. Employee owes PHP 500. DR Employee Receivable PHP 500, CR Bank PHP 500 (if cash returned) or CR Expense Recovery PHP 500. | Correction entries plus recovery recording. Net position: PHP 1,500 expense recognized; PHP 500 in employee receivable. | Overpayment recovery must be recorded to avoid understated receivables. BIR audit may question large correction entries. | N — requires human decision on recovery method |

---

### M. Reporting and Audit Scenarios

| ID | Area | Scenario | Preconditions | Steps | Expected result | Accounting impact | BIR/compliance impact | Auto (Y/N) |
|----|------|----------|---------------|-------|-----------------|-------------------|-----------------------|------------|
| M-001 | Reporting | Expense reporting by employee | Multiple posted expense reports from one employee | 1. Run expense analysis report filtered by employee. 2. Verify total expenses per employee match sum of individual posted reports. | Report total = sum of individual expense amounts. No double-counting. | Aggregate of journal entries per employee. | Employee-level expense analysis is used for budget control and potential benefit-in-kind assessment under BIR de minimis rules. | Y |
| M-002 | Reporting | Reporting by category | Multiple expenses across multiple categories | 1. Run expense analysis report filtered by category. 2. Verify each category total matches its journal entries. | Category totals match corresponding expense account balances in GL. | Per-category GL balance = per-category report total. | Category-level reporting allows identification of expense types for budget and tax analysis. | Y |
| M-003 | Reporting | Reporting by tax treatment | Report on all expenses with 12% VAT input vs expenses with no VAT | 1. Run expense analysis with tax filter: input VAT vs no tax. 2. Verify input VAT total matches Input VAT account balance for the period. | Input VAT report total = Input VAT GL account balance for the period. No-tax expense total = sum of non-VAT expense journal lines. | Account-level balances match report totals. | Input VAT report feeds 2550Q preparation. Discrepancy = incorrect return data. | Y |
| M-004 | Reporting | Reporting by reimbursable vs company-paid | Separate totals for employee reimbursement and company-paid expenses | 1. Run expense report split by payment mode. 2. Verify employee-reimbursable total = sum of employee payable credits from expense postings. 3. Verify company-paid total = sum of AP payable credits from expense postings. | Two separate totals. No mixing. | Employee payable account credits = employee reimbursable total. AP payable account credits = company-paid total. | Separation matters for cash planning (reimbursements are employee payments; company-paid are supplier payments) and for withholding analysis (EWT applies only to supplier/company-paid side). | Y |
| M-005 | Reporting | VAT-sensitive report totals — input VAT schedule reconciles to 2550Q | End of quarter: input VAT schedule total must match 2550Q Box 8B (or applicable box) | 1. Run input VAT schedule for the quarter. 2. Separately compute the sum of all expense input VAT journal entries for the quarter. 3. Cross-check: report total = journal entry total = 2550Q box. | All three figures match. No rounding difference larger than PHP 1.00 across the entire quarter. | Input VAT account closing balance for the quarter = report total. | This is the primary 2550Q preparation verification. Failure = filed return does not match the books. BIR can assess deficiency VAT. | Y |
| M-006 | Reporting | Withholding-sensitive report totals — EWT payable reconciles to 1601-EQ | End of month: EWT payable balance must match 1601-EQ remittance amount | 1. Run EWT payable balance for the month. 2. Cross-check against 1601-EQ draft return. 3. Verify both show same ATC breakdown. | EWT Payable account balance = 1601-EQ total remittance amount. ATC breakdown matches. | EWT Payable account per ATC = 1601-EQ per ATC. | If EWT Payable balance does not match 1601-EQ, either the return is wrong or the account is wrong. Must be reconciled before filing. | Y |
| M-007 | Reporting | Posted move totals reconcile with expense report totals | Cross-check: expense report total = journal entry total | 1. Select any posted expense report. 2. Open the journal entry. 3. Sum expense lines in journal entry. 4. Compare to expense report total. | Journal entry expense line total = expense report total. No discrepancy. | Account-level posting matches report-level total. | Discrepancy between expense report total and journal entry total is a data integrity failure. The report cannot be used to support BIR audit if it does not match the books. | Y |
| M-008 | Reporting | Audit trail from attachment to payment | Complete chain: attachment > expense line > report > journal entry > payment | 1. Select a paid expense. 2. Trace: OR attachment → expense line (OR number) → expense report → journal entry → payment entry. 3. Verify each link is intact. | Complete chain visible. No broken links. Each step has a reference to the next. | Full traceability in the system. | This is the BIR audit scenario. The auditor follows the chain from the return to the source document. If any link is broken, the input VAT claim is unsupported. | N — manual trace required |
| M-009 | Reporting | Traceability for later BIR support schedules/certificates | Quarterly: BIR SLP/SLS support schedule for 2550Q | 1. Run purchase register (SLP equivalent) for the quarter. 2. Verify each line shows: supplier TIN, OR/SI number, date, base amount, VAT amount, tax code. 3. Verify total matches 2550Q input VAT amount. | Purchase register has all required fields populated. Total matches 2550Q. | Aggregate of journal move lines with supplier info. | BIR may request the SLP as part of a 2550Q audit. If TIN or OR number is missing on any line, that line's input VAT claim is unsubstantiated. | N — data completeness requires human review per line |
| M-010 | Reporting | Multi-currency reporting behavior | Expenses in USD and PHP in same report period | 1. Post expenses in both USD and PHP. 2. Run reports. 3. Verify all amounts are in PHP (company currency). 4. Verify exchange rates applied are visible in the report. | All report amounts in PHP. Exchange rate used per expense is traceable. | PHP equivalent amounts in all ledger reports. | BIR returns are in PHP. Exchange rates must be documented. If BSP rate is required, verify it was the rate applied. | Y |

---

### N. Negative / Failure Scenarios

| ID | Area | Scenario | Preconditions | Steps | Expected result | Accounting impact | BIR/compliance impact | Auto (Y/N) |
|----|------|----------|---------------|-------|-----------------|-------------------|-----------------------|------------|
| N-001 | Failure | Missing journal on expense category | Expense category has no journal configured | 1. Create expense using category with no journal. 2. Attempt to post. | Odoo raises error: "Journal is required for this expense category." Posting blocked. | No accounting impact. | Posting blocked. Correct behavior — prevents silent misposting. | Y |
| N-002 | Failure | Missing expense account on category | Category account field is blank | 1. Create expense with category where account = blank. 2. Attempt to post. | Odoo raises error about missing account. Posting blocked. | No accounting impact. | Correct behavior. Without account, the expense line has nowhere to post. | Y |
| N-003 | Failure | Missing tax account on VAT tax configuration | Input VAT tax has no account configured | 1. Configure VAT tax with no tax account. 2. Create expense with this tax. 3. Attempt to post. | Odoo raises error about missing tax account. Posting blocked. | No accounting impact. | Correct behavior. Input VAT cannot be posted without a tax account. | Y |
| N-004 | Failure | Missing employee setup — employee not linked to user | Expense created by a user who has no employee record | 1. User creates expense. 2. System cannot link expense to an employee record. 3. Attempt to submit. | Odoo should require the expense to be associated with an employee. If no employee record exists for the user, submission may fail or create an unlinked expense. | Unlinked expense cannot be properly reimbursed. | Expense without an employee is an orphan record. Cannot be used for payable or reimbursement. Audit trail is incomplete. | Y |
| N-005 | Failure | Missing supplier TIN where withholding is required | Company-paid expense for professional services; supplier has no TIN on record | 1. Create company-paid expense for professional services. 2. Supplier record has no TIN. 3. EWT withholding rule applies. 4. Post. | Journal entry posts (Odoo does not block for missing TIN by default). But EWT is computed. However, 2307 certificate generation will fail or produce invalid certificate (no TIN). | Posting succeeds. Withholding computed. | 2307 without supplier TIN is invalid. BIR will not accept it. The company has withheld EWT but cannot issue a valid certificate. Custom validation should block posting or warn when TIN is missing and EWT applies. | N — requires custom validation module |
| N-006 | Failure | Invalid category setup — product category with circular tax dependency | Rare but possible: tax A includes tax B which includes tax A | 1. Create malformed tax with circular dependency. 2. Assign to expense category. 3. Create expense. 4. Attempt to post. | Odoo should detect circular tax reference and raise an error, or hang indefinitely. | No accounting impact if blocked. | Circular tax configurations are a system stability risk. Must be caught before they reach production. | Y |
| N-007 | Failure | Invalid withholding setup — withholding percentage = 0% | EWT rule created but rate set to 0 by mistake | 1. Create EWT rule at 0%. 2. Assign to expense category. 3. Post expense. | Journal entry has EWT line with PHP 0 withholding. AP payable = full gross. EWT Payable = PHP 0. | Functionally identical to no withholding. But the withholding line exists at PHP 0, which is misleading. | BIR expects non-zero EWT for applicable categories. A 0% EWT rule that exists but computes zero is a misconfiguration that will pass silently. 2307 would show PHP 0 EWT — functionally useless. | Y — detect zero-rate rule |
| N-008 | Failure | Invalid ATC mapping — ATC code not in BIR ATC table | User enters "ZZ999" as ATC, which does not exist in BIR's table | 1. Create EWT rule with ATC "ZZ999". 2. Post expense. 3. Generate 2307. | Certificate shows ATC "ZZ999". BIR system will reject this ATC on electronic filing. 1601-EQ with invalid ATC will fail e-filing validation. | Accounting entries are numerically correct. | Invalid ATC = rejected return at BIR e-filing portal. Must validate ATC against BIR's published ATC table. | N — requires ATC master data validation |
| N-009 | Failure | Inconsistent company / currency / branch data | Expense created in a branch company with different currency from the parent | 1. Multi-company setup: parent company in PHP, branch in USD. 2. Employee of parent company creates expense linked to branch company. 3. Currency conflict arises. | Odoo multi-company rules should enforce that the expense is posted to the correct company's books. Currency conversion must be explicit. | Multi-company journal entries with inter-company balancing. | Each BIR taxpayer (company/branch) files its own return. Cross-company expense posting must correctly attribute the expense to the right entity for the right return. | N — requires multi-company setup verification |
| N-010 | Failure | Deleted tax after draft expense was created | Tax T1 assigned to draft expense; T1 deleted before approval | 1. Create expense with tax T1 (12% VAT). 2. Admin deletes T1. 3. Submit expense. 4. Approve. 5. Post. | Odoo must either raise an error (tax no longer exists) or silently proceed without the tax. If it proceeds silently: no VAT line in journal entry despite employee having paid 12% VAT. | Either error (good) or silently wrong entry (bad). | Silent failure = loss of creditable input VAT. Employee paid PHP X including VAT; company does not claim it. Financial loss and inaccurate return. | Y — test error handling |
| N-011 | Failure | Changed tax configuration after approval but before posting | Tax rate changed from 12% to 0% after manager approved the report | 1. Expense approved with 12% VAT tax. 2. Admin changes tax rate to 0% (or reassigns account). 3. Accountant posts. 4. Verify: which rate was applied? | Odoo should apply the tax configuration as it was at the time the expense was created, not at the time of posting. If it applies current config: PHP 0 VAT is posted despite employee having paid 12%. | Post-approval config change creates a discrepancy between the OR (12% VAT) and the journal entry (0% VAT). | The posted entry does not match the source document. Input VAT is not claimed. Must verify Odoo 18 behavior and implement a control to lock tax configuration on expense after approval. | N — requires system behavior investigation |
| N-012 | Failure | Stale draft report after config change — category account changed | Category expense account changed after expense was created in draft | 1. Expense created in draft with account A. 2. Admin changes category to account B. 3. Expense posted. | Odoo may use account B (current config) or account A (account at time of creation) for posting. This depends on whether Odoo re-resolves the account at posting time. | If account B is used: expense may post to wrong account. | Wrong expense account = wrong P&L line = incorrect income tax return. | Y — test account resolution timing |
| N-013 | Failure | Unauthorized posting/reimbursement attempt | User without posting rights uses direct URL to access posting button | 1. Non-accountant user obtains URL of approved expense report. 2. Attempts to post via URL navigation. | Access control enforced at the application level. Posting fails with "Access Denied". Audit log records the unauthorized attempt. | No accounting impact. | Unauthorized posting bypass is a financial control failure. If successful, it bypasses the accounting review step. | Y |
| N-014 | Failure | Bad or missing attachments for policy-required expense categories | Category "International Travel" requires receipt; expense submitted without receipt | 1. Create international travel expense above PHP 5,000 without receipt. 2. Submit. | If ipai policy module is active: blocked at submission. If standard Odoo only: proceeds to manager who must enforce manually. | No accounting impact. | Receipt-less input VAT claim is disallowed by BIR. Missing OR = unsubstantiated claim for PHP X input VAT and expense deduction. | Y — test enforcement module |
| N-015 | Failure | Expense posted to wrong period due to incorrect posting date | Employee submits expense dated January; accountant posts with date in February (different quarter) | 1. Expense date = January. 2. Accountant posts with February date. 3. Expense appears in February ledger, not January. | Journal entry is in February. January books are unaffected. February books now include an expense that economically belongs to January. | Period allocation error. January P&L understated; February P&L overstated. | 2550Q for Q1 does not include the January input VAT; Q2 includes it. Filing discrepancy if January quarter return was filed before February posting. | N — requires date control review |

---

## 4. High-Risk Regression Suite

This is the minimum set of scenarios that must pass before any production release or significant configuration change. Each scenario is selected because it exercises a compliance-critical path that is both frequently encountered in PH deployments and most likely to fail silently.

| Suite ID | Maps to | Scenario description | Why mandatory |
|----------|---------|----------------------|---------------|
| REG-001 | E-002 | Employee-paid reimbursable VATable expense — complete flow: create, submit, approve, post, reimburse, verify input VAT account, verify employee payable cleared | Highest-volume PH expense flow. Input VAT misposting goes straight to 2550Q. |
| REG-002 | F-002 | Company-paid VATable expense — complete flow: create, post, verify input VAT, verify AP payable, verify supplier TIN on move | Second most common flow. AP + input VAT together. Withholding may also apply. |
| REG-003 | F-004 + H-001 + H-002 | Withholding-sensitive supplier/service expense — EWT computed on VAT-exclusive base, ATC present, journal balanced, 2307 data complete | Most compliance-critical. Wrong base or wrong ATC = invalid 2307 = BIR penalty. |
| REG-004 | C-003 + G-005 | Mixed-tax expense report — VATable + VAT-exempt + no-tax lines in one report — verify each line's tax treatment is independent, journal balanced, no cross-contamination | Most common report type in practice. Silent cross-contamination is the failure mode. |
| REG-005 | J-001 + J-003 + J-009 | Re-invoiced expense — expense posted, customer invoice generated, output VAT correct, no double-counting between input and output VAT | Critical for project-based businesses. Fiscal position errors cause incorrect output VAT. |
| REG-006 | L-001 + L-002 + L-004 | Reimbursement payment and reconciliation — employee payable cleared to zero, payment journal entry correct, no residual balance | Financial control gate. Uncleared payable = potential duplicate payment. |
| REG-007 | E-004 + G-009 + N-010 | Invalid tax/withholding setup negative path — VAT claimed on non-VAT purchase, deleted tax on draft expense, zero-rate EWT rule — each must either error correctly or be detectable | Silent failures in tax setup are the primary 2550Q risk. Must fail loudly or be caught. |
| REG-008 | M-008 + I-003 | Audit trail verification — complete chain from attachment to journal entry to payment, all links intact, OR number present on journal entry, supplier TIN present on move | BIR audit readiness. A broken chain at any point = an unsubstantiated claim. |
| REG-009 | H-004 | Withholding omitted when required — professional services category without EWT rule — verify system does not silently skip and that a detection report flags missing withholding | BIR penalizes the withholding agent (company) for failure to withhold. Must be caught pre-payment. |
| REG-010 | K-008 | Locked period posting — attempt to post expense into a closed/locked accounting period — verify block is effective | Prevents post-filing period entries from corrupting filed returns. |

**Execution requirement**: All REG-001 through REG-010 must pass (PASS state with accounting verification) before any production deployment. Failures block deployment. No partial-pass exceptions.

---

## 5. Automation Strategy

### Must Automate

These scenarios have fully deterministic inputs and outputs. The accounting logic is mechanical. Human judgment is not required to verify correctness. Automation provides the fastest and most reliable signal.

| Scenario group | Reason |
|----------------|--------|
| A-001, A-002, A-003, A-005 | Category tax configuration drives all downstream accounting. Deterministic: configure category → create expense → post → verify journal lines. |
| B-001, B-005, B-006, B-011, B-012, B-013 | Single-expense creation and validation. Amount and tax computed deterministically. |
| C-001, C-002, C-006, C-007, C-010 | Report creation and state transitions are deterministic workflow states. |
| D-001, D-002, D-003, D-004, D-005, D-006 | Role-based access control. Binary: allowed or denied. Fully automatable with test users. |
| E-001, E-002, E-006, E-007, E-008 | Reimbursement flows: amounts, payable balances, and payment reconciliation are deterministic. |
| F-001, F-002, F-003, F-004, F-005 | Company-paid accounting flows. Journal line amounts are computed from configured rates. |
| G-001 through G-008, G-010, G-012 | VAT computation, price-included vs excluded, rounding, missing account error handling. All deterministic. |
| H-001, H-002, H-003, H-004, H-005, H-006, H-007 | Withholding base computation, ATC presence, EWT payable amounts. Deterministic from configuration. |
| I-001, I-004, I-005 | Data completeness on journal lines (TIN, base, ATC present/absent). Can be checked programmatically. |
| J-001, J-002, J-003, J-008, J-009, J-010 | Re-invoicing flows with expected journal line composition. Deterministic from setup. |
| K-001 through K-007, K-010, K-011 | Journal integrity, correct accounts, state transitions. Deterministic from configuration. |
| L-001, L-002, L-003, L-004, L-007, L-008 | Payment and reconciliation amounts. Deterministic. |
| M-001 through M-007, M-010 | Report totals vs GL account totals. Cross-check is programmatic. |
| N-001, N-002, N-003, N-004, N-006, N-007, N-010, N-013, N-014 | Error handling and validation enforcement. Each has a deterministic expected error or block. |

**Automation framework recommendation**: Odoo 18 Python unit tests (`hr_expense` module test class inheriting from `AccountingTestCase`). Use `test_<module>` disposable database per test run. DO NOT run against `odoo_dev` or `odoo_staging`. Tests must create their own fixture data (companies, employees, categories, taxes, journals) and tear down after. Reference: `.claude/rules/testing.md`.

### Good to Automate (High Value but Higher Setup Cost)

These scenarios require more elaborate fixtures or involve multi-step flows that are testable but require significant test data setup.

| Scenario group | Reason |
|----------------|--------|
| C-003, C-004, C-005, C-008 | Mixed-category and mixed-currency reports. Require multiple pre-created expense fixtures. |
| E-003, E-005, E-009 | Non-creditable VAT, FX conversion, correction flow. Testable but require specific tax configurations. |
| G-009, N-011, N-012 | Config-change-during-draft scenarios. Require orchestrated sequence of config mutation + posting. |
| H-009, H-010 | Government withholding scenarios. Require specific customer/fiscal position setup plus multi-step payment flow. |
| H-011 | Partial payment withholding distribution. Requires multiple payment events in sequence. |
| J-004, J-005, J-007 | Fiscal position differences, government re-invoicing. Require specific customer master data. |
| K-008, K-009 | Locked period and reversal. Require period lock/unlock sequences. |
| L-005, L-006, L-009 | Post-correction payment flows. Require complete reset-correct-repost cycle before payment test. |
| M-008, M-009 | Audit trail and SLP completeness. Require full end-to-end fixture with attachments. |

### Keep Manual

These scenarios require human judgment, policy interpretation, document legibility review, or external-system interactions that cannot be reliably automated.

| Scenario group | Reason to keep manual |
|----------------|----------------------|
| B-002, B-010 | Attachment quality and legibility. System accepts any file; human must verify content is a valid OR. |
| B-004 | Supplier TIN missing on document — requires human cross-check of physical OR against system record. |
| B-009 | Multi-currency exchange rate sourcing. Rate must match BSP published rate for BIR compliance. Human must verify rate source. |
| C-009 | Stale draft after config change — requires human determination of which tax the OR actually shows. System behavior must be documented after manual investigation. |
| D-007, D-008 | Dual-role SOD and bypass attempt. D-007 is a policy documentation scenario; D-008 requires manual verification that the bypass control exists. |
| E-004 | VAT claimed on non-VAT purchase — requires human cross-check of OR (no VAT on OR) vs category (has VAT). Cannot be automated without OCR of the OR. |
| F-007 | Supplier invoice matching and withholding certificate linkage. Requires human reconciliation judgment. |
| H-009, H-010 | Government 2307 receipt and recording. External document from government entity; requires human follow-up. |
| H-012 | Compensation vs expense boundary. Policy-driven determination that requires HR and Finance joint review. |
| I-006 | Two-type 2307 from government (EWT + VAT withholding). Requires human coordination with government AP contact. |
| I-007 | Long-duration audit trail integrity (3-5 year horizon). Cannot be automated; requires periodic human verification. |
| M-008, M-009 | Full audit trail trace and SLP completeness review. Automated checks verify data presence; human must verify data accuracy and document readability. |
| N-005 | Missing supplier TIN with EWT — requires custom validation module decision. Policy and module implementation are human decisions. |
| N-008 | Invalid ATC code — requires validation against BIR's ATC master table, which must be maintained as a reference dataset. |
| N-015 | Wrong posting period — requires human review of expense date vs posting date policy and quarter-boundary management. |

---

## 6. Test Data Design

### Companies

| Entity | TIN | VAT Registration | Currency | Notes |
|--------|-----|-----------------|----------|-------|
| IPAI Main Co. | 000-000-000-001 | VAT-registered, 12% | PHP | Primary test company |
| IPAI Branch (USD) | 000-000-000-002 | VAT-registered | USD | Multi-currency branch for cross-company tests |
| Government Agency (Customer) | 000-111-000-001 | Government entity | PHP | Used for RMC 36-2021 / VAT withholding tests |

### Employees

| Role | Name | Manager | Notes |
|------|------|---------|-------|
| Regular employee | EMP-001 Juan dela Cruz | MGR-001 | Standard expense submitter |
| Regular employee | EMP-002 Maria Santos | MGR-001 | Used for wrong-employee edge case |
| Manager | MGR-001 Pedro Reyes | n/a | Expense approver for EMP-001 and EMP-002 |
| Manager-Accountant (dual role) | MGR-ACC-001 Ana Torres | n/a | SOD dual-role test subject |
| Accountant (no manage role) | ACC-001 Rosa Cruz | n/a | Posts journal entries; cannot approve |
| Finance (payment only) | FIN-001 Carlos Bautista | n/a | Registers reimbursement payments only |

### Suppliers

| Supplier | TIN | VAT Status | EWT Applicable | ATC | Notes |
|----------|-----|-----------|----------------|-----|-------|
| Hotel ABC | 123-456-789-000 | VAT-registered | No | n/a | Standard VAT hotel |
| Taxi Co. | n/a | Non-VAT | No | n/a | Non-VAT transport |
| IT Consultant A | 234-567-890-000 | VAT-registered | Yes, 2% EWT | WC158 | Professional services |
| Printing Shop B | 345-678-901-000 | Non-VAT | No | n/a | Non-VAT non-creditable |
| Conference Org C | 456-789-012-000 | VAT-registered | No | n/a | Conference registration |
| Law Firm D | 567-890-123-000 | VAT-registered | Yes, 10% EWT | WC160 | Legal services; higher EWT rate |
| Non-TIN Vendor | (blank) | Unknown | Potentially | Blank | Used for missing-TIN failure scenarios |

### Customers

| Customer | TIN | Type | Fiscal Position | Notes |
|----------|-----|------|-----------------|-------|
| Private Client A | 678-901-234-000 | Private sector | Standard PH | Standard private customer |
| Government Agency B | 000-111-000-001 | Government | Government PH — VAT withholding | Withholds 5% VAT + EWT |
| PEZA Entity C | 789-012-345-000 | PEZA | Zero-rated | 0% VAT on services |

### Expense Categories

| Category | Account | Tax | Payment Mode | EWT Rule | Notes |
|----------|---------|-----|--------------|----------|-------|
| Hotel / Accommodation | 600010 | 12% Input VAT (price-excluded) | Employee | None | Standard VATable |
| Transportation - Non-VAT | 600020 | None | Employee | None | Non-VAT supplier |
| Professional Fees | 600030 | 12% Input VAT | Company | 2% EWT WC158 | Withholding applies |
| Entertainment | 600040 | 12% VAT (non-creditable) | Employee | None | Non-creditable input VAT |
| Per Diem - Meals | 600050 | None | Employee | None | De minimis; no VAT |
| Project Travel - Rechargeable | 600060 | 12% Input VAT | Employee | None | Re-invoicing enabled |
| Legal Services | 600070 | 12% Input VAT | Company | 10% EWT WC160 | Higher EWT rate |
| International Travel | 600080 | None (foreign) | Employee | None | No input VAT; FX required |
| Misconfigured Category | 600099 | 12% VAT mapped to output VAT account | Employee | None | Used for misconfiguration tests only |

### Taxes

| Tax Name | Rate | Type | Account | Price | ATC | Notes |
|----------|------|------|---------|-------|-----|-------|
| 12% Input VAT - Local Services | 12% | Purchase | 190010 Input VAT | Excluded | n/a | Standard creditable input VAT |
| 12% Input VAT - Non-Creditable | 12% | Purchase | None (absorbed to expense) | Excluded | n/a | Entertainment, non-creditable |
| VAT-Exempt | 0% | Purchase | None | Excluded | n/a | Exempt purchases |
| Zero-Rated | 0% | Purchase | 190011 Zero-rated input | Excluded | n/a | PEZA/export |
| 2% EWT - Professional Services | 2% | Withholding | 200010 EWT Payable | n/a | WC158 | Creditable withholding tax |
| 10% EWT - Legal Services | 10% | Withholding | 200010 EWT Payable | n/a | WC160 | Creditable withholding tax |
| Broken Tax (no account) | 12% | Purchase | None | Excluded | n/a | Used for N-003 only |

### Journals

| Journal | Type | Currency | Notes |
|---------|------|----------|-------|
| Employee Expenses | Miscellaneous / Purchase | PHP | Used for all employee-paid expenses |
| Accounts Payable | Purchase | PHP | Used for all company-paid expenses |
| Main Bank | Bank | PHP | Reimbursement payments |
| Petty Cash | Cash | PHP | Small company-paid expenses |

### Currencies

| Currency | Rate (vs PHP) | Rate date | Notes |
|----------|--------------|-----------|-------|
| PHP | 1.00 | n/a | Company currency |
| USD | 57.50 | 2025-01-15 | Used for FX test scenarios |
| USD | 56.80 | 2025-02-01 | Second rate for FX gain/loss scenario |

### Reimbursement Cases

| Case ID | Employee | Report amount | Payment amount | Expected result |
|---------|----------|--------------|----------------|-----------------|
| RC-001 | EMP-001 | PHP 2,240 | PHP 2,240 | Full; payable cleared |
| RC-002 | EMP-001 | PHP 5,000 | PHP 4,000 | Partial; PHP 1,000 remaining |
| RC-003 | EMP-001 | PHP 8,750 (3 reports) | PHP 8,750 (1 payment) | Full multi-report; all cleared |
| RC-004 | EMP-001 | PHP 2,240 (already paid) | PHP 2,240 (attempt) | Blocked; duplicate prevention |

### Re-invoice Cases

| Case ID | Expense category | Customer | Markup | Expected output VAT |
|---------|-----------------|---------|--------|---------------------|
| RI-001 | Project Travel - Rechargeable | Private Client A | 0% | 12% on base |
| RI-002 | Project Travel - Rechargeable | PEZA Entity C | 0% | 0% |
| RI-003 | Project Travel - Rechargeable | Government Agency B | 0% | 12% output; 5% withheld by government |
| RI-004 | Project Travel - Rechargeable | Private Client A | 10% | 12% on base + markup |

### Source Documents (Test Fixtures)

| Doc ID | Type | Supplier | OR/SI Number | TIN | Base | VAT | Total | Notes |
|--------|------|----------|-------------|-----|------|-----|-------|-------|
| DOC-001 | OR | Hotel ABC | OR-2025-001 | 123-456-789-000 | 2,000 | 240 | 2,240 | Valid VAT OR |
| DOC-002 | OR | Taxi Co. | OR-2025-002 | n/a | 500 | 0 | 500 | Non-VAT |
| DOC-003 | SI | IT Consultant A | SI-2025-001 | 234-567-890-000 | 50,000 | 6,000 | 56,000 | Withholding applies |
| DOC-004 | None | n/a | n/a | n/a | n/a | n/a | 1,500 | Missing receipt scenario |
| DOC-005 | OR (corrupted file) | Hotel ABC | n/a | n/a | n/a | n/a | n/a | Unreadable attachment scenario |

---

## 7. PH/BIR Localization and Compliance Considerations

### VAT Registration vs Non-VAT Scenarios

The Philippines has two classes of suppliers relevant to expense processing:

**VAT-registered suppliers** charge 12% VAT. The purchasing company may claim this as creditable input VAT on BIR Form 2550Q, provided it has an official receipt or sales invoice showing the supplier's TIN, the VAT amount, and the OR/SI number. Expenses from VAT-registered suppliers without proper OR/SI cannot support an input VAT claim and should be recorded as a pure expense (no input VAT split).

**Non-VAT-registered suppliers** charge 3% percentage tax (or operate below the VAT threshold). The purchasing company has no creditable input VAT from these purchases. The 3% is the supplier's burden. The company records the full expense amount to the expense account with no input tax account entry.

**Implication for Odoo expense categories**: Each category must be aligned to the supplier type it is normally used with. If a category is used for both VAT and non-VAT suppliers, the employee or accountant must override the tax at the line level. This override capability must be tested (is it available in Odoo 18's expense module?) and the override must be documented in the expense record for audit purposes.

### Input VAT Support and Reporting Sensitivity

BIR Form 2550Q requires the following from the input VAT schedule:
- Total taxable purchases split by: local purchases of goods, local purchases of services, capital goods subject to amortization, importation of goods, services rendered by non-residents
- Total input VAT per category
- Total creditable input VAT (net of disallowed amounts)

Odoo's expense module must correctly classify each expense line to the right 2550Q input schedule box. This requires either:
1. BIR-specific tax tags on each tax record (e.g., "Local Purchases of Services" tag), or
2. Account-level classification where different input VAT accounts map to different 2550Q boxes

Without correct tax tags or account mapping, the 2550Q module cannot automatically populate the return from ledger data. This is the most frequently misconfigured element in PH Odoo deployments.

### Withholding Treatment Differences

**Creditable Withholding Tax on Income Payments (EWT)** — BIR Form 2307 / 1601-EQ:
Applied by the company when paying suppliers for services, rentals, or commissions. The ATC determines the rate and the return box. EWT is deducted from the net payment to the supplier. The company remits to BIR via 1601-EQ (monthly). The supplier receives a 2307 certificate to use as tax credit against their income tax.

**Withholding Tax on Compensation (WTC)** — BIR Form 2316 / 1601-C:
Applied by the company when paying salaries, wages, and compensation benefits to employees. This is processed through the payroll module (hr.payslip), not the expense module. The distinction is critical: if any benefit or allowance is disguised compensation and run through the expense module, it escapes 1601-C withholding and creates a compensation tax shortfall.

**Final Withholding Tax** — applicable to dividends, interest, specific passive income; generally not relevant to expense module flows.

**The expense module boundary**: Only EWT (first category above) can legitimately arise from expense module flows, and only for company-paid expenses to suppliers. Employee reimbursements are not subject to EWT. Any EWT withholding rule that appears on a pure employee reimbursement category is a misconfiguration.

### Government Withholding Behavior

Under existing BIR regulations and RMC 36-2021, government entities in the Philippines are required withholding agents. When the company is the vendor and the government is the customer:

**Income tax withholding**: Government withholds EWT from the company (vendor) at applicable rates. Company receives a BIR Form 2307 from the government for the withheld EWT. This 2307 is a tax asset that the company claims as creditable tax withheld on its annual income tax return.

**VAT withholding (RMC 36-2021)**: Government entities are required to withhold a portion of the VAT charged by vendors. The withheld VAT is remitted directly to BIR by the government. The vendor (company) receives a 2307 with the applicable VAT-withholding ATC as proof. The company uses this 2307 to credit the withheld VAT against its output VAT liability on 2550Q. If the 2307 is not received or is not recorded, the company remits the full 12% output VAT to BIR even though a portion was already remitted by the government — resulting in double remittance.

**Odoo implication**: When customer invoices are created for government customers, the accounts receivable posted must anticipate a net payment (payment minus withholding). The creditable tax assets (both EWT and VAT) must be recorded from the received 2307s. This requires either a custom workflow or a manual journal entry. Standard Odoo CE does not automate the receipt-of-2307 workflow.

### 2307-Sensitive Scenarios

BIR Form 2307 (Certificate of Creditable Tax Withheld at Source) is sensitive to the following data elements, all of which must be correctly stored in Odoo:
1. Name and TIN of the withholding agent (company)
2. Name and TIN of the payee (supplier or, in reverse, the customer who withheld from the company)
3. ATC (Alphanumeric Tax Code) specifying the nature of the income payment
4. Taxable amount (income payment base, exclusive of VAT)
5. Tax rate (matching the ATC)
6. Tax withheld amount
7. Quarter covered by the certificate
8. Date of issuance

In Odoo, items 1-8 must be derivable from the journal entry and its associated partner/tax records. If any element is missing (particularly TIN or ATC), the downstream 2307 generation module (OCA l10n_ph or ipai_bir_withholding) will produce an incomplete or invalid certificate.

### 1601-C Boundary Scenarios

BIR Form 1601-C is the monthly remittance return for withholding on compensation. It must include only withholding on salaries, wages, and compensation to employees. It must NOT include:
- EWT on supplier payments (1601-EQ scope)
- Final withholding tax (1601-FQ scope)
- VAT withholding (2550M/2550Q scope)

The risk in Odoo deployments is that employee expense reimbursements — particularly allowances that blur the line between compensation and cost reimbursement — may be processed through the expense module and treated as EWT, when the correct treatment would be 1601-C compensation withholding via payroll. The boundary test (H-012) is specifically designed to surface this classification risk.

### 2550Q-Sensitive Scenarios

BIR Form 2550Q is the quarterly VAT return. It requires:
- Total output VAT (from sales/invoices)
- Total input VAT (from purchases/expenses), split by type
- Input VAT carried forward from prior quarter
- Net VAT payable or refundable

The expense module contributes to the input VAT side. The most sensitive scenarios are:
- Claiming input VAT from a non-VAT supplier (G-004, N-005) — overclaiming
- Claiming non-creditable input VAT (entertainment, E-003) — overclaiming
- Omitting creditable input VAT because of a misconfigured category (A-001 on a VATable purchase) — underclaiming
- Wrong 2550Q box due to incorrect tax tag (A-010) — misallocation

Overclaiming triggers a BIR deficiency assessment and penalties. Underclaiming means the company paid more VAT than required — a cash loss.

### Historical/Legacy 2550M Sensitivity

BIR Form 2550M (Monthly VAT Declaration) was replaced by a combined quarterly filing approach under certain BIR issuances, but some businesses remain subject to monthly VAT declarations depending on their taxpayer classification and filing history. The test plan covers 2550Q as the primary target, but if the company's registered filing frequency is monthly, all scenarios marked as "feeds 2550Q" equivalently feed the monthly 2550M return. The accounting impact is the same; only the filing period differs. Confirm the company's registered filing frequency before configuring period-end VAT return generation in Odoo.

### Need for Accurate ATC Mapping

ATCs (Alphanumeric Tax Codes) are the BIR's classification system for income payments subject to withholding. Common ATCs relevant to expense flows:

| ATC | Description | Rate |
|-----|-------------|------|
| WC157 | Income payments to suppliers of goods | 1% |
| WC158 | Income payments to suppliers of services | 2% |
| WC160 | Professional fees — lawyers, CPAs, doctors | 10% or 15% depending on gross income |
| WI010 | Rental of real property (non-resident) | varies |
| WV010 | VAT withholding by government — creditable | 5% of VAT charged |

Each ATC must be stored in the Odoo withholding tax configuration record and must propagate to the journal move line. If the ATC is incorrect, the 2307 is invalid and the 1601-EQ return will have misallocated amounts.

### Need for Traceable Source Documents and Audit Trail

The BIR's audit process begins with the filed return and traces backward:
1. 2550Q total input VAT → input VAT account balance → individual tax move lines
2. Individual tax move line → journal entry → expense report → expense line
3. Expense line → OR/SI attachment → physical or scanned source document
4. Source document shows: supplier name, TIN, OR number, date, base amount, VAT amount

If any link in this chain is broken, the BIR examiner will disallow the related input VAT claim. The chain must be intact for every expense where input VAT was claimed. The audit trail scenarios (M-008, M-009, I-003, I-007) are specifically designed to verify this chain's integrity.

---

## 8. Gaps and Assumptions

### Odoo 18 CE Behavior Unknowns (Must Verify Before Go-Live)

| Gap ID | Item | Risk if wrong assumption | How to verify |
|--------|------|--------------------------|---------------|
| GAP-001 | Does Odoo 18 re-resolve tax from category at posting time, or does it lock the tax on the expense record at creation time? | If re-resolved at posting: config changes between creation and posting silently change the tax. C-009, G-009, N-011 all depend on this. | Create expense with tax T1. Change T1 to exempt. Post. Inspect journal entry tax line. |
| GAP-002 | Does Odoo 18 re-resolve the expense account from category at posting time? | If re-resolved: account changes between draft and posting change where the expense is posted. N-012 depends on this. | Same test pattern as GAP-001 but for the product account field. |
| GAP-003 | Does Odoo 18 block posting if a referenced tax is archived/deleted after the expense was created? | If it silently drops the tax line: creditable input VAT is lost without error. N-010 depends on this. | Create expense with tax T1. Archive T1. Post. Inspect journal entry. |
| GAP-004 | Does Odoo 18 expense module support line-level tax override (employee can change category-default tax on a specific expense line)? | If no line-level override: mixed VAT/non-VAT expenses from the same category must use separate expense records, increasing submission overhead. B-004 depends on this. | Attempt to modify the tax field on an expense line after category selection. |
| GAP-005 | Does Odoo 18's standard withholding tax module compute EWT base on net-of-VAT or gross-with-VAT? | If on gross-with-VAT: EWT is overcalculated for every VATable expense. H-002 is the critical test. | Create expense with both 12% VAT and 2% EWT. Verify EWT base in journal entry. |
| GAP-006 | Does Odoo 18 prevent partial payments from being registered on an already-paid expense report? | If not blocked: duplicate reimbursements are possible. E-008 depends on this. | Pay expense. Then attempt to register a second payment. |
| GAP-007 | How does Odoo 18 handle reversal of a posted expense — does the expense report return to "Draft" or "Refused"? | If it goes to a non-editable state: correction workflow breaks. K-009 depends on this. | Post expense. Reverse journal entry from accounting. Check expense report state. |
| GAP-008 | Does OCA l10n_ph (or the deployed ipai_bir_withholding module) correctly read ATC from the withholding tax line and populate the 2307 certificate? | If ATC is not read correctly: all 2307 certificates generated will have blank or wrong ATC. I-001, H-006, H-007 depend on this. | Post expense with known ATC. Generate 2307. Inspect ATC field on certificate. |

### Company Tax Policy Assumptions (Must Confirm)

| Assumption ID | Assumption | Action required |
|--------------|------------|-----------------|
| POL-001 | The company is VAT-registered and files 2550Q quarterly. | Confirm with tax counsel. Determine if monthly 2550M also applies. |
| POL-002 | All professional services paid by the company are subject to EWT. | Confirm with tax counsel which specific categories require withholding and at what ATC. |
| POL-003 | Employee reimbursements are NOT treated as compensation for 1601-C purposes. | Confirm with HR and tax counsel. If any allowance is compensation in nature, it must go through payroll. |
| POL-004 | Entertainment expenses are limited to 0.5% of net sales (for deductibility purposes). | Confirm limits and whether Odoo's expense module needs a budget control for entertainment. |
| POL-005 | De minimis benefits (meal allowances below PHP 2,000/month, etc.) are exempted from tax as per TRAIN law. | Confirm de minimis limits and whether the expense module needs to track and cap these. |
| POL-006 | The company has government customers and is subject to RMC 36-2021 VAT withholding. | Confirm which customers are government entities and ensure they are configured with the correct fiscal position. |
| POL-007 | Company has a receipt requirement policy: receipts required for all expenses above a defined threshold. | Define the threshold and whether to enforce it via system block or manual manager review. |

### BIR Compliance Interpretation Gaps

| Gap ID | Item | Implication |
|--------|------|-------------|
| BIR-001 | BIR has not issued specific guidance on Odoo-generated 2307 certificates. The certificate format must match the BIR prescribed format exactly. | The ipai_bir_withholding module's 2307 output must be reviewed against the current BIR-prescribed form before use in production. |
| BIR-002 | The treatment of withholding on partial payments is governed by RR 11-2018 but Odoo's standard withholding module may compute EWT at bill posting, not at payment time. | Verify whether the deployed withholding module computes EWT at payment or at bill posting, and whether this matches BIR's required timing. |
| BIR-003 | The BIR's SLP/SLS (Summary List of Purchases/Sales) format requirements may differ from Odoo's standard purchase/sale register. | The purchase register output from Odoo must be tested against the BIR's current SLP format requirements before using it for quarterly submission. |
| BIR-004 | Input VAT on entertainment is specifically disallowed under Section 110(B) of the NIRC. The tax configuration for entertainment must mark the input VAT as non-creditable, not as zero-rated or exempt. | Verify that the entertainment category tax is correctly classified as "non-creditable input VAT" in Odoo (absorbed to expense, not to input VAT account). |

### Reimbursement Policy Gaps

| Gap ID | Item | Action required |
|--------|------|-----------------|
| REI-001 | Is there a maximum per-diem rate? | Define in expense category maximum amount or company policy documentation. |
| REI-002 | Is there an approval matrix based on expense amount tiers (e.g., above PHP 50,000 requires VP approval)? | Configure in Odoo's expense approval settings or ipai_expense_policy module. |
| REI-003 | What is the company's policy on foreign currency expenses — is the employee reimbursed at the BSP rate on the transaction date, or at the rate on the payment date? | Define in policy document and configure system accordingly. |
| REI-004 | Does the company allow expenses from prior periods (e.g., an expense from 3 months ago) to be submitted? | Define cut-off policy and whether Odoo's expense module enforces it. |

### Expense Evidence Policy Gaps

| Gap ID | Item | Action required |
|--------|------|-----------------|
| EVI-001 | Which expense categories require a formal OR/SI (as opposed to an informal receipt or petty cash voucher)? | List must be defined per category. Input VAT can only be claimed for formal ORs from VAT-registered suppliers. |
| EVI-002 | How long must expense attachments be retained? BIR audit window is up to 10 years for fraud cases. | Confirm with tax counsel. Ensure Odoo/Azure storage retention policy matches. |
| EVI-003 | What is the process when an OR is lost after the expense has been approved and posted? | Define the correction/reversal procedure and document it as a policy exception. |

---

## Top 15 PH/BIR-Specific Scenarios Most Likely to Fail in Production

Ranked by combined operational impact and compliance risk. "Operational impact" means the failure directly disrupts financial operations (wrong payments, blocked postings, incorrect books). "Compliance risk" means the failure directly affects a filed BIR return or an audit defense.

---

**Rank 1 — Input VAT overclaimed from a non-VAT supplier (Scenario E-004, G-004)**

Operational impact: MEDIUM. Compliance risk: CRITICAL.

An expense category that has a 12% input VAT tax configured will apply that VAT to every expense posted against it, regardless of whether the actual receipt is from a VAT-registered supplier. If an employee uses this category to record a purchase from a non-VAT-registered supplier (e.g., a small printing shop), Odoo will split the amount into a base and a VAT component and debit the input VAT account. The company is claiming input VAT it never actually paid, because the non-VAT supplier did not charge VAT. BIR will disallow the claim. This is the highest-volume silent failure mode because it requires human judgment at the line level to override the category-default tax — a step that most employees skip.

Mitigation: require non-VAT-specific expense categories for non-VAT-supplier purchases, or implement a submission-time warning if no supplier TIN is entered but the category has a VAT tax.

---

**Rank 2 — EWT computed on gross-of-VAT amount instead of net-of-VAT (Scenario H-002)**

Operational impact: MEDIUM (supplier overpayment of certificate; company over-remits). Compliance risk: CRITICAL.

If Odoo's withholding tax module computes EWT on the total invoice amount (including VAT) rather than on the VAT-exclusive amount, every EWT computation involving a VAT-registered supplier will be wrong. The overcalculated EWT increases the supplier's 2307 credit beyond what was actually due. The company remits the correct EWT amount to BIR per their 1601-EQ computation, but the 2307 they issued to the supplier shows a different (higher) figure. This creates a mismatch when the supplier claims their credit. Depending on which direction the error runs, either the company under-remits (BIR penalty) or the supplier over-claims (potential BIR assessment of the supplier). This failure mode occurs at setup time and will affect every single EWT-applicable expense in production.

---

**Rank 3 — Blank or incorrect ATC on withholding journal entry (Scenarios H-006, H-007)**

Operational impact: LOW. Compliance risk: CRITICAL.

If the ATC field is not mapped in the withholding tax rule configuration, or is mapped to the wrong ATC, every 2307 certificate generated from that rule will have a blank or incorrect ATC. A blank-ATC 2307 is legally invalid — the supplier cannot use it to claim a tax credit. A wrong-ATC 2307 directs the credit to the wrong income type, causing the supplier's income tax return to fail BIR's ATC-level reconciliation. Meanwhile, the company's 1601-EQ return will aggregate EWT amounts under the wrong ATC bucket, causing the same reconciliation failure at BIR. This is a configuration-time failure that cascades to every single EWT transaction for the life of the deployment.

---

**Rank 4 — Employee reimbursement routed to AP payable instead of employee payable (Scenario F-006)**

Operational impact: HIGH. Compliance risk: HIGH.

If a company-paid expense category is accidentally configured with an employee payable account (or vice versa), the payable aging reports will show employee balances that are actually supplier AP, or supplier AP that is actually employee reimbursement. The immediate operational impact is that reimbursement payments may be made to employees for amounts the company already paid, creating a double disbursement. The compliance impact is that withholding certificates (2307) issued from the AP flow would reference employees as payees, which is incorrect. The reversal and correction of this error after payments have been made is complex and requires a full journal reversal and reissue of any affected certificates.

---

**Rank 5 — Non-creditable input VAT (entertainment) incorrectly claimed on 2550Q (Scenario E-003)**

Operational impact: LOW. Compliance risk: CRITICAL.

Section 110(B) of the NIRC disallows input VAT on entertainment, amusement, and recreation expenses. If the entertainment expense category in Odoo is configured with a standard 12% creditable input VAT tax (rather than a non-creditable version that absorbs the VAT into the expense account), the input VAT from entertainment expenses will flow into the creditable input VAT account and appear on the 2550Q input schedule. BIR examiners specifically look for entertainment input VAT claims and will disallow them with penalties. The correct configuration is to mark the entertainment VAT as non-creditable so it is absorbed into the entertainment expense account, not the input VAT account.

---

**Rank 6 — Government customer does not receive correct output VAT on re-invoiced expense (Scenario J-005, H-010)**

Operational impact: MEDIUM. Compliance risk: CRITICAL (RMC 36-2021).

When a company invoices a government customer and does not correctly configure the fiscal position to reflect government VAT-withholding requirements, the customer invoice may show an incorrect total, an incorrect VAT amount, or no provision for the VAT that the government is required to withhold. This leads to: (a) the government paying the wrong net amount, (b) the company failing to record the creditable VAT asset from the government's 2307, and (c) the company remitting full output VAT to BIR when the government has already remitted a portion. The net result is the company overpays VAT to BIR. Under RMC 36-2021, this scenario is increasingly common as more government entities properly withhold.

---

**Rank 7 — Stale draft expense picks up wrong tax after category configuration change (Scenario C-009, G-009)**

Operational impact: MEDIUM. Compliance risk: HIGH.

This is an insidious failure mode because it is invisible at the time of posting. An expense is created in draft when the category has a 12% VAT tax. An admin changes the category tax to exempt (perhaps to correct a different deployment error). The expense approver and accountant proceed without reviewing the tax change because the expense looks normal. The posted journal entry has no input VAT, but the employee's OR clearly shows 12% VAT. The company has overpaid the employee (full amount including VAT) but has not claimed the input VAT. This is a financial loss, not a tax overclaim, but it accumulates silently across every expense created before the config change.

---

**Rank 8 — Duplicate reimbursement payment on an already-paid report (Scenario E-008)**

Operational impact: CRITICAL. Compliance risk: MEDIUM.

If Odoo's reconciliation control does not prevent a second payment registration on a fully reconciled expense report, a finance user can inadvertently pay an employee twice for the same expense. This is a cash disbursement control failure. In a high-volume deployment, the probability of this occurring is proportional to report volume. The compliance implication is that the double payment appears as an unexplained cash outflow. If the second payment is to an employee for what was originally a company-paid expense (due to the F-006 misconfiguration), the double payment may also attract scrutiny as a disguised benefit subject to 1601-C withholding.

---

**Rank 9 — Missing supplier TIN on EWT-applicable expense prevents valid 2307 issuance (Scenario N-005)**

Operational impact: MEDIUM. Compliance risk: CRITICAL.

If the company posts an EWT-applicable expense against a supplier who has no TIN recorded in Odoo, the journal entry will compute and post the EWT correctly, and the 1601-EQ remittance will include the correct amount. However, the 2307 certificate cannot be issued with a valid TIN for the payee. The supplier cannot use a blank-TIN 2307 to claim their tax credit. The company has withheld from the supplier and remitted to BIR, but has not fulfilled its obligation to issue a valid certificate. BIR may penalize the company for failing to issue a compliant 2307. This failure is preventable only through a pre-posting validation that checks for supplier TIN when an EWT rule is applied.

---

**Rank 10 — Expense posted to wrong accounting period (Scenario N-015)**

Operational impact: HIGH. Compliance risk: HIGH.

When an expense with a January receipt date is posted with a February posting date (a different VAT quarter), the input VAT from that expense is excluded from the Q1 2550Q and incorrectly included in the Q2 2550Q. If the Q1 return has already been filed before the posting is made, the filed return understates input VAT and the company has overpaid Q1 VAT. The company would need to file an amended return (BIR Form 2550Q-A) to recover the overpayment. The operational impact is significant: amended returns require engagement with BIR and carry audit risk. This failure is common in organizations where the approval cycle is slow and expenses from Q1 are not posted until mid-Q2.

---

**Rank 11 — Compensation benefit misclassified as expense reimbursement — 1601-C boundary failure (Scenario H-012)**

Operational impact: MEDIUM. Compliance risk: CRITICAL.

If an HR or Finance manager routes a compensation benefit (e.g., a fixed monthly "transportation allowance" paid to an employee regardless of actual transportation costs) through the expense module, the system treats it as an expense reimbursement, not as compensation. The amount is posted to an expense account with no withholding tax (since expense reimbursements are not subject to EWT or WTC in this context). The 1601-C return will understate compensation taxable income. BIR may assess the company for deficiency withholding tax on compensation, plus penalties and interest. The distinction between a genuine cost reimbursement and a taxable compensation benefit must be enforced at the HR policy level, with finance reviewing expense categories for any that are regularly used to pay fixed amounts.

---

**Rank 12 — Mixed-tax expense report with input VAT crossing into VAT-exempt line (Scenario C-003, G-005)**

Operational impact: MEDIUM. Compliance risk: HIGH.

In a report containing both VATable and VAT-exempt expense lines, if Odoo applies the first line's tax to all lines (due to a report-level tax application bug or incorrect category configuration), VAT-exempt purchases will appear to have creditable input VAT. This overclaims input VAT on the 2550Q. Conversely, if a VATable line is silently stripped of its tax due to a report-level aggregation issue, the input VAT is underclaimed. Both directions are problematic. This failure mode is specific to multi-line, mixed-tax reports and is more likely in a deployment with many similar expense categories that differ only in tax treatment.

---

**Rank 13 — VAT rounding accumulation error across high-volume expense reports (Scenario G-008)**

Operational impact: LOW per report. Compliance risk: HIGH at scale.

Individual rounding errors on expense VAT computation (e.g., PHP 1,003.00 × 12% = PHP 120.36, rounded to PHP 120.00 — a PHP 0.36 difference) are trivial at the single-report level. However, in an organization processing hundreds or thousands of expense reports per quarter, these rounding errors accumulate. The 2550Q input VAT total derived from the ledger will differ from the sum of individual OR-level VAT amounts by the accumulated rounding difference. BIR may request a detailed reconciliation. If the rounding methodology is inconsistent across different computations (some rounding up, some truncating), the accumulated error can be larger and unpredictable.

---

**Rank 14 — Audit trail broken between expense attachment and journal entry (Scenario M-008)**

Operational impact: LOW. Compliance risk: CRITICAL during BIR audit.

This failure does not affect daily operations at all — posted journal entries, payments, and reports all look correct. The failure is only discovered during a BIR audit when the examiner requests the source document for a specific input VAT claim. If the OR attachment was deleted, the link between the expense report and the attachment was broken by a storage migration, or the attachment is unreadable (corrupted file), the company cannot produce the required OR. The BIR will disallow the entire input VAT claim for that expense, plus potentially apply a deficiency VAT assessment plus penalties. In a large organization with years of expense records and potentially multiple storage migrations, this risk compounds over time.

---

**Rank 15 — Re-invoiced expense with wrong tax mapping creates incorrect 2550Q output position (Scenario J-006)**

Operational impact: MEDIUM. Compliance risk: HIGH.

When an expense is re-invoiced to a customer and the customer's fiscal position incorrectly remaps the output VAT to zero or to the wrong tax code, the customer invoice is undercharged for VAT (if zero-mapped) or charged with the wrong VAT type. If zero-mapped for a private-sector customer who should pay full 12% VAT: the company under-collects output VAT from the customer, remits zero output VAT to BIR for that transaction, and understates output VAT on 2550Q. BIR will detect the discrepancy between the company's SLS (which shows the invoice amount) and the 2550Q output VAT (which is lower than expected). This is the most likely re-invoicing failure mode in deployments where multiple customer types (private, government, PEZA) share overlapping fiscal position configurations.

---

*End of test plan. Total scenarios: 155 (A: 10, B: 13, C: 11, D: 9, E: 10, F: 8, G: 12, H: 13, I: 7, J: 11, K: 11, L: 9, M: 10, N: 15, Regression: 10). Last updated: 2026-04-09.*
