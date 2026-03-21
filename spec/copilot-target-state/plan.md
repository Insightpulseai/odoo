# Copilot Target-State — Plan

## Deployment Ladder

### Phase 1 — Benchmark-ready (now)

Deploy internally as:

- Odoo runtime + Odoo Copilot widget (installed on `odoo_dev`)
- Foundry published agent
- Document Intelligence / OCR
- Private benchmark against SAP Joule

Deliverables:

- [ ] Publish Foundry agent to stable endpoint
- [ ] Connect `ipai_odoo_copilot` to published agent
- [ ] Wire OCR / Document Intelligence extraction flow
- [ ] Benchmark against SAP Joule capability classes
- [ ] Define metrics: informational accuracy, navigational success, transactional proposal acceptance

### Phase 2 — Private Microsoft 365/Teams distribution

- [ ] Package as Microsoft 365 / Teams app or custom engine agent
- [ ] Deploy to org catalog / private tenant
- [ ] Validate auth, install flow, role boundaries, UX

### Phase 3 — Marketplace readiness

- [ ] Finalize privacy / boundaries / eval pack
- [ ] Finalize commercial offer type (SaaS recommended)
- [ ] Prepare Partner Center assets
- [ ] Submit for Marketplace review (expect up to 4 weeks)

---

## SAP Joule Benchmark Scorecard

| Capability | SAP Joule Benchmark | Odoo Copilot Target |
| --- | --- | --- |
| Informational | Grounded answers and summaries | OCR/result explanation, policy Q&A, record summaries |
| Navigational | Find and navigate to apps/processes | Jump to records, menus, review queues, actions |
| Transactional | Complete tasks conversationally | Create draft bills, activities, review items, proposals |
| Safety | Output reviewed before use | Approval-gated financial/compliance writes |
| Packaging | Microsoft 365 / Teams presence | M365/Teams agent or SaaS-integrated listing |

---

## Marketplace Quality Gates

Before submission, all must be true:

- [ ] Purpose statement defined
- [ ] Boundaries / non-goals documented
- [ ] Privacy / data handling statement
- [ ] Response-time and quality targets
- [ ] Grounded-response metrics
- [ ] Regression test suite
- [ ] Human-in-the-loop policy for risky actions
- [ ] Partner Center submission assets ready

---

## Current State

- `ipai_odoo_copilot` installed on `odoo_dev` (local)
- Foundry agent `ipai-odoo-copilot-azure` exists as seed
- 3 Odoo modules planned: `ipai_odoo_copilot`, `ipai_document_intelligence_bridge`, `ipai_copilot_actions`
- 4 Foundry agents planned: Copilot, Document Triage, Finance Review, Compliance/Workflow
- 4 OCR lanes: Read, Layout, Prebuilt, Custom

---

## Implementation Sequence (Phase 1 detail)

### Wave 1 — Lock the assistant surface

Goal: Stable front-door agent with knowledge, evals, tracing, and document extraction.

- [ ] Publish `ipai-odoo-copilot-azure` Foundry agent
- [ ] Attach guardrails and eval datasets
- [ ] Enable Foundry tracing
- [ ] Wire Document Intelligence for attachment OCR
- [ ] Agent reads Odoo context via scoped tools only

### Wave 2 — Build the action layer

Goal: Odoo actions trigger AI/OCR jobs, results write back as proposals.

- [ ] Create `ipai_copilot_actions` module with job/audit models
- [ ] Create `ipai_document_intelligence_bridge` module
- [ ] Add server actions for OCR on attachment upload
- [ ] Add automation rules for state-change triggers
- [ ] Status lifecycle: `queued` → `running` → `done` / `failed` / `needs_review`

### Wave 3 — Add approval and business model actions

Goal: Finance review, compliance gates, interactive Copilot on target models.

- [ ] Add finance review actions (bill/receipt proposals)
- [ ] Add approval gates for high-risk writes
- [ ] Add interactive Copilot UI actions on priority business models
- [ ] Add Document Triage and Finance Review agents to Foundry
- [ ] Wire approval/review UI in Odoo

### Wave 4 — Benchmark and evaluate

Goal: Complete SAP Joule benchmark, evaluation pack, Marketplace gap analysis.

- [ ] Run informational accuracy benchmarks
- [ ] Run navigational success benchmarks
- [ ] Run transactional proposal acceptance benchmarks
- [ ] Complete evaluation pack for all agents
- [ ] Document Marketplace readiness gaps

---

---

## Phase A3 — Administrative Plane Foundations
- implement system landscape registry
- implement bootstrap readiness checks
- implement close/control role model and authorization groups
- implement adapter/connection registry

