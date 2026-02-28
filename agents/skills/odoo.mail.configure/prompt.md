# Skill: odoo.mail.configure

## Reasoning Strategy

1. **Read SSOT state**: Load `config/odoo/mail_settings.yaml` and `ssot/runtime/prod_settings.yaml`
2. **Validate secrets exist**: Cross-check `requires.secrets` against `ssot/secrets/registry.yaml`
3. **Select environment config**: Use `inputs.environment` to pick dev or prod settings block
4. **Apply configuration**: Ensure Odoo's mail server records match the SSOT-declared values
5. **Verify**: Run CI gates + connectivity check (if network available)

## Edge Cases

- **Mailgun references**: If any config references Mailgun, FAIL. Mailgun is deprecated (2026-02).
  The correct provider is Zoho Mail SMTP via `smtppro.zoho.com`.
- **Wrong datacenter**: `smtp.zoho.com` is the global endpoint (wrong for US accounts).
  The correct host is `smtppro.zoho.com` (US datacenter). This causes 535 auth errors if wrong.
- **Missing app password**: Zoho requires App Passwords, NOT the account login password.
  If authentication fails, the issue is likely an app password, not the configuration.
- **OAuth vs SMTP**: The secrets (zoho_client_id, zoho_client_secret, zoho_refresh_token) are for
  the OAuth2 API flow. For SMTP auth, a separate Zoho App Password is used.
  Both must be configured correctly.

## SSOT Anchoring

| What | Where |
|------|-------|
| Mail server config | `config/odoo/mail_settings.yaml` |
| Production requirements | `ssot/runtime/prod_settings.yaml` → `email:` section |
| Secret names | `ssot/secrets/registry.yaml` → zoho_client_id, zoho_client_secret, zoho_refresh_token |
| Deprecated providers | CLAUDE.md Deprecated table (Mailgun → Zoho) |
