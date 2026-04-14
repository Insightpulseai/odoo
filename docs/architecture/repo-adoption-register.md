# Repo Adoption Register

> **Authoritative narrative companion** to `ssot/governance/upstream-adoption-register.yaml`. Per-repo adoption decisions for the current desired end state.
>
> **Last updated:** 2026-04-14
> **Scope:** Pulser-for-Odoo on Azure. Three-surface benchmark (D365 Finance + Finance agents + D365 Project Operations).

## Default doctrine

> [!IMPORTANT]
> **Use upstream for commodity capability. Custom-build only for composition, policy, packaging, and thin business-specific gaps.**

- **Reuse the platform**: Adopt existing commodity tools and frameworks.
- **Adapt the reference**: Configure and extend canonical samples and accelerators.
- **Own only the delta**: Build unique business logic and thin orchestration bridges.

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
| `microsoft/agent-framework` | agent | `consume-directly` | agent-platform | dependency in `agent-platform/` | now | Canonical agent-plane runtime for Pulser orchestration, multi-agent workflows, checkpointing, HITL, and observability. Keep GitHub as source-control truth and Azure DevOps as planning/delivery integration surface; do not fork or embed business-domain logic in the framework. |
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
| Microsoft Finance agents docs | benchmark / product surface | `clone-reference` | architecture / product | `docs/architecture/reference-adaptations/` | now | Workflow and UX benchmark for Finance agents parity, including architecture, data handling, Excel and Outlook surfaces, Financial Reconciliation agent, and Collections in Outlook. Use as parity/workflow reference only; do not treat as product code or implementation repo. |
| `anthropics/financial-services-plugins` | agent / finance workflow packaging | `clone-reference` | agent-platform | `docs/architecture/reference-adaptations/` or `agent-platform/experiments/` | now | Reference for Claude-native finance plugin packaging, including skills, slash commands, sub-agents, and MCP-backed workflow organization. Adapt packaging patterns only; filter out investment-banking, equity-research, private-equity, and wealth-management assumptions that are outside current-wave scope. Fork only later if IPAI creates a durable Pulser finance plugin pack. |
| `gtzheng/Awesome-Agentic-System-Design` | agent / architecture research | `clone-reference` | agent-platform + docs | `docs/architecture/reference-adaptations/` | now | Curated reading/index repo for agent-system design, evaluation, safety, and framework comparison (covers AutoGen, Claude Agent SDK, CrewAI, Google ADK, LangGraph, Microsoft Agent Framework, M365 Agents SDK, OpenAI Agents SDK, Pydantic AI, SmolAgents, AWS Strands). Reference only — survey/index, not a runtime dependency or fork target. Use to shortlist architecture reading and compare frameworks against `microsoft/agent-framework`. |
| Playwright MCP / CLI | testing / agent browser ops | `consume-directly` | QA / delivery engineering | `tests/playwright/` and agent/editor configuration | now | Use as the canonical agent-compatible browser automation surface alongside Playwright Test. |
| Chrome DevTools MCP | testing / diagnostics | `do-not-adopt` | QA / delivery engineering | none | later | Use only as a debugging and diagnostics aid for browser/network/performance investigation; not a primary regression framework. |
| `microsoft/azure-pipelines-tasks` | delivery / CI-CD tasks | `clone-reference` | delivery-engineering | `docs/architecture/reference-adaptations/` | now | Pattern reference for built-in task implementations (Python, container, AKS, ACA deploy). Extract patterns only — do not fork the repo. |
| `microsoft/azure-pipelines-task-lib` | delivery / task SDK | `consume-directly` | delivery-engineering | `package.json devDependency` in custom task package | now | Required npm SDK for authoring custom Azure Pipelines tasks (Odoo deploy gate, BIR validation). Consume via npm, never fork. |
| `microsoft/azure-pipelines-extensions` | delivery / deploy patterns | `clone-reference` | delivery-engineering | `docs/architecture/reference-adaptations/` | now | Reference for InvokeRestAPI, ACA, and AKS deploy extension task implementations. |
| `Azure/PSRule.Rules.Azure` | delivery / IaC validation | `consume-directly` | platform-engineering | `azure-pipelines/` validate stage | now | WAF-aligned Bicep/ARM rule set; gate infra changes before `az deployment`. Run via PSRule-pipelines task companion. |
| `Azure/PSRule-pipelines` | delivery / IaC validation | `consume-directly` | platform-engineering | `azure-pipelines/` validate stage | now | Pipeline task wrapper that invokes `Azure/PSRule.Rules.Azure`. Both must be wired together. |
| `Azure-Samples/azure-container-apps-blue-green-with-azure-pipelines` | delivery / deploy pattern | `clone-reference` | delivery-engineering | `azure-pipelines/odoo-deploy.yml` | now | Blue/green ACA traffic-weight pattern for Odoo container slot promotion. Wave-01 critical. |
| `databricks/bundle-examples` | delivery / data platform | `clone-reference` | data-engineering | `azure-pipelines/databricks-deploy.yml` | now | Canonical Databricks Asset Bundle (DAB) CI/CD deploy pattern. Verify NOASSERTION license before embedding. |
| `microsoft/azure-pipelines-vscode` | delivery / dev tooling | `consume-directly` | delivery-engineering | `.devcontainer/devcontainer.json` extensions | later | VS Code extension for Azure Pipelines YAML schema validation and IntelliSense. |

