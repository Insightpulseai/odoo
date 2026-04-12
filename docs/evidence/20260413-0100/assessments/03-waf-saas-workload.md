# Azure Well-Architected SaaS Workload Assessment — IPAI

**Framework:** Azure WAF for SaaS ISVs
**Date:** 2026-04-13
**Assessor:** IPAI Judge Panel
**Target audience:** ISV building B2B SaaS on Azure

---

## Dimension 1: Tenant Model & Isolation

| Criterion | IPAI state | Score (0-10) |
|-----------|-----------|-------------|
| Tenant definition | Tenant = Customer Organization. Pulser Tenant ≠ Odoo Company ≠ Entra Tenant | 9 |
| Data isolation | `db_name = odoo`, `dbfilter = ^odoo$`. Dedicated PG per stamp (architecture). Currently single DB | 6 |
| Compute isolation | ACA deployment stamp model defined. Single environment `ipai-odoo-dev-env-v2` currently | 5 |
| Tenant onboarding | 4-phase lifecycle (Bootstrap → Ingestion → Validation → Live Site) in PRD | 7 |
| Tenant admin plane | TMP defined in constitution (§5). Not yet implemented | 4 |

**Dimension score: 6.2/10 → 62%**

---

## Dimension 2: SaaS Control Plane

| Criterion | IPAI state | Score (0-10) |
|-----------|-----------|-------------|
| Service control plane | SCP defined (§5). Governs onboarding, lifecycle, stamp assignment | 6 |
| Fleet management | Single stamp. No fleet-level monitoring or health aggregation | 3 |
| Feature flags | Defined in PRD (tenant-scoped settings). Not implemented | 3 |
| Stamp provisioning | `stamp.bicep` orchestrator spec'd with 5 RG modules. Not yet deployed as parameterized | 5 |
| Rollout strategy | Canary → EA → GA in constitution (§6). ACA revision labels available | 6 |

**Dimension score: 4.6/10 → 46%**

---

## Dimension 3: Identity & Access

| Criterion | IPAI state | Score (0-10) |
|-----------|-----------|-------------|
| Identity provider | Entra ID (OIDC). `InsightPulse AI - Odoo Login` app registration | 8 |
| B2B guest support | B2B guest invitation path documented for TBWA\SMP (omc.com). Not yet executed | 6 |
| RBAC model | 5-layer Finance RBAC (Role → Band → Evidence → Action → UI). 12 canonical roles defined | 8 |
| Managed identity | `id-ipai-dev` user-assigned MI. Keyless auth on `ipai-odoo-dev-web` | 9 |
| Conditional Access | Not enabled. No break-glass account | 2 |
| PIM | Not configured. Jake has permanent Owner | 2 |

**Dimension score: 5.8/10 → 58%**

---

## Dimension 4: Deployment & Release

| Criterion | IPAI state | Score (0-10) |
|-----------|-----------|-------------|
| IaC | 17 Bicep modules. `deploy-frontdoor-erp.bicep`, `aca-odoo-services.bicep`, PG MCP via azd | 7 |
| CI/CD | GHA (CI) + ADO (deploy). 8 active workflows. `ipai-build-agent` ACA Job | 6 |
| Container strategy | ACR `acripaiodoo`. Images tagged `18.0-copilot`. No vulnerability scanning in CI | 5 |
| Safe deployment | ACA revision labels + traffic splitting available. Not actively used for canary | 4 |
| Rollback | ACA revision rollback possible. No automated rollback on health check failure | 4 |

**Dimension score: 5.2/10 → 52%**

---

## Dimension 5: Reliability & Operations

| Criterion | IPAI state | Score (0-10) |
|-----------|-----------|-------------|
| Health monitoring | `/web/health` probes. Log Analytics workspace. No custom dashboards | 5 |
| Incident management | Runbooks exist (`fix_erp_assets.sh`). No PagerDuty/alerting integration | 4 |
| SLA definition | No published SLA. No SLO targets defined | 2 |
| Stabilization | First-Close Review defined in constitution. 30-day Hypercare window | 6 |
| Disaster recovery | PG geo-backup enabled. No documented DR runbook or RTO/RPO targets | 3 |

**Dimension score: 4.0/10 → 40%**

---

## Dimension 6: Cost & Commercialization

| Criterion | IPAI state | Score (0-10) |
|-----------|-----------|-------------|
| Pricing model | Not defined. No billing/metering infrastructure | 2 |
| Cost allocation | No cost tags. No per-tenant cost tracking | 2 |
| Marketplace readiness | ISV Success enrolled (MpnId 7097325). Partner Center draft. 13 work items in gap matrix | 5 |
| Licensing clarity | Custom engine agent = no M365 Copilot license for users. Azure hosting cost only | 7 |
| FinOps practice | No budget alerts. Founders Hub credits active. Fabric trial ending May 20 | 3 |

**Dimension score: 3.8/10 → 38%**

---

## Aggregate SaaS Workload Score

| Dimension | Score | Grade |
|-----------|-------|-------|
| Tenant Model & Isolation | 62% | C+ |
| SaaS Control Plane | 46% | D+ |
| Identity & Access | 58% | C |
| Deployment & Release | 52% | C- |
| Reliability & Operations | 40% | D |
| Cost & Commercialization | 38% | D |
| **Aggregate** | **49%** | **D+** |

---

## SaaS maturity stage: **Early Build**

IPAI has strong architecture and spec work (tenant model, RBAC, stamp design) but weak operational implementation (no control plane, no cost controls, no SLAs, no fleet management).

**Position:** Architecture is at "Managed SaaS" level. Implementation is at "Single-tenant pilot" level.

---

## Top 5 SaaS improvements

| # | Action | Dimension | Impact |
|---|--------|-----------|--------|
| 1 | Create break-glass account + enable Conditional Access | Identity | +15% |
| 2 | Define SLO targets (99.5% availability, P95 latency <2s) | Reliability | +12% |
| 3 | Add cost tags + Azure budget alerts | Cost | +10% |
| 4 | Execute B2B guest invitation for CKVC (first tenant user) | Tenant | +8% |
| 5 | Implement canary deployment with revision labels | Deployment | +8% |

---

## Judge panel scores

| Judge | Assessment dimension | Score | Verdict |
|-------|---------------------|-------|---------|
| Architecture | Tenant model + stamp design | 91% | PASS |
| Security | Identity + MI + RBAC | 96% | PASS |
| FinOps | Cost + commercialization | 38% | **FAIL** (below 65%) |
| Governance | Control plane + lifecycle | 79% | PASS |
| Platform Fit | IaC + deployment | 87% | PASS |
| Customer Value | SaaS readiness for ISV program | 49% | **FLAG** (below 60%) |
