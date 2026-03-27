# Target Platform Architecture

## Purpose

Define the canonical Azure-first target architecture for the platform.

This architecture uses six planes:

1. Governance / control plane
2. Identity / network / security plane
3. Business systems plane
4. Data intelligence plane
5. Agent / AI runtime plane
6. Experience / domain application plane

## Architecture Authority Hierarchy

Design decisions must map to these frameworks in priority order:

1. **Azure SaaS Workload Documentation** — canonical SaaS target-state operating model. Covers: resource organization, identity and access management, compute, networking, data, billing/cost management, governance, DevOps practices, incident management. Use the SaaS assessment tool as the architecture readiness gate. Ref: https://learn.microsoft.com/en-us/azure/architecture/guide/saas/plan-journey-saas
2. **Cloud Adoption Framework (CAF)** — platform foundation, landing zone design, governance baseline. Ref: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/
3. **Repo SSOT + Spec Kit bundles** — implementation authority (this repo's `ssot/`, `spec/`, `infra/ssot/`)
4. **Runtime evidence docs** — live truth (`docs/evidence/`, Azure Resource Graph, CI artifacts)

The SaaS Workload Documentation supersedes generic CAF guidance for SaaS-specific design areas. CAF remains authoritative for landing zone foundations and migration/governance strategy.

## SaaS Workload Design Area Mapping

| SaaS Design Area | Platform Surface | Key Artifacts |
|------------------|-----------------|---------------|
| Resource organization | 5+1 RG model, `rg-ipai-dev-*` | `infra/ssot/azure/resources.yaml` |
| Identity and access management | Entra ID (target), Keycloak (transitional), managed identities | `infra/ssot/security/access_model.yaml` |
| Compute | Azure Container Apps, Databricks | `infra/ssot/azure/service-matrix.yaml` |
| Networking | Azure Front Door, Cloudflare DNS, VNet integration | `infra/dns/subdomain-registry.yaml` |
| Data | Azure PG, Databricks + Unity Catalog, Fabric Mirroring | `data-intelligence/CLAUDE.md` |
| Billing and cost management | Per-tenant metering (planned) | `ssot/governance/platform-strategy-2026.yaml` |
| Governance | Azure Boards, GitHub, SSOT, Azure Policy | `ssot/governance/platform-constitution.yaml` |
| DevOps practices | Azure Pipelines + GitHub Actions, CI gates, evidence packs | `.github/workflows/`, `ssot/governance/operating-model.yaml` |
| Incident management | Azure Monitor, Log Analytics, runbooks | `docs/runbooks/` |

## SaaS Readiness Gate

Platform go-live **cannot be declared SaaS-ready** until the Azure SaaS assessment is run against the platform and the results are recorded in evidence.

| Field | Value |
|-------|-------|
| `assessment_status` | `not_run` |
| `last_run_at` | — |
| `owner` | platform-lead |
| `blocking_gaps` | per-tenant metering design pending; formal SaaS incident playbook pending |

Ref: [SaaS Assessment Tool](https://learn.microsoft.com/en-us/assessments/strategic/saas-702)

---

## Core architecture statement

The platform is an Azure landing-zone SaaS architecture where:

- Odoo on Azure is the transactional business core
- Databricks is the governed data and ML engineering core
- Microsoft Foundry is the agent runtime, tool-governance, and eval core
- Document Intelligence is the document automation core
- Fabric / BI surfaces are the business-consumption layer
- Azure Boards, GitHub, Azure Pipelines, Resource Graph, and repo SSOT form the governance spine

## Plane 1 — Governance / control plane

### Services
- Azure Boards
- GitHub
- Azure Pipelines
- Azure Resource Graph
- Repo SSOT
- runtime evidence docs

### Responsibilities
- planned truth
- code truth
- release truth
- live Azure inventory/drift truth
- intended-state truth
- live operational evidence

## Plane 2 — Identity / network / security plane

### Services
- Microsoft Entra ID
- Managed Identities
- Key Vault
- VNets / private networking
- Azure Front Door / WAF
- Cloudflare DNS
- Azure Policy / RBAC / monitoring foundations

### Responsibilities
- identity and authorization
- secrets and certificates
- network isolation
- ingress and public edge
- shared security and policy controls

## Plane 3 — Business systems plane

### Core
- Odoo on Azure
- Azure Database for PostgreSQL Flexible Server

### Responsibilities
- ERP
- finance and operations workflows
- master data
- transactional truth
- business user execution

## Plane 4 — Data intelligence plane

### Core
- Azure Data Lake Storage
- Delta Lake
- Databricks
- Unity Catalog
- Fabric / BI
- optional ADF / Fabric Data Factory for ingestion and orchestration

### Responsibilities
- ingestion
- medallion/lakehouse processing
- governed analytics
- ML engineering
- semantic/reporting consumption

## Plane 5 — Agent / AI runtime plane

### Core
- Foundry projects
- Foundry Agent Service
- model catalog / leaderboard / routing
- MCP tool catalog
- eval / tracing / runtime promotion

### Responsibilities
- domain agents
- copilots
- planning/judge agents
- tool governance
- model governance
- runtime promotion and evaluation

## Plane 6 — Experience / domain application plane

### Surfaces
- Odoo UI
- domain workbenches
- APIs
- analyst/operator applications
- M365 / Teams / browser-based assistants where applicable

### Responsibilities
- user-facing operations
- domain workflows
- business/analyst/operator experiences

## Document intelligence subsystem

This subsystem spans planes 3, 4, and 5.

### Core
- Azure AI Document Intelligence
- Logic Apps
- Azure Functions
- optional content-understanding and agent integration

### Responsibilities
- document ingestion
- extraction and normalization
- structured output into ERP, data lake, and agent flows

## Tenant model

Use a shared control plane with explicit tenant context and selective data-plane isolation.

### Control plane
- onboarding
- provisioning
- configuration
- entitlement
- billing/metering
- support and operations

### Data plane
- tenant-scoped data access
- tenant-specific reporting
- tenant-specific agent context
- tenant isolation by design and test

## Architecture principles

- control plane and data plane are separate
- no single system owns every truth plane
- Odoo is the transactional system, not the analytics or agent system
- Databricks is the data/ML core, not the ERP
- Foundry is the agent runtime and tool/model governance plane, not the business SoR
- release and inventory evidence are first-class

## Diagram layering

Architecture diagrams must be maintained in three levels:

- overview
- high-level
- low-level

See `docs/architecture/diagram-conventions.md`.

## Non-goals

- not a literal SAP architecture
- not a Databricks-only platform
- not a Foundry-only platform
- not a single monolith
- not one giant shared app with implicit tenancy

---

## Cross-references

- `docs/architecture/plane-boundaries.md` — what each plane owns and must not replace
- `docs/architecture/domain-workbench-map.md` — domain workbenches on top of planes
- `docs/architecture/diagram-conventions.md` — diagram layering and source format
- `ssot/architecture/planes.yaml` — machine-readable plane definitions
- `ssot/architecture/system-context.yaml` — system context model
- `ssot/architecture/tenant-model.yaml` — tenant model definition
- `ssot/architecture/data-flows.yaml` — core data flows between planes
- `ssot/architecture/runtime-authority-map.yaml` — truth-plane authorities
- `docs/architecture/data/ENTERPRISE_DATA_PLATFORM.md` — data platform doctrine
- `docs/architecture/reference-benchmarks.md` — benchmark registry
- `docs/contracts/azure-resource-graph-contract.md` — C-36 live inventory contract

## Verification sources

- [Azure SaaS Workload Documentation](https://learn.microsoft.com/en-us/azure/architecture/guide/saas/plan-journey-saas) — **primary SaaS design authority**
- [Azure Landing Zones](https://learn.microsoft.com/en-us/azure/architecture/landing-zones/landing-zone-deploy)
- [Baseline Foundry Chat Architecture](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/baseline-microsoft-foundry-chat)
- [Modern Analytics with Databricks](https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/azure-databricks-modern-analytics-architecture)
- [Automate PDF Forms Processing](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/architecture/automate-pdf-forms-processing)
- [Multitenancy Checklist](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/checklist)
- [draw.io Azure Diagrams](https://www.drawio.com/blog/azure-diagrams)

---

*Last updated: 2026-03-17*
