# Plan: Pulser for Odoo

> **Human-facing title**: `Pulser for Odoo`
> **Subtitle**: `Pulser Assistant for Odoo`
> **Canonical Slug**: `pulser-odoo`
> **Status**: Active
> **Companion spec**: [`spec/pulser-odoo-ph/plan.md`](../pulser-odoo-ph/plan.md) — PH-specific scope
> **Implementation Strategy**: Thin-bridge Odoo adapter with tri-modal agent routing.

---

## 1. Runtime Split & Architecture

The Pulser for Odoo system is split across two primary responsibility zones, following Microsoft's current architecture framing for Foundry Agents:

### 1.1 Use Foundry for:
- **Model Hosting & Agent Service**: Lifecycle and reasoning substrate.
- **Evaluations & Monitoring**: Quality and safety gates for the agent estate.
- **Guardrails**: Enterprise-ready content safety and groundedness checks.
- **Identity Boundary**: Microsoft Entra ID managed identity boundary.
- **Workflow Orchestration**: Sequential, human-in-the-loop, and group-chat patterns.

### 1.2 Use Odoo / App Runtime for:
- **ERP Integration**: Context packaging (active record, user ACLs).
- **Business Workflow Logic**: Final seat of technical and accounting authority.
- **Tool Adapters**: Bounded Odoo JSON-RPC or OpenAPI connectors.
- **Chat/Session UX**: The conversational shell (OWL component).
- **Domain Orchestration**: Selecting and routing to the correct agent for the task.

### 1.3 Best-Fit Reference Strategy
To ensure a production-ready rollout, the implementation adopts these benchmarks:
1. **`foundry-agent-webapp`**: Primary reference for the app/runtime pattern and Entra ID auth.
2. **`foundry-samples`**: Primary reference for Bicep/infra and service wiring examples.
3. **`Foundry-Local-Lab`**: Reference for local RAG and multi-agent experimentation.

---

## 2. Deployment Modes

### 2.1 Pilot Mode (MVP Default)
- **Runtime**: Lightweight agent shell on Azure Container Apps.
- **Networking**: Public endpoints with WAF protection.
- **Grounding**: File-based grounding (PDF/JSON) and live Odoo RPC.
- **Monitoring**: Application Insights baseline.

### 2.2 Governed Mode (Promotion Lane)
- **Runtime**: Managed Foundry Agent Service.
- **Networking**: Private endpoints and VNet isolation.
- **Grounding**: Azure AI Search with governed lakehouse grounding (Databricks).
- **Compliance**: Expanded tracing, evaluation, and safety gates.

---

## 3. Implementation Phases

### Phase 1: Bridge Foundations
1. Define tri-modal intent schema (Informational / Navigational / Transactional).
2. Establish the `ipai_odoo_copilot` module scaffold with security groups.
3. Build the context packager and HTTP provider for Foundry.
4. Implement the audit trail within Odoo.

### Phase 2: Finance-First Grounding
1. Implement Q&A context for Accounting (move, partner, bank).
2. Build Reconciliation and Collections assistance flows.
3. Wire domain agents (Expense, Project) with bounded tool access.
4. Implement the approval-gated action mediation pipeline.

### Phase 3: Knowledge & Compliance
1. Deploy RAG-only grounding for policies and SOPs.
2. Update global references to "Pulser for Odoo".
3. Apply Foundry description patches.
4. Finalize the release contract and ship-readiness checklist.

---

## 4. Technical Constraints

1. **ORM only**: No direct SQL writes; all actions go through the Odoo ORM.
2. **Security-First**: Context packaging must respect Odoo's native record rules and field-level permissions.
3. **No LLM in Odoo**: Keep the Odoo process thin; inference logic resides in Azure.
4. **Audit Completeness**: 100% request/response coverage is non-negotiable.

---

## 5. Workstream: REST/FastAPI Replacement by Strangler Pattern

**Goal**: Incrementally remove business logic from external REST/FastAPI layers and relocate it into Odoo-native services.

**Ref**: `docs/architecture/ODOO_EDGE_AND_AGENT_BOUNDARIES.md`

