# Expense Cash Advance — Task Breakdown

Version: 1.0.0 | Status: Draft | Last updated: 2026-03-03

## Phase -1: SSOT Gates

### T-GATE-CA-01: Create expense cash advance SSOT
- Create `ssot/finance/expense_cash_advance.yaml` with entities, status machines, accounting outcomes
- Acceptance: YAML parses, entities cover request/release/liquidation/item/violation

### T-GATE-CA-02: Create spec bundle
- Create `spec/expense-cash-advance/{constitution,prd,plan,tasks}.md`
- Acceptance: all 4 files exist, constitution has 10 non-negotiable rules

## Phase 1: Cash Advance Core

### T-CA-01: Extend state machine to target states
- Current: draft → submitted → approved → settled
- Target: draft → submitted → manager_approved → finance_approved → released → in_liquidation → liquidated → closed
- Add cancelled and rejected states
- Acceptance: all transitions work, guards enforce group membership

### T-CA-02: Implement multi-step approval
- Manager approval step with group guard
- Finance approval step with group guard
- Rejection with reason field logged to chatter
- Acceptance: manager cannot finance-approve; finance cannot skip manager step

### T-CA-03: Implement release accounting
- On release: create account.move (debit advance receivable, credit cash/bank)
- Idempotency key prevents double-posting
- Journal entry ID stored on liquidation record
- Acceptance: release creates exactly one journal entry; repeated release is no-op

### T-CA-04: Add notifications and reminders
- Chatter notification on each state transition
- Overdue reminder email (configurable days after release)
- Acceptance: state change creates mail.message; reminder fires on schedule

## Phase 2: Liquidation + Policy

### T-LIQ-01: Add policy engine
- Configurable rules: category limits, receipt threshold, submission deadline
- Policy check on submit populates policy_flags per line
- Acceptance: expense over limit gets flagged; missing receipt gets flagged

### T-LIQ-02: Create policy violation model
- Model: ipai.expense.policy.violation
- Fields: type, severity, evidence_refs, override_decision, approver, timestamp
- Acceptance: violation records created by policy check; override requires approver

### T-LIQ-03: Implement settlement accounting
- Liquidation post: debit expense accounts, credit advance receivable
- Return scenario: debit cash, credit advance receivable
- Reimburse scenario: debit expense, credit payable
- All with idempotency keys
- Acceptance: all 3 scenarios produce correct journal entries; no double-posting

### T-LIQ-04: Build audit queue view
- List view of pending liquidations for finance reviewers
- Priority sort: amount, violations, overdue
- Bulk approve for low-risk items
- Acceptance: queue shows pending items; bulk approve works for items without violations

## Phase 3: OCR Bridge

### T-OCR-01: Extend OCR for liquidation context
- ipai_expense_ocr receives receipt → returns extraction payload
- Store: original image + extraction JSON + confidence scores per field
- Acceptance: extraction payload includes merchant, amount, date, category with confidence

### T-OCR-02: Implement proposed expense items
- OCR extraction creates draft liquidation line items
- Confidence < threshold → flag "needs review"
- Human correction loop: edit → save final values
- Acceptance: low-confidence items marked for review; correction persists

### T-OCR-03: Evidence pack storage
- Each extraction generates evidence artifacts:
  - Extraction JSON log
  - Confidence report
  - Original receipt reference
- Acceptance: evidence pack created per receipt; JSON validates against schema

## Phase 4: Monitoring + Dashboards

### T-MON-01: Overdue liquidation detection
- Cron job: find released advances past liquidation deadline
- Create alert records in exception queue
- Escalation: manager notification, then finance director
- Acceptance: overdue advance triggers alert within 24h; escalation fires on schedule

### T-MON-02: Missing receipt detection
- Cron job: find expense items over threshold without receipt
- Flag on liquidation, block posting until resolved
- Acceptance: missing receipt blocks posting; adding receipt unblocks

### T-MON-03: Duplicate receipt detection
- Hash receipt images on upload
- Check for duplicate hashes across all liquidations
- Flag potential duplicates for manual review
- Acceptance: same receipt uploaded twice gets flagged; different receipts pass

### T-MON-04: Reporting and KPIs
- Dashboard: outstanding advances, overdue count, exceptions
- Spend breakdown by category/team/project
- Exportable reports (Excel/PDF)
- Acceptance: dashboard loads without error; export produces valid file

## CI / Testing Gates

### T-CI-01: Install smoke (fresh DB)
- Create fresh DB, install cash advance module set
- Acceptance: zero errors, all XML loads, security rules load

### T-CI-02: Upgrade smoke (seeded DB)
- Take seeded DB snapshot, upgrade module set
- Acceptance: zero migration errors, no broken views

### T-CI-03: State transition tests
- Test all state transitions (happy path + rejection + cancellation)
- Test guard enforcement (wrong group → denied)
- Acceptance: all transitions tested, unauthorized transitions raise AccessError

### T-CI-04: Accounting idempotency tests
- Release → verify journal entry → release again → verify no duplicate
- Liquidation post → verify entries → post again → verify no duplicate
- Acceptance: idempotency key prevents all double-posting scenarios

### T-CI-05: Policy rule tests
- Expense over limit → flagged
- Missing receipt → flagged
- Override by approver → logged
- Acceptance: all policy rules tested with positive and negative cases

### T-CI-06: Overdue detection tests
- Create released advance past deadline → run cron → verify alert created
- Acceptance: cron creates alert; resolved advance not re-alerted

## Evidence Pack Outputs

Evidence artifacts for each capability:

| Capability | Evidence Path |
|------------|---------------|
| Cash advance release | `docs/evidence/<stamp>/cash_advance_release/logs/` |
| Liquidation posting | `docs/evidence/<stamp>/liquidation_posting/logs/` |
| Receipt OCR | `docs/evidence/<stamp>/receipt_ocr/logs/` |
| Monitoring alerts | `docs/evidence/<stamp>/expense_monitoring/logs/` |

---

## Task Status Matrix

| Task | Phase | Status | Blocker |
|------|-------|--------|---------|
| T-GATE-CA-01 | -1 | completed | none |
| T-GATE-CA-02 | -1 | completed | none |
| T-CA-01 | 1 | pending | T-GATE-CA-01 |
| T-CA-02 | 1 | pending | T-CA-01 |
| T-CA-03 | 1 | pending | T-CA-01 |
| T-CA-04 | 1 | pending | T-CA-01 |
| T-LIQ-01 | 2 | pending | T-CA-03 |
| T-LIQ-02 | 2 | pending | T-LIQ-01 |
| T-LIQ-03 | 2 | pending | T-CA-03 |
| T-LIQ-04 | 2 | pending | T-LIQ-01 |
| T-OCR-01 | 3 | pending | none |
| T-OCR-02 | 3 | pending | T-OCR-01 |
| T-OCR-03 | 3 | pending | T-OCR-01 |
| T-MON-01 | 4 | pending | T-CA-03 |
| T-MON-02 | 4 | pending | T-LIQ-01 |
| T-MON-03 | 4 | pending | T-OCR-01 |
| T-MON-04 | 4 | pending | T-MON-01 |
| T-CI-01 | CI | pending | T-CA-01 |
| T-CI-02 | CI | pending | T-CA-01 |
| T-CI-03 | CI | pending | T-CA-01 |
| T-CI-04 | CI | pending | T-CA-03 |
| T-CI-05 | CI | pending | T-LIQ-01 |
| T-CI-06 | CI | pending | T-MON-01 |
