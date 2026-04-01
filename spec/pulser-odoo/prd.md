# PRD — Pulser Assistant: Odoo Adapter

## Status
Draft

## Problem

Pulser inside Odoo must be a thin embedded assistant and action adapter, not the whole assistant platform. Joule's benchmark treats integrated business systems as attached products inside a broader copilot landscape, not as the control plane itself. Odoo should provide: an embedded assistant UI, record-aware context assembly, approved actions, recommendation rendering, activity/chatter integration, and telemetry/evidence emission back to `platform`.

## Tier 1 Ownership: Pulser Odoo Adapter

The `odoo` repo owns only the Odoo-side embedded assistant surfaces and action adapters. It is one integrated system within a broader Pulser formation, not the assistant platform itself.

## Product Vision

Position `odoo` as the **Pulser Odoo Adapter** for:
- Embedded assistant UI (systray access, contextual panel)
- Record-aware context assembly (current model, record ID, key fields)
- Approved Odoo actions (with configurable safety modes)
- Recommendation rendering (suggested actions, related records)
- Activity/chatter/task integration (log assistant interactions in Odoo)
- Telemetry/evidence emission back to `platform`
- Tool endpoints consumed by `agents` runtime

## Core Surfaces

| Surface | Description |
|---------|-------------|
| PulserSystrayAssistant | Systray icon launching the assistant panel from any Odoo view |
| PulserRecordPanel | Contextual assistant panel aware of the current record |
| PulserActionRequest | Structured request from agent to execute an Odoo action |
| PulserRecommendationCard | UI card displaying agent suggestions/recommendations |
| PulserActionResult | Structured result of an executed Odoo action, returned to agent |
| PulserEvidenceEmitter | Outbound telemetry/evidence hook to platform registry |

## Users

| Role | Primary Interaction |
|------|-------------------|
| Finance Manager | Systray assistant, record panel (invoices, journal entries) |
| AR Specialist | Record panel (partner, open invoices), recommendations |
| Tax Accountant | Record panel (BIR forms, tax computations) |
| Procurement Lead | Record panel (purchase orders, vendor bills) |

## Non-Goals

- Not the Pulser control plane (that is `platform`)
- Not the canonical grounding registry (that is `platform`)
- Not the agent/template registry (that is `agents`)
- Not the preview/prod promotion authority (that is `platform`)
- Not the primary web copilot shell (that is `web`)
- Not the analytical data model host (that is `data-intelligence`)

## Capability-Type Adapters

Benchmark: SAP Joule capability taxonomy applied to Odoo adapter layer.

Each capability type has distinct Odoo-side behavior:

| Capability Type | Odoo Adapter Role |
|----------------|------------------|
| **Transactional** | Action adapters: create/update/post/approve with safe execution modes |
| **Navigational** | Menu/record/report resolvers: map intent to Odoo action/menu/view target |
| **Informational** | Record/doc/context exporters: assemble context for agent grounding |

Design rules:
- Transactional adapters enforce safe action modes (read_only, suggest_only, approval_required, direct_execution)
- Navigational resolvers must be permission-aware (filter by user groups/rules)
- Informational exporters provide structured context, not raw database dumps

## Tax Guru Copilot — Odoo Adapter Objects

Benchmark: AvaTax (ERP integration pattern) + Joule (attached product model).

Odoo is the tax execution/context adapter, not the tax control plane. Tax reasoning lives in `agents`, tax governance lives in `platform`.

### Odoo Domain Objects

#### `ipai.pulser.tax_context`
Tax context assembly for invoice/bill/PO/expense/journal records:
- `context_key` — unique identifier
- `model_name` — source Odoo model (account.move, purchase.order, hr.expense, etc.)
- `res_id` — source record ID
- `company_id` — company context
- `partner_tax_profile_json` — partner's tax classification, fiscal position, withholding status
- `line_tax_context_json` — per-line tax codes, amounts, product taxability
- `document_refs_json` — related documents (attachments, receipts)
- `last_built_at` — timestamp

#### `ipai.pulser.tax_action_request`
Structured request from agent to execute a tax-related Odoo action:
- `request_key` — unique identifier
- `res_model` — target Odoo model
- `res_id` — target record
- `action_type` — propose_tax_code, update_withholding, draft_correction, create_review_task, create_exception_case
- `proposed_tax_code` — suggested tax code (if applicable)
- `proposed_withholding_treatment` — suggested withholding classification (if applicable)
- `payload_json` — full action payload
- `action_mode` — read_only, suggest_only, approval_required, direct_execution
- `status` — pending, approved, executed, rejected

