# IPAI Azure Boards Portfolio Backlog

> **Source**: `docs/architecture/IPAI_PLATFORM_ANALYSIS.md` (R2, 2026-04-05)
> **Import file**: `docs/planning/IPAI_AZURE_BOARDS_IMPORT.csv`
> **Methodology**: Every hard blocker maps to a Feature. Every risk register entry maps to a Feature or PBI. Evidence gaps and implementation tasks are separated with `EVIDENCE:` / `IMPLEMENT:` prefixes.

---

## Epic 1: Governance & Drift Remediation

> IaC reconciliation, deprecated artifact cleanup, cost visibility.
> Maps to: R2 (IaC drift), R10 (FinOps), R13 (deprecated artifacts), N1, N2, N6.

### Feature 1.1: Reconcile IaC with Live Azure State (N1 / R2) -- HARD BLOCKER

> 20+ portal-deployed resources not tracked in Bicep. Primary governance risk.

- **PBI 1.1.1**: `EVIDENCE:` Inventory all 52 live Azure resources and map each to existing Bicep module or mark as untracked
- **PBI 1.1.2**: `IMPLEMENT:` Import portal-deployed alert rules (alert-http-5xx, alert-aca-restarts, alert-aca-no-replicas, alert-aca-high-cpu) into Bicep
- **PBI 1.1.3**: `IMPLEMENT:` Import WAF policy (wafipaidev) into Bicep Front Door module
- **PBI 1.1.4**: `IMPLEMENT:` Import HA environment (ipai-odoo-ha-env) + managed LB + public IP into Bicep
- **PBI 1.1.5**: `IMPLEMENT:` Import Grafana container app (ipai-grafana-dev) into Bicep
- **PBI 1.1.6**: `IMPLEMENT:` Import private DNS zone (privatelink.postgres.database.azure.com) into Bicep
- **PBI 1.1.7**: `EVIDENCE:` Run `az deployment group what-if` and confirm zero drift between Bicep and live state
- **PBI 1.1.8**: `IMPLEMENT:` Register justified exceptions for any resources intentionally outside IaC (e.g., NetworkWatcher)

### Feature 1.2: Enable Azure Cost Management (N2 / R10)

> No visibility into monthly Azure spend across 22 ACA apps + AI services.

- **PBI 1.2.1**: `IMPLEMENT:` Enable Azure Cost Management export to storage account
- **PBI 1.2.2**: `IMPLEMENT:` Create $500/month budget alert on subscription
- **PBI 1.2.3**: `IMPLEMENT:` Add cost export Bicep module to IaC
- **PBI 1.2.4**: `EVIDENCE:` Screenshot of cost dashboard showing 30-day trend

### Feature 1.3: Archive Deprecated Infrastructure Configs (N6 / R13)

> Repo contains DigitalOcean, Supabase, Mailgun cruft that confuses automation and agents.

- **PBI 1.3.1**: `IMPLEMENT:` Move `infra/deploy/DROPLET_DEPLOYMENT.md` and DigitalOcean configs to `archive/`
- **PBI 1.3.2**: `IMPLEMENT:` Move `infra/azure/supabase/` to `archive/`
- **PBI 1.3.3**: `IMPLEMENT:` Move Mailgun DNS references to `archive/`
- **PBI 1.3.4**: `EVIDENCE:` Verify `infra/` contains only active Azure configs after cleanup

---

## Epic 2: Production Readiness & Resilience

> Backup/restore, environment parity, SLOs, go-live gate consolidation.
> Maps to: R1 (single-env naming), R6 (no tested restore), R7 (5 go-live checklists), R12 (solo operator), N8, P1, P2, P3, P9.

### Feature 2.1: Set PostgreSQL Backup Retention in Bicep (N8 / R6)

> Backup policy planned but not in IaC. Untested backups are not backups.

- **PBI 2.1.1**: `IMPLEMENT:` Add `backupRetentionDays: 30` to PostgreSQL Flexible Server Bicep module
- **PBI 2.1.2**: `IMPLEMENT:` Deploy updated Bicep and confirm backup policy active
- **PBI 2.1.3**: `EVIDENCE:` Azure portal screenshot showing backup retention = 30 days

### Feature 2.2: Deploy Staging Environment (P1 / R1) -- HARD BLOCKER (for production)

