# Supabase Email Events Pack

**Status**: DRAFT / IMPLEMENTATION-READY
**Scope**: Mirror Odoo Enterprise-style email tracking and observability using Supabase.

This pack assumes:
- Outbound email is already wired through Mailgun via `ipai_mailgun_bridge`.
- Odoo is your canonical email sender; Supabase is the canonical **events warehouse**.

---

## 1. Objectives

1. Capture **all outbound email events** (delivered, opened, clicked, bounced, complained) in Supabase.
2. Capture **inbound email webhooks** (replies, support tickets, contact forms) for analysis.
3. Provide a **queryable analytics layer** (tables + views) for:
   - Delivery health
   - Engagement (opens/clicks)
   - Bounce/complaint tracking
4. Provide a **simple integration surface** for:
   - Dashboards (Superset, Scout, etc.)
   - Agents (Pulser, Odoo Cloud DevOps Copilot)
   - Alerting (n8n, Mattermost, email alerts)

---

## 2. Schema Design

Schema: `email_parity`

### 2.1. Tables

1. `email_parity.messages`
   - One row per logical outbound message.

   Columns (key ones):

   - `id` (bigint, PK)
   - `message_id` (text, unique)           – Mailgun / SMTP message ID
   - `odoo_mail_id` (integer, nullable)    – link to Odoo `mail.mail` (if known)
   - `from_address` (text)
   - `to_addresses` (text[])
   - `cc_addresses` (text[])
   - `bcc_addresses` (text[])
   - `subject` (text)
   - `template_key` (text, nullable)       – logical template identifier
   - `meta` (jsonb)                        – arbitrary metadata (campaign, model_name, res_id, etc.)
   - `created_at` (timestamptz, default now())

2. `email_parity.events`
   - One row per email event.

   Columns:

   - `id` (bigint, PK)
   - `message_id` (text, FK → messages.message_id)
   - `event_type` (text)           – delivered, opened, clicked, bounced, complained, stored, rejected, etc.
   - `provider` (text)             – 'mailgun'
   - `provider_event_id` (text)    – provider-specific ID
   - `event_payload` (jsonb)       – full webhook payload
   - `recipient` (text)
   - `endpoint` (text)             – which Edge Function / webhook
   - `ip` (inet, nullable)
   - `user_agent` (text, nullable)
   - `created_at` (timestamptz, default now())
   - `occurred_at` (timestamptz)   – event timestamp from provider

3. `email_parity.webhook_logs`
   - One row per webhook hit (for troubleshooting).

   Columns:

   - `id` (bigint, PK)
   - `endpoint` (text)
   - `status_code` (integer)
   - `request_headers` (jsonb)
   - `request_body` (jsonb)
   - `error_message` (text, nullable)
   - `received_at` (timestamptz, default now())

---

## 3. Views

1. `email_parity.v_message_summary`
   - Aggregated delivery/engagement metrics per message.

2. `email_parity.v_recipient_health`
   - Aggregated per-recipient status: last_delivery, last_bounce_reason, complaint_flag.

---

## 4. Security & RLS

- API clients normally **read-only** on:
  - `messages`
  - `events`
  - views (`v_message_summary`, `v_recipient_health`)
- **No direct inserts** from client; all writes come from:
  - Supabase Edge Functions (`auth.admin` or service-role)
  - Internal server-side jobs

RLS pattern (high-level):

- Public read access via PostgREST / GraphQL **may be restricted** to:
  - Internal service role
  - Specific dashboards (using JWT claims)
- Edge Function uses `service_role` key and bypasses RLS.

---

## 5. Ingestion Architecture

### 5.1. Provider → Supabase

Mailgun webhooks:

- Route 1: Outbound events
  - URL: `https://<project>.functions.supabase.co/email-events`
  - Event types: delivered, opened, clicked, bounced, complained, etc.

- Route 2: Inbound email
  - URL: `https://<project>.functions.supabase.co/email-inbound`
  - Event type: stored/forwarded emails

Supabase Edge Functions:

- `email-events`:
  - Validate HMAC signature from Mailgun.
  - Upsert into `email_parity.messages` using `message-id`.
  - Insert into `email_parity.events`.
  - Insert into `email_parity.webhook_logs`.

- `email-inbound`:
  - Same pattern, but focusing on inbound routing; can also call Odoo or Supabase RPCs for ticket creation.

---

## 6. Integration with Odoo

Odoo `ipai_mailgun_bridge` emits:

- `message-id` when sending emails.
- Odoo metadata (model, res_id, environment, user) in custom headers or the Mailgun variables payload.

Supabase pack expects:

- `message-id` to be consistent between Odoo and Mailgun.
- (Optional) `ipai_context` JSON field from Odoo, passed into Mailgun custom variables, stored in `messages.meta`.

Later, an Odoo module or Supabase script can:

- Join Odoo data with Supabase events for deep analytics.
- Provide **EE-like email insight dashboards**.

---

## 7. Use Cases / EE Parity Coverage

