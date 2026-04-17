# Plan — agent-platform

## Status
Draft

## Architecture Decision

- `agent-platform` targets Azure Container Apps.
- `agents` exists as a library/registry.
- **M365 Copilot** serves as a productivity surface channel.

It sits between:

- static agent definitions in `agents`
- control-plane support in `platform`
- workflow automation in `automations`
- application integrations in `odoo` and `web`

## Target Repo Structure

```text
agent-platform/
  spec/
    agent-platform/
  docs/
    architecture/
    evidence/
  src/
    api/
    orchestration/
    ledger/
    runtime_adapters/
    mcp/
    policy/
    events/
    telemetry/
  tests/
    unit/
    integration/
    contract/
  scripts/
  config/
```

## Core Components

### 1. API / Control Layer

Provides runtime-facing APIs for run creation, task updates, retries, cancellation, inspection, and operator control.

### 2. Orchestration Engine

Encodes explicit orchestration patterns:

* sequential
* concurrent
* maker-checker
* handoff
* magentic

### 3. Task Ledger

Stores run/task/session state durably. This is the machine-readable execution spine.

### 4. Runtime Adapters

Supports provider/runtime execution through adapters. Primary Azure-oriented runtime integration is expected, but workflows must remain adapter-based rather than provider-hardcoded.

### 5. MCP Tool Layer

Provides tool registration, invocation, and execution mediation through MCP contracts.

### 6. Policy / Judge Layer

Invokes judges and policy checks from `agents` or adjacent policy surfaces during execution.

### 7. Event/Webhook Layer

Publishes runtime events for external consumers such as `automations` / n8n and adjacent systems.

### 8. Telemetry / Evidence Layer

Captures logs, traces, metrics, run artifacts, policy outcomes, and completion evidence.

### 2.5 Enterprise Assistant Channel Adapters
- **Component**: Microsoft 365 Agents SDK / Copilot Studio integration.
- **Role**: Delivery/channel adapter for M365 Copilot, Teams, and Web.
- **Finance Runtime APIs**:
    - Finance Q&A runtime contract (KB + ERP access).
    - Balance Sheet Reconciliation runtime workflow (multi-source matching).
    - **Agent-to-Agent Workflow Patterns**:
        - Ledger Matching Agent (Data alignment)
        - Variance Detection Agent (Gap identification)
        - Correction Suggestion Agent (Root-cause remediation)
- **Control Interface**: Handoff/escalation to workflow systems (n8n/Odoo).

### 2.6 Odoo & Data Source Connectors
- **Component**: Odoo ERP Connector (RPC/REST).
- **Meta-Data Mapping**:
    - `account.move` -> Invoices & Payments
    - `account.analytic.line` -> Cost Centers & Budgeting
    - `res.partner` -> Customer/Supplier Entities
    - `ipai.knowledge` -> Finance Policy KB
- **Contract**: bi-directional sync/update capability for agent-initiated actions (e.g., "Suggest Journal Entry").

### 2.7 SAP Adapter Layer
- **Component**: Thin SAP integration adapter (Azure Functions or App Service).
- **SDK**: SAP Cloud SDK (TypeScript) for OData/RFC access.
- **Pattern**: Function-style edge adapter for event/webhook integration; service-style for sustained connectivity.
- **Scope**: Read/write SAP business objects via OData. Does NOT host SAP runtime.
- **Excluded**: NetWeaver/HANA/LaMa/S/4HANA infrastructure templates are non-canonical.

## 3. Durable Contracts

### Run

Fields:

* run_id
* workflow_id
* orchestration_pattern
* owner
* status
* created_at
* started_at
* ended_at
* correlation_id

### Task

Fields:

* task_id
* run_id
* parent_task_id
* assigned_runtime
* assigned_agent
* status
* input_ref
* output_ref
* retry_count
* handoff_target

### Tool Invocation

Fields:

* tool_call_id
* run_id
* mcp_server
* tool_name
* input_hash
* result_ref
* status

### Policy Decision

Fields:

* decision_id
* run_id
* stage
* policy_name
* result
* reviewer
* evidence_ref

## Pattern Mapping

### Sequential

Default for:

* AP invoice processing
* bank reconciliation
* expense liquidation
* compliance document flow
* deterministic enterprise action chains

### Concurrent

Default for:

* parallel specialist analysis
* multi-perspective scoring
* independent enrichment branches

### Maker-checker

Required for:

* policy validation
* release gates
* spec review
* compliance approval loops

### Handoff

Use when:

* the correct specialist is not known up front
* route selection emerges during execution

### Magentic

Reserve for:

* open-ended remediation
* control-room / manager-led coordination
* agent-factory style adaptive planning

## Cross-Repo Integration Plan

### `agents`

Consume:

* skills
* judges
* eval metadata
* prompt contracts

### `platform`

Consume:

* control-plane services
* vault references
* runtime metadata backing services

### `automations`

Integrate:

* inbound/outbound webhook events
* edge workflow callbacks
* notifications and scheduled automation

### `odoo`

Expose:

* copilot/runtime services
* workflow callbacks
* transactional assistant contracts

### `web`

Expose:

* control-room APIs
* run inspection endpoints
* operator action endpoints

## Security Model

* Entra-backed identity for Azure-hosted runtime surfaces
* Key Vault as production secret authority
* Azure RBAC as default authorization model for secret access
* no production secrets stored in repo
* explicit credential boundaries between runtime, control plane, and automation plane

## Observability Model

Every execution class must emit:

* structured run logs
* task state transitions
* tool invocation traces
* policy decisions
* failure reasons
* completion artifacts

## Phased Delivery

### Phase 0

* create repo and spec bundle
* define repo boundaries and contracts

### Phase 1

* implement task ledger contracts
* implement run lifecycle

### Phase 2

* implement orchestration engine with sequential + maker-checker first

### Phase 3

* wire MCP tool contracts

### Phase 4

* add runtime adapters and event/webhook integrations

### Phase 5

* add operator-facing evidence/telemetry and hardened policy integration

## WS6 — Foundry topology normalization

Scope:
- Record current resource / project / hub / standalone OpenAI inventory in `ssot/foundry/runtime_inventory.yaml`
- Mark one canonical resource + project pair (`data-intel-ph-resource` / `data-intel-ph`)
- Classify legacy hub-backed assets (`aifoundry-ipai-dev`, `proj-ipai-claude`) as transitional
- Define package-boundary policy for Python in `ssot/foundry/python_sdk_surfaces.yaml`
- Bind app integrations to canonical control-plane objects
- Distinguish UI evidence from control-plane and runtime evidence

## CLI Boundary Enforcement

- Approved Azure CLI surfaces for this platform:
  - `cognitiveservices` — Foundry model deployment and endpoint management
  - `ml` — only where Microsoft docs explicitly require it for Foundry project connection flows
- Excluded: `az workloads` (SAP-specific Virtual Instance management, benchmark-only for this platform)
- Agent Service references must use Foundry project endpoints rather than legacy hub-based connection strings
- Runbooks, bootstrap scripts, and CI pipelines must not include `az workloads` commands

## Foundry Reference Materials

The Microsoft sample repo `microsoft/microsoft-foundry-e2e-js` is a **learning reference** (JS/TS buildathon quest), not a deployment template. The canonical IPAI implementation remains Odoo + Azure-native infra + Foundry-backed agents. The adoptable artifact from that repo is the four-stage lifecycle model (selection → optimization → observability → security), which is encoded in `ssot/foundry/runtime_inventory.yaml` under `platform_framing.lifecycle_stages`.

## Open Constraints

* no runtime ownership may remain implicitly in `agents`
* n8n remains edge orchestration, not core runtime
* workflow behavior must be explicit in code/contracts, not hidden in prompts
