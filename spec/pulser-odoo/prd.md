# PRD: Pulser for Odoo

> **Human-facing title**: `Pulser for Odoo`
> **Subtitle**: `Pulser Assistant for Odoo`
> **Canonical Slug**: `pulser-odoo`
> **Status**: Superseded
> **Superseded by**: [`spec/pulser-odoo-ph/`](../pulser-odoo-ph/) — Odoo 18 PH Copilot (full scope)
> **Constitution**: [constitution.md](constitution.md)
>
> This spec defined the tax-adapter-only scope. The canonical Pulser spec is now
> [`pulser-odoo-ph`](../pulser-odoo-ph/), which expands scope to finance review,
> PH compliance, approval-gated actions, and Foundry-backed agent runtime.

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

## Architecture Boundary: Replacing REST/FastAPI Correctly

Pulser for Odoo does not introduce a broad custom REST/FastAPI business layer.

**Canonical rule** (ref: `docs/architecture/ODOO_EDGE_AND_AGENT_BOUNDARIES.md`):

- Odoo remains the sole business system of record.
- Business logic must live in Odoo addons/services.
- Foundry/Pulser provides assistive orchestration, explanation, routing, and bounded tool use.
- HTTP/OpenAPI/FastAPI surfaces are allowed only as thin adapters for ingress, callbacks, upload, or tool invocation where required.

**The product must not:**

- Duplicate tax or accounting logic outside Odoo.
- Create parallel approval or posting engines.
- Expose raw business-object CRUD APIs as the default integration model.

---

## 15. SMART success criteria

### 15.1 Measurement windows
- **Pilot window:** first 30 days after internal enablement
- **Release 1 window:** by 60 days after Release 1 go-live
- **Production hardening window:** by 90 days after Release 1 go-live

### 15.2 Current baseline at spec time
Current observed platform baseline:
- Foundry runtime is active with **5/5 agents running**
- only **1 evaluation** has completed
- several release-gate eval definitions exist but most have **0 runs**
- **0 custom compliance policies** are configured
- **0 Foundry IQ indexes** are configured
- **0 red-team runs** exist
- **0 stored completions** exist

If these baselines materially change before execution starts, re-baseline the numeric targets without changing the intent of the criteria.

### 15.3 Product outcome criteria

| ID | Objective | Metric | Baseline | Target | Time bound |
|---|---|---:|---:|---:|---|
| SC-PH-01 | Reduce generic clarification in active Odoo forms | % of active-form interactions that ask unnecessary generic clarification | high / unmeasured | **< 10%** | Within 60 days |
| SC-PH-02 | Make Pulser transactionally useful | successful completion rate for supported draft-safe workflows (AP, AR, expense, payment assist) | 0 formal baseline | **>= 80%** on scoped pilot scenarios | Within 60 days |
| SC-PH-03 | Improve operator speed | median time from document upload to draft-ready decision for supported AP/expense flows | manual / undefined | **< 3 minutes** | Within 60 days |
| SC-PH-04 | Improve finance correctness | incorrect safe-action rate on evaluated finance scenarios | no formal baseline | **< 2%** | Within 90 days |
| SC-PH-05 | Enforce context correctness | wrong-company-context action incidents in production | 0 verified baseline | **0 incidents** | Continuous after Release 1 |

### 15.4 PH finance and compliance criteria

| ID | Objective | Metric | Baseline | Target | Time bound |
|---|---|---:|---:|---:|---|
| SC-PH-06 | AP readiness | vendor-bill intake scenarios correctly classified, validated, and routed | none | **>= 90%** on eval set | Within 60 days |
| SC-PH-07 | Expense readiness | expense-form scenarios correctly resolved to correct / blocked / not_yet_computable | none | **>= 90%** on eval set | Within 60 days |
| SC-PH-08 | Cash advance control | unresolved cash advances older than policy threshold with no owner | undefined | **100% owner-assigned; 0 unowned** | Within 75 days |
| SC-PH-09 | Cash advance liquidation discipline | cash advances liquidated, returned, or escalated by due date | undefined | **>= 95%** of scoped pilot advances | Within 90 days |
| SC-PH-10 | PH tax blocker detection | recall for VAT / withholding / TIN / ATC blockers on scoped PH tax eval set | none | **>= 95% recall** | Within 75 days |
| SC-PH-11 | BIR readiness quality | false-ready rate for 2307 / 2550Q reference / SAWT / SLSP readiness | none | **< 1%** on eval set | Within 90 days |
| SC-PH-12 | Close readiness | month-end / tax-period blocker scenarios correctly surfaced with correct next safe action | none | **>= 90%** on eval set | Within 90 days |

### 15.5 Governance and safety criteria

| ID | Objective | Metric | Baseline | Target | Time bound |
|---|---|---:|---:|---:|---|
| SC-PH-13 | Eliminate unsafe autonomous posting | silent-post or unauthorized final-post incidents caused by Pulser | 0 verified incidents | **0** | Continuous |
| SC-PH-14 | Enforce policy posture | number of custom Pulser compliance policies active in Foundry | 0 | **>= 4** active policies | Within 30 days |
| SC-PH-15 | Make evals real | core agents with at least one passing release-gate eval run | partial | **100% of core agents** | Within 45 days |
| SC-PH-16 | Establish replayability | curated stored completions covering success + failure finance paths | 0 | **>= 25** runs | Within 60 days |
| SC-PH-17 | Establish adversarial testing | completed red-team runs against Pulser core agent surfaces | 0 | **>= 1** initial run, then monthly cadence | First within 45 days |

### 15.6 Knowledge and integration criteria

| ID | Objective | Metric | Baseline | Target | Time bound |
|---|---|---:|---:|---:|---|
| SC-PH-18 | Establish enterprise grounding | production-useful Foundry IQ / Azure AI Search indexes attached for Pulser | 0 | **>= 1** | Within 30 days |
| SC-PH-19 | Reduce ungrounded finance responses | groundedness pass rate on finance RAG / policy-answer scenarios | none | **>= 95%** | Within 60 days |
| SC-PH-20 | Validate retrieval usefulness | retrieval/document-retrieval evaluator pass rate on scoped knowledge tasks | none | **>= 90%** | Within 60 days |
| SC-PH-21 | Complete safe DB grounding path | PostgreSQL MCP integration status | not connected | **connected read-only with successful validation query** | Within 30 days |
| SC-PH-22 | Improve runtime observability | core agents with enabled monitoring and actionable alerts | low | **100% of core agents monitored** | Within 45 days |

### 15.7 External BIR boundary criteria

| ID | Objective | Metric | Baseline | Target | Time bound |
|---|---|---:|---:|---:|---|
| SC-PH-23 | Preserve official-system boundary | incidents where Pulser labels a workflow "officially filed" or "officially paid" without verified external confirmation | none | **0 incidents** | Continuous |
| SC-PH-24 | Distinguish readiness from submission | BIR-bound workflows using explicit statuses (`ready_for_filing`, `submitted_externally_pending_confirmation`, `officially_confirmed`, etc.) | none | **100% of BIR-bound flows** | Within 60 days |

### 15.8 Exit criteria for "production-ready for PH scoped finance use"
Pulser for PH may be called **production-ready for scoped PH finance use** only when all of the following are true:

