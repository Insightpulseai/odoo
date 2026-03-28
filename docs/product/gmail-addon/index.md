# InsightPulseAI for Gmail -- Product Scope

> Google Workspace add-on connecting Gmail to Odoo CE 19 on Azure Container Apps.

---

## Overview

InsightPulseAI for Gmail is a Google Workspace add-on that surfaces Odoo ERP context directly inside Gmail. Users can look up contacts, create leads, log emails, and submit expenses without leaving their inbox.

The add-on runs as a Google Workspace add-on (not a Chrome extension). Google hosts the card UI and manages user consent. The backend communicates with Odoo CE 19 via JSON-RPC through an integration layer on Azure Container Apps.

**Public brand**: Pulser for Gmail
**Internal name**: InsightPulseAI Gmail Add-on
**Marketplace listing name**: InsightPulseAI for Gmail

---

## Target Users

| Role | Primary Use Cases |
|------|-------------------|
| **Finance** | Submit expenses from receipt emails, view vendor payment status, link invoices to Odoo records |
| **Sales** | Create leads from prospect emails, view Odoo contact/company info, log sales-related emails |
| **HR / Admin** | Create internal tickets, log correspondence, look up employee records |
| **Operations** | Link emails to Odoo tasks, view delivery/purchase order status from supplier emails |

All target users are internal employees at `insightpulseai.com` who use Gmail as their primary email client.

---

## Supported Gmail Surfaces

| Surface | Trigger | Description |
|---------|---------|-------------|
| **Homepage card** | User opens the add-on panel | Shows authenticated user status, recent Odoo activity, quick-action buttons |
| **Contextual message card** | User opens an email | Looks up the sender's email in Odoo, shows matching partner/company info, related records (leads, invoices, tasks) |
| **Compose action** | User composes or replies | Offers to link the outgoing email to an Odoo record or create a new lead from the draft |

---

## Odoo Integration Scope

### Read Operations

- Partner/contact lookup by email address
- Company info display (name, phone, website, tags)
- Related record summary (open leads, recent invoices, active tasks)
- User session validation and status

### Write Operations

- Create lead (CRM) from email context
- Create ticket/task from email context
- Log email as a note on an existing Odoo record (partner, lead, task)
- Create expense entry from receipt email (with optional OCR attachment)

### Out of Scope

- Full Odoo UI rendering inside Gmail
- Bulk record operations
- Odoo settings or configuration changes
- Direct database access (all operations go through Odoo JSON-RPC)

---

## Distribution Strategy

| Phase | Visibility | Scope |
|-------|-----------|-------|
| **Phase 1** (current) | Private | `insightpulseai.com` domain only |
| **Phase 2** | Private (expanded) | Invited partner domains |
| **Phase 3** (future) | Public | Google Workspace Marketplace listing |

Private listing is the initial target. Google's Marketplace documentation notes that visibility choice (private vs. public) has implications for review scope and cannot be freely toggled after initial submission.

---

## Architecture Overview

```
Gmail UI (Google-hosted cards)
    |
    v
Google Workspace Add-on Runtime
    |
    v  (HTTPS + ID token)
Integration Backend (Azure Container Apps)
    |
    v  (JSON-RPC, session-based)
Odoo CE 19 (erp.insightpulseai.com)
    |
    v
PostgreSQL (pg-ipai-odoo)
```

The add-on has four planes:

1. **Gmail card UI** -- Google renders cards from JSON responses. No custom HTML.
2. **Integration backend** -- Receives card action requests, verifies Google ID tokens, maps Google identity to Odoo user, proxies operations to Odoo.
3. **Odoo API** -- Standard JSON-RPC endpoints plus custom `ipai_mail_plugin` controller routes.
4. **Google Cloud / Marketplace** -- OAuth consent, Workspace Marketplace listing, deployment configuration.

---

## Related Documents

| Document | Path |
|----------|------|
| Capability model | `docs/product/gmail-addon/capability-model.md` |
| Auth and permissions | `docs/product/gmail-addon/auth-and-permissions.md` |
| Marketplace distribution | `docs/product/gmail-addon/marketplace-distribution.md` |
| Privacy and data use | `docs/product/gmail-addon/privacy-data-use.md` |
| Architecture | `docs/architecture/gmail-addon-architecture.md` |
| Auth flow | `docs/architecture/gmail-addon-auth-flow.md` |
| Backend contract | `docs/architecture/gmail-addon-backend-contract.md` |
| SSOT contract | `ssot/google-workspace/gmail-addon-contract.yaml` |
| Source code | `web/apps/gmail-odoo-addon/` |
