# Upstream Landing Matrix

> **Purpose:** Define which upstream repos / patterns / clones land in which IPAI repo (or repo subtree). No new top-level org repos required.
>
> **Status:** Canonical
> **Date:** 2026-04-14
> **Anchors:** [`docs/architecture/repo-adoption-register.md`](repo-adoption-register.md), [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml), `CLAUDE.md` § Engineering Execution Doctrine

---

## 1. Per-repo landing rules

### A. `odoo` (this repo)

**Land here**
- `odoo/odoo` upstream tracking
- selected OCA repos/modules
- thin `ipai_*` transactional adapters only
- booking/resource modules
- finance / project-ops parity composition

**Clone/reference inputs**
- `odoo/odoo`
- selected `OCA/*` repos
- D365 Finance reference repos for parity reading only
- Project Operations reference surfaces for workflow mapping only

**Do NOT land here**
- Partner Center automation
- generic agent runtime
- Marketplace publishing logic
- Google Workspace admin tooling

---

### B. `agent-platform/`

**Land here**
- `microsoft/agent-framework` runtime adoption
- Pulser orchestration layer
- finance-agent tool wrappers
- approval / guardrail logic
- operator assistant surfaces
- Partner Center / Workspace / Azure task tools for agents

**Clone/reference inputs**
- `microsoft/agent-framework`
- `anthropics/financial-services-plugins`
- `Azure-Samples/get-started-with-ai-agents`
- `Azure-Samples/openai-chat-app-entra-auth-builtin`
- `gtzheng/Awesome-Agentic-System-Design` as architecture reference only

**Do NOT land here**
- ERP parity logic
- Odoo business-domain source-of-record code

---

### C. `platform/`

**Land here**
- control-plane contracts
- Partner Center API client contracts
- submission/offer schemas
- support-ticket status models
- shared metadata / SSOT-backed integration contracts

**Clone/reference inputs**
- Partner Center SDK/reference repos
- Marketplace submission/API references
- Azure Search / chat-with-your-data reference models
- Google Workspace API/client patterns

**Do NOT land here**
- scheduled jobs/runners
- infra deployment code
- Odoo modules

---

### D. `automations/` (subtree, currently `agents/workflows/`)

**Land here**
- scheduled sync jobs
- Partner Center polling/export jobs
- billing/report extraction jobs
- support-ticket sync
- operational runners and runbooks

**Clone/reference inputs**
- Azure Pipelines reference repos
- Google Workspace CLI usage patterns
- Partner Center Labs / operational samples

**Do NOT land here**
- authoritative schemas
- platform SSOT
- public web apps

---

### E. `infra/`

**Land here**
- Azure IaC (Bicep + AVM)
- Key Vault / app registration / identity wiring
- policy assignments
- tag enforcement
- network / ingress / runtime deployment composition
- Azure Pipelines deployment patterns after adaptation

**Clone/reference inputs**
- AVM/Bicep modules (`Azure/bicep-registry-modules`)
- `Azure-Samples/azure-container-apps-blue-green-with-azure-pipelines`
- `Azure/PSRule.Rules.Azure`
- `Azure/PSRule-pipelines`

**Do NOT land here**
- business logic
- Marketplace narratives
- agent workflows themselves

---

### F. `.github/`

**Land here**
- reusable workflows
- CI gates
- spec compliance checks
- release gates
- partner-center validate/sync workflows
- tag/audit drift checks

**Clone/reference inputs**
- `microsoft/azure-pipelines-yaml`
- spec-kit CI guard patterns (deferred — see `.specify/EXTENSION_EVALUATION.md`)
- PSRule validation stage patterns

**Do NOT land here**
- app code
- API client implementations

---

### G. `docs/`

**Land here**
- adoption registers
- reference-adaptation notes (`docs/architecture/reference-adaptations/`)
- Marketplace runbooks (`docs/marketplace/`)
- ISV Success artifacts
- Partner Center ops checklist
- delivery plans
- benchmark/parity documentation

**Clone/reference inputs**
- D365 docs repos (`MicrosoftDocs/dynamics-365-unified-operations-public`, `dynamics365-guidance`)
- FastTrack assets (`microsoft/Dynamics-365-FastTrack-Implementation-Assets`)
- MB-310 labs (`MicrosoftLearning/MB-310-Microsoft-Dynamics-365-Finance`)
- Odoo industry pages
- awesome-list / architecture reading repos

**Do NOT land here**
- executable runtime logic

