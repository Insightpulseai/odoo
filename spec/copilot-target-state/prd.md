# Copilot Target-State — PRD

## Six-Plane Architecture

The complete InsightPulseAI Odoo on Azure stack is a six-plane system:

1. **Experience plane** — Odoo 19 web UI, Copilot widget, admin/ops surfaces. Public ingress via Azure Front Door → Azure Container Apps.
2. **Business systems plane** — Odoo 19 as business core (accounting, CRM, projects, expenses, approvals, documents). Odoo owns trigger surface: server actions, automation rules, scheduled actions, client actions.
3. **AI / agent runtime plane** — Azure AI Foundry Agent Service hosts bounded agents: Copilot, Document Triage, Finance Review, Compliance/Workflow.
4. **Document processing plane** — Azure Document Intelligence for OCR, layout, tables, key/value extraction, and custom extraction models. Pattern: Document Intelligence first, Foundry interpretation second.
5. **Knowledge / grounding plane** — Foundry agents use scoped tools and knowledge, not unrestricted DB access. Tools: `get_record_context`, `submit_ocr_job`, `write_review_result`, `create_activity`, `post_chatter_note`.
6. **Security / observability plane** — Managed identity, Key Vault, end-to-end tracing across Odoo jobs, Foundry agent runs, and OCR jobs.

## What Odoo Copilot Is

Odoo Copilot is the **Odoo-side interaction and orchestration layer**, not the Foundry agent itself:

- Systray/inline widget in Odoo
- Client actions for interactive prompts
- Server actions / automation rules for background workflows
- Odoo-side job and audit models
- Bounded service clients for Foundry and Document Intelligence
- Approval UI for high-risk outputs

## Request Flows

### A. Interactive Copilot

User opens a record → clicks Ask Copilot → Odoo packages context + correlation ID → Foundry Copilot agent → response written to widget + chatter/audit.

### B. OCR / Intake

User uploads document → Odoo fires automation rule → Document Intelligence OCR/extraction → Foundry agent classifies/interprets normalized payload → Odoo stores reviewable proposal (not auto-posted).

### C. Background Workflow

Record state change / approval step / scheduled check → Odoo cron/automation → Foundry or OCR job (async) → status transitions: `queued` → `running` → `done` / `failed` / `needs_review`.

## Minimum Azure Resource Set

- Azure Front Door (external ingress)
- Azure Container Apps (Odoo + app services)
- Azure Database for PostgreSQL Flexible Server (Odoo DB)
- Redis-compatible cache (async coordination)
- Key Vault (secrets, endpoint refs)
- Azure AI Foundry project + Agent Service (hosted/prompt agents)
- Azure Document Intelligence (OCR/extraction)
- Azure AI Search (optional, grounding layer)
- Azure Monitor / App Insights (observability)

## Required Odoo Modules

### `ipai_odoo_copilot`

Widget, interactive prompt entry points, client/server actions, Foundry request packaging, user-visible responses.

### `ipai_document_intelligence_bridge`

OCR job submission, polling/callback, extraction normalization, attachment/document writeback.

### `ipai_copilot_actions`

Reusable action definitions, AI job models, audit logging, approval routing, model-specific automation hooks.

## Required Foundry Agent Set

| Agent | Role |
|-------|------|
| Copilot Agent | Interactive Q&A, summaries, recommendations |
| Document Triage Agent | Classify attachments, route to correct OCR/workflow path |
| Finance Review Agent | Interpret OCR output for receipts/bills, produce reviewable proposals |
| Compliance/Workflow Agent | Detect missing fields, approvals, routing errors, exceptions |

## Document Intelligence Model Mix

| Lane | Purpose |
|------|---------|
| Read OCR | Generic text extraction |
| Layout/table extraction | Structured documents |
| Prebuilt extraction | Common document patterns |
| Custom extraction | PH/BIR/vendor-specific forms and templates |

## Governance Rules

- Odoo stays the transactional system of record
- Foundry agents use scoped tools, not unrestricted DB access
- OCR results and agent outputs stored with correlation IDs and model/agent metadata
- Financial and compliance-affecting actions are proposal-first and approval-gated
- OCR and agent flows are asynchronous with retry and failure states
- All agent and OCR activity is observable and auditable

## Repo Ownership

