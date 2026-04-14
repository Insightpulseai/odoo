# Repo Adoption Register

> **Authoritative narrative companion** to `ssot/governance/upstream-adoption-register.yaml`. Per-repo adoption decisions for the current desired end state.
>
> **Last updated:** 2026-04-14
> **Scope:** Pulser-for-Odoo on Azure. Three-surface benchmark (D365 Finance + Finance agents + D365 Project Operations).

## Default doctrine

> Do not fork Microsoft/Azure platform repos unless IPAI is intentionally taking ownership of a long-lived derivative product. For the current stack, consume frameworks and registries directly, clone samples as references, and own only the thin Pulser/Odoo/Azure adapters, SSOT, tests, and platform composition.

## Adoption modes (5)

```
consume-directly  = use upstream package/registry/template, no fork
clone-reference   = study/copy selected patterns, do not track as a product fork
fork-later        = only if IPAI needs a long-lived derivative with custom controls
do-not-adopt      = useful for learning, not for the current stack
own-directly      = build and maintain in Insightpulseai because it is your SSOT/adapter/product code
```

## Plane mapping (current end state)

| Plane | Stack |
|---|---|
| Transaction | Odoo |
| Data intelligence | Databricks + Fabric |
| Agent | Foundry + Agent Framework |
| Delivery | GitHub-first, Azure DevOps-aware |
| Testing | Odoo native tests + Playwright |
| Portal-only | Partner Center (no repo automation now) |

---

## Comprehensive register

