---
name: email_communication
description: Configure and manage inbound/outbound email communication via chatter, aliases, and SMTP in Odoo.
metadata:
  author: Claude Agent
  version: "19.0"
  source: "Odoo 19.0 Official Documentation"
  extracted: "2026-02-18"
---

# email_communication — Odoo 19.0 Skill Reference

## Overview

Email communication in Odoo is centered on the **chatter** — a per-record discussion thread displayed on CRM opportunities, sales orders, invoices, and other models. Outgoing emails, incoming replies, internal notes, and notifications all flow through the chatter. The module covers outbound/inbound mail server configuration, custom domain setup (SPF/DKIM/DMARC), email aliases, and third-party OAuth integrations (Outlook, Gmail, Mailjet). Administrators, IT staff, and on-premise operators use these features to ensure reliable email delivery and routing.

## Key Concepts

- **Chatter**: Per-record threaded discussion panel that logs emails, notes, WhatsApp/SMS, and activities.
- **Alias domain**: The domain used for building catchall, bounce, and notification addresses (e.g., `company-name.odoo.com` or a custom domain).
- **Catchall alias**: Generic fallback email alias (`catchall@domain`) that routes replies to the correct chatter via `message-id` headers.
- **Bounce alias**: Address used in the `Return-Path` header; receives delivery-failure notifications (red envelope in chatter).
- **Notification address**: Default `FROM` address for outgoing emails (default: `notifications@domain`).
- **FROM filtering**: Per-server rule that selects which outgoing SMTP server to use based on the sender's email domain or address.
- **SPF (Sender Policy Framework)**: DNS TXT record specifying servers authorized to send on behalf of a domain.
- **DKIM (DomainKeys Identified Mail)**: CNAME DNS record enabling cryptographic signature verification of outgoing emails.
- **DMARC**: Protocol unifying SPF and DKIM that tells recipients what to do when checks fail (`p=none|quarantine|reject`).
- **Incoming mail server**: IMAP/POP configuration that fetches emails from a mailbox into Odoo via the `Mail: Fetchmail Service` scheduled action.
- **Redirection/forwarding**: Mail server rule that forwards alias emails to Odoo's subdomain for immediate delivery.
- **MX record method**: DNS record pointing a subdomain at Odoo's mail infrastructure (advanced, requires subdomain).

## Core Workflows

### 1. Configure a custom domain with Odoo's mail server (Online/SH)

1. Add SPF include: `v=spf1 include:_spf.odoo.com ~all` to the domain's TXT record.
2. Add DKIM CNAME: `odoo._domainkey` pointing to `odoo._domainkey.odoo.com.`
3. In Settings, set the custom domain as the **Alias Domain** for the company.
4. Configure inbound routing via redirections, incoming mail servers, or MX record.
5. Validate with MXToolbox or Mail-Tester.

### 2. Configure an external SMTP server (on-premise)

1. Navigate to Settings > enable **Use Custom Email Servers** > Save.
2. Go to Settings > Technical > Outgoing Email Servers > New.
3. Enter SMTP host, port (465/587/2525 — port 25 blocked on Online/SH), credentials, and encryption.
4. Set **FROM Filtering** to the custom domain or specific address.
5. Click **Test Connection**.

### 3. Split transactional and mass-mailing servers

1. Enable developer mode; go to Settings > Technical > Outgoing Mail Servers.
2. Create two servers: transactional (priority 1) and mass-mailing (priority 2).
3. In Email Marketing > Configuration > Settings, enable **Dedicated Server** and select the mass-mailing server.

### 4. Set up inbound mail via redirections

1. In the domain's mail server, create redirections: `catchall@custom.com` -> `catchall@db.odoo.com`, `bounce@custom.com` -> `bounce@db.odoo.com`, plus each alias.
2. Emails arrive in Odoo without delay.

### 5. Set up incoming mail servers (IMAP/POP)

1. Go to Settings > Technical > Incoming Mail Servers > New.
2. Enter server type (IMAP recommended), host, port, credentials.
3. Optionally set the model to create records (e.g., `crm.lead`).
4. Emails fetched by `Mail: Fetchmail Service` CRON.

## Technical Reference

### Models

| Model | Purpose |
|-------|---------|
| `ir.mail_server` | Outgoing mail server configuration |
| `fetchmail.server` | Incoming mail server configuration |
| `mail.alias` | Email alias definitions |
| `mail.alias.domain` | Alias domain management (developer mode) |
| `mail.message` | Individual chatter messages |
| `mail.mail` | Outgoing email queue |

### Key System Parameters

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `mail.default.from_filter` | (subdomain) | FROM filtering when no outgoing server is set |
| `mail.catchall.domain.allowed` | (none) | Comma-separated domains to accept for alias matching |
| `mail.gateway.loop.minutes` | `120` | Time window for loop detection |
| `mail.gateway.loop.threshold` | `20` | Max emails per sender in the loop window |

### Menu Paths

- `Settings > Emails > Use Custom Email Servers`
- `Settings > Technical > Email: Outgoing Mail Servers`
- `Settings > Technical > Email: Incoming Mail Servers`
- `Settings > Technical > Email: Alias Domains`
- `Settings > Technical > Aliases`

### DNS Records for Odoo's Mail Server

- **SPF TXT**: `v=spf1 include:_spf.odoo.com ~all`
- **DKIM CNAME**: `odoo._domainkey` -> `odoo._domainkey.odoo.com.`
- **DMARC TXT**: e.g., `v=DMARC1; p=none; rua=mailto:postmaster@example.com`

## API / RPC Patterns

<!-- TODO: not found in docs -->

## Version Notes (19.0)

<!-- TODO: not found in docs — no explicit 18 vs 19 breaking changes listed in RST source -->

## Common Pitfalls

- **Port 25 blocked**: On Odoo Online and Odoo.sh, port 25 is blocked. Use port 465, 587, or 2525.
- **Changing catchall/bounce aliases**: Modifying these after emails have been sent causes replies to old addresses to be lost.
- **Forwarding vs. redirection**: Forwarding rewrites the sender address; redirection preserves it. Use redirection for correct chatter attribution.
- **Multiple SPF records**: A domain must have only one SPF TXT record. Add Odoo's include to the existing record rather than creating a second one.
- **Loop protection**: A single sender can only send 20 emails in 120 minutes to record-creating aliases. Adjust system parameters if legitimate high-volume senders are blocked.