### §F.1 D365 Finance reference surfaces — Wave-01 parity (Epic #523)

> All D365 repos are `clone-reference` only. IPAI displaces D365 Finance with Odoo CE 18 + OCA + thin `ipai_*`. No fork, no consume-directly, no Dataverse-as-SoR.

| `microsoft/Dynamics-365-FastTrack-Implementation-Assets` | transaction + agent | `clone-reference` | odoo-platform | `docs/architecture/reference-adaptations/d365-finance/` | now | Primary D365 Finance parity library. Harvest `ERP/Finance/InvoiceCapture/`, `Agents/AI ERP Agents/`, `Administration/Analytics/EntityStoreTools/`. Filter `ERP/SCM/`, `ERP/Commerce/`. |
| `MicrosoftDocs/dynamics-365-unified-operations-public` | transaction (all Wave-01) | `clone-reference` | odoo-platform | `docs/architecture/reference-adaptations/d365-finance/` | now | Authoritative functional spec — GL, AP, AR, Budgeting, Cash & Bank, Fixed Assets, Asset Leasing, Subscription Billing, Tax, Electronic Invoicing, Finance Insights. CC-BY-4.0 — no code copy. Filter `articles/supply-chain/`, `articles/commerce/`, `articles/human-resources/`. |
| `MicrosoftDocs/dynamics365-guidance` | transaction + agent | `clone-reference` | odoo-platform + agent-platform | `docs/architecture/reference-adaptations/d365-finance/` | now | Harvest `finance-invoice-capture-ga-features-functionality.md`, `microsoft-copilot-finance.md`, `finance-globalization-studio-regulatory-configuration-service.md`. |
| `MicrosoftLearning/MB-310-Microsoft-Dynamics-365-Finance` | transaction (test/UAT) | `clone-reference` | odoo-platform | `docs/architecture/reference-adaptations/d365-finance/` | now | Lab sequence = Wave-01 UAT script template (GL, AP 3-way, AR collections, budgeting, bank recon, fixed assets, cost accounting). |
| `microsoft/ISM-Telemetry-for-Finance-and-Operations` | delivery (observability) | `clone-reference` | agent-platform | `docs/architecture/reference-adaptations/d365-finance/` | now | Application Insights KQL patterns for finance transaction telemetry; adapt to Odoo ACA + Azure Monitor. |

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
| `googleworkspace/cli` | agent / delivery | `consume-directly` | agent-platform | tool dependency | now | Official Workspace CLI with AI agent skills. Spans Drive, Gmail, Calendar, etc. |
| `googleworkspace/developer-tools` | agent / delivery | `consume-directly` | agent-platform | tool dependency | now | Official VS Code extension + OAuth linting + MCP support. |
| `googleworkspace/add-ons-samples` | agent | `clone-reference` | agent-platform | `docs/architecture/reference-adaptations/` | now | Gmail/Calendar/Docs/Drive add-on patterns. |
| `googleworkspace/google-chat-samples` | agent | `clone-reference` | agent-platform | `docs/architecture/reference-adaptations/` | now | Google Chat notification and bot patterns for W9 ops. |
| `googleworkspace/python-samples` | agent / transaction | `clone-reference` | agent-platform | `docs/architecture/reference-adaptations/` | now | Official Python samples for Workspace APIs (Gmail, Calendar, Drive). |
| `googleworkspace/meet` | agent | `clone-reference` | agent-platform | `docs/architecture/reference-adaptations/` | later | Meet-aware integration patterns; not current-wave core. |
| `googleworkspace/meet-media-api-samples` | agent | `clone-reference` | agent-platform | `docs/architecture/reference-adaptations/` | later | Advanced meeting/media integrations; later-phase core. |
| Partner Center portal / future APIs | partner ops | do-not-adopt | GTM / partner ops | none | later/never | Portal-driven until automation funded |

