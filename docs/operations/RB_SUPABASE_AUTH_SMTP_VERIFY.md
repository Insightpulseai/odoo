# Runbook: Verify Supabase Auth → Zoho SMTP

> **Goal**: Confirm that Supabase Auth sends invitation/reset emails via Zoho SMTP,
> with no Odoo involvement, and that delivery can be proven without logging secrets.
>
> Contract: `docs/contracts/SUPABASE_AUTH_SMTP_CONTRACT.md`
> Last updated: 2026-02-21

---

## Prerequisites

- Supabase project ref: `spdtwktxdalcfigzeqrz`
- Supabase CLI authenticated (`supabase login`)
- `SUPABASE_SERVICE_ROLE_KEY` in environment (for Admin API call)
- Test recipient email address you control

---

## Step 1 — Confirm SMTP config is present (non-secret values)

```bash
# Print only non-sensitive Auth config values
supabase auth config get --project-ref spdtwktxdalcfigzeqrz 2>/dev/null \
  | grep -E "(smtp_host|smtp_port|smtp_sender_name|smtp_admin_email)" \
  | grep -v "password\|secret\|key"
```

**Expected output** (values, not secrets):
```
smtp_host: smtppro.zoho.com
smtp_port: 587
smtp_sender_name: InsightPulse AI
smtp_admin_email: noreply@insightpulseai.com
```

If `smtp_host` is empty, the default Supabase SMTP provider is active — Zoho is not yet configured.

---

## Step 2 — Send a test invite via Admin API (no UI)

```bash
# Invite a test user — triggers auth invite email via configured SMTP
curl -s -X POST \
  "https://spdtwktxdalcfigzeqrz.supabase.co/auth/v1/admin/users" \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "YOUR_TEST_EMAIL@example.com",
    "invite": true,
    "email_confirm": false
  }' | python3 -m json.tool | grep -E '"id"|"email"|"invited_at"'
```

**Expected output** (no sensitive fields logged):
```json
"id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
"email": "your_test@example.com",
"invited_at": "2026-02-21T..."
```

---

## Step 3 — Verify delivery via email headers

Check the received email. Verify:

1. **From address**: `noreply@insightpulseai.com` (or configured sender)
2. **Received header**: contains `smtppro.zoho.com`
   ```
   Received: from smtppro.zoho.com (smtppro.zoho.com [xxx.xxx.xxx.xxx])
   ```
3. **SPF**: `spf=pass`
4. **DKIM**: `dkim=pass` with Zoho selector
5. **No Odoo headers**: must not contain `X-Odoo-*` headers

If `smtppro.zoho.com` does not appear in `Received:`, email went through default Supabase provider — reconfigure SMTP.

---

## Step 4 — Confirm Odoo is not involved

```bash
# Check Odoo container logs for any outbound mail activity during the test period
ssh root@178.128.112.214 \
  "docker logs odoo-prod --since 5m 2>&1 | grep -iE 'mail|smtp|invitation|invite' | head -20"
```

**Expected**: zero lines — Odoo should be silent for auth invite flows.

If lines appear, an Odoo module is incorrectly triggering email on user creation. Investigate `res.users` create hooks.

---

## Step 5 — Record evidence

Capture the verification outputs to a timestamped evidence bundle:

```bash
STAMP=$(date +"%Y%m%d-%H%M%S")
EVIDENCE_DIR="web/docs/evidence/${STAMP}+0800/supabase-auth-smtp/logs"
mkdir -p "$EVIDENCE_DIR"

# Config check (non-sensitive)
supabase auth config get --project-ref spdtwktxdalcfigzeqrz 2>/dev/null \
  | grep -E "(smtp_host|smtp_port|smtp_sender)" \
  > "$EVIDENCE_DIR/smtp_config_check.log"

echo "PASS: Evidence saved to $EVIDENCE_DIR"
```

---

## Checklist

- [ ] `smtp_host` = `smtppro.zoho.com` (confirmed via CLI)
- [ ] `smtp_port` = `587` or `465`
- [ ] Test invite email received within 60 seconds
- [ ] Email `Received:` header shows `smtppro.zoho.com`
- [ ] SPF pass, DKIM pass
- [ ] Odoo container logs show zero mail activity
- [ ] Evidence log saved to timestamped bundle

---

## Rollback

If Zoho SMTP fails during the test:

1. Temporarily clear the SMTP config in Supabase Auth settings to fall back to default provider.
2. Test invite delivery with default provider to confirm the issue is Zoho-specific.
3. Check app password expiry, SPF, DKIM, and Zoho App Password permissions.
4. Reconfigure Zoho SMTP once root cause is identified.

**Do not route auth invites through Odoo as a workaround** — see `SUPABASE_AUTH_SMTP_CONTRACT.md §7`.
