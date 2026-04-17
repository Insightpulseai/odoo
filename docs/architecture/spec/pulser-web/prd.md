# PRD — Pulser Assistant: Experience Layer

## Status
Draft

## Problem

Pulser needs browser-native surfaces for admin, preview, validation, workbench, and human approval flows. Foundry and Agent Framework solve the backend and runtime layers, but not the full productized operator and end-user web surfaces. Agent Framework's DevUI reinforces the need for dedicated interactive test/developer surfaces, separate from production.

Reference: [What is Microsoft Foundry?](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry)

## Tier 1 Ownership: Pulser Experience Layer

The `web` repo owns all browser-facing Pulser surfaces: operator workbench, preview assistant UI, production copilot shell, grounding management UI, evaluation viewer, HITL approval surfaces, and admin/debug shell.

## Product Vision

Position `web` as the **Pulser Experience Layer** for:
- Operator workbench (formation management, capability enablement, system status)
- Preview assistant UI (test new capabilities before production promotion)
- Production copilot shell outside Odoo (Ask Pulser on insightpulseai.com)
- Grounding management UI (source registration, pipeline status, refresh triggers)
- Evaluation viewer (eval results, trace data, quality metrics)
- HITL approval surfaces (workflow checkpoint approval/rejection)
- Admin/debug shell (DevUI-like interactive agent testing, separate from production)

## Core Surfaces

| Surface | Description | Backend |
|---------|-------------|---------|
| PulserChatSurface | Production Ask Pulser conversational UI | Foundry Agent Service |
| PulserWorkbench | Operator console for formations, capabilities, systems | Platform registry APIs |
| PulserGroundingConsole | Manage grounding sources, pipelines, refresh status | Platform grounding registry |
| PulserEvaluationViewer | Display eval results, traces, quality metrics | Foundry eval + platform evidence |
| PulserApprovalSurface | HITL checkpoints for workflow approval/rejection | Agent Platform checkpoint API |
| PulserAdminShell | DevUI-like internal agent testing (not production) | Foundry Responses API |

## Users

| Role | Primary Surfaces |
|------|-----------------|
| Platform Admin | Workbench, Grounding Console, Admin Shell |
| Agent Developer | Admin Shell, Evaluation Viewer |
| Finance Manager | Chat Surface (production), Approval Surface |
| Data Engineer | Grounding Console |
| QA Engineer | Evaluation Viewer, Admin Shell (preview) |

## Non-Goals

- Not the agent runtime owner (that is `agents`)
- Not the promotion registry (that is `platform`)
- Not the canonical data-model owner (that is `data-intelligence`)
- Not the Odoo transactional execution engine (that is `odoo`)
- Not a replacement for Odoo's native UI (Odoo has its own embedded assistant)

## Capability-Aware UI States

Benchmark: SAP Joule capability taxonomy applied to browser surfaces.

Each capability type renders differently:

| Capability Type | UI Behavior |
|----------------|------------|
| **Informational** | Sources/evidence display, document references, confidence indicators, "explain more" action |
| **Navigational** | "Open target" button/link, destination preview, permission-aware target resolution |
| **Transactional** | Action confirmation UI, risk level indicator, approval workflow trigger, execution result feedback |

Design rule: The chat surface must adapt its response rendering based on the capability type of each assistant response.

## Tax Guru Copilot — Web Surfaces

### Tax Decision Card
- Tax treatment summary with confidence score
- Evidence references (rule sources, documents)
- Actions: escalate, approve, open source document
- Rendered for informational and transactional tax responses

### Tax Exception Queue View
- Exception list: source record, severity, reason, assignee, status
- Filter by exception type: missing_code, ambiguous_taxability, variance, unsupported_case
- Bulk actions: assign, escalate, resolve

### Tax Evidence View
- Evidence bundle: rule sources, documents, explanation summary, timestamps
- Linked to determination results and exception cases
- Audit-ready export

### Tax Preview/Admin Shell
- DevUI-like testing surface for tax capabilities
- Test determination requests against preview tax rules
- Review confidence scores and evidence before production promotion

## Tax Guru PH — UI Card Models

### Tax Evidence Card View

```yaml
TaxEvidenceCardView:
  evidence_key: string
  answer_type: enum  # explanation, recommendation, navigation, action_proposal, exception_review
  title: string      # e.g., "BIR-backed explanation", "Filing guidance with official destinations"
  summary: string
  legal_basis_summary: string
  confidence_score: number
  requires_human_review: boolean
  authority_badges: [TaxAuthorityBadge]
  top_sources:
    - title: string
      authority_level: string
      url: string
      summary: string
  execution_notes: string|null
  ambiguity_flags: [string]
```

Render rule: Authority badges ordered by priority_rank. Show BIR_Legal first, BIR_Guidance second. Show Odoo_Execution only for implementation recommendations.

### Tax Navigation Card View

```yaml
TaxNavigationCardView:
  title: string
  destinations:
    - label: string
      destination_type: enum  # bir_service, form, odoo_view, report
      target_ref: string
      official: boolean
      reason: string
  source_refs: [string]
```

Render rule: Separate sections for **Official BIR destinations** and **Internal Odoo destinations**. Official entries always listed first.

### Tax Action Proposal Card View

```yaml
TaxActionProposalCardView:
  proposal_key: string
  title: string
  action_summary: string
  risk_level: string
  action_mode: string  # read_only, suggest_only, approval_required, direct_execution
  affected_records: [string]
  legal_basis_summary: string
  execution_notes: string
  evidence_key: string
  approval_required: boolean
```

Render rule: Must show legal basis, why the action is suggested, whether approval is required, and which records would change.

### Tax Ambiguity Banner View

```yaml
TaxAmbiguityBannerView:
  banner_type: enum
    - conflicting_sources
    - missing_authority
    - unsupported_case
    - requires_review
  message: string
  recommended_next_step: string
```

Use when: BIR source is missing or unclear, ERP state conflicts with expected treatment, or the case needs accountant/controller review.

### Tax Authority Badge

```yaml
TaxAuthorityBadge:
  badge_type: enum
    - BIR_Legal
    - BIR_Guidance
    - BIR_Service
    - CGPA_Competency
    - Odoo_Execution
    - Internal_Context
  label: string
  priority_rank: integer
```

## Functional Requirements

### FR-1 — Production chat
The chat surface must support streaming conversational interactions with production Pulser agents via SSE or WebSocket.

### FR-2 — Preview chat
A separate preview chat surface must allow testing of pre-production capabilities in an isolated environment.

### FR-3 — Formation workbench
Operators must be able to view and manage formations, capability packages, and integration targets.

### FR-4 — Grounding management
Operators must be able to register grounding sources, monitor pipeline status, and trigger manual refreshes.

### FR-5 — Evaluation viewing
Eval results, traces, and quality metrics must be viewable with drill-down to individual test cases.

### FR-6 — HITL approval
Workflow checkpoints requiring human approval must present clear context, options, and audit trail.

### FR-7 — Environment separation
Preview and production surfaces must be visually distinct to prevent accidental production actions during testing.

### FR-8 — Authentication
All surfaces must authenticate via Microsoft Entra ID (OIDC).

## Success Metrics

- Production Ask Pulser chat operational on insightpulseai.com
- Preview chat surface operational with visual distinction from production
- Operator workbench displaying formation status and capability packages
- Grounding console showing source status and pipeline health
- At least one HITL approval flow operational
- Admin shell available for agent developers (not publicly routed)
