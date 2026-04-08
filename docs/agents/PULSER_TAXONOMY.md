# Pulser Taxonomy

## Purpose

This document defines the canonical taxonomy for **Pulser**, the product-facing assistant layer within the InsightPulseAI agent platform.

It standardizes how Pulser is classified across:
- deployment surface
- operational mode
- access posture
- capability profile
- naming and branding policy

It also defines the boundary between **Pulser** and the broader internal agent ecosystem.

---

## Scope

Pulser covers the **product-facing assistants** exposed to end users, operators, visitors, or domain users through approved product surfaces.

Pulser does **not** refer to every persona, skill, workflow, policy, or Foundry artifact in the repo. The wider agent platform includes internal/platform-facing personas, skills, workflows, policies, schemas, and gates that support delivery and governance but are not Pulser-branded.

---

## Canonical mental model

```text
InsightPulseAI Agent Platform
├── Pulser (product-facing assistant brand)
│   ├── ERP assistant surfaces
│   ├── public advisory surfaces
│   ├── consulting / RAG surfaces
│   ├── messaging add-on surfaces
│   └── domain modes (docs, tax, learning, goal synthesis)
│
├── Internal agent platform
│   ├── personas (59)
│   ├── skills (266)
│   ├── workflows (12)
│   └── deployment / governance artifacts
│
└── Governance and promotion layer
    ├── policies
    ├── gates (S01-S14)
    ├── schemas
    └── publish controls
```

---

## Taxonomy axes

Pulser assistants are classified along four primary axes:

1. **Deployment surface** — where the assistant is exposed and how it is hosted
2. **Operational mode** — what job the assistant is doing for the user
3. **Access posture** — what level of access and write authority the assistant has
4. **Capability profile** — which tools, retrieval lanes, and actions are enabled

---

## 1. Deployment surface classes

| Class | Public brand | Surface | Runtime | Model | Status |
|-------|-------------|---------|---------|-------|--------|
| Pulser ERP | Pulser for Odoo | Odoo web client (authenticated) | Azure AI Foundry agent | gpt-4.1 | Active design/build lane |
| Pulser Public | Ask Pulser | Public website / landing page widget | Docs-grounded assistant surface | gpt-4.1 | Active |
| Pulser PrismaLab | Pulser | PrismaLab site widget | Foundry + RAG (pgvector) | gpt-4.1 | Active |
| Pulser Gmail | InsightPulseAI for Gmail | Gmail sidebar / add-on | Google Apps Script → Odoo bridge | CRM-context workflow | Build lane |
| Pulser Outlook | InsightPulseAI for Outlook | Outlook add-in | TBD | TBD | Planned |
| Pulser M365 | Pulser for Microsoft 365 | Teams / Microsoft 365 Copilot surface | TBD | TBD | Deferred |

### Notes

- Prefer **Pulser for Odoo** on public-facing documentation instead of **Odoo Copilot**.
- Keep internal technical identifiers such as `ipai_odoo_copilot` if changing them would create migration cost with no user-facing benefit.

---

## 2. Operational modes

| Mode | Primary trigger | Workflow / config anchor | Outcome |
|------|----------------|------------------------|---------|
| ERP Operations | Direct user chat in Odoo | Foundry agent config (`agent_config.yaml`) | Search, analyze, and act on ERP data |
| Docs Assist | Odoo product / config / localization question | `odoo-docs-assist.yaml` | Runtime context → KB → bounded web answer |
| Tax Assist | Tax-related query | `odoo-tax-assist.yaml` | Tax guidance routed through tax-specific layers |
| Learning Plan | Skill or training request | `learning-plan-recommendation.yaml` | Suggested learning paths |
| Goal Synthesis | Goal / OKR progress query | `goal-status-synthesis.yaml` | Goal progress synthesis |
| Consulting RAG | Consulting / research visitor question | RAG pipeline (`rag-pipeline.ts`) | Grounded knowledge answer + CTA routing |
| Public Advisory | Public site visitor prompt | `AskPulser.tsx` | Documentation-grounded advisory only |

### Mode rule

A Pulser deployment surface may support more than one operational mode. Surface and mode are related but not the same classification axis.

---

## 3. Access posture classes

| Posture | Authentication | Authority | Typical scope |
|---------|---------------|-----------|---------------|
| Public | None / unauthenticated | Read-only advisory | Docs, KB, CTA routing, public explanations |
| Authenticated | Entra ID and/or approved local auth | Read and bounded write actions | Odoo records, CRM, invoices, tasks, inventory |
| Admin | Elevated privileged access | System-level and sensitive operations | Health checks, config-sensitive actions, bulk operations |

### Access rule

