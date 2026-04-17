# Copilot Target-State — Constitution

> Non-negotiable rules governing the InsightPulseAI Odoo-on-Azure architecture.
> Entra-governed, CAF-aligned landing-zone workload: Odoo in application landing zones,
> Foundry and Document Intelligence as bounded AI services, Azure DevOps/GitHub as delivery spine.

---

## C1: Entra is the identity plane

- Humans sign in through **Microsoft Entra ID**
- Odoo runtime, jobs, and integrations use **managed identity / workload identity**
- Foundry-hosted agents are **governed agent identities**, not anonymous runtime actors
- Keycloak is transitional — Entra is the target IdP

## C2: Azure Landing Zone is the platform foundation

- One **platform landing zone** for shared identity, connectivity, management
- **Application landing zones** per workload: `odoo-dev/staging/prod`, `agent-platform`, `data-intelligence`
- AI workloads (Foundry, Document Intelligence) deploy **inside normal application landing zones**, not a separate AI zone
- CAF alignment is the structural authority

## C3: Odoo is the transactional system of record

- Odoo 18 owns accounting, CRM, projects, expenses, approvals, documents, posted business records
- Odoo exposes **server actions, automation rules, scheduled actions, client actions** as the trigger layer
- Business state is persisted and approved in Odoo, not in agent memory or external services
- Copilot explains, inspects, routes, and triggers — it never replaces the workflow engine

## C4: Foundry is the hosted AI runtime

- Azure AI Foundry Agent Service hosts bounded agents, not one universal agent
- Agent set: **Copilot**, **Document Triage**, **Finance Review**, **Compliance/Workflow**
- Agents use **scoped tools** (`get_record_context`, `submit_ocr_job`, `write_review_result`, `create_activity`, `post_chatter_note`)
- Agents do NOT receive unrestricted DB or ORM mutation capability
- Tool invocations are logged with correlation IDs

## C5: Document Intelligence is the extraction layer

- Pattern: **Document Intelligence first, Foundry interpretation second**
- Do not send raw PDFs/images straight to an LLM for structured business data
- Four extraction lanes: Read OCR, Layout/table, Prebuilt, Custom (PH/BIR/vendor)
- Normalized extraction output is what Odoo consumes — not raw OCR text

## C6: Odoo Copilot is the interaction layer, not the agent

- Systray/inline widget in Odoo
- Client actions for interactive prompts
- Server actions / automation rules for background workflows
- Odoo-side job and audit models
- Bounded service clients for Foundry and Document Intelligence
- Approval UI for high-risk outputs

## C7: Financial and compliance writes are proposal-first

- AI-generated financial outcomes are **proposals**, not auto-posted transactions
- Low-confidence results are flagged for manual review
- No posted journal entry without explicit human approval
- Approval policy is configurable by group/role
- Approved/rejected/edited outcomes are logged with full audit trail

## C8: Azure DevOps + GitHub is the delivery spine

- **Azure DevOps Boards** = planning/governance spine
- **GitHub** = code truth (transitional until intentional Azure Repos cutover)
- **Azure Pipelines** = release truth
- **GitHub Actions** = transitional where still needed
- One Azure DevOps project: `ipai-platform`

## C9: Observability is mandatory

- Correlation IDs propagate across Odoo → Foundry → Document Intelligence
- Failures classified as auth/network/service/model/data errors
- Retry policy defined per failure class
- Foundry tracing + App Insights connected
- All agent and OCR activity is observable and auditable
- Silent partial writes are prevented

---

## Ownership Matrix

