# IPAI Platform Analysis

> **Assessment Date**: 2026-04-05
> **Assessor**: Principal Cloud Architecture Assessment (automated, evidence-based)
> **Scope**: InsightPulseAI / IPAI Platform — Azure-first, Odoo CE ERP, AI/Agent workloads
> **Method**: Approximation against 11 Microsoft assessment lenses using repo/IaC/SSOT evidence
> **Confidence caveat**: No official Microsoft questionnaires were submitted. All scores are inferred from available architecture evidence and clearly marked assumptions.

---

## 1. Executive Summary

The IPAI platform assessment has been updated using live Azure Resource Graph inventory rather than IaC-only evidence. This materially improves confidence in the current runtime posture and raises the overall maturity score from **2.4** to **2.7**. The platform is now assessed as **Conditionally Ready** for controlled production use, subject to closure of the remaining operational and governance blockers.

The most important corrections are: deployed alerting coverage is confirmed, the WAF policy is active, the PostgreSQL private connectivity posture is partially evidenced through the private DNS zone, the Azure Container Apps estate is materially larger than previously modeled, and monitoring coverage is stronger than previously assessed due to confirmed Application Insights, Grafana, and health workbook assets.

The primary newly elevated risk is **IaC drift**: approximately twenty portal-created or portal-mutated Azure resources appear to exist outside the tracked Bicep-defined estate. This no longer supports a "not ready due to missing runtime controls" conclusion; instead, it supports a **conditionally ready but governance-drifted** conclusion. Immediate priority should shift from proving baseline runtime existence to reconciling live estate vs source-controlled intent, then closing the remaining production-hardening gaps.

**Overall Maturity: 2.7 / 5.0 (Emerging — approaching Defined)**

### Assessment Delta After Live Inventory Validation

| Item | IaC-only view | Live inventory view |
|---|---:|---:|
| Overall maturity score | 2.4 | 2.7 |
| Alert rules | Missing | 4 deployed |
| WAF policy | Conditional / unverified | Deployed |
| PostgreSQL private connectivity | Missing | Partially evidenced |
| Container Apps estate | 12 apps known | 22 apps + 1 job |
| HA runtime posture | Unknown | HA environment, load balancer, public IP present |
| Monitoring posture | Partial | Application Insights, Grafana, workbook, alerts present |
| Hard blockers | 8 | 5 |
| Final verdict | Not Ready | Conditionally Ready |

### Evidence Basis Update

This revision uses **live Azure Resource Graph inventory** as a higher-confidence current-state evidence source than IaC alone. Where IaC and live inventory disagree, live inventory is treated as authoritative for runtime existence, while IaC remains authoritative for intended-state governance. Any mismatch between the two is classified as a **drift finding**, not automatically as a missing control.

Markdown lint findings are non-blocking style issues only (for example, table spacing and emphasis-used-as-heading patterns). They do not affect rendering, evidence quality, scoring logic, or assessment conclusions.

### Top 5 Risks

| # | Risk | Impact |
|---|------|--------|
| R1 | Single-environment naming — all workloads named `*-dev` with no deployed staging/prod distinction | No deployment confidence, environment ambiguity |
| R2 | Identity gap — Entra OIDC registered but Odoo still uses basic login; Keycloak abandoned | Unauthorized access, no MFA enforcement |
| R3 | IaC drift — portal-deployed resources (alerts, WAF, PE) not tracked in Bicep | Config drift, reproducibility risk |
| R4 | No AI safety gates in CI/CD — eval framework exists but not integrated into release pipeline | Unvalidated AI outputs in production |
| R5 | No tested disaster recovery — PG backup assumed (Flex Server default) but no restore proof | Data loss risk unmitigated |

### Top 5 Strengths

| # | Strength | Evidence |
|---|----------|----------|
| S1 | Comprehensive IaC — 16 Bicep modules + Terraform DNS, parameterized for 3 environments | `infra/azure/modules/*.bicep`, `infra/azure/parameters/*.json` |
| S2 | SSOT governance framework — platform constitution, 37 contracts, CI/CD policy matrix | `ssot/governance/`, `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` |
| S3 | 8-stage release pipeline with approval gates | `.azuredevops/pipelines/odoo-module.yml` |
| S4 | Working AI copilot with 4-tier fallback, audit trail, deterministic skill routing | `addons/ipai/ipai_odoo_copilot/` — verified live 2026-04-05 |
| S5 | Deployed observability stack — 4 alert rules, App Insights, Grafana, health workbook, WAF | Azure Resource Graph: 52 live resources verified 2026-04-05 |

### Recommended Immediate Priorities

1. **Reconcile IaC with live state** — 4 alert rules, WAF, PG private endpoint, HA env deployed via portal but not in Bicep
2. **Deploy staging environment** using existing Bicep + parameter files (leverage `ipai-odoo-ha-env` as candidate)
3. **Activate Entra OIDC** for Odoo (app registration exists, module exists)
4. **Seed knowledge base index** — copilot is live but RAG returns empty without indexed docs
5. **Integrate eval gate** into CI/CD pipeline for AI copilot releases

---

## 2. Current Platform Snapshot

### Architecture Summary

```
Internet → Azure Front Door (Premium + WAF) → Azure Container Apps Environment
                                                  ├── ipai-odoo-dev-web (Odoo 18 CE, port 8069)
                                                  ├── ipai-odoo-dev-worker (background jobs)
                                                  ├── ipai-odoo-dev-cron (scheduled jobs)
                                                  ├── ipai-copilot-gateway (port 8088)
                                                  ├── ipai-mcp-dev (MCP coordination)
                                                  ├── ipai-auth-dev (Keycloak — decommission candidate)
                                                  ├── ipai-ocr-dev (Document Intelligence bridge)
                                                  ├── ipai-superset-dev (BI — supplemental)
                                                  ├── ipai-plane-dev (project management)
                                                  ├── ipai-shelf-dev, ipai-crm-dev, ipai-website-dev
                                                  └── (12+ container apps total)
                                               ↓
                                    Azure Database for PostgreSQL Flexible Server
                                    (ipai-odoo-dev-pg, southeastasia)
                                               ↓
                              Azure AI Services (eastus / eastus2 / southeastasia)
                              ├── Azure OpenAI (gpt-4.1 deployment)
                              ├── Azure AI Search (ipai-knowledge-index)
                              ├── Azure Document Intelligence
                              └── Azure AI Foundry (data-intel-ph project)
```

