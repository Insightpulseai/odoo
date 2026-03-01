# Supabase ↔ Vercel Integration Health Runbook
#
# SSOT:  ssot/secrets/registry.yaml §Supabase keys
# Spec:  n/a (Vercel marketplace integration)
# Project: spdtwktxdalcfigzeqrz (Supabase) ↔ odooops-console (Vercel)
# Updated: 2026-03-02

## Overview

The Vercel ↔ Supabase integration provides **read-only** access to the Supabase project
`spdtwktxdalcfigzeqrz` from the Vercel `odooops-console` project. Credentials are
auto-injected into Vercel build/runtime as environment variables and must be kept in
sync with the local `~/.zshrc` entries for development.

**Integration type**: Vercel Marketplace (Native Integration)
**Access model**: Read-only — Vercel cannot write to Supabase schema or Vault
**Plan**: Pro

---

## Required Environment Variables

These variables are auto-injected by Vercel once the integration is active.
They must also be stored in `~/.zshrc` for local development.

### App Client Keys (safe in browser bundles)

| Variable | Format | Purpose |
|----------|--------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | `https://<ref>.supabase.co` | PostgREST / Realtime base URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | JWT `eyJhbGci...` | Unauthenticated client access (RLS-gated) |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | `sb_publishable_...` | New-format publishable key |

### Server-Side Keys (never expose to browser)

| Variable | Format | Purpose |
|----------|--------|---------|
| `SUPABASE_SERVICE_ROLE_KEY` | JWT `eyJhbGci...` | Bypasses RLS — server-side only |
| `SUPABASE_JWT_SECRET` | base64 string | JWT verification in Edge Functions |
| `SUPABASE_SECRET_KEY` | `sb_secret_...` | New-format secret key (server-only) |

### Database Connection Strings

| Variable | Purpose |
|----------|---------|
| `POSTGRES_URL` | Pooled connection (port 6543, pgbouncer) — use for serverless |
| `POSTGRES_PRISMA_URL` | Prisma-compatible pooled connection |
| `POSTGRES_URL_NON_POOLING` | Direct connection (port 5432) — use for migrations |
| `POSTGRES_PASSWORD` | Raw DB password (for constructing custom DSNs) |

---

## Health Check Procedure

### 1. Verify integration is active in Vercel

```bash
# List env vars for the project (requires VERCEL_TOKEN)
vercel env ls --environment=production 2>&1 | grep -E 'SUPABASE|POSTGRES'
```

Expected: all 9 variables listed above are present with non-placeholder values.

### 2. Verify Supabase project is reachable

```bash
curl -s \
  -H "apikey: $NEXT_PUBLIC_SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $NEXT_PUBLIC_SUPABASE_ANON_KEY" \
  "$NEXT_PUBLIC_SUPABASE_URL/rest/v1/" | jq '.swagger // "OK: no swagger, REST reachable"'
```

Expected: JSON response (not `{"message":"Invalid API key"}`).

### 3. Verify service role key (server-side)

```bash
curl -s \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  "$SUPABASE_URL/rest/v1/ops.webhook_events?select=count" | jq .
```

Expected: `[{"count": <n>}]` — not an auth error.

### 4. Verify ops schema tables exist

```bash
SUPABASE_PROJECT_REF="spdtwktxdalcfigzeqrz"
curl -s \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  "${SUPABASE_URL}/rest/v1/rpc/get_all_tables" 2>/dev/null || \
psql "$POSTGRES_URL_NON_POOLING" -c "\dt ops.*" 2>&1
```

Expected tables: `ops.webhook_events`, `ops.task_queue`, `ops.platform_events`.

### 5. Verify Supabase CLI auth (separate from Vercel integration)

```bash
supabase projects list
```

If this returns `Unauthorized`, run `supabase login` (browser OAuth).
The Supabase CLI uses a **management API token** (`sbp_...`) independent of project keys.

---

## Troubleshooting

### "Invalid API key" on REST requests

**Cause**: `SUPABASE_ANON_KEY` or `SUPABASE_SERVICE_ROLE_KEY` is stale or from the wrong project.

**Fix**:
1. Log in to Supabase dashboard → Project Settings → API
2. Copy the current `anon public` and `service_role` keys
3. Update `~/.zshrc` and Vercel env vars:
   ```bash
   vercel env rm NEXT_PUBLIC_SUPABASE_ANON_KEY production
   vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
   ```
