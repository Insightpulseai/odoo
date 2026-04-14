# Industry Reference Matrix

## Status
Proposed

## Purpose
Map Odoo industry-reference pages to IPAI's current portfolio so vertical packaging stays:
- business-workflow driven
- Odoo CE + OCA implementable
- aligned to the current benchmark scope:
  - D365 Finance
  - Finance agents
  - D365 Project Operations

This matrix is a **workflow and packaging reference**, not a direct module or architecture authority.

---

## Doctrine

1. Use Odoo industry pages to define **business packaging and workflow expectations**.
2. Use `odoo/odoo` + selected OCA repos/modules to decide actual implementation.
3. Do not create a separate product/app/repo just because Odoo has a separate industry page.
4. Prefer:
   - shared platform
   - shared MCP substrate
   - shared transactional core
   - distinct business surfaces only where the customer-facing motion truly differs

---

## Current portfolio map

| IPAI surface | Primary Odoo industry reference | Secondary / overlay references | Why |
|---|---|---|---|
| InsightPulseAI | Odoo Partner | Marketing Agency, Software Reseller | services-led implementation business, package selling, quote-to-project flow, partner-style delivery, productized offers, recurring/renewal-capable commercial model |
| PrismaLab | Accounting Firm | Odoo Partner | document-heavy consulting/project delivery, lead-to-quote-to-project-to-invoice, timesheets, secure document workspace, e-sign, service execution |
| W9 Studio | Photography | Marketing Agency | booking, appointment scheduling, quotes, calendar sync, project execution, payments, portal-driven client interaction |

---

## Industry reference details

### 1. Odoo Partner
**Best fit for:** InsightPulseAI core operating model

Odoo's Partner industry page emphasizes:
- pre-defined service packs
- quote calculator
- reusable quotation templates
- automatic project and task creation after a sale
- centralized implementation/project dashboard
- timesheets and analytic profitability tracking
- CRM pipeline and invoicing

**Packaging implication**
Use this as the base reference for:
- implementation packages
- discovery / success packs
- quote-to-project automation
- timesheet-backed service delivery
- partner/implementation operating model

---

### 2. Marketing Agency
**Best fit for:** InsightPulseAI website and campaign/service overlay; partial fit for W9 content/lead flow

Odoo's Marketing Agency page emphasizes:
- website builder and landing pages
- appointment booking
- lead capture from website/email/WhatsApp
- centralized campaign/project hub
- project + timesheets + exchanges + meetings + invoices
- price lists and recurring invoices
- integrated marketing apps

**Packaging implication**
Use this as an overlay for:
- site-led demand generation
- campaign/project delivery visibility
- lead-to-invoice workflow
- marketing-service packaging

**Do not treat as**
- a separate top-level platform
- a reason to add large marketing-automation custom code before core Finance/Project Ops scope is stable

---

### 3. Accounting Firm
**Best fit for:** PrismaLab operating model

Odoo's Accounting Firm page emphasizes:
- lead-to-quote-to-invoice flow
- project dashboards and automated task creation
- timesheets
- secure document workspace
- e-sign
- flexible billing by time/materials, fixed rate, or milestones
- strong accounting/reconciliation posture

**Packaging implication**
Use this as the reference for:
- consulting/project-delivery operations
- document-heavy client service
- milestone/time-based billing
- secure client file handling
- e-sign and compliance-oriented workflows

**Important note**
This is an **operating-pattern** reference for PrismaLab, not a signal to turn PrismaLab into an accounting-practice product.

---

### 4. Photography
**Best fit for:** W9 Studio

Odoo's Photography page emphasizes:
- online appointments
- client portal rescheduling
- Google / Outlook calendar sync
- quote builder and quote templates
- automatic project creation after quote confirmation
- online signature
- online payment
- task/project management

**Packaging implication**
Use this as the primary reference for:
- booking and appointment handling
- quote-to-shoot/project flow
- deposits/payments
- customer portal interactions
- schedule-driven studio operations

---

### 5. Software Reseller
**Best fit for:** InsightPulseAI commercial / packaging overlay, especially where resale, licenses, subscriptions, or recurring service packages matter

Odoo's Software Reseller page emphasizes:
- full license lifecycle management from purchase to renewal
- automatic purchase-order creation when buying a license
- tracking license keys, users, developers, software versions, database size, CPU count, and renewal status
- centralized implementation/project dashboards
- recurring invoicing for licenses
- service billing via timesheets, milestones, or fixed rates
- quote templates and planning for implementation teams

**Packaging implication**
Use this as a strong overlay for InsightPulseAI where offers include:
- license or subscription resale
- managed service bundles
- recurring commercial contracts
- implementation + support packaging
- renewal-aware quoting and invoicing

