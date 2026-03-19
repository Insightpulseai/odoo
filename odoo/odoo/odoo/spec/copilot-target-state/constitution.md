# Copilot Target-State — Constitution

> Non-negotiable rules governing the ipai-odoo-copilot architecture.
> One visible Foundry assistant, backed by hidden router/ops/actions runtimes,
> grounded by Foundry IQ, governed by APIM, and executed through Odoo-native
> Projects/Tasks/Activities/Milestones with PLM-style approval gates.

---

## C1: One visible assistant, governed backend

Users interact with **one** Foundry prompt agent (`ipai-odoo-copilot-azure`).
Backend roles (Ops, Actions, Router) are internal — never exposed as separate user-facing agents.
This is not a chat-only copilot. It is a **Foundry-hosted assistant on top of an Odoo-native workflow engine**.

## C2: Copilot on top of Odoo workflow primitives, not instead of them

Odoo owns operational workflow state. Copilot explains, inspects, routes, and triggers approved actions on Odoo records. The copilot never:
- Replaces the task engine
- Invents workflow state outside Odoo records
- Holds the canonical due-date/task ledger in prompts

## C3: Odoo Project is the human workflow engine

Use Odoo's built-in Project/Services primitives as the canonical work-management layer:

| Odoo Primitive | Use in Target State |
|---|---|
| **Recurring Tasks** | Monthly/quarterly/annual close and filing tasks |
| **Task Dependencies** | Reconcile → compute → validate → approve → export → file → confirm |
| **Milestones** | Books ready, tax computed, validated, approved, filed, paid, closed |
| **Activities** | Reminders, review requests, follow-ups, exception handling |
| **Project Stages** | Planned, computed, for review, approved for export, filed, paid, confirmed, blocked |
| **Project Roles** | Preparer, reviewer, approver, payer, compliance owner |

## C4: Three logical roles + one workflow

| Component | Backing System | Primary Mode | Responsibility |
|---|---|---|---|
| **Advisory** | Foundry Agent Service | Informational | Explain, summarize, guide, cite, route |
| **Ops** | Agent Framework + Odoo reads | Navigational/diagnostic | Inspect blockers, find overdue items, diagnose missing data |
| **Actions** | Agent Framework + approved Odoo actions | Transactional | Compute, validate, export, notify, prepare packages |
| **Router** | Agent Framework workflow | Deterministic orchestration | Classify, route, pause for approval, resume, hand off |

## C5: Capability packs, not agent sprawl

Domain growth happens through **packs**, not new top-level agents:

| Capability Pack | Advisory | Ops | Actions | Router |
|---|---:|---:|---:|---:|
| Databricks Intelligence | Yes | Yes | Yes | Yes |
| fal Creative Production | Yes | Yes | Yes | Yes |
| Marketing Strategy & Insight | Yes | Yes | Light | No |
| BIR Compliance | Yes | Yes | Yes | Yes |
| Document Intake & Extraction | Yes | Yes | Yes | Yes |

## C6: APIM is the only production front door

| Ingress | Role | Target |
|---|---|---|
| **APIM AI Gateway** | Only production front door | All user/API traffic enters here |
| **Foundry project / OpenAI-compatible clients** | Internal runtime connectivity | Agent, eval, model, tracing calls |
| **Direct REST** | Adapters only | n8n, webhooks, lightweight bridges |
| **Playgrounds** | Non-production only | Prototype, tune, validate |

## C7: PLM-style approval gates

Approval semantics modeled after Odoo 19 PLM:

| Approval Type | Use in Tax Workflow |
|---|---|
| **Required** | Must approve before export, filing, payment confirmation |
| **Optional** | Reviewer input helpful but not blocking |
| **Comments only** | Observer/audit/advisory review |

Required approvals block the protected action until complete.

## C8: Observability is mandatory

Foundry tracing + App Insights connected. Every role traces.
Safety evaluations include human-in-the-loop review.

---

## Ownership Matrix (Authoritative)

| Layer | System of Responsibility | What It Owns | What It Must NOT Own |
|---|---|---|---|
| **Front-door assistant** | Microsoft Foundry Agent Service | `ipai-odoo-copilot-azure`, conversation runtime, tool orchestration, safety enforcement | Canonical tax workflow state, approval ledger, task templates |
| **Grounded knowledge** | Foundry IQ | Permission-aware multi-source KB, retrieval, citations, source ACL-aware grounding | Transactional business state, approvals, return lifecycle |
| **Extraction / document intelligence** | Foundry Tools | OCR, document extraction, content understanding, classification pipelines | Final compliance decisioning or filing approval |
| **Deterministic orchestration** | Microsoft Agent Framework | Router workflow, handoffs, retries, checkpointing, backend role execution | User-facing long-lived business workflow state |
| **Production ingress / governance** | APIM AI Gateway | External ingress, auth, quotas, routing, telemetry | Core business logic |
| **Business objects / source of truth** | Odoo modules | BIR returns, accounting data, payroll, attachments, filing artifacts, status fields | Generalized retrieval or model orchestration |
| **Human workflow engine** | Odoo Project / Tasks / Activities / Milestones | Recurring task templates, dependencies, deadlines, milestone tracking, approver work queues | LLM memory, knowledge grounding |
| **Approvals / gate semantics** | Odoo task/approval extension (PLM-style) | Required/optional/comments-only approvals, blocked transitions, audit trail | Free-form advisory answers |

---

## Foundry Knowledge and Tool Model

| Foundry Surface | Target Use |
|---|---|
| **Foundry IQ** | Shared, permission-aware KB for BIR, Odoo docs, internal finance policies, operating procedures |
| **File search / Azure AI Search** | Uploaded documents, policy docs, BIR references, source-cited answers |
| **Foundry Tools** | Document extraction, OCR, content understanding, future MCP/tool integrations |

---

## Artifact Binding

Every tax task must link to:
- BIR return record
- Export/report/XML/PDF artifact
- Proof of filing
- Proof of payment
- Approver evidence