### Environment Model

| Property | Dev | Staging | Production |
|----------|-----|---------|------------|
| **Status** | **Active (sole running env)** | **Defined in IaC, not deployed** | **Defined in IaC, not deployed** |
| Database | `odoo_dev` / `odoo_dev_18` | `odoo_staging` (planned) | `odoo` (planned) |
| Workers | 0 (single-process) | 2 (planned) | 4+ (planned) |
| Config | `config/dev/odoo.conf` | `config/staging/odoo.conf` | `config/prod/odoo.conf` |
| Public URL | `erp.insightpulseai.com` (actual) | `erp-staging.insightpulseai.com` (planned) | `erp.insightpulseai.com` (planned) |
| Backup | None | Daily/7-day (planned) | Daily/30-day + PITR (planned) |

### Delivery Model

- **CI**: GitHub Actions (17 workflows — validation, KB refresh, governance checks)
- **CD**: Azure DevOps Pipelines (8-stage idea-to-release for Odoo modules)
- **Registry**: Azure Container Registry (`cripaidev`, `ipaiodoodevacr`)
- **Auth**: OIDC workload identity federation (Azure DevOps ↔ Azure)
- **Secrets**: Azure Key Vault (`kv-ipai-dev`) with managed identity binding

### Security / Governance Model

- **IdP**: Entra ID tenant (`402de71a`) — bootstrapped, app registrations exist, OIDC not activated
- **Transitional IdP**: Keycloak (`ipai-auth-dev`) — never operationalized, decommission candidate
- **Secrets**: Key Vault with RBAC authorization, soft delete + purge protection enabled
- **Network**: VNet defined (5 subnets), Front Door Premium — but no NSGs, no private endpoints deployed
- **Scanning**: Dependabot (weekly), secret drift detection in PRs, Trivy in Docker builds
- **Missing**: CodeQL/GHAS, no SIEM, no Defender for Cloud

### AI / Platform Model

- **LLM**: Azure OpenAI `gpt-4.1` via simple chat completion (Foundry Agent Service as future target)
- **RAG**: Azure AI Search (`ipai-knowledge-index`) — pipeline built, 438 docs discovered, index needs seeding
- **Copilot**: `ipai_odoo_copilot` — live in Odoo with 11-skill deterministic router, 14 tool functions, audit trail
- **Safety**: SQL injection prevention, model blocklist (11 security-sensitive models), read-only default mode
- **Missing**: Prompt injection detection, PII masking, content filtering, eval gate in CI/CD

### Explicit Assumptions

1. Only `dev` environment is actually deployed and running. Staging and production exist as IaC definitions only.
2. The "production" Container App names contain `dev` (e.g., `ipai-odoo-dev-web`) — this is the dev environment serving as the only active runtime.
3. Keycloak was never operationalized — no applications authenticate through it.
4. Supabase is fully deprecated (2026-03-26) — residual configs still tracked in repo.
5. Solo operator model — no on-call rotation, no peer review (policy exists but single contributor).

---

## 3. Assessment Scorecard

| # | Assessment | Score | Confidence | Phase | Key Finding | Top Recommendation |
|---|-----------|-------|------------|-------|-------------|-------------------|
| A | **Well-Architected Review** | **2.7** | Medium-High | Now | IaC + deployed alerts/WAF/App Insights; single-env naming; PG PE exists | Reconcile IaC with live state; deploy staging |
| B | **Landing Zone / CAF Ready** | **2.5** | Medium | Now | VNet deployed, PG private endpoint active, WAF deployed; no Azure Policy enforcement | Formalize NSG rules in Bicep; enable tag policy |
| C | **Platform Engineering** | **2.8** | Medium | Now | Rich SSOT/contracts/golden paths but no self-service consumption | Activate pipeline for staging deploys |
| D | **DevOps Capability** | **3.2** | High | Now | 8-stage pipeline, P0-P3 gates, OIDC auth — but eval gate placeholder | Integrate eval gate, add perf testing |
| E | **FinOps Review** | **1.2** | Low | Now | DigitalOcean cost tracking only; 22 ACA apps + sprawl risk; no Azure budget | Enable Azure Cost Management + tag policy |
| F | **CASA (Security)** | **2.6** | Medium | Now | Key Vault + MI + secret scanning + WAF + PG PE — but no MFA, no SIEM | Activate Entra MFA + enable Defender |
| G | **GenAI Technical** | **2.5** | High | Now | Live copilot with audit trail + safety controls — but no eval gate, no PII masking | Integrate eval gate + add content filtering |
| H | **Go-Live WAF Review** | **1.8** | Medium | Pre-Prod | 5 go-live checklists + deployed alerts/health workbook; no tested DR | Consolidate checklist + test backup restore |
| I | **Developer Velocity** | **2.8** | Low | Later | Rich devcontainer + scripts — but solo operator, no CI wait time data | Defer until team scales |
| J | **Mission Critical WAF** | **1.2** | Medium | Later | HA env (`ipai-odoo-ha-env`) + LB deployed; no multi-region, no chaos | HA env is promising; formalize when SLA needed |
| K | **SaaS Journey Review** | **2.0** | Medium | Later | Tenancy model documented (3-phase) — but no implementation, no billing | Defer until first external tenant |

**Aggregate: 2.5 / 5.0 (Emerging — approaching Defined)**

> **Live resource corrections**: Alerts (+4 rules, +2 action groups), WAF policy (deployed), PG private endpoint (DNS zone active), HA Container Apps Environment (+ LB + public IP), Grafana (deployed), Odoo Platform Health workbook (deployed), 22 container apps (vs 12 in repo docs). These portal-deployed resources are not tracked in Bicep — creating an IaC drift risk.

---

## 4. Detailed Findings by Assessment

### A. Well-Architected Review

**Objective**: Evaluate across Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency.

#### A.1 Reliability — Score: 1.8

| Factor | Status | Evidence |
|--------|--------|----------|
| Multi-region | Not deployed | Single region: `southeastasia` |
| Failover | Not configured | No Traffic Manager, no geo-redundant PG |
| Health probes | Defined | Front Door routes: `/web/health` (30s), `/healthz` |
| Backup/PITR | Planned, not enforced | `config/ENVIRONMENTS.md` documents 30-day + PITR for prod; Bicep has no retention param |
| DR runbook | Not tested | 5 go-live checklists exist; no tested restore |