4. Re-deploy: `vercel deploy --prod`

### Vercel build fails: "supabase url not defined"

**Cause**: `NEXT_PUBLIC_SUPABASE_URL` not set in Vercel environment.

**Fix**:
```bash
vercel env add NEXT_PUBLIC_SUPABASE_URL production
# value: https://spdtwktxdalcfigzeqrz.supabase.co
```

### Database connection timeout in serverless

**Cause**: Using `POSTGRES_URL_NON_POOLING` (port 5432) in a serverless function.

**Fix**: Switch to `POSTGRES_URL` (port 6543, pgbouncer) for serverless routes.
Only use `POSTGRES_URL_NON_POOLING` for migrations (`supabase db push`).

### JWT signature verification fails

**Cause**: `SUPABASE_JWT_SECRET` is stale or mismatched with the project.

**Fix**: Re-generate from Supabase dashboard → Project Settings → API → JWT Settings.
Update in both `~/.zshrc` and Vercel env vars.

---

## Ops Tables Reference

### `ops.webhook_events`

Primary event ingestion table. Columns added by migration `20260302000050`:

| Column | Type | Description |
|--------|------|-------------|
| `delivery_id` | text | `X-GitHub-Delivery` UUID (unique index) |
| `action` | text | Event sub-action (opened, closed, merged, …) |
| `repo_full_name` | text | `org/repo` string |
| `installation_id` | bigint | GitHub App installation ID |
| `sender_login` | text | GitHub user who triggered event |
| `reason` | text | Structured reason for `status=unhandled` |

### `ops.task_queue`

Work items dispatched from webhook events. Append-only.

### `ops.platform_events`

Aggregated platform event log. Append-only.

---

## Edge Functions Consuming Supabase Keys

| Function | Keys Used | Notes |
|----------|-----------|-------|
| `ops-github-webhook-ingest` | `SUPABASE_SERVICE_ROLE_KEY`, `GITHUB_APP_WEBHOOK_SECRET` | Writes to `ops.webhook_events` |
| `ops-ppm-rollup` | `SUPABASE_SERVICE_ROLE_KEY` | Reads/writes task queue |
| `ops-search-query` | `SUPABASE_ANON_KEY` | Read-only search |
| `github-app-auth` | `GITHUB_PRIVATE_KEY`, `GITHUB_CLIENT_ID` | Mints installation tokens |

---

## Key Rotation Procedure

### Rotating project keys (anon / service_role)

> ⚠️ Rotating these invalidates all existing JWT tokens for logged-in users.

1. Supabase dashboard → Project Settings → API → Rotate Keys
2. Note new `anon public` and `service_role` values
3. Update `~/.zshrc`:
   ```bash
   # Replace old values for these keys:
   # SUPABASE_ANON_KEY, NEXT_PUBLIC_SUPABASE_ANON_KEY, VITE_SUPABASE_ANON_KEY
   # SUPABASE_SERVICE_ROLE_KEY
   ```
4. Update Vercel env vars (all environments):
   ```bash
   for env in development preview production; do
     vercel env rm NEXT_PUBLIC_SUPABASE_ANON_KEY $env
     vercel env rm SUPABASE_SERVICE_ROLE_KEY $env
   done
   # Then re-add with new values
   ```
5. Re-deploy ops-console: `vercel deploy --prod`
6. Update `ssot/secrets/registry.yaml` rotation date

### Rotating JWT Secret

Same procedure, but also requires re-deploying all Edge Functions:
```bash
supabase functions deploy --all
```

---

## Syncing Local Dev with Vercel Integration

After Vercel ↔ Supabase integration auto-rotates or updates keys:

```bash
# Pull current Vercel env to local .env.local (gitignored)
vercel env pull apps/ops-console/.env.local
```

This creates `apps/ops-console/.env.local` with current values. Do **not** commit this file.

---

## Related Runbooks

- `docs/runbooks/GITHUB_APP_PROVISIONING.md` — GitHub App webhook + ops.webhook_events
- `docs/runbooks/SECRETS_SSOT.md` — Full secrets management workflow
- `ssot/secrets/registry.yaml` — Secret name registry (no values)
- `ssot/errors/failure_modes.yaml` — Auth failure mode codes