**Steps**:

1. Inventory all existing REST/FastAPI endpoints touching Odoo business objects.
2. Classify each endpoint:
   - **thin edge adapter** (keep)
   - **duplicated business logic** (migrate to Odoo)
   - **Azure control-plane wrapper** (replace with official SDK)
3. For duplicated business logic:
   - Move rules into Odoo addon/service layer
   - Keep only minimal adapter contracts
4. Replace Azure-specific wrappers with official Azure SDK/REST/Foundry SDK where feasible.
5. Prove parity through targeted tests and golden-path workflow validation.
6. Register all endpoints in `ssot/agent-platform/odoo_edge_inventory.yaml`.

---

## 6. Workstream: Prompt & Grounding Contract

**Goal**: Define and enforce how the LLM is prompted, grounded, and constrained for every Pulser finance interaction.

**Ref**: `rules/pulser-odoo.rules.yaml` (section `llm_application_controls`)

**Steps**:

1. Define model input schemas for each active Odoo screen (account.move, hr.expense, sale.order, project.project).
2. Define supporting context fields (company, branch, linked records, attachments).
3. Define output schemas per workflow (4 schemas in `agents/schemas/workflow/pulser/`).
4. Define fallback states: `not_found`, `not_yet_computable`, `needs_review`, `blocked`.
5. Configure low-variance inference settings for finance-critical tasks.
6. Create at least 1 Foundry IQ / AI Search index for finance policy grounding.

**Controls**:
- Task instruction first in every prompt.
- Structured output required for all finance workflows.
- Tool/retrieval use before unsupported generation.
- No chain-of-thought extraction as safety mechanism.

---

## 7. Workstream: Tool-First Validation Layer

**Goal**: Split classify/extract/validate/act into separate steps so that record inspection and config checks always run before action selection.

**Ref**: Workflow specs in `automations/workflows/odoo/pulser-*.yaml`

**Steps**:

1. Ensure every finance answer can point to a source record or extracted field.
2. Use the model to decide *what to check*, then use Odoo/data tools to *fetch the facts*.
3. For document workflows: model decides class -> extraction tool returns fields -> validation layer compares -> action layer creates or blocks.
4. Never let the model directly invent partner, tax, or posting state.

---

## 8. Workstream: Workflow Implementation

**Goal**: Implement the 4 core Pulser workflows in Azure AI Foundry.

**Ref**: `automations/workflows/odoo/pulser-*.yaml`, `agents/schemas/workflow/pulser/*.schema.json`

| Workflow | Pattern | SC-PH Coverage |
|----------|---------|----------------|
| `pulser-doc-intake-v1` | Sequential | SC-PH-03, SC-PH-06 |
| `pulser-form-validator-v1` | Sequential | SC-PH-01, SC-PH-07 |
| `pulser-payment-reconcile-v1` | Sequential | SC-PH-02 |
| `pulser-close-orchestrator-v1` | Human-in-the-loop | SC-PH-12 |

**Steps**:

1. Wire each workflow spec to Foundry workflow definitions.
2. Configure structured JSON output per schema.
3. Wire Odoo ORM calls for draft creation with idempotency keys.
4. Wire evidence persistence to Azure Blob Storage.
5. Wire human-in-the-loop gates for close orchestrator.

---

## 9. Workstream: Document Pipeline

**Goal**: Stand up the finance document-analysis contract using Azure Document Intelligence and Content Understanding.

**Steps**:

1. Provision Azure Blob Storage for raw document intake.
2. Wire Content Understanding Read/Layout as first-pass OCR.
3. Wire Document Intelligence prebuilt models for invoice/receipt/bill extraction.
4. Build PH-specific extraction schema (BIR fields, TIN, ATC, withholding).
5. Create classification eval dataset (min 50 samples per class).
6. Define extraction result storage schema.

---

## 10. Workstream: Governance & Hardening

**Goal**: Make evals, guardrails, and adversarial testing real.

**Steps**:

1. Configure >= 4 custom Pulser compliance policies in Foundry.
2. Run release-gate evals for all 5 core agents.
3. Complete >= 1 red-team run against Pulser core agent surfaces.
4. Curate >= 25 stored completions covering success + failure finance paths.
5. Set up actionable monitoring alerts for all core agents.
6. Implement runtime duplicate detection and company-context validation.

---

## 11. 8-Plane Architecture Reference

The complete Pulser production capability model spans 8 planes:

| # | Plane | Purpose |
|---|-------|---------|
| 1 | Data | Where data lives and is retained (Odoo/PG, Blob, extraction store) |
| 2 | Document Pipeline | How documents are ingested, extracted, and classified |
| 3 | LLM Application | How the model is prompted, grounded, and constrained |
| 4 | Decision / Policy | How business rules choose a safe action |
| 5 | Transaction | How Odoo records are created, updated, or blocked |
| 6 | Integration | How Pulser is exposed to other systems and clients |
| 7 | Governance / Control | Identity, auth, evals, adversarial testing, observability |
| 8 | Operating / Compliance | Close orchestration, compliance scenarios, evidence packs |

**Current status**: 0/8 PASS, 8/8 PARTIAL. See `docs/architecture/PULSER_8_PLANE_CAPABILITY_MATRIX.md`.

---

## 12. Finance PPM OKR Dashboard Implementation

### Execution substrate
Use the Odoo Project runtime as the operational execution surface:
- milestones for objective checkpoints
- task dependencies for close/tax sequencing
- recurring tasks for month-end and tax-period cadence
- task logs for effort/timing evidence
- scheduled activities for reviewer/approver follow-ups

### CE + OCA + Delta decomposition
See `docs/architecture/PPM_DASHBOARD_DECOMPOSITION.md` for the full matrix.

- **CE native**: task kanban/graph/pivot, milestones, dependencies, recurring, activities
- **OCA**: `mis_builder` (KPI reports), `project_timeline` (Gantt), `project_pivot`
- **Delta**: `ppm.okr.objective` + `ppm.okr.key_result` (0.0-1.0 scoring with computed RAG)

### Canonical project structure
Create one canonical finance program project:
- Pulser for PH — Finance PPM / OKR

Milestone groups:
- Foundation
- Finance Core (AP/AR)
- Cash Advance
- PH Tax / BIR
- Close
- Governance / Evals / Launch

### Metric sources
- AP / AR draft and review events
- expense and cash advance states
- tax readiness result states
- close blocker states
- task, milestone, and activity states
- eval / policy / knowledge / red-team gate states
- AI workflow volume and cost telemetry

---

## 13. Finance PPM Document-Retention Model

### Operating split
- Finance PPM dashboard = status, KPIs, blockers, OKRs, execution
- Odoo Documents = copies of evidence, source artifacts, generated packs, receipts, approvals

### Required document directories
- Finance PPM / 00 Executive OKRs
- Finance PPM / 01 AP
- Finance PPM / 02 AR
- Finance PPM / 03 Expenses
- Finance PPM / 04 Cash Advance
- Finance PPM / 05 PH Tax
- Finance PPM / 06 BIR Ready
- Finance PPM / 07 Close
- Finance PPM / 08 Approvals
- Finance PPM / 09 External Confirmations
- Finance PPM / 10 Identity
- Finance PPM / 11 Office Publishing
- Finance PPM / 99 Archive

### Metadata model
Each file copy should carry metadata/tags for: fiscal period, company, branch, lane, milestone, OKR/KR, task, owner, reviewer, approver, evidence type, external status.

---

## 14. Odoo Documents as Pulser Grounding Surface

### Retrieval model
Pulser retrieves from Odoo Documents using: directory, tags/metadata, linked task/milestone/KR, linked accounting record, company/branch/period, evidence type.

### Answering model
1. Inspect active record context
2. Retrieve linked Odoo Documents artifacts
3. Check linked task/milestone/OKR context
4. Form an evidence-backed answer
5. Return file-aware reasoning and missing-evidence notices

### Guardrail
Pulser must not present unsupported claims as if they came from retained evidence. If no supporting file exists in Odoo Documents, Pulser must say evidence is missing.

---

## 15. Professional Office Skills — Studio Architecture

### Architecture pattern

