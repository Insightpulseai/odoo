# Odoo Settings Contract

> **Contract ID**: C-15
> **SSOT**: `config/odoo/settings.yaml` + `config/odoo/desired_modules.yml`
> **Applier**: `scripts/odoo/apply_settings.py`
> **Status**: ✅ Active
> **Created**: 2026-02-21

---

## 1. Purpose

Odoo settings drift silently. A checkbox toggled in the UI does not appear in git.
This contract defines which settings are managed as code, which are forbidden from code,
and how violations are detected.

---

## 2. Settings Taxonomy

| Bucket | Storage | SSOT file | Applier |
|--------|---------|-----------|---------|
| **Config parameters** (`ir.config_parameter`) | Odoo DB | `config/odoo/settings.yaml` | `apply_settings.py` |
| **Mail servers** (`ir.mail_server` / `fetchmail.server`) | Odoo DB | `config/odoo/mail_settings.yaml` | `apply_mail_settings.py` |
| **Module install state** | Odoo DB | `config/odoo/desired_modules.yml` | `install-ce-apps.sh` (CI) |
| **Identity / auth** (invites, OTP, MFA) | Supabase Auth | `supabase/config.toml` + Vault | Supabase CLI |

### Not managed here

| Setting type | Why excluded |
|-------------|-------------|
| Secrets (SMTP passwords, API keys) | Never in YAML — use container env vars |
| Module toggles (checkboxes that install modules) | Use `desired_modules.yml` |
| User-specific preferences | Not a platform concern |
| Enterprise / IAP / OdooSh features | CE-only stack; these don't exist |

---

## 3. Invariants

1. **`auth_signup.invitation_scope = "b2b"`** — Odoo MUST be set to "On invitation". Supabase Auth owns the invite flow; Odoo is a relying party.
2. **`web.base.url = "https://erp.insightpulseai.com"`** — Must match `infra/dns/subdomain-registry.yaml`. Frozen via `web.base.url.freeze = True`.
3. **No free signup** — `auth_signup.allow_uninvited = False`. Supabase handles onboarding.
4. **No secrets in settings.yaml** — Any key whose value contains a token, password, or key is a violation.

---

## 4. Managed Config Parameters

| Key | Value | Rationale |
|-----|-------|-----------|
| `auth_signup.invitation_scope` | `b2b` | Odoo is relying party; Supabase sends invites |
| `auth_signup.allow_uninvited` | `False` | No free signup |
| `auth_signup.reset_password` | `True` | Fallback for service accounts |
| `base_import.import_enabled` | `True` | Enable CSV/XLSX import in list views |
| `web.base.url` | `https://erp.insightpulseai.com` | Must match DNS SSOT |
| `web.base.url.freeze` | `True` | Prevent Odoo from auto-updating URL |
| `default_user_tz` | `Asia/Manila` | All users default to PH timezone |
| `lang` | `en_PH` | Philippine English |
| `discuss.discuss.disable_odoobot` | `True` | AI Copilot replaces OdooBot |

---

## 5. Forbidden Config Parameters (never managed here)

| Key | Reason |
|-----|--------|
| `mail.catchall.domain` | Managed by `apply_mail_settings.py` |
| `mail.default.from` | Same |
| `database.secret` | Security — never touch |
| Any `*password*` or `*token*` key | Secrets must not be in YAML |

---

## 6. Apply Procedure

```bash
# Dry run (shows what would change, exits 2 if diff)
ODOO_URL=https://erp.insightpulseai.com \
ODOO_DB=odoo_prod \
ODOO_ADMIN_PASSWORD=$ODOO_ADMIN_PASSWORD \
python scripts/odoo/apply_settings.py --dry-run

# Apply
ODOO_URL=https://erp.insightpulseai.com \
ODOO_DB=odoo_prod \
ODOO_ADMIN_PASSWORD=$ODOO_ADMIN_PASSWORD \
python scripts/odoo/apply_settings.py

# Verify only (no writes)
python scripts/odoo/apply_settings.py --verify-only
```

---

## 7. Drift Detection

Add to CI (`scripts/ci/check_settings_ssot_drift.sh`):

```bash
#!/usr/bin/env bash
set -euo pipefail
# Fail if settings.yaml contains a literal secret (not a ${VAR} placeholder)
if grep -E '(password|token|key|secret)\s*:\s*[^$"{]' config/odoo/settings.yaml; then
  echo "ERROR: settings.yaml contains a potential secret (not an env-var reference)"
  exit 1
fi
echo "✓ settings.yaml secret scan passed"
```

CI workflow path: `.github/workflows/odoo-settings-guard.yml` (pending creation).

---

## 8. Relationship to Supabase Auth SSOT

```
Supabase Auth (IdP / SSOT for identity)
    │  sends invite email via Zoho
    │  generates session JWT
    │  provisions Odoo user on demand (via hook)
    ▼
Odoo (SOR for ERP data; relying party for identity)
    auth_signup.invitation_scope = "b2b"   ← config/odoo/settings.yaml
    auth_signup.allow_uninvited = False     ← same
    (no invite emails sent from Odoo)
```

Digest emails, template rendering, and invitations should be generated from Supabase
`ops.*` tables and sent via the Zoho bridge Edge Function — not via Odoo's mail queue.
See `docs/architecture/SSOT_BOUNDARIES.md §1` for the full identity boundary rules.

---

## 9. Related Contracts

| Contract | Relationship |
|----------|-------------|
| [C-02 Outbound Mail Bridge](MAIL_BRIDGE_CONTRACT.md) | Bridge sends ERP document mail — not identity |
| [C-10 Supabase Auth SMTP](SUPABASE_AUTH_SMTP_CONTRACT.md) | Supabase sends identity mail via Zoho |
| [C-11 Edge Functions](SUPABASE_EDGE_FUNCTIONS_CONTRACT.md) | Invite + digest generation |
