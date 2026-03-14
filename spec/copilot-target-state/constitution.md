# Copilot Target-State — Constitution

> Non-negotiable rules governing the ipai-odoo-copilot architecture.

---

## C1: One visible assistant, governed backend

Users interact with **one** Foundry prompt agent (`ipai-odoo-copilot-azure`).
Backend roles (Ops, Actions, Router) are internal — never exposed as separate user-facing agents.

## C2: Copilot on top of Odoo workflow primitives, not instead of them

Odoo owns operational workflow state. Copilot explains, inspects, routes, and triggers approved actions on Odoo records. The copilot never:
- Replaces the task engine
- Invents workflow state outside Odoo records
- Holds the canonical due-date/task ledger in prompts

## C3: Odoo-native primitives first

Use Odoo's built-in operational patterns before custom copilot behavior:
- **Stages** → filing lifecycle/status lanes
- **Activities** → reminders, approvals, due-date follow-ups
- **Reporting** → filing worklist visibility and month-end control views
- **Project/service task patterns** → recurring compliance task templates
- **Milestone-style checkpoints** → compute, validate, export, pay, confirm

## C4: Three logical roles + one workflow

| Component | Runtime | Purpose |
|-----------|---------|---------|
| Advisory | Foundry prompt agent | User-facing, grounded Q&A and guidance |
| Ops | Agent Framework runtime | Internal diagnostics, read-only inspection |
| Actions | Agent Framework runtime | Approval-gated writes, exports, triggers |
| Router | Agent Framework workflow | Deterministic routing, approvals, checkpoints |

## C5: Capability packs, not agent sprawl

Domain growth happens through **packs**, not new top-level agents:
- Databricks Intelligence Pack
- fal Creative Production Pack
- Marketing Strategy & Insight Pack
- BIR Compliance Pack
- Document Intake & Extraction Pack

## C6: APIM is the production front door

Production traffic enters through Azure API Management AI Gateway.
Direct REST is only for adapters/automation bridges.
Foundry Playgrounds are for prototyping only, never production.

## C7: Actions are always approval-gated

No broad mutation from Advisory surface. Actions runtime requires:
- Explicit approval checkpoints
- Evidence + rollback notes
- Smallest approved write scope first

## C8: Observability is mandatory

Foundry tracing + App Insights connected. Every role traces.
Safety evaluations include human-in-the-loop review.

---

## BIR/Tax Workflow Mapping (Odoo-native)

| Odoo primitive | Tax/compliance use |
|---|---|
| **Stages** | Draft → Computed → Validated → Approved → Filed → Confirmed |
| **Activities** | Reminders, approvals, missing-data follow-ups |
| **Reporting** | Overdue filings, blocked filings, upcoming deadlines |
| **Service/project task templates** | Recurring BIR/month-end tasks |
| **Milestone-style checkpoints** | Compute, validate, export, pay, confirm |

## End-State Ownership

- **Odoo** owns operational workflow state
- **Copilot** explains, inspects, routes, and triggers approved actions
- **Agent Framework** orchestrates approvals and backend logic
- **Foundry** provides grounding/evals/tracing
- **Odoo Services/Project-style tasking** provides the human work management layer
