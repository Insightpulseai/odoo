# Upstream Landing Matrix

## Status
Proposed

## Purpose
Define where cloned, forked, consumed, and adapted upstream assets should land in the current Insightpulseai GitHub organization once adoption work is complete.

This matrix is grounded in the current org structure and current delivery posture:
- 17 active repos in the Insightpulseai org, including `odoo`, `agent-platform`, `platform`, `automations`, `infra`, `.github`, `docs`, `data-intelligence`, `web`, and `agents`.
- Wave-01 delivery remains staged across R1–R4, with first customer-usable Finance slice targeted for **2026-07-14** and GA / partner-shippable target for **2026-12-15**.
- Azure BOM for the scoped sponsorship snapshot currently validates to **24 total resources**, with remaining reconciliation needed for one missing Action Group and one extra managed certificate.

---

## Core doctrine

1. Do not create new top-level org repos unless an ownership boundary truly requires it.
2. Commodity capability should land in the repo that owns the plane, not in a new repo.
3. Use upstream directly where possible.
4. Clone as reference when harvesting patterns or docs.
5. Fork only when a long-lived internal derivative is justified.
6. Build only the thin IPAI-specific delta:
   - adapters
   - policies
   - composition
   - tests
   - SSOT
   - release governance

---

## Current org target repos

| Repo | Canonical role |
|---|---|
| `odoo` | Transaction plane: Odoo CE + OCA + thin `ipai_*` transactional adapters |
| `agent-platform` | Agent plane runtime, orchestration, retrieval, tool wiring, operator/assistant backend |
| `platform` | Control-plane contracts, SSOT-backed service contracts, shared metadata, integration schemas |
| `automations` | Scheduled jobs, sync runners, batch tasks, operational runbooks |
| `infra` | Azure-first IaC, identity, Key Vault, policy, networking, deployment patterns |
| `.github` | Reusable workflows, CI/CD gates, policy automation, validation workflows |
| `docs` | Architecture, strategy, governance, runbooks, evidence, marketplace and partner operations docs |
| `data-intelligence` | Databricks/Fabric/Power BI-aligned data engineering, telemetry, reporting, semantic-serving prep |
| `web` | Browser-facing sites and product UIs only |
| `agents` | Agent personas, skills, judges, evals, metadata, registries, prompt contracts |

---

## Landing rules by repo

### 1. `odoo`
**Own here**
- upstream `odoo/odoo` tracking
- selected OCA repos/modules
- thin transactional `ipai_*` adapters
- Finance parity composition
- Project Operations parity composition
- booking/resource modules and website-to-transaction glue

**Typical upstream inputs**
- `odoo/odoo`
- selected `OCA/*` repos
- D365 Finance functional references
- D365 Project Operations functional references
- Odoo industry workflow references

**Do not land here**
- Partner Center automation
- generic agent runtime
- Azure infra policy
- Marketplace publishing clients
- Google Workspace admin tooling

---

### 2. `agent-platform`
**Own here**
- `microsoft/agent-framework` runtime adoption
- Pulser orchestration layer
- finance-agent workflow tools
- guarded action wrappers
- approval and policy enforcement
- operator/assistant backend surfaces
- external task tools for Odoo, Partner Center, Google Workspace, Azure

**Typical upstream inputs**
- `microsoft/agent-framework`
- `anthropics/financial-services-plugins`
- `Azure-Samples/get-started-with-ai-agents`
- `Azure-Samples/openai-chat-app-entra-auth-builtin`
- curated architecture references such as awesome-list style repos

**Do not land here**
- ERP source-of-record logic
- Odoo model/business logic
- reporting semantics
- Azure policy/IaC

---

### 3. `platform`
**Own here**
- Partner Center API contracts and schemas
- Marketplace offer/submission models
- shared integration schemas
- support-request models
- control-plane service contracts
- machine-readable metadata and internal API boundaries

**Typical upstream inputs**
- Partner Center SDK/sample repos
- Marketplace submission/API docs and schemas
- Google Workspace API/client patterns
- Azure Search / RAG control-plane patterns

**Do not land here**
- scheduled jobs
- deployment IaC
- public UIs
- Odoo addons

---