| Layer | System | Owns | Must NOT Own |
|---|---|---|---|
| **Identity** | Entra ID / Workload ID / Agent ID | Auth, access, agent governance | Business workflow state |
| **Platform foundation** | Azure Landing Zone (CAF) | Subscription structure, shared services, policy | Application-specific business logic |
| **Business core** | Odoo 18 | Transactions, approvals, posted records, trigger surface | LLM orchestration, knowledge retrieval |
| **AI runtime** | Foundry Agent Service | Agent hosting, tool execution, reasoning | Unrestricted DB writes, canonical business state |
| **Document processing** | Document Intelligence | OCR, extraction, classification | Business interpretation or approval decisions |
| **Knowledge** | Foundry tools + AI Search | Grounded retrieval, scoped tool access | Transactional state |
| **Delivery** | Azure DevOps + GitHub | Planning, code, release, governance | Runtime configuration authority |
| **Observability** | Monitor + App Insights + Foundry tracing | Traces, logs, evals, alerts | Business logic enforcement |

---

## Repo Ownership

| Repo | Owns |
|---|---|
| `odoo` | Runtime, addons, action hooks, widget, job/audit models |
| `agent-platform` | Foundry agents, hosted runtime, tools, evals |
| `platform` | Normalized AI/OCR contracts, control-plane, admin services |
| `infra` | Landing zone, Front Door, ACA, PostgreSQL, Key Vault, networking |
| `data-intelligence` | Lakehouse, BI, training/eval datasets |
| `agents` | Shared prompts, skills, registries |
| `automations` | Schedulers, jobs, runbooks |
| `web` | Public/product web surfaces |
| `design` | Tokens, components, brand |
| `docs` | Cross-platform architecture/governance |
| `templates` | Scaffolds only |

---

## C10: Close Control Plane Doctrine

Odoo Copilot includes a distinct close-control administrative plane that governs setup, access, connectivity, monitoring, and lifecycle management for regulated finance workflows.

### Administrative planes
1. **Bootstrap & Landscape**
   - define source systems, entities, calendars, jurisdictions, ledgers, and scenario enablement
   - validate prerequisites before scenarios/runs are allowed to execute

2. **Security & Access**
   - define role-bound access for design, operations, approval, audit, and admin functions
   - separate read/review permissions from state-changing remediation permissions

3. **Connectivity & Integration**
   - register and monitor connected systems, adapters, and sync health
   - define read/write scope, auth requirements, evidence returned, and failure semantics per adapter

4. **Monitoring & Reliability**
   - monitor runs, connector health, sync failures, degraded mode, and business logs
   - preserve operator visibility when dependencies fail

5. **Lifecycle & Retention**
   - govern archive, restore, retention, anonymization, export, purge, and offboarding
   - require explicit administrative workflow for destructive actions

### Governance rules
- Administrative-plane capabilities are part of Odoo Copilot, not separate products.
- All remediation outcomes must resolve back to Odoo records/workflows.
- Findings, runs, tasks, evidence packs, and exports must remain accessible to authorized admins/auditors across their lifecycle.
- Connector failure must degrade gracefully: findings stay visible, blocked actions are explicit, retries/escalations are logged.

## C11: Payment Execution Guardrail Doctrine

Odoo Copilot may assist with payment-adjacent workflows when payment configuration already exists in Odoo or an approved connected payment system.

### Allowed posture
- Odoo Copilot may prepare payment proposals, payment batches, remittance drafts, payment recommendations, and payment-status explanations.
- Odoo Copilot may trigger payment actions only when:
  - the payment journal/provider/bank flow is already configured,
  - the acting user has the required role/authority,
  - the action is within a governed workflow,
  - and a human explicitly confirms the final state-changing action.

### Human-in-the-loop rule
- Final payment execution must remain human-approved.
- Copilot may never treat payment execution as a silent background automation for finance-critical disbursements.
- Payment initiation, release, posting, and submission actions must generate auditable logs and evidence.

### Product boundary
- Odoo Copilot is allowed to automate the preparation and orchestration of payments.
- Odoo Copilot is not allowed to imply that external filing/submission/payment rails exist when they are not configured.
- Capability responses must distinguish between:
  1. what Odoo can do now,
  2. what can be done if payment is configured,
  3. what still requires a human approval or external authority action.