| Repo | Owns |
|------|------|
| `odoo` | Runtime, addons, action hooks, UI widget, Odoo job/audit models |
| `agent-platform` | Foundry agent definitions, hosted agent runtime, evals, tool contracts |
| `platform` | Normalized OCR/AI contracts, orchestration metadata, shared control-plane |
| `infra` | Front Door, Container Apps, PostgreSQL, Key Vault, identity, networking, observability |
| `data-intelligence` | Only if document/AI flows feed lakehouse, BI, or training/eval datasets |

## Definition of Complete

- Odoo has working Copilot UI actions on target models
- Odoo automation rules trigger OCR/agent jobs on document and workflow events
- Foundry hosted/prompt agents are deployed and reachable
- Document Intelligence extracts text/fields/tables from uploaded attachments
- Normalized extraction output written back into Odoo review models
- High-risk writes require human approval
- Secrets/identity wired securely
- Traces, logs, and evaluations exist for both OCR and agent flows
- Repo ownership split is explicit and stable

## Administrative Planes

To support enterprise-grade close and tax operations, Odoo Copilot includes five internal administrative planes.

### 1. Bootstrap & Landscape
Purpose:
- register entities, calendars, ledgers, jurisdictions, and source systems
- seed and enable scenarios/playbooks
- validate readiness before live execution

Proposed surfaces:
- System Landscape
- Bootstrap Status
- Scenario Enablement

### 2. Security & Access
Purpose:
- manage close/control roles
- assign authorization groups
- enforce separation between inquiry, review, approval, and admin actions

Proposed surfaces:
- Manage Roles
- Manage Role Assignments
- Authorization Groups

### 3. Connectivity & Integration
Purpose:
- register adapters and connected systems
- monitor synchronization and job handoff
- expose external dependency state to operators

Proposed surfaces:
- Connected Systems
- Sync Status
- External Job Results
- Adapter Registry

### 4. Monitoring & Reliability
Purpose:
- monitor run execution, connector health, and degraded mode
- capture retryable vs terminal failures
- support operator troubleshooting without losing context

Proposed surfaces:
- Run Monitor
- Connector Health
- Sync Failures
- Business Logs
- Degraded Mode Alerts

### 5. Lifecycle & Retention
Purpose:
- archive and restore close artifacts
- generate auditor-ready exports
- manage retention, anonymization, purge, and offboarding

Proposed surfaces:
- Evidence Export Center
- Archive / Restore Console
- Retention Policy Console
- Offboarding Checklist

### Product requirement
These administrative planes must be internal Odoo Copilot capabilities. They must not create separate user-facing products or bypass Odoo as the action authority.

## Databricks Launch / Handoff UI

Odoo Copilot supports a contextual handoff from Odoo into Databricks.

### Primary UX
A user can trigger a contextual Databricks launch from Odoo using:
- an **Open in Databricks** button/action
- an optional **Databricks mode** toggle in Odoo Copilot
- record-level smart actions where analytics context exists

### Supported launch contexts
- active portfolio / program / project
- active close scenario / run / finding
- active vendor bill / AP review set
- active dashboard / report pack
- active attachment/artifact preview context

### Supported Databricks destinations
- `ipai-finance-copilot` app
- finance PPM dashboard
- Genie space
- notebook/query surface
- mapped workspace folder for the current business object

### Context payload
Odoo should pass a governed context pack such as:
- user identity / role
- company/entity
- source model
- source record id / external key
- scenario / run / project / program identifiers
- date range / fiscal period
- selected filters
- artifact or attachment references where permitted

### Product requirement
The launch must land the user in the most relevant Databricks destination, not a generic workspace home, whenever a mapping exists.

## Launch Modes

### 1. Direct launch
A button or smart action opens the mapped Databricks destination in a new tab/window.

Best for:
- dashboards
- Genie
- app landing pages
- project/program portfolio analysis

### 2. Copilot toggle
A toggle inside Odoo Copilot switches the current conversation into "Databricks-backed analysis mode" while keeping the user in Odoo until launch is needed.

Best for:
- "analyze this portfolio in Databricks"
- "open the dashboard behind this answer"
- "take me to the finance copilot app"

### 3. Embedded preview card
Odoo Copilot shows a Databricks destination card with:
- destination name
- why it is relevant
- open action
- optional last refresh / health metadata

