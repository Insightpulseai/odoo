# Secrets Inventory — InsightPulse AI (insightpulseai/odoo)

**SSOT source**: [`ssot/secrets/inventory.yaml`](../../ssot/secrets/inventory.yaml)
**Registry**: [`ssot/secrets/registry.yaml`](../../ssot/secrets/registry.yaml)
**Runbook**: [`docs/runbooks/SECRETS_SSOT.md`](../runbooks/SECRETS_SSOT.md)
**Last generated**: 2026-03-02
**Validator**: `python scripts/ci/check_secrets_ssot.py --check-inventory`

> **NEVER print secret values.** All entries reference identifiers only.

---

## Status Summary

| Metric | Count |
|--------|-------|
| Total tracked secrets | 84 |
| **working** (confirmed) | 13 |
| **stale** (confirmed broken) | 2 |
| **missing** | 0 |
| **unknown** (no test this cycle) | 69 |
| **rotate_now = true** | 2 |

### Immediate Action Required

| ID | Status | rotate_now | Reason |
|----|--------|-----------|--------|
| `supabase_management_token` | stale | **YES** | HTTP 401 from management API — blocks edge fn deployment |
| `supabase_access_token` | stale | **YES** | Same token, same failure — blocks CI |

> **Unblock**: Generate new token at `https://app.supabase.com/account/tokens`,
> then update GitHub Actions secret `SUPABASE_ACCESS_TOKEN`.

---

## Full Inventory Table

