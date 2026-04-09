# Odoo on Azure Reference Architecture

> **Created**: 2026-04-05
> **Status**: Active
> **Benchmark**: 4-layer hierarchy — Odoo CE 18 + OCA (application), ACA Well-Architected (runtime), Foundry SDK (AI), AvaTax capability (tax/compliance), SAP-on-Azure (ops maturity only)
> **Scope**: Odoo 18 CE + OCA on Azure — runtime, security, observability, AI, and control plane

## Purpose

Define the canonical Azure-native operating model for running **Odoo 18 CE + OCA** as the ERP system of record, with Azure providing the runtime, security, observability, AI, and operational control-plane layers.

This document uses a **4-layer benchmark model**:

| Layer | Benchmark |
|---|---|
| ERP/application architecture | Odoo CE 18 + OCA + thin-bridge doctrine |
| Cloud runtime | Azure Container Apps Well-Architected guidance |
| AI/copilot runtime | Microsoft Foundry SDK/project model |
| Tax/compliance product ambition | AvaTax-style capability benchmark (PH-first) |
| Ops/governance maturity | SAP-on-Azure seriousness / landing-zone discipline |

SAP-on-Azure is the ops/governance maturity reference only. It governs:
- workload center / control plane discipline
- workload-specific monitoring rigor
- deployment automation framework patterns
- landing-zone separation and environment isolation
- integration playbook completeness

The goal is **not** to emulate SAP product behavior.
The goal is to emulate the **ops/governance maturity of SAP on Azure** for Odoo, while using the correct benchmark per layer for application architecture, runtime, AI, and tax/compliance.

**Ops/Governance Maturity Benchmark (SAP on Azure) — ops-maturity reference only, not application/runtime/AI benchmark**

| SAP on Azure ops pattern | Odoo / IPAI ops equivalent |
|---|---|
| Azure Center for SAP solutions | IPAI workload center / ops dashboard / inventory control plane |
| Azure Monitor for SAP solutions | Odoo-specific monitor pack: web, worker, cron, DB, queue, OCR, copilot |
| SAP deployment automation framework | Bicep/azd-based Odoo deployment automation framework |
| Certified SAP VM/HA guidance | Canonical ACA / Postgres / Front Door / WAF / private networking pattern |
| SAP integrations guidance | Odoo bridge catalog for Entra, Foundry, OCR, M365, AI Search, Service Bus |

---

## Microsoft Benchmark Hierarchy

### Application architecture benchmark (Layer 1)
- **Odoo CE 18 + OCA + thin-bridge doctrine** (primary)
- Use for: all ERP application design, addon taxonomy, parity work, custom module boundaries
- Framing: Config → OCA → Delta (`ipai_*` only for true custom needs)

### Cloud runtime benchmark (Layer 2)
- **Azure Container Apps Well-Architected guidance** (primary)
- Use for: ACA environment design, scaling, revisions, ingress, private networking, resilience
- Gap map: `docs/benchmarks/MICROSOFT_AI_LANDING_ZONES_GAP_MAP.md`

### AI/copilot runtime benchmark (Layer 3)
- **Microsoft Foundry SDK/project model** (primary)
- Use for: agent runtime, model access, orchestration, evaluation, safety, governance
- Gap map: `docs/benchmarks/MICROSOFT_AI_PRODUCTION_ACCELERATOR_GAP_MAP.md`
- Complement: **microsoft/Deploy-Your-AI-Application-In-Production** for end-to-end AI app stack

### Tax/compliance product benchmark (Layer 4)
- **AvaTax-style capability benchmark (PH-first)**
- Use for: tax calculation, jurisdiction-aware rules, BIR compliance, fiscal position quality bar

### Ops/governance maturity benchmark (Layer 5)
- **Microsoft SAP on Azure docs** (ops/governance maturity only — NOT application, runtime, or AI benchmark)
- Use for: landing-zone discipline, environment separation, deployment automation rigor, workload monitoring patterns
- Applies to: `docs/runbooks/`, deployment pipeline patterns, workload-center design, IaC discipline

---

## Scope

This reference architecture covers:

- Odoo 18 CE as the ERP core
- OCA as the default parity and enhancement lane
- Azure-native runtime, security, networking, data, monitoring, and AI bridges
- IPAI thin bridge modules and external services
- Deployment, recovery, and governance patterns

This document does **not** define:
- Odoo Enterprise feature adoption
- Broad custom-module parity work
- Non-Azure primary runtime patterns

---

## Architectural Principles