Best for:
- guided handoff
- explainable routing
- multiple possible destinations

## Close Operations Roles

Recommended role families:
- `copilot_close_admin`
- `copilot_close_designer`
- `copilot_close_operator`
- `copilot_close_approver`
- `copilot_close_auditor`
- `copilot_close_viewer`

Role visibility must govern:
- which scenarios/checks can be defined
- who can execute or rerun scenarios
- who can view findings/evidence
- who can approve, suppress, close, or purge
- who can perform export/archive/offboarding actions

## Payment-Enabled Skills

Odoo Copilot supports payment-related workflows only where payment execution is already configured in Odoo or an approved connected system.

### Payment skill behaviors
- explain payment status and readiness
- prepare payment proposals
- assemble payment batches
- recommend payment timing and routing
- generate remittance or support documents
- surface blockers (missing approval, missing bank details, policy hold, missing vendor/payment configuration)
- request explicit human approval before execution
- record execution outcome and evidence after confirmation

### Guardrails
- no implied payment capability without underlying configuration
- no silent auto-disbursement
- no bypass of maker/checker or approval-chain controls
- no generic chat-only answer when a structured payment proposal or blocker object should exist

### Required UX distinction
Every payment-related response must clearly separate:
- **Configured and executable now**
- **Configurable but not currently enabled**
- **Human approval required before execution**

## Sandboxed Workspace & Artifact Generation

Odoo Copilot includes a sandboxed workspace where users can generate operational artifacts directly from governed business context.

### Supported artifact classes
- spreadsheets and CSV exports
- BIR/tax working papers and template-ready schedules
- reconciliation workbooks
- payment support packs and remittance files
- evidence packs
- executive summaries and DOCX/PDF reports
- slide decks and presentation artifacts
- machine-readable JSON/XML outputs for downstream submission or integration

### Workspace model
1. User invokes a workspace-capable skill
2. Odoo Copilot assembles a scoped context pack
3. Copilot generates one or more artifacts inside the sandbox
4. User reviews the generated outputs
5. User may export, publish, attach, or request governed writeback
6. Any Odoo mutation or regulated submission path requires explicit confirmation

### Required UX surfaces
- Workspace
- Artifact Shelf
- Preview / Compare
- Export / Publish
- Attach to Record
- Request Writeback

### Product requirement
When the user intent is to produce a concrete deliverable, Odoo Copilot must be able to generate the artifact directly in the sandbox rather than responding only with narrative instructions.

## Attachment Intake & Analysis

Odoo Copilot supports direct user file attachment and in-sandbox analysis.

### Supported attachment classes
- PDF
- images
- spreadsheets
- slides
- DOCX / text documents
- CSV / JSON / XML
- email-style exports and supporting files
- multi-file evidence bundles

### Core behaviors
1. User attaches file(s) in the copilot UI
2. Odoo Copilot stores them in a scoped workspace session
3. Copilot classifies file type and intent
4. Copilot analyzes the file(s) using the appropriate skill path
5. Copilot returns:
   - summary,
   - extracted fields,
   - comparison results,
   - findings/exceptions,
   - generated artifacts,
   - or a governed writeback proposal

### Example outcomes
- analyze a vendor invoice PDF and propose a draft vendor bill
- inspect a tax workbook and identify missing columns or filing gaps
- compare two statements and generate a reconciliation worksheet
- read a closing checklist spreadsheet and create findings/tasks
- summarize an uploaded policy document and map it to approval rules
- package uploaded evidence into an audit-ready bundle

### Product requirement
If a user attaches a file, Odoo Copilot must treat the file as a first-class input to the workflow rather than forcing the user to manually restate its contents.

## Artifact Preview

Odoo Copilot must provide inline preview and review for generated artifacts inside the sandboxed workspace.

### Preview objectives
- let users verify generated outputs without leaving Odoo Copilot
- reduce blind export/download workflows
- support governed approval before attachment, export, publish, or writeback

### Supported preview modes
- **Rendered preview**: PDF, DOCX-derived view, slides, formatted reports
- **Tabular preview**: spreadsheets, CSV, schedules, working papers
- **Structured preview**: JSON, XML, extracted fields, mappings
- **Diff/compare preview**: regenerated artifact vs previous version, or artifact vs source data
- **Evidence preview**: bundled attachments, filing packs, reconciliation packs

