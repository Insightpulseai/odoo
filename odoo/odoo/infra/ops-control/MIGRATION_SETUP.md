# 🔧 Database Migration Setup - Quick Fix

**Problem:** Tables don't exist in your Supabase database yet.

**Solution:** Apply the migration file to create all required tables.

---

## ✅ Option 1: Supabase CLI (Recommended)

If you have Supabase CLI installed:

```bash
# 1. Link to your project
supabase link --project-ref YOUR_PROJECT_REF

# 2. Push all migrations
supabase db push

# 3. Verify tables were created
supabase db diff
```

**Get your project ref:**
- Go to https://supabase.com/dashboard
- Select your project
- Look at the URL: `https://supabase.com/dashboard/project/{YOUR_PROJECT_REF}`

---

## ✅ Option 2: Supabase Dashboard (Easiest)

If you don't have Supabase CLI:

### Step 1: Copy the Migration SQL

Open this file and copy its contents:
- `/supabase/migrations/20250108000000_move_to_public_schema.sql`

### Step 2: Run in SQL Editor

1. Go to https://supabase.com/dashboard
2. Select your project
3. Click **SQL Editor** in the left sidebar
4. Click **New query**
5. Paste the entire migration file contents
6. Click **Run** (bottom right)

### Step 3: Verify Tables

Run this query to verify tables were created:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name IN (
    'sessions',
    'runs',
    'run_events',
    'artifacts',
    'run_templates',
    'spec_docs',
    'run_steps'
  )
ORDER BY table_name;
```

You should see 7 tables listed.

---

## ✅ Option 3: Manual Table Creation (If migration fails)

If the migration file causes errors, run these commands one by one in SQL Editor:

### 1. Create Sessions Table

```sql
create table if not exists public.sessions (
  id uuid primary key default gen_random_uuid(),
  created_by uuid null,
  title text not null default 'Session',
  intent text not null default '',
  status text not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.sessions enable row level security;

create policy sessions_select_anon on public.sessions
for select to anon using (true);

create policy sessions_insert_anon on public.sessions
for insert to anon with check (true);

create policy sessions_update_anon on public.sessions
for update to anon using (true) with check (true);
```

### 2. Create Runs Table

```sql
create table if not exists public.runs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  created_by uuid null,
  env text not null check (env in ('prod','staging','dev')),
  kind text not null check (kind in ('deploy','healthcheck','spec','incident','schema_sync')),
  plan jsonb null,
  intent text not null default '',
  template_id uuid null,
  input jsonb not null default '{}'::jsonb,
  status text not null default 'queued' check (status in ('queued','running','success','error','canceled')),
  started_at timestamptz null,
  finished_at timestamptz null,
  error_message text null,
  session_id uuid null references public.sessions(id) on delete set null,
  lane text not null default 'A',
  priority int not null default 100,
  claimed_by text null,
  claimed_at timestamptz null,
  heartbeat_at timestamptz null,
  canceled_at timestamptz null
);

create index idx_runs_created_at on public.runs(created_at desc);
create index idx_runs_status on public.runs(status);
create index idx_runs_session_idx on public.runs(session_id, created_at desc);
create index idx_runs_claim_idx on public.runs(status, priority, created_at);

alter table public.runs enable row level security;

create policy runs_select_anon on public.runs
for select to anon using (true);

create policy runs_insert_anon on public.runs
for insert to anon with check (true);

create policy runs_update_anon on public.runs
for update to anon using (true) with check (true);
```

### 3. Create Run Events Table

```sql
create table if not exists public.run_events (
  id bigserial primary key,
  run_id uuid not null references public.runs(id) on delete cascade,
  ts timestamptz not null default now(),
  level text not null check (level in ('debug','info','warn','error','success')),
  source text not null,
  message text not null,
  data jsonb null
);

create index idx_run_events_run_id on public.run_events(run_id);
create index idx_run_events_ts on public.run_events(ts);

alter table public.run_events enable row level security;

create policy events_select_anon on public.run_events
for select to anon using (true);