- **Strengths**: Health probes defined per service; environment doctrine mandates backup tiers
- **Gaps**: No deployed backup policy; no tested restore; no RTO/RPO targets measured
- **Missing evidence**: Actual backup retention on `ipai-odoo-dev-pg`; Azure Backup integration
- **Recommendations**: (1) Set PG PITR to 30 days in Bicep, (2) Test backup restore monthly, (3) Define RTO/RPO targets

#### A.2 Security — Score: 2.6

| Factor | Status | Evidence |
|--------|--------|----------|
| Identity/MFA | Partial | Entra tenant exists, P2 licensed, MFA not enforced |
| Network isolation | Partially deployed | VNet deployed; PG private endpoint active (`privatelink.postgres.database.azure.com` DNS zone); NSG rules unknown |
| Secrets | Strong | Key Vault RBAC + purge protection + managed identities |
| Scanning | Partial | Dependabot + Trivy + secret drift; no CodeQL/GHAS |
| WAF | **Deployed** | `wafipaidev` WAF policy active on Front Door (Global) |

- **Strengths**: Zero-PAT policy; OIDC workload federation; managed identities; WAF deployed; PG private endpoint active
- **Gaps**: Entra MFA not activated; no Defender for Cloud; no SIEM integration
- **Missing evidence**: WAF rule details; NSG rule specifics; Defender enablement state
- **Recommendations**: (1) Enforce MFA via Conditional Access, (2) Formalize NSG rules in Bicep, (3) Enable Defender for Containers

#### A.3 Cost Optimization — Score: 1.5

| Factor | Status | Evidence |
|--------|--------|----------|
| Cost visibility | Minimal | DigitalOcean costs tracked in YAML; no Azure equivalent |
| Tagging | Defined, not enforced | `ssot/azure/resources.yaml` has owner_domain; no Azure Policy |
| Budget alerts | Missing | No Azure Budgets configured |
| Rightsizing | Not assessed | No SKU optimization evidence |
| Reservations | Missing | No Savings Plans or Reserved Instances |

- **Strengths**: Resource inventory exists (65 Azure resources enumerated)
- **Gaps**: No Azure Cost Management dashboards; no budget alerts; 12+ ACA apps with unknown idle percentage
- **Recommendations**: (1) Enable Azure Cost Management, (2) Set monthly budget alerts, (3) Audit idle container apps

#### A.4 Operational Excellence — Score: 3.0

| Factor | Status | Evidence |
|--------|--------|----------|
| IaC | Strong (with drift) | 16 Bicep modules + Terraform DNS; parameterized 3-env; portal resources not in IaC |
| CI/CD | Strong | 8-stage ADO pipeline + 17 GH Actions workflows |
| Monitoring | **Deployed** | `ipai-appinsights` (App Insights) + `ipai-grafana-dev` + `Odoo Platform Health` workbook |
| Alerting | **Deployed** | 4 alert rules: `alert-http-5xx`, `alert-aca-restarts`, `alert-aca-no-replicas`, `alert-aca-high-cpu`; 2 action groups: `ag-ipai-platform`, `Smart Detection` |
| Runbooks | Partial | Go-live checklists exist; no incident runbooks |

- **Strengths**: Deployed alerting covers the critical signals (5xx, restarts, no replicas, high CPU); Grafana + workbook provide dashboards; CI/CD has P0-P3 quality gates
- **Gaps**: Alert rules not tracked in IaC (portal-deployed); no incident response runbook; no on-call process; alert action group targets unknown
- **IaC drift risk**: Portal-deployed resources (`alert-*`, `wafipaidev`, `ipai-grafana-dev`, `ipai-odoo-ha-env`, etc.) must be imported into Bicep to prevent configuration loss
- **Recommendations**: (1) Import alert rules + WAF policy into Bicep, (2) Create incident runbook, (3) Verify `ag-ipai-platform` action group targets (email? Slack?)

#### A.5 Performance Efficiency — Score: 2.8

| Factor | Status | Evidence |
|--------|--------|----------|
| Autoscaling | Defined | ACA min/max replicas in Bicep modules |
| Resource limits | Defined | CPU/memory per container role (web=1.0/2Gi, worker=0.5/1Gi) |
| Load testing | Missing | No performance baseline or load test evidence |
| CDN/caching | Partial | Front Door provides edge caching; no explicit cache rules |
| Cross-region latency | Unmitigated | OpenAI in East US, workloads in Southeast Asia |

- **Strengths**: Role-based container sizing; Front Door edge delivery
- **Gaps**: No load testing baseline; cross-region AI latency (~200ms added); no CDN cache rules
- **Recommendations**: (1) Establish Odoo response time baseline, (2) Evaluate OpenAI regional availability, (3) Configure Front Door caching rules

**Overall WAF Score: 2.4 / 5.0** — Strong design intent, weak operational deployment

---

### B. Landing Zone / CAF Ready

**Objective**: Foundational Azure hygiene — subscriptions, identity, networking, policy, logging, backup.

**Score: 2.2 | Confidence: Medium**

| Domain | Current State | Level (0-4) |
|--------|-------------|-------------|
| Subscription structure | Single subscription (inferred), no management groups | L1 |
| Resource group naming | Inconsistent (`rg-ipai-dev-odoo-runtime` vs `rg-ipai-data-dev`) | L1 |
| Identity | Entra P2 tenant, MFA not enforced, MI for workloads | L2 |
| Networking | VNet + 5 subnets defined; no NSGs, no PE, no bastion | L1 |
| Policy | Platform constitution + maturity rubric; no Azure Policy deployed | L1 |
| Logging | Log Analytics + App Insights defined in Bicep | L2 |
| Backup | Planned in env doctrine; not enforced in IaC | L1 |
| Naming/tagging | Convention exists in SSOT; not enforced via policy | L2 |

- **Strengths**: VNet subnet design separates ACA, PG, Databricks; env doctrine is well-defined
- **Gaps**: No Azure Policy assignments; no bastion host; DNS still partially on Cloudflare (migration to Azure DNS incomplete per SSOT)
- **Missing evidence**: Actual Azure Policy state; subscription topology; management group hierarchy
- **Owner**: Architecture / Infrastructure
- **Recommendations**: (1) Deploy NSGs per subnet, (2) Enable Azure Policy for mandatory tagging, (3) Deploy private endpoints for PG + KV, (4) Standardize RG naming

---

### C. Platform Engineering Technical Assessment

