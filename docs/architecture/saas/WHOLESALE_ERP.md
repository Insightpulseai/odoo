# Wholesale SaaS ERP on Azure — Architecture Rationale

> **Role:** Long-form rationale and deep-research synthesis.
> **Not canonical target doctrine** — that is `../target-state/PLATFORM.md`.
> **Not cross-domain topology** — that is `../target-state/UNIFIED.md`.
>
> Cross-references:
> - `../target-state/PLATFORM.md` (canonical target doctrine)
> - `../target-state/UNIFIED.md` (cross-domain topology)
> - `ssot/architecture/platform-boundaries.yaml` (machine-readable boundaries)
> - `ssot/architecture/data-flows.yaml` (machine-readable data flows)
> - `spec/wholesale-saas-erp-azure/` (spec bundle: constitution, PRD, plan, tasks)

---

## 1. Executive Summary

InsightPulse AI is a **six-plane Azure-first architecture** for wholesale/distribution ERP. Within that model, three systems form the operational core:

- **Odoo CE 19** — transactional system of record
- **Azure Databricks + ADLS/Delta + Unity Catalog** — governed data intelligence core
- **Microsoft Foundry** — agent factory and hosted agent runtime

This document explains *why* these architectural decisions were made, the trade-offs considered, and the implementation interpretation. It is the research synthesis — not the operational doctrine.

---

## 2. Canonical Decisions

### 2.1 Six-Plane Architecture (not three-plane)

The platform is organized into six architectural planes, not three systems. The three-system operational core (Odoo/Databricks/Foundry) lives *within* the six-plane model:

| # | Plane | Scope |
| --- | --- | --- |
| 1 | Governance / Control | Planning, code, release, policy enforcement |
| 2 | Identity / Network / Security | Auth, edge routing, secrets, API governance |
| 3 | Business Systems | Transactional ERP and workflow automation |
| 4 | Data Intelligence | Governed lakehouse, ML, feature store, BI serving |
| 5 | Agent / AI Runtime | Agent factory, model hosting, tracing, evaluations |
| 6 | Experience / Domain Applications | User-facing surfaces consuming platform services |

**Why six, not three?** The three-system framing (SoR/SoI/SoA) is useful shorthand for the compute core but omits governance, identity, and experience — planes that carry significant architectural decisions and operational surface area. A three-plane model leaves those decisions implicit, which causes drift.

### 2.2 Truth Authority as Separate Model

Plane membership describes *where* a system sits architecturally. Truth authority describes *what* each system is the operational source of truth for. These must be documented separately.

| Authority | System |
| --- | --- |
| Planned truth | Azure Boards |
| Code truth | GitHub |
| Release truth | Azure Pipelines |
| Live inventory truth | Azure Resource Graph |
| Agent/runtime truth | Microsoft Foundry |
| Intended-state truth | Repo SSOT (`ssot/`) |

**Why separate?** Without explicit truth-authority mapping, teams default to treating the loudest system as authoritative. Azure Boards becomes "truth" for both planning and release status; GitHub becomes "truth" for both code and deployment state. Explicit separation prevents authority creep.

### 2.3 Databricks is Canonical (Not Optional)

Azure Databricks + ADLS/Delta + Unity Catalog is the canonical data intelligence plane. It is not "optional" or "only for complex transforms."

**Why?** Analytical workloads must never execute within the Odoo PostgreSQL instance. Even simple reporting queries against live Odoo data degrade transactional performance. A governed lakehouse with medallion architecture (bronze/silver/gold) provides the separation needed for a lean team to serve both transactional and analytical needs without infrastructure contention.

### 2.4 Foundry is Agent Runtime (Not Just Compute)

Microsoft Foundry is the agent factory, hosted runtime, tracing system, evaluation pipeline, and monitoring surface. It is not "compute only."

**Why?** Treating Foundry as generic compute ignores its operational surface area: agent lifecycle management, model/tool governance, prompt tracing, and evaluation pipelines. These capabilities are load-bearing — without them, agents become unmonitored black boxes.

### 2.5 APIM is a Boundary (Not a Platform)

Azure API Management is the governed ingress/egress and policy boundary. It is not the system of record, not the agent runtime, and not a control plane.

**Why?** API gateways have a tendency to become accidental control planes when teams route too many concerns through them. Explicitly constraining APIM to ingress/egress policy prevents drift toward gateway-as-platform anti-patterns.

### 2.6 OCA-First Module Policy

CE + OCA is the primary EE parity vehicle. `ipai_*` modules are thin bridge/meta/integration glue only — not a general business capability lane.

**Why?** Custom module sprawl increases maintenance burden faster than it increases capability. OCA modules are community-maintained, tested across deployments, and follow established quality gates. `ipai_*` should only exist where no OCA module can serve the need.

---

## 3. Architecture by Plane

### 3.1 Governance / Control

- **Azure Boards**: Epic/Feature/Story hierarchy for work planning. Planned truth.
- **GitHub**: All source code, PRs, branch policies, CODEOWNERS. Code truth.
- **Azure Pipelines**: CI/CD for all environments. Release truth. No deployments bypass Pipelines.
- **Azure Policy**: Guardrails for resource compliance. Prevents manual/unmanaged provisioning.
- **Azure Resource Graph**: Live inventory queries. Drift detection against intended state.

### 3.2 Identity / Network / Security

- **Microsoft Entra ID**: Canonical identity plane. Workforce SSO, B2B, managed identities.
- **Azure Front Door**: TLS termination, WAF, hostname routing, origin shielding.
- **Azure Key Vault**: All secrets. Runtime binding via managed identity. Never in git or env vars.
- **Azure API Management**: Governed ingress/egress for all cross-tenant and agent-to-Odoo calls.

### 3.3 Business Systems