| ID | Type | Environments | Status | rotate_now | Evidence Kind | Last Checked |
|----|------|-------------|--------|-----------|--------------|-------------|
| `cf_dns_read_token` | API token | prod, ci | unknown | no | — | — |
| `cf_dns_edit_token` | API token | prod, ci | unknown | no | — | — |
| `cloudflare_global_api_key` | API key | prod | unknown | no | — | — |
| `cloudflare_zone_id` | Zone ID | prod | working | no | session_log | 2026-03-02 |
| `cloudflare_api_token` | API token | prod | unknown | no | — | — |
| `zoho_client_id` | OAuth client ID | prod | unknown | no | — | — |
| `zoho_client_secret` | OAuth secret | prod | unknown | no | — | — |
| `zoho_refresh_token` | OAuth refresh | prod | unknown | no | — | — |
| `zoho_smtp_user` | SMTP username | dev, prod | working | no | session_log | 2026-03-02 |
| `zoho_smtp_app_password` | SMTP password | dev, prod | working | no | session_log | 2026-03-02 |
| `zoho_mail_smtp_password` | SMTP password | prod | working | no | session_log | 2026-03-02 |
| `supabase_service_role_key` | Service role key | dev, prod, ci | unknown | no | — | — |
| `supabase_anon_key` | Anon key | dev, prod | unknown | no | — | — |
| `supabase_management_token` | Management API token | prod, ci | **stale** | **YES** | api_call | 2026-03-02 |
| `supabase_access_token` | Management API token | prod, ci | **stale** | **YES** | api_call | 2026-03-02 |
| `supabase_jwt_secret` | JWT secret | prod | unknown | no | — | — |
| `gemini_api_key` | AI API key | prod | unknown | no | — | — |
| `anthropic_api_key` | AI API key | prod | unknown | no | — | — |
| `openai_api_key` | AI API key | prod | unknown | no | — | — |
| `llm_bridge_webhook_secret` | Webhook HMAC | prod | unknown | no | — | — |
| `vercel_ai_gateway_api_key` | API key | prod | unknown | no | — | — |
| `slack_bot_token` | Bot token | prod | unknown | no | — | — |
| `slack_signing_secret` | Signing secret | prod | unknown | no | — | — |
| `github_token` | PAT | dev, ci | working | no | session_log | 2026-03-02 |
| `github_pat_admin` | PAT (admin) | dev, ci | working | no | session_log | 2026-03-02 |
| `github_pat_projects_token` | PAT | ci | unknown | no | — | — |
| `github_pat_superset` | PAT | ci | unknown | no | — | — |
| `github_token_vercel_diff` | PAT | ci | unknown | no | — | — |
| `github_webhook_secret` | Webhook HMAC | prod | unknown | no | — | — |
| `github_app_id` | App ID | prod | unknown | no | — | — |
| `github_app_private_key` | PEM private key | prod, ci | unknown | no | — | — |
| `github_app_client_id` | OAuth client ID | prod | unknown | no | — | — |
| `github_app_client_secret` | OAuth secret | prod | unknown | no | — | — |
| `github_app_webhook_secret` | Webhook HMAC | prod | unknown | no | — | — |
| `github_app_id_n8n` | App ID | prod | unknown | no | — | — |
| `github_app_private_key_n8n` | PEM private key | prod | unknown | no | — | — |
| `github_app_webhook_secret_n8n` | Webhook HMAC | prod | unknown | no | — | — |
| `github_app_id_plane` | App ID | prod | unknown | no | — | — |
| `github_app_webhook_secret_plane` | Webhook HMAC | prod | unknown | no | — | — |
| `github_app_ipai_integrations` | App config | prod | unknown | no | — | — |
| `github_cli_auth` | PAT | dev | working | no | session_log | 2026-03-02 |
| `do_access_token` | API token | dev, prod, ci | working | no | ssh_session | 2026-03-02 |
| `digitalocean_api_token` | API token | prod, ci | working | no | session_log | 2026-03-02 |
| `digitalocean_access_token` | API token | prod, ci | unknown | no | — | — |
| `digitalocean_api_token_genai` | Scoped API token | prod | unknown | no | — | — |
| `gradient_model_access_key` | AI model key | prod | unknown | no | — | — |
| `mailgun_api_key` | API key | prod | working | no | api_call | 2026-03-02 |
| `mailgun_signing_key` | Webhook HMAC | prod | unknown | no | — | — |
| `mailgun_smtp_password` | SMTP password | prod | unknown | no | — | — |
| `odoo_mailgun_smtp_password` | SMTP password | prod | working | no | psql_query | 2026-03-02 |
| `stripe_secret_key` | API key | prod | unknown | no | — | — |
| `stripe_webhook_signing_secret` | Webhook secret | prod | unknown | no | — | — |
| `stripe_publishable_key` | Public key | prod | unknown | no | — | — |
| `plane_api_key` | API key | prod | unknown | no | — | — |
| `plane_oauth_client_id` | OAuth client ID | prod | unknown | no | — | — |
| `plane_oauth_client_secret` | OAuth secret | prod | unknown | no | — | — |
| `plane_workspace_id` | Workspace ID | prod | unknown | no | — | — |
| `plane_slack_client_id` | OAuth client ID | prod | unknown | no | — | — |
| `plane_slack_client_secret` | OAuth secret | prod | unknown | no | — | — |
| `plane_webhook_secret` | Webhook HMAC | prod | unknown | no | — | — |
| `n8n_api_key` | API key | prod | unknown | no | — | — |
| `n8n_webhook_secret` | Webhook secret | prod | unknown | no | — | — |
| `n8n_webhook_github_url` | Webhook URL | prod | unknown | no | — | — |
| `vercel_token` | API token | prod, ci | unknown | no | — | — |
| `figma_oauth_client_id` | OAuth client ID | prod | unknown | no | — | — |
| `figma_oauth_client_secret` | OAuth secret | prod | unknown | no | — | — |
| `figma_personal_access_token` | PAT | prod, ci | unknown | no | — | — |
| `figma_webhook_secret` | Webhook HMAC | prod | unknown | no | — | — |
| `cron_secret` | Internal token | prod | unknown | no | — | — |
| `ocr_bridge_token` | Bridge token | prod | unknown | no | — | — |
| `autonoma_oauth_client_id` | OAuth client ID | prod | unknown | no | — | — |
| `autonoma_oauth_client_secret` | OAuth secret | prod | unknown | no | — | — |
| `prod_ssh_key` | SSH private key | prod, ci | working | no | ssh_session | 2026-03-02 |
| `prod_ssh_host` | SSH host IP | prod, ci | working | no | ssh_session | 2026-03-02 |
| `odoo_db_password` | DB password | dev, prod | unknown | no | — | — |
| `azure_ad_client_secret` | OAuth secret | prod | unknown | no | — | — |
| `azure_ad_tenant_id` | Tenant ID | prod | unknown | no | — | — |
| `sentry_auth_token` | API token | prod | unknown | no | — | — |
| `google_client_secret` | OAuth secret | ci | unknown | no | — | — |
| `google_client_id` | OAuth client ID | ci | unknown | no | — | — |
| `mcp_remote_token` | Internal token | prod | unknown | no | — | — |
| `mcp_local_api_key` | Internal key | dev, prod | unknown | no | — | — |
| `seed_run_token` | Seed auth token | dev, prod | unknown | no | — | — |
| `databricks_token` | API token | prod, ci | unknown | no | — | — |
| `databricks_host` | Workspace URL | prod, ci | unknown | no | — | — |

---

## Registry Quality Issues

These issues exist in `ssot/secrets/registry.yaml` and should be resolved in a follow-up:

| Issue | Affected Keys |
|-------|--------------|
| **Duplicate YAML keys** (later entry silently overwrites earlier) | `supabase_service_role_key` (×2), `supabase_anon_key` (×2), `slack_bot_token` (×2), `slack_signing_secret` (×2), `plane_webhook_secret` (×2), `vercel_token` (×3), `mailgun_api_key` (×2), `github_webhook_secret` (×2) |
| **Not in registry** (found in code scan, added in this PR) | `prod_ssh_key`, `prod_ssh_host`, `odoo_db_password`, `supabase_jwt_secret`, `azure_ad_client_secret`, `azure_ad_tenant_id`, `sentry_auth_token`, `google_client_secret`, `google_client_id`, `mcp_remote_token`, `mcp_local_api_key`, `seed_run_token`, `databricks_token`, `databricks_host` |

---

## How to Verify

Run these commands to check each integration. **No UI steps.**

```bash
# ── Supabase access token (should return project list, not 401) ──
curl -sf -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  https://api.supabase.com/v1/projects | jq '.[0].id'
# PASS: returns project ref   FAIL: returns {"message":"..."} or empty

# ── Mailgun API key ──
curl -sf -u "api:$MAILGUN_API_KEY" \
  "https://api.mailgun.net/v3/domains/mg.insightpulseai.com" | jq '.domain.state'
# PASS: "active"

# ── GitHub token (PAT) ──
gh api /user --jq '.login'
# PASS: returns GitHub username

# ── DigitalOcean token ──
doctl account get --format Email --no-header
# PASS: returns account email

# ── SSH to prod droplet ──
ssh -o ConnectTimeout=10 -o BatchMode=yes root@178.128.112.214 exit
echo "exit code: $?"
# PASS: exit code 0

# ── Cloudflare DNS read token ──
curl -sf -H "Authorization: Bearer $CF_DNS_READ_TOKEN" \
  "https://api.cloudflare.com/client/v4/user/tokens/verify" | jq '.result.status'
# PASS: "active"

# ── Slack bot token ──
curl -sf -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  "https://slack.com/api/auth.test" | jq '.ok'
# PASS: true

# ── Anthropic API key ──
curl -sf -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  "https://api.anthropic.com/v1/models" | jq '.models[0].id'
# PASS: returns model ID

# ── OpenAI API key ──
curl -sf -H "Authorization: Bearer $OPENAI_API_KEY" \
  "https://api.openai.com/v1/models" | jq '.data[0].id'
# PASS: returns model ID

# ── Zoho SMTP app password (test connection) ──
openssl s_client -connect smtppro.zoho.com:587 -starttls smtp \
  -crlf -quiet 2>&1 | head -5
# PASS: "220 ... ESMTP"

# ── n8n API key ──
curl -sf -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "https://n8n.insightpulseai.com/api/v1/workflows?limit=1" | jq '.data | length'
# PASS: returns number (0 or more)

# ── Plane API key ──
curl -sf -H "x-api-key: $PLANE_API_KEY" \
  "https://api.plane.so/api/v1/workspaces/" | jq '.[0].slug'
# PASS: returns workspace slug

# ── Vercel token ──
curl -sf -H "Authorization: Bearer $VERCEL_TOKEN" \
  "https://api.vercel.com/v2/user" | jq '.user.username'
# PASS: returns username

# ── Stripe secret key ──
curl -sf -u "$STRIPE_SECRET_KEY:" \
  "https://api.stripe.com/v1/balance" | jq '.object'
# PASS: "balance"
```

---

## How to Rotate

> All rotations follow the same pattern: generate new → store → update consumers → verify → remove old.
> **No UI navigation steps.** Platform-specific console URLs are listed as references only.

### Supabase Access Token (rotate_now=TRUE)

```bash
# 1. Generate new token
#    Dashboard: https://app.supabase.com/account/tokens
#    No CLI equivalent — must generate in Supabase dashboard.

# 2. Update GitHub Actions secret
gh secret set SUPABASE_ACCESS_TOKEN --body "$(cat ~/.supabase/access-token)"
# Or if manually obtained:
# gh secret set SUPABASE_ACCESS_TOKEN

# 3. Update local CLI token
supabase login  # stores in ~/.supabase/access-token

# 4. Verify
curl -sf -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  https://api.supabase.com/v1/projects | jq '.[0].id'
```

### GitHub PAT (quarterly rotation)

```bash
# 1. Generate new token
#    Dashboard: https://github.com/settings/tokens (classic) or fine-grained
#    gh auth login  # can also generate via CLI

# 2. Store in macOS Keychain
security add-generic-password -s "github-pat-admin" -a "jgtolentino" -w

# 3. Update gh CLI auth
gh auth login --with-token < <(security find-generic-password -s "github-pat-admin" -a "jgtolentino" -w)

# 4. Update GitHub Actions secret if used in CI
gh secret set GITHUB_TOKEN --body "$(security find-generic-password -s github-pat-admin -a jgtolentino -w)"
```

### Mailgun API Key

