# Tasks — PPM Clarity for Odoo 18

## Phase 0 — Reset and Inventory

- [ ] Confirm Odoo CE 18 `project` baseline capabilities used as the execution foundation
- [ ] Confirm adopted OCA `project` modules from current workspace inventory
- [ ] Build capability map: current `ipai_finance_ppm` feature → CE / OCA / custom delta / delete
- [ ] Record known parity gaps that remain outside CE/OCA coverage

## Phase 1 — Architecture Correction

- [ ] Rewrite spec language to make CE/OCA the default baseline
- [ ] Reclassify `ipai_finance_ppm` as delta-only scope
- [ ] Remove any requirement that duplicates hierarchy/stakeholder/role/timeline/pivot/template features already available in CE/OCA
- [ ] Add explicit non-goals against monolithic custom PPM implementation

## Phase 2 — Implementation Decomposition

- [ ] Remove `project_task_integration.py` (deprecated Supabase webhook event emission)
- [ ] Remove `hr_expense.py` Pulser AI binding (unrelated to PPM)
- [ ] Remove `data/ir_cron_ppm_sync.xml` (deprecated webhook cron)
- [ ] Evaluate and clean `data/ir_config_parameter_powerbi.xml`
- [ ] Remove or rewrite `static/src/js/okr_dashboard_action.js`
- [ ] Keep `project_project.py` budget/cost-center fields (delta)
- [ ] Keep `analytic_account.py` budget sync (delta)
- [ ] Add `ppm.budget.line` model (budget/forecast/actual per period)
- [ ] Add `ppm.portfolio.health` model (RAG status per project)
- [ ] Add `ppm.risk` model (risk register)
- [ ] Add `ppm.issue` model (issue register)
- [ ] Add `ppm.scoring` model (investment scoring)
- [ ] Add `ppm.gate.review` model (phase-gate reviews)
- [ ] Update `__manifest__.py` — bump to v18.0.2.0.0, add OCA depends, remove deprecated data files
- [ ] Add form/tree/kanban views for delta models
- [ ] Add portfolio dashboard (pivot + graph on delta models)
- [ ] Update security CSV for new models

## Phase 3 — Proof and Validation

- [ ] Add proof matrix showing CE/OCA coverage vs custom delta coverage
- [ ] Add regression tests for retained delta models only
- [ ] Add installation/contract test for required CE/OCA project baseline
- [ ] Add documentation of known gaps (dependency/capacity limitations)

## Phase 4 — Release Gate

- [ ] Fail release if `ipai_finance_ppm` still owns a CE/OCA-covered capability without documented exception
- [ ] Fail release if parity claims omit known project-planning gaps
- [ ] Fail release if deprecated integration residue remains in PPM core