### Required preview actions
- open preview
- inspect source context
- view warnings / low-confidence fields
- compare versions
- approve for export
- approve for attachment to record
- request regeneration
- request writeback
- reject / discard draft

### Product requirement
When Odoo Copilot generates an artifact, the default next step must be preview-and-review, not immediate download-only behavior.

## OpenAI Academy Skill-Pack Mapping

Odoo Copilot incorporates two structured skill packs derived from external prompt-pack patterns: Product and Finance.

### Product skill pack

| Capability Area | Odoo Copilot Skill | Primary Inputs | Primary Action Targets |
|---|---|---|---|
| Competitive research | `product_competitive_research` | competitors, market URLs, notes, screenshots, user prompt | comparison tables, research summaries, recommendation artifacts |
| Roadmap prioritization | `product_roadmap_prioritization` | initiative list, impact/effort scores, strategic notes | ranked roadmap, rationale memo, planning artifact |
| Product strategy | `product_strategy_pack` | product context, audience, goals, pricing details | monetization options, vision statements, feature ideas |
| PRD generation | `product_prd_builder` | feature/problem context, customer need, constraints | draft PRD, acceptance criteria, success metrics |
| Launch content | `product_launch_content` | release notes, launch details, stakeholder questions | changelog, FAQ, value prop, pitch/deck outline |
| UX/design support | `product_design_artifacts` | persona, flow, UI intent, screenshots | user journeys, wireframes, comparison visuals |

### Finance skill pack

| Capability Area | Odoo Copilot Skill | Primary Inputs | Primary Action Targets |
|---|---|---|---|
| Financial benchmarking | `finance_benchmarking` | company metrics, peer set, public sources | benchmark tables, commentary, source-backed summaries |
| Forecasting & planning | `finance_forecasting` | historical financial data, assumptions, scenarios | forecast tables, assumptions packs, executive summary |
| Cash-flow/scenario modeling | `finance_scenario_modeling` | planning inputs, cash assumptions, operating cases | scenario comparisons, risk commentary, planning workbook |
| Board/QBR reporting | `finance_exec_reporting` | P&L summaries, board data, QBR inputs | talking points, slide content, investor/update drafts |
| Audit & variance translation | `finance_audit_translation` | audit findings, variance analyses, support docs | exec summaries, manager-friendly explanations, next-step memo |
| Process improvement | `finance_process_improvement` | budget reports, cost center data, ops metrics | savings tables, efficiency opportunities, risk notes |

### Product requirement
These skill packs must be callable from the same unified Odoo Copilot surface and must honor:
- skill registry truth
- sandboxed artifact generation
- artifact preview/review
- attachment intake and file analysis
- execution-mode guardrails
- human approval for high-risk actions

## Prompt-Pack Demo Catalog

The seeded demo workspace should support at least these representative prompts.

### Product
- Compare 3 competitors' onboarding UX for the current workflow
- Prioritize the current roadmap using impact, effort, and strategic alignment
- Draft a PRD for a new Odoo Copilot capability
- Create release notes and a go-to-market FAQ for a feature launch
- Generate a user journey for the month-end close manager

### Finance
- Benchmark portfolio/program financial performance against peers or targets
- Forecast next-quarter spend/revenue/cash trend from uploaded data
- Draft board talking points from current program and finance status
- Translate current variance analysis into manager-friendly language
- Summarize audit findings and recommend next steps
- Identify cost-reduction opportunities from the seeded budget report

## Skill Registry Expectations

Capabilities described in the Odoo Copilot UI must map to registered internal skills rather than static narrative text.

At minimum, the following user-visible capability areas must resolve to concrete skills:
- direct artifact generation
- report building
- export operations
- pivot/analysis generation
- BIR template preparation
- recurring export automation
- payment orchestration
- attachment/evidence pack assembly

No capability should be presented as available unless:
1. the underlying data source is available,
2. required configuration exists,
3. required role permissions are satisfied,
4. and any state-changing action is gated by explicit human approval where required.

## Execution Modes

Odoo Copilot supports explicit execution modes so users can choose how much operational autonomy to grant.

### Mode definitions