The same Pulser surface may expose different capabilities depending on access posture. For example, a public assistant may answer documentation questions while the authenticated ERP assistant may perform controlled operational actions.

---

## 4. Capability profile

### Core ERP / Foundry capability set

| Tool / function family | Purpose |
|----------------------|---------|
| `odoo_search_partners` | Search contacts and companies |
| `odoo_list_opportunities` | Inspect CRM pipeline |
| `odoo_search_sale_orders` | Search quotations and sales orders |
| `odoo_list_overdue_invoices` | Review overdue receivables |
| `odoo_list_project_tasks` | Inspect project tasks |
| `odoo_get_product_availability` | Check stock availability |
| `odoo_create_activity` | Create follow-up activity |
| `odoo_health_check` | Check system connectivity / health |
| `search_odoo_knowledge` | Search documentation and knowledge base |

### Capability tiers

| Tier | Description |
|------|-------------|
| Advisory | Explain, summarize, guide, retrieve grounded answers |
| Operational Read | Query live business records and operational context |
| Controlled Action | Create bounded follow-up actions after confirmation |
| Administrative | Health, configuration-adjacent, and privileged actions |

### Capability rule

Pulser should follow least privilege:
- enable only the tools required for the current surface and mode
- require explicit confirmation before mutating records
- keep destructive or bulk operations behind higher-trust postures

---

## 5. Branding and naming policy

### Public-facing naming

Use:
- **Pulser**
- **Ask Pulser**
- **Pulser for Odoo**
- **AI assistant** as a generic descriptor where needed

Avoid:
- **Odoo Copilot**
- **IPAI Copilot**
- **InsightPulse Copilot**
- any wording that implies **Copilot** is the owned product brand

### Internal technical naming

Allowed internally:
- `copilot_*`
- `ipai_odoo_copilot`
- other legacy technical identifiers already wired into code, data, or deployment artifacts

### API boundary rule

Public or external API surfaces should prefer `pulser_*` naming over `copilot_*` naming.

---

## 6. What is and is not Pulser

### Included in Pulser

- the ERP assistant surface
- the public Ask Pulser surface
- consulting / RAG Pulser surfaces
- messaging add-on assistant surfaces
- approved user-facing modes (docs, tax, learning, goal synthesis)

### Not included in Pulser

The following are part of the larger agent platform but are **not** Pulser:

- internal personas (59)
- internal skills (266)
- CI / platform workflows (12)
- Foundry policies, gates, schemas, and tooling
- platform governance artifacts
- non-user-facing factory or orchestration agents

### Boundary rule

Pulser is the **product face** of the agent platform. The broader platform is the **agent factory and governance system** behind it.

---

## 7. Microsoft Copilot agent alignment

| Our Agent | Microsoft Classification | Rationale |
|-----------|------------------------|-----------|
| Pulser ERP | Custom Engine Agent | Own orchestrator (Foundry), own model, own tools, external data (Odoo) |
| Pulser Public | Custom Engine Agent | External website, own hosting (ACA), own model |
| Pulser PrismaLab | Custom Engine Agent | External website, own RAG pipeline, own model |
| Pulser Gmail | N/A (Google ecosystem) | Separate ecosystem, not M365 |
| Pulser Outlook | Declarative Agent candidate | Could use Copilot's orchestrator for M365 context |
| Pulser M365 | Declarative Agent | Would use Copilot's infrastructure, deploy to Teams/Outlook |
| Docs Assist | Declarative Agent candidate | 3-lane retrieval fits declarative knowledge pattern |
| Tax Assist | Custom Engine Agent | Complex business logic, multi-layer routing |

---

## 8. Documentation usage rules

When documenting a Pulser assistant, always specify:

1. **Surface class**
2. **Operational mode**
3. **Access posture**
4. **Capability tier**
5. **Brand-safe public name**
6. **Owning runtime or workflow anchor**

### Example

- Surface class: Pulser ERP
- Mode: ERP Operations
- Access posture: Authenticated
- Capability tier: Controlled Action
- Public name: Pulser for Odoo
- Runtime anchor: Azure AI Foundry agent config

---

## 9. Canonical shorthand

```text
Pulser   = product-facing assistant brand
Mode     = job the assistant is doing
Surface  = where it lives
Posture  = what it is allowed to access/do
Capability = which tools/actions are enabled
```

---

## 10. Open follow-ups

The following should be clarified in adjacent docs, not in this taxonomy:

- promotion / graduation stage per Pulser variant → [PULSER_LIFECYCLE_AND_PROMOTION.md](./PULSER_LIFECYCLE_AND_PROMOTION.md)
- production readiness per surface
- exact model routing policy per environment
- final packaging path for Outlook and Microsoft 365 variants
- monetization / marketplace packaging strategy