1. **Odoo CE + OCA is the application baseline.**
   Functional parity should default to CE core and OCA before any custom module work.

2. **Azure is the system/platform layer.**
   Runtime, identity, secrets, observability, network, backup/DR, AI, and integration messaging belong to Azure-native services.

3. **Custom Odoo modules must remain thin.**
   `ipai_*` addons are limited to bridge, connector, adapter, meta-module, or narrowly scoped glue behavior. See `ssot/odoo/custom_module_policy.yaml`.

4. **Heavy AI and orchestration stay outside Odoo.**
   Agent runtime, RAG, OCR pipelines, and model orchestration belong in external Azure services/apps.

5. **Live runtime and IaC must converge.**
   Live inventory is current-state truth; IaC is intended-state truth; drift between them is a governed risk.

6. **Reference architecture beats ad hoc hosting.**
   The objective is a repeatable, supportable Odoo-on-Azure operating model, not a one-off deployment.

---

## Canonical Platform Layers

### 1. ERP Application Layer

This layer contains:
- Odoo 18 CE
- OCA addons
- Thin IPAI bridge/meta addons

Responsibilities:
- Transactional ERP behavior
- Core business workflows
- OCA-based parity/extensions
- Safe exposure of bridge actions into Odoo UI or server methods

Default addon lanes:
- `addons/oca/*` — parity and feature depth
- `addons/ipai/*` — thin bridge/meta modules only
- `addons/local/*` — rare, explicitly approved exceptions

SSOT references:
- `ssot/odoo/ee_gap_matrix.yaml` — EE parity coverage
- `ssot/odoo/custom_module_policy.yaml` — addon boundary rules

### 2. Runtime Layer

Canonical Azure runtime:
- **Azure Container Apps** for:
  - `odoo-web` (HTTP-facing Odoo process)
  - `odoo-worker` (background processing)
  - `odoo-cron` (scheduled jobs)
  - Connector/bridge services
  - OCR and copilot gateway as adjacent services
- **Azure Container Registry** for images
- **Azure Front Door + WAF** for public ingress
- **Private networking** for backend service connectivity

Responsibilities:
- Container hosting
- Rollout/revision control
- Autoscaling
- Ingress policy
- Environment isolation (dev / staging / prod)

SSOT references:
- `ssot/azure/odoo_bridge_matrix.yaml` — bridge: `container_runtime`, `edge_ingress`, `registry`
- `infra/azure/` — Bicep definitions

### 3. Data Layer

Canonical data services:
- **Azure Database for PostgreSQL Flexible Server** — primary transactional database
- **Storage accounts** for auxiliary file/artifact/document storage
- **Private DNS / private connectivity** where applicable

Responsibilities:
- Transactional persistence
- Availability and restore posture (PITR, backup retention)
- Controlled storage of non-database artifacts

SSOT references:
- `ssot/azure/odoo_bridge_matrix.yaml` — bridge: `database`, `backup_and_dr`, `document_storage`

### 4. Security and Identity Layer

Canonical security services:
- **Microsoft Entra ID** — workload and user identity
- **Managed Identity** — service-to-service auth
- **Azure Key Vault** — secret and key management
- **Front Door WAF** — ingress hardening
- **Network isolation controls** — VNet, NSGs, private endpoints

Responsibilities:
- Workload identity
- Secret and key management
- Secure service-to-service access
- Ingress hardening
- Access boundary enforcement

SSOT references:
- `ssot/azure/odoo_bridge_matrix.yaml` — bridge: `identity_and_secrets`, `private_networking`
- `infra/ssot/auth/oidc_clients.yaml`
- `infra/ssot/security/workload_identities.yaml`

### 5. Observability and Operations Layer

Canonical observability services:
- **Azure Monitor** / **Log Analytics** / **Application Insights**
- **Alert rules** (HTTP 5xx, ACA restarts, no-replicas, high-CPU)
- **Action groups** for notification routing
- **Workbooks** for health visualization
- **Optional Grafana** for custom dashboards

Responsibilities:
- Application and platform telemetry
- Health visibility
- Alerting
- Diagnostics
- Controlled production operations

SSOT references:
- `ssot/azure/odoo_bridge_matrix.yaml` — bridge: `observability`

### 6. AI and Document Intelligence Layer

Canonical Azure-native bridges:
- **Azure AI Foundry** / model access plane
- **Azure AI Search** for retrieval/grounding
- **OCR / Document Intelligence** bridge services
- **Optional agent runtime services** outside Odoo

Responsibilities:
- Copilots and assistants
- Knowledge retrieval
- OCR/document extraction
- Agent workflows
- Model/service abstraction

