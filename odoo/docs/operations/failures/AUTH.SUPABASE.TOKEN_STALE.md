# Supabase Management Token Stale/Expired

**Failure code**: `AUTH.SUPABASE.TOKEN_STALE`
**Severity**: critical
**CI behavior**: blocking
**SSOT**: `ssot/errors/failure_modes.yaml`
**Convergence kind**: `token_stale` on target `Supabase Access Token`

---

## What it means

The `SUPABASE_ACCESS_TOKEN` used by CI and the convergence scan has expired or been
revoked. Tokens expire after 90 days. Affected operations:
- `supabase db push` (migrations fail with 401)
- `supabase functions deploy` (fails with 401)
- `ops-convergence-scan` token health check emits a `token_stale` finding

---

## Verify the token is stale

```bash
curl -s https://api.supabase.com/v1/projects \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  | jq '.[0].id // "AUTH_FAILED"'
```

Expected if valid: project ID string (e.g., `"spdtwktxdalcfigzeqrz"`)
Expected if stale: `"AUTH_FAILED"` or HTTP 401 body

---

## Fix steps

### Step 1 — Generate a new token

Go to Supabase Dashboard:
- Account → Access Tokens → Generate new token
- Name: `ipai-ci-<YYYYMM>` (include month for rotation tracking)
- Copy the token value immediately (shown once only)

### Step 2 — Update GitHub secret

```bash
gh secret set SUPABASE_ACCESS_TOKEN --repo Insightpulseai/odoo
# Paste the new token value when prompted
```

### Step 3 — Update local keychain

```bash
# macOS
security add-generic-password -s "supabase-access-token" -a ipai -w "<new-token>" -U
# Or update ~/.zshrc / ~/.env.local directly (never commit the value)
```

### Step 4 — Verify the new token works

```bash
export SUPABASE_ACCESS_TOKEN="<new-token>"
curl -s https://api.supabase.com/v1/projects \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  | jq '.[0].id'
# Must return: "spdtwktxdalcfigzeqrz"
```

### Step 5 — Run any pending migrations

```bash
supabase db push --project-ref spdtwktxdalcfigzeqrz
```

### Step 6 — Redeploy any affected functions

```bash
supabase functions deploy ops-convergence-scan --project-ref spdtwktxdalcfigzeqrz
```

---

## Prevention

Set a calendar reminder 2 weeks before the 90-day expiry. Token creation date is
visible in Supabase Dashboard → Account → Access Tokens.

The convergence scan will emit a `token_stale` finding when it detects a 401
from the Supabase management API, providing early warning before CI breaks.

---

## Related files

- `ssot/errors/failure_modes.yaml` (entry: `AUTH.SUPABASE.TOKEN_STALE`)
- `ssot/secrets/registry.yaml` (secret: `SUPABASE_ACCESS_TOKEN`)
- `supabase/functions/ops-convergence-scan/index.ts` (token health check)