| Mode | What Copilot may do | What Copilot may not do |
|---|---|---|
| Explain Only | answer, analyze, summarize, recommend | generate artifacts, mutate Odoo, call external execution paths |
| Prepare Only | generate artifacts, drafts, proposals, sandbox outputs | mutate Odoo, release payments, change approvals |
| Ask Before Acting | prepare and execute after explicit confirmation | silently execute state-changing actions |
| Act Within Guardrails | run pre-approved low-risk actions automatically | perform high-risk, regulated, destructive, or finance-critical execution without confirmation |

### Low-risk action examples
- generate recurring exports
- assemble attachment packs
- refresh sandbox artifacts
- create non-posted drafts
- run read-only checks/scenarios
- schedule approved recurring non-destructive jobs

### High-risk action examples
- payment execution or release
- journal posting
- approval/rejection state changes
- tax/regulatory submission
- purge/archive destruction
- writeback that changes financial state

### UX requirement
Users must be able to see:
- current mode
- why an action is blocked or confirmation-gated
- which skills honor sandbox autonomy only
- which skills require human approval regardless of mode

## Expanded Capability Matrix

| Capability Area | Odoo Copilot Skill | Primary Inputs | Primary Action Targets |
|---|---|---|---|
| Artifact workspace | `artifact_workspace` | scoped Odoo context, documents, tables, scenario outputs, user instructions | XLSX, CSV, PDF, DOCX, PPTX, JSON, XML, evidence packs |
| Payment orchestration | `payment_ops` | vendor bills, due items, payment journals, bank/payment config, approval state | payment proposal, payment batch, remittance, execution request |
| Report generation | `report_builder` | accounting records, tax records, saved views, filters | report draft, export pack, workbook, PDF summary |
| Export operations | `export_ops` | list views, report outputs, filing schedules, selected records | CSV/XLSX export, attachment pack, scheduled export request |
| Pivot & analysis | `pivot_analytics` | grouped accounting data, report tables, saved measures | pivot views, summarized tables, analysis workbook |
| BIR template generation | `bir_template_builder` | tax mappings, filing forms, period data, report outputs | BIR-ready templates, working papers, schedule drafts |
| Recurring automation | `recurring_export_automation` | export definitions, schedules, recipients, artifact templates | scheduled export jobs, recurring packs, reminders |
| Attachment packager | `attachment_packager` | reports, invoices, evidence docs, schedules | filing pack, payment support pack, reconciliation pack |
| Execution control | `execution_mode_control` | user role, environment policy, action classification, skill policy | mode selection, confirmation gating, autonomy scope, risk banner |
| Attachment intake | `attachment_intake` | user-uploaded files, chat context, active Odoo context | file classification, sandbox storage, evidence linkage, downstream skill routing |
| File analysis | `file_analysis` | PDFs, images, spreadsheets, docs, bundles | extraction, summary, comparison, findings, artifact generation, writeback proposal |
| Artifact preview | `artifact_preview` | generated artifacts, source context, prior versions, confidence/warning metadata | inline preview, compare/diff, approval decision, regenerate request, writeback request |
| Databricks handoff | `databricks_handoff` | active Odoo context, mapped destination, user role, launch policy | Databricks app/dashboard/Genie/notebook launch with scoped context |

## Non-Goals

- forcing users to manually recreate artifacts outside Odoo Copilot when the system can generate them directly
- allowing sandbox outputs to silently mutate production records without approval
- implying payment execution exists when journals/providers/workflows are not configured
- fully autonomous finance disbursement without explicit human approval
- a global unrestricted "act without asking" mode across all Odoo Copilot skills
- silent execution of finance-critical or regulated actions
- requiring users to manually restate uploaded file contents when the attachment can be analyzed directly
- silently mutating Odoo records immediately after file upload without explicit governed confirmation
- forcing users to download files just to inspect what Odoo Copilot generated
- bypassing preview for regulated or finance-critical generated outputs
- sending users to a generic Databricks home page when a mapped destination exists
- implying Databricks has direct transactional authority over Odoo records
- silent background writeback from Databricks into Odoo without governed APIs and approvals

## One-Sentence Target

> Odoo 19 on Azure Container Apps, PostgreSQL Flexible Server as the ERP database, Odoo actions as the trigger layer, Foundry Agent Service as the hosted AI runtime, Document Intelligence as the OCR/extraction layer, scoped tools/knowledge between Odoo and Foundry, and an approval/audit layer that keeps Odoo as the system of record.