```
1. Inputs          →  Odoo records, PPM objects, retained Documents, approved knowledge
2. Grounding       →  Active record context, linked artifacts, evidence classification
3. Studio gen      →  PowerPoint Studio / Word Studio / Excel Studio
4. QA & review     →  Render QA, story flow, hierarchy, formula integrity, DOCX/XLSX/PPTX checks
5. Publish         →  Retained copies stored in Odoo Documents, derivative artifacts with trace links
```

**Rule**: If retained evidence exists in Odoo Documents, Pulser should prefer that evidence over generic model-only explanation.

### Studio definitions

| Studio | Core services | Grounding surface | Output formats |
|--------|--------------|-------------------|----------------|
| PowerPoint Studio | Skill orchestration, narrative structure, visual layout, slide generation | PPM OKRs, retained visuals, Odoo metrics | PPTX, PDF |
| Word Studio | Formal document structure, policy/procedure formatting, review workflow | Odoo Documents, approved policies, approval artifacts | DOCX, PDF |
| Excel Studio | Formula-safe workbook generation, KPI model building, scenario analysis | Record metrics, OKR scores, derived formulas | XLSX |

### Publish gate (all studios)

1. Content grounded in Odoo / Documents / approved knowledge.
2. Artifact renders cleanly with no overflow, overlap, or broken layout.
3. Reviewer notes resolved and retained copies stored in Odoo Documents.
4. Final output ready to circulate externally without reformatting.

### Finance PPM dashboard + Documents vault linkage

- **Finance PPM dashboard**: Status, KPIs, blockers, OKRs, execution.
- **Odoo Documents vault**: Source files and derivative publishable artifacts.
  - Grounded in Odoo / Documents / approved knowledge
  - Copies stored with trace links back to OKR/KR/milestone
  - BIR readiness packs and close packs retained as publishable artifacts
  - External confirmation and approval artifacts archived

### Publishable-quality targets

| Metric | Target |
|--------|--------|
| First publishable draft cycle | < 1 day |
| QA pass without major rework | ≥ 90% |
| Grounded publishable outputs | ≥ 95% |
| Reviewer turnaround improvement | −30% |
| Artifacts retained with trace links | 100% |

### Release phases

| Phase | Scope | Deliverables |
|-------|-------|-------------|
| R1 Foundation | Define studio schemas, replace HTML dashboard, native Odoo OKR views | Skill contracts, OKR views, spec bundle patch |
| R2 Core | Documents retention, grounded answering, first publishable templates | Evidence vault live, publishable artifact set |
| R3 Hardening | Policies + evals + red-team + evidence completeness checks | Release gate, governed publish flow |

---

## 16. Office Publishing Accelerator Model

### Multi-agent orchestration

Use a specialized agent choreography pattern for professional Office artifact creation:

```
User request
  ↓
[1. Triage Agent]         → classify artifact type, assign studio
  ↓
[2. Planning Agent]       → structure outline, section plan, data bindings
  ↓
[3. Grounding Agent]      → retrieve enterprise data, classify evidence
  ↓
[4. Studio Agent]         → generate native PPTX / DOCX / XLSX
  (PPT | Word | Excel)
  ↓
[5. Publishability QA]    → format, structure, grounding, lane-specific checks
  ↓                         ↓ (fail → loop back to Studio Agent with fix instructions)
[6. Evidence Agent]       → retain in Odoo Documents with trace links
  ↓
Publishable artifact + retained copy
```

### Agent responsibilities

| Agent | Owns | Does not own |
|-------|------|--------------|
| Triage | Request interpretation, studio routing | Content generation |
| Planning | Narrative structure, data binding plan | Source retrieval |
| Grounding | Enterprise data retrieval, evidence classification | Artifact creation |
| Studio (×3) | Native file generation, brand-safe formatting | Quality validation |
| Publishability QA | Pass/fail gate, fix instructions | File generation |
| Evidence / Documents | Retention, trace links, metadata tagging | Content review |

### Native output requirement

The preferred outputs are native Office formats — not HTML exports, screenshots, or PDF-only:

| Format | Library | Use |
|--------|---------|-----|
| PPTX | `python-pptx` | Narrative decks, board updates, operating reviews |
| DOCX | `python-docx` | Formal documents, policies, close packs |
| XLSX | `openpyxl` | KPI models, OKR dashboards, scenario workbooks |

### Validation requirement

No Office artifact should be marked publishable unless it passes:

1. **Layout/format checks** — no overflow, consistent styling, clean render
2. **Grounding checks** — all data points traced to enterprise sources
3. **Evidence-link checks** — retained copy in Odoo Documents with trace links
4. **Lane-specific QA** — story flow (slides), hierarchy/citations (docs), formula integrity (sheets)

### Publishability scoring

| Score | Meaning | Action |
|-------|---------|--------|
| ≥ 90% | Publishable | Release to audience |
| 70–89% | Needs minor revision | Auto-fix or single reviewer pass |
| < 70% | Needs rework | Loop back to planning/generation |

---

## 17. CE / OCA / Thin-Delta Decomposition

### Odoo CE 18 native
Use natively for:
- Project tasks, milestones, dependencies, recurring tasks, activities
- Odoo Documents
- Expenses
- Invoicing/accounting core
- `mail.thread` and activity workflows

### OCA
Use for:
- Analytics and pivots (`mis_builder`, `project_pivot`)
- Project reporting enhancements (`project_timeline`)
- Accounting/project extensions where stable and aligned
- Any must-have modules that reduce custom delta

### Thin delta (`ipai_finance_ppm` and adjacent bridge modules)
Build only where neither native nor OCA covers the need:
- OKR objective and key-result models
- Finance PPM dashboard composition
- Evidence completeness computation
- Missing evidence queue
- PH tax/BIR readiness state machine
- Documents-grounded response linkage
- Publishability QA orchestration
- Pulser-specific skill routing and safe-action policy

**Rule**: Do not build custom delta modules where native Odoo 18 or OCA already covers the capability sufficiently.

---

## 18. Foundry-Native Runtime Posture

### Canonical runtime shell
Use a Foundry-native web/gateway shell with Entra-aware authentication and Foundry agent integration as the baseline product posture.

### Canonical repo baseline

**Foundry-org repos**

| Repo | Role | Use |
|------|------|-----|
| `foundry-agent-webapp` | Primary app shell | Entra-aware web/gateway surface with Foundry Agents integration. Adopt directly. |
| `foundry-samples` | Patterns and Bicep | Reference repo for infra, service wiring, and sample implementations. Adopt directly. |
| `Foundry-Local-Lab` | Dev/experiment only | Local RAG and multi-agent experimentation. Reference only. |
| `foundry-mcp-playground` | MCP sandbox | Experimental MCP surface. Playground only. |
| `mcp-foundry` | Deprecated | Moved to cloud; replaced by Foundry MCP Server. Do not use as primary. |

**Microsoft OSS repos**

| Tier | Repo | Use |
|------|------|-----|
| 1 — Adopt directly | `microsoft/agent-framework` | Core multi-agent orchestration and deployment substrate |
| 1 — Adopt directly | `microsoft/azure-skills` | Azure-facing skill packaging baseline |
| 1 — Adopt directly | `microsoft/skills` | Skill catalog structure and MCP server patterns |
| 1 — Adopt directly | `microsoft/azure-devops-mcp` | Boards / work-item / pipeline-aware agent governance |
| 1 — Adopt directly | `microsoft/agent-governance-toolkit` | Policy enforcement, zero-trust identity, execution sandboxing, reliability engineering |
| 1 — Adopt directly | `microsoft/Multi-Agent-Custom-Automation-Engine-Solution-Accelerator` | Solution-accelerator packaging pattern for productionized multi-agent systems |
| 2 — Reference | `microsoft/autogen` | Ecosystem reference; not the primary orchestration base |
| 2 — Reference | `microsoft/semanticworkbench` | Prototyping and eval harness reference |
| 2 — Reference | `microsoft/powerbi-modeling-mcp` | Optional for CFO/FP&A governed reporting layer |