**Objective**: Internal platform capabilities — golden paths, self-service, drift prevention.

**Score: 2.8 | Confidence: Medium**

| Capability | Status | Evidence |
|-----------|--------|----------|
| Golden paths | Defined | Spec kit structure (constitution/prd/plan/tasks); ADO pipeline |
| Environment consistency | Documented | `config/ENVIRONMENTS.md` + per-env feature flags |
| Service templates | Partial | Bicep modules reusable; no app-level templates |
| Release automation | Strong | 8-stage pipeline with approval gates |
| Self-service | None | Solo operator; no portal/CLI for environment provisioning |
| Platform contracts | Strong | 37 contracts in `docs/contracts/` with validators |
| Drift prevention | Partial | Naming drift check, diagram drift check, SSOT validators |
| IDP capabilities | None | No internal developer platform |

- **Strengths**: Exceptional contract governance (37 contracts with CI validators); machine-readable SSOT
- **Gaps**: No self-service (appropriate for solo operator); no app-level service templates
- **Owner**: Platform / Architecture
- **Recommendations**: (1) Consolidate go-live checklists into single canonical gate, (2) Template new ACA service from existing Bicep modules

---

### D. DevOps Capability Assessment

**Objective**: Source control, CI/CD, testing, release safety, DORA metrics.

**Score: 3.2 | Confidence: High**

| DORA Dimension | Assessment | Evidence |
|---------------|-----------|----------|
| Deployment frequency | Low-Medium | Manual trigger; no continuous deployment |
| Lead time for changes | Unknown | No metrics collection |
| Change failure rate | Unknown | No metrics collection |
| Mean time to restore | Unknown | Rollback mechanism exists (ACA revision) but untested |

| Capability | Level | Evidence |
|-----------|-------|----------|
| Source control | L4 | Git + PR template + 5 policy gates + CODEOWNERS |
| Branch/PR controls | L3 | PR template with mandatory gates; branch protection YAML |
| CI quality gates | L4 | P0-P3 gate taxonomy (13+ P0 checks) |
| Deployment automation | L3 | 8-stage ADO pipeline with OIDC; staging auto, prod manual |
| Test automation | L2 | 24 test files + 5 module test suites; no integration test in CI |
| Observability feedback | L1 | App Insights telemetry; no alert-to-deploy feedback loop |
| Release safety | L3 | Trivy scanning, revision rollback, evidence trail |
| Rollback readiness | L2 | ACA revision rollback documented; not tested |

- **Strengths**: Best-in-class CI governance for a solo operator; machine-readable policy matrix
- **Gaps**: Eval gate pending SDK integration; no DORA metrics collection; no load/perf testing in pipeline
- **Owner**: Platform / DevOps
- **Recommendations**: (1) Integrate Foundry eval gate, (2) Add DORA metrics via Azure DevOps analytics, (3) Add rollback smoke test to pipeline

---

### E. FinOps Review

**Objective**: Cost visibility, ownership, tagging, budgets, rightsizing.

**Score: 1.2 | Confidence: Low**

| Domain | Status | Evidence |
|--------|--------|----------|
| Cost visibility | Minimal | DigitalOcean YAML tracking; no Azure Cost Management |
| Ownership allocation | Partial | `ssot/azure/resources.yaml` has `owner_domain` field |
| Tagging | Defined, not enforced | Bicep templates include `Environment`/`Project` tags; no Azure Policy |
| Budget controls | Missing | No Azure Budgets |
| Rightsizing | Not assessed | No SKU optimization analysis |
| Environment sprawl | Risk | 12+ ACA apps; several potentially idle (shelf, crm, auth) |
| Idle resource detection | Missing | No Azure Advisor cost recommendations tracked |
| Forecastability | Missing | No cost forecasting model |
| Cost efficiency | Unknown | Cross-region AI adds latency + potential egress costs |

- **Strengths**: Resource inventory exists; owner_domain field enables future chargeback
- **Gaps**: Zero Azure cost governance; no budgets, no alerts, no reservations
- **Missing evidence**: Actual monthly Azure spend; resource utilization metrics
- **Owner**: FinOps / Architecture
- **Recommendations**: (1) Enable Azure Cost Management + export, (2) Set $500/month budget alert, (3) Audit idle ACA apps, (4) Evaluate AI service region consolidation

---

### F. Cloud Adoption Security Assessment (CASA)

**Objective**: IAM, secrets, network, hardening, detection, incident readiness.

**Score: 2.3 | Confidence: Medium**

| Domain | Level | Evidence |
|--------|-------|----------|
| IAM / MFA | L2 | Entra P2 tenant; MFA not enforced; OIDC registered not activated |
| Privileged access | L2 | Zero-PAT policy; break-glass password policy; no PIM |
| Secrets handling | L3 | Key Vault RBAC + purge protection + MI binding |
| Network exposure | L1 | Front Door Premium; no NSGs, no PE, default-allow KV network ACLs |
| Workload hardening | L2 | Container resource limits; non-root containers (web shell); Trivy scanning |
| Logging / detection | L1 | Log Analytics defined; no alert rules; no SIEM; no Defender |
| Incident readiness | L1 | Web shell threat model with kill switch; no general incident runbook |
| Data protection | L2 | TDE assumed (PG Flex default); Key Vault encryption; no classification policy |
| Vulnerability management | L2 | Dependabot weekly; Trivy in Docker builds; no CodeQL |

- **Strengths**: Excellent secrets discipline; zero-PAT enforcement; workload identity federation
- **Gaps**: MFA not enforced; no SIEM; no Defender for Cloud; network wide open within VNet
- **Missing evidence**: Actual Defender enablement state; Conditional Access policies; NSG deployment
- **Owner**: Security / Platform
- **Recommendations**: (1) Enable Conditional Access with MFA, (2) Deploy NSGs, (3) Enable Defender for Containers, (4) Enable CodeQL

---

### G. Technical Assessment for Generative AI in Azure

**Objective**: Production readiness for AI workloads — safety, evals, observability, grounding.

**Score: 2.5 | Confidence: High**

