# Odoo Copilot on Azure — Constitution

## Purpose

Define hard boundaries and non-negotiables for the Azure-native Odoo Copilot — a governed action layer and conversational interface that exposes business capabilities through the Microsoft Agent Framework and MCP-based tool contracts.

## Platform Role

- **Microsoft Agent Framework** is the agent/tool platform, not the ERP source of truth.
- **Odoo** remains the transactional source of truth for ERP, finance, CRM, and approvals.
- **Supabase** remains the control plane for identity mapping, sync state, integration metadata, and lightweight APIs.
- **Databricks** is an optional intelligence plane for analytics, forecasting, anomaly detection, and summarized writebacks — not required for core copilot functionality.
- **Plane** remains the workspace/docs/project coordination layer.

## Non-Negotiables

### 1. Agent Model

- All business-facing copilot capabilities must map to one of:
  - **Transactional** — create, approve, reject, update records
  - **Navigational** — deep-link to records, open views, surface blockers
  - **Informational** — summarize, explain, answer policy questions from grounded sources
- No freeform business action is allowed without an explicit tool/action contract.
- Tool access must be least-privilege and auditable.

### 2. Azure Architecture Rules

- **Microsoft Agent Framework** is the default agent orchestration layer, hosted via ASP.NET Core or Durable Azure Functions.
- **Agents** are open-ended, tool-using, context-aware processes that can reason about next steps.
- **Workflows** are deterministic multi-step processes with defined inputs/outputs.
- **MCP** is the standard tool protocol for external/internal tool connectivity.
- **API Management** is the preferred gateway for externally consumable agent endpoints.
- **Container Apps** is the default custom runtime host for supporting web/API components and custom agent workloads.
- **Managed identity** is required for Azure-native service-to-service access.
- **Key Vault** stores all secrets — no hardcoded credentials.

### 3. Security and Compliance

- No direct unrestricted database access from copilots.
- Sensitive prompts, responses, tool arguments, and tool outputs must not be logged in production unless explicitly approved.
- Role-aware access and Odoo permission parity are mandatory for all actions.
- All tool invocations are audit-logged with: user, tool, arguments (redacted), timestamp, result status.

### 4. Source of Truth Boundaries

| System | Owns | Does NOT Own |
|--------|------|-------------|
| Odoo | ERP records, finance, CRM, approvals, workflows | Agent orchestration, analytics, docs |
| Supabase | Identity map, sync state, integration events, lightweight APIs | Business logic, ERP data |
| Databricks | Analytics marts, forecasts, anomaly signals | Transactional records, approval state |
| Plane | Workspaces, docs, project coordination, SOPs | ERP data, financial records |
| Agent Framework | Agent orchestration, tool catalog, session state, middleware | Business data, computation |

### 5. Product Boundary

- Odoo Copilot is a governed action layer and conversational interface, NOT a replacement UI for all Odoo workflows.
- Documents, SOPs, and workspace knowledge may be grounded, but they do not supersede ERP truth.
- The copilot does not own business rules — it delegates to domain services.

### 6. Module Split

- **Odoo modules stay thin**: `ipai_copilot_*` modules expose API endpoints and tool contracts only.
- **Agent logic lives outside Odoo**: in `agents/odoo-copilot/` and `packages/tool-*`.
- **Agent Framework owns orchestration**: agent composition, workflow, session state, memory, middleware, tools.
- **MCP/tool contracts own integration shape**: typed schemas, error taxonomy, retry semantics.

### 7. Naming Conventions

- Spec slug: `odoo-copilot-azure`
- Odoo modules: `ipai_copilot_gateway`, `ipai_copilot_finance`, `ipai_copilot_compliance`, `ipai_copilot_workspace_bridge`
- Agent code: `agents/odoo-copilot/`
- Tool packages: `packages/tool-odoo/`, `packages/tool-supabase/`, `packages/tool-databricks/`, `packages/tool-plane/`

## Boundaries

### In Scope

- Governed transactional, navigational, and informational capabilities
- Microsoft Agent Framework agent orchestration and tool catalog
- Agent Framework runtime (agents, workflows, MCP, structured output, RAG, memory, middleware)
- MCP-based tool federation to Odoo, Supabase, Databricks, Plane
- Publication paths: Agent Framework, Microsoft 365 Copilot, Teams
- Thin Odoo modules for ERP tool exposure
- Observability via Azure Monitor / App Insights / OpenTelemetry

### Out of Scope

- Replacing Odoo UI wholesale
- Moving ERP truth into Agent Framework
- Duplicating Databricks marts into Odoo or Supabase
- Building ad-hoc tool calls with no contract or approval model
- Generic chatbot / chat-app boilerplate
