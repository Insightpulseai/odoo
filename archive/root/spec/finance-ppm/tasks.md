# Finance PPM — Tasks

> **Spec**: `spec/finance-ppm/`
> **Status**: Active
> **Last updated**: 2026-02-24

---

## Phase 0: Seed Data & Team Setup

- [ ] **T-01** Validate team directory CSV via `scripts/finance/validate_team_directory.py`
- [ ] **T-02** Import team directory into Odoo users via `scripts/finance/import_team_directory.py`
- [ ] **T-03** Create 6 shared Kanban stages (To Do, In Preparation, Under Review, Pending Approval, Done, Cancelled)
- [ ] **T-04** Import 33 tags from `data/seed/finance_ppm/tbwa_smp/tags.csv`

## Phase 1: Project Structure

- [ ] **T-05** Import IM1 Month-End Close tasks (39 tasks) from `tasks_month_end.csv`
- [ ] **T-06** Import IM2 BIR Tax Filing tasks (50 tasks) from `tasks_bir_tax.csv`
- [ ] **T-07** Import 11 logframe milestones from `logframe.csv`

## Phase 2: OCA Module Installation

- [ ] **T-08** Install `project_task_dependency` (task predecessors/successors)
- [ ] **T-09** Install `project_timeline` (timeline bar view)
- [ ] **T-10** Install `project_stage_closed` (Done/Cancelled distinction)

## Phase 3: ipai Delta Modules

- [ ] **T-11** Install `ipai_enterprise_bridge` (safe EE stubs)
- [ ] **T-12** Install `ipai_finance_workflow` (role-based stage transitions)
- [ ] **T-13** Install `ipai_finance_ppm` (budget/forecast/variance + event emitter)
- [ ] **T-14** Install `ipai_bir_notifications` (filing deadline alerts)
- [ ] **T-15** Install `ipai_bir_tax_compliance` (36 eBIRForms support)

## Phase 4: Platform Bridges

- [ ] **T-16** Apply Supabase email notification queue migrations (4 migration files)
- [ ] **T-17** Deploy `email-dispatcher` Edge Function
- [ ] **T-18** Deploy updated `tick` Edge Function (wakes email-dispatcher)
- [ ] **T-19** Set required Supabase secrets (BRIDGE_SHARED_SECRET, ZOHO_FROM_EMAIL)
- [ ] **T-20** Run email pipeline smoke test (insert test event, verify enqueue + dispatch)
- [ ] **T-21** Configure n8n recurrent alerts (9AM + 5PM PHT cron)
- [ ] **T-22** Set up BIR form generation bridge

## Phase 5: Validation

- [ ] **T-23** Run `validate_team_directory.py` — exits 0
- [ ] **T-24** Run `validate_seed_ssot.py` — exits 0
- [ ] **T-25** Run `validate_parity_map.py` — exits 0
- [ ] **T-26** Run `test_finance_ppm_odoo18.sh` — exits 0
- [ ] **T-27** Verify logframe KPI baselines (on-time filing, avg delay, TB reconciliation, BIR overdue)
