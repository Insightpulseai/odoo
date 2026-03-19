# Copilot Target-State — Plan

## Current State

- 1 Foundry prompt agent: `ipai-odoo-copilot-azure`
- BIR module: `draft → computed → validated → filed → confirmed` (missing `approved`)
- `mail.activity.mixin` inherited (activities work)
- Copilot: 18 tools, 1 BIR tool (read-only `bir_compliance_search`)
- Tax Pulse: spec kit complete, rates/rules/engine ported (67 tests), tool contracts defined
- Agent framework: 3-agent + 1-workflow model specced, capability matrix with BIR pack
- Odoo Project: available with recurring tasks, dependencies, milestones, roles, activities
- No PLM-style approval gates yet
- No company-scoped compliance project templates

## Implementation Waves

### Wave 1 — Lock the assistant surface

**Goal**: Stabilize the front-door agent with knowledge, evals, tracing, and document extraction.

**Deliverables**:
- Foundry IQ knowledge store: BIR regulations, form guides, TRAIN law references
- Eval datasets: `bir_advisory.yaml` (50 cases), `bir_ops.yaml` (30), `bir_actions.yaml` (40)
- Guardrails: no ungrounded tax advice, no unauthorized writes
- App Insights tracing enabled
- Document extraction pipeline (Azure Document Intelligence) for invoices/receipts/BIR attachments

**Exit gate**: Advisory answers BIR questions with grounded citations, traces visible.

### Wave 2 — Build hidden backend roles

**Goal**: Router + Ops + Actions behind the Advisory front door.

**Deliverables**:
- `copilot_router.py` — deterministic intent classification (channel + model + role + intent)
- Ops runtime — read-only Odoo queries for filing readiness, overdue detection, blocker diagnosis
- Actions runtime — approval-gated compute, validate, export via Odoo state machine
- 8 BIR copilot tools wired to Odoo actions
- `approved` state added to `bir.tax.return`
- `group_ipai_bir_approver` security group

**Exit gate**: Router classifies 95%+ correctly, approval gate blocks all unauthorized writes.

### Wave 3 — Operationalize Odoo Project

**Goal**: Company-scoped compliance projects with recurring tasks, dependencies, and milestones.

**Deliverables**:
- `bir.filing.task.template` model — seed templates for all 24 form types
- Month-end closing workbook normalized into Odoo seed XML
- Recurring task generation cron (N days before deadline)
- Task dependency chains: reconcile → compute → validate → approve → export → file → confirm
- Milestones: books ready, tax computed, validated, approved, filed, paid, closed
- Project roles: preparer, reviewer, approver, payer, compliance owner
- Company-scoped project template (multi-company ready)
- Kanban + calendar views for compliance worklist

**Exit gate**: Tasks auto-generate per cadence, dependency chains enforce order, milestones track progress.

### Wave 4 — Add approval semantics

**Goal**: PLM-style approval gates on stage transitions.

**Deliverables**:
- Approval model extension on `bir.tax.return` (required/optional/comments-only)
- Stage transition rules:
  - For review → approved for export (required approval by `group_ipai_bir_approver`)
  - Approved for export → filed (required approval by `group_ipai_finance_manager`)
  - Filed/paid → confirmed (required approval by compliance owner)
- Activity auto-creation for approval requests
- Blocked state when required approval missing
- Audit trail on all approvals

**Exit gate**: Required approvals block transitions, audit trail captures all decisions.

### Wave 5 — Bind artifacts and evidence

**Goal**: Every tax task links to its full evidence chain.

**Deliverables**:
- BIR return ↔ project task linking
- Export artifacts (eFPS XML, PDF, alphalist) attached to task
- Proof of filing attachment field
- Proof of payment attachment field
- Approver evidence (who approved, when, what comments)
- Evidence completeness check before period close
- APIM production ingress wired

**Exit gate**: Full audit chain from task → return → artifact → proof → approval for any filing.

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| Odoo Project doesn't have PLM-style approvals natively | Model as `ipai_*` extension using `mail.activity` + required flag + blocked state |
| Recurring task cadence mismatch with BIR deadlines | Use form-type-specific lead days in task templates |
| Multi-company project scoping complexity | Use Odoo's native `company_id` field + multi-company rules |
| Agent Framework SDK pre-release | Phase 2 is last to need it; fallback: sequential Responses API calls |
| Foundry IQ knowledge lag on new BIR regulations | Manual knowledge update process; flag stale citations |