1. **SC-PH-13** is satisfied: zero silent-post incidents.
2. **SC-PH-14** is satisfied: at least 4 custom Pulser policies are active.
3. **SC-PH-15** is satisfied: all core agents have passing release-gate eval runs.
4. **SC-PH-17** is satisfied: at least one completed red-team run exists.
5. **SC-PH-18** is satisfied: at least one production-useful knowledge index is active.
6. **SC-PH-21** is satisfied: PostgreSQL MCP is connected read-only and validated.
7. **SC-PH-06**, **SC-PH-07**, **SC-PH-10**, and **SC-PH-12** are satisfied for AP, expense, PH tax, and close baseline capability.
8. **SC-PH-23** is satisfied: no false claims of official BIR completion.
9. **SC-PH-28** is satisfied: all publishable Office artifacts are retained and linked in Odoo Documents.

### 15.9 Professional Office publishing criteria

| ID | Objective | Metric | Baseline | Target | Time bound |
|---|---|---:|---:|---:|---|
| SC-PH-25 | Native Office artifact coverage | requested professional artifacts delivered as native PPTX / DOCX / XLSX instead of fallback-only formats | low / undefined | **≥ 95%** of scoped Office requests | Within 60 days |
| SC-PH-26 | Publishability pass rate | Office artifacts that pass publishability QA on first review cycle | none | **≥ 90%** on scoped pilot artifacts | Within 75 days |
| SC-PH-27 | Formatting defect escape rate | publishable artifacts requiring material formatting rework after QA | none | **< 10%** | Within 75 days |
| SC-PH-28 | Evidence linkage coverage | publishable Office artifacts with retained copy and linked evidence metadata in Odoo Documents | none | **100%** | Within 60 days |
| SC-PH-29 | Documents-grounded answer quality | artifact-related Pulser answers correctly grounded in retained Office artifacts when linked artifacts exist | none | **≥ 95%** on eval set | Within 90 days |
| SC-PH-30 | Preview / render QA coverage | generated Office artifacts with preview or render sanity check completed before publishable status | none | **100%** of publishable artifacts | Within 60 days |

### 15.10 Anti-vanity rule
The following do **not** count as success by themselves:
- number of agents running
- number of models deployed
- quota availability
- presence of default Microsoft guardrails
- number of eval definitions created without runs
- existence of datasets without active usage

Only measured behavior in supported PH finance workflows counts toward success.

### 15.11 Best-of-session consolidated SMART criteria

The table below cross-references the best-of-session targets against existing SC-PH IDs for dashboard binding. Where a new metric is introduced it carries a new `SC-PH-B` ID.

| ID | Objective | Metric | Target | Ref SC-PH |
|---|---|---:|---:|---|
| SC-PH-B01 | Faster finance execution | median upload-to-draft-ready decision | < 3 min | SC-PH-03 |
| SC-PH-B02 | Faster finance execution | finance-review turnaround reduction | ≥ 30% | SC-PH-02 (17.3) |
| SC-PH-B03 | Stronger controls | incorrect safe-action rate | < 2% | SC-PH-04 |
| SC-PH-B04 | Stronger controls | wrong-company-context incidents | 0 | SC-PH-05 |
| SC-PH-B05 | Cash advance discipline | overdue advances without owner | 0 | SC-PH-08 |
| SC-PH-B06 | Cash advance discipline | on-time liquidation / return / escalation | ≥ 95% | SC-PH-09 |
| SC-PH-B07 | PH readiness | VAT / withholding / TIN / ATC blocker recall | ≥ 95% | SC-PH-10 |
| SC-PH-B08 | PH readiness | false-ready rate for BIR readiness workflows | < 1% | SC-PH-11 |
| SC-PH-B09 | Close quality | correct close blocker surfacing | ≥ 90% | SC-PH-12 |
| SC-PH-B10 | Evidence discipline | evidence completeness for finance-critical workflows | ≥ 95% | SC-PH-28 (19.4) |
| SC-PH-B11 | Document grounding | finance-critical answers backed by retained artifacts when available | ≥ 95% | SC-PH-29 |
| SC-PH-B12 | Office publishing | native publishable PPTX / DOCX / XLSX coverage for scoped requests | ≥ 95% | SC-PH-25 |
| SC-PH-B13 | Office publishing | first-pass publishability QA success | ≥ 90% | SC-PH-26 |
| SC-PH-B14 | AI financial discipline | cost per successful workflow | measured and stable/declining | SC-PH (O6-KR1) |

---

## 16. Solution Kit packaging model

Pulser for PH must be packaged not only as a runtime product, but as a solution kit for regulated Philippine finance operations.

### 16.1 Kit components

**1. Prompt Packs**
- AP Prompt Pack
- AR Prompt Pack
- Expense & Cash Advance Prompt Pack
- PH Tax & BIR Prompt Pack
- Month-End Close Prompt Pack
- Controller / Reviewer Prompt Pack

**2. Prebuilt Expert Agents**
- Pulser AP Expert
- Pulser AR Expert
- Pulser Expense & Cash Advance Expert
- Pulser PH Tax Expert
- Pulser Close Expert
- Pulser BIR Boundary Expert

**3. Workflow Kits**
- vendor bill intake
- invoice readiness
- expense validation
- cash advance issuance and liquidation
- PH tax readiness
- BIR attachment readiness
- month-end close
- evidence pack generation

**4. Governance Kit**
- custom policy pack
- release-gate eval pack
- red-team starter pack
- monitoring/alert pack
- MCP read-only grounding pack

**5. Adoption Kit**
- executive overview
- operator enablement guide
- reviewer/controller guide
- implementation guide
- pilot-to-production guide
- ROI/FinOps worksheet

**6. Evidence Kit**
- AP review pack
- expense review pack
- cash advance aging pack
- BIR readiness pack
- close pack
- external confirmation/status pack

### 16.2 Packaging rationale

The product has two layers:

**Runtime layer**: Odoo 18 + OCA runtime, Foundry agents/skills/evals, MCP/knowledge/policies, BIR boundary workflows.

**Solution-kit layer**: Role-based prompt packs, prebuilt expert agents, workflow playbooks, governance/eval pack, adoption guides, ROI/FinOps/rollout materials.

This follows the pattern established by OpenAI Academy's financial services resource (solution-kit packaging for regulated institutions) combined with Azure AI Foundry's three-phase adoption model (establish AI foundation, build GenAI solutions efficiently, manage AI investments).

---

## 17. Measurable business case

Pulser for PH exists to improve Philippine finance operations inside Odoo by reducing manual effort, improving control quality, strengthening cash advance and working-capital discipline, improving PH tax/BIR readiness, and shortening close cycles.

### 17.1 Value pillars
1. Process efficiency
2. Control and correctness
3. Cash and working-capital discipline
4. PH compliance readiness
5. AI financial discipline

### 17.2 Primary pilot KPIs
- median time from document upload to draft-ready decision
- finance-review turnaround time
- incorrect safe-action rate
- overdue unresolved cash advances
- on-time liquidation / escalation rate
- VAT / withholding / TIN / ATC blocker recall
- false-ready rate for BIR readiness workflows
- correct close blocker surfacing rate
- cost per successfully completed workflow

### 17.3 Initial pilot targets
- < 3 minutes median upload-to-draft-ready decision
- >= 30% reduction in finance-review turnaround time
- < 2% incorrect safe-action rate
- 0 wrong-company-context incidents
- 0 silent-post incidents
- >= 95% cash advances liquidated, returned, or escalated by due date
- >= 95% VAT / withholding / TIN / ATC blocker recall
- < 1% false-ready rate for BIR readiness workflows
- >= 90% correct close blocker surfacing

### 17.4 Pilot scope (4 measurable workflows)
1. Vendor bill intake to draft
2. Expense + cash advance liquidation review
3. VAT / withholding / TIN / ATC readiness
4. Month-end blocker detection

---

## 18. Finance PPM OKR dashboard

Pulser for PH must expose its measurable business case through a Finance PPM OKR dashboard inside the Odoo operating workspace.

