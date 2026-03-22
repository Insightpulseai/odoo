# Constitution: ipai_odoo_copilot

> **Status**: Draft
> **Purpose**: Thin Odoo bridge module for an external AI runtime (Azure AI Foundry).
> **Scope**: Defines the non-negotiable principles that govern the design, implementation, and operation of the `ipai_odoo_copilot` module.

---

## Governing Principles

### 1. Odoo remains the transactional system of record

All financial, HR, project, and operational data is authored and persisted in Odoo.
The copilot module never duplicates, caches, or shadows Odoo transactional state.
It reads context on demand and delegates intelligence to an external runtime.

### 2. Foundry is the primary AI and agent plane

Azure AI Foundry (or a compatible provider) hosts models, prompt orchestration,
tool definitions, grounding indexes, and evaluation pipelines.
The Odoo module does not embed inference logic, prompt templates, or model
selection heuristics. It packages context, delegates, and renders results.

### 3. Thin-bridge architecture only

The module's Python footprint inside Odoo is limited to:

- Context packaging (reading Odoo data the user is allowed to see).
- Request serialization to an external endpoint.
- Response deserialization and rendering in the Odoo UI.
- Audit logging of every request/response pair.
- Admin configuration (endpoint URL, feature flags, policy toggles).

No LLM libraries, no vector stores, no embedding pipelines, no RAG indexes
run inside the Odoo process. The module is a bridge, not a platform.

### 4. Identity-first integration (Entra)

Every copilot request carries the authenticated Odoo user's identity.
The external runtime validates identity via Microsoft Entra ID tokens.
No anonymous or system-only copilot calls are permitted in production.
The module must support Entra OIDC token acquisition or relay for
user-scoped authorization at the Foundry layer.

### 5. Odoo action safety (read-only default)

By default the copilot may only read Odoo data and present suggestions.
Write actions (create, update, confirm, post) require:

- An explicit admin-configured policy allowlist.
- A user confirmation step in the UI before execution.
- An audit trail entry linking the action to the copilot session.

No implicit or automatic writes. The user is always the final authority.

### 6. Analytics context must be governed

When the copilot grounds its answers on analytics data (Databricks lakehouse,
Power BI datasets, or external indexes), the data lineage must be traceable.
The module does not query analytics sources directly; it delegates to the
Foundry runtime, which is responsible for governed data access via Unity Catalog
or equivalent access-control layers.

### 7. Delivery must be Odoo.sh-aligned, Azure-native

The module must install and operate on both:

- Azure Container Apps (canonical production runtime).
- Odoo.sh (for customers or partners using Odoo's managed hosting).

This means: no Azure-only SDK dependencies in the Odoo process, no Container
Apps sidecar assumptions. Azure-native features (Key Vault, Managed Identity,
Front Door) are consumed at the infrastructure layer, not imported into module
Python code.

### 8. Finance-first release discipline

The first production release targets finance operators exclusively:

- Month-end close Q&A.
- Reconciliation assistance.
- Collections follow-up drafting.
- Variance analysis summaries.

All other domains (HR, project, helpdesk, sales) are deferred until the
finance vertical is validated, measured, and stable.

### 9. No embedded reconciliation engine

The copilot assists with reconciliation by surfacing context, suggesting
matches, and drafting journal entries for human review. It does not execute
reconciliation logic inside the module. Reconciliation remains an Odoo-native
operation (manual or via OCA `account_reconcile_oca`). The copilot is an
advisor, not an engine.

---

## In Scope

| Area | What the module does |
|------|---------------------|
| UI entry points | Systray icon, form-view helper button, chat panel |
| Context packaging | Reads active record, user role, company, and related data |
| External delegation | Sends structured request to Foundry endpoint |
| Response rendering | Displays assistant text, suggested actions, citations |
| Audit logging | Persists every request/response with user, timestamp, model |
| Admin configuration | Endpoint URL, feature flags, action policy, provider selection |
| Finance Q&A | Month-end close, reconciliation, collections, variance |

## Out of Scope

| Area | Why excluded |
|------|-------------|
| Model hosting | Foundry responsibility |
| Prompt engineering | Foundry tool definitions and system prompts |
| Vector indexing / RAG | Foundry or Databricks responsibility |
| Direct database queries to analytics | Governed by Databricks Unity Catalog |
| Identity provider management | Entra ID configuration, not module code |
| Reconciliation execution | Odoo-native or OCA module |
| Multi-tenant SaaS metering | Platform-level concern, not module-level |
| Non-finance domains (Release 1) | Deferred to Release 2+ |

---

## Non-Negotiable Constraints

1. **CE-only**: The module must not depend on Odoo Enterprise modules or odoo.com IAP services.
2. **No secrets in code**: All credentials (API keys, client secrets, managed identity tokens) are resolved from environment variables or Azure Key Vault at runtime. Never committed to source.
3. **No LLM in process**: No `openai`, `anthropic`, `langchain`, `llama-index`, or similar libraries in the module's Python dependencies.
4. **Audit completeness**: Every copilot interaction (including failures and timeouts) must produce an audit record.
5. **User consent**: No copilot action modifies Odoo state without explicit user confirmation.
6. **Graceful degradation**: If the external runtime is unavailable, the module must not break the Odoo UI. It must display a clear "service unavailable" state and allow normal ERP operation.
7. **OCA compatibility**: The module must coexist with OCA accounting, project, and web modules without conflict.
8. **Naming convention**: Module technical name is `ipai_odoo_copilot`. All models use the `ipai.copilot.` prefix. All XML IDs use the `ipai_odoo_copilot.` namespace.
9. **Single responsibility**: This module is the bridge. Foundry tool definitions, analytics grounding, and identity federation are owned by their respective infrastructure layers.

---

*Last updated: 2026-03-22*
