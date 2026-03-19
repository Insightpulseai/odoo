# SSOT Boundaries — InsightPulse AI Platform

> Human-readable view of `ssot/architecture/platform-boundaries.yaml`.
> This file is **derived** — edit the YAML source, not this document.

---

## Architecture Model

**Six-plane Azure-first architecture.**

| # | Plane | Scope | Key Systems |
|---|-------|-------|-------------|
| 1 | Governance / Control | Planning, code, release, policy | Azure Boards, GitHub, Azure Pipelines, Azure Policy |
| 2 | Identity / Network / Security | Auth, edge, secrets, API governance | Entra ID, Front Door, Key Vault, APIM |
| 3 | Business Systems | Transactional ERP, automation | Odoo CE 19, n8n |
| 4 | Data Intelligence | Lakehouse, ML, BI serving | Databricks, ADLS Gen2, Unity Catalog |
| 5 | Agent / AI Runtime | Agent factory, tracing, evals | Microsoft Foundry, Azure OpenAI, Document Intelligence |
| 6 | Experience / Domain Apps | User-facing surfaces | Ops Console, BI surfaces, Copilot UIs, Slack |

---

## System Authority Model

Every system has exactly one role. No system may claim authority beyond its designation.

| System | Role | Plane | Owns | Does NOT Own |
|--------|------|-------|------|-------------|
| **Odoo CE 19** | System of Record (SoR) | Business Systems | Accounting, invoicing, projects, tasks, BIR filings, employees, vendors, analytic accounts, expense documents | Identity, platform events, vector embeddings, analytical workloads |
| **Databricks + ADLS/Delta + Unity Catalog** | System of Intelligence (SoI) | Data Intelligence | Medallion lakehouse, ML features, serving endpoints, Gold KPIs, financial consolidation, sales forecasting, operational BI | Transactional ERP data, identity, secrets |
| **Microsoft Foundry** | Agent Runtime | Agent / AI Runtime | Agent lifecycle, model/tool governance, prompt tracing, evaluation pipelines, monitoring | Transactional ERP data, lakehouse governance, identity |
| **Azure API Management** | Governed Ingress/Egress | Identity / Network / Security | Policy enforcement boundary | Not SoR, not agent runtime |

**Hard boundary:** Databricks, n8n, and Azure Front Door never become SSOT or SOR. They read from Odoo/Supabase and publish only *derived artifacts*.

---

## Truth Authorities

Separate from plane membership. Each authority is the operational source of truth for its domain.

| Authority | System | Scope |
|-----------|--------|-------|
| **Planned truth** | Azure Boards | Work items, sprints, epics, capacity planning |
| **Code truth** | GitHub | Source code, PRs, branch policies, CODEOWNERS |
| **Release truth** | Azure Pipelines | Build/release gates, environment promotions, artifact registry |
| **Live inventory truth** | Azure Resource Graph | Actual Azure resource state, drift detection |
| **Agent runtime truth** | Microsoft Foundry | Agent deployments, model versions, trace logs, eval results |
| **Intended state truth** | Repo SSOT | Machine-readable YAML in `ssot/` directories across repos |

---

## Tenancy Doctrine

| Tier | App Model | Data Model |
|------|-----------|------------|
| Default | Shared runtime farm (single ACA environment) | Database-per-tenant (dedicated PostgreSQL DB) |
| Premium | Deployment stamp per tenant (dedicated ACA + DB) | Dedicated database |

Promotion from shared to stamped deployment must be **fully automated** — no manual infrastructure provisioning.

---

## Repo Ownership

| Repo | Plane | Purpose |
|------|-------|---------|
| `odoo` | Business Systems | Odoo CE 19, OCA modules, thin `ipai_*` bridges |
| `platform` | Governance / Control | Governance/control plane application surfaces |
| `data-intelligence` | Data Intelligence | Databricks notebooks, ADLS schemas, Unity Catalog |
| `agent-platform` | Agent / AI Runtime | Foundry agents, tools, evals, prompts |
| `web` | Experience / Domain Apps | Experience / domain application frontends |
| `infra` | Identity / Network / Security | IaC, landing zones, networking, Key Vault, APIM |
| `automations` | Business Systems | n8n workflows, orchestration assets |

### Within `odoo` repo

| Path | Role |
|------|------|
| `addons/ipai/` | Thin bridge/meta modules only — not general business capability |
| `addons/oca/` | Primary business capability lane (OCA-first policy) |
| `ssot/` | Machine-readable intended-state YAML |

---

## Integration Boundary

- **API Gateway**: Azure API Management (governed ingress/egress only)
- **Event Bus**: Azure Service Bus
- **Edge**: Azure Front Door
- All agent-to-Odoo calls routed through APIM
- All cross-tenant routing through APIM
- APIM is NOT the system of record and NOT the agent runtime

---

## Prohibited Flows

| Flow | Reason |
|------|--------|
| Databricks writing directly to Odoo PostgreSQL | Lakehouse is read-only consumer of ERP data |
| BI surfaces writing back to any operational system | BI is presentation-only |
| Agents bypassing APIM for Odoo access | All agent-to-Odoo calls must be governed and traced |
| ADLS used as operational data source | ADLS is analytical only |
| Supabase used as primary identity plane | Microsoft Entra ID is canonical identity |

---

*Source: `ssot/architecture/platform-boundaries.yaml` (last updated 2026-03-18)*