### Template adoption set
Adopt patterns from:
- Get started with AI agents
- Multi-Agent Workflow Automation
- Multi-modal Content Processing
- Document Generation and Summarization
- Deploy Your AI Application in Production
- **Data and Agent Governance and Security** ← governance/security baseline for finance-critical flows

### Tooling adoption set
Enable and standardize around:

| Tool | Purpose | Priority |
|------|----------|----------|
| Azure AI Search | Finance knowledge indexing and agentic retrieval | Must-have |
| File Search | Evidence/document retrieval | Must-have |
| Azure Database for PostgreSQL | Read-only MCP grounding | Must-have |
| Foundry MCP Server | Canonical tool exposure | Must-have |
| Azure DevOps MCP Server | Board/progress sync and release-gate tracking | Must-have |
| GitHub | Spec, skills, workflow, and template sourcing | Must-have |
| Code Interpreter | Formula validation, scenario computation | Must-have |
| Browser Automation | BIR portal and external confirmation workflows | Very useful |
| Work IQ Word | Word document generation | Very useful |
| Microsoft MCP Server for Enterprise | Entra/directory-aware enterprise flows | Very useful |
| Azure Speech MCP Server | Voice mode only if explicitly scoped | Optional |

**Office tool gap note**: `Work IQ Word` covers the Word lane via a Foundry-native tool path. No equivalent first-party PowerPoint or Excel tools are currently in the catalog. PowerPoint and Excel generation must use the custom native-artifact path (`python-pptx`, `openpyxl`) defined in Phases 17–22 of `tasks.md`.

### Capability-family architecture layers

Map every implementation phase to one of three architecture layers:

**Foundation layer** (Tier 1 — must be in place first)
- `pulser-data-foundation` → Azure AI Search + File Search + PostgreSQL tool + Odoo context
- `pulser-copilot-experience` → `foundry-agent-webapp` + Get started with AI agents
- `pulser-agentic-workflows` → `agent-framework` + Multi-Agent Workflow Automation
- `pulser-analytics-insights-planning` → agent templates + OKR dashboard + `powerbi-modeling-mcp` (optional)
- `pulser-documents-evidence-grounding` → Multi-modal Content Processing + File Search + Azure AI Search

**Business execution layer** (Tier 2 — core value delivery)
- `pulser-finance-close-and-reconciliation` → agent orchestration + PostgreSQL + governance/security template
- `pulser-project-spend-and-profitability` → agent orchestration + Odoo/Postgres grounding
- `pulser-ph-tax-and-bir-readiness` → Multi-modal Content Processing + Browser Automation + Documents grounding

**Scaling and governance layer** (Tier 3 — governed publishing and hardening)
- `pulser-office-publishing` → Document Generation and Summarization + Work IQ Word + Code Interpreter + custom PPTX/XLSX path
- `pulser-mcp-testing-review-security` → Foundry MCP Server + `azure-devops-mcp` + `agent-governance-toolkit` + `skills` + GitHub

---

## 19. Agentic Lifecycle

Pulser workflows must follow this lifecycle:

```
Plan → Prototype → Create → Test → Review → Optimize → Secure
```

**Design rule**: No finance-critical workflow may jump from generation to completion without validation and review boundaries.

| Stage | Gate |
|-------|------|
| Plan | Spec bundle valid, SC-PH criteria bound |
| Prototype | Workflow runs in sandbox with test data |
| Create | Agents wired, schemas validated, evals defined |
| Test | Release-gate evals passing, red-team run complete |
| Review | Reviewer signoff, evidence retained in Documents |
| Optimize | Cost/latency measured, declining trend confirmed |
| Secure | Policies active, governance baseline complete |

---

## 20. Release Gates (A–D)

### Gate A — Foundation
- Identity and access path verified (Entra login + service identity)
- Data foundation in place (Odoo records, OKR/KR models live)
- Documents vault directory structure created (00–99)
- OKR objectives seeded and milestone structure defined

### Gate B — Pilot Workflows
- AP / expenses / tax readiness / close blocker detection working
- Evidence retention enforced for all pilot workflow lanes
- Finance PPM dashboard widgets populated from live data
- PostgreSQL MCP connected read-only and validated