SSOT references:
- `ssot/azure/odoo_bridge_matrix.yaml` — bridges: `ai_foundry_gateway`, `ai_retrieval`, `document_ocr`
- `ssot/integrations/microsoft_skills.yaml`, `microsoft_azure_skills.yaml`

### 7. Control Plane and Governance Layer

Canonical control plane surfaces:
- **SSOT files** (`ssot/`) — intended-state registry
- **IaC** (`infra/azure/`) — Bicep/Terraform
- **CI/CD** — Azure DevOps + GitHub Actions
- **Architecture/runbooks** (`docs/architecture/`, `docs/runbooks/`)
- **Azure Boards / planning** — portfolio backlog
- **Runtime reconciliation** — drift registry

Responsibilities:
- Intended-state control
- Release governance
- Environment reproducibility
- Reconciliation of live estate vs source-controlled design

SSOT references:
- `docs/architecture/IPAI_PLATFORM_ANALYSIS.md` — assessment and risk register
- `docs/planning/IPAI_AZURE_BOARDS_BACKLOG.md` — portfolio backlog
- `ssot/governance/platform-constitution.yaml`

---

## Odoo Center on Azure

### Objective

Provide the Odoo equivalent of a workload center/control-plane view similar in spirit to Azure Center for SAP solutions.

### Required Capabilities

- Inventory of Odoo environments (dev, staging, prod)
- Runtime topology (web, worker, cron, connectors, gateways)
- Service/component mapping
- Database and storage mapping
- Deployment state visibility
- Drift and exception visibility
- Environment lifecycle tracking
- Health summary and blocker summary

### Recommended Implementation Surfaces

- Ops dashboard / workload center app (`ipai-ops-dashboard`, `ipai-workload-center`)
- Azure workbook(s) (Odoo Platform Health)
- SSOT registry (`ssot/azure/`, `ssot/odoo/`)
- Environment manifest(s) (`config/ENVIRONMENTS.md`, `config/{dev,staging,prod}/`)
- Drift exception registry (IaC reconciliation output)

### Minimum Managed Objects

| Object | Example Resource |
|---|---|
| Web app | `ipai-odoo-dev-web` |
| Worker | `ipai-odoo-dev-worker` |
| Cron | `ipai-odoo-dev-cron` |
| Connector services | `ipai-odoo-connector` |
| OCR services | `ipai-ocr-dev` |
| Copilot/agent gateways | `ipai-copilot-gateway` |
| PostgreSQL | `pg-ipai-odoo` |
| Ingress/WAF | `afd-ipai-dev`, `wafipaidev` |
| Identity/secrets | `kv-ipai-dev`, Entra app registrations |
| Alert/workbook surfaces | `alert-*`, `ag-ipai-platform`, Odoo Platform Health workbook |

---

## Azure Monitor for Odoo

### Objective

Provide a workload-specific monitoring pack for Odoo comparable in role to Azure Monitor for SAP solutions.

### Minimum Monitoring Domains

**Application health:**
- `/web/health` endpoint reachability
- Login route reachability
- Request latency (p50, p95, p99)
- Error rate (5xx, 4xx)
- Worker and cron liveness

**Runtime health:**
- ACA restart rate (`alert-aca-restarts`)
- Replica counts (`alert-aca-no-replicas`)
- CPU and memory pressure (`alert-aca-high-cpu`)
- Revision drift (active vs latest)
- Image/version alignment across web, worker, cron

**Data health:**
- PostgreSQL availability
- Connection errors and pool exhaustion
- Storage utilization
- Backup/restore evidence
- PITR window verification

**Odoo-specific health:**
- Cron backlog (scheduled actions pending)
- Queue backlog (`queue_job` if active)
- Mail or notification failures
- Connector failure rate
- Long-running jobs
- Document/OCR processing failures

**AI bridge health:**
- Copilot gateway availability
- Retrieval/index freshness (AI Search)
- OCR job latency/failure rate
- Model/provider error rate (Foundry)

### Minimum Outputs

- Health workbook (Odoo Platform Health)
- Environment summary dashboard
- Action-group-backed alerts (4 deployed: HTTP 5xx, ACA restarts, no-replicas, high-CPU)
- Incident-ready logs and traces (Application Insights + Log Analytics)

---

## Odoo on Azure Deployment Automation Framework

### Objective

Provide the Odoo equivalent of SAP on Azure deployment automation: repeatable, source-controlled environment creation and promotion.

### Canonical Automation Responsibilities