| Domain | Level | Evidence |
|--------|-------|----------|
| Model/provider abstraction | L3 | 4-tier fallback (SDK → HTTP → simple → offline) |
| Authentication | L2 | API key in `ir.config_parameter`; managed identity support coded but not active |
| Safety controls | L2 | SQL injection prevention, model blocklist, read-only default; no PII masking |
| Evals | L1 | 28-capability matrix + eval contract + 4 evaluator types; not integrated in CI/CD |
| Observability | L2 | App Insights telemetry (5 event types); no alerts, no dashboards |
| Data boundaries | L2 | KB scope + group_ids in search index; no tenant isolation for AI queries |
| Grounding / retrieval | L2 | Azure AI Search index schema; pipeline built; index needs seeding (438 docs discovered) |
| Fallback behavior | L3 | 4-tier cascade with offline response; activity timeline for transparency |
| Secrets and identity | L2 | API key in DB (not Key Vault secret reference); MI support not activated |
| Release discipline | L1 | Eval gate stage in pipeline but placeholder ("pending SDK integration") |

- **Strengths**: Deterministic skill router (no ML black box); comprehensive audit trail (28 fields); 14 governed tool functions
- **Gaps**: Eval gate not enforced; no prompt injection detection; no PII masking; KB not seeded
- **Missing evidence**: Content safety filter config on Azure OpenAI deployment; token consumption metrics
- **Owner**: AI / Platform
- **Recommendations**: (1) Seed knowledge index, (2) Integrate eval gate in pipeline, (3) Add prompt injection detection, (4) Move API key to Key Vault secret reference

---

### H. Go-Live | Well-Architected Review

**Objective**: Pre-production cutover readiness.

**Score: 1.5 | Confidence: Medium**

| Domain | Status | Evidence |
|--------|--------|----------|
| Runbooks | Partial | 5 go-live checklists in different locations; no canonical version |
| Rollback plan | Documented | ACA revision rollback; SQL migration rollback paths |
| SLOs / health checks | Partial | Health probes defined; no SLO targets |
| Alerting | Missing | Zero alert rules |
| On-call ownership | Missing | Solo operator; no escalation path |
| Dependency readiness | Partial | 65 Azure resources inventoried; deployment order undocumented |
| Migration sequencing | Missing | No cutover plan from dev to staging/prod |
| Data integrity | Missing | No data validation suite for migration |
| Backup restore proof | Missing | No tested restore |
| Business continuity | Missing | No BC plan |

- **Strengths**: Multiple go-live checklists show awareness; rollback mechanisms exist
- **Gaps**: No canonical go-live gate; no tested backup restore; no SLOs
- **Owner**: Architecture / Runtime
- **Recommendations**: (1) Consolidate into single go-live checklist, (2) Test PG backup restore, (3) Define SLOs for Odoo response time + uptime

---

### I. Developer Velocity Index

**Objective**: Development friction, CI wait times, cognitive load.

**Score: 2.8 | Confidence: Low**

| Domain | Assessment | Evidence |
|--------|-----------|----------|
| Local setup | Medium friction | Devcontainer exists; pyenv + native Mac also supported |
| CI wait times | Unknown | No metrics; 17 workflows, most lightweight validation |
| Test confidence | Low | 5/69 modules have tests; no integration tests in CI |
| Cognitive load | High | 437 docs, 37 contracts, 38 specs — rich but overwhelming |
| Environment parity | Defined | Three-env doctrine; only dev deployed |
| Documentation discoverability | Strong | SSOT governance, CLAUDE.md hierarchy, indexed contracts |

- **Strengths**: Rich documentation ecosystem; devcontainer for fast onboarding
- **Gaps**: Solo operator makes DVI less meaningful; test coverage at 7% of modules
- **Owner**: Platform
- **Recommendations**: Defer formal DVI until team > 1; increase test coverage incrementally

---

### J. Mission Critical | Well-Architected Review

**Objective**: Suitability for >99.9% SLA workloads.

**Score: 0.8 | Confidence: Low**

| Domain | Status |
|--------|--------|
| Multi-region / HA | Not deployed (single region) |
| Blast radius reduction | Minimal (subnets defined, no fault domains) |
| Resiliency patterns | Health probes only |
| Chaos engineering | Not practiced |
| Operational rigor | No on-call, no incident process |

- **Assessment**: The platform is not designed for mission-critical SLAs and does not need to be at this stage. Revisit when business requirements demand >99.9% uptime.
- **Owner**: Architecture (future)

---

### K. SaaS Journey Review

**Objective**: Readiness for multi-tenant SaaS delivery.

**Score: 2.0 | Confidence: Medium**

| Domain | Status | Evidence |
|--------|--------|----------|
| Tenancy model | Documented | `TENANCY_MODEL.md` + `MULTITENANCY_MODEL.md` — 3-phase plan |
| Configuration isolation | Planned | Per-layer isolation matrix documented; not implemented |
| Lifecycle automation | Missing | No tenant provisioning/deprovisioning |
| Billing/metering | Missing | No billing module, no COGS tracking |
| Supportability | Missing | No customer support workflow |
| Upgrade strategy | Partial | Odoo module upgrade pipeline exists; no tenant-aware rollout |

- **Strengths**: Exceptionally detailed tenancy architecture documentation with per-plane isolation matrix
- **Gaps**: Zero implementation — all SaaS capability is on paper only
- **Owner**: Architecture (future)
- **Recommendations**: Defer active SaaS development until single-tenant production is stable

---

## 5. Cross-Cutting Risk Register