create policy events_insert_anon on public.run_events
for insert to anon with check (true);
```

### 4. Create Artifacts Table

```sql
create table if not exists public.artifacts (
  id bigserial primary key,
  run_id uuid not null references public.runs(id) on delete cascade,
  created_at timestamptz not null default now(),
  kind text not null check (kind in ('link','diff','file')),
  title text not null,
  value text not null
);

create index idx_artifacts_run_id on public.artifacts(run_id);

alter table public.artifacts enable row level security;

create policy artifacts_select_anon on public.artifacts
for select to anon using (true);

create policy artifacts_insert_anon on public.artifacts
for insert to anon with check (true);
```

### 5. Create Run Templates Table

```sql
create table if not exists public.run_templates (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  title text not null,
  description text not null default '',
  template_yaml text not null,
  created_at timestamptz not null default now()
);

alter table public.run_templates enable row level security;

create policy templates_select_anon on public.run_templates
for select to anon using (true);

create policy templates_insert_anon on public.run_templates
for insert to anon with check (true);

create policy templates_update_anon on public.run_templates
for update to anon using (true) with check (true);
```

### 6. Create Spec Docs Table

```sql
create table if not exists public.spec_docs (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  title text not null,
  content text not null,
  updated_at timestamptz not null default now()
);

alter table public.spec_docs enable row level security;

create policy spec_select_anon on public.spec_docs
for select to anon using (true);

create policy spec_insert_anon on public.spec_docs
for insert to anon with check (true);

create policy spec_update_anon on public.spec_docs
for update to anon using (true) with check (true);
```

### 7. Create Run Steps Table

```sql
do $$ begin
  create type public.step_status as enum ('queued','running','succeeded','failed','canceled');
exception when duplicate_object then null; end $$;

create table if not exists public.run_steps (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references public.runs(id) on delete cascade,
  idx int not null,
  step_id text not null,
  title text not null,
  kind text not null default 'system',
  tool text null,
  action text null,
  args jsonb not null default '{}'::jsonb,
  status public.step_status not null default 'queued',
  started_at timestamptz null,
  finished_at timestamptz null,
  error text null
);

create unique index idx_run_steps_unique on public.run_steps(run_id, idx);
create index idx_run_steps_run_idx on public.run_steps(run_id, idx);

alter table public.run_steps enable row level security;

create policy steps_select_anon on public.run_steps
for select to anon using (true);

create policy steps_insert_anon on public.run_steps
for insert to anon with check (true);
```

### 8. Create Helper Functions

```sql
-- Touch updated_at trigger
create or replace function public.touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end $$;

drop trigger if exists trg_sessions_updated_at on public.sessions;
create trigger trg_sessions_updated_at
before update on public.sessions
for each row execute function public.touch_updated_at();

drop trigger if exists trg_runs_updated_at on public.runs;
create trigger trg_runs_updated_at
before update on public.runs
for each row execute function public.touch_updated_at();

-- Claim runs function
create or replace function public.claim_runs(p_worker text, p_limit int default 1)
returns setof public.runs
language plpgsql
security definer
as $$
begin
  return query
  with cte as (
    select id
    from public.runs
    where status = 'queued'
      and (canceled_at is null)
      and (claimed_at is null or claimed_at < now() - interval '5 minutes')
    order by priority asc, created_at asc
    for update skip locked
    limit p_limit
  )
  update public.runs r
  set status = 'running',
      claimed_by = p_worker,
      claimed_at = now(),
      heartbeat_at = now(),
      updated_at = now()
  from cte
  where r.id = cte.id
  returning r.*;
end $$;

grant execute on function public.claim_runs(text, int) to anon;

-- Heartbeat function
create or replace function public.heartbeat_run(p_run_id uuid, p_worker text)
returns void
language plpgsql
security definer
as $$
begin
  update public.runs
  set heartbeat_at = now(),
      claimed_by = p_worker
  where id = p_run_id and status = 'running';
end $$;

grant execute on function public.heartbeat_run(uuid, text) to anon;

-- Cancel run function
create or replace function public.cancel_run(p_run_id uuid)
returns void
language plpgsql
security definer
as $$
begin
  update public.runs
  set status = 'canceled',
      canceled_at = now(),
      updated_at = now()
  where id = p_run_id;
end $$;