| Upstream / surface | Plane | Mode | Internal owner | Target internal destination | Timing | Decision |
|---|---|---|---|---|---|---|
| `Azure/bicep-registry-modules` | infra | consume-directly | infra/platform | `infra/azure/` composition only | now | Use AVM directly |
| `Azure-Samples/azure-fastapi-postgres-flexible-aca` | infra | clone-reference | infra/platform | `docs/architecture/reference-adaptations/` | now | Harvest ACA/Postgres/azd patterns |
| `Azure-Samples/Azure-PostgreSQL-Resiliency-Architecture` | infra/data | clone-reference | platform/data | `docs/architecture/` | now | Use for HA/DR decisions |
| `Azure-Samples/azure-postgres-pgvector-python` | data/agent | clone-reference | agent/data platform | `data-intelligence/experiments/` | later | Use for vector-sidecar patterns |
| `Azure-Samples/azure-postgresql-mcp` | agent/data | fork-later | agent-platform | `agent-platform/tools/postgresql-mcp/` | later | Reference now; fork only if controls needed |
| `microsoft/agent-framework` | agent | consume-directly | agent-platform | dependency in `agent-platform/` | now | Canonical orchestration runtime |
| Foundry AI templates / RMA | agent/delivery | clone-reference | delivery + agent | `docs/architecture/reference-adaptations/` | now | Adapt patterns, not productize |
| `microsoft/azure-devops-mcp` | delivery | consume-directly | delivery/platform | agent/editor config | now | Use upstream MCP directly |
| `microsoft/azure-pipelines-yaml` | delivery | clone-reference | delivery/platform | `azure-pipelines/` or docs | now | Copy only useful templates |
| `microsoft/azure-pipelines-agent` | delivery | do-not-adopt | delivery ops | none (docs only) | never | Operational reference only |
| `microsoft/playwright` | testing | consume-directly | QA / delivery | `tests/playwright/` | now | Canonical browser automation |
| `Azure-Samples/azure-search-openai-demo` | agent / public web | `clone-reference` | web + agent-platform | `docs/architecture/reference-adaptations/` | now | Reference for shared knowledge assistant, Azure AI Search + OpenAI RAG, citations UX, and public-facing chat patterns. |
| `Azure-Samples/chat-with-your-data-solution-accelerator` | agent / control plane | `clone-reference` | agent-platform | `docs/architecture/reference-adaptations/` | now | Reference for ingestion-heavy “chat with your data” architecture, document upload flows, and internal knowledge assistant patterns. |
| `Azure-Samples/get-started-with-ai-agents` | agent | `clone-reference` | agent-platform | `agent-platform/experiments/` or `docs/architecture/reference-adaptations/` | now | Reference for Foundry-native agent bootstrap, monitoring, tracing, and file-search grounding patterns. |
| `Azure-Samples/openai-chat-app-entra-auth-builtin` | agent / internal app | `clone-reference` | web + agent-platform | `agent-platform/experiments/` or `docs/architecture/reference-adaptations/` | now | Reference for authenticated internal assistant/admin-console patterns on Azure Container Apps with built-in Entra auth. |
| `Azure-Samples/postgres-agentic-shop` | agent / data | `clone-reference` | agent-platform | `agent-platform/experiments/` | later | Reference for multi-agent customer-experience patterns backed by PostgreSQL; not current-wave core. |
| Playwright MCP / CLI | testing / agent browser ops | `consume-directly` | QA / delivery engineering | `tests/playwright/` and agent/editor configuration | now | Use as the canonical agent-compatible browser automation surface alongside Playwright Test. |
| Chrome DevTools MCP | testing / diagnostics | `do-not-adopt` | QA / delivery engineering | none | later | Use only as a debugging and diagnostics aid for browser/network/performance investigation; not a primary regression framework. |
| `OCA/account-financial-reporting` | transaction | `clone-reference` | odoo/platform | `addons/oca/` | now | Selected finance reporting modules only; do not fork the whole repo by default. |
| `OCA/account-financial-tools` | transaction | `clone-reference` | odoo/platform | `addons/oca/` | now | Selected finance operations modules only; upstream fixes should go back to OCA where feasible. |
| `OCA/account-reconcile` | transaction | `clone-reference` | odoo/platform | `addons/oca/` | now | Selected reconciliation modules only for current Finance parity scope. |
| `OCA/mis-builder` | transaction / reporting | `clone-reference` | odoo/platform | `addons/oca/` | now | Selected MIS/reporting modules only for finance reporting and budgeting support. |
| `OCA/account-analytic` | transaction | `clone-reference` | odoo/platform | `addons/oca/` | now | Selected analytic-accounting modules only where CE/OCA composition requires them. |
| `OCA/currency` | transaction | `clone-reference` | odoo/platform | `addons/oca/` | now | Selected currency and FX-support modules only. |
| `OCA/server-ux` | transaction / UX | `clone-reference` | odoo/platform | `addons/oca/` | now | Selected UX helpers only, including date-range and related operator ergonomics where justified. |
| `OCA/partner-contact` | transaction / CRM base | `clone-reference` | odoo/platform | `addons/oca/` | now | Selected contact/partner-management modules only for current CRM and finance-adjacent needs. |
| `OCA/sale-workflow` | transaction / project-ops adjacent | `clone-reference` | odoo/platform | `addons/oca/` | now | Selected sales-workflow modules only where needed for Project Operations parity. |
| `OCA/sale-reporting` | transaction / project-ops adjacent | `clone-reference` | odoo/platform | `addons/oca/` | now | Selected sales-reporting modules only where needed for Project Operations parity. |
| Partner Center portal / future APIs | partner ops | do-not-adopt | GTM / partner ops | none | later/never | Portal-driven until automation funded |
| **IPAI infra composition** | infra | own-directly | infra/platform | `infra/azure/` | now | Own |
| **IPAI Azure SSOT** | cross-cutting | own-directly | architecture/platform | `ssot/azure/` | now | Own |
| **IPAI Pulser tools/policies** | agent | own-directly | agent-platform | `agent-platform/` | now | Own |
| **IPAI Odoo thin adapters** | transaction | own-directly | odoo/platform | `addons/ipai/` | now | Own |
| **IPAI tests + fixtures** | testing | own-directly | QA / delivery | `tests/` | now | Own |
| **IPAI delivery doctrine + templates** | delivery | own-directly | delivery/platform | `.github/`, `docs/delivery/`, `azure-pipelines/` | now | Own |

---

## Fork triggers (explicit conditions only)

