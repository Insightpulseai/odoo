# W9 Studio — Google Workspace Integration Architecture

## Status
Proposed

## Purpose
Define the W9 Studio operating model where **Google Workspace is the collaboration / identity / communications plane** and **Odoo remains the transactional system of record**.

---

## Doctrine

> **Google Workspace = identity, communication, calendar, documents, internal productivity.**
> **Odoo = lead, booking, quote, invoice, project, portal, operational record.**

Do NOT let Google Workspace become the booking system of record.
Do NOT split customer truth between Workspace and Odoo.

---

## Plane assignment

### Google Workspace owns
- User identity + Google sign-in (staff)
- Gmail (operational mail)
- Google Calendar (staff + studio/resource calendars)
- Google Meet (call links)
- Drive / Docs / Sheets (collaborative working files)
- Groups / mailing lists (functional routing aliases)
- Room/resource calendars for studio scheduling
- Internal staff productivity (Gemini in Workspace)

### Odoo owns
- Leads + CRM
- Booking records (authoritative)
- Quotes + packages
- Deposits + invoices
- Projects + shoot execution
- Customer portal
- Tasking + operational follow-through
- Reporting tied to sales/bookings/delivery

---

## Why this fits W9

Odoo 18 ships with documented Google integrations:
- **Google Sign-In Authentication** for users signing into Odoo with Google accounts (Workspace-aware)
- **Google Calendar synchronization** (two-way sync between Odoo and Google Calendar)
- **Gmail OAuth integration** (secure outbound email from Odoo through Google Workspace)

Upstream Odoo modules: `google_account`, `google_calendar`, `google_gmail` (plus `microsoft_outlook` adjacent).

---

## Operating model

### Front office (W9 website — `w9studio.net`)
- Inquiry capture
- Service/package discovery
- Booking request or appointment request
- Quote request

### Odoo (transactional truth)
- Lead
- Customer
- Booking
- Quotation
- Invoice/deposit
- Project/task

### Google Workspace (collaboration + scheduling)
- Calendar availability
- Booking confirmations by email
- Meet links for virtual client calls
- Shared documents for briefs, shot lists, contracts
- Internal team communication

---

## Integration blueprint

### 1. Google Workspace login for staff (P0)
- Use Google Workspace accounts as the staff identity layer for Odoo login
- Reduces local password sprawl; fits existing Workspace tenancy
- Module: Odoo `google_account` + Google Sign-In configuration

### 2. Google Calendar as availability surface (P0)
- Staff calendars (per-employee)
- Studio/resource calendars (per-room/per-asset)
- Room/resource availability
- Client meeting coordination
- Sync state: **Odoo holds booking record**; Calendar shows availability
- Module: Odoo `google_calendar` (two-way sync)

### 3. Gmail as outbound communications rail (P0)
- Inquiry acknowledgments
- Quote follow-ups
- Booking confirmations
- Reminders
- Production updates
- Module: Odoo `google_gmail` (OAuth)

### 4. Drive as working document layer (P1)
- Client briefs
- Shoot plans
- Floor plans
- Run sheets
- Contracts
- Production checklists
- Pattern: Odoo stores the booking/quote/invoice/project record; Drive stores the collaborative working files
- Reference link from Odoo project → Drive folder

### 5. Meet as meeting/call layer (P1)
- Discovery calls
- Pre-production calls
- Virtual walkthroughs
- Client reviews
- Pattern: Meet event attached to Odoo booking/project record (via Calendar sync)

### 6. Groups as functional routing (P1)
- `bookings@`
- `studio@`
- `production@`
- `finance@`
- `hello@`
- Route inquiries into Odoo workflows (don't keep email-only ops)

### 7. Gemini in Workspace for internal productivity (P2)
- Summarize email threads
- Draft client replies
- Extract action items from notes/docs
- Prepare internal content
- Boundary: Pulser/Odoo assistant remains the **business-action layer** (booking state, quotes, payments, projects, client/account context)

---

## Shared MCP layer impact

W9 + Google Workspace does **NOT** require a new site-specific MCP stack.

### Required (harden these shared MCPs)
- **Scheduling MCP** (Calendar + Odoo)
- **Email/communications MCP** (Gmail OAuth + Odoo `mail.mail`)
- **Documents MCP** (Drive + Odoo documents linkage)
- (optional) Workspace identity/admin bridge for internal ops

### Still shared with the rest of the platform
- CRM MCP
- Odoo/ERP MCP
- Knowledge MCP
- Content MCP

This preserves the shared-MCP doctrine in `ssot/apps/desired-end-state-matrix.yaml`.

---

## Implementation sequencing

### P0 (now)
- Google Sign-In for Odoo staff
- Gmail OAuth for outbound mail
- Google Calendar sync for bookings/appointments
- Google Groups for routing aliases

### P1 (next)
- Drive/Docs linkage from Odoo booking/project records
- Meet link generation in booking/project flows
- Shared room/resource calendar model for studio spaces

### P2 (later)
- Workspace-aware assistant workflows (Pulser × Workspace tools)
- Gemini-assisted internal ops patterns
- Admin/automation layer for Workspace-backed operational tasks

---

## Anti-patterns (do NOT do)

- ❌ Use Google Calendar as the **only** booking database
- ❌ Manage quotes and invoices in Sheets/Docs
- ❌ Let Drive folder structure become the client/project source of truth
- ❌ Split customer truth between Workspace and Odoo
- ❌ Build a W9-specific MCP stack (per-site MCPs are rejected by `feedback_apps_and_mcp_architecture.md`)

---

## Anchors

- **Apps SSOT:** [`ssot/apps/desired-end-state-matrix.yaml`](../../ssot/apps/desired-end-state-matrix.yaml)
- **Industry mapping:** [`industry-reference-matrix.md`](industry-reference-matrix.md)
- **Upstream register:** [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml) (§I Google Workspace)
- **Tenancy:** [`docs/tenants/TENANCY_MODEL.md`](../tenants/TENANCY_MODEL.md) (W9 = company_id 2)
- **Memory:**
  - `feedback_w9_google_workspace_integration.md`
  - `feedback_apps_and_mcp_architecture.md`
  - `project_w9studio_concept.md`

## Bottom line

W9 leverages Google Workspace **for collaboration and scheduling**, while Odoo stays the **transaction and operations** system of record. This gives W9 the best of both ecosystems without muddying system ownership.