grant execute on function public.cancel_run(uuid) to anon;
```

### 9. Enable Realtime

```sql
drop publication if exists supabase_realtime cascade;
create publication supabase_realtime;

alter publication supabase_realtime add table public.sessions;
alter publication supabase_realtime add table public.runs;
alter publication supabase_realtime add table public.run_events;
alter publication supabase_realtime add table public.artifacts;
alter publication supabase_realtime add table public.run_steps;
```

---

## 🎉 After Migration

### Test That It Works

Run this query to count rows in each table:

```sql
SELECT 
  'sessions' as table_name, 
  count(*) as row_count 
FROM public.sessions
UNION ALL
SELECT 'runs', count(*) FROM public.runs
UNION ALL
SELECT 'run_events', count(*) FROM public.run_events
UNION ALL
SELECT 'artifacts', count(*) FROM public.artifacts
UNION ALL
SELECT 'run_templates', count(*) FROM public.run_templates
UNION ALL
SELECT 'spec_docs', count(*) FROM public.spec_docs
UNION ALL
SELECT 'run_steps', count(*) FROM public.run_steps;
```

All tables should show `0` rows (or more if you've already added data).

### Refresh Your App

1. Go back to your Figma Make app
2. Refresh the page (Cmd/Ctrl + R)
3. The errors should be gone!

---

## 🔍 Troubleshooting

### Error: "permission denied for schema public"

**Solution:** You need to be the database owner. In Supabase Dashboard:
1. Go to **SQL Editor**
2. Run: `GRANT ALL ON SCHEMA public TO postgres;`
3. Run: `GRANT ALL ON SCHEMA public TO anon;`
4. Try the migration again

### Error: "relation already exists"

**Solution:** Some tables already exist. Drop them first:

```sql
DROP TABLE IF EXISTS public.run_steps CASCADE;
DROP TABLE IF EXISTS public.artifacts CASCADE;
DROP TABLE IF EXISTS public.run_events CASCADE;
DROP TABLE IF EXISTS public.runs CASCADE;
DROP TABLE IF EXISTS public.sessions CASCADE;
DROP TABLE IF EXISTS public.run_templates CASCADE;
DROP TABLE IF EXISTS public.spec_docs CASCADE;
DROP TYPE IF EXISTS public.step_status CASCADE;
```

Then run the migration again.

### Error: "function already exists"

**Solution:** Drop and recreate:

```sql
DROP FUNCTION IF EXISTS public.claim_runs(text, int) CASCADE;
DROP FUNCTION IF EXISTS public.heartbeat_run(uuid, text) CASCADE;
DROP FUNCTION IF EXISTS public.cancel_run(uuid) CASCADE;
DROP FUNCTION IF EXISTS public.touch_updated_at() CASCADE;
```

Then recreate the functions from Option 3 above.

### Still Getting Errors?

1. Check Supabase Dashboard → Database → Tables
2. Verify all 7 tables exist under "public" schema
3. Check browser console for more detailed error messages
4. Verify your `.env` file has correct credentials

---

## 📝 Next Steps After Migration

1. ✅ Tables created
2. ✅ Realtime enabled
3. ✅ RLS policies set
4. ✅ Helper functions created

Now you can:
- Create sessions in the Runboard tab
- Run tasks in lanes A/B/C/D
- Watch logs stream in real-time
- View artifacts

---

## 🆘 Quick Support

**Still stuck?** Check these:

1. **Is your Supabase URL correct in `.env`?**
   ```bash
   cat .env | grep VITE_SUPABASE_URL
   # Should show: https://YOUR_PROJECT.supabase.co
   ```

2. **Is your anon key correct in `.env`?**
   ```bash
   cat .env | grep VITE_SUPABASE_ANON_KEY
   # Should show a long JWT token
   ```

3. **Is realtime enabled?**
   - Go to Supabase Dashboard → Database → Replication
   - Enable "supabase_realtime" publication
   - Add tables: sessions, runs, run_events, artifacts, run_steps

4. **Are RLS policies correct?**
   - Go to Supabase Dashboard → Authentication → Policies
   - You should see policies for each table allowing "anon" access

---

**After migration is complete, your app will work perfectly!** 🎉