> All workloads named `*-dev` with no deployed staging/prod distinction.

- **PBI 2.2.1**: `EVIDENCE:` Document target staging topology (ACA env, PG, networking)
- **PBI 2.2.2**: `IMPLEMENT:` Create staging Bicep parameter file (`parameters/staging.parameters.json`)
- **PBI 2.2.3**: `IMPLEMENT:` Deploy staging ACA environment using `ipai-odoo-ha-env` or new env
- **PBI 2.2.4**: `IMPLEMENT:` Deploy staging PostgreSQL instance or configure read replica
- **PBI 2.2.5**: `EVIDENCE:` Health check green on staging endpoints

### Feature 2.3: Test Backup Restore (P3 / R6) -- HARD BLOCKER

> Untested backups are not backups. RTO is unknown.

- **PBI 2.3.1**: `IMPLEMENT:` Restore PostgreSQL to disposable `test_restore_*` database
- **PBI 2.3.2**: `EVIDENCE:` Row count match between source and restored DB
- **PBI 2.3.3**: `EVIDENCE:` Document measured RTO (time from initiation to verified restore)

### Feature 2.4: Consolidate Go-Live Checklist (P2 / R7)

> 5 versions of go-live checklists create confusion at cutover.

- **PBI 2.4.1**: `EVIDENCE:` Inventory all go-live checklists in `docs/runbooks/` and `docs/delivery/`
- **PBI 2.4.2**: `IMPLEMENT:` Consolidate into single `docs/runbooks/GO_LIVE_GATE.md`
- **PBI 2.4.3**: `IMPLEMENT:` Archive superseded checklists

### Feature 2.5: Define Production SLOs (P9)

> No targets means no measurement. Cannot evaluate operational health.

- **PBI 2.5.1**: `IMPLEMENT:` Create SLO document: uptime 99.5%, p95 latency < 3s, error budget
- **PBI 2.5.2**: `IMPLEMENT:` Map SLOs to existing alert rules (5xx, restarts, no-replicas, high-cpu)
- **PBI 2.5.3**: `EVIDENCE:` SLO dashboard or workbook linked to Application Insights

### Feature 2.6: Solo Operator Mitigation (R12)

> Bus factor = 1. No peer review, no on-call rotation.

- **PBI 2.6.1**: `IMPLEMENT:` Document operational runbooks for top 5 failure scenarios
- **PBI 2.6.2**: `IMPLEMENT:` Establish escalation path (even if external/contracted)
- **PBI 2.6.3**: `EVIDENCE:` Runbook dry-run evidence for at least 1 scenario

---

## Epic 3: Security & Network Hardening

> Identity (Entra OIDC + MFA), private endpoints, NSGs, CodeQL, Key Vault hardening.
> Maps to: R3 (identity gap), R4 (network partially secured), R9 (no CodeQL), N3, N4, N7, P5, P8.

### Feature 3.1: Enable Entra Conditional Access + MFA (N4 / R3) -- HARD BLOCKER

> Admin access to Azure/Odoo has no MFA enforcement.

- **PBI 3.1.1**: `IMPLEMENT:` Create Conditional Access policy requiring MFA for all admin roles
- **PBI 3.1.2**: `IMPLEMENT:` Deploy CA policy via Entra portal or Terraform
- **PBI 3.1.3**: `EVIDENCE:` CA policy screenshot + sign-in log showing MFA challenge

### Feature 3.2: Activate Entra OIDC for Odoo (P5 / R3) -- HARD BLOCKER

> Odoo uses basic login; no SSO, no MFA for end users.

- **PBI 3.2.1**: `EVIDENCE:` Verify `ipai_auth_oidc` module exists or needs rebuild
- **PBI 3.2.2**: `IMPLEMENT:` Port/rebuild OIDC module for Odoo 18
- **PBI 3.2.3**: `IMPLEMENT:` Configure Entra app registration redirect URIs for Odoo
- **PBI 3.2.4**: `IMPLEMENT:` Deploy and test Odoo login via Entra redirect
- **PBI 3.2.5**: `EVIDENCE:` Screenshot of Odoo login via Entra + sign-in log

### Feature 3.3: Formalize NSG Rules in Bicep (N3 / R4)

> VNet deployed but NSG rules unknown/untracked.