### 18.1 Architecture
The dashboard is decomposed as CE + OCA + thin delta:
- **CE native**: task kanban/graph/pivot views, milestones, dependencies, recurring tasks, activities
- **OCA**: `mis_builder` for KPI reports, `project_timeline` for Gantt, `project_pivot` for project-level pivot
- **Delta** (`ipai_finance_ppm`): `ppm.okr.objective` and `ppm.okr.key_result` models with 0.0-1.0 scoring

### 18.2 OKR model (O1-O6)

**O1 -- Faster finance execution**
- KR1: median upload-to-draft-ready < 3 min
- KR2: finance-review turnaround -30%
- KR3: supported workflow success rate >= 80%

**O2 -- Stronger control and correctness**
- KR1: incorrect safe-action rate < 2%
- KR2: wrong-company-context incidents = 0
- KR3: silent-post incidents = 0

**O3 -- Cash advance discipline**
- KR1: overdue advances without owner = 0
- KR2: on-time liquidation / return / escalation >= 95%
- KR3: outstanding advance aging trend improving

**O4 -- PH tax and BIR readiness**
- KR1: blocker recall >= 95%
- KR2: false-ready rate < 1%
- KR3: explicit readiness/submission state usage = 100%

**O5 -- Faster and safer close**
- KR1: correct close blocker surfacing >= 90%
- KR2: evidence pack completeness >= 95%
- KR3: critical-path tasks with owner + due date = 100%

**O6 -- AI financial discipline**
- KR1: cost per successful workflow is measured and trending down
- KR2: all core agents gated by evals
- KR3: policy + knowledge + red-team baseline complete

---

## 19. Documents is the retained-copy system for Finance PPM

### 19.1 Product rule
For finance, compliance, and close workflows:
- dashboard state is operational
- project tasks are executional
- Odoo Documents is the retained-copy and evidence surface

A workflow is not fully complete unless its required retained copies exist in Odoo Documents.

### 19.2 Required retained-copy classes
- original source artifacts (invoice PDF, receipt, request form)
- extracted structured payloads (JSON, XML)
- review summaries
- approval and signoff artifacts
- cash advance request and liquidation packs
- tax/BIR readiness packs
- close evidence packs
- external confirmations / acknowledgements
- exception notes and manual override justifications

### 19.3 Required linkage
Each retained copy must be linkable to:
- OKR objective and key result
- finance PPM project and milestone
- task
- company and branch
- fiscal period
- workflow lane (AP, AR, Expense, Cash Advance, PH Tax, BIR, Close)
- accounting record when applicable
- BIR external-state object when applicable

### 19.4 Completion rule
No finance-critical OKR, task, milestone, or readiness state should be considered complete if the required retained-copy set is missing from Odoo Documents.

### 19.5 Retained-copy policy by lane

**AP**: source invoice/bill, XML if present, extracted payload, review summary, duplicate-check result, draft creation result.

**Expenses**: receipt/source file, extracted payload, review note, reimbursement decision artifact.

**Cash advance**: request artifact, approval artifact, issuance proof, liquidation pack, return proof or escalation note.

**PH tax / BIR**: readiness report, blocker report, supporting schedules, generated submission pack, external acknowledgement/receipt.

**Close**: checklist snapshot, blocker report, dependency exception note, reviewer signoff, close evidence pack.

---

## 20. Pulser must answer from retained Documents evidence

### 20.1 Product rule
Odoo Documents is not only a storage surface. It is a governed grounding surface for Pulser. When retained evidence exists, Pulser must prefer that evidence over generic model-only explanation.

### 20.2 Answering priority
1. Active Odoo record context
2. Linked retained artifacts in Odoo Documents
3. Linked task / milestone / OKR context
4. Approved indexed policy / knowledge sources
5. Allowed external systems only when explicitly connected

### 20.3 Response classification
- `evidence_found`: direct evidence in retained files
- `evidence_found_with_inference`: conclusion drawn from multiple retained artifacts
- `evidence_missing`: required artifact not found
- `evidence_conflicting`: retained artifacts disagree
- `linked_file_not_readable`: file exists but cannot be interpreted

### 20.4 Required supported questions
Pulser must answer from retained Documents artifacts for:
- what evidence supports this status?
- why is this bill / expense / close item blocked?
- what file is missing for this KR or milestone?
- what changed between the source document and the draft?
- do we already have the BIR-ready attachment set?
- what signoff artifact is missing?

### 20.5 Guardrail
Pulser must not present unsupported claims as if they came from retained evidence. If no supporting file exists, Pulser must return missing-evidence status rather than imply support.

---

## 21. Required Finance PPM dashboard widgets

### 21.1 Evidence Completeness
% of KR-linked and milestone-linked workflows with required retained copies present in Odoo Documents.

### 21.2 Document Grounding Coverage
% of finance-critical Pulser answers backed by linked Odoo Documents artifacts.

### 21.3 Missing Evidence Queue
List of tasks / milestones / readiness states blocked by absent retained copies.

---

## 22. Professional Office Skills

### 22.1 Purpose

Define the office-artifact skill layer that lets Pulser create, revise, ground, review, and publish presentation decks, formal documents, and formula-safe workbooks at professional quality.

### 22.2 Office skill families

| Studio | Primary outputs | Grounding sources | Publish target |
|--------|----------------|-------------------|----------------|
| **PowerPoint Studio** | Exec decks, operating reviews, board updates | Odoo context, PPM metrics, retained visuals | PPTX / PDF |
| **Word Studio** | PRDs, policies, playbooks, close packs | Odoo docs, policy indexes, approvals | DOCX / PDF |
| **Excel Studio** | OKR dashboards, skill matrices, KPI scorecards | Record metrics, tasks, OKRs, derived formulas | XLSX |

### 22.3 Design and publishing standard

- Every artifact must be brand-safe, readable, traceable, and reviewer-ready.
- Pulser should use evidence-backed content, consistent typography, restrained color, and deliberate hierarchy.
- No artifact is considered complete until it passes render QA, reviewer checks, and retained-copy storage in Odoo Documents.

### 22.4 Grounding and evidence model

- Primary grounding order: active Odoo record context → linked Odoo Documents artifacts → Finance PPM task / milestone / OKR → approved policy indexes → allowed external systems.
- Pulser responses must classify support as `evidence_found`, `evidence_found_with_inference`, `evidence_missing`, or `evidence_conflicting`.
- Any publishable artifact that references finance-critical decisions must link back to its retained supporting files.

### 22.5 Studio responsibilities

#### PowerPoint Studio
Pulser must support:
- executive decks
- operating reviews
- close review decks
- roadmap decks
- board or steering-committee summaries
- publishable slide master alignment
- visually consistent charts, tables, and narrative pacing

#### Word Studio
Pulser must support:
- formal briefs
- policies
- implementation guides
- close memos
- compliance writeups
- reviewer and signoff packs
- professional heading hierarchy, page flow, and appendix structure

#### Excel Studio
Pulser must support:
- OKR scorecards
- KPI models
- scenario sheets
- roadmap sheets
- capability matrices
- formula-safe structured workbooks
- finance-ready tab layout and presentation quality

### 22.6 Capability matrix

| Studio | Primary outputs | Grounding sources | Quality gates | Publish target |
|--------|----------------|-------------------|---------------|----------------|
| PowerPoint | Exec decks, reviews, board updates | Odoo context, PPM metrics, retained visuals | story flow, no overflow, render QA | PPTX / PDF |
| Word | PRDs, policies, briefs, playbooks | Odoo docs, policy indexes, approvals | page render, hierarchy, citations, signoff | DOCX / PDF |
| Excel | KPI workbooks, matrices, models | Record metrics, tasks, OKRs, derived formulas | formula integrity, recalc, render QA | XLSX |

