# Industry Reference Matrix — Odoo Industry Pages → IPAI Surfaces

> **Vertical packaging reference**, not canonical architecture. Maps Odoo's industry-vertical bundles to IPAI's 3 public surfaces.
>
> **Last updated:** 2026-04-14
> **Authority:** This file. Implementation truth still lives in OCA composition + `addons/ipai/` thin adapters per `CLAUDE.md` and `feedback_odoo_module_selection_doctrine.md`.

## Doctrine

Odoo industry pages are **marketing bundles**, not CE/OCA implementation contracts. Use them to:
- Define **business workflows** per vertical
- Identify what packaged experience customers expect
- Set scope boundaries per public surface

Then implement via `odoo/odoo` + selected OCA modules (per `feedback_odoo_module_selection_doctrine.md`). Only add `ipai_*` where CE+OCA composition still leaves a gap.

**Hard rule:** These 4 industry pages do NOT imply 4 separate platform builds. They imply **3 business surfaces + 1 adjacent overlay** on **one shared platform**.

---

## Mapping summary

| IPAI Surface | Primary Odoo industry reference | Adjacent overlay |
|---|---|---|
| **InsightPulseAI** (`insightpulseai.com`) | Odoo Partner | Marketing Agency |
| **PrismaLab** (`prismalab.insightpulseai.com`) | Accounting Firm (as operating model, NOT domain) | — |
| **W9 Studio** (`w9studio.net`) | Photography (1:1 match) | — |

---

## A. InsightPulseAI ← Odoo Partner + Marketing Agency overlay

**Why Odoo Partner is primary:** packaged professional-services/implementation business stack — service packages, quote calculator, quote templates, automatic project + task creation after sale, project control, timesheets, documents, invoicing.

**Why Marketing Agency is overlay:** brand/site + lead-gen + campaign/project layer — website builder, appointments, CRM, projects, timesheets, invoices, marketing tools, price lists, recurring invoices.

**Use this for:** IPAI's public site, lead capture, proposal-to-project flow, implementation delivery, partner/service packaging.

### Packaged app bundle for InsightPulseAI

```
Base modules (CE + OCA composition):
- CRM                        (CE crm + OCA crm)
- Sales / quoting            (CE sale_management + OCA sale-workflow)
- Project                    (CE project + OCA project + project-reporting)
- Timesheets                 (CE hr_timesheet + sale_timesheet + OCA timesheet)
- Invoicing / accounting     (CE account + OCA account-financial-tools/reporting)
- Website                    (CE website)
- Calendar / appointments    (CE calendar + OCA calendar)
- Marketing automation       (CE marketing_automation, lightweight)
- Knowledge / docs workspace (CE knowledge / OCA knowledge)
- Pulser assistant layer     (agents/ + agent-platform/)
```

Cross-reference: `ssot/apps/desired-end-state-matrix.yaml` app-insightpulseai.

---

## B. PrismaLab ← Accounting Firm (operating model, not domain)

**Important:** PrismaLab is NOT an accounting firm. The Accounting Firm Odoo bundle just happens to match the **operating model** PrismaLab needs:
- lead → quote → project → time tracking → document workspace → invoice
- strong document/e-sign workflow
- time-and-materials / fixed-rate / milestone billing
- project dashboard + client service delivery tracking

**Use this for:** PrismaLab consulting/project delivery structure, document-heavy service execution, client-facing delivery workflow.

**DO NOT** treat this mapping as a signal to build tax-practice or accounting-specific scope unless PrismaLab actually moves there.

### Packaged app bundle for PrismaLab

```
Base modules (CE + OCA composition):
- CRM                        (CE crm + OCA crm)
- Sales / proposals          (CE sale_management + OCA sale-workflow)
- Project                    (CE project + OCA project + project-reporting)
- Timesheets                 (CE hr_timesheet + OCA timesheet)
- Invoicing / accounting     (CE account + OCA account-financial-tools)
- Documents / file workspace (CE documents + OCA knowledge)
- e-sign workflow            (CE sign — verify CE vs Enterprise availability;
                              if EE-only, use OCA sign equivalent)
- Client portal              (CE portal + OCA portal extensions)
- Pulser assistant layer     (agents/ + agent-platform/ — RAG via prismalab-rag-v1)
```

