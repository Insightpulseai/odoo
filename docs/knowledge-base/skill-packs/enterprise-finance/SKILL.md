# Enterprise Finance Skill Pack

> Odoo 18 CE + OCA | SAP-equivalent: FI (Financial Accounting)

---

## Scope

General Ledger, Accounts Payable, Accounts Receivable, period close, multi-company
consolidation, bank reconciliation, and payment processing. Covers the full financial
backbone required for enterprise-grade accounting on Odoo 18 CE without Enterprise modules.

---

## Concepts

| Concept | SAP Equivalent | Odoo Surface |
|---------|---------------|--------------|
| General Ledger | FI-GL | `account.account`, `account.move` (type=entry) |
| Accounts Payable | FI-AP | `account.move` (type=in_invoice, in_refund) |
| Accounts Receivable | FI-AR | `account.move` (type=out_invoice, out_refund) |
| Journal | Document Type / Posting Key | `account.journal` |
| Fiscal Year / Period | FI Fiscal Year Variant | `account.fiscal.year` (OCA) |
| Chart of Accounts | CoA (SKA1/SKR04) | `account.chart.template` |
| Bank Statement | Electronic Bank Statement | `account.bank.statement` |
| Payment Order | Automatic Payment Program (F110) | OCA `account.payment.order` |
| Tax Code | Tax Condition / Tax Key | `account.tax` |
| Analytic Account | Cost Center (CO) | `account.analytic.account` |

---

## Must-Know Vocabulary

- **account.move**: The universal journal entry model. Invoices, bills, credit notes, and
  manual entries are all `account.move` records differentiated by `move_type`.
- **account.move.line**: Individual debit/credit line within a journal entry.
- **account.journal**: Groups entries by type (sale, purchase, bank, cash, general).
- **account.account**: GL account. Field `account_type` replaces the deprecated `user_type_id`.
- **account.reconcile.model**: Rules for automatic reconciliation of bank statement lines.
- **account.full.reconcile**: Marks a set of move lines as fully reconciled.
- **account.partial.reconcile**: Partial matching (e.g., partial payment against invoice).
- **Sequence**: Auto-numbering per journal. Field `sequence_override_regex` controls format.
- **Lock Date**: `fiscalyear_lock_date` (hard) and `period_lock_date` (advisors only).
- **Multi-company**: `company_id` on every financial record. `allowed_company_ids` in context.

---

## Core Workflows

### 1. Chart of Accounts Setup
1. Install localization module (e.g., `l10n_ph` for Philippines, `l10n_generic_coa` for generic).
2. Review `account.account` records. Map to enterprise CoA requirements.
3. Add missing accounts via `account.account` create. Use correct `account_type`.
4. Tag accounts with `account.account.tag` for reporting groups.

### 2. Vendor Bill (AP Cycle)
1. Create `account.move` with `move_type='in_invoice'`.
2. Add `account.move.line` entries: expense account (debit), AP account (credit auto).
3. Validate (post) the bill: `action_post()`.
4. Register payment: `account.payment` linked to the bill.
5. Reconciliation happens automatically on payment matching.

### 3. Customer Invoice (AR Cycle)
1. Create `account.move` with `move_type='out_invoice'`.
2. Lines: revenue account (credit), AR account (debit auto).
3. Post and send to customer.
4. Record payment or import bank statement for matching.

### 4. Bank Reconciliation
1. Import bank statement (OFX, CAMT.053, CSV) into `account.bank.statement`.
2. Statement lines (`account.bank.statement.line`) appear in reconciliation widget.
3. Match against open invoices/bills using `account.reconcile.model` rules.
4. Unmatched lines create journal entries on reconciliation.

### 5. Period Close
1. Set `period_lock_date` to prevent non-advisor edits on closed months.
2. Run OCA `account_financial_report` trial balance to verify balances.
3. Post adjusting entries (accruals, deferrals, FX revaluation).
4. Set `fiscalyear_lock_date` after year-end audit.
5. Generate closing entry to move P&L balances to retained earnings.

### 6. Multi-Company Consolidation
1. Each company has its own CoA, journals, and fiscal settings.
2. Inter-company transactions use `account.move` with partner = sibling company.
3. OCA `account_financial_report` generates per-company and consolidated reports.
4. Elimination entries are manual journal entries in the parent company.

---

## Edge Cases

- **Partial reconciliation**: A payment covers only part of an invoice. Odoo creates
  `account.partial.reconcile`. The remaining balance stays open on the invoice.
- **Multi-currency invoices**: Exchange rate differences generate automatic journal entries
  on the `currency_exchange_journal_id`.
- **Stale drafts**: Draft moves with sequence numbers consume sequence gaps. Use
  `sequence_override_regex` or periodically clean drafts.
- **Tax rounding**: `tax_calculation_rounding_method` (global vs per-line) causes cent
  differences. Set at company level and document the choice.
- **Negative invoices**: Odoo 18 handles credit notes separately (`out_refund`/`in_refund`).
  Do not use negative lines on invoices.
