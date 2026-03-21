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
- [ ] Browser-based log viewer (Superset or Azure Workbooks)

## Phase 0G -- Reference Source Curation

- [ ] Classify normative vs exemplar sources in platform docs
- [ ] Mark foundry-rs/* as excluded from core platform baseline
- [ ] Add Microsoft Foundry exemplar inventory to docs
- [ ] Add baseline/starter hardening note for AI bootstrap templates
- [ ] Remove Viva Goals references from any forward-looking tool examples

## Phase 1G -- Interface Standardization

- [ ] Document the standard interface for development-environment setup
- [ ] Document the standard interface for application diagnosis
- [ ] Identify remaining custom/team-local request paths
- [ ] Select the first workflows to move from standard tooling to self-service

## Phase 1H -- Paved Provisioning

- [ ] Define canonical IaC templates for core environment/resource types
- [ ] Define structured request workflows and approval rules
- [ ] Define centralized allocation and utilization dashboards
- [ ] Eliminate manual one-off provisioning for core workflows

## Phase 1I -- AI Extension Patterns

- [ ] Evaluate mcp-foundry for provider/orchestrator fit
- [ ] Evaluate foundry-agent-webapp for auth/webapp integration patterns
- [ ] Evaluate Foundry Local for local-dev/offline agent workflows
- [ ] Evaluate Azure AI Foundry baseline for production guardrails

## Phase 2F -- Automated Self-Service

- [ ] Automate core provisioning through CI/CD-integrated workflows
- [ ] Expose controlled self-service for authorized users
- [ ] Define dedicated-vs-shared environment creation rules
- [ ] Embed governance/compliance checks in provisioning workflows

## Phase 3A -- Integrated Experience

- [ ] Identify where platform capabilities should surface directly in CLI/IDE/current engineering flows
- [ ] Define minimum diagnostic affordances available on demand from the platform
- [ ] Prioritize integrated-services improvements only after the standard/self-service paths show adoption

## Progress Summary

| Phase | Status | Completion |
|-------|--------|-----------|
| Phase 0: Spec | **Complete** | 100% |
| Phase 0G: Source curation | **Not started** | 0% |
| Phase 1: CI/CD | **Mostly done** | 75% |
| Phase 1G: Interface standardization | **Not started** | 0% |
| Phase 1H: Paved provisioning | **Not started** | 0% |
| Phase 1I: AI extension patterns | **Not started** | 0% |
| Phase 2: Runtime | **Mostly done** | 70% |
| Phase 2F: Automated self-service | **Not started** | 0% |
| Phase 3: Data | **Mostly done** | 70% |
| Phase 3A: Integrated experience | **Not started** | 0% |
| Phase 4: Non-prod safety | **Mostly done** | 85% |
| Phase 5: Promotion/rollback | **Started** | 30% |
| Phase 6: Observability | **Started** | 20% |
| **Overall** | **In progress** | **55%** |