### 22.7 Business case and OKR linkage

| Objective | Key result | Target |
|-----------|-----------|--------|
| O1 Faster artifact production | Median first publishable draft cycle time | < 1 day |
| O2 Higher publication quality | Artifacts passing QA without major rework | ≥ 90% |
| O3 Stronger grounding | Publishable outputs backed by retained evidence | ≥ 95% |
| O4 Reviewer efficiency | Review turnaround on office artifacts | −30% |
| O5 Governance readiness | Artifacts stored in Documents with trace links | 100% |

### 22.8 Delivery workstreams

- **Workstream A — Skill definitions**: Define PowerPoint Studio, Word Studio, and Excel Studio prompts, schemas, and publish targets.
- **Workstream B — Native artifact generation**: Use native Office-generation libraries and Odoo-aware data contracts rather than brittle HTML exports.
- **Workstream C — Render and review gates**: Enforce render QA for decks, docs, and spreadsheets before publish.
- **Workstream D — Documents retention and grounding**: Keep source and derivative copies in Odoo Documents and make them retrievable by Pulser.
- **Workstream E — Finance PPM linkage**: Expose business-case KPIs, KR health, and evidence completeness in the dashboard.

### 22.9 Publishability QA (per-lane checks)

#### Common checks
- grounding completeness
- structure completeness
- missing-evidence detection
- retained-copy linkage
- naming/version sanity
- render/preview sanity

#### PowerPoint checks
- slide consistency
- readable layouts
- chart and table legibility
- narrative flow
- title/subtitle consistency

#### Word checks
- heading hierarchy
- paragraph consistency
- table and appendix consistency
- document completeness
- page-level readability

#### Excel checks
- workbook structure sanity
- formula integrity
- sheet naming consistency
- visible assumptions/notes where needed
- presentation quality of dashboards and models

### 22.10 Publish standard

**Pulser Professional Office Skills publish gate:**

1. Content is grounded in Odoo / Documents / approved knowledge.
2. Artifact renders cleanly with no overflow, overlap, or broken layout.
3. Reviewer notes are resolved and retained copies are stored in Odoo Documents.
4. Final output is ready to circulate externally without reformatting.

### 22.11 Retention and answering behavior

Every publishable Office artifact must:
- be retained in Odoo Documents
- be linkable to OKR / KR / milestone / task / period / owner
- support Pulser answering based on that retained artifact later

When a linked retained Office artifact exists, Pulser must prefer that retained artifact over generic model-only explanation.

Rendered HTML dashboards or one-off mockups do not satisfy the native artifact requirement when the requested output is an Office artifact.

### 22.12 Release roadmap

| Phase | Scope | Key deliverables |
|-------|-------|-----------------|
| R1 Foundation | Define studio schemas, replace HTML dashboard, native Odoo OKR views | PPT / Word / Excel skill contracts, OKR views live |
| R2 Core | Documents retention, grounded answering, first publishable templates | Evidence vault in Documents, publishable deck / doc / workbook set |
| R3 Hardening | Policies + evals + red-team + evidence completeness checks | Release gate, governed publish flow |

---

## 23. Solution accelerator pattern for Pulser Office skills

### 23.1 Accelerator framing

Pulser must package professional Office artifact generation as a solution-accelerator-style capability — not a simple "content generator." The pattern is: specialized multi-agent orchestration, grounded generation over enterprise data, compliance/validation pass before output, and explicit proof-of-concept vs production boundaries.

### 23.2 Capability family

```
pulser-office-publishing/
  triage                 → interpret request, classify artifact type
  source-grounding       → retrieve and rank enterprise data sources
  narrative-planning     → structure the artifact's story or schema
  ppt-generation         → native PPTX creation
  docx-generation        → native DOCX creation
  xlsx-generation        → native XLSX creation
  formatting-qa          → layout, overflow, brand, formula checks
  publishability-review  → governed pass/fail before output
  evidence-linking       → retain copies in Odoo Documents with trace links
```

### 23.3 Agent choreography

| Agent | Role | Inputs | Outputs |
|-------|------|--------|---------|
| Office Triage Agent | Interpret user request, classify artifact type and studio | User prompt, active Odoo context | Artifact type, studio assignment, scope |
| Office Planning Agent | Structure narrative arc or schema before generation | Triage output, grounding data | Outline, section plan, data bindings |
| Office Research / Grounding Agent | Retrieve and rank enterprise data from Odoo, Documents, knowledge indexes | Planning output, source identifiers | Grounded data payload with evidence classification |
| PowerPoint Studio Agent | Generate native PPTX from grounded data | Planning + grounding output | Draft PPTX artifact |
| Word Studio Agent | Generate native DOCX from grounded data | Planning + grounding output | Draft DOCX artifact |
| Excel Studio Agent | Generate native XLSX from grounded data | Planning + grounding output | Draft XLSX artifact |
| Publishability QA Agent | Run format, structure, grounding, and lane-specific QA | Draft artifact | QA scorecard, pass/fail, fix instructions |
| Evidence / Documents Agent | Retain copies in Odoo Documents with metadata and trace links | Approved artifact | Retained copy, trace links, evidence classification |

### 23.4 Required behavior

Pulser must:
- Interpret the user's artifact request via the triage agent.
- Ground content from approved enterprise sources (Odoo records, Documents, knowledge indexes).
- Generate native Office artifacts (PPTX, DOCX, XLSX) — not HTML facsimiles.
- Validate formatting and publishability before final output.
- Retain linked copies in Odoo Documents.
- Answer questions based on the retained artifacts.

### 23.5 Quality gates (per-lane)

| Gate | PowerPoint | Word | Excel |
|------|-----------|------|-------|
| Format QA | Slide bounds, font consistency, visual hierarchy | Pagination, orphan headers, margins | Cell overflow, column widths, print area |
| Structure QA | Story flow, narrative arc, data-to-insight | Heading hierarchy, TOC accuracy, section flow | Sheet organization, named ranges, tab structure |
| Grounding QA | All data points traced to source | All claims cited to Documents/records | All formulas grounded in source metrics |
| Brand/Layout QA | Color palette, typography, slide master | Document styling, header/footer | Conditional formatting, chart styling |
| Evidence-link QA | Deck linked to source OKRs/milestones | Document linked to approval chain | Workbook linked to source records |

### 23.6 Product rule

> **Pulser should not merely generate Office files. It should generate publishable, grounded, professionally formatted Office artifacts with retained evidence links.**

Office artifact generation is not "content generation." It is a governed professional publishing workflow for finance, compliance, close, and executive reporting.

### 23.7 Production boundary

| Stage | Scope | Gate |
|-------|-------|------|
| Proof-of-concept | Single-studio generation with manual review | Internal use only, no external circulation |
| Pilot | Multi-studio with QA pass, limited audience | Reviewer-approved, retained in Documents |
| Production | Full orchestration, publishability gate, evidence linking | Governed publish flow, external-ready |

---

## 24. Canonical capability families — product definition

### 24.1 Product summary
Pulser for PH is a Foundry-native, Odoo-grounded, agentic finance and project-operations expert for Philippine operations.

It combines:
- context-aware copilot experience in Odoo
- bounded multi-step agentic workflows
- finance/project/tax/close execution support
- evidence-grounded reasoning from Odoo Documents
- publishable Office artifact generation
- MCP-backed validation, tooling, and governance

### 24.2 Capability family scope definitions

