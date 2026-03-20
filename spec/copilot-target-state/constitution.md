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

- Odoo 19 owns accounting, CRM, projects, expenses, approvals, documents, posted business records
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
| **Business core** | Odoo 19 | Transactions, approvals, posted records, trigger surface | LLM orchestration, knowledge retrieval |
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

## Canonical Statement

> InsightPulseAI Odoo on Azure is an Entra-governed, CAF-aligned landing-zone workload:
> Odoo in application landing zones, Foundry and Document Intelligence as bounded AI
> services inside those workloads, scoped tools between Odoo and Foundry, approval gates
> for high-risk writes, and Azure DevOps/GitHub as the delivery spine.
