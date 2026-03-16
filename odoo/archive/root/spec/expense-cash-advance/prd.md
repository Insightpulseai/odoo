# Expense Cash Advance — Product Requirements

Version: 1.0.0 | Status: Draft | Last updated: 2026-03-03

## Vision

Deliver a Concur-like Travel & Expense experience with cash advance lifecycle, liquidation, monitoring, and OCR — as a first-party Odoo 19 CE capability using OCA + IPAI bridges.

---

## Concur-like Cash Advance + Monitoring Outcomes

### P0 Outcomes (Ship-Blocking)

#### 1. Cash Advance Request → Approval → Release

- Employee submits cash advance request with purpose, dates, amount
- Manager approves (or rejects with reason)
- Finance approves and triggers release
- Release creates accounting entry (debit: employee advance receivable, credit: cash/bank)
- Acceptance: approvals are multi-step; finance release produces accounting entries; audit envelope present

#### 2. Liquidation

- Employee attaches receipts and compiles expense items
- Policy checks run (missing receipt, over limit, duplicate claim)
- Finance audits and posts journal entries
- Advance balance cleared: expenses offset advance, remainder returned or reimbursed
- Acceptance: liquidation clears advance balance correctly in all 3 scenarios (equal/over/under)

#### 3. Monitoring / Controls

- Dashboards and alerts for:
  - Overdue liquidations (advance released but not liquidated within policy period)
  - Missing receipts (expense items without attachments)
  - Policy violations (over limit, unapproved category, late submission)
  - Duplicate receipts/claims (hash-based detection)
  - Spend by category/team/project
- Acceptance: overdue detection rule triggers within 24h of policy deadline; exception queue populated

#### 4. Receipt OCR (Bridge-First)

- Receipt upload generates extraction payload (merchant, amount, date, category)
- Confidence score attached to each extracted field
- Proposed expense items created for human correction loop
- Evidence pack stored (original image + extraction JSON + confidence)
- Acceptance: OCR extraction creates proposed expense item; confidence < threshold routes to "needs review"

### P1 Outcomes (Next Sprint)

- Per-diem support (daily allowance by destination)
- Mileage claims (distance-based reimbursement)
- Corporate card reconciliation (match card transactions to expense items)
- Trip-based grouping and budgets

### Non-Goals

- No SAP Concur integration
- No Odoo Enterprise code reuse
- No voice input for expenses (P2 at earliest)
- No mobile-specific UI in this spec (see `spec/odoo-mobile/`)

---

## Existing Module Baseline

| Module | Status | Coverage |
|--------|--------|----------|
| `ipai_hr_expense_liquidation` | Active | Cash advance + liquidation + bucket totals (simplified states) |
| `ipai_expense_ocr` | Active | Receipt OCR ingestion into hr.expense |
| `OCA/hr-expense` | Submodule present, empty for 19.0 | [NEEDS CLARIFICATION] |

The SSOT domain model targets a more comprehensive state machine than what's currently implemented. See `ssot/finance/expense_cash_advance.yaml` for the full target vs. current state.

---

## Constraints

- CE only: no Enterprise module dependencies
- OCA first: use OCA modules when available for 19.0
- IPAI bridge: OCR and AI services route through bridge, not direct API calls
- Secrets: OCR credentials in env vars, never in Odoo DB or git
- Idempotency: all accounting entries use idempotency keys (no double-posting)
- Approval: multi-step (manager + finance) before disbursement