```bash
# 1. Generate new key
#    Dashboard: https://app.mailgun.com/settings/api_security
#    Mailgun CLI (if available): mailgun domain list

# 2. Store in macOS Keychain
security add-generic-password -s "mailgun-api-key" -a "insightpulseai" -w

# 3. Update environment
export MAILGUN_API_KEY="$(security find-generic-password -s mailgun-api-key -a insightpulseai -w)"

# 4. Verify
curl -sf -u "api:$MAILGUN_API_KEY" \
  "https://api.mailgun.net/v3/domains/mg.insightpulseai.com" | jq '.domain.state'
```

### Zoho SMTP App Password

```bash
# 1. Generate new app password
#    Zoho: https://accounts.zoho.com/u/h#security/app_password
#    Create new password for "Odoo Mail"

# 2. Update Odoo ir.mail_server via psql on prod
ssh root@178.128.112.214
docker exec -i odoo-postgres-1 psql -U odoo -d odoo << 'SQL'
UPDATE ir_mail_server
SET smtp_pass = 'NEW_APP_PASSWORD_HERE'
WHERE smtp_host ILIKE '%zoho%';
SQL

# 3. Restart Odoo to pick up new value
docker restart odoo-prod

# 4. Verify (check Odoo mail logs or trigger test email)
docker logs odoo-prod --tail 50 | grep -i "smtp\|mail"
```

### DigitalOcean API Token

```bash
# 1. Generate new token
#    Dashboard: https://cloud.digitalocean.com/account/api/tokens

# 2. Store in macOS Keychain
security add-generic-password -s "do-api-token" -a "insightpulseai" -w

# 3. Update doctl auth
doctl auth init

# 4. Update GitHub Actions secret
gh secret set DIGITALOCEAN_API_TOKEN --body "$(security find-generic-password -s do-api-token -a insightpulseai -w)"
gh secret set DO_API_TOKEN --body "$(security find-generic-password -s do-api-token -a insightpulseai -w)"

# 5. Verify
doctl account get --format Email
```

### Cloudflare DNS Tokens

```bash
# 1. Generate new tokens at https://dash.cloudflare.com/profile/api-tokens
#    Create two scoped tokens:
#    - DNS:Read for cf_dns_read_token
#    - DNS:Edit for cf_dns_edit_token

# 2. Update GitHub Actions secrets
gh secret set CF_DNS_READ_TOKEN
gh secret set CF_DNS_EDIT_TOKEN

# 3. Verify DNS read token
curl -sf -H "Authorization: Bearer $CF_DNS_READ_TOKEN" \
  "https://api.cloudflare.com/client/v4/user/tokens/verify" | jq '.result.status'
```

### prod_ssh_key (on offboarding)

```bash
# 1. Generate new keypair
ssh-keygen -t ed25519 -C "deploy-prod@insightpulseai.com" -f ~/.ssh/id_prod_deploy

# 2. Add public key to prod droplet
ssh root@178.128.112.214 "cat >> ~/.ssh/authorized_keys" < ~/.ssh/id_prod_deploy.pub

# 3. Verify new key works
ssh -i ~/.ssh/id_prod_deploy root@178.128.112.214 exit

# 4. Update GitHub Actions secret
gh secret set PROD_SSH_KEY < ~/.ssh/id_prod_deploy

# 5. Remove old key from authorized_keys on prod (confirm new key works first)
ssh root@178.128.112.214 "grep -v 'OLD_KEY_COMMENT' ~/.ssh/authorized_keys > /tmp/ak && mv /tmp/ak ~/.ssh/authorized_keys"
```

---

## Known Blockers

### BLOCKER 1: Supabase Edge Functions Not Deployed (HTTP 404)

**Affected functions**: `ops-mailgun-ingest`, `ops-convergence-scan`, `ops-fixbot-dispatch`, `ops-workitems-processor`

**Root cause**: `SUPABASE_ACCESS_TOKEN` is stale (HTTP 401) AND GitHub Actions is locked (billing).

**Resolution**:
1. Renew Supabase access token (see rotation section above)
2. OR resolve GitHub Actions billing lock
3. Then re-run: `.github/workflows/supabase-deploy.yml`

---

## CI Gate

```bash
# Validate registry schema
python scripts/ci/check_secrets_ssot.py
# Expected: exit 0, "N secrets validated"

# Validate inventory schema + registry cross-reference
python scripts/ci/check_secrets_ssot.py --check-inventory
# Expected: exit 0, "inventory valid — N entries checked"

# Full check (registry + inventory)
python scripts/ci/check_secrets_ssot.py && python scripts/ci/check_secrets_ssot.py --check-inventory
```

---

*Auto-generated from `ssot/secrets/inventory.yaml` — do not edit manually.
Edit the YAML source and regenerate this doc if needed.*
