# Record-to-Report Skill Pack

> Odoo 18 CE + OCA | SAP-equivalent: FI-GL (Close & Reporting) + CO-PA

---

## Scope

Transaction posting through to financial statement generation: journal entry creation,
reconciliation, period-end adjustments, trial balance, income statement, balance sheet,
and cash flow statement. Covers accruals, deferrals, FX revaluation, intercompany
elimination, and management reporting using OCA MIS Builder.

---

## Concepts

| Concept | SAP Equivalent | Odoo Surface |
|---------|---------------|--------------|
| Journal Entry | FB01 (Document Posting) | `account.move` (type=entry) |
| Recurring Entry | FBD1 (Recurring Document) | `account.move` + OCA recurring |
| Bank Reconciliation | FF67 (Bank Reconciliation) | `account.bank.statement.line` matching |
| Trial Balance | F.01 (Trial Balance) | OCA `account_financial_report` |
| Balance Sheet | F.01 + S_ALR_87012284 | OCA `account_financial_report` or `mis_builder` |
| Income Statement | S_ALR_87012271 | OCA `account_financial_report` or `mis_builder` |
| Cash Flow Statement | S_ALR_87012272 | OCA `mis_builder` with cash flow template |
| Accrual/Deferral | FBS1 (Accrual Document) | Manual `account.move` or OCA `account_cutoff_*` |
| FX Revaluation | FAGL_FC_VAL | OCA `account_multicurrency_revaluation` |
| Period Close | MMPV (Period Close) | Lock dates on `res.company` |
| Consolidation | CX10/CX20 | Multi-company reporting + elimination entries |

---

## Must-Know Vocabulary

- **account.move (type=entry)**: Manual journal entry for adjustments, accruals, reclassifications.
- **account.bank.statement**: Bank statement header. Contains lines for reconciliation.
- **account.bank.statement.line**: Individual bank transaction matched to journal entries.
- **account.full.reconcile**: Group of `account.move.line` records that net to zero.
- **account.partial.reconcile**: Partial matching of move lines (open balance remains).
- **mis.report**: OCA MIS Builder report definition. Matrix of KPIs vs periods.
- **mis.report.instance**: Configured run of a MIS report with specific date ranges.
- **account_financial_report**: OCA suite of standard financial reports (trial balance,
  aged partner, general ledger, journal ledger).
- **Lock date**: Two levels -- `period_lock_date` (soft, advisers bypass) and
  `fiscalyear_lock_date` (hard, no bypass).
- **Currency revaluation**: Adjusts unrealized gains/losses on foreign-currency open items.

---

## Core Workflows

### 1. Daily Transaction Posting
1. Transactions auto-post from sub-ledgers: invoices (AP/AR), payments, inventory moves.
2. Manual entries via `account.move` (type=entry) for adjustments.
3. All entries require balanced debits and credits per move.
4. Entries posted to specific journals (general, adjustment, closing).

### 2. Bank Reconciliation
1. Import bank statements (OFX, CAMT.053, CSV, MT940).
2. Auto-matching rules (`account.reconcile.model`) match statement lines to open items.
3. Manual matching for unmatched lines via reconciliation widget.
4. Unmatched lines create new journal entries (bank fees, interest, etc.).
5. Reconciliation complete when all statement lines are matched.

### 3. Period-End Adjustments
1. **Accruals**: Recognize expenses/revenue earned but not yet invoiced.
   Create reversing journal entries with OCA `account_cutoff_accrual_picking` or manual.
2. **Deferrals**: Prepaid expenses spread over future periods. Manual entries or
   OCA `account_cutoff_prepaid`.
3. **Depreciation**: Asset depreciation entries from OCA `account_asset_management` (CE has NO native asset module — Enterprise-only).
4. **FX revaluation**: OCA `account_multicurrency_revaluation` adjusts open items to
   period-end exchange rates. Posts unrealized gain/loss entries.
5. **Provisions**: Manual entries for doubtful debts, warranties, etc.

### 4. Trial Balance Verification
1. Generate trial balance via OCA `account_financial_report`.
2. Verify total debits = total credits (always true in double-entry, but verify per account).
3. Compare sub-ledger totals (AP/AR aging) to GL control accounts.
4. Investigate and resolve differences before closing.

### 5. Financial Statement Generation
1. **Income Statement**: OCA `mis_builder` with P&L template or `account_financial_report`.
2. **Balance Sheet**: MIS Builder template with assets, liabilities, equity sections.
3. **Cash Flow Statement**: MIS Builder indirect method (net income + adjustments) or
   direct method (cash receipts/payments).
4. Period comparison (current vs prior year, current vs budget).
5. Export to XLSX, PDF, or push to Databricks for BI dashboards.

### 6. Period Close Process
1. Ensure all transactions posted (no draft entries in the period).
2. Complete bank reconciliation for all bank journals.
3. Post all period-end adjustments.
4. Run trial balance and verify.
5. Generate financial statements.
6. Set `period_lock_date` via OCA `account_lock_date_update` wizard (logs the action).
7. Year-end: generate closing entry (P&L to retained earnings).
8. Set `fiscalyear_lock_date` after audit completion.

---

## Edge Cases

- **Unbalanced multi-currency entries**: Each entry must balance in both company currency
  and transaction currency. Exchange rate differences auto-adjust.
- **Retroactive corrections**: Entries before lock date require lock date reset (adviser only).
  OCA `account_lock_date_update` provides audit trail for changes.
- **Sub-ledger vs GL mismatch**: If AP/AR aging totals differ from GL control account, look
  for entries posted directly to control accounts (bypass of sub-ledger).
- **Intercompany transactions**: Must net to zero across companies. Elimination entries
  remove intercompany balances in consolidated reports.
