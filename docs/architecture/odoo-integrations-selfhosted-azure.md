# Odoo Integrations Doctrine — Self-Hosted on Azure

## Status
Proposed

## Purpose
Define the integration doctrine for IPAI's self-hosted Odoo on Azure runtime.

This document clarifies:
- what counts as the default integration path
- what changes when Odoo is self-hosted on Azure
- how Google, Microsoft, email, calendar, storage, external API, payments, and agent access should be handled
- when to use core Odoo, OCA, thin IPAI adapters, or third-party modules

---

## Scope

### In scope
- self-hosted Odoo on Azure
- current-wave benchmark surfaces:
  - Finance
  - Finance agents
  - Project Operations
- Google Workspace integrations
- Microsoft account/calendar/outlook integrations
- Azure-hosted secrets, networking, storage, and runtime concerns
- external API and controlled agent access
- payment-provider decision order

### Out of scope
- Odoo Online / Odoo.sh operational assumptions
- broad marketplace-module adoption without a proven gap
- generic MCP-first integration strategy
- custom forks of Odoo core for standard integrations
- broad supply-chain, manufacturing, Commerce, or HR expansion

---

## Core doctrine

1. **Built-in Odoo integrations come first.**
2. **OCA comes second** when core Odoo is insufficient.
3. **Thin IPAI adapters come third** only when CE + OCA composition still leaves a real gap.
4. **Third-party marketplace modules are last resort** for current-wave scope.
5. **Do not fork Odoo core just to support standard integrations.**
6. **Self-hosting on Azure means IPAI owns the infrastructure responsibilities** around domain stability, HTTPS, OAuth callbacks, secrets, webhook reachability, and environment separation.

---

## Integration decision order

Use this order for every new integration proposal:

1. Odoo core module or documented built-in feature
2. Selected OCA module
3. Thin IPAI adapter or bridge
4. Third-party marketplace/vendor module
5. Custom implementation only if all above are insufficient

---

## Self-hosted-on-Azure responsibilities

For self-hosted Odoo, the application capability may be built-in, but IPAI owns the deployment responsibilities.

### IPAI-owned responsibilities
- public base URL stability
- HTTPS / certificate management
- OAuth redirect URI correctness
- secret storage and rotation
- outbound egress policy
- inbound webhook reachability
- DNS and mail-domain alignment
- dev/stg/prod environment separation
- integration test databases and non-production mailboxes

### Required Azure posture
- Key Vault for secrets
- stable public ingress for callback-based integrations
- per-environment separation of app/runtime settings
- explicit observability for failed OAuth, mail, calendar, and webhook events

---

## Default approved integration categories

### Google Workspace
Approved as a primary collaboration and productivity plane.

#### Preferred uses
- Google Sign-In for staff
- Gmail OAuth for outbound mail
- Google Calendar sync
- Google Meet-aware scheduling workflows
- Drive/Docs/Sheets as collaborative document layer

#### System-of-record rule
- Google Workspace is **not** the booking, CRM, quote, invoice, or project system of record
- Odoo remains the transactional system of record
- Workspace remains the identity / communication / scheduling / collaboration plane

---

### Microsoft account / calendar / outlook
Approved where a business unit or customer context requires Microsoft-based productivity integration.

#### Preferred uses
- Microsoft identity for staff where justified
- Outlook/calendar synchronization
- mail and scheduling interoperability

#### System-of-record rule
- Microsoft productivity surfaces are adjunct collaboration tools
- Odoo remains the operational and transactional source of truth

---

### Azure-backed storage
Approved where Azure-native object/document storage is needed.

#### Preferred uses
- document/blob storage support
- controlled Azure-hosted file strategies
- separation between transactional records and working-file storage

#### Rule
- documents/files may live in Azure-backed storage
- transactional references, workflow state, and business records remain in Odoo

---

## Built-in-first integration inventory

For current-wave self-hosted Azure deployments, treat these as the default starting point:

### Identity / auth
- Google Sign-In
- Microsoft account where justified

### Productivity
- Google Calendar synchronization
- Gmail OAuth
- Microsoft calendar / Outlook where justified

### Storage
- Azure-backed cloud storage support where appropriate

### API / automation
- Odoo external API for controlled integrations and agent access

### Payments
- built-in payment providers first
- OCA or vendor modules only for real regional/provider gaps

---

## External API doctrine

### Default rule
Use the Odoo external API as the first programmable integration surface for:
- controlled backend integrations
- internal automation
- Pulser/agent access through approved boundaries
- operational read/write actions with explicit governance

### Do not default to
- deep custom MCP modules
- custom Odoo forks
- direct uncontrolled agent write access to production finance objects

### Agent-access rule
Agent access to Odoo must be:
- least-privilege
- auditable
- tool-allowlisted
- approval-aware for sensitive actions
- segregated by environment

---

## MCP doctrine for Odoo

### Current-wave position
MCP is **optional and secondary**, not the default first integration layer.

### Use MCP only when
- external API plus thin service logic is not enough
- a controlled tool surface materially improves agent safety/usability
- the MCP boundary can be governed more safely than direct application access

### Do not use MCP as
- the first answer to every Odoo integration request
- a substitute for core API design
- a reason to introduce custom finance-side access without approval controls

---

## Payments doctrine

