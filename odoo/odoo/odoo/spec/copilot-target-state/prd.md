# Copilot Target-State — PRD

## Problem

The current system has 1 Foundry prompt agent as a seed. Without a governed architecture, growth leads to agent sprawl, copilot-as-workflow-engine anti-patterns, and ungoverned transactional actions. The desired end state is not a chat-only copilot — it is a Foundry-hosted assistant on top of an Odoo-native workflow engine.

## Solution

One assistant product backed by a governed multi-role runtime with APIM ingress, Agent Framework orchestration, and domain capability packs. Odoo Project/Tasks/Activities/Milestones serve as the human workflow engine with PLM-style approval gates.

## Success Criteria

1. Users interact with **one assistant**
2. Chat answers are grounded and safe (Foundry IQ + citations)
3. Complex work routes to correct backend role (Router → Ops/Actions)
4. Writes are isolated and approval-gated (PLM-style required/optional/comments)
5. APIM fronts production traffic
6. Traces and evals exist for every role
7. Vendor/domain growth happens through packs, not new agents
8. Odoo Project owns recurring tasks, dependencies, milestones, and approval work queues
9. Every tax task links to return, artifact, proof of filing, proof of payment, and approver evidence

## Rollout Waves

### Wave 1 — Lock the assistant surface
- Keep `ipai-odoo-copilot-azure` as user-facing
- Attach guardrails, eval datasets, tracing
- Foundry IQ grounding for BIR knowledge
- Document extraction hookup
- Agent remains read-only by default

### Wave 2 — Build hidden backend roles
- Router workflow (deterministic classification, approval pause/resume)
- Ops runtime (read-only diagnostics, filing inspection)
- Actions runtime (smallest approved write scope, evidence + rollback)
- Deterministic handoffs between roles

### Wave 3 — Operationalize Odoo Project
Create company-scoped compliance projects with:
- Recurring tasks (monthly/quarterly/annual per form type)
- Task dependencies (reconcile → compute → validate → approve → export → file → confirm)
- Milestones (books ready, tax computed, validated, approved, filed, paid, closed)
- Project roles (preparer, reviewer, approver, payer, compliance owner)
- Activity plans for exception handling

### Wave 4 — Add approval semantics
Implement PLM-style approval classes for stage transitions:
- For review → approved for export (required approval)
- Approved for export → filed (required approval)
- Filed/paid → confirmed (required approval)
- Optional and comments-only for observer/audit review

### Wave 5 — Bind artifacts and evidence
Every tax task links to:
- BIR return record
- Export/report/XML/PDF artifact
- Proof of filing
- Proof of payment
- Approver evidence (audit trail)

## Azure Stack Mapping

| Component | Azure Service |
|---|---|
| Front-door agent | Foundry Agent Service |
| Knowledge grounding | Foundry IQ (permission-aware, multi-source, Azure AI Search) |
| Document extraction | Foundry Tools (Document Intelligence) |
| Router/Ops/Actions | Agent Framework |
| Runtime | Azure Container Apps |
| Production ingress | APIM AI Gateway |
| Observability | Foundry Tracing + App Insights |

## Template Reuse Strategy

| Template | Use as |
|---|---|
| Get started with AI agents | Primary starter skeleton |
| RAG chat with Azure AI Search | Knowledge-grounding benchmark |
| Deploy AI app in production | Runtime hardening benchmark |
| Home Banking Assistant / multi-agent | Approval-safe transactional benchmark |
| Multi-modal Content Processing | Document ingestion benchmark |

## Odoo Workflow Model

### Project Stages
Planned → Computed → For Review → Approved for Export → Filed → Paid → Confirmed → Blocked

### Project Roles
| Role | Responsibility |
|---|---|
| Preparer | Compute and draft returns |
| Reviewer | Validate data completeness and accuracy |
| Approver | Gate export/filing/payment (required approval) |
| Payer | Execute payment and attach proof |
| Compliance Owner | Final confirmation and period close |

### Approval Model (PLM-style)
| Approval Type | Use |
|---|---|
| Required | Must approve before export, filing, payment confirmation |
| Optional | Reviewer input helpful but not blocking |
| Comments only | Observer/audit/advisory review |

## Do Not

- Create separate top-level agents per domain/vendor
- Rely on playground configs as production SSOT
- Fine-tune before knowledge/tools/evals work
- Allow direct transactional actions from Advisory surface
- Hold tax computation state in prompts or chat memory
- Bypass Odoo's state machine for filing lifecycle
- Replace the Odoo task engine with copilot workflow