### §F.2 Reconciled upstreams (added 2026-04-14)

> Reconciled UP from `platform/templates/adaptation-map.yaml` and memory notes into the canonical YAML. Listed here for narrative coverage.

| `microsoft-foundry/foundry-samples` | agent | `clone-reference` | agent-platform | `agent-platform/experiments/foundry-samples/` | now | Pattern reference for Pulser agent bootstrap. Explicit enumeration (replaces former `microsoft-foundry/*` wildcard). |
| `microsoft-foundry/foundry-agent-webapp` | agent | `clone-reference` | agent-platform | `agent-platform/experiments/` | now | Foundry-native web app shell reference. |
| `microsoft-foundry/mcp-foundry` | agent | `clone-reference` | agent-platform | `agent-platform/experiments/` | now | Foundry ↔ MCP integration patterns. |
| `microsoft-foundry/fine-tuning` | agent | `clone-reference` | agent-platform | `agent-platform/experiments/` | later | Deferred; adopt only when custom-model tuning is in scope. |
| `Azure-Samples/release-manager-assistant` (RMA) | agent/delivery | `clone-reference` | agent-platform | `agent-platform/agents/release-manager/` | now | Already scaffolded via `infra/azure/modules/release-manager-aca.bicep`. Fork trigger: Pulser Release Ops productizes per PRD §0.7. |
| Azure MCP Server (first-party) | agent/platform | `consume-directly` | platform-engineering | `.mcp.json` + `.vscode/mcp.json` | now | 40+ namespace first-party MCP. Replaces community Azure MCP entries. |
| Azure Developer CLI (`azd`) | platform | `consume-directly` | platform-engineering | devcontainer + `scripts/` + `azure-pipelines/` | now | Canonical CLI for azd-shaped templates. |
| `microsoft/dev-proxy` | testing | `clone-reference` | qa-engineering | `docs/architecture/reference-adaptations/` | now | LLM rate-limit + API chaos companion to Playwright. |
| Azure Python SDK pin manifest | agent-platform | `consume-directly` | agent-platform | `pyproject.toml`/`requirements.txt` | now | `azure-ai-agents>=1.1.0`, `azure-ai-projects>=2.0.1`, `azure-ai-evaluation>=1.16.3`, `azure-ai-documentintelligence>=1.0.2`, `azure-search-documents>=11.6.0`, `azure-identity>=1.25.3`, `azure-keyvault-secrets>=4.10.0`. |
| `microsoft/unified-data-foundation` | data-platform | `consume-directly` | data-engineering | `infra/azure/` composition + `data-intelligence/` integration | now (P0) | **Time-sensitive** — Fabric trial ~2026-05-20. Terraform IaC for Databricks + Fabric + mirroring in one unit. |
| Partner Center SaaS Fulfillment API v2 | partner-ops | `consume-directly` (REST) | platform | `platform/partner-center/fulfillment/` | now | Required for SaaS offer launch. Odoo remains entitlement record of truth. |
| Partner Center Marketplace Metering API | partner-ops | `consume-directly` (REST) | platform | `platform/partner-center/metering/` | now | Idempotent usage events, 24h submission window. Reconciled to Microsoft invoice. |
| Partner Center Referrals / Co-sell API | partner-ops | `do-not-adopt` (defer) | platform | none | defer_until_listing_live | Not actionable until SaaS offer is live. |
| **IPAI infra composition** | infra | own-directly | infra/platform | `infra/azure/` | now | Own |
| **IPAI Azure SSOT** | cross-cutting | own-directly | architecture/platform | `ssot/azure/` | now | Own |
| **IPAI Pulser tools/policies** | agent | own-directly | agent-platform | `agent-platform/` | now | Own |
| **IPAI Odoo thin adapters** | transaction | own-directly | odoo/platform | `addons/ipai/` | now | Own |
| **IPAI tests + fixtures** | testing | own-directly | QA / delivery | `tests/` | now | Own |
| **IPAI delivery doctrine + templates** | delivery | own-directly | delivery/platform | `.github/`, `docs/delivery/`, `azure-pipelines/` | now | Own |