### Gate C — Publishing
- PPTX / DOCX / XLSX native generation live
- Publishability QA enforced (all three studios)
- Retained-copy linkage working in Odoo Documents
- Evidence-grounded artifact answering working

### Gate D — Production
- Governance/evals in place (≥ 4 custom policies, ≥ 1 red-team run)
- MCP/tool boundaries documented
- Cost/usage measurement live and trending
- Missing-evidence fail-closed behavior live
- All SC-PH exit criteria from `prd.md §15.8` satisfied

---

## 21. Agent-Centered ERP Workspace — Implementation Model

> **Benchmark**: Notion 3.0 product shift (September 2025)  
> **Ref**: `prd.md §27`  
> **Rule**: Copy the product shape, not the horizontal scope.

### Implementation themes

| Theme | Pulser-native translation |
|-------|--------------------------|
| Agent-first entry | Dedicated agent entry point in Odoo side-panel; agent routing before RAG-only Q&A |
| Multi-step execution | Foundry sequential + human-in-the-loop orchestration patterns; resumable workflow state |
| Memory/instructions | Per-agent instruction YAML stored in Odoo config; user preference surface in side-panel |
| Specialist agents | One agent per capability family lane (AP, Expense, PH Tax, Close, Publishing, Retrieval) |
| Connector reach | MCP-first: Foundry MCP, PostgreSQL, Azure DevOps MCP, GitHub, Work IQ Word |
| Security hardening | Input/output safeguards at every MCP boundary; prompt injection in eval and red-team scope |

### Design rule — authority model
Pulser copies the benchmark's product shape but keeps its own authority model:

```
System of action:     Odoo (records, ORM, audit)
Evidence authority:   Odoo Documents (retained copies, grounding surface)
Execution boundaries: Policy/review gates, approval thresholds, PIM-gated identity
Memory authority:     Subordinate to live Odoo state and retained evidence
```

### Specialist agent sequencing

Build specialist agents in this order (matches capability family tiers):

| Agent | Tier | Maps to |
|-------|------|---------|
| Retrieval/Evidence Agent | 1 | `pulser-documents-evidence-grounding` |
| AP Agent | 2 | `pulser-finance-close-and-reconciliation` / `pulser-data-foundation` |
| Expense & Cash Advance Agent | 2 | `pulser-project-spend-and-profitability` |
| PH Tax/BIR Agent | 2 | `pulser-ph-tax-and-bir-readiness` |
| Close Agent | 2 | `pulser-finance-close-and-reconciliation` |
| Reporting/Publishing Agent | 3 | `pulser-office-publishing` |

### Prompt injection and connector security

Treat as engineering requirements, not afterthoughts:
- All MCP tool inputs sanitized before execution
- All MCP tool outputs validated against expected schema before action
- Injection-test scenarios added to red-team eval pack
- Tool execution logged to `ipai.copilot.audit` with tool name, inputs hash, action result
- No tool may write to Odoo without user confirmation (existing safe-action gate enforced)

---

## 22. Finance Operations Platform Implementation Model

> **Benchmark**: MB-500 (Dynamics 365 Finance & Operations Developer)  
> **Rule**: Build a platform, not an assistant.

### Implementation themes

| Lane | Pulser-native implementation |
|------|-----------------------------|
| **ALM & Tooling** | Git + PR + Pipelines (`constitution.md §11`) |
| **Architecture** | CE/OCA/Delta decomposition (`plan.md §17`) |
| **UI/Workspaces** | Foundry-native webapp + high-density dashboards |
| **Integration** | MCP-first connectors + OData/REST bridges |
| **Security** | RBAC/IAM Remediation (`AZURE_IAM_REMEDIATION.md`) |
| **Performance** | Async job framework for long-running finance tasks |

### Reporting surface implementation
- **Dashboards**: Pulser Finance PPM Dashboard (Phase 13).
- **Artifacts**: Azure-native document generation for PPTX/DOCX/XLSX.
- **KPIs**: Mapped to SMART criteria in `prd.md §15.8` and §31.

---

*Last updated: 2026-04-11*