### Decision order
1. Built-in Odoo payment provider
2. Selected OCA payment/bank-payment support
3. Vendor/regional module if there is a real provider gap
4. Thin IPAI bridge only if prior paths fail

### Rules
- do not build custom payment-provider code where built-in or community-supported modules exist
- payment-provider selection must be driven by actual regional/provider need
- current-wave payment work should support the public-site and finance scope without dragging in unrelated Commerce expansion

---

## Environment separation doctrine

### Required environment split
- `dev`
- `stg`
- `prod`

### Integration rules
- non-production OAuth projects/apps may be separate where provider constraints require it
- non-production mailboxes/calendars should be used for integration testing
- callback URLs must be environment-specific
- test databases must not accidentally send production mail or invites
- production credentials must never be reused casually in lower environments

---

## Google Workspace doctrine for W9 / public-site operations

### Approved split
- Google Workspace:
  - identity
  - Gmail
  - Calendar
  - Meet
  - Drive / Docs / Sheets
  - Groups
- Odoo:
  - leads
  - bookings
  - quotes
  - invoices
  - projects
  - portal
  - operational workflow

### Rule
Do not allow Google Calendar, Gmail, Drive folders, or Docs to become the operational source of truth for bookings or project state.

---

## Azure implementation rules

### Secrets
- store OAuth client credentials, API tokens, mail secrets, and webhook secrets in Key Vault
- inject secrets into runtime; do not commit to repo
- rotate via platform process, not ad hoc edits

### Networking
- keep public callback endpoints stable
- ensure providers can reach webhook/callback routes
- document outbound dependency list for Google/Microsoft/payment endpoints

### Observability
Track and alert on:
- OAuth failures
- token refresh failures
- mail delivery/auth failures
- calendar sync failures
- webhook delivery failures
- external API auth failures

---

## Approved extension strategy by category

| Category | Default path | Escalation path | Last resort |
|---|---|---|---|
| Google auth/mail/calendar | Odoo core | thin config/ops adapter | third-party module |
| Microsoft auth/mail/calendar | Odoo core | thin config/ops adapter | third-party module |
| Storage | Odoo core / Azure-native config | thin bridge | custom module |
| Payments | Odoo core | OCA / vendor module | thin IPAI bridge |
| Agent access | external API + governed service layer | MCP wrapper | custom module |
| Booking-specific UX | core + OCA | selected third-party | thin IPAI adapter |

---

## Explicit prohibitions

Do not:
- fork Odoo core to support standard Google/Microsoft integrations
- default to marketplace modules before checking core and OCA
- expose production finance objects to unrestricted agent write access
- let Gmail/Calendar/Drive replace Odoo as the system of record
- treat MCP as mandatory for all Odoo integrations
- collapse dev/stg/prod into one shared integration configuration

---

## Current-wave desired end state

### Integration posture
- self-hosted Odoo on Azure is the transactional core
- Google Workspace is the primary collaboration/identity plane where applicable
- built-in Odoo integrations are enabled first
- external API is the default programmable access layer
- MCP is optional and controlled
- payments follow built-in → OCA/vendor → thin bridge order

### Operational posture
- all integration secrets live in Key Vault
- callback URLs are stable and environment-specific
- observability exists for auth/mail/calendar/webhook/API failures
- test/prod separation is explicit

### Code ownership posture
- no standard-integration fork of Odoo core
- OCA selected surgically for real gaps
- IPAI owns only:
  - thin adapters
  - environment composition
  - SSOT
  - tests
  - delivery and governance logic

---

## Final doctrine statement

For self-hosted Odoo on Azure, IPAI will use built-in Odoo integrations first, selected OCA modules second, and thin IPAI adapters only when a proven functional or operational gap remains. Azure is responsible for runtime, secrets, networking, and callback stability; Odoo remains the transactional system of record; productivity suites such as Google Workspace or Microsoft 365 remain collaboration and communication layers, not operational truth.

---

## Source basis

- Odoo 18 integrations docs: https://www.odoo.com/documentation/18.0/applications/general/integrations.html
- Google Calendar sync (incl. test-DB recommendation): https://www.odoo.com/documentation/18.0/applications/productivity/calendar/google.html
- Gmail OAuth: https://www.odoo.com/documentation/18.0/applications/general/email_communication/google_oauth.html
- External API (self-hosted favorable): https://www.odoo.com/documentation/18.0/developer/reference/external_api.html

## Anchors

- **Upstream register:** [`ssot/governance/upstream-adoption-register.yaml`](../../ssot/governance/upstream-adoption-register.yaml) (§I Google Workspace + §J self-hosted built-in-first)
- **W9 Workspace integration:** [`w9-google-workspace-integration.md`](w9-google-workspace-integration.md)
- **Module selection:** `feedback_odoo_module_selection_doctrine.md` (memory)
- **Azure BOM:** [`ssot/azure/bom.yaml`](../../ssot/azure/bom.yaml)
- **Azure naming:** [`ssot/azure/naming-convention.yaml`](../../ssot/azure/naming-convention.yaml)
- **CLAUDE.md** — Zoho SMTP rules + DB convention
- **Memory:** `feedback_odoo_selfhosted_azure_integrations.md`, `feedback_w9_google_workspace_integration.md`