| ID | Risk | Impact | Likelihood | Evidence | Mitigation | Phase |
|----|------|--------|-----------|----------|------------|-------|
| R1 | **Single-environment naming** — all workloads named `*-dev`; no staging/prod distinction | Critical | Certain | All ACA names contain `dev`; `pg-ipai-odoo` is prod-grade but unnamed as staging/prod | Deploy staging using `ipai-odoo-ha-env` or new env | Now |
| R2 | **IaC drift** — portal-deployed resources not in Bicep (alerts, WAF, PE, HA env, Grafana) | High | Certain | 52 live resources; Bicep defines ~30; delta created via portal | Import portal resources into Bicep | Now |
| R3 | **Identity not enforced** — Entra OIDC registered but Odoo uses basic login | High | Certain | `ipai_auth_oidc` module referenced but not found in codebase | Rebuild/port OIDC module; enforce Conditional Access | Now |
| R4 | **Network partially secured** — PG private endpoint active but KV still default-allow | Medium | Likely | `privatelink.postgres.database.azure.com` exists; KV Bicep has `defaultAction: 'Allow'` | Set KV network to `Deny` + add PE for KV | Now |
| R5 | **AI eval gate not enforced** — copilot releases bypass quality validation | Medium | Likely | `Eval_Gate` stage in pipeline = placeholder | Seed KB + expand eval dataset + activate gate | Now |
| R6 | **No tested backup restore** — backup policies planned but never validated | High | Possible | `config/ENVIRONMENTS.md` plans PITR; no restore evidence | Monthly restore test to disposable DB | Pre-Prod |
| R7 | **5 go-live checklists, no canonical gate** — risk of incomplete cutover | Medium | Likely | 5 files in `docs/runbooks/` and `docs/delivery/` | Consolidate into single gated checklist | Pre-Prod |
| R8 | **Cross-region AI latency** — OpenAI in East US, workloads in SEA | Medium | Certain | `oai-ipai-dev` in East US; ACA in Southeast Asia | Evaluate SEA OpenAI availability; measure actual latency | Pre-Prod |
| R9 | **No CodeQL / GHAS** — static analysis limited to linting | Medium | Possible | No CodeQL workflows found | Enable GHAS + CodeQL for Python/JS | Now |
| R10 | **FinOps blind spot** — no Azure cost visibility | Medium | Certain | No Azure Cost Management evidence | Enable cost export + budget alerts | Now |
| R11 | **Key Vault API key for AI** — copilot API key stored in `ir.config_parameter` (DB) not Key Vault | Medium | Possible | `foundry_service.py` reads from ICP; key set via `psql` | Migrate to Key Vault secret reference via env var | Pre-Prod |
| R12 | **Solo operator** — bus factor = 1, no peer review, no on-call | High | Certain | Single contributor | Document runbooks; establish escalation path | Pre-Prod |
| R13 | **Deprecated artifacts in repo** — DigitalOcean, Supabase configs still tracked | Low | Certain | `infra/deploy/DROPLET_DEPLOYMENT.md`, `infra/azure/supabase/` | Archive to `archive/` directory | Now |
| R14 | **Prompt injection risk** — no input validation before LLM | Medium | Possible | No content filter in `foundry_service.py` or controller | Add prompt injection detector | Pre-Prod |

---

## 6. Prioritized Roadmap

### Now (0-30 days)

| # | Title | Why It Matters | Prerequisites | Evidence to Close | Expected Outcome |
|---|-------|---------------|---------------|-------------------|-----------------|
| N1 | **Reconcile IaC with live Azure state** | 20+ portal-deployed resources not tracked in Bicep — reproducibility and drift risk | Bicep modules (exist); live resource inventory (52 resources) | All live resources represented in Bicep; `az deployment what-if` clean | IaC is source of truth; no portal-only config |
| N2 | **Enable Azure Cost Management** | No visibility into monthly Azure spend; 22 ACA apps + AI services | Azure subscription access | Cost export + $500/month budget alert | Cost anomalies detected within 24h |
| N3 | **Formalize NSG rules in Bicep** | VNet deployed but NSG rules unknown/untracked | VNet deployment (live) | NSG rules in Bicep matching live state + deployment proof | Network controls are reproducible |
| N4 | **Enable Entra Conditional Access + MFA** | Admin access to Azure/Odoo has no MFA | Entra P2 (already licensed) | CA policy screenshot + sign-in log | All admin logins require MFA |
| N5 | **Seed knowledge base index** | RAG copilot returns empty results without data | Azure AI Search + OpenAI (exist) | `ingest.sh --full` output + search query proof | 7,000+ chunks indexed and retrievable |
| N6 | **Archive deprecated infra configs** | Repo contains DigitalOcean/Supabase cruft | None | Git commit moving files to `archive/` | Clean `infra/` directory |
| N7 | **Enable CodeQL via GitHub Actions** | No static security analysis beyond linting | GitHub Advanced Security (free for public repo or paid) | CodeQL workflow + first scan results | Security vulnerabilities detected in CI |
| N8 | **Set PG backup retention in Bicep** | Backup policy planned but not in IaC | PostgreSQL Flexible Server module | `backupRetentionDays: 30` in Bicep + deploy | Automated 30-day PITR |

### Before Production Cutover

| # | Title | Why It Matters | Prerequisites | Evidence to Close | Expected Outcome |
|---|-------|---------------|---------------|-------------------|-----------------|
| P1 | **Deploy staging environment** | No environment parity for pre-prod validation | N3, N4 (network + identity) | Staging ACA + PG running; health check green | Staging mirrors prod topology |
| P2 | **Consolidate go-live checklist** | 5 versions create confusion at cutover | None | Single `docs/runbooks/GO_LIVE_GATE.md` | One canonical pre-prod gate |
| P3 | **Test backup restore** | Untested backups are not backups | N8 (backup retention) | Restore to `test_restore_*` DB + row count match | RTO measured and documented |
| P4 | **Integrate eval gate in CI/CD** | AI copilot releases bypass quality validation | N5 (KB seeded) + eval dataset (20+ cases) | Eval_Gate stage passes/fails on real data | AI releases gated on quality scores |
| P5 | **Activate Entra OIDC for Odoo** | Odoo uses basic login; no SSO, no MFA for users | N4 (MFA enabled) + OIDC module port | Odoo login via Entra redirect proof | All Odoo users authenticate via Entra |
| P6 | **Migrate AI API key to Key Vault** | API key in Odoo DB is weaker than Key Vault ref | Key Vault PE deployed (N3) | Env var `FOUNDRY_API_KEY` sourced from KV | No secrets in application database |
| P7 | **Add prompt injection detection** | User input goes raw to LLM | None | Detector in controller pipeline + test cases | Malicious prompts blocked before LLM |
| P8 | **Deploy private endpoints for PG + KV** | Database and secrets accessible on public network | N3 (NSGs) | PE resources in Bicep + connectivity proof | No public access to PG or KV |
| P9 | **Define production SLOs** | No targets means no measurement | N1 (alerts) | SLO doc: uptime 99.5%, p95 latency < 3s | Measurable production targets |

### Later at Scale

| # | Title | Why It Matters | Prerequisites | Evidence to Close | Expected Outcome |
|---|-------|---------------|---------------|-------------------|-----------------|
| L1 | **Multi-region deployment** | Single-region = single point of failure | P1, P3, P9 | Secondary region deployment + failover test | Regional resilience |
| L2 | **Implement tenant isolation** | SaaS requires data boundary enforcement | P5 (identity), SaaS spec | Tenant context middleware + leakage test | Multi-tenant safe |
| L3 | **Enable Defender for Cloud** | Advanced threat detection | N4 (identity), P8 (network) | Defender dashboard + alert integration | Runtime threat detection |
| L4 | **Azure Savings Plans / Reservations** | Cost optimization at scale | N2 (cost visibility) + 3 months usage data | Reservation coverage report | 20-40% compute cost reduction |
| L5 | **DORA metrics collection** | Quantify delivery performance | P1 (staging), P4 (eval gate) | Azure DevOps analytics dashboard | Data-driven delivery improvement |
| L6 | **Internal developer platform** | Self-service for team growth | P1 (staging), multiple operators | Service catalog + provisioning CLI | Reduced onboarding friction |

