# C-MAIL-01 — Mail Catcher Contract (Odoo.sh Parity)

> **Contract ID**: C-MAIL-01
> **Status**: Planned
> **Owner**: Platform Engineering
> **Last Updated**: 2026-03-01

---

## 1. Scope

This contract governs outbound mail routing policy and the mail catcher
infrastructure for non-production environments (STAGE, DEV).

---

## 2. Outbound Mail Policy

| Environment | Policy | SMTP Host | Port | Credentials |
|-------------|--------|-----------|------|-------------|
| PROD | Transactional mail | `smtp.mailgun.org` | 587 | prod Mailgun creds |
| STAGE | **Catcher required** | `smtp.mailgun.org` | 2525 | non-prod creds only |
| DEV | **Catcher required** | `smtp.mailgun.org` | 2525 | non-prod creds only |

**Forbidden** (enforced by CI gate):
- `SMTP_PORT = 25` in any environment (blocked by most cloud providers)
- STAGE/DEV environments referencing production Mailgun credentials
- STAGE/DEV sending to real recipient addresses without catcher routing

---

## 3. Evidence Requirements

Every captured mail event **MUST** have the following fields in `ops.mail_events`:

| Field | Type | Required |
|-------|------|----------|
| `env` | `prod\|stage\|dev` | ✅ |
| `provider` | `mailgun` | ✅ |
| `message_id` | string | ✅ |
| `subject` | string | ✅ |
| `sender` | string | ✅ |
| `recipient` | string | ✅ |
| `transport` | e.g. `smtp.mailgun.org:2525` | ✅ |
| `stamp` | ISO8601 or timestamptz | ✅ |
| `received_at` | timestamptz | ✅ |
| `raw` | jsonb (Mailgun webhook payload) | ✅ |

Evidence anchor (confirmed working): subject `E2E-MAILGUN-ODOO-TEXT`,
transport `smtp.mailgun.org:2525`, from `no-reply@mg.insightpulseai.com`.

---

## 4. Webhook Ingest Requirements

The `ops-mailgun-ingest` Edge Function **MUST**:

1. Verify the Mailgun webhook HMAC signature (using `mailgun_signing_key` from Vault).
2. Reject requests with invalid signatures → `{ ok: false, error: "invalid signature" }`.
3. Normalize the payload to `ops.mail_events` schema.
4. Upsert (dedupe on `message_id`).
5. Return `{ ok: true }` on success — always JSON, never `204`.

---

## 5. CI Policy Gate

Gate validates:

```bash
# STAGE/DEV config must route to catcher
SMTP_HOST != "smtp.mailgun.org" → FAIL "non-catcher SMTP in non-prod"
SMTP_PORT == "25"               → FAIL "port 25 forbidden"
SMTP_USER references PROD_CREDS → FAIL "prod creds in non-prod"
```

Gate runs on PR and push to `main`.

---

## 6. SSOT References

| Resource | Path |
|----------|------|
| Mailgun config | `ssot/integrations/mailgun.yaml` |
| Secret names | `ssot/secrets/registry.yaml → mailgun_*` |
| Edge Function | `supabase/functions/ops-mailgun-ingest/` |
| Database table | `ops.mail_events` |
| Parity contract | `docs/contracts/C-ODOOS-01-parity.md` |

---

## 7. Change Process

Updates require PR with changes to this file + `ssot/integrations/mailgun.yaml` + corresponding spec tasks.
