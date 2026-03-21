# PRD — agent-platform

## Status
Draft

## Summary

Create the missing canonical `agent-platform` repository that owns the runtime execution layer for the InsightPulseAI agent system.

This repo separates runtime orchestration and task execution from static agent definitions. It standardizes how agents run, how tools are invoked, how state is persisted, how policy checks are applied, and how execution evidence is captured.

## Problem

Current repo boundaries are misaligned:

- `agents` is carrying runtime/orchestration language it should not own
- runtime logic risks being scattered across `agents`, `automations`, `platform`, and app repos
- orchestration patterns are implied by prompts and docs rather than encoded as explicit runtime contracts
- there is no canonical home for task ledgers, run lifecycle, or runtime/provider adapters

This creates drift, duplicated logic, and weak operational traceability.

## Goals

1. Establish `agent-platform` as the sole canonical runtime/orchestration repo.
2. Encode explicit orchestration patterns and execution contracts.
3. Provide durable run/task/session state.
4. Standardize MCP-based tool invocation.
5. Integrate policy/judge steps into runtime flows.
6. Support multiple model/runtime adapters without changing workflow logic.
7. Produce execution evidence suitable for governance, debugging, and go-live review.

## Non-Goals

- Replacing the `agents` repo
- Replacing `automations` or n8n
- Replacing `platform` as SSOT/control plane
- Replacing `odoo` business logic
- Building all end-user UI in this repo
- Collapsing every AI-related artifact into one repo

## Primary Users

- platform/runtime engineers
- agent workflow authors
- application integrators
- operators / on-call maintainers
- evaluators and policy reviewers
- cross-repo maintainers integrating runtime into Odoo, web, and platform surfaces

## Functional Requirements

### FR-1 — Run lifecycle
The system must manage agent runs with explicit states such as queued, running, blocked, waiting, failed, completed, cancelled.

### FR-2 — Task ledger
The system must maintain a durable task ledger for all multi-step or long-running executions.

### FR-3 — Orchestration pattern selection
Each workflow must declare its orchestration mode explicitly:
- sequential
- concurrent
- maker-checker
- handoff
- magentic

### FR-4 — MCP tool integration
The runtime must invoke shared tools through MCP contracts where reusable tools exist.

### FR-5 — Policy/judge integration
The runtime must support pre-execution, in-flight, and post-execution policy/judge hooks.

### FR-6 — Runtime adapters
The platform must support adapter-based execution across approved runtimes/providers without rewriting business workflows.

### FR-7 — Durable execution state
The runtime must persist task state, handoffs, tool results, policy decisions, and completion evidence to durable storage.

### FR-8 — Event integration
The runtime must emit events/webhooks that can be consumed by `automations` / n8n and adjacent systems.

### FR-9 — Operational control
Operators must be able to inspect run state, failure state, retryability, and evidence.

### FR-10 — Cross-repo contract enforcement
The repo must make clear which responsibilities belong to `agents`, `platform`, `automations`, `odoo`, and `web`.

## Non-Functional Requirements

### NFR-1 — Security
Azure-hosted runtime surfaces must use Entra-backed identity and retrieve production secrets via Key Vault.

### NFR-2 — Auditability
Every run must have durable traceability: IDs, timestamps, actor/runtime, tools used, policy outcomes, and final disposition.

### NFR-3 — Idempotency
Retries and duplicate event handling must be safe by design.

### NFR-4 — Modularity
Runtime adapters and tool adapters must be swappable behind stable contracts.

### NFR-5 — Scale
The system must not rely on in-memory-only state for production operation.

### NFR-6 — Explicitness
No workflow may depend on hidden prompt-only orchestration logic for critical execution behavior.

## Supported Delivery Surfaces

- **Microsoft 365 Copilot** (Enterprise assistant)
- **Copilot Studio** (Custom agent builder/extensibility)
- **Enterprise Channels**: Teams, Outlook, Excel, Word, PowerPoint agent-enabled workflows.

## Reference Implementations (Canonical Patterns)

1.  **Finance Q&A Agent**:
    - **Scenario**: Employee self-service for finance policy, status, and reporting.
    - **Integration**: Knowledge base + ERP/Odoo connection.
    - **Runtime**: `agent-platform` for task routing, escalation, and logging.