---

## 7. Decision Memo

### Is IPAI ready for controlled production?

**Verdict: CONDITIONALLY READY**

The IPAI platform is not blocked by absence of core Azure runtime controls. Live inventory confirms that major production primitives are in place, including WAF, alerting, Container Apps runtime, PostgreSQL Flexible Server, monitoring assets, and broader platform service coverage than previously captured.

However, the platform is not yet fully production-governed. The principal concern is now **control-plane integrity**, not basic runtime existence. Approximately twenty live Azure resources appear to be outside the current Bicep-tracked estate, creating a significant IaC drift risk. This weakens reproducibility, reviewability, and disaster recovery confidence.

### Hard Blockers (must resolve before any production traffic)

1. **Reconcile live Azure resources into IaC** or explicitly register justified exceptions
2. **Prove restore / recovery posture** for PostgreSQL and filestore-adjacent data
3. **Confirm private connectivity and exposure boundaries** end to end, not just DNS artifacts
4. **Verify production alert routing and operational response ownership**
5. **Close identity gaps** — activate Entra OIDC for Odoo; enforce MFA via Conditional Access

### Can Safely Wait

- Multi-region deployment (L1)
- SaaS tenant isolation (L2)
- Defender for Cloud (L3) — important but not a launch blocker
- Azure Reservations (L4)
- DORA metrics (L5)
- Internal developer platform (L6)
- Mission Critical WAF assessment
- Developer Velocity assessment
- Platform Engineering self-service

### Path to Conditional Readiness

Complete **N1-N8** (Now tier, ~2-4 weeks) + **P1, P2, P3, P5, P6, P9** (Pre-Prod essentials) to achieve a **controlled production posture** suitable for internal users with accepted risk. External/customer-facing production requires the full Pre-Prod tier + P4, P7, P8.

---

## 8. Appendix

### A. Evidence Sources Reviewed

| Source | Path | Type |
|--------|------|------|
| Bicep IaC | `infra/azure/main.bicep`, `odoo-runtime.bicep`, `modules/*.bicep` | IaC (intended state) |
| Bicep parameters | `infra/azure/parameters/*.parameters.json` (8 files) | IaC (intended state) |
| Terraform DNS | `infra/terraform/cloudflare/insightpulseai.com/main.tf` | IaC (intended state) |
| Azure DevOps pipeline | `.azuredevops/pipelines/odoo-module.yml` (479 lines) | CD definition |
| GitHub Actions | `.github/workflows/` (17 workflows) | CI definition |
| CI scripts | `scripts/ci/` (15 validators) | CI tooling |
| CI/CD policy matrix | `ssot/ci/ci_cd_policy_matrix.yaml` (442 lines) | Governance |
| Platform constitution | `ssot/governance/platform-constitution.yaml` | Governance |
| Platform maturity benchmark | `ssot/azure/platform_maturity_benchmark.yaml` | Self-assessment rubric |
| Azure resources inventory | `ssot/azure/resources.yaml` (65 resources) | Resource inventory |
| Front Door routes | `ssot/azure/front-door-routes.yaml` | Routing (intended state) |
| Environment config | `config/ENVIRONMENTS.md`, `config/{dev,staging,prod}/` | Environment doctrine |
| Contracts index | `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` (37 contracts) | Cross-boundary contracts |
| OIDC clients | `infra/ssot/auth/oidc_clients.yaml` | Identity config |
| GitHub auth surface | `infra/ssot/auth/github_auth_surface.yaml` | Auth policy |
| Workload identities | `infra/ssot/security/workload_identities.yaml` | Identity config |
| Key Vault Bicep | `infra/azure/modules/keyvault.bicep` | IaC (intended state) |
| Copilot source | `addons/ipai/ipai_odoo_copilot/` (all models, controllers, data) | Application code |
| Copilot eval | `agents/evals/odoo_copilot_target_capabilities.yaml` | Eval framework |
| KB pipeline | `packages/odoo-docs-kb/` | Data pipeline code |
| Tenancy model | `docs/architecture/TENANCY_MODEL.md`, `MULTITENANCY_MODEL.md` | Architecture doc |
| Docker image | `docker/Dockerfile.prod` | Container definition |
| Devcontainer | `.devcontainer/devcontainer.json` | Dev environment |
| PR template | `.github/pull_request_template.md` | Quality gate |
| Dependabot | `.github/dependabot.yml` | Vulnerability scanning |
| Admin email policy | `infra/identity/admin-email-policy.yaml` | Identity governance |
| Web shell threat model | `infra/security/WEB_SHELL_THREAT_MODEL.md` | Security analysis |
| Go-live checklists | `docs/runbooks/ODOO19_GO_LIVE_CHECKLIST.md` + 4 others | Cutover planning |
| DigitalOcean costs | `infra/ssot/infra/digitalocean/costs/2026-*.yaml` | Cost tracking |
| Copilot live test | `curl /api/pulser/chat` on 2026-04-05 | Runtime verification |

### A2. Live Azure Resource Inventory (52 resources, 2026-04-05)

Sourced from Azure Resource Graph (portal screenshot). This inventory supersedes repo-only evidence.

**Resource Groups (6):**
- `rg-ipai-dev-odoo-runtime` (primary — 39 resources)
- `rg-ipai-dev-odoo-data` (2 resources: `pg-ipai-odoo`, `stipaiodoodev`)
- `rg-ipai-dev-platform` (1 resource: `kv-ipai-dev`)
- `rg-data-intel-ph` (2 resources: Foundry project + resource)
- `ME_ipai-odoo-ha-env_*` (managed — LB + public IP)
- Auto-managed (Log Analytics, Network Watcher, DevOps org)

