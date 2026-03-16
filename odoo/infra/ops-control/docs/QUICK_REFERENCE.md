# 🎯 Ops Control Room - Quick Reference

## Command Examples

```bash
# Deployments
"deploy prod"
"deploy staging with migrations"

# Health Checks
"check prod status"
"health check all services"

# Spec Generation
"generate spec for user dashboard"
"create prd for payment flow"

# Incident Response
"fix production error"
"triage staging incident"

# Schema Management
"sync database schema"
"run schema diff"
```

---

## Runbook Plan Structure

```typescript
{
  id: "deploy_1234567890",
  kind: "deploy",
  title: "Deploy",
  summary: "Deploy prod (build, migrate, verify).",
  inputs: [
    { key: "env", label: "Environment", type: "select", options: ["prod", "staging", "dev"], value: "prod" },
    { key: "repo", label: "Repo", type: "text", value: "org/repo" },
    { key: "target", label: "Target", type: "text", value: "vercel" }
  ],
  risks: [
    { level: "warn", code: "PROD_CHANGE", message: "Production deployment will modify live services." }
  ],
  integrations: ["GitHub", "Vercel", "Supabase"]
}
```

---

## Execution Phases

```
┌──────────────┐
│  Phase 0     │  Validate inputs
│  Validate    │  → Block if missing required fields
└──────┬───────┘
       │
┌──────▼───────┐
│  Phase 1     │  Preflight checks
│  Preflight   │  → Health checks, latest deployment status
└──────┬───────┘
       │
┌──────▼───────┐
│  Phase 2     │  Execute action
│  Action      │  → Deploy / PR / Schema sync
└──────┬───────┘
       │
┌──────▼───────┐
│  Phase 3     │  Verify results
│  Verify      │  → Re-check health, GitHub Actions status
└──────┬───────┘
       │
┌──────▼───────┐
│  Phase 4     │  Summarize
│  Summarize   │  → Generate artifacts, log next steps
└──────────────┘
```

---

## Database Tables

### `ops.runs`
Stores runbook executions

```sql
id              uuid         -- Primary key
created_at      timestamptz  -- When queued
created_by      uuid         -- User ID (nullable)
env             text         -- prod/staging/dev
kind            text         -- deploy/healthcheck/spec/incident/schema_sync
plan            jsonb        -- Full RunbookPlan
status          text         -- queued/running/success/error
started_at      timestamptz  -- When claimed by executor
finished_at     timestamptz  -- When completed
error_message   text         -- If status=error
```

### `ops.run_events`
Log entries for each run (realtime)

```sql
id              bigserial    -- Primary key
run_id          uuid         -- Foreign key → ops.runs
ts              timestamptz  -- Event timestamp
level           text         -- debug/info/warn/error/success
source          text         -- System/Vercel/GitHub/etc
message         text         -- Log message
data            jsonb        -- Optional structured data
```

### `ops.artifacts`
Output files/links from runs

```sql
id              bigserial    -- Primary key
run_id          uuid         -- Foreign key → ops.runs
created_at      timestamptz  -- When created
kind            text         -- link/diff/file
title           text         -- Display title
value           text         -- URL or file content
```

---

## API Endpoints

### Supabase Client (Browser)

```typescript
// Create a run
const { data: run } = await supabase
  .from('ops.runs')
  .insert({ env: 'prod', kind: 'deploy', plan: {...} })
  .select()
  .single();

// Subscribe to events
const channel = supabase
  .channel(`run-events:${runId}`)
  .on('postgres_changes', { 
    event: 'INSERT', 
    schema: 'ops', 
    table: 'run_events',
    filter: `run_id=eq.${runId}`
  }, (payload) => {
    console.log('New event:', payload.new);
  })
  .subscribe();
```

### Edge Function (Executor)