#### 1. `pulser-data-foundation`
- Unified governed operational data from Odoo
- Transactional records: accounts, invoices, expenses, cash advances, vendors, customers
- Finance PPM OKR / key-result / milestone / task models
- Company / branch / fiscal period context
- Read-only grounded retrieval over live business state

#### 2. `pulser-copilot-experience`
- Odoo-native side-panel assistant surface
- Context-aware prompting and explanation
- Record-aware next-step guidance
- Review / block / escalate / recommend UX interactions
- Evidence-aware answers tied to retained Documents

#### 3. `pulser-agentic-workflows`
- Plan / decide / act behavior across multi-step workflows
- Bounded execution with safe-action routing
- Validation-before-completion for finance-critical actions
- Escalation, stop, and approval-gate rules
- Agentic lifecycle: Plan → Prototype → Create → Test → Review → Optimize → Secure

#### 4. `pulser-analytics-insights-planning`
- Analytics: real-time unified finance visibility and KPI dashboards
- Insights: proactive anomaly, risk, and opportunity detection
- Planning: scenario-based decisions, OKRs, milestones, and forecasts
- CFO operating triad: **analytics → insights → planning**

#### 5. `pulser-finance-close-and-reconciliation`
- Month-end / year-end / tax-period close orchestration
- Reconciliation assistance with confidence scoring
- Close blocker detection and dependency sequencing
- Evidence packs and signoff readiness
- Finance performance review support

#### 6. `pulser-project-spend-and-profitability`
- Time and expense review and approvals
- Project spend control and visibility
- Cash advance issuance and liquidation tracking
- Project profitability analysis
- Project-to-finance record linkage

#### 7. `pulser-ph-tax-and-bir-readiness`
- VAT / withholding / TIN / ATC validation
- 2307 / 2550Q / SAWT / SLSP readiness
- BIR evidence packs and attachment completeness
- Explicit BIR boundary status tracking (`ready_for_filing`, `submitted_externally_pending_confirmation`, `officially_confirmed`)
- Blocker routing for missing requirements

#### 8. `pulser-documents-evidence-grounding`
- Retained copies in Odoo Documents as governed grounding surface
- Evidence completeness computation
- Missing evidence queue and fail-closed behavior
- Answer-from-retained-evidence with response classification (`evidence_found`, `evidence_found_with_inference`, `evidence_missing`, `evidence_conflicting`)
- File-linked workflow support

#### 9. `pulser-office-publishing`
- PowerPoint Studio (custom native path — `python-pptx`)
- Word Studio (Foundry-native tool path + `python-docx`)
- Excel Studio (custom native path — `openpyxl`)
- Publishable-quality native Office outputs (PPTX / DOCX / XLSX)
- Publishability QA pass before release
- Retained artifact linkage in Odoo Documents

#### 10. `pulser-mcp-testing-review-security`
- MCP-backed read-only grounding (PostgreSQL, Foundry MCP Server, Azure DevOps MCP)
- Structured tool execution and tool-use policy
- Testing and validation harnesses (evals, stored completions)
- Review gates and red-team runs
- Runtime monitoring and alerting
- Security and governance controls (custom policies, zero-trust identity)

### 24.3 Foundry-first product stack

Pulser is built Foundry-first. See `plan.md §18` for the full repo baseline and capability-family architecture-layer map.

**Preferred template baselines**
- Get started with AI agents
- Multi-Agent Workflow Automation
- Multi-modal Content Processing
- Document Generation and Summarization
- Deploy Your AI Application in Production
- Data and Agent Governance and Security

**Preferred tool baselines**
- Azure AI Search (must-have)
- File Search (must-have)
- Azure Database for PostgreSQL, read-only MCP grounding (must-have)
- Foundry MCP Server (must-have)
- Azure DevOps MCP Server (must-have)
- GitHub (must-have)
- Code Interpreter (must-have)
- Browser Automation (very useful)
- Work IQ Word (very useful)
- Microsoft MCP Server for Enterprise (very useful)

### 24.4 Priority tiers

| Tier | Families | Rationale |
|------|----------|----------|
| 1 — Foundation | `pulser-data-foundation`, `pulser-copilot-experience`, `pulser-agentic-workflows`, `pulser-analytics-insights-planning`, `pulser-documents-evidence-grounding` | Prerequisites for all value delivery |
| 2 — Business execution | `pulser-finance-close-and-reconciliation`, `pulser-project-spend-and-profitability`, `pulser-ph-tax-and-bir-readiness` | Core PH finance value lanes |
| 3 — Scale and governance | `pulser-office-publishing`, `pulser-mcp-testing-review-security` | Governed publishing and production hardening |

Tier 1 families must be functionally in place before Tier 2 workflows are released to production. Tier 3 runs parallel but must complete before Gate D.

### 24.5 Product rule
All major Pulser features, workstreams, board epics, and release gates must map to one or more canonical capability families. Scope outside these families requires explicit spec amendment.

### 24.6 Agentic ERP product model
The winning conceptual model is: **data + Copilot + agents**, where agents plan, decide, and act.

**Strongest target finance lanes:**
- financial planning and analysis
- accounting and financial close
- tax management (PH/BIR)
- quote to cash
- cash management
- business performance management

---

## 25. Microsoft 365 developer sandbox posture

Pulser may use a Microsoft 365 Developer Program tenant as a sandbox for Office and Microsoft 365 integration development and testing.

### Intended uses
- Word, Excel, and PowerPoint add-in prototyping (`pulser-office-publishing`)
- Teams / SharePoint / Graph integration testing
- Office artifact rendering and review-loop validation
- Entra-authenticated M365 workflow experiments
- Publishability QA validation against a real M365 tenant

### Product rule
The Microsoft 365 developer tenant is a **development and testing environment only**.

It must not be treated as:
- a production tenant
- a durable business data store or long-term evidence vault
- the primary identity authority for customers or employees
- a substitute for Azure production infrastructure

### Canonical runtime split

| Lane | Surface |
|------|---------|
| Production runtime | Azure / Foundry / Odoo |
| Office/M365 integration sandbox | Microsoft 365 Developer Program tenant (dev/test only) |

### Subscription constraints to track
- One tenant per organization maximum
- 25 user licenses included
- Renewable based on qualified developer activity
- Does **not** include Azure — keep Azure infra in the primary Azure subscription
- Power BI Pro included (not Premium); sufficient for analytics prototypes only

---

## 26. Commercial and partner readiness

Pulser for PH must treat Microsoft Partner Center and commercial marketplace posture as part of production readiness tracking, separate from the 10 capability families.

### Proven commercial baseline
Current commercial identity baseline for InsightPulseAI:
- Authorized vetting status
- Seller ID: `94146040`
- Partner ID: `7097325`
- Commercial Marketplace publisher ID: `insightpulseai`
- Publisher name: `InsightPulseAI`
- Microsoft Entra tenant: `insightpulseai.com`
- DUNS: `719209694`

### Not yet proven
- Solutions Partner score (currently `0 / 100`, Not Started across all solution areas)
- Benefits redemption / Partner Marketing Center Pro activation
- Offer creation and marketplace publishing readiness

### Strategic growth lanes
For future partner-score alignment, prioritize:
- **Business Applications** — maps to Odoo / ERP / finance / project operations
- **Data & AI** — maps to Foundry / agentic workflows / analytics / AI copilots

### Product rule
Pulser may be treated as **commercially identity-ready** once publisher/legal identity is confirmed. It must not claim **Solutions Partner designation** until solution-area scoring and evidence are formally established.

> **Verification note**: Confirm seller contact name in Partner Center matches legal/canonical identity before any marketplace listing or partner-facing materials are published.

