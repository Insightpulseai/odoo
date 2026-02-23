# Supabase Auth SMTP Contract — Zoho US DC

> **Scope**: All identity lifecycle emails (invitations, password reset, magic links, OTP)
> are sent by **Supabase Auth** via **Zoho SMTP** (US datacenter).
> Odoo is a relying party; it must not send identity emails.
>
> SSOT: `docs/architecture/SSOT_BOUNDARIES.md §1 Identity emails`
> Last updated: 2026-02-21

---

## 1. SMTP Endpoints (Zoho US Datacenter)

| Protocol | Host | Port | Encryption | Notes |
|----------|------|------|------------|-------|
| SMTP | `smtppro.zoho.com` | `587` | STARTTLS | **Preferred** |
| SMTP | `smtppro.zoho.com` | `465` | SSL/TLS | Alternative |

**Never use** `smtp.zoho.com` — that is the global endpoint and will reject auth for US DC accounts.

---

## 2. Required Secrets (names only — values never in Git)

| Secret name | Where stored | What it is |
|------------|-------------|-----------|
| `ZOHO_SMTP_USER` | Supabase Auth SMTP config (project settings) | Full Zoho email address |
| `ZOHO_SMTP_APP_PASSWORD` | Supabase Auth SMTP config (project settings) | App-specific password (not account password) |
| `AUTH_FROM_EMAIL` | Supabase Auth config / `supabase/config.toml` | From address shown in emails |
| `AUTH_FROM_NAME` | Supabase Auth config / `supabase/config.toml` | Display name (e.g. "InsightPulse AI") |

**Generate app password at**: Zoho Mail → Account Settings → Security → App Passwords
**Never use your Zoho account password** — app passwords are revocable and scoped.

---

## 3. Supabase Config Anchors

These values belong in `supabase/config.toml` (non-secret portion only):

```toml
[auth.email]
enable_signup = true
double_confirm_changes = true
enable_confirmations = true

# SMTP settings are runtime-only (Supabase dashboard or CLI secrets).
# Auth email templates are customized in supabase/config.toml under [auth.email.templates]
# if using local dev; production templates are managed via Supabase dashboard.
```

**SMTP host/port/user/password** are set at runtime via the Supabase Auth SMTP settings panel
or `supabase auth config set` CLI — not committed to git.

---

## 4. Redaction Policy

| Value | Log policy |
|-------|-----------|
| SMTP host + port | May be logged (not sensitive) |
| From email address | May be logged |
| SMTP username | May be logged (it is an email address) |
| SMTP password / App password | **NEVER log — redact entirely** |
| Auth JWT / magic link tokens | **NEVER log — these are session credentials** |
| Invite tokens in email bodies | **NEVER log** |

CI scripts may only print: `host`, `port`, `from_email`, `PASS/FAIL`.

---

## 5. Verification Checklist

Verify the Supabase → Zoho SMTP connection is working:

- [ ] Supabase Auth SMTP settings show `smtppro.zoho.com:587` (or `:465`)
- [ ] App password is set (not the Zoho account password)
- [ ] Test invite email is sent via Supabase Auth Admin API or dashboard invite
- [ ] Received email headers show `Received: from smtppro.zoho.com`
- [ ] SPF passes: `mail from:` domain has `include:zoho.com` in SPF record
- [ ] DKIM passes: Zoho DKIM selector present in `infra/dns/zoho_mail_dns.yaml`
- [ ] No Odoo mail server involved in the delivery path

---

## 6. Rollback / Provider Swap

If Zoho SMTP is unavailable, Supabase Auth supports any SMTP provider:

1. In Supabase Auth SMTP settings, replace `smtppro.zoho.com` with alternative host.
2. Update `ZOHO_SMTP_USER` / `ZOHO_SMTP_APP_PASSWORD` with new provider credentials.
3. Test with a manual invite before re-enabling signup.
4. Update this contract with the new provider details.

**Do not route identity emails through Odoo** — Odoo's `ipai_mail_bridge_zoho` is not designed for auth flows.

---

## 7. Out of Scope

| Concern | Who handles it | Where configured |
|---------|---------------|-----------------|
| ERP document email (invoices, POs) | Odoo + `ipai_mail_bridge_zoho` | Container env vars |
| Inbound catchall email | Zoho Mail inbox | Zoho admin panel |
| Marketing / bulk email | Out of scope (not configured) | — |
| n8n notification email | n8n SMTP node | n8n credentials |

---

## 8. Related Docs

- `docs/architecture/SSOT_BOUNDARIES.md` §1 — Identity & Access boundary
- `docs/contracts/DNS_EMAIL_CONTRACT.md` — DNS/SPF/DKIM for `@insightpulseai.com`
- `docs/contracts/MAIL_BRIDGE_CONTRACT.md` — Odoo ERP document email (separate flow)
- `docs/runbooks/RB_SUPABASE_AUTH_SMTP_VERIFY.md` — Step-by-step verification
