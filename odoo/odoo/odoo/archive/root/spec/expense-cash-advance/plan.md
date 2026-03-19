# Expense Cash Advance — Implementation Plan

Version: 1.0.0 | Status: Draft | Last updated: 2026-03-03

## Architecture Overview

```
Employee (Browser)        Odoo (Python/OWL)           Bridge Services
──────────────────        ─────────────────           ───────────────
Submit advance            hr.expense.liquidation
Attach receipts    ────►  ipai_expense_ocr      ────► PaddleOCR service
View status               policy_check()
                          action_release()
                          action_liquidate()
                          action_post()         ────► account.move (journal entries)
                  ◄────   notifications
                          monitoring cron        ────► alerts/exception queue
```

## Phase -1: Gates (Prerequisites)

- Tool Contract v1 enforced (preview→approval→commit; audit envelope; idempotency)
- Knowledge/action eval harness in place for:
  - Read-only defaults
  - Approval compliance = 100%
  - Extraction payload schema correctness
- SSOT: `ssot/finance/expense_cash_advance.yaml` documents entities, states, accounting

## Phase 1: Cash Advance Core

**Goal**: Full request → approval → release → accounting entry lifecycle.

### 1.1 Extend State Machine
- Extend `ipai_hr_expense_liquidation` state machine from current (draft → submitted → approved → settled) to target (draft → submitted → manager_approved → finance_approved → released → in_liquidation → liquidated → closed)
- Add transition guards (manager group, finance group)
- Add `cancelled` and `rejected` states

### 1.2 Multi-Step Approval
- Manager approval step (guard: `hr.group_hr_manager` or `manager_id`)
- Finance approval step (guard: `account.group_account_manager`)
- Rejection with reason field (logged to chatter)

### 1.3 Release and Accounting
- On release: create `account.move` entry (debit: advance receivable, credit: cash/bank)
- Idempotency key: `cash_advance_release_{request_id}_{released_at}`
- Store journal entry reference on liquidation record

### 1.4 Notifications
- Email/chatter notification on each state transition
- Reminder notification for overdue liquidation (configurable days)

## Phase 2: Liquidation + Policy Checks

**Goal**: Expense capture, policy validation, accounting settlement.

### 2.1 Enhanced Expense Items
- Add fields: merchant, attendees, cost_center, extraction_confidence, policy_flags
- Link to OCR extraction result

### 2.2 Policy Engine
- Configurable rules: per-category limits, receipt required threshold, submission deadline
- Policy check runs on submit → populates policy_flags on each line
- Violations create `policy_violation` records

### 2.3 Settlement Accounting
- On liquidation post: debit expense accounts, credit advance receivable
- On return (expenses < advance): debit cash/bank, credit advance receivable
- On additional reimbursement (expenses > advance): debit expense, credit payable
- All entries use idempotency keys

### 2.4 Audit Queue
- Finance reviewers see queue of pending liquidations
- Priority sorting: amount, violations, overdue status
- Bulk approve/reject for low-risk items

## Phase 3: OCR Bridge

**Goal**: Receipt ingestion → proposed expense items → human correction loop.

### 3.1 Receipt Ingestion
- Extend `ipai_expense_ocr` for liquidation context
- Upload receipt → call PaddleOCR bridge → get extraction payload
- Store: original image + extraction JSON + confidence scores

### 3.2 Proposed Expense Items
- OCR extraction creates draft expense items (merchant, amount, date, category)
- Confidence < threshold → flag "needs review"
- Human corrects → saves final values

### 3.3 Evidence Packs
- Each receipt generates evidence pack:
  - `docs/evidence/<stamp>/receipt_ocr/logs/extraction.json`
  - Original receipt image stored as `ir.attachment`
  - Confidence report per field

## Phase 4: Monitoring + Dashboards

**Goal**: Concur-like controls and exception management.

### 4.1 Overdue Detection
- Cron job: find released advances past liquidation deadline
- Create alert records → push to exception queue
- Escalation: notify manager after N days, finance director after 2N days

### 4.2 Missing Receipt Detection
- Cron job: find expense items over threshold without receipt attachment
- Flag on liquidation record, block posting until resolved

### 4.3 Duplicate Detection
- Hash receipt images → check for duplicate hashes across liquidations
- Flag potential duplicates for manual review

### 4.4 Reporting
- KPI views: outstanding advances, overdue count, exceptions
- Spend breakdown by category/team/project
- Exportable reports for audit (Excel/PDF via Odoo reporting engine)

---

## OCA vs Bridge Decision Table

| Capability | OCA Available (19.0)? | Decision |
|------------|----------------------|----------|
| Cash advance request + approval | [NEEDS CLARIFICATION] | Use `ipai_hr_expense_liquidation` (existing) |
| Advance clearing/liquidation | [NEEDS CLARIFICATION] | Extend existing module |
| Receipt OCR | No | Bridge-first (`ipai_expense_ocr`) |
| Monitoring / alerts | No | Custom implementation |
| Policy violations | No | New model in existing module |

---

## Delivery Sequence

```
Commit 1: ssot(finance): cash advance domain model + spec bundle
  → ssot/finance/expense_cash_advance.yaml
  → spec/expense-cash-advance/{constitution,prd,plan,tasks}.md

Commit 2: feat(ipai): extend state machine + multi-step approval
  → addons/ipai/ipai_hr_expense_liquidation/models/

Commit 3: feat(ipai): accounting entries + idempotency
  → addons/ipai/ipai_hr_expense_liquidation/models/

Commit 4: feat(ipai): policy engine + violation tracking
  → addons/ipai/ipai_hr_expense_liquidation/

Commit 5: feat(ipai): monitoring cron + exception queue
  → addons/ipai/ipai_hr_expense_liquidation/data/

Commit 6: test(ipai): install smoke + upgrade smoke + accounting tests
  → tests/ + CI workflows
```