---

## 27. Reverse benchmark — Notion 3.0 → Pulser Agentic ERP Workspace

### 27.1 Product thesis

Pulser for PH should evolve from an assistant attached to Odoo into an **agent-centered operating surface** for finance and project operations.

The benchmark signal is the product shift represented by Notion 3.0 (launched September 2025):
- agents at the center of the product, not as a sidebar feature
- multi-step action rather than suggestion-only AI
- personalization and memory (instruction pages)
- team of specialist agents as the forward roadmap
- connectors/MCP-based tool reach
- explicit prompt-injection and security hardening

Pulser should apply those moves to **ERP finance operations**, not general knowledge work.

### 27.2 Positioning

Pulser is not a generic workspace agent. Pulser is a **domain-specialized agentic ERP workspace** for:
- finance execution (AP, AR, reconciliation)
- project spend and profitability
- PH tax and BIR readiness
- month-end / year-end / tax-period close
- evidence-backed reporting and publishable outputs

### 27.3 Core product promise

Anything a disciplined finance operator can do across the scoped Pulser surfaces, Pulser should progressively be able to: **understand → plan → execute in bounded steps → retain evidence → explain with citations → escalate when approval is required.**

### 27.4 Reverse-benchmarked product pillars

#### A. Agent-centered workspace
Pulser makes agents the primary execution interface for repetitive and research-heavy finance work, while preserving Odoo records as the system of action and Odoo Documents as the evidence system.

#### B. Multi-step workflow completion
Pulser must go beyond answering and editing. It must execute multi-step workflows:
- review document → extract data → check policy/tax blockers → prepare draft → retain evidence → notify reviewer
- gather evidence across Odoo and retained files → assemble close pack → surface blockers → route for signoff
- compile findings → produce structured report / dashboard / publishable artifact

#### C. Personalization and memory
Pulser should support explicit instruction and memory surfaces for:
- formatting preferences
- routing/escalation preferences
- recurring finance conventions
- project/company/branch context
- review style and artifact expectations

Memory is **subordinate** to:
1. Live Odoo state (highest authority)
2. Retained evidence in Odoo Documents
3. Workflow/policy state

#### D. Team of specialist agents
Pulser should evolve from one general assistant into a managed set of specialist agents:

| Agent | Primary lane |
|-------|-------------|
| AP Agent | Vendor bill intake, duplicate detection, draft creation |
| Expense & Cash Advance Agent | Review, approval, liquidation tracking |
| PH Tax/BIR Agent | VAT, withholding, TIN/ATC validation, readiness packs |
| Close Agent | Blocker detection, sequencing, evidence pack generation |
| Reporting/Publishing Agent | PPTX / DOCX / XLSX generation, publishability QA |
| Retrieval/Evidence Agent | Documents-grounded answers, missing-evidence detection |

#### E. Controlled connectors and MCP reach
Pulser extends safely across approved systems using:
- MCP-first tool access (Foundry MCP Server, PostgreSQL, Azure DevOps MCP, GitHub)
- approved connectors with scoped permissions
- auditable action traces for every tool call

#### F. Security by design
Pulser treats prompt injection, unsafe tool use, and evidence corruption as first-class risks:
- input and output safeguards at every execution boundary
- approval boundaries enforced before finance-critical actions
- evidence-aware reasoning (grounding before generation)
- session/action auditability via `ipai.copilot.audit`
- policy-constrained tool execution

### 27.5 Product requirements

| ID | Requirement |
|----|-------------|
| PR-A01 | Pulser must expose a clear agent-first entry point inside the Odoo operating experience |
| PR-A02 | Pulser must support long-running, bounded, multi-step work sessions with resumability and progress visibility |
| PR-A03 | Pulser must operate across multiple Odoo records, retained files, tasks/milestones/OKRs, and knowledge sources in a single workflow |
| PR-A04 | Pulser must support an editable instruction/memory surface per agent or user context, governed by ERP/policy authority rules |
| PR-A05 | Pulser must support creation and reuse of specialist agents by finance lane |
| PR-A06 | Every Pulser-generated operational artifact must remain linkable to retained evidence and, where relevant, be saved in Odoo Documents |
| PR-A07 | Pulser must generate native, professionally formatted PPTX / DOCX / XLSX for finance, close, and executive workflows |

### 27.6 Non-goals

Pulser should not attempt to mirror the full breadth of Notion's horizontal workspace. Pulser is not:
- a general team docs/wiki platform
- a general chat workspace or consumer productivity suite
- a project management system (Odoo Project + Plane cover this)

### 27.7 Competitive improvement over the benchmark

Compared with a horizontal agent workspace, Pulser should be better at:

| Dimension | Pulser advantage |
|-----------|-----------------|
| Grounding | System-of-record grounding (live Odoo state, not just indexed docs) |
| Control | Explicit approval boundaries and safe-action mediation |
| Domain depth | Finance-specific workflow decomposition (AP, close, BIR, reconciliation) |
| Evidence discipline | Fail-closed evidence retention; missing evidence = blocked state |
| Tax/compliance | PH-specific BIR readiness logic not present in horizontal tools |
| Publishing | ERP-grounded, evidence-linked native Office artifacts |
| Traceability | `ipai.copilot.audit` record for every interaction |

### 27.8 Benchmark-derived success criteria

| ID | Objective | Metric | Target | Window |
|----|-----------|--------|--------|--------|
| SC-PH-41 | Agent-first adoption | % of scoped pilot workflows initiated through Pulser agent entry points | ≥ 70% | 90 days |
| SC-PH-42 | Multi-step completion depth | % of scoped pilot workflows completing ≥ 3 bounded steps without manual re-orchestration | ≥ 80% | 90 days |
| SC-PH-43 | Instruction/memory utility | % of pilot users reporting measurable improvement from explicit Pulser memory/instruction surfaces | ≥ 80% | 90 days |
| SC-PH-44 | Specialist-agent coverage | Production-scoped specialist agents defined and usable for core lanes | ≥ 5 agents before GA | — |
| SC-PH-45 | Evidence-linked artifact integrity | Publishable Pulser-generated finance artifacts retaining evidence linkage before release | 100% | Continuous |

---

## 28. Cloud Adoption and Delivery Governance Baseline

Pulser for PH must align to a full Azure cloud adoption and delivery lifecycle rather than ad hoc workload deployment.

### 28.1 Required CAF lifecycle

| Phase | Pulser scope |
|-------|-------------|
| **Strategy** | Business justification, stakeholder alignment, operating model definition |
| **Plan** | Spec bundle, OKRs, delivery sequencing, board structure |
| **Ready** | Landing zone readiness — platform and application separation, IAM baseline |
| **Adopt** | Workload deployment — Odoo, Pulser agents, Foundry services |
| **Govern** | Policy compliance, IAM hygiene, drift detection, `PULSER-IAM-GATE-01` |
| **Secure** | Threat model, zero-trust identity, prompt injection hardening, WAF |
| **Manage** | Monitoring, alerting, cost control, SLA observability |

IAM/RBAC cleanup (`constitution.md §11`, `tasks.md Phase 28`) belongs to **Govern + Secure** — not side maintenance.

### 28.2 Delivery rule — Git/PR/pipeline

All Pulser code changes must follow (see `constitution.md §11` for invariants):
- Git-based source control — no TFVC
- pull-request review before merge
- protected branches with required status checks
- pipeline-driven environment changes — no manual mutations

### 28.3 Pipeline topology

