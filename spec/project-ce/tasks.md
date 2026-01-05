# Tasks — Checklist

## Scaffold

- [x] Create module structure under `addons/ipai/ipai_project_suite`
- [x] Add manifest + init
- [x] Add settings toggles (config_parameter-backed)
- [x] Add security groups + ACLs
- [x] Add base views (settings block)

## Models

- [x] Milestone model + links to project/task
- [x] Dependency model + links to task + circular detection
- [x] Budget + budget lines + computed totals
- [x] RACI model + assignment links + single accountable constraint
- [x] Stage gate model + check mechanics
- [x] Template model + apply-to-project action

## Views

- [x] Project form: Milestones smart button
- [x] Project form: Budgets smart button
- [x] Project form: RACI tab (toggle-gated)
- [x] Task form: Dependencies tab (toggle-gated)
- [x] Task form: Milestone field (toggle-gated)
- [x] Task form: RACI tab (toggle-gated)
- [x] Milestone list/form/kanban views
- [x] Dependency list/form views
- [x] Budget list/form views
- [x] Menu items for configuration

## Import System

- [x] Generator script for Month-end workbook
- [x] JSON-RPC importer script
- [x] Import templates (CSV)
- [x] Import README documentation
- [x] GitHub Actions workflow for CI

## Automation / Verification

- [ ] Install/upgrade scripts
- [ ] Smoke test script
- [ ] GitHub Action: install/upgrade gate

## Documentation

- [x] Spec kit bundle (constitution, prd, plan, tasks)
- [x] Import README
- [ ] Module README

## Future Enhancements

- [ ] Reporting SQL views
- [ ] Gantt-style timeline view (CE-safe)
- [ ] Agile/Scrum board extension
- [ ] Timesheet integration
- [ ] Analytic account integration for budget actuals
