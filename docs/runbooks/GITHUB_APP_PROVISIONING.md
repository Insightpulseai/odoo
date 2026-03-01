# GitHub App Provisioning Runbook
# Runbook for provisioning and maintaining the pulser-hub GitHub App.
#
# SSOT:  ssot/github/app-manifest.yaml
# Spec:  spec/github-integrations/prd.md
# Secrets: ssot/secrets/registry.yaml §GitHub App credentials

## Prerequisites

- Org owner access on `Insightpulseai` GitHub org
- Supabase CLI authenticated (`supabase login`)
- macOS Keychain access for local secret storage

---

## Step 1: Create or update the GitHub App

1. Navigate to: `https://github.com/organizations/Insightpulseai/settings/apps`
2. App name: **pulser-hub**
3. Set permissions exactly as declared in `ssot/github/app-manifest.yaml §permissions`
4. Subscribe to events declared in `ssot/github/app-manifest.yaml §events`
5. Set webhook URL:
   ```
   https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/ops-github-webhook-ingest
   ```
6. Generate a webhook secret:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
   Copy value — you will need it in Step 3.
7. Generate a private key (RSA) — save the `.pem` file to macOS Keychain.

---

## Step 2: Record App identity values

From the App settings page, note:
- **App ID** (numeric) → `GITHUB_APP_ID`
- **Client ID** (alphanumeric) → `GITHUB_CLIENT_ID`

These are not secrets (visible in the public URL) but must be registered in SSOT.

---

## Step 3: Store secrets in Supabase Vault

```bash
# Store App ID (not a secret, but tracked for ops-secrets-scan)
supabase secrets set GITHUB_APP_ID=<app_id>

# Store private key (PEM — keep newlines)
PRIVATE_KEY=$(cat ~/path/to/pulser-hub.pem | base64)
supabase secrets set GITHUB_PRIVATE_KEY="$PRIVATE_KEY"

# Store webhook secret
supabase secrets set GITHUB_APP_WEBHOOK_SECRET=<webhook_secret>

# Store client ID
supabase secrets set GITHUB_CLIENT_ID=<client_id>

# Store client secret (only if OAuth is active)
supabase secrets set GITHUB_CLIENT_SECRET=<client_secret>
```

> **Note**: `supabase secrets set` stores in Supabase Vault. Edge Functions
> access them as `Deno.env.get(...)`. Never commit values to git.

---

## Step 4: Deploy the ingest function

```bash
supabase functions deploy ops-github-webhook-ingest
```

Verify it responds correctly:
```bash
# Expect 405 for GET
curl -s -X GET \
  https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/ops-github-webhook-ingest \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY" | jq .
# Expected: {"error":"Method Not Allowed"}
```

---

## Step 5: Install the App on the repo

1. Navigate to: `https://github.com/settings/apps/pulser-hub/installations`
2. Install on `Insightpulseai/odoo`
3. Note the **Installation ID** (from the URL after redirect)
4. Store it:
   ```bash
   supabase secrets set GITHUB_APP_INSTALLATION_ID=<installation_id>
   ```

---

## Step 6: Verify signature verification is active

Send a test ping from the GitHub App settings page and check Supabase function logs:
```bash
supabase functions logs ops-github-webhook-ingest --tail 20
```

Expected log (successful delivery):
```
ops-github-webhook-ingest: stored delivery=<uuid> event=ping status=unhandled
```

Signature failure would log:
```
ops-github-webhook-ingest: invalid signature delivery=<uuid> event=ping
```

---

## Rotation

### Private key rotation

1. In GitHub App settings: generate a new key (do **not** delete the old one yet)
2. Update Supabase Vault: `supabase secrets set GITHUB_PRIVATE_KEY=<new_pem>`
3. Verify `github-app-auth` can mint tokens with the new key
4. Delete the old key from GitHub App settings

### Webhook secret rotation

1. Generate new secret: `python3 -c "import secrets; print(secrets.token_hex(32))"`
2. Update Supabase Vault: `supabase secrets set GITHUB_APP_WEBHOOK_SECRET=<new_secret>`
3. Update webhook secret in GitHub App settings (same page as Step 1)
4. Verify incoming webhooks pass signature check (check function logs)

---

## Least-privilege checklist

Before expanding permissions, verify it is required by a specific integration:
- [ ] Check `spec/github-integrations/prd.md §Permissions Matrix`
- [ ] Open a PR that adds the permission row to the table
- [ ] Only then update the App settings and re-deploy

Permissions never needed:
- `administration` (org admin operations)
- `members` (org membership management)
- `emails` (user email access)
- `secrets` (repository secrets — use Supabase Vault instead)