- **PBI 3.3.1**: `EVIDENCE:` Export current NSG rules from Azure portal
- **PBI 3.3.2**: `IMPLEMENT:` Encode NSG rules in Bicep network module
- **PBI 3.3.3**: `IMPLEMENT:` Deploy and verify connectivity (ACA → PG, ACA → KV)
- **PBI 3.3.4**: `EVIDENCE:` `az deployment group what-if` shows zero NSG drift

### Feature 3.4: Deploy Private Endpoints for PG + KV (P8 / R4)

> Database and secrets accessible on public network paths.

- **PBI 3.4.1**: `IMPLEMENT:` Set Key Vault network to `Deny` default action in Bicep
- **PBI 3.4.2**: `IMPLEMENT:` Deploy private endpoint for Key Vault
- **PBI 3.4.3**: `EVIDENCE:` Confirm PG private endpoint active (DNS zone exists; validate connectivity)
- **PBI 3.4.4**: `EVIDENCE:` Confirm KV accessible only via private endpoint

### Feature 3.5: Enable CodeQL via GitHub Actions (N7 / R9)

> No static security analysis beyond linting.

- **PBI 3.5.1**: `IMPLEMENT:` Create `.github/workflows/codeql.yml` for Python and JavaScript
- **PBI 3.5.2**: `IMPLEMENT:` Run initial scan and triage findings
- **PBI 3.5.3**: `EVIDENCE:` CodeQL dashboard screenshot with first scan results

---

## Epic 4: Observability & Operations

> Alert routing verification, operational response ownership, runbooks.
> Maps to: R7 (checklist fragmentation), R12 (solo operator), N1 (alerts in IaC).

### Feature 4.1: Verify Production Alert Routing and Response Ownership -- HARD BLOCKER

> 4 alert rules deployed but routing and response ownership unverified.

- **PBI 4.1.1**: `EVIDENCE:` Confirm action group `ag-ipai-platform` has valid notification targets (email, SMS, or webhook)
- **PBI 4.1.2**: `EVIDENCE:` Trigger test alert and confirm notification received
- **PBI 4.1.3**: `IMPLEMENT:` Document alert → response ownership matrix
- **PBI 4.1.4**: `IMPLEMENT:` Add alert routing config to Bicep (if not already tracked)

### Feature 4.2: Operational Runbooks

> No documented incident response for common failure scenarios.

- **PBI 4.2.1**: `IMPLEMENT:` Runbook: ACA container restart loop
- **PBI 4.2.2**: `IMPLEMENT:` Runbook: PostgreSQL connection exhaustion
- **PBI 4.2.3**: `IMPLEMENT:` Runbook: Front Door routing failure
- **PBI 4.2.4**: `IMPLEMENT:` Runbook: Copilot/AI gateway degradation
- **PBI 4.2.5**: `IMPLEMENT:` Runbook: Certificate expiry / TLS failure

---

## Epic 5: AI Platform Readiness

> KB seeding, eval gate, prompt injection detection, API key migration.
> Maps to: R5 (AI eval gate), R11 (API key in DB), R14 (prompt injection), N5, P4, P6, P7.

### Feature 5.1: Seed Knowledge Base Index (N5 / R5)

> RAG copilot returns empty results without indexed data.

- **PBI 5.1.1**: `IMPLEMENT:` Run `ingest.sh --full` against Odoo 18 docs corpus
- **PBI 5.1.2**: `EVIDENCE:` Confirm 7,000+ chunks indexed in Azure AI Search
- **PBI 5.1.3**: `EVIDENCE:` Execute 3 test search queries and verify relevant results returned

### Feature 5.2: Integrate Eval Gate in CI/CD (P4 / R5)

> AI copilot releases bypass quality validation. Eval_Gate stage is a placeholder.

- **PBI 5.2.1**: `IMPLEMENT:` Create eval dataset with 20+ test cases covering all 11 copilot skills
- **PBI 5.2.2**: `IMPLEMENT:` Wire Eval_Gate stage in Azure DevOps pipeline to run eval dataset
- **PBI 5.2.3**: `IMPLEMENT:` Define pass/fail thresholds (e.g., >80% skill routing accuracy)
- **PBI 5.2.4**: `EVIDENCE:` Pipeline run showing Eval_Gate pass/fail on real data

### Feature 5.3: Migrate AI API Key to Key Vault (P6 / R11)

