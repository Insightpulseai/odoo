# AFC Parity — Task Backlog

**Version:** 1.0 | **Date:** 2026-03-15

## Phase 1: Dependency Engine

- [ ] **T-001** Add `close.task.dependency` model to `ipai_finance_ppm`
- [ ] **T-002** Implement circular dependency detection constraint
- [ ] **T-003** Implement dependency resolution engine (`_resolve_successor_states`)
- [ ] **T-004** Add "Completed with Errors" and "Blocked" task states
- [ ] **T-005** Add cron `_cron_resolve_dependencies` (15-minute interval)
- [ ] **T-006** Add retrigger capability (reset failed predecessor → re-evaluate chain)
- [ ] **T-007** Write unit tests for dependency resolution
- [ ] **T-008** Write integration test for 5-task chain with failure cascade
- [ ] **T-009** Add dependency visualization to task form view
- [ ] **T-010** Update `ipai_finance_ppm` manifest and security CSV

## Phase 2: Archival Policy

- [ ] **T-011** Scaffold `ipai_financial_close_archive` module
- [ ] **T-012** Add `close.archive.policy` model with default PH policies
- [ ] **T-013** Implement `_cron_archive_closed_runs` (daily cron)
- [ ] **T-014** Implement obsolete task auto-archive (1 month)
- [ ] **T-015** Implement `action_restore_archived_run` method
- [ ] **T-016** Add archive list view and search filters
- [ ] **T-017** Write tests for archive and restore workflows
- [ ] **T-018** Add archive policy settings to `res.config.settings`

## Phase 3: Notifications

- [ ] **T-019** Add `close.notification.scenario` model
- [ ] **T-020** Create mail templates for 7 notification scenarios
- [ ] **T-021** Implement `_cron_send_deadline_notifications` (daily 8am PHT)
- [ ] **T-022** Add 7-day and 3-day advance deadline warnings
- [ ] **T-023** Add overdue escalation via `mail.activity`
- [ ] **T-024** Add notification scenario configuration to settings UI
- [ ] **T-025** Write tests for notification triggering

## Phase 4: BIR Form Expansion

- [ ] **T-026** Implement BIR 2550M (Monthly VAT Declaration) in `ipai_bir_tax_compliance`
- [ ] **T-027** Implement BIR 2550Q (Quarterly VAT Return)
- [ ] **T-028** Implement BIR 0619-E (Monthly EWT Remittance)
- [ ] **T-029** Add DAT export format for each new form
- [ ] **T-030** Register new forms in compliance check catalog (CI-013, CI-014, CI-015)
- [ ] **T-031** Write tests: generate forms from test data, verify GL totals match

## Phase 5: P2 Gaps

- [ ] **T-032** G-09: Add webhook emission on task state change (for n8n)
- [ ] **T-033** G-05: Add substitute/delegation model and assignment UI
- [ ] **T-034** G-07: Build system health dashboard (KPI cards, overdue counts, SLA metrics)
- [ ] **T-035** G-06: Integrate ClamAV for malware scanning on `ir.attachment` create
- [ ] **T-036** G-08: Implement email anonymization cron (redact usernames after N months)

## Documentation

- [ ] **T-037** Update unified docs app with implementation status as gaps close
- [ ] **T-038** Add each new feature to the SAP AFC parity matrix
- [ ] **T-039** Create evidence bundles for each completed phase

## Status Key

- [ ] Not started
- [~] In progress
- [x] Complete
- [-] Blocked
- [!] Skipped with justification