```typescript
// Claim a run (atomic)
const { data: runId } = await supabase.rpc('ops.claim_run');

// Write an event
await supabase.from('ops.run_events').insert({
  run_id: runId,
  level: 'info',
  source: 'System',
  message: 'Starting execution...'
});

// Complete the run
await supabase.rpc('ops.complete_run', {
  p_run_id: runId,
  p_status: 'success'
});
```

---

## Environment Variables

### Frontend (.env)
```env
VITE_SUPABASE_URL=https://xyz.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...
```

### Edge Function (supabase secrets)
```bash
SUPABASE_SERVICE_ROLE_KEY=...
VERCEL_TOKEN=...
GITHUB_TOKEN=...
DIGITALOCEAN_TOKEN=...
```

---

## Common Tasks

### Deploy Edge Function
```bash
supabase functions deploy ops-executor
```

### View Edge Function Logs
```bash
supabase functions logs ops-executor --tail
```

### Manually Trigger Executor
```bash
curl -X POST https://xyz.supabase.co/functions/v1/ops-executor \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY"
```

### Query Runs
```bash
# Via Supabase SQL Editor
select * from ops.runs order by created_at desc limit 10;

# Via API
curl https://xyz.supabase.co/rest/v1/ops.runs?select=*&order=created_at.desc&limit=10 \
  -H "apikey: $SUPABASE_ANON_KEY"
```

---

## Risk Levels

| Level | Color | Meaning | Example |
|-------|-------|---------|---------|
| `info` | Blue | Informational | "Safe defaults" |
| `warn` | Amber | Caution | "Production change" |
| `block` | Red | Blocked | "Missing credentials" |

---

## Event Levels

| Level | Color | Icon | Usage |
|-------|-------|------|-------|
| `debug` | Gray | Info | Verbose logging |
| `info` | Blue | Info | Standard progress |
| `success` | Green | Check | Completed step |
| `warn` | Amber | Warning | Non-critical issue |
| `error` | Red | X | Critical failure |

---

## Integration Icons

| Integration | Use Case |
|-------------|----------|
| Vercel | Deployments, build logs |
| GitHub | PRs, Actions, commits |
| Supabase | DB checks, migrations, RPC |
| DigitalOcean | Droplet health, SSH |
| Kubernetes | Pod status, deployments |

---

## File Locations

```
/src/app/App.tsx              Main UI component
/src/core/parse.ts            Command → RunbookPlan
/src/core/runbooks.ts         Plan templates
/src/lib/runs.ts              Supabase CRUD + realtime
/supabase/schema.sql          Database schema
/supabase/functions/          Edge Function executor
```

---

## Debugging Checklist

- [ ] `.env` file exists with valid credentials
- [ ] Supabase tables created (run `schema.sql`)
- [ ] Edge Function deployed
- [ ] Secrets set (`supabase secrets list`)
- [ ] RLS policies enabled
- [ ] Realtime publication enabled
- [ ] Cron job configured (for auto-execution)
- [ ] Browser console shows no errors
- [ ] Supabase logs show successful API calls

---

## Performance Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Event latency | <200ms | Postgres CDC → WebSocket |
| Run claim time | <50ms | `FOR UPDATE SKIP LOCKED` |
| API call timeout | 5s | Per external API |
| Log viewer FPS | 60fps | Virtual scrolling |

---

## Security Checklist

- [x] Anon key in browser (RLS protected)
- [x] Service role key in Edge Function only
- [x] External API tokens server-side only
- [x] RLS policies enforce user isolation
- [x] HTTPS only (Supabase enforces)
- [ ] Add Supabase Auth (v2)
- [ ] Add approval workflows (v2)

---

## Support

- **Docs:** [README.md](../README.md)
- **Setup:** [SETUP.md](../SETUP.md)
- **Adapters:** [docs/ADAPTER_GUIDE.md](./ADAPTER_GUIDE.md)
- **Demo:** [docs/DEMO_MODE.md](./DEMO_MODE.md)