2.  **Balance Sheet Reconciliation Agent**:
    - **Scenario**: Ensure accurate balance sheets by detecting variances and automating corrections.
    - **Inputs**:
        - Ledger and balance sheet entries (CSV, JSON)
        - Bank and intercompany statements (PDF, CSV)
        - Month-end checklist and reconciliation policies (DOC, XLSX)
    - **Workflow steps**:
        1.  **Pull Financial Data**: Automated multi-source ingestion.
        2.  **Reconcile Cross-System**: Align transactions across ledgers/entities.
        3.  **Detect Missing Records**: Identify gaps and currency mismatches.
        4.  **Analyze Root Cause**: Correlate timing vs. missing entry issues.
        5.  **Track Reconciliation**: Route unresolved issues for review.
        6.  **Monitor Continuously**: Spot trends and prevent downstream errors.
    - **Integration**: Direct ERP/Odoo-backed actions + analytical lake (ADLS/Databricks).
    - **Runtime**: Durable task ledgering and root-cause analysis workflows.

## Odoo + M365 Copilot Capability Map

### Foundational Productivity (M365 "Top 10")
| Capability | Odoo Integration Point | Example Finance Prompt |
|------------|------------------------|------------------------|
| **Recap Meeting** | `mcp-jobs` / `taskbus` | "Summarize the budget review meeting and update the Odoo project status." |
| **Summarize Document** | `addons/ipai` / Odoo Documents | "Summarize this vendor contract and extract key T&Cs into the Odoo Purchase Order." |
| **Summarize Thread** | Odoo Chatter / Mail | "Give me a recap of the internal discussion on Invoice #1234." |
| **Draft Email** | Odoo Mail / Outlook | "Draft an overdue payment reminder for [Customer] based on their current balance." |
| **Formula Help** | Odoo Spreadsheet / Pivot | "How do I calculate the variance between actual and budgeted spend in this view?" |

### Strategic Finance Capabilities (Industry KPIs)
| KPI / Scenario | Odoo Data Source | Copilot Outcome |
|----------------|------------------|-----------------|
| **Days Sales Outstanding** | `account.move`, `account.payment` | Proactive collection coordination and automated payment reminders. |
| **Time to Close** | `account.move`, `account.bank.statement` | Automated reconciliation of intercompany and ledger entries. |
| **Risk Management** | `res.partner`, `res.config_settings` | Real-time audit of vendor compliance and regulatory standard alignment. |
| **Finance Q&A** | `ipai.knowledge`, `account.account` | Employee self-service for policy, budget status, and expense tracking. |
| **Variance Analysis** | `account.budget`, `account.analytic.line` | Dynamic reporting on spend-to-budget ratios with root-cause insights. |

## External Enterprise Adapters

### SAP Integration

SAP is an external enterprise system integrated through thin adapter services.

**Approved adapter patterns**:
- **SAP Cloud SDK on Azure Functions** — event/webhook-style, OData access, edge adapter
- **SAP Cloud SDK on Azure App Service** — longer-lived service adapter for sustained SAP connectivity

**Reference only (not canonical baseline)**:
- SAP CAP on Azure App Service — app-pattern reference only; Cosmos DB for PostgreSQL does not match platform doctrine

**Excluded (not in scope)**:
- SAP NetWeaver 2-tier/3-tier templates
- SAP LaMa templates
- SAP HANA Azure NetApp Files templates
- S/4HANA fully activated appliance
- SAP file server / ILM store templates

These are for hosting SAP landscapes, not for integrating with SAP as an external system.

## Success Metrics

- `agent-platform` exists as a separate canonical repo with approved boundary docs
- at least one runtime task ledger is operational
- at least one MCP tool path is operational
- at least one maker-checker workflow is encoded in runtime contracts
- at least one sequential production-class flow is encoded in runtime contracts
- run evidence is queryable and reproducible
- `agents` repo description and usage no longer imply runtime ownership

## Risks

- repo boundaries remain blurred if integrations are not updated
- n8n may be overused as runtime logic instead of edge orchestration
- prompt-level behavior may continue to bypass explicit contracts
- provider/runtime logic may sprawl if adapter boundaries are weak
- control-plane duplication may emerge if `platform` and `agent-platform` responsibilities are not enforced
