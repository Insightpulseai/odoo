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

## One-Sentence Target

> Odoo 19 on Azure Container Apps, PostgreSQL Flexible Server as the ERP database, Odoo actions as the trigger layer, Foundry Agent Service as the hosted AI runtime, Document Intelligence as the OCR/extraction layer, scoped tools/knowledge between Odoo and Foundry, and an approval/audit layer that keeps Odoo as the system of record.