---

### H. `data-intelligence/`

**Land here**
- Databricks bundle patterns
- semantic/reporting models
- Power BI / Fabric prep
- finance telemetry interpretation
- reporting extracts

**Clone/reference inputs**
- `databricks/bundle-examples`
- `microsoft/ISM-Telemetry-for-Finance-and-Operations`

---

### I. `web/` (optional, currently `apps/`)

**Land here only if needed**
- public-facing marketing/demo/operator web surfaces
- not the core Partner Center automation path

---

## 2. Fork / clone / consume rule (canonical)

### Consume directly
- `microsoft/agent-framework`
- AVM/Bicep modules (`Azure/bicep-registry-modules`)
- Playwright (`microsoft/playwright`)
- Google Workspace CLI (`googleworkspace/cli`)
- Azure DevOps MCP (`microsoft/azure-devops-mcp`)
- PSRule packages (`Azure/PSRule.Rules.Azure`, `Azure/PSRule-pipelines`)

### Clone as reference
- Azure Samples (`Azure-Samples/*`)
- Partner Center SDK/sample repos
- OCA repos (selected modules only)
- D365 docs / labs / FastTrack assets
- Anthropic finance plugin repo
- awesome-list architecture repos

### Fork later only if
- you need a **durable internal derivative**
- upstream cannot carry the behavior
- thin wrappers are no longer enough

### Build yourselves
Only the thin delta:
- Pulser tools/policies
- Odoo adapters (`addons/ipai/*`)
- Marketplace/operator glue
- delivery gates
- SSOT
- tests

---

## 3. Minimal org-level landing map

```text
odoo               <- Odoo core/OCA composition + thin transactional adapters
agent-platform/    <- agent runtime substrate + Pulser orchestration/tools
platform/          <- control-plane contracts + Partner Center/API schemas
automations/       <- scheduled jobs/runners/syncs (currently agents/workflows/)
infra/             <- Azure IaC/policy/identity/deploy patterns
.github/           <- reusable workflows/gates/validation
docs/              <- runbooks/adoption registers/reference adaptations/evidence
data-intelligence/ <- BI/semantic/reporting/telemetry patterns
web/               <- only UI surfaces, not core automation (optional)
```

**No new top-level repos required.** This is a monorepo subtree allocation.

---

## 4. Shipping status (canonical, repeat verbatim)

```text
Azure substrate:                     YES
Functional F&O-equivalent OS:        NOT YET
Go-live-ready:                       NOT YET
```

### Already live
- Odoo 18 CE on Azure Container Apps
- Front Door + WAF + custom domain (`afd-ipai-dev`)
- Pulser Odoo Copilot
- PrismaLab gateway
- Zoho mail integration
- Spec Kit pinned (`v0.6.2`) and active

### Infrastructure validation (2026-04-14)
- 24 total BOM resources (count-matched via `az resource list`)
- Subscription-level canonical tags applied (15/15)
- BOM reconciliation: Action Group missing (gap to close R2), Managed Cert reconciled

### Delivery timeline (board-aligned to ADO iterations R1–R4)
| Milestone | Date | Iteration |
|---|---|---|
| Internal / live platform | **Now** | — |
| First customer-usable Wave-01 slice (GL + AP + AR + Reconciliation Agent v0 + basic PO) | **2026-07-14** | R2-Core-Execution-60d |
| PH BIR / hardening milestone | **2026-10-14** | R3-PH-Ops-Hardening-90d |
| GA / partner-shippable | **2026-12-15** | R4-GA |

---

## 5. Practical percentage-style read (program-level)

| Layer | % There | What's missing |
|---|---|---|
| **Platform / infrastructure** | **~75–85%** | Resource-level tag policy enforcement, AVM migration of 21 hand-written Bicep modules, Action Group provisioning |
| **Product parity** | **~25–40%** | Wave-01 functional implementation (Odoo modules + thin `ipai_*` adapters) — doctrine/SSOT/backlog/specs are strong but execution ahead |
| **Ship readiness for paying customers** | **Not ready for GA**; **ready for controlled internal/demo use now**; **first usable customer slice target = R2 (July 2026)** | Wave-01 epics #523/#524/#525 implementation |

---

## 6. Bottom line

- **No new top-level org repos required.** Existing subtrees absorb all clone/fork/adapt outputs.
- **Platform is live.** Product parity is in execution.
- **First real customer-usable slice = July 2026.**
- **Partner-shippable target = December 2026.**

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
