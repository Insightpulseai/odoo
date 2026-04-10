# PRD: Pulser for Odoo

> **Human-facing title**: `Pulser for Odoo`
> **Subtitle**: `Pulser Assistant for Odoo`
> **Canonical Slug**: `pulser-odoo`
> **Status**: MVP / Ship-Ready Candidate
> **Constitution**: [constitution.md](constitution.md)

---

## Problem

Finance operators using Odoo CE spend significant time on repetitive investigative tasks during month-end close, reconciliation, collections, and variance analysis. They alt-tab between Odoo and other systems to assemble context that an AI assistant could surface in seconds.

ERP copilots often become navigation overlays that are weakly grounded in operational truth. Odoo users need an assistant that is grounded in Odoo's operational state, respects safety gates, and provides explainable rationale.

## Goal

Deliver **Pulser for Odoo**, a thin Odoo adapter layer that:
1. Lets finance operators ask natural-language questions from within Odoo.
2. Packages the relevant ERP context (active record, user, company) and delegates to Azure AI Foundry.
3. Renders actionable answers (text, suggested actions, citations) inline.
4. Maintains safe action gates (read-only default, approval-required for writes).

## Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| Module installs cleanly | 0 errors on `odoo-bin -i ipai_odoo_copilot` | CI gate |
| Finance Q&A latency | < 5 seconds p95 (Odoo to Foundry and back) | App Insights |
| Audit coverage | 100% of interactions produce an audit record | Unit test |
| Read-only safety | No Odoo writes without explicit user confirmation | Security test |

---

## Product Vision: The Odoo Adapter

Position Odoo as the **Pulser Odoo Adapter** for:
- **Informational**: Live questions about invoices, aging, balances, and journal entries.
- **Navigational**: Guiding users to the right menus, reports, or views.
- **Transactional**: Executing bounded actions (posts, approvals) with safety gates.

## Core Scenarios (Finance-First)

1. **Month-End Close Q&A**: "Are there any unposted journal entries for March?"
2. **Bank Reconciliation**: Suggesting matches for bank statement lines with confidence scores.
3. **Collections Follow-Up**: Drafting professional emails referencing overdue invoices.
4. **Variance Analysis**: Explaining why a cost center is over budget using live Odoo context.

---

## Functional Requirements

### FR-1: Entry Points
- Systray icon (top-right system tray).
- Form helper button (model-aware helper).
- Chat panel (slide-out conversation UI).

### FR-2: Context Packaging
Packages `user_id`, `company_id`, `active_model`, `active_id`, and `active_record_data` for delegation. Respects user security groups and field-level permissions.

### FR-3: External Delegation
Sends structured JSON payloads to the Pulser Foundry endpoint. Uses Microsoft Entra ID (Managed Identity) for user-scoped authorization.

### FR-4: Safe Action Mediation
Write actions require:
1. Admin-configured policy allowlist.
2. Visual confirmation dialog showing the exact action payload.
3. Human-in-the-loop approval before ORM execution.

### FR-5: Auditability
Produces `ipai.copilot.audit` records representing every request/response, including latency and action results.

---

## MVP Scope

### Included
- Assistant shell with tri-modal behavior.
- Finance-First grounding (Accounting, Partner, Bank models).
- Read-only Q&A + approval-gated drafting/actions.
- Full audit trail within Odoo.
- Integration with `ipai_knowledge_bridge` for cited grounding.

### Out of Scope
- Autonomous background operations.
- Non-finance domains (HR, Project, Helpdesk deferred to Release 2).
- Native mobile assistance (web/backend first).

---

*Last updated: 2026-04-10*