- Environment bootstrap (new environment from zero)
- Network and ingress provisioning (VNet, Front Door, WAF)
- PostgreSQL provisioning (Flexible Server, backup, private endpoint)
- ACA environment and apps (web, worker, cron, sidecars)
- Container registry binding
- Identity and Key Vault wiring (managed identity, secret refs)
- Monitor/alerts/workbooks deployment
- DNS/routing configuration
- Release and rollback workflow

### Reference Repo Boundaries

| Path | Owns |
|---|---|
| `infra/azure/` | Bicep modules and parameter files |
| `.azure/` and `azure.yaml` | azd configuration (if adopted) |
| `.azdo/` | Azure DevOps pipeline definitions |
| `.github/workflows/` | GitHub Actions CI/CD |
| `ssot/azure/*` | Intended-state SSOT for Azure resources |
| `docs/architecture/*` | Architecture decisions and reference patterns |
| `scripts/` | Deterministic helper flows only |

### Governing Rule

Any retained production-significant resource must be:
- Defined in IaC, **or**
- Registered in an approved exception/drift registry

---

## Supported Runtime Reference Pattern

### Canonical Pattern

```
Internet
  └→ Azure Front Door + WAF
       └→ Azure Container Apps Environment
            ├→ odoo-web        (port 8069, public ingress)
            ├→ odoo-worker     (internal, no ingress)
            ├→ odoo-cron       (internal, no ingress)
            ├→ copilot-gateway (internal, port 8088)
            ├→ ocr-service     (internal)
            └→ connector       (internal)
       └→ PostgreSQL Flexible Server (private endpoint)
       └→ Key Vault (private endpoint)
       └→ Storage Account(s)
       └→ Application Insights + Log Analytics
       └→ Alert Rules + Action Groups
```

### Preferred Service Decomposition

- Odoo web process isolated from worker and cron
- OCR and AI gateways as separate services (not in-Odoo)
- External connector services outside core Odoo container
- Build/release automation separated from runtime

### Anti-Patterns

- Monolithic "everything in one container"
- Platform logic embedded in Odoo addons
- Unmanaged portal-created production resources without reconciliation
- Direct public exposure of backend-only services
- AI runtime implemented as a fat custom addon

---

## Odoo Integration Playbooks on Azure

### Identity and Secrets

**Use:**
- Entra ID for user and workload identity
- Managed Identity for service-to-service auth
- Key Vault for secret/key/cert management

**Do not:**
- Hard-code secrets in addons or config
- Embed long-lived credentials in runtime config where managed identity is viable
- Use basic login when Entra OIDC is available

### OCR / Document Intelligence

**Use:**
- External OCR/document-intelligence service (Azure Document Intelligence or Odoo Extract API)
- Thin Odoo connector surface for status/result sync
- Async processing with webhook or polling

**Do not:**
- Build document intelligence engines inside Odoo addons
- Embed CV/ML models in the Odoo process

### AI / Agents / Copilot

**Use:**
- External Azure agent/runtime apps (copilot-gateway, agent-platform)
- AI Search for retrieval grounding
- Foundry/model gateway patterns
- Thin Odoo action and result surfaces

**Do not:**
- Host the primary agent runtime inside Odoo
- Embed LLM chains or prompt templates in addons
- Add MCP server logic to Odoo controllers

### Messaging / Decoupled Integration

**Use:**
- External messaging/event bridge (Service Bus) where durable decoupling is required
- `queue_job` (OCA) for in-app deferred work only
- n8n for webhook-driven automation workflows

**Do not:**
- Build a full messaging bus inside Odoo
- Use Odoo cron as a substitute for durable messaging

### Reporting / Operational Visibility

**Use:**
- Azure Monitor / workbooks / dashboards for ops visibility
- Odoo and OCA reporting (`account_financial_report`, `mis_builder`) for ERP/business needs
- Power BI (primary) or Superset (supplemental) for platform-wide reporting

**Do not:**
- Build operational dashboards as Odoo views
- Duplicate Azure Monitor data inside Odoo

---

## Custom Module Policy Linkage

This reference architecture depends on the custom-module boundary defined in `ssot/odoo/custom_module_policy.yaml`.

**Allowed by default:**
- Thin bridge modules (API call, config, result storage)
- Thin connector modules (webhook receiver, status sync)
- Dependency-only meta-modules
- Narrow business-specific glue when OCA/config/bridge is insufficient

**Disallowed by default:**
- Large EE-parity custom modules
- Platform/runtime logic inside `addons/`
- Agent/orchestration/RAG/OCR systems implemented as Odoo modules

