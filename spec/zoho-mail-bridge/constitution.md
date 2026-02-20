# Constitution — Zoho Mail Bridge

> Non-negotiable governance rules for the Zoho Mail integration bridge.

## Core Rules

1. **No secrets in repo.** Credentials (client_id, client_secret, refresh_token, app_password) live in Supabase Vault or container env vars only. Never in committed files.

2. **Idempotent only.** Every script, migration, and Edge Function must be safe to re-run. Use `CREATE TABLE IF NOT EXISTS`, `UPDATE … WHERE name = …`, etc.

3. **Audit all operations.** Every token mint, email send, and config sync must produce a row in `ops.platform_events`. No silent side effects.

4. **US datacenter endpoints only.** `smtppro.zoho.com:587` (STARTTLS) and `imappro.zoho.com:993` (SSL). Never use global `smtp.zoho.com` / `imap.zoho.com` for `@insightpulseai.com`.

5. **App passwords ≠ account password.** All automated auth must use Zoho Application-Specific Passwords (for SMTP) or OAuth2 access tokens (for API). Never the Zoho account login password.

6. **Config SSOT.** `config/odoo/mail_settings.yaml` is the single source of truth for hostnames, ports, and usernames. Scripts and Terraform read from it — they do not hardcode values.

7. **No silent failures.** Errors in Edge Functions must be logged to `ops.platform_events` and returned to the caller as structured JSON `{ "error": "...", "code": "..." }`.

8. **CE + OCA only.** No Odoo Enterprise modules. Mail integration extends the open `mail` module only via `ipai_zoho_mail`.

9. **Zoho OAuth2 client is manual.** Creation of the OAuth2 client in Zoho API Console requires human login. All automation starts *after* client credentials exist in Vault.

10. **Passwords never in logs.** `apply_mail_settings.py` must mask passwords in all stdout/log output using `****` substitution.
