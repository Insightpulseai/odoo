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
