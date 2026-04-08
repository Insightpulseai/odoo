# PRD: InsightPulseAI Gmail Add-on + Odoo Bridge

## Problem

Odoo's official Gmail plugin requires the `mail_plugin` module to communicate
with `odoo.com` infrastructure for IAP-based enrichment and partner matching.
Our on-premise ERP at `erp.insightpulseai.com` cannot use this plugin because:

1. The marketplace plugin hardcodes calls to `partner-autocomplete.odoo.com`.
2. It requires an `odoo.com` account and IAP credits.
3. It does not support self-hosted or custom-domain Odoo instances.

## Solution

Build an **org-owned Google Workspace add-on** paired with a **thin Odoo HTTP
bridge module** (`ipai_mail_plugin_bridge`). The add-on runs inside Gmail,
calls our own bridge endpoints on `erp.insightpulseai.com`, and never contacts
`odoo.com`.

### Architecture

```
Gmail UI (Card Service)
    |
    | HTTPS / JSON-RPC
    v
erp.insightpulseai.com/ipai/mail_plugin/*
    |
    | ORM
    v
Odoo CE 19 (res.partner, crm.lead, project.task, mail.thread)
```

## V1 Scope

| Feature | Endpoint |
|---------|----------|
| Auth via API key | `POST /ipai/mail_plugin/session` |
| Contact lookup by sender email | `POST /ipai/mail_plugin/context` |
| View related leads | included in context response |
| View related tasks/tickets | included in context response |
| Create CRM lead | `POST /ipai/mail_plugin/actions/create_lead` |
| Create ticket (project.task) | `POST /ipai/mail_plugin/actions/create_ticket` |
| Log note to chatter | `POST /ipai/mail_plugin/actions/log_note` |
| Open record in Odoo | client-side OpenLink |

## V1.1 (Planned)

- Draft reply from Odoo email templates
- Helpdesk module integration (if `helpdesk` OCA module adopted)
- Attachment forwarding to Odoo chatter

## Later

- Foundry-assisted email summarization via Azure OpenAI
- Suggested replies based on CRM stage
- Calendar event creation from email context

## Security

- Tokens are stored as SHA-256 hashes server-side; raw tokens stay client-side.
- API key authentication; no session cookies exposed to the add-on.
- Credentials stored in `PropertiesService.getUserProperties()` (per-user, encrypted by Google).
- All traffic over TLS via Azure Front Door.

## Deployment

- Add-on: deployed to the Google Workspace org via Apps Script project (not marketplace).
- Bridge: installed as an Odoo module (`ipai_mail_plugin_bridge`) on `erp.insightpulseai.com`.

## Success Criteria

- Gmail sidebar shows matched contact within 2 seconds of opening a message.
- Lead creation from Gmail takes fewer than 3 clicks.
- No dependency on `odoo.com`, IAP, or the official Odoo Gmail plugin.