> API key stored in Odoo `ir.config_parameter` (DB) instead of Key Vault.

- **PBI 5.3.1**: `IMPLEMENT:` Create Key Vault secret `FOUNDRY_API_KEY`
- **PBI 5.3.2**: `IMPLEMENT:` Update `foundry_service.py` to read from env var instead of ICP
- **PBI 5.3.3**: `IMPLEMENT:` Wire ACA env var to Key Vault secret reference
- **PBI 5.3.4**: `EVIDENCE:` Copilot functional after migration (chat endpoint returns valid response)

### Feature 5.4: Add Prompt Injection Detection (P7 / R14)

> User input goes raw to LLM with no content filtering.

- **PBI 5.4.1**: `IMPLEMENT:` Add prompt injection detector in copilot controller pipeline
- **PBI 5.4.2**: `IMPLEMENT:` Create test cases for known injection patterns
- **PBI 5.4.3**: `EVIDENCE:` Test showing malicious prompts blocked before reaching LLM

---

## Epic 6: Platform Productization & Scale

> Multi-region, SaaS isolation, Defender, FinOps optimization, DORA metrics.
> Maps to: L1-L6 (Later tier). Not required for initial production.

### Feature 6.1: Multi-Region Deployment (L1)

- **PBI 6.1.1**: `EVIDENCE:` Document secondary region selection and failover strategy
- **PBI 6.1.2**: `IMPLEMENT:` Deploy secondary region ACA + PG replica
- **PBI 6.1.3**: `EVIDENCE:` Failover test with measured RTO/RPO

### Feature 6.2: Implement Tenant Isolation (L2)

- **PBI 6.2.1**: `EVIDENCE:` Finalize tenancy model from existing architecture docs
- **PBI 6.2.2**: `IMPLEMENT:` Tenant context middleware in Odoo
- **PBI 6.2.3**: `EVIDENCE:` Cross-tenant data leakage test (negative test)

### Feature 6.3: Enable Defender for Cloud (L3)

- **PBI 6.3.1**: `IMPLEMENT:` Enable Defender for Cloud on subscription
- **PBI 6.3.2**: `IMPLEMENT:` Integrate Defender alerts with action group
- **PBI 6.3.3**: `EVIDENCE:` Defender dashboard screenshot with initial posture score

### Feature 6.4: Azure Savings Plans / Reservations (L4)

- **PBI 6.4.1**: `EVIDENCE:` 3 months usage data from Cost Management
- **PBI 6.4.2**: `IMPLEMENT:` Purchase reservation or savings plan for steady-state compute
- **PBI 6.4.3**: `EVIDENCE:` Reservation coverage report showing 20-40% savings

### Feature 6.5: DORA Metrics Collection (L5)

- **PBI 6.5.1**: `IMPLEMENT:` Configure Azure DevOps analytics for deployment frequency, lead time, MTTR, change failure rate
- **PBI 6.5.2**: `EVIDENCE:` DORA dashboard with baseline metrics

### Feature 6.6: Internal Developer Platform (L6)

- **PBI 6.6.1**: `EVIDENCE:` Document service catalog and provisioning requirements
- **PBI 6.6.2**: `IMPLEMENT:` Build provisioning CLI or portal for new service onboarding

---

## Verification Checklist

- [x] Every hard blocker (5) maps to a Feature
- [x] Every risk register entry (R1-R14) maps to a Feature or PBI
- [x] Every roadmap item (N1-N8, P1-P9, L1-L6) maps to a Feature or PBI
- [x] Evidence gaps separated from implementation tasks with `EVIDENCE:` / `IMPLEMENT:` prefixes
- [x] Now-tier items in Epics 1-5; Later-tier items in Epic 6
- [x] Hard blockers marked explicitly

### Hard Blocker Traceability

| Hard Blocker | Feature |
|---|---|
| Reconcile live Azure resources into IaC | Feature 1.1 |
| Prove restore / recovery posture | Feature 2.3 |
| Confirm private connectivity and exposure boundaries | Feature 3.4 |
| Verify production alert routing and operational response | Feature 4.1 |
| Close identity gaps (Entra OIDC + MFA) | Features 3.1 + 3.2 |

---

*Generated: 2026-04-05 | Source: IPAI Platform Analysis R2*