### `Azure-Samples/azure-postgresql-mcp` → fork-later

Fork only if you need:
- Query allowlists (block destructive SQL from agents)
- Tenant-aware access control (per-customer scoping)
- Stricter write restrictions
- Custom audit / policy hooks

### `Foundry AI templates / RMA` → fork-later

Fork only if **Pulser Release Ops** becomes a productized internal service per PRD §0.7 with long-lived divergence from upstream RMA.

---

## Do-now list

1. **Consume directly:**
   - `Azure/bicep-registry-modules` (AVM)
   - `microsoft/agent-framework`
   - `microsoft/azure-devops-mcp`
   - `microsoft/playwright`
   - Playwright MCP / CLI
2. **Clone as reference:**
   - `Azure-Samples/azure-fastapi-postgres-flexible-aca`
   - `Azure-Samples/Azure-PostgreSQL-Resiliency-Architecture`
   - `Azure-Samples/azure-search-openai-demo`
   - `Azure-Samples/chat-with-your-data-solution-accelerator`
   - `Azure-Samples/get-started-with-ai-agents`
   - `Azure-Samples/openai-chat-app-entra-auth-builtin`
   - Selected OCA modules (Finance, Reporting, Tools, UX)
   - Foundry solution templates / Release Manager Assistant
   - `microsoft/azure-pipelines-yaml`
3. **Own directly:**
   - `infra/azure/` (AVM composition)
   - `ssot/azure/` (BOM, naming, tags, desired end state)
   - `agent-platform/` (Pulser tools, policies, telemetry)
   - `addons/ipai/` (thin Odoo adapters)
   - `tests/playwright/` (browser/E2E suites)
   - `.github/` + `azure-pipelines/` + `docs/delivery/` (delivery doctrine)

---

## Anti-patterns (rejected at code review)

- Forking AVM/Bicep modules — creates downstream burden Microsoft now solves
- Forking `microsoft/agent-framework` — re-implementing what Microsoft owns
- Forking `microsoft/playwright` — adopting upstream test framework as your codebase
- Cloning Foundry templates as productized internal codebases without an explicit fork_trigger documented
- Vendoring `Azure-Samples/*` repos under Insightpulseai (creates stale copies)
- Forking `azure-pipelines-agent` — agent ops is reference-only

---

## Mirror principle

> Mirror only **OUTCOMES** (composition, decision records, thin adapters, tests). Keep upstreams upstream.

**IPAI mirror targets:**
- `infra/azure-avm-composition`
- `docs/architecture/reference-adaptations`
- `agent-platform/pulser-tools`
- `tests/playwright`
- `ssot/azure`
- `docs/delivery`

---

## Hard constraints (sourced)

- **AVM is Microsoft's single Bicep-module standard.** New non-AVM modules no longer accepted.
- **`azure-fastapi-postgres-flexible-aca` is a FastAPI sample** with `infra/`, `src/`, `azd`, and GitHub workflows. It is a reference pattern, NOT an Odoo app base.
- **`microsoft/agent-framework` is the intended Microsoft runtime** for orchestrated agents (Python + .NET).
- **`microsoft/azure-devops-mcp` already exposes the DevOps surface to agents** with scoped domains (work, work-items, repos, pipelines, wiki, test-plans).

---

## Anchors

- **SSOT YAML:** [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml)
- **Coverage matrix:** [`microsoft-reference-coverage-matrix.md`](microsoft-reference-coverage-matrix.md)
- **Cross-tool authority split:** [`ssot/governance/platform-authority-split.yaml`](../../ssot/governance/platform-authority-split.yaml)
- **PRD doctrine:** [`spec/pulser-odoo/prd.md`](../../spec/pulser-odoo/prd.md) §0
- **Memory:** `feedback_upstream_adoption_doctrine.md`, `feedback_microsoft_reference_coverage_doctrine.md`

## Changelog

- **2026-04-14** Initial canonical register. 5 consume-directly + 21 clone-reference + 2 fork-later + 3 do-not-adopt + 6 own-directly.