Cross-reference: `ssot/apps/desired-end-state-matrix.yaml` app-prismalab + `prismalab_rag_corpus.md` memory.

---

## C. W9 Studio ← Photography (1:1 match)

**The clearest 1:1 match of any IPAI surface.** Odoo Photography page explicitly bundles:
- CRM lead capture from website/email
- Quote builder
- Online appointments
- Customer portal rescheduling
- Google/Outlook calendar sync
- Project creation after quote confirmation
- Online signatures
- Online payments
- Task management

**Use this for:** Studio inquiries, booking, scheduling, shoot/project management, deposits/payments, post-booking execution.

### Packaged app bundle for W9 Studio

```
Base modules (CE + OCA composition):
- CRM                        (CE crm + OCA crm)
- Website inquiry capture    (CE website + website_form)
- Appointments / bookings    (OCA calendar resource_booking — see booking adoption rows)
- Calendar sync              (CE calendar + Google/Outlook connectors)
- Sales / quotes             (CE sale_management + OCA sale-workflow
                              + sale_resource_booking)
- Deposits / payments        (CE payment + OCA payment connectors;
                              PayMongo + PayPal + Xendit per memory)
- Project / task management  (CE project + OCA project)
- Customer portal            (CE portal)
- Email follow-up            (CE mail.mail via Zoho SMTP per CLAUDE.md)
- Pulser assistant layer     (agents/teams-surface — already live booking assistant)
```

Cross-reference:
- `ssot/apps/desired-end-state-matrix.yaml` app-w9studio
- `ssot/governance/upstream-adoption-register.yaml` §H OCA booking stack
- `project_payment_provider_stack.md` memory (PayPal + Xendit native, PayMongo custom)
- `project_w9studio_concept.md` memory

---

## Vertical-page guardrails

| Industry page | Use as | Do NOT use as |
|---|---|---|
| Odoo Partner | InsightPulseAI services-business operating model | Signal to build a separate "Partner ERP" |
| Marketing Agency | InsightPulseAI website + campaign overlay | Reason to build full marketing-agency app |
| Accounting Firm | PrismaLab professional-services operating model | Signal that PrismaLab is becoming an accounting firm |
| Photography | W9 Studio booking/studio app | Justification for new photo-vertical addons |

---

## Shared platform underneath (single shared substrate)

All 3 surfaces sit on **one shared platform**:

| Plane | Implementation |
|---|---|
| Transaction | Odoo CE + selected OCA + thin `ipai_*` adapters (one DB per `docs/tenants/TENANCY_MODEL.md` — multi-company per tenant) |
| Data intelligence | Databricks + Fabric |
| Agent | Foundry + Agent Framework + Pulser tools |
| Delivery | GitHub-first SDLC |

Plus **shared MCP layer** (5–7 MCPs per `ssot/apps/desired-end-state-matrix.yaml`):
- content + crm + scheduling + odoo_erp + knowledge (P0)
- documents + email (P1)
- analytics + payments (P2)

---

## What this changes operationally

1. **InsightPulseAI** gets a clear marketing/agency overlay messaging — adjacent to Partner/services positioning.
2. **PrismaLab** uses the Accounting Firm operating-model template **without** scope creep into accounting verticals.
3. **W9 Studio** has a 1:1 reference for end-to-end flow validation — easiest to scope and ship.
4. **No new platform builds.** Three surfaces, one platform.

---

## Anchors

- **Apps SSOT:** [`ssot/apps/desired-end-state-matrix.yaml`](../../ssot/apps/desired-end-state-matrix.yaml)
- **Upstream register:** [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml)
- **Repo adoption:** [`docs/architecture/repo-adoption-register.md`](repo-adoption-register.md)
- **Desired end state matrix:** [`docs/architecture/desired-end-state-matrix.md`](desired-end-state-matrix.md)
- **Tenancy model:** [`docs/tenants/TENANCY_MODEL.md`](../tenants/TENANCY_MODEL.md)
- **Memory:**
  - `feedback_apps_and_mcp_architecture.md`
  - `feedback_odoo_module_selection_doctrine.md`
  - `project_w9studio_concept.md`
  - `project_payment_provider_stack.md`
  - `prismalab_rag_corpus.md`

## Changelog

- **2026-04-14** Initial vertical-packaging matrix. 3 surfaces × Odoo industry pages mapped. Booking stack adopted.