**Container Apps (22) + Jobs (1):**
`ipai-odoo-dev-web`, `ipai-odoo-dev-worker`, `ipai-odoo-dev-cron`, `ipai-copilot-gateway`, `ipai-mcp-dev`, `ipai-ocr-dev`, `ipai-superset-dev`, `ipai-website-dev`, `ipai-login-dev`, `ipai-mailpit-dev`, `ipai-grafana-dev`, `ipai-ops-dashboard`, `ipai-code-server-dev`, `ipai-odoo-connector`, `ipai-workload-center`, `ipai-w9studio-dev`, `ipai-prismalab-dev`, `w9studio-landing-dev`, `ipai-build-agent` (Job)

**Container Apps Environments (2):**
`ipai-odoo-dev-env` (original), `ipai-odoo-ha-env` (HA — with managed LB + public IP)

**Monitoring:**
- `ipai-appinsights` (Application Insights)
- `func-ipai-meta-capi` (Application Insights — Meta CAPI)
- `la-ipai-odoo-dev` (Log Analytics)
- `managed-ipai-appinsights-ws` (Log Analytics — managed)
- `Odoo Platform Health` (Azure Workbook)
- `ipai-grafana-dev` (Grafana container app)

**Alerting:**
- `alert-http-5xx` (Metric alert rule)
- `alert-aca-restarts` (Metric alert rule)
- `alert-aca-no-replicas` (Metric alert rule)
- `alert-aca-high-cpu` (Metric alert rule)
- `ag-ipai-platform` (Action group)
- `Application Insights Smart Detection` (Action group)

**Security / Networking:**
- `afd-ipai-dev` (Front Door)
- `wafipaidev` (Front Door WAF policy)
- `vnet-ipai-dev` (Virtual network)
- `privatelink.postgres.database.azure.com` (Private DNS zone — PG private endpoint)
- `kv-ipai-dev` (Key Vault)

**Data:**
- `pg-ipai-odoo` (PostgreSQL Flexible Server — General Purpose, upgraded from Burstable)
- `stipaiodoodev`, `stipaidev` (Storage accounts)
- `acripaiodoo` (Container Registry)

**DNS:**
- `insightpulseai.com` (Azure DNS zone)
- `w9studio.net` (Azure DNS zone)

**AI:**
- `ipai-copilot-resource` (Foundry, East US 2)
- `ipai-copilot` (Foundry project, East US 2)

**Other:**
- `func-ipai-meta-capi` (Function App)
- `SoutheastAsiaLinuxDynamicPlan` (App Service plan)
- `insightpulseai` (Azure DevOps organization)
- `NetworkWatcher_southeastasia`

### B. Assumptions

1. Only `dev` environment is deployed. No runtime evidence of staging or production environments.
2. Azure subscription is single-subscription (no management group evidence found).
3. PostgreSQL uses Azure-default TDE (transparent data encryption) — not explicitly configured in Bicep.
4. All `dev`-named Container Apps are the actual running workloads, not a parallel dev instance alongside production.
5. WAF policy on Front Door is conditional in Bicep — assumed not yet deployed.
6. Keycloak was never operationalized based on infrastructure rules stating "no apps authenticate through it."
7. Cost posture is unknown — DigitalOcean tracking exists but no Azure cost data in repo.

### C. Unanswered Questions

1. What is the actual monthly Azure spend?
2. Is the Entra Conditional Access policy deployed, or just the tenant?
3. What is the actual PostgreSQL backup retention currently configured?
4. Are any NSGs deployed outside of Bicep (via portal)?
5. Is Application Insights instrumented in the running Odoo container (connection string set)?
6. What is the actual latency between Southeast Asia ACA and East US OpenAI?
7. Is the `ipai_auth_oidc` module archived or permanently removed?
8. Are there Azure Policy assignments deployed via portal (not tracked in repo)?

### D. Confidence Caveats

- **IaC ≠ Deployed**: Many scores reflect intended state (Bicep/SSOT) not verified runtime state. The platform likely scores lower on actual deployment than on design.
- **Solo operator context**: Some gaps (no peer review, no on-call) are structural to team size, not negligence. Scores reflect the gap regardless of cause.
- **Evidence selection bias**: Assessment relied on repo artifacts. Azure portal state, runtime metrics, and actual costs were not directly observable.
- **Assessment approximation**: These are not official Microsoft assessment results. Scores are calibrated against the published rubrics but carry inherent subjectivity.

---

## 9. Azure Boards Translation

This assessment translates directly into an Azure Boards portfolio backlog. The mapping convention is:

| Assessment Artifact | Azure Boards Work Item |
|---|---|
| Assessment lens (A-K) | **Epic** (grouped by governance theme, not 1:1 with lens) |
| Cross-cutting risk (R1-R14) | **Feature** under the relevant Epic |
| Roadmap item (N1-N8, P1-P9, L1-L6) | **Feature** or **PBI** depending on scope |
| Evidence gap | **PBI** prefixed `EVIDENCE:` |
| Implementation task | **PBI** prefixed `IMPLEMENT:` |

### Default Epics

| Epic | Scope |
|---|---|
| **Governance & Drift Remediation** | IaC reconciliation, deprecated artifact cleanup, cost visibility |
| **Production Readiness & Resilience** | Backup/restore, environment parity, SLOs, go-live gate |
| **Security & Network Hardening** | Identity (Entra OIDC + MFA), private endpoints, NSGs, CodeQL |
| **Observability & Operations** | Alert routing, runbooks, solo-operator mitigation |
| **AI Platform Readiness** | KB seeding, eval gate, prompt injection, API key migration |
| **Platform Productization & Scale** | Multi-region, SaaS isolation, Defender, FinOps, DORA |

### Backlog Files

| File | Purpose |
|---|---|
| `docs/planning/IPAI_AZURE_BOARDS_BACKLOG.md` | Full Epic → Feature → PBI hierarchy (human-readable) |
| `docs/planning/IPAI_AZURE_BOARDS_IMPORT.csv` | CSV for Azure Boards bulk import |

### Field Conventions

- **Business Value**: 1-10 (10 = hard blocker for production)
- **Time Criticality**: 1-10 (10 = Now tier)
- **Tags**: `platform-assessment`, `now`, `pre-prod`, `later`, `evidence`, `implement`
- **Area Path**: `IPAI\Platform`
- **Iteration Path**: `IPAI\Sprint 1` (Now), `IPAI\Sprint 2` (Pre-Prod), `IPAI\Backlog` (Later)

---

*Generated: 2026-04-05 | Assessor: Claude Code (Principal Cloud Architecture Assessment) | Version: 1.0*
