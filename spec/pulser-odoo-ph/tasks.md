# Tasks — Pulser: Odoo 18 PH Copilot

## Status
Draft

---

## Phase 1 — Odoo contextual copilot foundation

### T1.1 Odoo assistant shell
- [ ] Add systray entry point for Pulser
- [ ] Add assistant panel/modal shell
- [ ] Add session bootstrap and current-user context wiring

### T1.2 Supported record context extraction
- [ ] Define supported MVP models:
  - account.move
  - res.partner
  - project.project
  - project.task
  - mail.thread-backed records where relevant
- [ ] Build server-side context serializer with ACL-safe field allowlist
- [ ] Add record summary formatter

### T1.3 Pulser gateway contract
- [ ] Define request/response schema between Odoo and Pulser service
- [ ] Include:
  - user identity reference
  - record context
  - conversation turn
  - requested mode
  - trace correlation id

### T1.4 Foundry integration baseline
- [ ] Initialize Foundry SDK project client
- [ ] Create project-derived OpenAI-compatible client path
- [ ] Add configuration placeholders for:
  - Foundry resource endpoint
  - project endpoint
  - model deployment names
- [ ] Keep project name unresolved until verified

### T1.5 Basic answer modes
- [ ] Implement:
  - summarize current record
  - explain current state
  - draft follow-up/note/email
- [ ] Add failure-mode handling for missing context and downstream unavailability

### T1.6 Trace baseline
- [ ] Emit trace/log metadata for every request
- [ ] Record:
  - user
  - model path
  - tools requested
  - tools executed
  - approval state
  - latency/error outcome

### Phase 1 exit criteria
- User can open Pulser from Odoo and get record summary/explanation/draft responses

---

## Phase 2 — Finance review copilot

### T2.1 AP invoice review path
- [ ] Add AP review mode for vendor bills
- [ ] Return:
  - summary
  - suggested account/tax handling
  - detected anomalies
  - rationale

### T2.2 Expense/account/tax suggestion assistance
- [ ] Implement bounded suggestion flows for:
  - account classification
  - tax treatment suggestion
  - expense categorization
- [ ] Mark all outputs as suggestions, not auto-posted outcomes

### T2.3 Variance/anomaly explanation
- [ ] Add comparison logic for source values vs expected values where available
- [ ] Generate reviewer-facing explanation text

### T2.4 Finance review UI states
- [ ] Add confidence / review-needed labels
- [ ] Add explicit "requires approval" or "manual review required" states

### Phase 2 exit criteria
- AP review suggestions and variance explanations work on supported documents

---

## Phase 3 — PH compliance copilot

### T3.1 PH entity scoping
- [ ] Add company/entity configuration flags for PH compliance mode
- [ ] Ensure logic can be entity-specific

### T3.2 PH compliance checklist tooling
- [ ] Implement document/work item checklist generation for supported PH workflows
- [ ] Validate required metadata presence and flag missing fields

### T3.3 Workpaper draft generation
- [ ] Generate review-ready drafts for supported PH finance/compliance flows
- [ ] Include rationale and missing-evidence sections

### T3.4 Retrieval grounding for PH references
- [ ] Connect approved PH compliance reference corpus
- [ ] Add internal citation/explanation metadata for answer provenance

### Phase 3 exit criteria
- PH compliance checklist/workpaper draft flows work for scoped entity/workflows

---

## Phase 4 — Approval-gated bounded actions

### T4.1 Action risk classification
- [ ] Define low / medium / high risk taxonomy
- [ ] Map supported tools/actions into risk classes

### T4.2 Approval workflow
- [ ] Require explicit human approval before any high-risk action execution
- [ ] Persist approval decisions in trace/audit records

### T4.3 Bounded Odoo tool execution
- [ ] Implement safe tool paths for selected low-risk actions only
- [ ] Block hidden or implicit execution paths

### Phase 4 exit criteria
- High-risk actions are approval-gated and traceable

---

## Phase 5 — Evals, hardening, and observability

### T5.1 Eval dataset
- [ ] Build eval cases for:
  - record summary
  - record explanation
  - AP review
  - PH checklist/workpaper generation
  - approval-gated action handling

### T5.2 Quality evaluation
- [ ] Measure:
  - answer usefulness
  - grounding correctness
  - unsafe action attempts
  - latency

### T5.3 Operational hardening
- [ ] Add fallback behavior for:
  - Foundry unavailable
  - retrieval unavailable
  - document analysis unavailable
- [ ] Ensure graceful error surfacing in Odoo UI

### T5.4 Audit and trace review
- [ ] Validate 100% trace coverage for executed actions
- [ ] Validate approval-gated actions cannot bypass review

### Phase 5 exit criteria
- Eval baseline exists, traces are inspectable, and failure modes are controlled