## C12: Sandboxed Artifact Workspace Doctrine

Odoo Copilot includes a sandboxed workspace for direct artifact generation, transformation, and review.

### Purpose
The sandboxed workspace allows Odoo Copilot to:
- generate spreadsheets, CSVs, PDFs, DOCX, PPTX, JSON, XML, working papers, reconciliation packs, tax templates, and evidence bundles
- transform scoped business data into exportable artifacts
- stage intermediate analysis without mutating production records
- prepare publish-ready outputs for human review

### Isolation rules
- Workspace execution is sandboxed and isolated from direct production mutation.
- The workspace may read scoped/copied context from Odoo and approved connected systems.
- Generated artifacts are draft outputs until explicitly approved for export, publish, or writeback.
- File creation, transformation, and analysis must be audit-logged.

### Human-in-the-loop rules
- Artifact generation may be automatic.
- Artifact publication, import, posting, submission, or writeback to Odoo must remain explicitly user-confirmed when state changes or regulated outputs are involved.
- Copilot must clearly distinguish:
  1. generated in sandbox,
  2. ready for review,
  3. approved for export/publish,
  4. approved for Odoo writeback.

### Product boundary
- The sandboxed workspace is part of Odoo Copilot, not a separate office/productivity suite.
- Odoo remains the transactional authority.
- The workspace is for preparation, analysis, and artifact production; final operational state changes still resolve through governed Odoo workflows.

## C15: User Attachment Ingestion Doctrine

Odoo Copilot must allow users to attach files directly in the copilot interface and have those files analyzed within governed context.

### Supported posture
- Users may attach one or more files to a copilot interaction.
- Odoo Copilot may classify, extract, summarize, compare, validate, and transform attached files inside the sandboxed workspace.
- Attached files may be used to:
  - answer contextual questions,
  - generate artifacts,
  - create findings/exceptions,
  - populate drafts,
  - attach evidence to runs/tasks/records,
  - or prepare governed writeback proposals.

### Isolation and safety
- File analysis occurs in the sandboxed workspace, not as an implicit production mutation.
- Attachments are treated as scoped evidence inputs until explicitly attached to an Odoo record, promoted to an evidence pack, or approved for writeback.
- Unsupported, unreadable, or low-confidence files must produce explicit status and fallback behavior.

### Human-in-the-loop rules
- File analysis may be automatic.
- Any resulting state change in Odoo must remain explicitly confirmed if it creates, updates, posts, approves, submits, or deletes business records.
- Copilot must distinguish:
  1. file received,
  2. file analyzed,
  3. draft output prepared,
  4. writeback/attachment/export awaiting approval.

## C16: Artifact Preview & Review Doctrine

Odoo Copilot must provide first-class preview and review capabilities for all generated artifacts before export, publish, attachment, or writeback.

### Required preview posture
- Every generated artifact must be previewable inside Odoo Copilot before downstream action.
- Preview must support both human-readable and structure-aware inspection where applicable.
- Artifact preview is part of the sandboxed workspace lifecycle and does not itself mutate production records.

### Minimum review capabilities
- open/view generated artifact
- inspect metadata (type, source context, generation time, skill, status)
- compare current artifact against source inputs or prior versions
- highlight low-confidence sections, inferred values, and unresolved fields
- approve for export, approve for attachment, request regeneration, or request writeback

### Governance rules
- Preview is mandatory for regulated, finance-critical, or state-changing outputs.
- If preview cannot be rendered inline, Odoo Copilot must provide a safe fallback (downloadable draft, alternate format, or structured summary).
- Approval decisions taken from preview must be audit-logged with artifact version and acting user.

## C17: External Prompt-Pack Alignment Doctrine

Odoo Copilot may adopt external prompt-pack patterns as internal skill packs when they align with governed business workflows.