**Do not treat as**
- a separate fourth product line for the current wave
- a justification to expand into broad inventory/SCM scope

---

## Desired business-surface packaging

### A. InsightPulseAI package
**Primary references**
- Odoo Partner
- Software Reseller
- Marketing Agency

**Business shape**
- implementation and advisory services
- packaged success offers
- recurring service/support/subscription contracts
- website-led lead generation
- quote-to-project-to-timesheet-to-invoice flow

**Expected capability bundle**
- CRM
- Sales / quotations
- Subscription / recurring billing where justified
- Project
- Timesheets
- Invoicing / Accounting
- Website / landing pages
- Appointments
- Documents / knowledge
- Pulser assistant overlay

---

### B. PrismaLab package
**Primary references**
- Accounting Firm
- Odoo Partner (secondary)

**Business shape**
- professional services
- structured project delivery
- document-centric workflows
- time/material, fixed-fee, and milestone billing
- client-facing deliverables and controlled records

**Expected capability bundle**
- CRM
- Sales / proposals
- Project
- Timesheets
- Documents
- eSign
- Invoicing / Accounting
- Client portal
- Pulser assistant overlay

---

### C. W9 Studio package
**Primary references**
- Photography
- Marketing Agency (secondary)

**Business shape**
- booking-led studio/production service
- quote/deposit/scheduling/project execution
- portal-supported customer interaction
- campaign/content overlay where useful

**Expected capability bundle**
- CRM
- Website inquiry capture
- Appointments / bookings
- Calendar sync
- Sales / quotes
- Payments / deposits
- Project / task management
- Portal
- Email follow-up
- Pulser assistant overlay

---

## Packaging matrix

| Package | Primary business motion | Odoo reference pages | Core workflow | Shared platform dependencies | Notes |
|---|---|---|---|---|---|
| InsightPulseAI | partner/services + software resale/subscription + marketing-led lead gen | Odoo Partner, Software Reseller, Marketing Agency | lead → quote/package → sale → project → timesheet → invoice/renewal | Odoo ERP, shared MCPs, analytics, assistant control plane | most likely to use subscription/renewal patterns |
| PrismaLab | document-heavy consulting/project delivery | Accounting Firm, Odoo Partner | lead → proposal → project → documents/e-sign → timesheet/milestone billing → invoice | Odoo ERP, documents, knowledge, assistant control plane | use Accounting Firm as operating-pattern reference |
| W9 Studio | booking / scheduling / quote / project execution | Photography, Marketing Agency | inquiry → appointment → quote → deposit/payment → project/task execution | Odoo ERP, scheduling, email, optional payments | strongest need for booking and calendar UX |

---

## Shared platform interpretation

These pages do **not** imply five separate applications.
They imply **three business surfaces on one shared platform**.

### Shared underneath
- one transactional Odoo core
- one shared MCP substrate
- one shared agent/admin control surface
- one shared analytics/reporting layer

### Shared MCP layer
- Content
- CRM
- Scheduling
- Odoo / ERP
- Knowledge
- Documents
- Email
- optional Payments
- optional Analytics

---

## Current-wave implementation rule

### Use industry pages for
- workflow expectations
- packaging language
- customer-facing journey design
- benchmark UX and commercial shape

### Do not use industry pages for
- deciding core module source of truth
- overriding CE/OCA-first doctrine
- justifying new top-level product lines
- justifying broad custom-module expansion

---

## Current-wave exclusions

Even if adjacent Odoo industry pages exist, do **not** expand current scope into:
- Supply Chain / warehouse / manufacturing-heavy flows
- Commerce / POS / call-center expansion
- hard-core HR / payroll
- broad software-distributor inventory scope beyond current commercial packaging needs

---

## Final packaging statement

The current IPAI vertical-packaging target is not a collection of separate vertical ERP products. It is a shared Odoo-on-Azure platform with three distinct business surfaces: InsightPulseAI packaged primarily as an Odoo Partner + Software Reseller + Marketing Agency workflow; PrismaLab packaged primarily as an Accounting Firm-style professional-services workflow; and W9 Studio packaged primarily as a Photography-style booking and project-delivery workflow.

---

## Anchors

- **Apps SSOT:** [`ssot/apps/desired-end-state-matrix.yaml`](../../ssot/apps/desired-end-state-matrix.yaml)
- **Upstream register:** [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml)
- **Repo adoption:** [`docs/architecture/repo-adoption-register.md`](repo-adoption-register.md)
- **Desired end state matrix:** [`docs/architecture/desired-end-state-matrix.md`](desired-end-state-matrix.md)
- **Tenancy model:** [`docs/tenants/TENANCY_MODEL.md`](../tenants/TENANCY_MODEL.md)
- **Machine-readable companion:** `ssot/architecture/industry-reference-matrix.yaml` (see below)
