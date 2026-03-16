# AFC Parity — Implementation Plan

**Version:** 1.0 | **Date:** 2026-03-15

## Architecture

No new modules. All changes extend existing `ipai_finance_ppm` and `ipai_bir_tax_compliance` modules, plus one new `ipai_financial_close_archive` module.

## Phase 1: Dependency Engine (Weeks 1-4)

**Target gap:** G-01 (Successor invalidation cascade)

### Deliverables

1. Add `close.task.dependency` model to `ipai_finance_ppm`
   - Fields: `task_id`, `predecessor_id`, `dependency_type` (process/time/approval)
   - Constraint: no circular dependencies

2. Add dependency resolution engine
   - On task status change → evaluate all successor tasks
   - If predecessor fails → invalidate successors (set to "blocked")
   - If predecessor completes → unlock successors (set to "ready")
   - Cron: `_cron_resolve_dependencies` runs every 15 minutes

3. Add "Completed with Errors" task state
   - New state in task selection: triggers successor invalidation
   - Retrigger capability: reset failed predecessor → re-evaluate chain

4. Tests: dependency chain resolution, circular detection, invalidation cascade

### Verification

- Unit tests for dependency resolution
- Integration test: 5-task chain with failure at step 3 → verify steps 4-5 blocked

## Phase 2: Archival Policy (Weeks 5-8)

**Target gap:** G-02 (Automatic archiving)

### Deliverables

1. New module: `ipai_financial_close_archive`
   - `close.archive.policy` model: `closing_type` (monthly/quarterly/annual), `archive_after_months`, `is_production`
   - Default policies: monthly=6mo, quarterly=12mo, annual=18mo

2. Cron: `_cron_archive_closed_runs` (daily)
   - Find `close.run` records where `state=closed` and `close_date + archive_months < today`
   - Set `archived=True`, move to archive view
   - Obsolete tasks archived after 1 month regardless

3. Restore capability: `action_restore_archived_run` method
   - Restored runs auto-archive again after default period

4. Archive list view and search filters

### Verification

- Test: create a run, close it, advance date, verify auto-archive
- Test: restore archived run, verify re-archive timer resets

## Phase 3: Notifications (Weeks 9-12)

**Target gap:** G-03 (Granular notification scenarios)

### Deliverables

1. `close.notification.scenario` model
   - Scenarios: task_assigned, task_completed, task_overdue, deadline_approaching, approval_requested, approval_granted, approval_rejected
   - Config: enabled/disabled per scenario, recipient (assignee/reviewer/manager), days_before (for deadline)

2. Mail templates for each scenario

3. Cron: `_cron_send_deadline_notifications` (daily at 8am PHT)
   - 7-day and 3-day advance warnings
   - Overdue escalation

### Verification

- Test: configure scenario, trigger event, verify email queued

## Phase 4: BIR Form Expansion (Weeks 13-16)

**Target gap:** G-04 (BIR 2550M/Q + 0619-E)

### Deliverables

1. Add 2550M (Monthly VAT Declaration) to `ipai_bir_tax_compliance`
   - Tax line aggregation from `account.tax` for output/input VAT
   - DAT export format per BIR spec

2. Add 2550Q (Quarterly VAT Return)
   - Quarterly aggregation with input VAT credit carryover

3. Add 0619-E (Monthly EWT Remittance)
   - EWT line aggregation by ATC code
   - Summary and detail export

4. Add forms to compliance check CI catalog

### Verification

- Test: generate each form from test data, verify totals match GL

## Phase 5: P2 Gaps (Weeks 17-28)

Sequenced as:
1. G-09: Task-status webhooks to n8n (week 17-18)
2. G-05: Substitute/delegation workflow (week 19-20)
3. G-07: System health dashboard (week 21-24)
4. G-06: Malware scanning (week 25-26)
5. G-08: Email anonymization (week 27-28)

## First engineering target

**Successor invalidation cascade (G-01)** — this is the highest-value gap and the foundation for all subsequent close orchestration improvements.