## Phase B3 — Sandboxed Workspace Foundation
- implement workspace session model
- implement scoped context-pack loading
- implement direct artifact generation pipeline
- implement artifact preview, export, attach, and publish flows
- implement governed request-writeback flow for state-changing outputs

## Phase B4 — Skill Registry Hardening
- formalize the Odoo Copilot skill registry
- map current UI capability copy to real skills
- validate configuration/permission prerequisites per skill
- expose enabled/disabled status by environment and role
- prevent unsupported capability claims in runtime responses

## Phase B5 — Execution Mode Control
- implement execution mode model and policy matrix
- classify skills/actions into low-risk vs high-risk
- implement ask-before-acting as the default production mode
- implement scoped guarded autonomy for approved low-risk actions
- implement risk banners, confirmation prompts, and blocked-action explanations

## Phase B3.1 — Artifact Preview & Review
- implement inline preview renderer by artifact class
- implement tabular and structured preview modes
- implement compare/diff view for regenerated and prior-version outputs
- implement warning/confidence overlays
- implement preview-driven approval, regenerate, discard, export, attach, and writeback actions

## Phase B6 — Attachment Intake & Analysis
- implement attachment upload/session handling in the copilot UI
- implement file classification and routing
- implement spreadsheet/document/image/PDF analysis flows
- implement attachment-to-evidence and attachment-to-record review flows
- implement low-confidence / unsupported-file fallback states

## Phase B7 — Prompt-Pack Skill Pack Enablement
- register product and finance skill packs in the skill registry
- map academy-style use cases to concrete internal skills
- connect skill packs to sandboxed artifact generation and preview
- add seeded demo prompts and expected outputs
- enforce citations/source handling for research-oriented skills

## Phase C3 — Operational Reliability
- implement connector health monitoring
- implement sync/job status tracking
- implement degraded-mode behavior and alerts
- implement business-log visibility and retry workflows

## Phase C4 — Payment Orchestration
- detect configured payment rails/journals/providers
- implement payment readiness checks
- implement payment proposal and batch generation
- implement explicit confirmation step before execution
- implement payment evidence and post-execution logging

## Phase C5 — Databricks Handoff
- define destination registry for Databricks apps, dashboards, Genie spaces, notebooks, and folders
- define Odoo-context-to-Databricks mapping rules
- implement Open in Databricks action and optional Copilot toggle
- implement governed context-pack handoff
- implement return-link / back-to-Odoo behavior

## Phase D3 — Lifecycle Governance
- implement archive/restore workflows
- implement auditor export flows
- implement retention/anonymization/purge controls
- implement offboarding checklist and guarded destructive actions

---

## Runtime Rules

- artifact generation occurs in a sandboxed workspace, not directly against live production state
- workspace artifacts must have lifecycle states: draft, review-ready, approved-export, approved-writeback
- writeback/import/publish actions require explicit confirmation and audit logging
- every executable skill must declare its allowed execution modes
- production default is Ask Before Acting
- guarded autonomy must be scoped by role, environment, and action classification
- high-risk actions always require explicit human confirmation regardless of mode
- bootstrap readiness must be validated before production scenario execution
- admin-plane actions must be role-gated and audit-logged
- connector and degraded-mode state must be observable independently from scenario state
- archive/purge/offboarding actions require explicit governed workflows
- payment actions must validate underlying configuration before any execution path is offered
- payment execution requires explicit user confirmation and role validation
- payment proposals and executions must be audit-logged as first-class artifacts
- uploaded files are first-class workflow inputs
- all uploaded-file analysis occurs in the sandboxed workspace
- file-derived outputs may become findings, artifacts, drafts, or writeback proposals
- no file-derived state change may bypass explicit approval where required
- generated artifacts must enter preview state before downstream approval actions
- preview must expose artifact status, source context, and warning/confidence metadata
- regulated or finance-critical outputs require preview before export/publish/writeback
- research-oriented product/finance skills must surface sources when external/public facts are used
- strategy/content skills may generate artifacts in the sandbox but must not imply operational execution without the appropriate downstream skill and guardrails
- Databricks launches must resolve through a destination registry, not hard-coded scattered links
- handoff must preserve least-privilege context
- if no destination mapping exists, Odoo Copilot must say so explicitly rather than sending the user to a generic dead-end

---

## Repo Ownership for Implementation

| Module/Agent | Owning Repo |
| --- | --- |
| `ipai_odoo_copilot` | `odoo` |
| `ipai_document_intelligence_bridge` | `odoo` |
| `ipai_copilot_actions` | `odoo` |
| Foundry agent definitions | `agent-platform` |
| OCR normalization contracts | `platform` |
| Key Vault / identity wiring | `infra` |
| Evaluation datasets | `agent-platform` |
