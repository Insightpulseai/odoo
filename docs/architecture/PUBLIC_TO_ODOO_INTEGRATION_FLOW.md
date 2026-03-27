# Public-to-Odoo Integration Flow

> Defines how browser-facing surfaces integrate with Odoo without direct coupling.
> Cross-referenced by: `INSIGHTPULSEAI_TARGET_STATE_ARCHITECTURE.md` §3, §4
> Updated: 2026-03-25

---

## Principle

**No direct browser-to-Odoo coupling.** All public interactions go through a thin API facade that validates, rate-limits, and proxies to Odoo's internal API. The browser never sees Odoo session cookies, JSON-RPC endpoints, or internal error messages.

---

## Architecture

```
Browser (public)
    │
    ▼
Azure Front Door (TLS, WAF, rate limit)
    │
    ├── GET /           → ipai-website-dev (landing page, static)
    ├── GET /ask        → ipai-copilot-gateway (Ask Pulser, anonymous)
    ├── POST /api/v1/*  → ipai-api-facade (thin proxy)
    │                         │
    │                         ▼
    │                    Odoo JSON-RPC (internal network)
    │                         │
    │                         ▼
    │                    Odoo creates record (crm.lead, calendar.event, etc.)
    │                         │
    │                         ▼
    │                    Odoo sends notification (Zoho SMTP)
    │
    └── GET /erp/*      → ipai-odoo-dev-web (authenticated, Entra OIDC)
```

## API Facade

The facade is a thin ACA container in `web/packages/api-facade/`:

| Endpoint | Method | Input | Odoo Target | Output |
|----------|--------|-------|-------------|--------|
| `/api/v1/leads` | POST | `{name, email, company, message}` | `crm.lead.create()` | `201 {id, status}` |
| `/api/v1/demo` | POST | `{name, email, preferred_date}` | `calendar.event.create()` | `201 {id, status}` |
| `/api/v1/contact` | POST | `{name, email, subject, body}` | `mail.mail.create().send()` | `201 {status}` |

### Facade Responsibilities

1. **Schema validation** — JSON Schema on every request body
2. **CAPTCHA verification** — Verify turnstile/reCAPTCHA token
3. **Rate limiting** — Per-IP and per-endpoint (in addition to Front Door WAF)
4. **Input sanitization** — Strip HTML, validate email format, length limits
5. **Odoo proxy** — Call Odoo JSON-RPC on internal network with service API key
6. **Error abstraction** — Never expose Odoo tracebacks; return clean error codes

### Facade Does NOT

- Store any data (stateless)
- Authenticate users (that's Entra for /erp routes)
- Execute business logic (that's Odoo)
- Reason about data (that's Foundry/Pulser)

## Ask Pulser Flow

```
Browser → Front Door (/ask) → ipai-copilot-gateway →
  Foundry Agent (ask-pulser-agent) →
    Grounding: approved_public_docs, pricing_faq, architecture_pages →
  Streamed response → Browser
```

- Anonymous, read-only, no PII
- No Odoo access (Ask Pulser has no Odoo tool bindings)
- Rate-limited at Front Door + gateway level

## Lead Capture Flow (Detail)

```
1. User fills form on landing page (web/ipai-landing/)
2. Browser POSTs to /api/v1/leads with CAPTCHA token
3. Front Door WAF validates (rate limit, geo, bot detection)
4. API facade receives request:
   a. Validates JSON Schema
   b. Verifies CAPTCHA token
   c. Sanitizes inputs
   d. Calls Odoo JSON-RPC: crm.lead.create({
        name: sanitized_name,
        email_from: sanitized_email,
        partner_name: sanitized_company,
        description: sanitized_message,
        source_id: web_landing_source_id
      })
   e. Odoo creates crm.lead record
   f. Odoo triggers automation:
      - Assign to sales team
      - Send notification via Zoho SMTP
      - Create activity for follow-up
5. Facade returns 201 {id: lead_id, status: "created"}
6. Browser shows confirmation
```

## Security

- API facade runs on internal VNet with Front Door as sole ingress
- Odoo API key stored in Key Vault, injected as env var
- No Odoo session cookies exposed to browser
- All requests logged to Application Insights

---

*See `INSIGHTPULSEAI_TARGET_STATE_ARCHITECTURE.md` §4.2 for the facade contract.*