- **Odoo CE 19**: System of Record. Accounting, invoicing, sales, purchasing, inventory, HR, BIR compliance.
- **n8n**: Workflow automation, event routing, connector glue. No data ownership.
- **Module policy**: Config → OCA → Delta (`ipai_*` only for truly custom integration needs).

### 3.4 Data Intelligence

- **Azure Databricks**: Compute for transforms, ML, feature serving. Canonical — not optional.
- **ADLS Gen2**: Storage for medallion lakehouse (bronze/silver/gold).
- **Unity Catalog**: Governance, lineage, access control across the lakehouse.
- **Hard boundary**: Databricks never writes directly to Odoo PostgreSQL. ADLS is analytical only.

### 3.5 Agent / AI Runtime

- **Microsoft Foundry**: Agent lifecycle, model/tool governance, tracing, evaluations, monitoring.
- **Azure OpenAI**: Model hosting (GPT-4, embeddings).
- **Azure AI Document Intelligence**: OCR extraction for vendor bills and purchase orders.
- **Hard boundary**: All agent-to-Odoo calls go through APIM. No direct database access.

### 3.6 Experience / Domain Applications

- **Ops Console**: Internal operations dashboard.
- **BI surfaces**: Tableau Cloud / Fabric consuming ADLS gold layer.
- **Copilot UIs**: Foundry-backed conversational interfaces.
- **Slack integrations**: ChatOps, notifications, alerts.

---

## 4. Tenancy Doctrine

### 4.1 Default Tier

- **App model**: Shared runtime farm (single ACA environment serving all tenants).
- **Data model**: Database-per-tenant (each tenant gets a dedicated PostgreSQL database).
- **Rationale**: Keeps infrastructure costs feasible for a lean team while maintaining strong data isolation.

### 4.2 Premium / Regulated Tier

- **App model**: Deployment stamp per tenant (dedicated ACA environment).
- **Data model**: Dedicated database.
- **Rationale**: Required for regulated industries or enterprise customers demanding full isolation.

### 4.3 Migration Requirement

Promotion from shared to stamped deployment **must be fully automated**. No manual infrastructure provisioning for tenant tier upgrades.

**Why?** Manual tier upgrades create operational bottlenecks and risk downtime. If the promotion path is not automated, the lean team cannot scale the tenant onboarding process.

---

## 5. Repo Ownership Mapping

| Repo/Path | Plane / Role |
| --- | --- |
| `odoo` | Business Systems |
| `platform` | Governance / Control plane applications |
| `data-intelligence` | Data Intelligence |
| `agent-platform` | Agent / AI Runtime |
| `web` | Experience / Domain Applications |
| `infra` | Identity / Network / Security substrate + IaC |
| `automations` | Orchestration assets (n8n workflows) |
| `agents` | Personas / skills / evals |
| `design` | Design assets / tokens |
| `ssot/` | Intended-state truth artifacts within each owning repo |
| `addons/ipai/` | **Thin bridge/meta only** — not general parity/business lane |
| `addons/oca/` | Primary business capability lane (OCA-first policy) |

---

## 6. DevEx / SDLC Model

- **Local development**: VS Code `.devcontainer` environments. Guarantees identical toolchains.
- **Source control**: GitHub (code truth).
- **Planning**: Azure Boards (planned truth).
- **CI/CD**: Azure Pipelines (release truth). No deployments bypass Pipelines.
- **Agent development**: Foundry workspace with tracing and eval pipelines.
- **Data development**: Databricks notebooks with Unity Catalog governance.

---

## 7. Risks / Anti-Patterns

| Anti-Pattern | Risk | Mitigation |
| --- | --- | --- |
| APIM as control plane | Gateway accumulates business logic, becomes bottleneck | Constrain APIM to ingress/egress policy only |
| Custom module sprawl | Maintenance burden grows faster than capability | OCA-first policy; `ipai_*` for bridge/meta only |
| Databricks as optional | Analytical queries on Odoo PostgreSQL degrade transactions | Databricks is canonical, not optional |
| Foundry as compute-only | Agents become unmonitored black boxes | Foundry owns lifecycle, tracing, evals |
| Manual tenant promotion | Operational bottleneck at scale | Automated shared-to-stamp promotion required |
| Competing canonical docs | Architecture drift across documents | Clear doc hierarchy: TARGET_STATE > UNIFIED > this doc |

---

## 8. Phased Roadmap

| Phase | Focus | Key Deliverables |
| --- | --- | --- |
| 0 | Foundations | Devcontainers, Azure DevOps, landing zones, SSOT YAML |
| 1 | Transactional Core | Odoo CE 19 on ACA, PostgreSQL Flex, Front Door, Entra SSO |
| 2 | Intelligence Layer | Databricks, ADLS/Delta, Unity Catalog, medallion pipelines |
| 3 | Agent Runtime | Foundry workspace, Document Intelligence, APIM-governed tool calls |
| 4 | Enterprise Hardening | DR testing, tenant promotion automation, drift detection |

---

## 9. Benchmark References vs Canonical Implementation

This document synthesizes research from Azure Well-Architected Framework, Microsoft SaaS reference architectures, and Odoo deployment patterns. The canonical implementation diverges from generic references in these ways:

- **Lean team assumption**: Solo developer + AI agents, not a dedicated platform team. This drives the shared-runtime default and automation requirements.
- **OCA-first**: Unlike typical Odoo customization patterns, EE parity is achieved through curated OCA modules rather than custom development.
- **Foundry as production runtime**: Most references treat AI as an add-on. Here, Foundry is a first-class architectural plane with tracing and eval requirements.
- **Six-plane model**: Standard Azure landing zone patterns use a simpler subscription/management-group hierarchy. The six-plane model adds explicit governance and experience planes.

---

*Last updated: 2026-03-18*
