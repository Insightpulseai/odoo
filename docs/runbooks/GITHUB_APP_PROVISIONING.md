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

The function reads `GITHUB_APP_WEBHOOK_SECRET` from Supabase Vault (set in Step 3).
If the secret is absent the function logs a warning and processes the request without
signature verification — acceptable during initial setup, **not** in production.

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

### Stored event shape

All accepted deliveries are stored in `ops.webhook_events`. Key columns added by
migration `20260302000050`:

| Column | Description |
|--------|-------------|
| `delivery_id` | `X-GitHub-Delivery` UUID — deduplicated by unique index |
| `action` | event sub-action (opened / closed / merged / …) |
| `repo_full_name` | `org/repo` extracted from payload |
| `installation_id` | GitHub App installation ID |
| `sender_login` | GitHub login who triggered the event |
| `reason` | structured reason for `status=unhandled`: `unknown_event`, `missing_action`, `payload_too_large`, `schema_mismatch` |

Supported events that produce `status=queued`: `issues`, `pull_request`,
`check_run`, `check_suite`, `push`, `installation`.

All other events are stored with `status=unhandled` and a `reason` code; they are
**not** dropped.

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

Expected log (successful delivery — ping is `unhandled` because it is not a subscribed event):
```
ops-github-webhook-ingest: payload_too_large delivery=<uuid> size=<n>   # if oversized
ops-github-webhook-ingest: invalid signature delivery=<uuid> event=ping  # sig failure
```

A successful ingest does not emit a log line — inspect `ops.webhook_events` directly:
```sql
SELECT delivery_id, event_type, status, reason, received_at
FROM ops.webhook_events
WHERE integration = 'github'
ORDER BY received_at DESC
LIMIT 10;
```

Signature failure blocks storage and returns HTTP 401. All other events
(including unsupported ones) are stored and queryable.

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