### 4. `automations`
**Own here**
- scheduled polling jobs
- sync runners
- support-ticket sync
- billing/export pulls
- operational scripts and runbooks
- non-interactive background jobs

**Typical upstream inputs**
- Azure Pipelines reference repos
- Google Workspace CLI usage patterns
- Partner Center Labs operational samples
- export/download examples

**Do not land here**
- canonical schemas
- policy definitions
- app backends
- ERP logic

---

### 5. `infra`
**Own here**
- Azure IaC
- app registrations
- Key Vault references
- managed identities / service principals
- policy assignments
- tag enforcement
- Front Door / ACA / network / security composition
- deployment topologies and blue/green patterns

**Typical upstream inputs**
- AVM/Bicep modules
- `Azure-Samples/azure-container-apps-blue-green-with-azure-pipelines`
- `Azure/PSRule.Rules.Azure`
- `Azure/PSRule-pipelines`

**Do not land here**
- business workflows
- Partner Center narratives
- finance-agent policies
- UI code

---

### 6. `.github`
**Own here**
- reusable workflows
- CI validation
- release gates
- spec compliance
- tag/audit drift checks
- Partner Center validate/sync workflows
- deployment approval jobs

**Typical upstream inputs**
- `microsoft/azure-pipelines-yaml`
- spec-kit CI guard patterns
- PSRule validation-stage patterns
- GitHub workflow references

**Do not land here**
- product code
- Odoo modules
- long-lived service clients

---

### 7. `docs`
**Own here**
- adoption registers
- reference-adaptation notes
- Partner Center operations docs
- ISV Success briefs
- Marketplace runbooks
- delivery plans
- benchmark/parity docs
- evidence packs
- architecture doctrine
- landing matrices

**Typical upstream inputs**
- D365 docs repos
- FastTrack implementation assets
- MB-310 lab materials
- Odoo industry pages
- curated architecture reading lists

**Do not land here**
- executable runtime logic
- secrets
- deployable service code

---

### 8. `data-intelligence`
**Own here**
- Databricks bundle adaptations
- Power BI semantic prep
- finance telemetry interpretation
- reporting extracts
- governed datasets and models

**Typical upstream inputs**
- `databricks/bundle-examples`
- `microsoft/ISM-Telemetry-for-Finance-and-Operations`

**Do not land here**
- transactional logic
- Marketplace publishing workflows
- generic agent runtime

---

### 9. `web`
**Own here**
- public sites
- docs sites
- browser-facing product apps
- operator UIs only when they are truly web surfaces

**Typical upstream inputs**
- web UI examples
- authenticated chat/admin app references

**Do not land here**
- core Partner Center automation contracts
- infra logic
- scheduled jobs

---

### 10. `agents`
**Own here**
- personas
- skills
- judges
- evals
- metadata
- prompt contracts
- registries

**Typical upstream inputs**
- finance plugin packaging ideas
- skill decomposition patterns
- command naming patterns

**Do not land here**
- runtime orchestration engine
- API clients
- deployment logic

---

## Upstream-to-repo landing matrix

| Upstream / source type | Mode | Canonical landing repo | Secondary repo(s) | Notes |
|---|---|---|---|---|
| `odoo/odoo` | consume-directly / upstream tracking | `odoo` | `docs` | Track upstream; do not maintain a divergence-heavy fork |
| Selected `OCA/*` repos | clone-reference / selective vendor | `odoo` | `docs` | Pull only justified modules/repos |
| `microsoft/agent-framework` | consume-directly | `agent-platform` | `docs`, `.github` | Canonical agent runtime substrate |
| `anthropics/financial-services-plugins` | clone-reference | `agent-platform` | `agents`, `docs` | Harvest packaging patterns only |
| `Azure-Samples/get-started-with-ai-agents` | clone-reference | `agent-platform` | `docs` | Reference for agent bootstrap and grounding patterns |
| `Azure-Samples/openai-chat-app-entra-auth-builtin` | clone-reference | `agent-platform` | `web`, `docs` | Internal operator/authenticated assistant patterns |
| Partner Center SDK/sample repos | clone-reference | `platform` | `automations`, `docs` | Contracts first, jobs second |
| Google Workspace CLI / tooling | consume-directly | `automations` | `platform`, `docs` | Use as tooling/dependency, not fork |
| AVM/Bicep modules | consume-directly | `infra` | `.github`, `docs` | Composition-owned, modules not forked |
| Azure Pipelines reference repos | clone-reference | `infra` | `.github`, `automations`, `docs` | Deployment patterns and CI/CD examples |
| PSRule repos | consume-directly | `infra` | `.github` | Policy validation and pipeline enforcement |
| D365 Finance docs / FastTrack / MB-310 | clone-reference | `docs` | `odoo`, `data-intelligence` | Functional parity authority and UAT references |
| Project Operations references | clone-reference | `docs` | `odoo` | Services-ERP workflow mapping only |
| Databricks bundle examples | clone-reference | `data-intelligence` | `infra`, `.github` | Data-deploy patterns only |
| Finance telemetry references | clone-reference | `data-intelligence` | `docs` | KQL/reporting/observability patterns |
| Odoo industry pages | reference-only | `docs` | `odoo`, `web` | Workflow and packaging reference only |
| Awesome-list / research repos | clone-reference / bookmark-reference | `docs` | `agent-platform` | Reading and comparison only |