This pack targets parity with typical Odoo Enterprise email tracking:

1. **Deliverability monitoring**
   - Which emails are bouncing?
   - Which domains are problematic?

2. **Engagement analytics**
   - Who opened/clicked which campaigns?
   - Aggregate open/click rates by template or campaign.

3. **Support & Helpdesk**
   - See inbound reply patterns by user/company.
   - Hook into Odoo Helpdesk or custom ticketing.

4. **Compliance & Audit**
   - Full log of webhook calls and outcomes.
   - Capability to reprocess events if downstream processing fails.

---

## 8. Implementation Steps

1. Apply migrations (schema + views).
2. Deploy Edge Functions (`email-events`, `email-inbound`).
3. Configure Mailgun webhooks to point to the Supabase function URLs.
4. Update `ipai_mailgun_bridge` to include:
   - `message-id` and `ipai_context` variables for each email.
5. Wire analytics tools (Superset, custom dashboards, agents) to query views.

---

## 9. Verification Commands

```bash
# Check schema exists
psql "$SUPABASE_DB_URL" <<'SQL'
SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'email_parity';
SQL

# View recent messages
psql "$SUPABASE_DB_URL" <<'SQL'
SELECT message_id, subject, from_address, created_at
FROM email_parity.messages
ORDER BY created_at DESC
LIMIT 10;
SQL

# View recent events
psql "$SUPABASE_DB_URL" <<'SQL'
SELECT message_id, event_type, recipient, occurred_at
FROM email_parity.events
ORDER BY occurred_at DESC
LIMIT 10;
SQL

# Check delivery metrics
psql "$SUPABASE_DB_URL" <<'SQL'
SELECT * FROM email_parity.v_message_summary
ORDER BY last_event_at DESC
LIMIT 10;
SQL

# Check recipient health
psql "$SUPABASE_DB_URL" <<'SQL'
SELECT * FROM email_parity.v_recipient_health
WHERE bounce_count > 0 OR complaint_count > 0
ORDER BY last_bounce_at DESC NULLS LAST
LIMIT 10;
SQL
```

---

## 10. Monitoring & Alerts

**Health Checks**:
- Webhook delivery rate (should be >99%)
- Event processing latency (<5 seconds)
- Bounce rate by domain (<5%)
- Complaint rate (<0.1%)

**Alert Thresholds** (n8n workflows):
- **Critical**: Webhook endpoint down (5+ failures in 5 minutes)
- **Warning**: Bounce rate >10% for any domain in last hour
- **Info**: New complaint received (immediate notification)

**Dashboard Metrics** (Superset):
- Daily email volume by template
- Delivery success rate trend (7/30 days)
- Engagement funnel (delivered → opened → clicked)
- Top bouncing domains
- Recent complaints with context

---

## 11. Mailgun Webhook Configuration

**Required Webhooks** (configure in Mailgun dashboard):

| Event Type | URL | Description |
|------------|-----|-------------|
| delivered | `https://<project>.functions.supabase.co/email-events` | Successful delivery |
| opened | `https://<project>.functions.supabase.co/email-events` | Email opened (tracking pixel) |
| clicked | `https://<project>.functions.supabase.co/email-events` | Link clicked |
| bounced | `https://<project>.functions.supabase.co/email-events` | Hard/soft bounce |
| complained | `https://<project>.functions.supabase.co/email-events` | Spam complaint |
| unsubscribed | `https://<project>.functions.supabase.co/email-events` | Unsubscribe request |
| stored | `https://<project>.functions.supabase.co/email-inbound` | Inbound email stored |

**Security**:
- Enable HMAC signature verification (Mailgun signing key)
- Configure IP whitelist (Mailgun webhook IPs only)
- Use HTTPS only

---

## 12. EE Parity Checklist

- [x] **Event Capture**: All outbound events (delivered, opened, clicked, bounced, complained)
- [x] **Inbound Processing**: Stored emails with metadata
- [x] **Analytics Views**: Message summary, recipient health
- [x] **Webhook Logs**: Full audit trail for troubleshooting
- [x] **Integration Surface**: PostgREST API for dashboards/agents
- [x] **Security**: Service-role only writes, read-only client access
- [ ] **HMAC Verification**: Implement full Mailgun signature validation (stubbed)
- [ ] **RLS Policies**: Row-level security for multi-tenant scenarios (optional)
- [ ] **Inbound Routing**: Connect to Odoo Helpdesk/ticketing (optional)
- [ ] **Superset Dashboards**: Pre-built email analytics dashboards (optional)

---

## 13. Related Documentation

- **Mailgun Bridge**: `sandbox/dev/addons/ipai_mailgun_bridge/`
- **Canonical DNS**: `docs/infra/CANONICAL_DNS_INSIGHTPULSEAI.md`
- **Odoo Pack**: `docs/infra/CANONICAL_ODOO_PACK.md`
- **Agent Skills**: `docs/agents/ODOO_CLOUD_DEVOPS_AGENT_SKILLS.md`