- **Recurring entries drift**: Monthly recurring entries on the 31st skip short months.
  Use OCA `account_move_template` for controlled recurring patterns.
- **Retained earnings account**: Odoo auto-computes retained earnings for balance sheet.
  The account type `equity_unaffected` serves this role. Only one account should have
  this type per company.
- **Audit adjustments**: Post-close audit findings require lock date reset, adjustment
  entry, and re-close. Document the full cycle.

---

## Controls & Compliance

| Control | Implementation |
|---------|---------------|
| Period lock | `period_lock_date` prevents non-adviser edits. `fiscalyear_lock_date` is absolute. |
| Close checklist | Custom `ipai_*` server action or OCA module for mandatory pre-close checks. |
| Reconciliation completeness | Monitor `account.bank.statement.line` with `is_reconciled=False`. |
| Trial balance sign-off | Export trial balance, attach to `ir.attachment` with approval note. |
| Financial statement approval | Board/management sign-off before fiscal year close. |
| Audit trail | All `account.move` records immutable once posted. Reversal entries for corrections. |
| Sequential numbering | No gaps in posted entry sequences (legal requirement). |
| Multi-company consolidation | Separate close per company, then consolidated elimination. |

---

## Odoo/OCA Implementation Surfaces

### Core Odoo 18 CE Models
- `account.move` / `account.move.line` -- all journal entries
- `account.bank.statement` / `account.bank.statement.line` -- bank reconciliation
- `account.full.reconcile` / `account.partial.reconcile` -- matching engine
- `account.reconcile.model` -- auto-matching rules
- `account.account` -- GL accounts with `account_type`
- `res.company` -- lock dates, fiscal settings, currency

### OCA Modules (18.0-compatible)
| Module | Repo | Purpose |
|--------|------|---------|
| `account_financial_report` | OCA/account-financial-reporting | Trial balance, GL, aged partner, journal ledger |
| `mis_builder` | OCA/mis-builder | Flexible financial reporting engine (P&L, BS, CF) |
| `mis_builder_budget` | OCA/mis-builder | Budget vs actual comparison in MIS reports |
| `account_lock_date_update` | OCA/account-financial-tools | Wizard to change lock dates with logging |
| `account_fiscal_year` | OCA/account-financial-tools | Explicit fiscal year/period objects |
| `account_move_template` | OCA/account-financial-tools | Predefined entry templates for recurring postings |
| `account_cutoff_accrual_picking` | OCA/account-closing | Auto-accruals based on received-not-invoiced |
| `account_multicurrency_revaluation` | OCA/account-closing | Period-end FX revaluation |
| `account_reconcile_oca` | OCA/account-reconcile | Enhanced reconciliation UX |

---

## Azure/Platform Considerations

- **Reporting performance**: MIS Builder runs complex SQL. For large datasets (>1M move
  lines), pre-aggregate with PostgreSQL materialized views or extract to Databricks.
- **Scheduled close tasks**: Azure Container Apps cron jobs for auto-posting recurring
  entries, bank statement imports, and reconciliation model execution.
- **Backup before close**: Trigger `pg_dump` snapshot before setting lock dates.
  Store in Azure Blob Storage with retention policy.
- **Multi-company reporting**: Consolidated reports query across company boundaries.
  Ensure `ir.rule` does not block cross-company read for reporting users.
- **Financial data retention**: Legal retention (10 years in PH for BIR). Archive older
  fiscal years to cold storage but keep GL balances accessible.

---

## Exercises

### Exercise 1: Month-End Close Walkthrough
For March 2026: (1) verify no draft entries, (2) complete bank reconciliation, (3) post
an accrual for PHP 50K utilities received but not invoiced, (4) run trial balance,
(5) set period lock date.

### Exercise 2: MIS Builder P&L Report
Install `mis_builder`. Create a P&L report template with: Revenue, COGS, Gross Profit,
Operating Expenses (by category), EBITDA, Depreciation, Net Income. Configure an instance
for Q1 2026 with prior-year comparison.

### Exercise 3: FX Revaluation
Set up a vendor with USD-denominated open bills. Run `account_multicurrency_revaluation`
with the month-end rate. Verify the unrealized gain/loss journal entry and its impact on
the trial balance.

### Exercise 4: Intercompany Elimination
Two companies: Parent Co and Subsidiary Co. Parent invoices Subsidiary PHP 200K for
management fees. Generate individual company P&L reports, then create elimination entries
and generate a consolidated P&L. Verify the intercompany revenue/expense nets to zero.

### Exercise 5: Year-End Close
For FY 2025: (1) set period lock for all months, (2) generate year-end closing entry
(P&L to retained earnings), (3) verify opening balances for FY 2026, (4) set fiscal
year lock date.

---

## Test Prompts for Agents

1. "Run a trial balance as of March 31, 2026 using OCA account_financial_report. Show
   totals by account type and flag any accounts with unusual balances."

2. "Create a recurring journal entry template for monthly rent expense (PHP 120K, debit
   Rent Expense, credit Accrued Liabilities) that auto-reverses on the 1st of the next month."

3. "Generate a balance sheet using MIS Builder as of March 31, 2026. Compare against
   December 31, 2025. Highlight accounts with >20% change."

4. "We have 15 unreconciled bank statement lines for March. Show me the lines, run auto-
   matching, and report which ones still need manual reconciliation."

5. "Run FX revaluation for all USD and EUR open items as of March 31, 2026. Show the
   journal entries created and their impact on the P&L."

6. "Execute the full month-end close for March 2026: verify completeness, post adjustments,
   generate TB/P&L/BS, and set the lock date. Produce a close status report."

7. "Build a cash flow statement (indirect method) for Q1 2026 using MIS Builder. Show
   operating, investing, and financing activities."