---

### General Fork / Clone / Build Rules

1. **Consume directly (Adopt)**: Use as-is for frameworks, registries, and CLIs providing generic business/infra primitives. 
2. **Clone as reference (Adapt)**: Copy patterns from samples, accelerators, and industry references; harvest deltas, do not fork product code.
3. **Fork later**: Only when policy-enforced behavior, tenant-aware restrictions, or durable internal product divergence is required.
4. **Custom build only the delta**: Own the thin adapters, composition, packaging, governance SSOT, and business-specific workflows.

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
   - `googleworkspace/cli`
   - `googleworkspace/developer-tools`
2. **Clone as reference:**
   - `Azure-Samples/azure-fastapi-postgres-flexible-aca`
   - `Azure-Samples/Azure-PostgreSQL-Resiliency-Architecture`
   - `Azure-Samples/azure-search-openai-demo`
   - `Azure-Samples/chat-with-your-data-solution-accelerator`
   - `Azure-Samples/get-started-with-ai-agents`
   - `Azure-Samples/openai-chat-app-entra-auth-builtin`
   - `googleworkspace/add-ons-samples`
   - `googleworkspace/google-chat-samples`
   - `googleworkspace/python-samples`
   - Selected OCA modules (Finance, Reporting, Tools, UX)
   - `microsoft-foundry/foundry-samples`, `foundry-agent-webapp`, `mcp-foundry` (split from former wildcard)
   - `Azure-Samples/release-manager-assistant` (adapt patterns; fork only when Pulser Release Ops productizes)
   - `microsoft/azure-pipelines-yaml`
   - `microsoft/dev-proxy` (chaos/rate-limit testing)
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

- **2026-04-14** Initial canonical register. 8 consume-directly + 33 clone-reference + 2 fork-later + 3 do-not-adopt + 6 own-directly.
- **2026-04-14 (reconciliation)** Removed 8 phantom Copilot-sample rows (OfficeDev/M365, Dynamics-365, Power-Platform, CopilotStudio, Security-Copilot, Fabric-Copilot, azure-copilot-samples, github/awesome-copilot) — not in canonical YAML, overlap M365 Agents SDK + Foundry, Copilot Studio is declarative-tier (Pulser is custom-engine). Added §F.2 reconciled upstreams: split `microsoft-foundry/*` wildcard into 4 named entries + RMA; reconciled Azure MCP Server, `azd`, dev-proxy, Azure Python SDK pin manifest, `microsoft/unified-data-foundation` (P0, Fabric trial time-sensitive), Partner Center SaaS Fulfillment v2 + Metering API. Net counts: 15 consume-directly + ~35 clone-reference + 0 fork-later + 10 do-not-adopt + 6 own-directly.