- **Lock date bypass**: Users in the Adviser group can still post before `period_lock_date`.
  Only `fiscalyear_lock_date` is absolute.

---

## Controls & Compliance

| Control | Implementation |
|---------|---------------|
| Segregation of duties | Odoo groups: Invoicing, Payments, Adviser. OCA `base_tier_validation` for approval chains. |
| Audit trail | `account.move` is immutable once posted. Reversals create new entries. |
| Lock dates | `period_lock_date` + `fiscalyear_lock_date` on `res.company`. |
| Tax compliance | `account.tax` with correct `tax_group_id`. BIR/VAT reports via localization. |
| Bank statement import | OFX/CAMT/CSV parsers validate format before import. |
| Payment approval | OCA `account_payment_order` with two-step (draft -> open -> generated -> uploaded). |
| Sequential numbering | Journal sequences enforced. No gaps allowed in posted entries (legal requirement in PH/EU). |

---

## Odoo/OCA Implementation Surfaces

### Core Odoo 18 CE Models
- `account.move` / `account.move.line` -- journal entries and lines
- `account.journal` -- sale, purchase, bank, cash, general
- `account.account` -- GL accounts with `account_type`
- `account.tax` / `account.tax.group` -- tax definitions
- `account.payment` -- payment registration
- `account.bank.statement` / `account.bank.statement.line` -- bank imports
- `account.reconcile.model` -- auto-reconciliation rules
- `account.fiscal.position` -- tax/account mapping per partner/country

### OCA Modules (18.0-compatible)
| Module | Repo | Purpose |
|--------|------|---------|
| `account_financial_report` | OCA/account-financial-reporting | Trial balance, general ledger, aged partner balance, journal ledger |
| `account_payment_order` | OCA/bank-payment | Batch payment files (SEPA, local formats) |
| `account_payment_mode` | OCA/bank-payment | Payment method configuration per partner |
| `account_fiscal_year` | OCA/account-financial-tools | Explicit fiscal year objects |
| `account_lock_date_update` | OCA/account-financial-tools | Wizard to update lock dates with audit log |
| `account_move_name_sequence` | OCA/account-financial-tools | Customizable move naming |
| `account_reconcile_oca` | OCA/account-reconcile | Enhanced reconciliation interface |
| `base_tier_validation` | OCA/server-ux | Approval tiers for invoices and payments |

---

## Azure/Platform Considerations

- **Backup**: PostgreSQL 16 `pg_dump` of `account_move`, `account_move_line` tables is
  critical. Schedule via Azure Container Apps cron job.
- **Performance**: `account_move_line` is the largest table in most Odoo DBs. Index on
  `(company_id, account_id, date)` and `(partner_id, reconciled)`.
- **Multi-company isolation**: Use `ir.rule` record rules. Validate with
  `SELECT company_id, COUNT(*) FROM account_move GROUP BY company_id`.
- **Reporting at scale**: OCA `account_financial_report` runs SQL queries. For large datasets,
  consider materialized views or Databricks extract via JDBC.
- **Secrets**: Bank API credentials (for statement import) go in `.env` or Azure Key Vault,
  never in `ir.config_parameter`.

---

## Exercises

### Exercise 1: Chart of Accounts Validation
Write a Python script using `xmlrpc` to list all `account.account` records, group by
`account_type`, and flag any account without a tag. Output as CSV.

### Exercise 2: Aged Receivable Report
Install `account_financial_report`. Generate an aged partner balance for AR as of today.
Verify totals match the `account.move.line` sum for receivable accounts.

### Exercise 3: Bank Reconciliation Automation
Create an `account.reconcile.model` rule that auto-matches bank lines where the
`payment_ref` contains an invoice number pattern (e.g., `INV/2026/`). Test with 10
sample statement lines.

### Exercise 4: Payment Order Workflow
Install `account_payment_order`. Create a payment mode for wire transfer. Select 5 open
vendor bills, generate a payment order, and advance it through draft -> open -> generated.
Verify the resulting `account.payment` records.

### Exercise 5: Period Close Checklist
Write a server action that: (1) checks all draft moves for a given month, (2) lists
unreconciled bank statement lines, (3) verifies trial balance debits = credits, and
(4) sets `period_lock_date` if all checks pass.

---

## Test Prompts for Agents

1. "Create a vendor bill for PHP 50,000 against GL account 600100 (Office Supplies) with
   12% VAT. Post it and register a partial payment of PHP 30,000."

2. "Import a bank statement CSV with 25 lines. Auto-reconcile what matches, then show me
   the unreconciled lines with suggested matches."

3. "Generate a trial balance for Q1 2026 using OCA account_financial_report. Export to XLSX."

4. "Set up a new company (Branch 2) with the same CoA as the parent. Create an inter-company
   invoice and show the resulting journal entries in both companies."

5. "Close the March 2026 period: verify no draft entries remain, confirm bank is fully
   reconciled, set lock date, and generate the period close report."

6. "List all posted journal entries where debit != credit at the move level. This should
   return zero results -- explain why if it does not."

7. "Configure a payment order mode for PESONET. Select all open AP invoices over 30 days
   and generate a batch payment file."
