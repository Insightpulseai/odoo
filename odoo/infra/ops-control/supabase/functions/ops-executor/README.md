# Supabase Edge Function: ops-executor

**Purpose:** Executes queued runbooks with privileged access to external APIs (Vercel, GitHub, DigitalOcean, Supabase).

## Deployment

```bash
# Deploy to Supabase
supabase functions deploy ops-executor

# Set environment variables (secrets)
supabase secrets set \
  VERCEL_TOKEN=your_vercel_token \
  GITHUB_TOKEN=your_github_token \
  DIGITALOCEAN_TOKEN=your_do_token \
  SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

## Invocation

The executor can be triggered in two ways:

1. **Cron (recommended):** Set up a Supabase cron job to call this every minute
2. **HTTP:** Call via POST from UI (still secure - runs server-side)

```bash
# Manual trigger
curl -X POST https://your-project.supabase.co/functions/v1/ops-executor \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY"
```

## Architecture

1. Claims the oldest queued run (atomic with `for update skip locked`)
2. Executes phases: validate → preflight → action → verify → summarize
3. Writes events to `ops.run_events` in real-time
4. Writes artifacts to `ops.artifacts` when complete
5. Updates run status to `success` or `error`

## Environment Variables

- `VERCEL_TOKEN` - Vercel API token
- `GITHUB_TOKEN` - GitHub personal access token
- `DIGITALOCEAN_TOKEN` - DigitalOcean API token
- `SUPABASE_SERVICE_ROLE_KEY` - For direct DB writes (bypasses RLS)
