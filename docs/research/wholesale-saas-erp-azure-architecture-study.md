# Wholesale SaaS ERP on Azure — Odoo SoR, Databricks Intelligence, Foundry Agent Runtime

> Architecture study for a wholesale SaaS ERP built on Azure with Odoo, Databricks,
> Foundry Agent Service, Azure DevOps, VS Code devcontainers, and Anthropic agent patterns.
>
> **Status**: Canonicalized 2026-03-17.
> **Origin**: ChatGPT deep research synthesis; citations replaced with inline references.
> **Binding decisions extracted to**: `docs/architecture/ADR_ERP_PLATFORM_ROLE_SPLIT.md`,
> `docs/architecture/ADR_VSCODE_ENGINEERING_COCKPIT.md`

---

## Executive summary

The target state is a **three-plane architecture**:

| Plane | Platform | Role |
|-------|----------|------|
| **System of Record (SoR)** | Odoo CE 19 | Transactional ERP — orders, invoices, inventory, purchasing, accounting, master data |
| **System of Intelligence (SoI)** | Azure Databricks + Unity Catalog | Governed lakehouse — medallion layers, data products, analytics, AI context datasets |
| **Agent Runtime** | Microsoft Foundry Agent Service | Production agent hosting, tracing, evaluation, publish promotion, monitoring |

Microsoft Foundry Agent Service is the production agent runtime and operations plane;
Microsoft Foundry more broadly is the model/agent development and governance surface.
See [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview).

Anthropic capabilities (Claude models, Agent SDK, MCP tool connectivity) are consumed
through well-defined standards — not embedded ad-hoc into ERP logic.

### One-page decision memo

**Adopt**: Odoo (transactional) + Azure Database for PostgreSQL Flexible Server (durable, HA-ready)
+ Azure Databricks + Unity Catalog (governed lakehouse) + Microsoft Foundry Agent Service
(agent runtime + tracing/evals/monitoring) + Azure API Management (tool gateway for agents
and external API governance) + Azure DevOps Boards + GitHub repos (portfolio + code + CI/CD)
+ VS Code devcontainers (deterministic engineering cockpit).

**Why this wins**: Cleanly separates SoR / SoI / agent factory responsibilities, matches
vendor guidance for governance and multitenancy, and optimizes for a lean operator by
pushing complexity into managed services and repeatable devcontainers.

**Major tradeoffs**: Early investment required in (1) tenant provisioning automation,
(2) data ingestion discipline, and (3) agent evaluation/observability to avoid brittle
"AI glued into ERP" failure modes.

---

## Source references

Primary sources (official / first-party):

