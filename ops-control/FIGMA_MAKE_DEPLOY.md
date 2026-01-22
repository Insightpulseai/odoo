# 🎨 Figma Make + Supabase Deployment Guide

**Optimized for Figma Make's Supabase integration patterns**

---

## ✅ What You Already Have (Status Check)

Your project **already includes** the required Supabase deploy artifacts:

```
supabase/
├── migrations/
│   └── 20250103000000_ops_schema.sql  ✅ Complete ops schema
└── functions/
    └── ops-executor/
        └── index.ts                    ✅ 5-phase executor
```

**This means:** The "No Supabase code to deploy" error is **resolved** once you follow the steps below.

---

## 🎯 Figma Make's Supabase Integration: 3 Primitives

According to [Figma's documentation](https://help.figma.com/hc/en-us/articles/32640822050199), the integration gives you:

### 1. **Secret Storage**
- Via Figma Make's UI: Settings → Secrets → Create a secret
- NOT in `.env` or prompts
- Available to Edge Functions via `Deno.env.get()`

### 2. **Edge Functions** (Compute)
- Defined in `supabase/functions/`
- Deployed when you click Deploy
- Can access secrets server-side

### 3. **Postgres Database**
- Figma Make sets up basic key-value stores by default
- For custom schemas (like `ops.*`), you **must** provide migrations
- Deployed when you click Deploy

---

## 🚀 Deployment Steps (Figma Make Workflow)

### Step 1: Add Backend Connection (One-Time)

1. **In Figma Make:** Click the backend icon or Settings
2. **Choose:** Supabase
3. **Connect** to your existing Supabase project
   - Project URL: `https://your-project.supabase.co`
   - Anon key: From Supabase Dashboard → Settings → API

**Note:** This is **one backend per Figma Make file**. Once connected, you're done.

---

### Step 2: Set Up Secrets (Figma Make UI)

**Figma Make → Settings → Secrets**

Click **"Create a secret"** for each:

| Secret Name | Value | Where to Get |
|------------|-------|--------------|
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbG...` | Supabase Dashboard → Settings → API → service_role |
| `VERCEL_TOKEN` | `vercel_...` | [vercel.com/account/tokens](https://vercel.com/account/tokens) |
| `GITHUB_TOKEN` | `ghp_...` | [github.com/settings/tokens](https://github.com/settings/tokens) |
| `DIGITALOCEAN_TOKEN` | `dop_...` | [cloud.digitalocean.com/account/api/tokens](https://cloud.digitalocean.com/account/api/tokens) |

**Important:**
- ✅ Use Figma's secret UI (not Supabase Dashboard)
- ✅ Secrets are automatically available to Edge Functions
- ✅ Never put secrets in code or prompts

---

### Step 3: Deploy

Click **Deploy** button in Figma Make (top-right).

This will:
1. ✅ Apply migration `20250103000000_ops_schema.sql`
   - Creates `ops.runs`, `ops.run_events`, `ops.artifacts` tables
   - Enables Row Level Security
   - Creates helper functions
2. ✅ Deploy Edge Function `ops-executor`
   - Makes it available at `https://your-project.supabase.co/functions/v1/ops-executor`
   - Injects secrets from Step 2

**Expected output:**
```
✓ Applied migration: 20250103000000_ops_schema.sql
✓ Deployed function: ops-executor
✓ Deployment complete
```

---

### Step 4: Enable Realtime (One-Time)

**Supabase Dashboard → Database → Replication**

Enable publication for:
- ✅ `ops.runs`
- ✅ `ops.run_events`
- ✅ `ops.artifacts`

Or run this SQL in Supabase SQL Editor:

```sql
alter publication supabase_realtime add table ops.runs;
alter publication supabase_realtime add table ops.run_events;
alter publication supabase_realtime add table ops.artifacts;
```

**Why:** This enables real-time log streaming to the UI.

---

### Step 5: Set Up Executor Trigger (Cron)

The Edge Function needs to check for queued runs periodically.

**Option A: Supabase pg_cron (Recommended)**

Run in **Supabase SQL Editor**:

```sql
create extension if not exists pg_cron;

select cron.schedule(
  'ops-executor-cron',
  '* * * * *',  -- Every minute
  $$
  select net.http_post(
    url := 'https://YOUR-PROJECT-REF.supabase.co/functions/v1/ops-executor',
    headers := '{"Authorization": "Bearer YOUR-ANON-KEY"}'::jsonb
  )
  $$
);
```

Replace:
- `YOUR-PROJECT-REF` with your project ID
- `YOUR-ANON-KEY` with your anon key

**Option B: Manual Trigger (Testing)**

```bash
curl -X POST https://YOUR-PROJECT.supabase.co/functions/v1/ops-executor \
  -H "Authorization: Bearer YOUR-ANON-KEY"
```

---

### Step 6: Test End-to-End

1. **Open your Figma Make app** (published URL or preview)
2. **Type:** `"check prod status"`
3. **Click Run** on the runbook card
4. **Watch:** Real-time logs stream into fullscreen viewer

**Verify in Supabase Dashboard:**
- Table Editor → ops → runs (should see a row with `status = 'success'`)
- Table Editor → ops → run_events (should see multiple log entries)

---

## 📋 What Gets Created

### Database Schema (from migration)

**ops.runs**
```sql
create table ops.runs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  created_by uuid null references auth.users(id),
  env text not null check (env in ('prod','staging','dev')),
  kind text not null check (kind in ('deploy','healthcheck','spec','incident','schema_sync')),
  plan jsonb not null,
  status text not null default 'queued' check (status in ('queued','running','success','error')),
  started_at timestamptz null,
  finished_at timestamptz null,
  error_message text null
);
```

**ops.run_events**
```sql
create table ops.run_events (
  id bigserial primary key,
  run_id uuid not null references ops.runs(id) on delete cascade,
  ts timestamptz not null default now(),
  level text not null check (level in ('debug','info','warn','error','success')),
  source text not null,
  message text not null,
  data jsonb null
);
```

**ops.artifacts**
```sql
create table ops.artifacts (
  id bigserial primary key,
  run_id uuid not null references ops.runs(id) on delete cascade,
  created_at timestamptz not null default now(),
  kind text not null check (kind in ('link','diff','file')),
  title text not null,
  value text not null
);
```

### RLS Policies

**For authenticated users:**
- ✅ Can read/write their own runs (`created_by = auth.uid()`)
- ✅ Can read their own events/artifacts
- ❌ Cannot write events/artifacts (only executor can)

**For service_role (Edge Function):**
- ✅ Can write events/artifacts for any run
- ✅ Can update run status

### Helper Functions

**ops.enqueue_run(env, kind, plan)**
- Creates a queued run
- Returns: run_id

**ops.claim_run()**
- Atomically claims next queued run
- Returns: run_id or null

**ops.complete_run(run_id, status, error_message)**
- Marks run as success/error
- Returns: void

---

## 🔐 Security Model (Aligned with Figma Make)

### Frontend (Browser)
```typescript
// From .env
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;
```
✅ Safe - Protected by RLS policies  
✅ Users can only see their own runs  
✅ Cannot write fake logs

### Edge Function (Server-Side)
```typescript
// From Figma Make secrets (NOT in code!)
const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
const vercelToken = Deno.env.get("VERCEL_TOKEN");
const githubToken = Deno.env.get("GITHUB_TOKEN");
```
❌ NEVER exposed to browser  
❌ Managed via Figma Make's secret UI  
✅ Bypasses RLS for writing logs/artifacts

---

## 🔄 Execution Flow

```
1. User types command
   └─→ CommandBar.tsx parses intent
   
2. Generate runbook plan
   └─→ runbooks.ts creates RunbookPlan JSON
   
3. User clicks Run
   └─→ runs.ts calls enqueue_run()
   └─→ INSERT into ops.runs with status='queued'
   
4. Cron triggers Edge Function (every 1 min)
   └─→ Edge Function calls claim_run()
   └─→ UPDATE ops.runs SET status='running'
   
5. Edge Function executes 5 phases
   ├─→ Phase 0: Validate inputs
   ├─→ Phase 1: Preflight checks
   ├─→ Phase 2: Execute action
   ├─→ Phase 3: Verify results
   └─→ Phase 4: Summarize
   
6. Each phase writes events
   └─→ INSERT into ops.run_events
   
7. UI subscribes to realtime
   └─→ LogViewer.tsx receives events
   └─→ Streams logs like ChatGPT
   
8. Edge Function completes
   └─→ Calls complete_run(run_id, 'success')
   └─→ Writes artifacts
   └─→ UPDATE ops.runs SET status='success'
```

---

## 🧪 Testing Checklist

### After Deployment

- [ ] **Database tables exist**
  - Supabase Dashboard → Table Editor → ops schema
  - Should see: runs, run_events, artifacts

- [ ] **Edge Function deployed**
  - Supabase Dashboard → Edge Functions
  - Should see: ops-executor

- [ ] **Secrets configured**
  - Figma Make → Settings → Secrets
  - Should see: SUPABASE_SERVICE_ROLE_KEY, etc.

- [ ] **Realtime enabled**
  - Supabase Dashboard → Database → Replication
  - Should see: ops.runs, ops.run_events, ops.artifacts enabled

- [ ] **Cron trigger set up**
  - Test with manual curl
  - Or verify pg_cron schedule exists

### Test Cases

**Test 1: Create a run (UI → Database)**
```
1. Open app
2. Type: "check prod status"
3. Click Run
4. Check Supabase Dashboard → ops.runs
   Expected: New row with status='queued'
```

**Test 2: Execute a run (Executor → Database)**
```
1. Trigger executor manually or wait for cron
2. Check ops.runs: status should change 'queued' → 'running' → 'success'
3. Check ops.run_events: Should have ~10-15 log entries
```

**Test 3: Real-time streaming (Database → UI)**
```
1. Create a run and click Run
2. Watch LogViewer
3. Expected: Logs appear in real-time as executor writes them
4. Expected: "Phase 0: Validate" → "Phase 1: Preflight" → etc.
```

---

## 🛠️ Troubleshooting

### "No Supabase code to deploy"

**Status:** ✅ FIXED (you have migrations + functions now)

**If still seeing this:**
- Verify `/supabase/migrations/20250103000000_ops_schema.sql` exists
- Verify `/supabase/functions/ops-executor/index.ts` exists
- Refresh Figma Make and try Deploy again

### "Missing Supabase environment variables"

**Solution:** Edit `/.env` file with:
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

**Get these from:** Supabase Dashboard → Settings → API

### "RPC function not found: ops.claim_run"

**Solution:** Migration didn't apply successfully

**Fix:**
1. Go to Supabase Dashboard → SQL Editor
2. Copy contents of `/supabase/migrations/20250103000000_ops_schema.sql`
3. Paste and Run
4. Verify `ops` schema exists in Database → Schema Visualizer

### "No events appearing in UI"

**Checklist:**
- [ ] Realtime enabled? (Database → Replication)
- [ ] Edge Function deployed? (Edge Functions tab)
- [ ] Secrets set? (Figma Make → Settings → Secrets)
- [ ] Cron trigger active? (Test with manual curl)

**Debug:**
1. Check Edge Function logs: Supabase Dashboard → Edge Functions → ops-executor → Logs
2. Look for errors or "No queued runs" message
3. Verify run exists: Table Editor → ops.runs

### "Service role key not working"

**Solution:** Use Figma Make's secret UI, not Supabase Dashboard

**Correct flow:**
1. Copy service_role key from Supabase
2. Paste in **Figma Make → Settings → Secrets**
3. **NOT** in Supabase Dashboard → Edge Functions → Settings

---

## 📦 What's Different from Standard Supabase

| Standard Supabase Setup | Figma Make + Supabase |
|------------------------|----------------------|
| Secrets in Supabase Dashboard | Secrets in Figma Make Settings |
| Deploy via `supabase functions deploy` | Deploy via Figma Make Deploy button |
| Migrations via `supabase db push` | Migrations via Figma Make Deploy button |
| Manual RLS setup | RLS included in migration |
| Separate auth setup | Optional (can skip initially) |

**Key insight:** Figma Make **wraps** the Supabase CLI for you. Use the Deploy button instead of manual CLI commands.

---

## 🎯 Simplified Auth Strategy (Optional)

### v1: No Auth (Simplest)

Update RLS policies to allow unauthenticated access:

```sql
-- Allow anyone to insert runs
create policy "runs_insert_anon" on ops.runs 
  for insert to anon 
  with check (true);

-- Allow anyone to read events
create policy "events_select_anon" on ops.run_events 
  for select to anon 
  using (true);
```

**Use when:** Single-user prototype, internal tool, demo

### v2: Magic Link (Simple)

Keep existing policies (`authenticated` role), add magic link:

```typescript
await supabase.auth.signInWithOtp({ email: 'user@example.com' });
```

**Use when:** Need user tracking but not complex auth

### v3: Full Auth (Production)

Add email/password or OAuth:

```typescript
await supabase.auth.signInWithPassword({ email, password });
```

**Use when:** Production multi-user system

**Recommendation:** Start with v1, upgrade to v2 when needed.

---

## ✅ You're Ready!

Your Ops Control Room is properly configured for Figma Make's Supabase integration:

- ✅ Migration defines custom `ops.*` schema (not just key-value)
- ✅ Edge Function has 5-phase executor logic
- ✅ Secrets managed via Figma Make UI
- ✅ RLS protects data
- ✅ Realtime streams logs

**Next:** Click Deploy and test with "check prod status"!

---

## 🔗 References

- [Figma: Add a backend to a functional prototype](https://help.figma.com/hc/en-us/articles/32640822050199)
- [Supabase Edge Functions](https://supabase.com/docs/guides/functions)
- [Supabase Realtime](https://supabase.com/docs/guides/realtime)
- [PostgreSQL Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
