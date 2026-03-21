# Constitution — agent-platform

## Status
Draft

## Purpose

`agent-platform` is the canonical runtime and orchestration repository for the InsightPulseAI agent estate.

It exists to separate **agent execution** from **agent definitions**.

## Non-Goals

- Replacing `agents` repo persona definitions
- **Replacing Microsoft 365 Agents SDK** (SDK is a channel layer)
- End-user chat UI components
- Direct model training/fine-tuning (Foundry/Databricks)
- `agents` owns personas, skills, judges, evals, registries, and prompt contracts.
- `agent-platform` owns orchestration, task ledgering, execution contracts, runtime adapters, and control-room integrations.

## Repo Boundary

This repository **owns**:

- agent runtime orchestration
- task ledger and run lifecycle contracts
- session and execution state contracts
- orchestration-pattern selection and enforcement
- MCP tool runtime integration
- runtime adapters for model/provider execution
- **NOT** user-facing channel logic (M365, Teams, Slack)
- control-room APIs and operational runtime glue
- policy/judge invocation hooks during execution
- execution evidence, traceability, and run observability

This repository **does not own**:

- generic agent personas, skills, or eval suites
- business workflow automation owned by `automations`
- transactional ERP logic owned by `odoo`
- platform SSOT or secret authority owned by `platform`
- analytics engineering owned by `data-intelligence`
- end-user web product surfaces owned by `web`
- broad cross-repo architecture docs owned by `docs`

## Mandatory Architecture Rules

1. **MCP is mandatory** for reusable cross-agent tool interoperability.
2. **Durable external state is mandatory**. No critical run state may exist only in memory.
3. **Pattern choice must be explicit per workflow**:
   - sequential
   - concurrent
   - maker-checker / group chat
   - handoff
   - magentic
4. **Sequential is the default** for deterministic finance, compliance, and transaction-style flows.
5. **Maker-checker is mandatory** for policy, release, compliance, and spec review loops.
6. **Handoff is only for dynamic specialist routing**, not fixed routing.
7. **Magentic is reserved** for open-ended adaptive planning and control-room workloads.
8. **n8n is orchestration-adjacent, not the runtime core**. `agent-platform` integrates with it but does not collapse into it.
9. **Microsoft Entra ID is the identity plane** and **Azure Key Vault is the secret authority** for Azure-hosted runtime surfaces.
10. **Runtime truth must be evidenced** through logs, traces, and run artifacts.

### 3. Microsoft 365 Agents SDK / Copilot Studio
- `agent-platform` may expose runtime services to **Microsoft 365 Copilot**, **Copilot Studio**, and **Copilot Agents** via the SDK.
- These are approved **enterprise delivery surfaces** for finance use cases.
- The SDK/Studio layer is a **channel layer**, never the orchestration authority.
- Integration must leverage `agent-platform` execution contracts.

> **Doctrine**: Microsoft 365 Copilot, Copilot Studio, and Copilot Agents are governed enterprise delivery surfaces for finance use cases; `agent-platform` remains the canonical runtime/orchestration layer behind them.

### 4. SAP Integration

- SAP is an **integrated external enterprise surface**, not a hosted runtime.
- Approved adapter patterns: **Azure Functions** or **App Service** with **SAP Cloud SDK** (OData/RFC).
- SAP infrastructure hosting templates (NetWeaver, HANA, LaMa, S/4HANA) are **non-canonical** unless SAP workload hosting is explicitly approved.
- SAP adapters are owned by `agent-platform` (function-style edge) or `automations` (workflow glue).

## Platform Invariants

- All execution contracts are machine-readable.
- All runtime mutations are idempotent or replay-safe.
- Every run has a stable ID, owner, status, and evidence trail.
- Tool calls are mediated through explicit contracts, not hidden prompt assumptions.
- Runtime/provider switching must be adapter-based, not hard-coded into workflow logic.
- Policy failures must be explicit, durable, and reviewable.

## Cross-Repo Contracts

### `agents`
Consumes skills, judge policies, eval criteria, and prompt contracts.

### `platform`
Provides control-plane backing services, vault references, runtime metadata, and backend support surfaces.

### `automations`
Receives webhooks/events and hosts n8n-managed workflow automations outside the core runtime.

### `odoo`
Consumes runtime services for copilot, transactional assistance, and business-process execution.

### `data-intelligence`
Consumes runtime telemetry and produces analytical views of execution behavior; does not own runtime orchestration.

### `web`
Owns user-facing control-room and operator surfaces that talk to this repo's APIs.

## Non-Goals

This repository is not:

- the canonical home for all prompts
- the canonical home for all workflow JSONs
- the control-plane secret store
- the analytics warehouse
- the business SoR
- a generic monorepo dump for all AI-related code

## Acceptance Criteria

This repo is only considered established when:

- runtime boundaries are separated from `agents`
- MCP tool integration is operational
- durable task/run state exists
- orchestration patterns are encoded explicitly
- policy/judge hooks are wired
- runtime evidence is produced for every execution class
- ownership boundaries with `platform`, `automations`, `agents`, and `odoo` are documented and enforced