| Pipeline | Trigger | Steps |
|----------|---------|-------|
| **PR pipeline** | Every PR to `odoo`, `agent-platform`, `infra` | Lint, type/static validation, unit tests, security/dependency checks, spec contract checks |
| **CI pipeline** | Merge to main | Repeat PR checks, integration tests, Key Vault secret fetch, build artifacts, build/push container images to ACR |
| **CD pipeline** | Artifact promotion | Deploy to staging, acceptance tests, manual validation for finance-critical flows, production release, smoke tests, rollback on failure |

### 28.4 Runtime rule

Pulser defaults to **container-based delivery** for all agent and web surfaces. Container images are built, versioned, and pushed to Azure Container Registry via CI pipeline. VM/IaaS deployment is the exception path and requires documented justification.

### 28.5 Azure DevOps role

| Use | Yes / No |
|-----|---------|
| Boards / work items | ✅ Yes |
| Pipelines (CI/CD) | ✅ Yes |
| Azure DevOps MCP Server | ✅ Yes |
| TFVC for Pulser repos | ❌ No |
| Azure DevOps Server on-prem | ❌ No — cloud-native baseline only |

### 28.6 Landing zone separation

Pulser Azure resources must be classified into distinct responsibility lanes:

| Lane | Scope |
|------|-------|
| **Platform landing zone** | Shared services: Key Vault, ACR, Log Analytics, AFD, DNS, shared networking |
| **Application landing zone** | Workload resources: Odoo ACA, Pulser agent runtime, Foundry services, PostgreSQL |
| **Security lane** | IAM, Defender, Policy, WAF — separate from platform/app responsibilities |

Do not collapse platform, application, and security responsibilities into a single subscription or resource group.

### 28.7 Delivery success criteria

| ID | Objective | Metric | Target |
|----|-----------|--------|--------|
| SC-PH-51 | PR discipline | Scoped repos with protected branches requiring PR flow | 100% |
| SC-PH-52 | Policy-gated merges | Key branches with required status checks before merge | 100% |
| SC-PH-53 | CAF completeness | Pulser operating model explicitly mapped to all 7 CAF phases | 100% |
| SC-PH-54 | Pipeline-driven changes | Staging and production environment changes executed through pipelines | 100% |
| SC-PH-55 | Container delivery baseline | Pulser runtime services built and published as versioned container images | 100% of scoped services |

### 28.8 What not to do

- ❌ TFVC for Pulser repos
- ❌ Azure DevOps Server on-prem without a hard regulatory requirement
- ❌ VM/IaaS as default runtime for Pulser agent or web surfaces
- ❌ Direct environment mutations outside pipeline execution
- ❌ Treating IAM/RBAC cleanup as optional post-launch work

---

## 29. Platform Governance and Identity Baseline

Pulser for PH must be operated as a governed internal platform capability, not just a collection of apps and agents.

### 29.1 Platform engineering posture
Pulser follows a platform engineering model as defined by Microsoft:
- **Product mindset**: The platform is a product for developers and business users.
- **Governed self-service**: Users act within a secure, predefined framework.
- **Reusable building blocks**: Prefer existing Azure/Foundry components.
- **Lifecycle management**: Continuous provisioning, measurement, and feedback.

### 29.2 Identity governance posture
Pulser enforces least privilege across five identity classes:
1. **Human Admins**: JIT/PIM required; no permanent subscription-level Owner.
2. **Business Users**: Entitlement-based access to workspace surfaces.
3. **Service Principals**: Scoped to specific resource boundaries; no broad Owner.
4. **Managed Identities**: Workload-specific roles only.
5. **Agent Identities**: Accountable human sponsor; explicit access reviews; no indefinite unmanaged access.

### 29.3 Governance Production Gates
Pulser is not production-ready while any of the following remain unresolved:
- Unexplained root-scope standing privileged access.
- Unknown principals with Owner access.
- Duplicate permanent Owner paths.
- Lack of privileged access review and JIT/PIM posture.

---

## 30. Finance Operations Application Benchmark (MB-500)

Pulser for PH must meet the standard of a serious finance-operations application platform, comparable to enterprise-grade Finance and Operations apps (Dynamics 365 benchmark).

### 30.1 Core capability areas
Pulser must satisfy the MB-500 benchmark across:
- **Architecture and solution design**: Durable ALM, spec-driven delivery.
- **Developer tooling**: Git-first, PR-driven, pipeline-enforced.
- **UI/Workspace/Reporting**: High-density finance dashboards, KPIs, and workspaces.
- **Integration and data management**: REST integration, OData patterns, business events.
- **Security controls**: XDS-like security policies, Duty/Role/Privilege separation.
- **Performance optimization**: Tracing, batch/async optimization, sandbox frameworks.

### 30.2 Reporting and Workspace requirements
Reporting is a first-class citizen in the Pulser workspace:
- **KPI Dashboards**: OKR and Finance PPM dashboards.
- **Close Packs**: Automated generation of month-end/year-end evidence folders.
- **Publishable Artifacts**: High-fidelity native PPTX, DOCX, and XLSX outputs.
- **Drill-through**: Viz to record drill-through between workspace and Odoo.

### 30.3 Security and Performance gates
Production gates must include finance-specific requirements:
- **IAM/RBAC cleanup**: Aligned with Least Privilege (EPIC-GOVERNANCE).
- **Audit Traceability**: `ipai.copilot.audit` as a continuous performance and security trace.
- **Async Reliability**: Formal job design for long-running finance batch processes.

---

## 31. Success Criteria Additions (Governance & Finance Ops)

| ID | Objective | Metric | Target |
|----|-----------|--------|--------|
| **Governance & Identity** | | | |
| SC-PH-46 | Least privilege baseline | Unknown principals with Owner access | 0 |
| SC-PH-47 | Root governance | Standing root-scope privileged assignments without approved exception | 0 |
| SC-PH-48 | Privileged access hygiene | Privileged human/admin paths using eligible or time-bound activation (PIM) | ≥ 90% |
| SC-PH-49 | Review discipline | Privileged roles covered by recurring access review | 100% |
| SC-PH-50 | Agent governance | Production Pulser agent identities with accountable sponsor/owner defined | 100% |
| **Finance Ops Maturity (MB-500)** | | | |
| SC-PH-56 | Finance-app completeness | Pulser roadmap explicitly mapped to MB-500 capability areas | 100% |
| SC-PH-57 | Reporting maturity | Scoped finance workflows with workspace/KPI/reporting support | ≥ 90% |
| SC-PH-58 | Integration maturity | Priority Pulser workflows with documented integration pattern and secrets strategy | 100% |

---

## 32. SaaS Tenancy Model

Pulser for PH is a B2B SaaS platform. Each customer organization is treated as a distinct Pulser tenant.

### 32.1 Tenancy rules
- **Tenant Independence**: Pulser tenant != Odoo company. Pulser tenant != Microsoft Entra tenant.
- **Boundary**: A Pulser tenant is the unit of policy, lifecycle, and service responsibility.
- **Multitenancy approach**: Shared control/runtime components may be used while preserving tenant isolation for sensitive data, evidence, and operational boundaries.

## 33. Control Plane Architecture

Pulser must include a productized control plane with two distinct layers.

### 33.1 Service-level Control Plane
- **Responsibilities**: Tenant onboarding, lifecycle state, deployment-stamp assignment, policy rollout, release targeting, and fleet health observability.

### 33.2 Tenant-level Admin Plane
- **Responsibilities**: Tenant admin settings, approved feature enablement, maintenance actions, evidence policy configuration, and tenant-specific health views.

## 34. Deployment Stamp Model

Pulser must scale through deployment stamps to minimize blast radius and support regional expansion.

### 34.1 Stamp composition
Each stamp includes:
- Odoo runtime components and Pulser agent services.
- Search/model/retrieval integration bindings.
- Observability/health wiring and stamp-scoped rollout controls.