---

## What should not create new repos

The following should land inside existing repos, not as new top-level org repos:
- Partner Center automation
- Marketplace offer tooling
- Azure policy/tagging enforcement
- Pulser orchestration runtime
- D365 parity references
- Google Workspace integration glue
- delivery/release governance
- Odoo booking adaptation
- finance-agent tool wrappers

---

## Shipping posture

### Current honest state
Use this statement externally and internally:

```text
Azure substrate: YES
Functional F&O-equivalent OS: NOT YET
Go-live-ready: NOT YET
```

This remains the correct canonical status statement.

### What is already live
- Odoo 18 CE on Azure Container Apps
- Front Door + WAF + custom domain
- Pulser Odoo Copilot
- PrismaLab gateway
- Zoho mail integration
- Spec Kit pinned and active

### Validated infrastructure status
- current scoped Azure BOM total validates at **24 resources**
- subscription-level canonical tags are cleaned and corrected
- resource-level enforcement and one BOM reconciliation pass are still pending

### Delivery milestones

| Milestone | Target | Meaning |
|---|---|---|
| Internal/live platform | now | substrate and internal surfaces available |
| First customer-usable Wave-01 slice | 2026-07-14 | GL + AP + AR + Finance Reconciliation Agent v0 + basic Project Ops target |
| PH BIR / hardening milestone | 2026-10-14 | production hardening + BIR pack + solution kit milestone |
| GA / partner-shippable | 2026-12-15 | 80% parity target, Wave-01 epics closed, partner-ready state |

Source basis for these dates is the current R1–R4 cadence and delivery framing already recorded on the active branch.

---

## Practical ship-readiness read

### Platform / infrastructure
Approximately **75–85%** complete:
- live substrate exists
- tagging baseline cleaned
- BOM total validated
- policy/resource-level enforcement still incomplete

### Product parity
Approximately **25–40%** complete:
- doctrine, backlog, SSOT, spec bundles, benchmark references are strong
- actual Wave-01 business implementation still remains

### Commercial ship readiness
- ready for internal/demo use now
- not ready for GA now
- first real customer-usable slice targeted for R2
- partner-shippable target remains December 2026

---

## Final rule

The current org already has the right top-level repositories.
The work now is to land upstream-derived assets into the correct existing repos, not to create new top-level homes for each capability.

---

## Anchors

- **Adoption register (doc):** [`repo-adoption-register.md`](repo-adoption-register.md)
- **Adoption register (SSOT):** [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml)
- **Engineering doctrine:** `CLAUDE.md` § Engineering Execution Doctrine + Cross-Repo Invariant #23
- **Self-hosted Azure integrations:** [`odoo-integrations-selfhosted-azure.md`](odoo-integrations-selfhosted-azure.md)
- **Delivery position:** memory `project_delivery_position_20260414.md`
- **Current state:** memory `project_current_state_20260414.md`
- **Tag policy (canonical):** [`ssot/azure/tag-policy.yaml`](../../ssot/azure/tag-policy.yaml)
- **BOM:** [`ssot/azure/bom.yaml`](../../ssot/azure/bom.yaml)
