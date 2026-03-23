# Tasks — OdooSH Azure Equivalent

## Phase 0 — Spec and SSOT

- [x] Add OdooSH Azure parity matrix (`docs/operations/ODOOSH_AZURE_PARITY_MATRIX.md`)
- [x] Add constitution/prd/plan/tasks (`spec/odoo-sh-azure-equivalent/`)
- [x] Define environment naming contract (dev/staging/prod, DB names)
- [x] Define evidence schema (image digest, test results, approvals)

## Phase 1 — CI/CD Foundation

- [x] Deploy workflow: build → ACR → ACA → health check (`deploy-azure.yml`)
- [x] CI workflow for Odoo tests (`ci-odoo.yml`)
- [x] PR preview workflow (`pr-preview.yml`)
- [x] Module install workflow (`odoo-module-install.yml`)
- [x] Auto-upgrade workflow (`odoo-auto-upgrade.yml`)
- [ ] Add Key Vault variable groups to pipelines
- [ ] Add artifact/image promotion between stages
- [ ] Add deployment evidence emission to CI

## Phase 2 — Runtime

- [x] ACA app definitions: web, worker, cron
- [x] `ODOO_STAGE` env var on all containers
- [x] `az containerapp exec` for shell access
- [ ] Health endpoint probe configuration
- [ ] Auto-scaling rules for production web
- [ ] Resource limits per environment (dev=low, staging=medium, prod=full)

## Phase 3 — Data

- [x] PG Flexible Server deployed (`ipai-odoo-dev-pg`)
- [x] Backup retention increased to 35 days
- [x] Staging refresh script (`refresh_staging.sh`)
- [x] PII sanitization SQL (`sanitize_staging.sql`)
- [x] Production seed plan (`production_seed_plan.yaml`)
- [x] Seed validation script (`validate_seed_state.py`)
- [ ] Separate PG server per environment (target state)
- [ ] Read-only replica for BI/analytics access
- [ ] Backup/restore rehearsal (document and test)
- [ ] HA enablement for production PG

## Phase 4 — Non-Prod Safety

- [x] Mailpit compose config (`docker-compose.mailpit.yml`)
- [x] Mail server deactivation in sanitize script
- [x] Cron suppression in sanitize script
- [x] Password reset in sanitize script
- [x] Payment provider credential removal
- [x] Social integration token clearing
- [x] Calendar/drive sync token removal
- [x] IAP token clearing
- [x] `/robots.txt` disabled for staging
- [x] `ODOO_STAGE` env var set
- [ ] Deploy Mailpit as ACA sidecar in dev/staging
- [ ] Automated staging refresh on schedule (weekly cron)

## Phase 5 — Production Promotion and Rollback

- [x] Deploy workflow with environment targeting
- [ ] Environment protection rules (required reviewers for prod)
- [ ] Pre-deploy smoke test gate
- [ ] Post-deploy health check gate
- [ ] App rollback to known-good ACA revision
- [ ] DB restore runbook (PITR-based)
- [ ] Rollback evidence recording

## Phase 6 — Observability and Evidence

- [x] Azure Monitor connected to ACA
- [ ] App Insights integration for Odoo traces
- [ ] Log Analytics workspace for centralized logs
- [ ] Deployment history dashboard
- [ ] Alert rules (container restart, PG connection exhaustion, cron failure)
- [ ] Promotion evidence pack (automated capture)
- [ ] Browser-based log viewer (Power BI or Azure Workbooks)

## Progress Summary

| Phase | Status | Completion |
|-------|--------|-----------|
| Phase 0: Spec | **Complete** | 100% |
| Phase 1: CI/CD | **Mostly done** | 75% |
| Phase 2: Runtime | **Mostly done** | 70% |
| Phase 3: Data | **Mostly done** | 70% |
| Phase 4: Non-prod safety | **Mostly done** | 85% |
| Phase 5: Promotion/rollback | **Started** | 30% |
| Phase 6: Observability | **Started** | 20% |
| **Overall** | **In progress** | **65%** |
