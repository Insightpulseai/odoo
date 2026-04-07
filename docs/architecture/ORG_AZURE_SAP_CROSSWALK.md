# Org Topology ↔ Azure Landscape Crosswalk

> Maps the Insightpulseai GitHub org structure to Azure's SAP whole-landscape guidance.
> SSOT: `ssot/governance/repo-topology.yaml`
> Reference: [Azure SAP whole-landscape architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/sap/sap-whole-landscape)

---

## Why this exists

Microsoft's SAP whole-landscape guidance recommends a **hub-spoke** design with subscriptions aligned to **billing, policy, and security boundaries** — not one per system. The same logic drives repo structure: repos map to **responsibility planes**, not environments or instances.

---

## Azure concept → Repo mapping

| Azure concept | Operational meaning | Org function | Repo |
|---|---|---|---|
| Management groups / policy boundaries | Central policy, standards, governance | Governance spine | `.github` |
| Reference architecture / operating model | Cross-plane standards, runbooks, ADRs | Architecture + governance docs | `docs` |
| Regional hub subscription | Shared connectivity, firewalling, central services | Platform/infra substrate | `infra` |
| Hub VNet | Central network/control point | Networking + landing zone | `infra` |
| Central services (not workload-specific) | Shared secrets refs, metadata, platform contracts | Control plane | `platform` |
| Central identity / AD / DNS extension | Central user management, directory ops | Identity/control-plane contracts | `platform` |
| SAP non-prod subscription | Dev/test/QA/preprod runtime boundary | Runtime environment config | `odoo` + `infra` |
| SAP prod subscription | Production + DR runtime boundary | Release/deploy control | `odoo` + `infra` |
| One VNet per SAP environment | Environment isolation by tier | Environment overlays | `infra` + `odoo` |
| SAP spoke VNet | Workload-owned application boundary | ERP transactional/runtime | `odoo` |
| SAP perimeter subnet | Internet-facing SAP-dependent services | Browser-facing ERP perimeter | `web` |
| Application Gateway subnet | Internet ingress for SAP/Fiori-style traffic | Edge/app ingress | `infra` |
| SAP systems / app servers / DB VMs | Actual business runtime | ERP models, addons, runtime | `odoo` |
| ExpressRoute / hybrid connectivity | Hybrid enterprise connection | Network/hybrid integration | `infra` |
| SAP Basis-style automation | Start/stop, provisioning, scheduling | Ops automation + runbooks | `automations` |
| Single pane of glass / landscape console | Centralized visibility and control | Ops console / admin UX | `web` + `platform` |
| Templated deployment / ARM repeatability | Consistent repeatable env creation | Bootstrap templates | `templates` + `infra` |
| REST/API extensibility + workflow hooks | Automation hooks from external systems | Agent/runtime integration | `agent-platform` |
| AI / assistant / workflow orchestration | Agent runtime, retrieval, orchestration | Agent runtime ownership | `agent-platform` |
| Agent definitions / evals / judges | Personas, skills, prompts, eval harnesses | Agent spec layer | `agents` |
| Analytics / reporting plane | BI, medallion, semantic serving | Data/analytics ownership | `data-intelligence` |
| Shared design system | Consistent UX/tokens/components | Design authority | `design` |

---

## Structural implications

### 1. Separate hub/platform from workload

The Azure guide makes the **hub** the central connectivity plane while **SAP spokes** hold workloads.

- `infra` = hub / landing zone / edge / network
- `platform` = shared control plane
- `odoo` = SAP-equivalent workload repo

### 2. Keep internet-facing services with the workload team

The guide says services in the **SAP perimeter subnet** have SAP dependencies and should be managed by the **SAP team**, not central IT.

- `web` = perimeter/browser-facing surfaces (workload team owns)
- `infra` = ingress/network substrate only

### 3. Do not create repos per environment or system

Microsoft says not to explode the landscape into too many subscriptions. Same for repos:

- No `odoo-prod`, `odoo-dev`, `odoo-qa`
- Environment separation lives in config/deployment structure, not repo boundaries

### 4. Centralize identity and operational control

The SAP guidance describes a **single pane of glass** with central user management.

- `platform` owns identity/control concerns
- Workload repos consume identity contracts, never define them

---

## Canonical planes

```yaml
governance:           [.github, docs]
platform_substrate:   [infra, platform]
transactional_runtime: [odoo]
perimeter_experience: [web]
operations_automation: [automations]
agent_runtime:        [agent-platform]
agent_spec_layer:     [agents]
analytics:            [data-intelligence]
shared_assets:        [design, templates]
```

**12 core repos** (architecture-authority) + **3 adjunct repos** (public/OSS, no architecture authority: `powerbi-skills`, `ugc-mediaops-kit`, `landing.io`).

---

## Decision rule (quick reference)

| I need to... | Repo |
|---|---|
| Change shared connectivity / IaC / DNS / ingress | `infra` |
| Change shared metadata / control contracts / admin UI | `platform` |
| Change business logic / ERP models / Odoo addons | `odoo` |
| Change browser-facing portal / marketing / login UX | `web` |
| Add scheduled jobs / event-driven automation | `automations` |
| Change agent runtime / orchestration / retrieval | `agent-platform` |
| Change agent definitions / skills / evals / judges | `agents` |
| Change data products / lakehouse / analytics | `data-intelligence` |
| Change design tokens / brand assets / components | `design` |
| Change org policy / reusable workflows | `.github` |
| Change cross-repo architecture docs / ADRs | `docs` |
| Bootstrap a new repo / spec / automation | `templates` |

---

*Last updated: 2026-04-07*
