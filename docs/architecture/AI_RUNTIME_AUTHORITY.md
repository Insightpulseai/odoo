# AI Runtime Authority Split

> Version: 1.0.0
> Last updated: 2026-03-23
> Parent: `docs/delivery/ODOO_AZURE_GENIE_GO_LIVE_CHECKLIST.md`

---

## Revised authority split: Odoo Copilot / Genie / Document Intelligence

### Odoo Copilot

Authority surface for:
- transactional/process guidance inside Odoo
- record-aware user assistance
- governed proposal-first assistance
- ERP workflow explanation and next-step routing

Runtime: Azure AI Foundry Agent Service (`data-intel-ph`)
Module: `ipai_odoo_copilot`
Consumption: Discuss bot, systray widget, HTTP API

### Databricks Genie

Authority surface for:
- conversational analytics over curated governed data
- KPI and operational question answering
- non-transactional analytical assistance
- natural-language-to-SQL over Unity Catalog datasets

Runtime: Databricks SQL warehouse (Pro or Serverless)
Prerequisite: Unity Catalog, curated gold marts, business definitions

### Document Intelligence assistant

Authority surface for:
- document extraction (invoices, receipts, forms, statements)
- OCR/layout/field capture
- review-assist workflows
- structured data output for downstream processing

Runtime: Azure AI Document Intelligence (`docai-ipai-dev`)
Mode: Extract + human review (no autonomous posting)

### Azure AI Foundry

Authority surface for:
- governed agent runtime
- retrieval/inference/tool orchestration
- endpoint/evaluation layer
- thread management and observability

Runtime: Foundry project `data-intel-ph` (East US 2)
Connections: AI Search, Azure OpenAI (to be wired)

---

## Boundary rules

1. **Odoo Copilot does NOT do analytics**. Questions about KPIs, trends, and aggregated data go to Genie.
2. **Genie does NOT execute ERP transactions**. It reads curated data, never writes to Odoo.
3. **Document Intelligence does NOT auto-post**. It extracts and routes to review queues.
4. **Foundry is the orchestration layer**, not a user-facing surface. Users interact with Copilot, Genie, or DocAI — never directly with Foundry.

---

## Current launch rule

Until Stage 3 retrieval and runtime hardening are complete, the allowed release posture remains:
- internal beta
- trusted users only
- read-only advisory by default

GA blockers are tracked in:
- `docs/runbooks/ODOO_AZURE_GENIE_GO_LIVE_CHECKLIST.md` §11
- `docs/delivery/ODOO_AZURE_GENIE_GO_LIVE_CHECKLIST.md` §Go-Live Decision Matrix
- `ssot/ai/go_live_posture.yaml`

---

## Foundry Go-Live Tool Envelope

The Foundry tool catalog exposes 35+ connectors. First-wave go-live uses a **controlled subset** — 9 tools across 4 assistant profiles. Remaining tools are deferred until first-wave stability is proven.

### First-Wave Tools (enable now)

| Tool | Auth Mode | Category |
|------|-----------|----------|
| GitHub | OAuth | Code/repo |
| Vercel | OAuth | Deployment |
| Azure DevOps MCP Server (preview) | OAuth | Planning/CI |
| Foundry MCP Server (preview) | Managed identity | Agent runtime |
| Azure Databricks Genie | Managed identity | Analytics |
| Azure Database for PostgreSQL | Managed identity | Operational data |
| Supabase | OAuth / key | App backend |
| Azure Managed Grafana | Managed identity | Observability |
| Azure MCP Server | Managed identity | Platform context |

### Enable Next (after first-wave stability)

| Tool | Trigger |
|------|---------|
| Azure Managed Redis | Agent memory / semantic cache need |
| Azure Language in Foundry Tools | NLP pipeline need |
| Selected Work IQ tools | Concrete workflow requirement |

### Deferred (not first-wave dependencies)

Work IQ Mail, Calendar, Teams, SharePoint, Word, OneDrive, Copilot. Microsoft 365 Admin Center. Dataverse, Pipedream, ClickUp, Atlassian, Infobip, Morningstar, Marketnode, MiHCM.

**Rationale**: These expand blast radius, auth complexity, and governance surface. Enable per-tool only when a concrete workflow justifies the cost.

### Tool Profiles

Four assistant surfaces, each with a distinct tool envelope:

#### `landing_public_assistant`

| Property | Value |
|----------|-------|
| **Enabled tools** | None (docs-grounded only) |
| **Action mode** | None — advisory only |
| **Tenant scope** | None — anonymous/public |
| **Auth** | No identity token required |

The public assistant must remain non-tenant-aware, non-action-capable, and docs-grounded. Foundry tools are NOT exposed to this surface.

#### `odoo_copilot_internal_beta`

| Property | Value |
|----------|-------|
| **Enabled tools** | Foundry MCP Server, GitHub, Vercel, Azure DevOps MCP Server, Azure Managed Grafana, Azure MCP Server |
| **Action mode** | Fail-closed (read-only default, write requires explicit allowlist) |
| **Tenant scope** | Trusted internal users only |
| **Auth** | Odoo user session + Entra OAuth for tool access |

Provides code/repo context, deployment context, DevOps context, runtime/ops context, and Foundry-native evaluation visibility. No Microsoft 365 action surfaces.

#### `data_intelligence_assistant`

| Property | Value |
|----------|-------|
| **Enabled tools** | Azure Databricks Genie, Azure Database for PostgreSQL, Supabase, Azure Managed Grafana |
| **Action mode** | Read-only |
| **Tenant scope** | Governed data plane |
| **Auth** | Managed identity for Azure-native, OAuth for Supabase |

Cleanest data plane: Genie for semantic Q&A, PostgreSQL for operational data, Supabase for control-plane context, Grafana for observable metrics. Separated from ops and admin tooling.

#### `ops_release_assistant`

| Property | Value |
|----------|-------|
| **Enabled tools** | GitHub, Vercel, Azure DevOps MCP Server, Azure MCP Server, Azure Managed Grafana, Foundry MCP Server |
| **Action mode** | Controlled (release checks, deployment validation, environment review) |
| **Tenant scope** | Ops internal |
| **Auth** | OAuth for dev tools, managed identity for Azure-native |

Best fit for release checks, deployment validation, failed deployment inspection, environment/status review, and cross-system reconciliation.

### Auth Policy

| Auth mode | When to use |
|-----------|-------------|
| **Managed identity** | Azure-native local MCP servers, platform/resource context, production infra |
| **OAuth** | Human-scoped work tools: GitHub, Vercel, Azure DevOps MCP, selective Work IQ |
| **Key-based** | Avoid for first-wave. Use only where no cleaner identity option exists |

Enforce identity policy **per profile**, not by accepting connector defaults.

---

*Last updated: 2026-03-23*