### 34.2 Rollout rule
Pulser must support progressive rollout across stamps. Promoting a release must be done stamp-by-stamp, not all-at-once across the fleet.

## 35. Safe Rollout and Environment Routing

Pulser must support controlled exposure in production through modern Azure Container Apps (ACA) revision patterns.

### 35.1 ACA rollout posture
- **Revision-based deployment**: Use ACA revisions for every new release.
- **Label-based routing**: Utilize labels (e.g., `canary`, `stable`) for environment promotion.
- **Traffic splitting**: Support controlled traffic splits (e.g., 5% to canary) for zero-downtime releases.

### 35.2 Shift-right validation
Production validation is required for behaviors that cannot be fully simulated (e.g., live traffic patterns, cross-service resiliency, failover behavior).

## 36. Live-Site and Telemetry Model

Pulser must be operated as a "live site" with a primary focus on production reliability.

### 36.1 Operational posture
- **Actionable Alerting**: Alerts must be tied to customer or platform impact.
- **Telemetry rule**: High-fidelity logs, traces, and anomaly detection are mandatory for all runtime components.

## 37. Agent-Platform Reference Shape

The Pulser agent-platform runtime must reflect a multi-agent product architecture.
- **Planner/Router layer**: Orchestrates specialist agents.
- **Specialist Agents**: AP, Expense, Tax, Close, Publishing.
- **Integrations**: MCP-based tool access and secure data handling.
- **Management**: Explicit session and message lifecycle management.

## 38. Smart Success Criteria Addition (SaaS & Operations)

| ID | Objective | Metric | Target |
|----|-----------|--------|--------|
| SC-PH-59 | Tenant model clarity | Product/docs distinguish Pulser tenant, Odoo company, and Entra tenant | 100% |
| SC-PH-60 | Control plane coverage | Tenant onboarding and lifecycle operations mapped to designated planes | 100% |
| SC-PH-61 | Stamp readiness | At least 2 deployment-stamp-capable environments defined before GA | 100% |
| SC-PH-62 | Progressive rollout safety | Finance-critical releases support canary promotion and rollback | 100% |
| SC-PH-63 | Live-site telemetry | Production Pulser components emit actionable logs, traces, and alerts | 100% |
| SC-PH-64 | ACA safe routing | ACA services support revision and traffic-based rollout patterns | 100% |

---

## 39. Agent SDK and Channel Strategy

Pulser must distinguish between the core reasoning plane and the multichannel delivery layers.

### 39.1 Core runtime rule
The primary Pulser reasoning and retrieval plane remains:
- **Core Plane**: Azure AI Foundry / Azure OpenAI / Azure AI Search.
- **Logic**: Pulser SaaS control-plane logic and MCP-first tool access.
- **Authority**: Odoo-grounded workflow execution and evidence retention.

### 39.2 Microsoft Agents SDK (Enterprise Channel Shell)
Microsoft 365 Agents SDK is the primary channel/container layer for reaching enterprise surfaces:
- **Surface Reach**: M365 Copilot, Microsoft Teams, and custom Web/App channels.
- **Role**: Serves as the outer "multichannel shell" for delivery, state, and activity handling.
- **Integration**: Leverages Azure AI Foundry as the backend functionality plane.

### 39.3 GitHub Copilot SDK (Developer/Operator Runtime)
GitHub Copilot SDK is an optional embedded runtime for internal/operational lanes:
- **Scope**: GitHub-native developer workflows and internal release/devops assistants.
- **Role**: Provides repository-aware automation and planning for engineering personas.
- **Restriction**: Do not make GitHub Copilot SDK the default enterprise/customer runtime.

### 39.4 Identity and Architecture Priority
- **Identity Rule**: If Entra ID or managed identities are required, the core Foundry-native path must be used. GitHub Copilot SDK BYOK mode is restricted to scenarios compatible with key-based auth.
- **Priority Order**:
    1. **Foundry/Search/Odoo**: Core Runtime.
    2. **Microsoft Agents SDK**: Multichannel delivery/container shell.
    3. **GitHub Copilot SDK**: Optional developer/operator runtime extension.

---

## 40. Office Productivity and Multichannel Benchmarks

Pulser identifies the Microsoft Finance agents as the primary benchmark for Office-native finance user experiences.

### 40.1 Excel Benchmark Lane
Pulser must support an Excel-native experience comparable to:
- **Finance Reconciliation**: Assistance with discrepancy discovery and analysis.
- **Traceability**: Reusable action items and templates grounded in Odoo business records.
- **Autonomous Flows**: Low-latency reconciliation assistance within the spreadsheet surface.

### 40.2 Outlook Benchmark Lane
Pulser must support an Outlook-native experience comparable to:
- **Collections Workflows**: Identification and prioritization of collection tasks.
- **Account Context**: ERP-grounded customer and account context surfaced in the email rail.
- **Action Items**: Suggested responses, summaries, and automated ERP note-taking.

### 40.3 Platform Dependency Rule
While Pulser targets the UX/workflow outcomes of the Microsoft Finance benchmarks, it must **not** adopt their underlying platform dependency stack as a core requirement.
- **Dataverse/Copilot Studio**: Not required for core Pulser runtime; may be used as optional adapters only.
- **Billing/Licensing**: Pulser SaaS control plane remains the authority for tenant entitlement, not M365 per-seat Dataverse licensing.

---

## 41. End-to-end Business Architecture

Pulser is modeled on formal end-to-end business scenarios to ensure agents contribute to measurable process outcomes rather than isolated tasks.

### 41.1 Primary Scenarios
- **Project to Profit**: Direct benchmark from Dynamics 365 Project Operations. Connects sales, resourcing, project management, and finance to maximize profitability.
- **Record to Report**: Governs the finance-close spine, variance analysis, auditability, and retained evidence.

### 41.2 Supporting Scenarios
- **Source to Pay**: Anchors AP, expenses, cash advances, and tax treatment (BIR readiness).
- **Order to Cash**: Governs project billing, collections, and revenue realization.
- **Administer to Operate**: Anchors the Pulser control plane, tenant admin, IAM, and live-site operations.

### 41.3 Product Rule
Every Pulser capability must map to at least one end-to-end scenario. Feature "sprawl" outside of these governed process lanes is prohibited without a formal spec update.

### 41.4 Domain Mapping (Success Matrix)
| Domain | E2E Scenario | Primary Outcome |
|--------|--------------|-----------------|
| Finance PPM / OKRs | Project to Profit | Delivery Margin & OKR Achievement |
| Month-End Close / Audit | Record to Report | Statutory Compliance & Internal Audit |
| AP / Expense / Liquidation | Source to Pay | Spend Control & Tax Readiness |
| Billing / Collections | Order to Cash | Revenue Velocity & Collections efficiency |
| Control Plane / Tenant Ops | Administer to Operate | Platform uptime, security, & scale |

### 41.5 Smart Success Criteria Addition (Business Scenarios)

| ID | Objective | Metric | Target |
|----|-----------|--------|--------|
| SC-PH-65 | Scenario coverage | Pulser capabilities mapped to a formal end-to-end scenario | 100% |
| SC-PH-66 | Project-to-profit completeness | Scoped Finance PPM features mapped to project-to-profit flow | ≥ 90% |
| SC-PH-67 | Record-to-report completeness | Scoped close/reporting features mapped to record-to-report flow | ≥ 90% |
| SC-PH-68 | Platform-operability mapping | Control-plane and admin functions mapped to Administer to operate | 100% |

---

*Last updated: 2026-04-11*