---

## Reference Architecture Mapping to Current IPAI Baseline

| Layer | Current State | Maturity |
|---|---|---|
| ERP Application | Odoo 18 CE + 76 OCA modules + 69 ipai_* addons | Operational |
| Runtime | 22 ACA apps + 1 job across 2 environments | Operational, drift present |
| Data | PG Flexible Server (General Purpose), 2 storage accounts | Operational |
| Security/Identity | Key Vault present; Entra registered but not enforced | Partial |
| Observability | App Insights, Log Analytics, 4 alerts, workbook, Grafana | Operational |
| AI/Document Intel | Foundry project + copilot gateway; AI Search missing | Partial |
| Control Plane | SSOT, IaC (Bicep), CI/CD, architecture docs | Governance-drifted |

**Current readiness interpretation:**
- Runtime controls are live and sufficient for controlled production
- Dominant residual risk is governance drift, not absence of baseline infrastructure
- Primary maturity work is convergence of live estate, automation, and control-plane quality

See `docs/architecture/IPAI_PLATFORM_ANALYSIS.md` for detailed assessment scores and risk register.

---

## Exit Criteria for "Odoo on Azure Mature Baseline"

The platform should only be considered architecturally mature when all of the following are true:

- [ ] Runtime topology is standardized and documented
- [ ] Production-significant resources are reconciled into IaC or approved exceptions
- [ ] Odoo-specific monitoring and alerts are live and actionable
- [ ] Restore/recovery posture is evidenced
- [ ] Identity and secrets flows are explicit and keyless where appropriate
- [ ] AI/OCR bridges are externalized and observable
- [ ] Custom addons remain within thin bridge/meta/glue policy
- [ ] Deployment and rollback are repeatable from repo-controlled artifacts

---

## Benchmark Extensions

This reference architecture uses three additional Microsoft benchmarks beyond SAP on Azure:

| Benchmark | IPAI Doc Family | Canonical Location | Role |
|---|---|---|---|
| Microsoft Foundry | AI Platform | `platform/docs/ai-platform/` | Model access, orchestration, evaluation, safety, governance |
| AI-led SDLC (Azure + GitHub) | Engineering | `agents/docs/engineering/` | Spec-first delivery, coding agents, quality agents, CI/CD, SRE loops |
| Databricks + Fabric | Data Intelligence | `data-intelligence/docs/` | Lakehouse, governance, ingestion, BI, AI-ready data |

Each benchmark family has:
- A **canonical full page** in its subsystem directory (platform, agents, or data-intelligence)
- A **thin index page** in `docs/odoo-on-azure/` for cross-repo discoverability
- A **benchmark parity table** tracking current status against the reference

See `docs/odoo-on-azure/reference/doc-authority.md` for the full documentation ownership model.

---

## Azure Architecture Center and SAP on Azure alignment

This reference architecture uses:

- Azure Architecture Center as the benchmark for reference-pattern alignment
- SAP on Azure offerings as the benchmark for workload-operating-model taxonomy

Current implications:

- Azure Container Apps remains the default runtime choice for the current workload profile over AKS
- Databricks for engineering/transformation and Fabric for mirroring/serving remains the preferred analytics doctrine
- workload-team vs platform-team ownership boundaries must remain explicit
- Odoo-on-Azure documentation should continue to mirror the operational family structure used by SAP on Azure:
  - workload center
  - deployment automation
  - monitoring
  - integrations
  - backup / disaster recovery
  - analytics
  - DevOps / IaC / governance

This is directly consistent with the SAP-on-Azure service families Microsoft exposes, including Azure Center for SAP solutions, deployment automation, Azure Monitor for SAP solutions, integrations with Microsoft services, backup and site recovery, analytics services, Azure DevOps, IaC, and Azure Policy.

---

## Non-Goals

This reference architecture does not attempt to:
- Make Odoo identical to SAP
- Recreate Azure's SAP-specific product surfaces literally
- Justify broad custom-module development
- Replace OCA with bespoke IPAI business modules
- Embed full AI platform behavior inside Odoo

---

## Summary

The strategic target is:

- **OCA** for application parity
- **Azure** for platform/system parity
- **IPAI control-plane** (docs + IaC + monitoring + automation) for operating-model maturity

This is the Odoo-on-Azure equivalent of what SAP on Azure receives from Microsoft as a first-party workload operating model.

---

*Generated: 2026-04-05 | Source: SAP on Azure operating-model benchmark | Version: 1.0*