#### `ipai.pulser.tax_exception_event`
Outbound exception emission to platform:
- `event_key` — unique identifier
- `source_record_ref` — originating Odoo record
- `exception_type` — missing_code, ambiguous_taxability, variance, unsupported_case
- `severity` — low, medium, high, critical
- `platform_synced` — boolean
- `emitted_at` — timestamp

### Safety Rules
- Tax actions default to `suggest_only` or `approval_required`
- Direct execution limited to narrow, reversible, low-risk tax actions only
- Exception events always emitted to platform (no silent failures)

### PH Execution Benchmark Integration

Odoo 18 accounting localization pattern is the execution benchmark for how PH tax logic should land inside Odoo:

- **Localization module structure**: `l10n_ph` pattern — `data/template`, `models/template_ph.py`, manifest/demo/view files
- **Tax configuration**: `account.tax.group-ph.csv` and `account.tax-ph.csv`
- **Tax reporting**: `account.report` records with report lines in XML under the generic tax report root

#### `ipai.pulser.tax_action_request` (expanded)
Additional fields for PH execution benchmark:
- `execution_model_ref` — link to Odoo localization artifact (tax group, tax template, report) when the action depends on PH Odoo tax configuration
- `localization_mapping_ref` — reference to specific `l10n_ph` tax group/template when action maps a BIR rule to Odoo configuration
- `legal_basis_ref` — reference to BIR authority citation that justifies this action

Rule: Every tax action that modifies tax configuration must cite both the BIR legal basis (Tier 1-2) AND the localization mapping (Tier 5). The legal basis determines **what** to do; the localization mapping determines **how** Odoo implements it.

#### `ipai.pulser.tax_exception_event` (expanded)
Additional fields for evidence gap tracking:
- `evidence_gap` — what authority/citation is missing
- `required_authority_tier` — minimum tier needed to resolve (1-6)
- `escalation_recommendation` — suggested next step

#### ERP Context in Evidence Bundles
When Odoo assembles tax context for agent consumption:
- Odoo record data is classified as Tier 6 (internal_transaction_context)
- Tax configuration references are classified as Tier 5 (odoo_execution_benchmark)
- Neither overrides BIR legal authority (Tier 1-2)
- Evidence bundles flowing back from agents must be stored with citations for audit trail

### TaxPulse PH Pack Positioning

TaxPulse PH Pack (`github.com/jgtolentino/TaxPulse-PH-Pack`) is a bounded Odoo-side execution pack for Philippine tax compliance.

**It is not the full Tax Guru Copilot.**

It provides localized BIR forms, tax computations, agency mappings, report outputs, and sync hooks. The Odoo adapter (`ipai.pulser.tax_context`, `ipai.pulser.tax_action_request`) bridges between the TaxPulse PH Pack execution layer and the broader Tax Guru agent runtime.

**Integration pattern**: TaxPulse PH Pack computes → Odoo adapter formats context → agents reason → web surfaces display.

## Functional Requirements

### FR-1 — Embedded UI
The Odoo adapter must provide a systray assistant icon and contextual record panel accessible from any Odoo backend view.

### FR-2 — Record context
The adapter must assemble record context (model name, record ID, key fields, related records) and pass it to the agent runtime.

### FR-3 — Safe action modes
All Odoo actions requested by agents must go through configurable safety modes:
- **Read-only**: Query only, no mutations
- **Suggest-only**: Show recommendations, user executes manually
- **Approval-required**: Agent proposes, user approves before execution
- **Direct-execution**: Narrow safe actions only (e.g., logging a note)

### FR-4 — Recommendation rendering
Agent suggestions must render as structured UI cards with context, rationale, and action buttons.

### FR-5 — Activity integration
All assistant interactions must be loggable in Odoo's chatter/activity system for audit trail.

### FR-6 — Telemetry emission
All assistant actions must emit structured telemetry events to `platform` for evidence and monitoring.

### FR-7 — Tool endpoints
Odoo must expose FastAPI endpoints that agents can call as tool bindings (read records, create entries, update status).

### FR-8 — Preview/prod configuration
The adapter must support separate configuration for preview and production assistant channels.

## Success Metrics

- Systray assistant accessible from all major Odoo views
- Record context correctly assembled for account.move, res.partner, purchase.order
- Safety modes enforced (no direct-execution on finance-sensitive actions without approval)
- Activity logging operational for all assistant interactions
- Telemetry emission reaching platform evidence store
- FastAPI tool endpoints operational and registered in agents tool catalog
- Preview/prod configuration separation working