### Product skill pack
Odoo Copilot includes a product-oriented skill pack for:
- competitive and market research
- roadmap prioritization
- monetization and vision framing
- PRD and release-content generation
- FAQ/value-proposition/pitch-deck generation
- user journey and design artifact support

### Finance skill pack
Odoo Copilot includes a finance-oriented skill pack for:
- financial benchmarking and market analysis
- budget/forecast/scenario planning
- executive/board/QBR reporting
- audit finding summarization
- variance translation
- operational finance and process-improvement analysis

### Governance rules
- External prompt-pack ideas must map to concrete registered Odoo Copilot skills.
- No prompt-pack pattern may bypass existing sandbox, payment, execution-mode, or writeback guardrails.
- Product and finance prompt-pack capabilities are internal Odoo Copilot skill packs, not separate end-user products.

## C18: Databricks Handoff Doctrine

Odoo Copilot may hand off users from Odoo into Databricks when a task is better served by analytics, dashboards, Genie, notebooks, or Databricks-hosted copilot apps.

### Product posture
- Databricks remains an analytics/application surface.
- Odoo remains the transactional authority.
- Odoo Copilot may launch users into an approved Databricks destination with scoped context from the active Odoo screen, record, scenario, or portfolio object.

### Allowed handoff targets
- Databricks app
- dashboard
- Genie / ask surface
- notebook / query workspace
- project-specific workspace folder

### Governance rules
- Handoff must be explicit and user-visible.
- Context passed to Databricks must be scoped and auditable.
- Handoff does not imply writeback authority.
- Any writeback from Databricks back into Odoo must go through governed APIs and explicit approval where required.

### UX rule
The handoff should appear as a first-class action/toggle inside Odoo Copilot and, where useful, on relevant record views.

## C13: Skill Realization Doctrine

Odoo Copilot capability claims must resolve to concrete registered skills.

### Rules
- UI capability lists must reflect actual skill availability, not aspirational prose.
- Each major capability area must have:
  - a stable skill identifier,
  - defined inputs,
  - defined outputs/artifacts,
  - permission requirements,
  - configuration prerequisites,
  - and audit/logging behavior.
- Skills that generate artifacts may run automatically in the sandbox.
- Skills that mutate Odoo state, release payments, submit regulated outputs, or change approvals must remain explicitly human-approved and role-gated.

## C14: Execution Mode & Supervised Autonomy Doctrine

Odoo Copilot exposes explicit execution modes so users can control whether Copilot explains, prepares, asks, or acts.

### Supported execution modes
1. **Explain Only**
   - Copilot answers, analyzes, and recommends
   - no artifact generation, no writeback, no external action

2. **Prepare Only**
   - Copilot may generate artifacts, drafts, proposals, and staged outputs in the sandbox
   - no state-changing execution

3. **Ask Before Acting** *(default)*
   - Copilot may prepare the next action and request confirmation before any state change
   - this is the default mode for production use

4. **Act Within Guardrails**
   - Copilot may execute pre-approved low-risk actions without prompting each time
   - only allowed for actions explicitly classified as low-risk, role-permitted, and policy-safe
   - all actions must be logged and reversible where applicable

### Hard guardrails
- Final payment execution remains human-approved.
- Regulated filings/submissions remain human-approved.
- Journal posting, approval-state changes, destructive actions, purge/offboarding, and external disbursement actions must not run in silent autonomy mode.
- "Act without asking" is never global; it is always scoped by action class, environment, role, and policy.

### Product requirement
The UI must clearly show the current execution mode and the risk posture of that mode.

---

## Canonical Statement

> InsightPulseAI Odoo on Azure is an Entra-governed, CAF-aligned landing-zone workload:
> Odoo in application landing zones, Foundry and Document Intelligence as bounded AI
> services inside those workloads, scoped tools between Odoo and Foundry, approval gates
> for high-risk writes, and Azure DevOps/GitHub as the delivery spine.
