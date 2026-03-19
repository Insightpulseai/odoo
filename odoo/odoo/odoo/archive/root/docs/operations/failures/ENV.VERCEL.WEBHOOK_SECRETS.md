# Missing Vercel Webhook Secrets (odooops-console)

**Failure code**: `ENV.VERCEL.KEY_MISSING.PLANE_WEBHOOK_SECRET` /
                  `ENV.VERCEL.KEY_MISSING.GITHUB_WEBHOOK_SECRET`
**Severity**: high
**CI behavior**: non-blocking
**SSOT**: `ssot/errors/failure_modes.yaml`
**Convergence kind**: `env_missing`
**Targets**: `PLANE_WEBHOOK_SECRET@vercel:odooops-console`,
             `GITHUB_WEBHOOK_SECRET@vercel:odooops-console`

---

## What it means

The `odooops-console` Vercel project is missing one or both webhook secret environment
variables. When missing, webhook signature validation in the ops-console API fails
silently or returns HTTP 400. Plane task events and GitHub events will not be processed.

---

## Generate secret values

Run once per secret. Do not reuse the same value for both:

```bash
openssl rand -hex 32
# Copy output — this is PLANE_WEBHOOK_SECRET

openssl rand -hex 32
# Copy output — this is GITHUB_WEBHOOK_SECRET
```

---

## Set in Vercel

```bash
# Set for production environment
vercel env add PLANE_WEBHOOK_SECRET production --yes
# Paste the generated value when prompted

vercel env add GITHUB_WEBHOOK_SECRET production --yes
# Paste the generated value when prompted
```

If the Vercel CLI is not authenticated:
```bash
vercel login
vercel link --project odooops-console
# Then re-run the env add commands above
```

---

## Set in Supabase Vault (if ops-console Edge Functions consume these)

```bash
# Check if any Edge Function reads these secrets
grep -r "PLANE_WEBHOOK_SECRET\|GITHUB_WEBHOOK_SECRET" supabase/functions/

# If found, also add to Vault:
supabase secrets set PLANE_WEBHOOK_SECRET=<value> --project-ref spdtwktxdalcfigzeqrz
supabase secrets set GITHUB_WEBHOOK_SECRET=<value> --project-ref spdtwktxdalcfigzeqrz
```

---

## Set matching values in the webhook source

**Plane**: Plane Dashboard → Settings → Webhooks → odooops-console → update secret to match `PLANE_WEBHOOK_SECRET`.

**GitHub**: Repository Settings → Webhooks → ops-console webhook → update secret to match `GITHUB_WEBHOOK_SECRET`.

---

## Verify

Trigger a test webhook event from each source, then check the ops-console logs:

```bash
vercel logs --project odooops-console --limit 20
```

Expected: HTTP 200 responses. No "Invalid signature" or "Missing secret" errors.

---

## Redeploy to pick up new env vars

```bash
vercel deploy --prod --project odooops-console
```

---

## Related files

- `ssot/errors/failure_modes.yaml` (entries: `ENV.VERCEL.KEY_MISSING.*`)
- `ssot/secrets/registry.yaml` (secret names and consumers)
- `supabase/functions/ops-convergence-scan/index.ts` (env_missing check)
- `apps/ops-console/` (webhook handlers)
