# PRD — Pulser: Odoo 18 PH Copilot

## Status
Draft

## Feature Branch
`pulser-odoo-ph`

## Supersedes
`spec/pulser-odoo/` (tax-adapter-only scope)

---

# Product

## Name
Pulser — Odoo 18 PH Copilot

## One-line positioning
An agentic, approval-gated finance, tax, and operations copilot for Odoo 18 in the Philippines.

## Problem
Odoo users in finance and operations lose time switching between ERP records, policy documents,
tax rules, supporting documents, and manual review steps. Generic chat assistants can answer
questions, but they are usually not record-aware, workflow-aware, or Philippines-compliance-aware.
They also fail to provide audit-ready traces for recommendations and actions.

## Why now
- Microsoft Foundry now cleanly separates:
  - project-native agent/app capabilities via the Foundry SDK
  - OpenAI-compatible model access via project-derived or `/openai/v1` clients
  - service-specific AI tooling via Foundry Tools SDKs
- This makes it practical to build Pulser as an Odoo-native copilot shell backed by a governed
  agent runtime instead of a thin "chat with model" feature. The Foundry guidance explicitly
  positions the Foundry SDK for agents, evaluations, and tracing, while the OpenAI-compatible
  client is used for model-shaped interactions such as Responses API calls.

## Target users
- Accountant
- AP reviewer
- Controller
- Operations manager
- Founder / admin

## Jobs to be done
- Explain why a record is in its current state
- Summarize chatter, documents, invoices, partners, journals, tasks, and projects
- Suggest next actions based on Odoo context and company policy
- Review AP and expense documents with accounting/tax suggestions
- Prepare PH compliance workpapers and exception summaries
- Ground answers in internal policies, prior transactions, and approved reference material

## Goals
1. Reduce manual finance and ops review time inside Odoo
2. Make recommendations contextual to the active record and user permissions
3. Support PH tax/compliance assistance without autonomous filing or posting
4. Produce audit-ready traces for prompts, tools, approvals, and outputs
5. Keep Odoo as the transactional system of record

## Non-goals
- Replace Odoo workflows or UI for core ERP transactions
- Perform autonomous accounting posting by default
- Perform autonomous tax filing or regulatory submission
- Build a general-purpose multi-agent platform in V1
- Recreate ERP logic already present in Odoo or OCA

## Product principles
- Record-aware: every answer should be tied to Odoo context
- Workflow-aware: responses should reflect current process state
- Policy-aware: recommendations must use approved internal guidance where available
- Compliance-aware: PH-specific tax/document logic must be first-class, not an afterthought
- Human-governed: high-risk actions require approval
- Explainable: recommendations must expose rationale and source context

---

## MVP scope

### Capability lane A — Contextual Odoo Copilot
- Record summary for invoices, bills, partners, projects, tasks, journals, and chatter threads
- "Why is this in this state?" explanation flows
- Draft note, email, follow-up, activity, and summary generation
- Next-best-action suggestions

### Capability lane B — Finance review copilot
- AP invoice review
- Expense classification assistance
- Account suggestion assistance
- Tax code / tax treatment suggestion assistance
- Variance and anomaly explanation

### Capability lane C — PH compliance copilot
- VAT / EWT guidance assistance
- Document metadata validation
- Invoice / receipt checklist assistance
- Filing workpaper draft preparation
- Exception queue summarization

### Capability lane D — Retrieval and grounding
- Company policy grounding
- PH tax/compliance grounding
- Historical transaction grounding
- Internal audit/explanation traces

---

## User stories

### Story 1 — Record explanation
As an accountant, I want Pulser to explain the current state of an invoice or journal entry so
that I can review faster without manually tracing every related record.

#### Acceptance criteria
- Given an active Odoo record, when the user asks for an explanation, then Pulser returns a
  concise explanation tied to record fields, related records, and recent workflow actions.
- Given insufficient context, when Pulser cannot determine a reliable explanation, then it
  states uncertainty and requests or retrieves additional allowed context instead of guessing.

### Story 2 — Finance review assistance
As an AP reviewer, I want Pulser to review incoming invoices and suggest classifications or tax
handling so that I can reduce manual review effort.

#### Acceptance criteria
- Given an AP document, when Pulser reviews it, then it returns suggested account/tax treatment,
  identified discrepancies, and a confidence/rationale summary.
- Given a high-risk or low-confidence recommendation, then Pulser routes the action for review
  and does not auto-post changes.

### Story 3 — PH compliance assistance
As a controller in the Philippines, I want Pulser to help prepare workpapers and validate
document requirements so that compliance work is faster and more consistent.

#### Acceptance criteria
- Given a PH-scoped entity, when Pulser evaluates a document/work item, then it applies the
  PH compliance rules configured for that entity.
- Given missing required metadata or documentary support, then Pulser flags the exception and
  produces a checklist or workpaper draft instead of silently proceeding.

### Story 4 — Governed action execution
As an admin, I want Pulser to assist with actions in Odoo while enforcing approval gates so that
the system remains safe and auditable.

#### Acceptance criteria
- Given a low-risk action, when approved by policy, then Pulser may execute through a tool path.
- Given a high-risk action, then Pulser must require explicit human approval before execution.
- All tool calls, approvals, and outputs must be logged for traceability.

---

## Functional requirements
- Pulser shall run as an Odoo-native assistant surface for supported record types.
- Pulser shall use Microsoft Foundry as the primary agent runtime for agent, tracing, and
  evaluation workflows. The Foundry SDK is the intended integration path for these features.
- Pulser shall use an OpenAI-compatible client for model-shaped interactions such as Responses API calls.
- Pulser shall support grounding against approved internal knowledge and selected Odoo context.
- Pulser shall expose tool paths for safe Odoo actions behind policy and approval checks.
- Pulser shall support PH finance/tax assistance in MVP scope.
- Pulser shall record trace metadata for prompts, tool calls, approvals, and outputs.

## Guardrails
- No autonomous posting to books by default
- No autonomous tax filing or external submission
- No hidden execution of high-risk tools
- No fabricated policy or tax advice when source context is absent
- No access beyond the current user's permitted Odoo scope

## Success metrics
- Reduce AP review time by at least 30% in pilot workflows
- Reduce manual policy lookup time by at least 50%
- Achieve trace coverage for 100% of tool-executed actions
- Achieve first-pass useful answer rate above 80% on supported record explanation flows
- Keep approval-gated action compliance at 100%

---

## Existing IPAI Modules (Foundation)

| Module | Role in Pulser PH |
|--------|------------------|
| `ipai_odoo_copilot` | Canonical copilot shell (systray, chat panel, context packaging) |
| `ipai_copilot_actions` | Agent action queue + human approval framework |
| `ipai_tax_intelligence` | Core tax determination kernel (55 tests) |
| `ipai_bir_tax_compliance` | PH compliance pack prototype |
| `ipai_bir_notifications` | PH filing notification framework |
| `ipai_document_intelligence` | Document extraction for AP invoice intake |
| `ipai_expense_ops` | AP discrepancy control pattern |
| `ipai_branch_profile` | Multi-entity / branch-aware operations |

---

## References

- [Azure AI Foundry SDK — Choosing Your Path](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/sdk-overview)
- [spec/pulser-odoo/](../pulser-odoo/) — predecessor tax-adapter spec
- [spec/pulsetax-agentic-control-plane/](../pulsetax-agentic-control-plane/) — PulseTax product spec