| Vendor | Topic | Reference |
|--------|-------|-----------|
| Anthropic | Agent SDK, MCP, tool use, production practices | [Claude Agent SDK docs](https://docs.anthropic.com/en/docs/agents-and-tools/agent-sdk), [MCP spec](https://modelcontextprotocol.io/) |
| Microsoft Foundry | Agent factory, runtime, tracing, evaluation, monitoring | [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview) |
| Azure | Landing zones, WAF, subscription governance | [Azure landing zone architecture](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/) |
| Odoo | Multi-db hosting, dbfilter, Python/PG requirements | [Odoo 19 source install](https://www.odoo.com/documentation/19.0/administration/on_premise/source.html), [Odoo deploy docs](https://www.odoo.com/documentation/19.0/administration/on_premise/deploy.html) |
| Databricks | Medallion architecture, Unity Catalog governance | [Medallion architecture](https://www.databricks.com/glossary/medallion-architecture), [Unity Catalog](https://learn.microsoft.com/en-us/azure/databricks/data-governance/unity-catalog/) |
| Azure DevOps | Boards-GitHub integration, Pipelines, approvals | [Azure Boards-GitHub integration](https://learn.microsoft.com/en-us/azure/devops/boards/github/) |
| VS Code | Devcontainers, workspace settings | [Dev Containers spec](https://containers.dev/), [VS Code settings](https://code.visualstudio.com/docs/getstarted/settings) |

---

## Target-state architecture

### System boundary framing

**System of Record (SoR): Odoo**

Odoo's architecture supports multi-tenant hosting at the multi-database level, with
hostname-based database routing via `dbfilter`. Database-per-tenant is the recommended
SaaS isolation model for this architecture because it aligns well with Odoo's multi-database
hosting pattern and hostname-based database routing via `dbfilter`.

Multi-company inside a tenant database handles the "one tenant = many legal entities" pattern.

Odoo 19 source install requires Python ≥3.10 and PostgreSQL ≥13 — hard constraints for
both runtime and devcontainer images. Current repo standard: Python 3.11.
See [Odoo 19 source install](https://www.odoo.com/documentation/19.0/administration/on_premise/source.html).

**System of Intelligence (SoI): Azure Databricks lakehouse**

Databricks owns analytics, AI-ready data products, and governed context datasets.
Medallion/lakehouse approach (bronze → silver → gold) is documented for Azure Databricks
and widely used for quality staging and incremental refinement.

Unity Catalog is the cross-workspace governance plane for data assets (permissions, auditing,
lineage, quality monitoring, discovery) — the security boundary for data products.
See [Data preparation cheat sheet](https://learn.microsoft.com/en-us/azure/databricks/cheat-sheet/bi-serving-data-prep).

**Agent Runtime: Microsoft Foundry Agent Service**

Foundry Agent Service is the lifecycle control plane for agents: create → test → trace →
evaluate → publish → monitor. Built-in agent observability captures tool usage, latencies,
and costs, with monitoring dashboards and metrics in Azure Monitor.

The broader Foundry platform (formerly Azure AI Studio) provides model catalog access
including models from multiple providers (including Claude), enabling a governed multi-model
strategy without rewriting the agent factory.
See [Foundry Agent Service overview](https://learn.microsoft.com/en-us/azure/foundry/agents/overview).

**System of Engagement: web + API gateway + channels**

For wholesale ERP, engagement includes: internal ERP UI, customer/self-service portals,
partner APIs, EDI-like integrations, and internal admin tooling. Azure API Management
centralizes API publication and policy enforcement, and serves as the "tool gateway" for
agent-to-service calls.

### Control plane vs workload planes

Use Azure landing zone guidance to separate foundational platform controls (identity,
network, management) from workload subscriptions/environments.

Pragmatic subscription layout:

- **Platform subscription(s)**: shared networking, central logging/monitoring, key management,
  shared CI/CD agent infrastructure
- **Workload subscriptions per environment** (dev/test/prod): Odoo runtime, Postgres,
  integration services, Foundry resources, Databricks workspaces/metastore, customer endpoints

Decide early and keep modular — subscription refactoring later is painful.

### Tenancy strategy for SaaS ERP

Database-per-tenant is the recommended SaaS isolation model for this architecture because
it aligns well with Odoo's multi-database hosting pattern and hostname-based database
routing via `dbfilter`.

| Pattern | Description | Strengths | Weaknesses | Use case |
|---------|-------------|-----------|------------|----------|
| Shared runtime + DB-per-tenant | One Odoo farm, many tenant DBs; `dbfilter` routes by hostname | Natural fit to Odoo multi-db; simpler ops; strong data isolation at DB boundary | Requires provisioning automation; noisy-neighbor compute risk; must harden dbfilter | Default for SMB/mid-market |
| Deployment-per-tenant ("stamp") | Dedicated Odoo + Postgres per tenant | Strong isolation; per-tenant upgrades/SLAs; blast radius reduction | Higher ops cost; slower onboarding without automation | Enterprise tier / regulated |
| Hybrid (tiered) | Shared for standard; stamped for top tier | Balances cost vs isolation; migration path as tenant grows | Requires tenant tiering + migration playbooks | Best overall growth model |

### Reference deployment architecture

**Edge + routing**: Azure Front Door (global routing, L7, fast failover) + WAF policy.

**App workloads**: Odoo on Azure Container Apps (serverless containers, reduced infra
overhead). AKS if full Kubernetes control needed — Container Apps default for lean team.

**Data plane**:
- Azure Database for PostgreSQL Flexible Server (Odoo databases, HA-capable)
- Azure Data Lake Storage Gen2 (lakehouse storage substrate)
- Azure Databricks + Unity Catalog (governance)

**Integration/eventing**:
- Azure Service Bus: durable enterprise messaging (queues + topics/subscriptions)
- Azure Event Grid: reactive event fan-out (near-real-time)

**Secrets/identity/observability**:
- Managed identities (token-based, no embedded credentials)
- Azure Key Vault (secret storage, encryption at rest)
- Application Insights + OpenTelemetry (standardized telemetry)

**Document intelligence**: Azure Document Intelligence (Foundry tool) for wholesale
document workflows (invoices, POs, BOLs, receipts).

---

## Role boundaries and decision matrix

### Clear ownership

| Platform | Owns | Must NOT own |
|----------|------|--------------|
| **Odoo** | Orders, invoices, inventory, purchasing, accounting, master data; multi-company/warehouse/currency | Analytics lake, agent orchestration, agent governance |
| **Azure Databricks** | Lakehouse, medallion layers, data products, context datasets, cross-domain analytics | ERP transactions (medallion = analytics, not transactional core) |
| **Microsoft Foundry** | Agent runtime, lifecycle (trace/eval/publish/monitor), agent observability | Data engineering (Databricks), ERP transaction semantics (Odoo) |
| **Anthropic** | Model behavior, Agent SDK, MCP tool connectivity standard, tool quality practices | Tenant isolation, enterprise policy, data governance |

### Foundry vs Databricks vs Anthropic

| Platform | Best for | Should not own | Interoperation |
|----------|----------|----------------|----------------|
| Foundry Agent Service | Agent runtime + lifecycle: trace/evaluate/publish/monitor | Lakehouse; SoR | Agents call tools via APIs (often through APIM); traces/evals feed CI gates |
| Azure Databricks | Lakehouse + governed analytics + medallion + Unity Catalog | ERP transactions; agent orchestration | Produces curated context products (gold datasets) for agents; Unity Catalog enforces governance |
| Anthropic Agent SDK + MCP | Agent implementation patterns, tool use, MCP connectivity | Enterprise governance, tenant isolation | MCP servers implement tool surfaces; Foundry hosts agents; APIM enforces auth/policy |

### Wholesale capability ownership

- **Order-to-cash**: Odoo SoR → Databricks analytics → agents handle exceptions (not direct posting)
- **Procure-to-pay**: Odoo SoR → Databricks supplier analytics → agents assist with Document Intelligence
- **Inventory & warehousing**: Odoo SoR → Databricks intelligence/forecasting → agents recommend replenishment
- **Finance**: Odoo SoR → Databricks finance intelligence → agents assist narrative/anomaly triage (not ledger posting)

---

## Developer experience and SDLC model

### Azure DevOps + GitHub coexistence

| System | Role | Owns |
|--------|------|------|
| **Azure DevOps Boards** | Portfolio / control SoR | Epics, features, stories, dashboards, audit narrative |
| **GitHub** | Source-control and PR truth | Monorepo, branches, PRs, code review, lightweight CI (Actions) |
| **Azure Pipelines** | Governed deployment / release path | Environment approvals/checks, release gates, infra deployment |

This matches the documented Azure Boards-GitHub integration patterns including `AB#` linking.
See [Azure Boards-GitHub integration](https://learn.microsoft.com/en-us/azure/devops/boards/github/).

**Runner/agent policy**:
- Microsoft-hosted agents default (reimaged per run, no cross-contamination)
- Self-hosted agents only for private-network access or specialized deps
- GitHub self-hosted runners when inside-VNet execution needed

### VS Code devcontainer-first cockpit

The devcontainer is the runtime and tooling contract. The repo's `devcontainer.json` is
the source of truth for a consistent tool/runtime stack.
See [Dev Containers spec](https://containers.dev/).

**Settings model**:

| Location | What belongs there | Why |
|----------|-------------------|-----|
| User settings | Personal UX only (font, UI layout) | Avoid per-developer drift on runtime/debug |
| Root `.vscode/settings.json` | Repo-wide exclusions, formatters, YAML/JSON schemas, tooling toggles | Portable, applies across subprojects |
| `odoo/.vscode/settings.json` | Python interpreter (inside devcontainer), Odoo lint paths, debug defaults | Stricter constraints tied to Odoo 19 requirements |
| Nested frontend `.vscode/` | TypeScript/Node version, formatter/linter | Isolates frontend from Python/Odoo |
| **Avoid entirely** | Hardcoded local interpreter paths, machine-specific paths, "disable core IDE features" | Breaks portability, causes hidden failures |

**Rules**:
- Repo-scoped settings own correctness
- User settings own personal UX only
- Devcontainer is the runtime/tooling contract
- No hardcoded local interpreter paths in tracked settings

### Target VS Code capability matrix

| Capability | Implementation | Workspace scope |
|-----------|---------------|-----------------|
| Deterministic Odoo runtime | Devcontainer image pinned; Python ≥3.10; Postgres ≥13 service | `odoo/` devcontainer |
| Addon import resolution | `addons-path` in launch/debug tasks; lint paths match addon roots | `odoo/.vscode/` |
| Ruff formatting/linting | Odoo PEP8 exceptions mapped into Ruff config | repo root config |
| YAML/JSON schema support | Workspace schema associations | root `.vscode/settings.json` |
| Prompt/eval authoring | Versioned files; Foundry eval runs in CI gates | `agent-platform/` |
| MCP-aware development | Tool surfaces as MCP servers; Agent SDK integration | `agent-platform/` |
| Devcontainer features reuse | Reusable Features from spec/official repos | root + subfolders |
| Monorepo performance | `files.watcherExclude` / `search.exclude` in workspace settings | root `.vscode/settings.json` |
| Debug/test tasks | VS Code tasks/launch configs in repo | root + `odoo/` |
| Pipeline authoring | Repo-scoped schemas; Azure Pipelines approvals for prod | root |

---

## Risks, anti-patterns, and failure modes

| Risk | Mitigation |
|------|-----------|
| Misconfigured multi-db routing | Strict hostname → db mapping via `dbfilter`; disable database list/manager surfaces |
| Lakehouse treated as transactional core | Keep transaction authoring in Odoo/Postgres; medallion is analytics |
| Agent sprawl without observability | Require trace + eval gates before publishing agents (Foundry lifecycle) |
| Tool/prompt fragility | Version tools, build eval suites, keep MCP tool contracts stable |
| Governance too heavy for lean team | Start with minimal gates; expand as tenant count grows |
| VS Code drift | Repo-scoped devcontainer + workspace settings for correctness; no user-scope runtime config |

---

## Phased roadmap

| Phase | Focus | Key deliverables |
|-------|-------|-----------------|
| **P0 Foundations** | Landing zone, identity, secrets, observability, devcontainer cockpit | Subscription layout, Key Vault, managed identity, monitoring baseline, `devcontainer.json` |
| **P1 MVP ERP** | Odoo 19 DB-per-tenant + dbfilter, customer portal, API gateway | Tenant provisioning, APIM setup, portal MVP, `dbfilter` enforcement |
| **P2 Analytics** | Databricks lakehouse + Unity Catalog, medallion from Odoo | Bronze ingestion, silver validation, gold KPIs, Unity Catalog governance |
| **P3 Copilots** | Foundry agents with trace/eval/monitor, Document Intelligence | Agent runtime, eval harness, document processing workflows |
| **P4 Multi-tenant hardening** | Hybrid tenancy, approval gates, SLOs, self-hosted where needed | Stamp factory, release governance, runbooks |

### Build now / Defer / Avoid

| Build now | Defer | Avoid entirely |
|-----------|-------|----------------|
| Odoo 19 SoR with DB-per-tenant + dbfilter | Per-tenant stamps until revenue justifies | Databricks as transactional core |
| Deterministic devcontainers | Advanced multi-region stamping | ERP posting via agents without guardrails |
| Baseline CI/CD with approvals for prod | Broad agent marketplace | Untracked VS Code user-setting dependencies |
| Databricks + Unity Catalog foundation | Cross-tenant benchmarking products | Agents without trace/eval gates |
| Foundry tracing/evals for first agents | | |

---

*Canonicalized 2026-03-17. Origin: ChatGPT deep research synthesis.*
