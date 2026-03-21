# PRD — Odoo Copilot Agent Framework

## Problem

The current AI consolidation (PRs #594-#598) established one Foundry agent with five capability modes. But the single-agent/five-mode split conflates user-facing advisory with internal ops, and read-only with write-capable flows. This creates:

- No isolation between customer-facing and internal-only contexts
- Write access modes (Transaction, Creative) share instruction space with read-only modes
- No deterministic routing — mode selection relies on prompt classification
- Capability packs (Databricks, fal, Marketing) have no defined attachment points
- No evaluation framework per agent role

## Solution

Split the single agent into **three logical agents + one deterministic router**, each with bounded scope, dedicated evaluation criteria, and clear tool/write boundaries.

## Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │  Microsoft Foundry (data-intel-ph)            │
                    │  Physical agent: ipai-odoo-copilot-azure      │
                    │                                                │
                    │  ┌─────────────────────────────────────────┐  │
                    │  │ Router (deterministic, no LLM)          │  │
                    │  │ Rules: channel + model + role + intent   │  │
                    │  └────┬──────────┬──────────┬──────────────┘  │
                    │       │          │          │                  │
                    │  ┌────▼────┐ ┌───▼────┐ ┌──▼──────────┐     │
                    │  │Advisory │ │  Ops   │ │  Actions    │     │
                    │  │(user)   │ │(internal│ │(controlled  │     │
                    │  │read-only│ │read-only│ │writes)      │     │
                    │  └─────────┘ └────────┘ └─────────────┘     │
                    │                                                │
                    │  Capability Packs (attached inside agents):    │
                    │  ├── Databricks Intelligence (Advisory+Ops)    │
                    │  ├── fal Creative Production (Actions)         │
                    │  └── Marketing Strategy (Advisory)             │
                    └──────────────────────────────────────────────┘
                                       │
                           Responses API (/openai/v1/)
                                       │
          ┌────────────────────────────┼────────────────────────┐
          │                            │                        │
    ┌─────▼──────┐          ┌─────────▼────────┐     ┌────────▼──────┐
    │ SDK Direct │          │ REST Direct      │     │ APIM Gateway  │
    │ (internal  │          │ (n8n, adapters)  │     │ (enterprise   │
    │  services) │          │                  │     │  front door)  │
    └────────────┘          └──────────────────┘     └───────────────┘
```

## Target top-level components

| Component | Form | Purpose |
|---|---|---|
| `ipai-odoo-copilot-advisory` | Foundry prompt agent | user-facing grounded Q&A, guidance, strategy |
| `ipai-odoo-copilot-ops` | Agent Framework agent | internal diagnostics, read-only operational inspection |
| `ipai-odoo-copilot-actions` | Agent Framework agent | controlled execution and bounded writes |
| `ipai-odoo-copilot-router` | Agent Framework workflow | deterministic routing, approvals, checkpoints, handoffs |

## Agent matrix

| Component | Primary responsibility | Core tools / packs | Allowed actions | Hard blocks | Required evaluations |
|---|---|---|---|---|---|
| `ipai-odoo-copilot-advisory` | user-facing Q&A, grounded explanation, strategy guidance | Azure AI Search / Foundry knowledge, Marketing Strategy & Insight Pack, Databricks Intelligence Pack | explain, summarize, recommend, compare, hand off | no writes, no admin/security changes, no direct publish/export, no finance execution | Task Completion, Task Adherence, Intent Resolution, Relevance, Groundedness where applicable |
| `ipai-odoo-copilot-ops` | internal diagnostics, read-only operational inspection | read-only Odoo tools, Databricks monitoring/health, infra/runtime reads | inspect, diagnose, compare state, summarize incidents, propose remediation | no record mutation, no secret changes, no role changes, no uncontrolled job execution | Task Completion, Task Adherence, Tool Selection, Tool Call Success, Tool Output Utilization |
| `ipai-odoo-copilot-actions` | controlled execution and bounded writes | approved Odoo write tools, approved Databricks job/app actions, fal Creative Production Pack actions | create/update allowed records, trigger approved jobs, launch approved creative runs, prepare exports, write evidence | no unrestricted writes, no destructive ops, no policy bypass, no silent batch execution | Tool Selection, Tool Input Accuracy, Tool Call Success, approval compliance, unauthorized-action refusal |
| `ipai-odoo-copilot-router` | deterministic routing, approvals, handoffs, checkpointing | workflow graph, approval steps, evidence correlation | route, pause for approval, resume, hand off, checkpoint, collect trace context | no free-form business reasoning, no broad vendor logic, no direct domain mutation | routing correctness, handoff success, approval compliance, end-to-end task completion |

## Three Agents

### 1. Advisory Agent (User-Facing, Read-Only)

| Attribute | Value |
|-----------|-------|
| **Audience** | End users, portal visitors, livechat |
| **Write access** | None |
| **Foundry tools** | `search_records`, `read_record`, `search_knowledge`, `web_search` |
| **Memory** | `user_profile` (personalization) |
| **Replaces modes** | Ask, Livechat |
| **Capability packs** | Databricks Intelligence, Marketing Strategy & Insight, fal Creative (read-only) |
| **Evaluation** | Groundedness ≥ 0.8, Relevance ≥ 0.85, Citation accuracy ≥ 0.9 |
| **Guardrails** | No PII in responses, no financial advice disclaimers, cite sources |

### 2. Ops Agent (Internal, Read-Only)

| Attribute | Value |
|-----------|-------|
| **Audience** | Internal staff, admin, finance team |
| **Write access** | None |
| **Foundry tools** | `search_records`, `read_record`, `search_knowledge`, `code_interpreter`, `file_search` |
| **Memory** | `chat_summary` (session continuity) |
| **Replaces modes** | Authoring (read/analysis portion) |
| **Capability packs** | Databricks Intelligence, Marketing Strategy & Insight, fal Creative (read-only) |
| **Evaluation** | Groundedness ≥ 0.85, Coherence ≥ 0.9, Data accuracy ≥ 0.95 |
| **Guardrails** | No external data leakage, internal-only context, audit all queries |

### 3. Actions Agent (Controlled Writes)

| Attribute | Value |
|-----------|-------|
| **Audience** | Authorized users with write roles |
| **Write access** | Bounded CRUD (model allowlist + field allowlist + state constraints) |
| **Foundry tools** | All read tools + `create_draft`, `create_record`, `update_record`, `execute_action`, `image_generation`, `code_interpreter` |
| **Memory** | `chat_summary` (multi-step transaction continuity) |
| **Replaces modes** | Authoring (draft creation), Transaction, Creative |
| **Capability packs** | Databricks Intelligence, fal Creative Production, Marketing Strategy & Insight (light) |
| **Evaluation** | Action correctness ≥ 0.95, Safety (no unauthorized writes) = 1.0 |
| **Guardrails** | Approval gates, undo support, draft-first default, model/field allowlists |

## Deterministic Router

Routes requests to the correct agent without LLM inference:

| Signal | Advisory | Ops | Actions |
|--------|----------|-----|---------|
| Channel = livechat/portal | Yes | — | — |
| Channel = internal + intent = read | — | Yes | — |
| Channel = internal + intent = write | — | — | Yes |
| User role ∉ write_roles | Yes | Yes | Blocked |
| Model in write_allowlist | — | — | Yes |
| Explicit mode override | Honored | Honored | Honored |

## Capability packs (cross-agent attachment)

| Capability pack | Advisory | Ops | Actions | Router |
|---|---:|---:|---:|---:|
| Databricks Intelligence Pack | Yes | Yes | Yes | Yes |
| fal Creative Production Pack | Yes | Yes | Yes | Yes |
| Marketing Strategy & Insight Pack | Yes | Yes | Light | No |
| BIR Compliance Pack | Yes | Read-only | Write (approval) | Context |
| Document Intake & Extraction Pack | — | — | Yes | — |

## Foundry + Agent Framework split

- Foundry is the control plane for prompt agents, datasets, evaluations, tracing, and project-scoped resources.
- Agent Framework is the execution plane for graph workflows, checkpointing, middleware, and multi-agent orchestration.
- Do not add more than 3 agents + 1 workflow until eval coverage and tracing are stable.

## Capability Packs (Detail)

### Databricks Intelligence Pack

| Attribute | Value |
|-----------|-------|
| **Attaches to** | Advisory (read), Ops (read), Actions (job triggers), Router (routing context) |
| **Tools** | `databricks_sql_query`, `databricks_unity_search`, `databricks_dashboard_embed` |
| **Credentials** | `DATABRICKS_HOST`, `DATABRICKS_TOKEN` (Key Vault) |
| **Degrades** | Pack disabled if credentials absent; agents still work without Databricks tools |
| **Source refs** | Databricks SQL Connector, Unity Catalog, Genie, Lakeview |

### fal Creative Production Pack

| Attribute | Value |
|-----------|-------|
| **Attaches to** | Advisory (read/preview), Ops (read/preview), Actions (write/generate), Router (routing context) |
| **Tools** | `fal_image_generate`, `fal_video_generate`, `fal_style_transfer` |
| **Write tools** | Only available in Actions agent; Advisory/Ops get read-only preview access |
| **Credentials** | `FAL_KEY` (Key Vault) |
| **Degrades** | Falls back to Foundry built-in `image_generation` (DALL-E 3) |
| **Source refs** | fal.ai model catalog, UGC generation patterns |

### Marketing Strategy & Insight Pack

| Attribute | Value |
|-----------|-------|
| **Attaches to** | Advisory (full), Ops (full), Actions (light — prompt context only, no dedicated tools) |
| **Tools** | `web_search` (existing), `search_knowledge` (brand guidelines RAG) |
| **Light attachment** | On Actions, provides brand/campaign context in prompt but no Marketing-specific tool invocations |
| **Credentials** | None (uses existing Foundry built-ins) |
| **Degrades** | N/A (no external credentials needed) |
| **Source refs** | Smartly (creative automation), Quilt.AI (cultural intelligence), LIONS Marketing Assistant (effectiveness), Data Intelligence (analytics) |

### BIR Compliance Pack (Tax Pulse)

| Attribute | Value |
|-----------|-------|
| **Attaches to** | Advisory (full — informational), Ops (read-only — inspection), Actions (write — approval-gated), Router (context) |
| **Tools** | `bir_compliance_search`, `check_overdue_filings`, `compute_bir_vat_return`, `compute_bir_withholding_return`, `validate_bir_return`, `generate_alphalist`, `generate_efps_xml`, `generate_bir_pdf` |
| **Write tools** | Only available in Actions agent with `group_ipai_bir_approver` approval |
| **Credentials** | None (uses Odoo MCP + local rules engine) |
| **Degrades** | N/A (no external credentials needed) |
| **Knowledge** | `ph_rates_2025.json`, `vat.rules.yaml`, `ewt.rules.yaml`, BIR regulation knowledge store |
| **Workflow** | Odoo-native stages (Draft → Computed → Validated → Approved → Filed → Confirmed), Activities, task templates |
| **Spec** | `spec/tax-pulse-sub-agent/` |
| **Source refs** | TaxPulse-PH-Pack (ported), BIR Revenue Regulations, TRAIN Law |

### Document Intake & Extraction Pack

| Attribute | Value |
|-----------|-------|
| **Attaches to** | Actions (write — extraction + linking) |
| **Tools** | `document_extract`, `document_classify`, `document_link_record` |
| **Credentials** | `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT`, `AZURE_DOCUMENT_INTELLIGENCE_KEY` |
| **Degrades** | Pack disabled when credentials absent |
| **Status** | Planned |
| **Source refs** | Azure AI Document Intelligence (invoices, receipts, BIR attachments) |

## Ingress Paths

| Path | Purpose | Who | Governance |
|------|---------|-----|-----------|
| **Foundry Project Client** | config, connections, tracing, Foundry-native ops | internal control-plane services | Foundry RBAC + project scope |
| **OpenAI-compatible client** | agents, evals, responses, model calls | advisory, ops, actions runtime | project scope + deployment policy |
| **Direct REST** | adapters, n8n/webhooks, lightweight bridges | automation bridges, service adapters | APIM or service auth |
| **APIM AI gateway** | **required production front door** | **all production clients** | auth, quotas, throttling, telemetry |
| **Foundry Playgrounds** | rapid prototyping, validation | builders/operators only | **non-production only** |

## Ingress ownership by component

| Component | Primary ingress | Secondary ingress | Notes |
|---|---|---|---|
| Advisory | APIM → Foundry/OpenAI-compatible client | Playground during prototyping | main enterprise chat/API surface |
| Ops | internal APIM route → Agent Framework runtime | project client for setup/tracing | internal-only |
| Actions | internal APIM route → Agent Framework runtime | none | approval-gated only |
| Router | internal service ingress only | none | not user-facing |

## Endpoints

| Endpoint | URL Pattern | Client |
|----------|-------------|--------|
| Project | `https://data-intel-ph-resource.services.ai.azure.com/api/projects/data-intel-ph` | AIProjectClient |
| OpenAI-compatible | `https://data-intel-ph-resource.openai.azure.com/openai/v1/` | OpenAI() |
| APIM (required) | `https://apim-ipai-dev.azure-api.net/foundry/v1/` | Any HTTP client |

## Acceptance Criteria

1. Router correctly classifies 95%+ of test requests to the right agent
2. Advisory agent passes groundedness ≥ 0.8 on Foundry evaluation suite
3. Ops agent returns no PII to unauthorized callers (100% pass rate)
4. Actions agent refuses writes outside model/field allowlist (100% pass rate)
5. Capability packs degrade gracefully when credentials absent
6. All agent invocations produce App Insights telemetry with user, mode, tools, tokens, latency
7. Multi-agent workflow (expense approval) completes end-to-end with OTel trace
8. No additional Foundry agents created — all modes use `ipai-odoo-copilot-azure`

---

## AFC Parity — Capability Class Mapping

Aligned with SAP Joule benchmark capability classes. Every agent response is classified:

| Capability Class | Description | Agent | Write Access | Confirmation Required |
|---|---|---|---|---|
| **Informational** | Explain rules, deadlines, statuses, penalties, rates | Advisory | None | No |
| **Navigational** | Locate records, deep-link to Odoo screens, surface blockers | Advisory, Ops | None | No |
| **Transactional** | Create/update records, trigger state transitions, generate artifacts | Actions | Bounded CRUD | Yes (Adaptive Card) |
| **Compliance Intelligence** | Cross-check data quality, surface findings, flag gaps | Ops (read), Actions (write) | Findings only | Yes for writes |

### Channel-Surface Rules

| Channel | Default Agent | Allowed Capability Classes | Card Surfaces |
|---|---|---|---|
| Teams (user DM) | Advisory | Informational, Navigational | NavigationCard, DeadlineAlertCard |
| Teams (#tax-compliance) | Ops | Informational, Navigational, Compliance Intelligence (read) | ComplianceBriefingCard, FindingCard |
| Odoo Widget | Actions (gated) | All | ConfirmActionCard, TaskCard, FindingCard |
| APIM (programmatic) | Router decides | All | JSON responses (no cards) |

### Confirmation Card Requirement

All write operations surfaced to users through Teams or Odoo Widget MUST present a `ConfirmActionCard` (Adaptive Card v1.4) before execution. The card displays:
- Action description
- Target record (model + ID)
- Payload summary
- Yes/No buttons

Card JSON: `agents/contracts/ui/confirm_action_card.json`
Card index: `agents/contracts/ui/adaptive_cards_index.yaml`

### Bridge API Boundary

Agent-to-Odoo communication uses a narrow OpenAPI bridge, NOT direct JSON-RPC:
- OpenAPI spec: `agents/contracts/openapi/ipai_odoo_bridge.openapi.yaml`
- Gateway: Azure APIM (`apim-ipai-dev.azure-api.net/odoo`)
- Auth: `X-IPAI-Key` header (API key via Azure Key Vault)
- Backend: Azure Function or FastAPI, translates to Odoo JSON-RPC internally

---

## How Skills Are Built

Odoo Copilot skills are built from five layers.

### 1. Skill manifest
Defines:
- skill id
- purpose
- required inputs
- output types
- execution modes
- permissions
- prerequisites

### 2. Context pack
Supplies:
- active Odoo model/record/view
- user role and company/entity
- relevant dates/periods
- attached files/artifacts
- related scenario/run/finding context
- configured integrations and destinations

### 3. Runtime adapter chain
A skill may call one or more of:
- Odoo ORM/API adapters
- attachment/file analysis
- artifact workspace
- reporting/export adapters
- payment adapters
- Databricks handoff
- external research/search adapters where permitted

### 4. Output contract
A skill must return one or more of:
- answer
- finding
- remediation task
- draft object
- artifact
- preview
- execution request
- handoff destination
- blocked-state explanation

### 5. Governance wrapper
Every skill must be wrapped by:
- execution-mode control
- permission checks
- configuration checks
- audit logging
- preview/review rules
- writeback/payment guardrails

## Canonical Skill Lifecycle

1. User invokes Copilot
2. Router selects candidate skill(s)
3. Skill validates prerequisites and permissions
4. Skill assembles required context pack
5. Skill runs adapters/tools
6. Skill returns typed output(s)
7. Copilot renders preview / asks for approval / executes allowed action
8. Copilot logs run, outputs, decisions, and resulting state

## Skill Types

### A. Informational skills
Return:
- answers
- explanations
- summaries
- recommendations

Examples:
- `finance_qa`
- `policy_guard`
- `finance_audit_translation`

### B. Sandbox-generative skills
Return:
- artifacts
- workbooks
- reports
- templates
- evidence packs

Examples:
- `artifact_workspace`
- `report_builder`
- `bir_template_builder`
- `attachment_packager`

### C. Record-producing skills
Return:
- draft Odoo objects
- findings
- remediation tasks
- scenario runs

Examples:
- `document_intake`
- `reconciliation`
- `close_orchestrator`

### D. Governed execution skills
Return:
- execution requests
- payment proposals
- attach/export/writeback actions
- Databricks handoff

Examples:
- `payment_ops`
- `export_ops`
- `databricks_handoff`

## Canonical Skill Manifest Example

```yaml
skill_id: payment_ops
display_name: Payment Operations
category: finance_execution
description: Prepare and govern payment proposals and execution requests.
inputs:
  required:
    - company_id
    - selected_record_ids
  optional:
    - payment_date
    - payment_journal_id
    - attached_files
outputs:
  - payment_proposal
  - blocker_report
  - execution_request
execution_modes:
  - prepare_only
  - ask_before_acting
permissions:
  any_of:
    - copilot_finance_operator
    - copilot_close_approver
prerequisites:
  - payment_configuration_present
  - payable_records_selected
human_approval_required:
  - execution_request
preview_required: true
writeback_targets:
  - account.payment.register
  - payment_batch
handoff_targets:
  - databricks_dashboard/payment-ops
```

## Skill Design Checklist

A skill is not ready unless all are true:

- It has a stable `skill_id`
- It declares required inputs
- It declares typed outputs
- It declares allowed execution modes
- It declares permission prerequisites
- It declares config prerequisites
- It declares whether preview is required
- It declares whether approval is required
- It logs runs and outcomes
- It has blocked-state behavior
- It does not rely on narrative-only responses for operational workflows
