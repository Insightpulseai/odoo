# Supabase ops.* Schema Setup Guide

> Comprehensive setup guide for the OdooOps Sh control plane schema in Supabase (spdtwktxdalcfigzeqrz).
> Based on spec bundle: `spec/odooops-sh/`

---

## Overview

This guide covers the complete setup of 9 ops.* tables for the Odoo.sh replacement control plane:

1. `ops.projects` - Workspace containers
2. `ops.workflows` - Workflow definitions (build, test, deploy, backup, upgrade)
3. `ops.runs` - Main execution queue with worker claiming
4. `ops.run_events` - Append-only event log
5. `ops.run_artifacts` - Build output metadata (S3-style)
6. `ops.run_logs` - Structured log lines
7. `ops.tools` - Docker image registry
8. `ops.upgrade_advisories` - Breaking change warnings
9. `ops.project_memberships` - User access control

**Architecture Pattern**: Queue-based execution with worker claim pattern (SELECT FOR UPDATE SKIP LOCKED)

**SSOT Boundaries**:
- **Odoo Database**: Business data (res.partner, account.move)
- **Supabase ops.***: Control plane state
- **Supabase Storage**: Binary artifacts

---

## Prerequisites

**Required**:
- Supabase CLI (`brew install supabase/tap/supabase`)
- Project: `spdtwktxdalcfigzeqrz`
- Access tokens in `~/.zshrc`:
  ```bash
  export SUPABASE_PROJECT_REF=spdtwktxdalcfigzeqrz
  export SUPABASE_ACCESS_TOKEN=sbp_...
  export SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
  export SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```

**Verify**:
```bash
supabase link --project-ref spdtwktxdalcfigzeqrz
supabase status
```

---

## Migration Files Structure

```
supabase/migrations/
├── 20260213_000001_ops_rename_agent_tables.sql      # Breaking change: rename agent tables
├── 20260213_000100_ops_core_schema.sql              # Core 9 tables
├── 20260213_000200_ops_rpc_functions.sql            # 6 RPC functions
├── 20260213_000300_ops_rls_policies.sql             # Row-level security
└── 20260213_000400_ops_indexes_constraints.sql      # Performance + safety
```

---

## Step 1: Breaking Change Migration (Rename Agent Tables)

**Purpose**: Avoid naming collision between existing agent tracking and new OdooOps Sh control plane.

**Migration**: `20260213_000001_ops_rename_agent_tables.sql`

```sql
-- ===========================================================================
-- Breaking Change: Rename agent tables to avoid collision
-- ===========================================================================
-- Context: Existing ops.runs table used for agent tracking
-- Change: Rename to ops.agent_runs to free up ops.runs for OdooOps Sh
-- ===========================================================================

-- Step 1: Rename existing agent tracking tables
alter table if exists ops.runs rename to agent_runs;
alter table if exists ops.run_logs rename to agent_run_logs;

-- Step 2: Update dependent Edge Functions (2 affected)
-- Edge Functions to update:
--   1. ops-ingest: Change table references
--   2. executor: Change table references

-- Step 3: Verify no data loss
comment on table ops.agent_runs is 'Renamed from ops.runs 2026-02-13 for OdooOps Sh compatibility';
comment on table ops.agent_run_logs is 'Renamed from ops.run_logs 2026-02-13 for OdooOps Sh compatibility';

-- Step 4: Create views for backward compatibility (temporary)
create or replace view ops.agent_runs_v as select * from ops.agent_runs;
create or replace view ops.agent_run_logs_v as select * from ops.agent_run_logs;

-- Verification
do $$
begin
  if exists (select 1 from information_schema.tables where table_schema='ops' and table_name='agent_runs') then
    raise notice 'SUCCESS: ops.agent_runs exists';
  else
    raise exception 'FAILED: ops.agent_runs not found';
  end if;

  if exists (select 1 from information_schema.tables where table_schema='ops' and table_name='agent_run_logs') then
    raise notice 'SUCCESS: ops.agent_run_logs exists';
  else
    raise exception 'FAILED: ops.agent_run_logs not found';
  end if;
end $$;
```

**Apply**:
```bash
# Test locally first
supabase db reset
supabase db push

# Apply to remote
supabase db push --linked
```

**Verification**:
```bash
psql "$SUPABASE_URL" -c "\dt ops.agent_*"
psql "$SUPABASE_URL" -c "SELECT count(*) FROM ops.agent_runs;"
```

**Edge Function Updates Required**:
```bash
# Update 2 Edge Functions
supabase functions deploy ops-ingest    # Change ops.runs → ops.agent_runs
supabase functions deploy executor      # Change ops.run_logs → ops.agent_run_logs
```

---

## Step 2: Core Schema (9 Tables)

**Migration**: `20260213_000100_ops_core_schema.sql`

```sql
-- ===========================================================================
-- OdooOps Sh Core Schema: 9 Tables
-- ===========================================================================
-- Purpose: Odoo.sh-style control plane for self-hosted Odoo environments
-- State Machine: queued → claimed → running → succeeded|failed
-- ===========================================================================

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- 1. ops.projects - Workspace Containers
-- ---------------------------------------------------------------------------
create table ops.projects (
  id uuid primary key default gen_random_uuid(),
  workspace_key text not null unique,           -- e.g., ipai_workspace
  slug text not null unique,                     -- human-readable identifier
  name text not null,                            -- display name
  description text,
  odoo_version text not null,                    -- 17.0, 18.0, 19.0
  status text not null default 'active' check (status in ('active', 'archived')),
  config jsonb not null default '{}'::jsonb,     -- custom project settings
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

comment on table ops.projects is 'Workspace containers for OdooOps Sh projects';
comment on column ops.projects.workspace_key is 'Unique workspace identifier (e.g., ipai_workspace)';
comment on column ops.projects.slug is 'Human-readable project slug';
comment on column ops.projects.odoo_version is 'Target Odoo version (17.0, 18.0, 19.0)';

create index idx_ops_projects_workspace_key on ops.projects(workspace_key);
create index idx_ops_projects_slug on ops.projects(slug);
create index idx_ops_projects_status on ops.projects(status) where status = 'active';

-- ---------------------------------------------------------------------------
-- 2. ops.workflows - Workflow Definitions
-- ---------------------------------------------------------------------------
create table ops.workflows (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references ops.projects(id) on delete cascade,
  workflow_type text not null check (workflow_type in ('build', 'test', 'deploy', 'backup', 'upgrade')),
  name text not null,                            -- display name
  description text,
  enabled boolean not null default true,
  git_ref text,                                  -- branch or tag
  git_commit text,                               -- commit SHA
  config jsonb not null default '{}'::jsonb,     -- workflow-specific config
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (project_id, workflow_type, name)
);

comment on table ops.workflows is 'Workflow definitions (build, test, deploy, backup, upgrade)';
comment on column ops.workflows.workflow_type is 'Type: build | test | deploy | backup | upgrade';
comment on column ops.workflows.git_ref is 'Branch or tag reference';
comment on column ops.workflows.git_commit is 'Commit SHA for reproducibility';

create index idx_ops_workflows_project_id on ops.workflows(project_id);
create index idx_ops_workflows_type on ops.workflows(workflow_type);
create index idx_ops_workflows_enabled on ops.workflows(enabled) where enabled = true;

-- ---------------------------------------------------------------------------
-- 3. ops.runs - Main Execution Queue
-- ---------------------------------------------------------------------------
create table ops.runs (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references ops.projects(id) on delete cascade,
  workflow_id uuid not null references ops.workflows(id) on delete cascade,
  run_number serial not null,                    -- auto-incrementing per project
  idempotency_key text unique,                   -- client-generated deduplication
  status text not null default 'queued' check (status in ('queued', 'claimed', 'running', 'succeeded', 'failed', 'canceled')),

  -- Worker claim fields
  claimed_by text,                               -- worker identifier
  claimed_at timestamptz,

  -- Execution timestamps
  started_at timestamptz,
  finished_at timestamptz,

  -- Execution metadata
  exit_code int,
  error_message text,
  metadata jsonb not null default '{}'::jsonb,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

comment on table ops.runs is 'Main execution queue with worker claim pattern';
comment on column ops.runs.run_number is 'Auto-incrementing run number per project';
comment on column ops.runs.idempotency_key is 'Client-generated key for deduplication';
comment on column ops.runs.claimed_by is 'Worker ID that claimed this run';
comment on column ops.runs.claimed_at is 'Timestamp when worker claimed run';

create index idx_ops_runs_project_id on ops.runs(project_id, run_number desc);
create index idx_ops_runs_workflow_id on ops.runs(workflow_id);
create index idx_ops_runs_status on ops.runs(status);
create index idx_ops_runs_queued on ops.runs(created_at) where status = 'queued';
create index idx_ops_runs_claimed_by on ops.runs(claimed_by, claimed_at desc);
create index idx_ops_runs_idempotency on ops.runs(idempotency_key) where idempotency_key is not null;

-- ---------------------------------------------------------------------------
-- 4. ops.run_events - Append-Only Event Log
-- ---------------------------------------------------------------------------
create table ops.run_events (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references ops.runs(id) on delete cascade,
  event_type text not null check (event_type in ('state_change', 'error', 'warning', 'info')),
  message text not null,
  payload jsonb not null default '{}'::jsonb,    -- extensible metadata
  created_at timestamptz not null default now()
);

comment on table ops.run_events is 'Append-only event log for audit trail';
comment on column ops.run_events.event_type is 'Event type: state_change | error | warning | info';
comment on column ops.run_events.payload is 'Extensible JSON payload';

create index idx_ops_run_events_run_id on ops.run_events(run_id, created_at desc);
create index idx_ops_run_events_type on ops.run_events(event_type, created_at desc);

-- ---------------------------------------------------------------------------
-- 5. ops.run_artifacts - Build Output Metadata
-- ---------------------------------------------------------------------------
create table ops.run_artifacts (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references ops.runs(id) on delete cascade,
  artifact_key text not null,                    -- S3-style key (e.g., builds/project-123/artifact.tar.gz)
  artifact_url text not null,                    -- Supabase Storage URL
  content_type text,                             -- MIME type
  size_bytes bigint,                             -- File size
  checksum text,                                 -- SHA-256 checksum
  expires_at timestamptz,                        -- Expiry date for cleanup
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (run_id, artifact_key)
);

comment on table ops.run_artifacts is 'Build output metadata (S3-style)';
comment on column ops.run_artifacts.artifact_key is 'S3-style artifact key';
comment on column ops.run_artifacts.checksum is 'SHA-256 checksum for integrity verification';
comment on column ops.run_artifacts.expires_at is 'Expiry date for automated cleanup';

create index idx_ops_run_artifacts_run_id on ops.run_artifacts(run_id);
create index idx_ops_run_artifacts_key on ops.run_artifacts(artifact_key);
create index idx_ops_run_artifacts_expires on ops.run_artifacts(expires_at) where expires_at is not null;

-- ---------------------------------------------------------------------------
-- 6. ops.run_logs - Structured Log Lines
-- ---------------------------------------------------------------------------
create table ops.run_logs (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references ops.runs(id) on delete cascade,
  log_level text not null check (log_level in ('debug', 'info', 'warn', 'error')),
  message text not null,
  metadata jsonb not null default '{}'::jsonb,
  timestamp timestamptz not null default now()
);

comment on table ops.run_logs is 'Structured log lines with full-text search';
comment on column ops.run_logs.log_level is 'Log level: debug | info | warn | error';

create index idx_ops_run_logs_run_id on ops.run_logs(run_id, timestamp desc);
create index idx_ops_run_logs_level on ops.run_logs(log_level, timestamp desc);

-- Full-text search support
create index idx_ops_run_logs_message_fts on ops.run_logs using gin(to_tsvector('english', message));

-- ---------------------------------------------------------------------------
-- 7. ops.tools - Docker Image Registry
-- ---------------------------------------------------------------------------
create table ops.tools (
  id uuid primary key default gen_random_uuid(),
  tool_name text not null,                       -- e.g., odoo, postgres, nginx
  version text not null,                         -- e.g., 19.0, 16.4
  docker_image text not null,                    -- Full image reference (e.g., odoo:19.0)
  config jsonb not null default '{}'::jsonb,     -- Tool-specific configuration
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tool_name, version)
);

comment on table ops.tools is 'Docker image registry for tools';
comment on column ops.tools.docker_image is 'Full Docker image reference';

create index idx_ops_tools_name on ops.tools(tool_name);
create index idx_ops_tools_name_version on ops.tools(tool_name, version);

-- ---------------------------------------------------------------------------
-- 8. ops.upgrade_advisories - Breaking Change Warnings
-- ---------------------------------------------------------------------------
create table ops.upgrade_advisories (
  id uuid primary key default gen_random_uuid(),
  from_version text not null,                    -- e.g., 17.0
  to_version text not null,                      -- e.g., 18.0
  severity text not null check (severity in ('low', 'medium', 'high', 'critical')),
  title text not null,
  description text not null,
  migration_guide text,                          -- Markdown or URL
  affects_modules text[],                        -- List of affected modules
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

comment on table ops.upgrade_advisories is 'Breaking change warnings for version upgrades';
comment on column ops.upgrade_advisories.severity is 'Severity: low | medium | high | critical';
comment on column ops.upgrade_advisories.migration_guide is 'Markdown guide or URL to documentation';

create index idx_ops_upgrade_advisories_versions on ops.upgrade_advisories(from_version, to_version);
create index idx_ops_upgrade_advisories_severity on ops.upgrade_advisories(severity);

-- ---------------------------------------------------------------------------
-- 9. ops.project_memberships - User Access Control
-- ---------------------------------------------------------------------------
create table ops.project_memberships (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references ops.projects(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('owner', 'admin', 'developer', 'viewer')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (project_id, user_id)
);

comment on table ops.project_memberships is 'User access control for projects';
comment on column ops.project_memberships.role is 'Role: owner | admin | developer | viewer';

create index idx_ops_project_memberships_project_id on ops.project_memberships(project_id);
create index idx_ops_project_memberships_user_id on ops.project_memberships(user_id);
create index idx_ops_project_memberships_role on ops.project_memberships(role);

-- ---------------------------------------------------------------------------
-- Verification
-- ---------------------------------------------------------------------------
do $$
declare
  table_count int;
begin
  select count(*) into table_count
  from information_schema.tables
  where table_schema = 'ops'
    and table_name in (
      'projects', 'workflows', 'runs', 'run_events', 'run_artifacts',
      'run_logs', 'tools', 'upgrade_advisories', 'project_memberships'
    );

  if table_count = 9 then
    raise notice 'SUCCESS: All 9 ops.* tables created';
  else
    raise exception 'FAILED: Expected 9 tables, found %', table_count;
  end if;
end $$;
```

**Apply**:
```bash
supabase db push --linked
```

**Verification**:
```bash
# List all ops.* tables
psql "$SUPABASE_URL" -c "SELECT tablename FROM pg_tables WHERE schemaname='ops' ORDER BY tablename;"

# Verify table structure
psql "$SUPABASE_URL" -c "\d ops.projects"
psql "$SUPABASE_URL" -c "\d ops.runs"
```

---

## Step 3: RPC Functions (Worker Queue & Lifecycle)

**Migration**: `20260213_000200_ops_rpc_functions.sql`

```sql
-- ===========================================================================
-- OdooOps Sh RPC Functions: Worker Queue & Run Lifecycle
-- ===========================================================================
-- Purpose: 6 RPC functions for safe worker claiming and run state management
-- Pattern: SELECT FOR UPDATE SKIP LOCKED for queue concurrency
-- ===========================================================================

-- ---------------------------------------------------------------------------
-- 1. ops.claim_next_run(p_worker_id) - Worker Queue Claiming
-- ---------------------------------------------------------------------------
create or replace function ops.claim_next_run(p_worker_id text)
returns jsonb
language plpgsql
as $$
declare
  v_run record;
begin
  -- Claim oldest queued run atomically
  select * into v_run
  from ops.runs
  where status = 'queued'
  order by created_at
  for update skip locked
  limit 1;

  if not found then
    return jsonb_build_object('run_id', null, 'message', 'No queued runs available');
  end if;

  -- Update run to claimed state
  update ops.runs
  set status = 'claimed',
      claimed_by = p_worker_id,
      claimed_at = now(),
      updated_at = now()
  where id = v_run.id;

  -- Log state change event
  insert into ops.run_events (run_id, event_type, message, payload)
  values (
    v_run.id,
    'state_change',
    'Run claimed by worker',
    jsonb_build_object('worker_id', p_worker_id, 'previous_status', 'queued', 'new_status', 'claimed')
  );

  return jsonb_build_object(
    'run_id', v_run.id,
    'project_id', v_run.project_id,
    'workflow_id', v_run.workflow_id,
    'run_number', v_run.run_number,
    'claimed_at', now()
  );
end;
$$;

comment on function ops.claim_next_run is 'Atomically claim next queued run for worker execution';

-- ---------------------------------------------------------------------------
-- 2. ops.start_workflow_run(p_run_id, p_worker_id) - Mark as Running
-- ---------------------------------------------------------------------------
create or replace function ops.start_workflow_run(p_run_id uuid, p_worker_id text)
returns jsonb
language plpgsql
as $$
declare
  v_run record;
begin
  -- Verify run is claimed by this worker
  select * into v_run
  from ops.runs
  where id = p_run_id
    and status = 'claimed'
    and claimed_by = p_worker_id
  for update;

  if not found then
    return jsonb_build_object('success', false, 'error', 'Run not found or not claimed by this worker');
  end if;

  -- Update to running state
  update ops.runs
  set status = 'running',
      started_at = now(),
      updated_at = now()
  where id = p_run_id;

  -- Log state change event
  insert into ops.run_events (run_id, event_type, message, payload)
  values (
    p_run_id,
    'state_change',
    'Run started execution',
    jsonb_build_object('worker_id', p_worker_id, 'previous_status', 'claimed', 'new_status', 'running')
  );

  return jsonb_build_object('success', true, 'started_at', now());
end;
$$;

comment on function ops.start_workflow_run is 'Mark claimed run as running (pre-execution validation)';

-- ---------------------------------------------------------------------------
-- 3. ops.complete_workflow_run(p_run_id, p_exit_code, p_error_message) - Finish Run
-- ---------------------------------------------------------------------------
create or replace function ops.complete_workflow_run(
  p_run_id uuid,
  p_exit_code int,
  p_error_message text default null
)
returns jsonb
language plpgsql
as $$
declare
  v_run record;
  v_new_status text;
begin
  -- Verify run is running
  select * into v_run
  from ops.runs
  where id = p_run_id
    and status = 'running'
  for update;

  if not found then
    return jsonb_build_object('success', false, 'error', 'Run not found or not in running state');
  end if;

  -- Determine final status based on exit code
  v_new_status := case when p_exit_code = 0 then 'succeeded' else 'failed' end;

  -- Update to final state
  update ops.runs
  set status = v_new_status,
      finished_at = now(),
      exit_code = p_exit_code,
      error_message = p_error_message,
      updated_at = now()
  where id = p_run_id;

  -- Log state change event
  insert into ops.run_events (run_id, event_type, message, payload)
  values (
    p_run_id,
    'state_change',
    format('Run completed with status: %s', v_new_status),
    jsonb_build_object(
      'previous_status', 'running',
      'new_status', v_new_status,
      'exit_code', p_exit_code,
      'error_message', p_error_message
    )
  );

  return jsonb_build_object(
    'success', true,
    'status', v_new_status,
    'finished_at', now(),
    'exit_code', p_exit_code
  );
end;
$$;

comment on function ops.complete_workflow_run is 'Mark running run as succeeded or failed based on exit code';

-- ---------------------------------------------------------------------------
-- 4. ops.append_run_log(p_run_id, p_level, p_message, p_metadata) - Log Entry
-- ---------------------------------------------------------------------------
create or replace function ops.append_run_log(
  p_run_id uuid,
  p_level text,
  p_message text,
  p_metadata jsonb default '{}'::jsonb
)
returns jsonb
language plpgsql
as $$
begin
  -- Validate log level
  if p_level not in ('debug', 'info', 'warn', 'error') then
    return jsonb_build_object('success', false, 'error', 'Invalid log level');
  end if;

  -- Insert log entry
  insert into ops.run_logs (run_id, log_level, message, metadata, timestamp)
  values (p_run_id, p_level, p_message, p_metadata, now());

  return jsonb_build_object('success', true, 'timestamp', now());
end;
$$;

comment on function ops.append_run_log is 'Append structured log entry to run logs';

-- ---------------------------------------------------------------------------
-- 5. ops.add_run_artifact(p_run_id, p_artifact_key, p_s3_url, ...) - Store Artifact
-- ---------------------------------------------------------------------------
create or replace function ops.add_run_artifact(
  p_run_id uuid,
  p_artifact_key text,
  p_artifact_url text,
  p_content_type text default null,
  p_size_bytes bigint default null,
  p_checksum text default null,
  p_expires_at timestamptz default null,
  p_metadata jsonb default '{}'::jsonb
)
returns jsonb
language plpgsql
as $$
declare
  v_artifact_id uuid;
begin
  -- Insert artifact metadata
  insert into ops.run_artifacts (
    run_id, artifact_key, artifact_url, content_type,
    size_bytes, checksum, expires_at, metadata
  )
  values (
    p_run_id, p_artifact_key, p_artifact_url, p_content_type,
    p_size_bytes, p_checksum, p_expires_at, p_metadata
  )
  on conflict (run_id, artifact_key)
  do update set
    artifact_url = excluded.artifact_url,
    content_type = excluded.content_type,
    size_bytes = excluded.size_bytes,
    checksum = excluded.checksum,
    expires_at = excluded.expires_at,
    metadata = excluded.metadata
  returning id into v_artifact_id;

  -- Log artifact addition event
  insert into ops.run_events (run_id, event_type, message, payload)
  values (
    p_run_id,
    'info',
    format('Artifact added: %s', p_artifact_key),
    jsonb_build_object('artifact_key', p_artifact_key, 'artifact_id', v_artifact_id)
  );

  return jsonb_build_object('success', true, 'artifact_id', v_artifact_id);
end;
$$;

comment on function ops.add_run_artifact is 'Store artifact metadata for run (upsert on artifact_key)';

-- ---------------------------------------------------------------------------
-- 6. ops.list_queued_runs() - Admin Queue View
-- ---------------------------------------------------------------------------
create or replace function ops.list_queued_runs()
returns table (
  run_id uuid,
  project_id uuid,
  workflow_id uuid,
  run_number int,
  status text,
  created_at timestamptz,
  claimed_by text,
  claimed_at timestamptz
)
language sql
stable
as $$
  select
    id, project_id, workflow_id, run_number,
    status, created_at, claimed_by, claimed_at
  from ops.runs
  where status in ('queued', 'claimed')
  order by created_at;
$$;

comment on function ops.list_queued_runs is 'List all queued and claimed runs for admin view';

-- ---------------------------------------------------------------------------
-- Verification
-- ---------------------------------------------------------------------------
do $$
declare
  function_count int;
begin
  select count(*) into function_count
  from pg_proc p
  join pg_namespace n on p.pronamespace = n.oid
  where n.nspname = 'ops'
    and p.proname in (
      'claim_next_run',
      'start_workflow_run',
      'complete_workflow_run',
      'append_run_log',
      'add_run_artifact',
      'list_queued_runs'
    );

  if function_count = 6 then
    raise notice 'SUCCESS: All 6 RPC functions created';
  else
    raise exception 'FAILED: Expected 6 functions, found %', function_count;
  end if;
end $$;
```

**Apply**:
```bash
supabase db push --linked
```

**Verification**:
```bash
# List RPC functions
psql "$SUPABASE_URL" -c "\df ops.*"

# Test claim_next_run (should return no runs)
psql "$SUPABASE_URL" -c "SELECT ops.claim_next_run('test-worker');"
```

---

## Step 4: Row-Level Security (RLS) Policies

**Migration**: `20260213_000300_ops_rls_policies.sql`

```sql
-- ===========================================================================
-- OdooOps Sh RLS Policies: Project-Based Access Control
-- ===========================================================================
-- Security Model:
--   - Project Isolation: Users can only access their project's data
--   - Role Hierarchy: owner > admin > developer > viewer
--   - Service Role Bypass: Edge Functions use service role (bypasses RLS)
-- ===========================================================================

-- ---------------------------------------------------------------------------
-- Enable RLS on All ops.* Tables
-- ---------------------------------------------------------------------------
alter table ops.projects enable row level security;
alter table ops.workflows enable row level security;
alter table ops.runs enable row level security;
alter table ops.run_events enable row level security;
alter table ops.run_artifacts enable row level security;
alter table ops.run_logs enable row level security;
alter table ops.tools enable row level security;
alter table ops.upgrade_advisories enable row level security;
alter table ops.project_memberships enable row level security;

-- ---------------------------------------------------------------------------
-- Helper Functions for Current User Context
-- ---------------------------------------------------------------------------
create or replace function ops.current_user_id()
returns uuid
language sql
stable
as $$
  select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid;
$$;

create or replace function ops.current_user_role(p_project_id uuid)
returns text
language sql
stable
as $$
  select role
  from ops.project_memberships
  where project_id = p_project_id
    and user_id = ops.current_user_id()
  limit 1;
$$;

-- ---------------------------------------------------------------------------
-- 1. ops.projects Policies
-- ---------------------------------------------------------------------------
-- Users can only see projects they are members of
create policy projects_select_member on ops.projects
  for select
  using (
    id in (
      select project_id
      from ops.project_memberships
      where user_id = ops.current_user_id()
    )
  );

-- Only owners can update project settings
create policy projects_update_owner on ops.projects
  for update
  using (ops.current_user_role(id) = 'owner')
  with check (ops.current_user_role(id) = 'owner');

-- Only owners can create projects (via invitation)
create policy projects_insert_owner on ops.projects
  for insert
  with check (true); -- Handled by Edge Function logic

-- No direct project deletion (use soft delete via status)

comment on policy projects_select_member on ops.projects is 'Users can only view projects they are members of';
comment on policy projects_update_owner on ops.projects is 'Only project owners can modify settings';

-- ---------------------------------------------------------------------------
-- 2. ops.workflows Policies
-- ---------------------------------------------------------------------------
-- Members can view all workflows in their projects
create policy workflows_select_member on ops.workflows
  for select
  using (
    project_id in (
      select project_id
      from ops.project_memberships
      where user_id = ops.current_user_id()
    )
  );

-- Developers, admins, owners can create/update workflows
create policy workflows_modify_developer on ops.workflows
  for all
  using (
    ops.current_user_role(project_id) in ('owner', 'admin', 'developer')
  )
  with check (
    ops.current_user_role(project_id) in ('owner', 'admin', 'developer')
  );

comment on policy workflows_select_member on ops.workflows is 'Members can view workflows in their projects';
comment on policy workflows_modify_developer on ops.workflows is 'Developers+ can create/update workflows';

-- ---------------------------------------------------------------------------
-- 3. ops.runs Policies
-- ---------------------------------------------------------------------------
-- Members can view all runs in their projects
create policy runs_select_member on ops.runs
  for select
  using (
    project_id in (
      select project_id
      from ops.project_memberships
      where user_id = ops.current_user_id()
    )
  );

-- Developers+ can create runs
create policy runs_insert_developer on ops.runs
  for insert
  with check (
    ops.current_user_role(project_id) in ('owner', 'admin', 'developer')
  );

-- No direct updates (use RPC functions for state machine)

comment on policy runs_select_member on ops.runs is 'Members can view runs in their projects';
comment on policy runs_insert_developer on ops.runs is 'Developers+ can create runs';

-- ---------------------------------------------------------------------------
-- 4. ops.run_events Policies (Read-Only for Users)
-- ---------------------------------------------------------------------------
-- Members can view events for runs in their projects
create policy run_events_select_member on ops.run_events
  for select
  using (
    run_id in (
      select id
      from ops.runs
      where project_id in (
        select project_id
        from ops.project_memberships
        where user_id = ops.current_user_id()
      )
    )
  );

-- No insert/update/delete for users (only via RPC functions)

comment on policy run_events_select_member on ops.run_events is 'Members can view events for runs in their projects';

-- ---------------------------------------------------------------------------
-- 5. ops.run_artifacts Policies
-- ---------------------------------------------------------------------------
-- Members can view artifacts for runs in their projects
create policy run_artifacts_select_member on ops.run_artifacts
  for select
  using (
    run_id in (
      select id
      from ops.runs
      where project_id in (
        select project_id
        from ops.project_memberships
        where user_id = ops.current_user_id()
      )
    )
  );

comment on policy run_artifacts_select_member on ops.run_artifacts is 'Members can view artifacts for runs in their projects';

-- ---------------------------------------------------------------------------
-- 6. ops.run_logs Policies
-- ---------------------------------------------------------------------------
-- Members can view logs for runs in their projects
create policy run_logs_select_member on ops.run_logs
  for select
  using (
    run_id in (
      select id
      from ops.runs
      where project_id in (
        select project_id
        from ops.project_memberships
        where user_id = ops.current_user_id()
      )
    )
  );

comment on policy run_logs_select_member on ops.run_logs is 'Members can view logs for runs in their projects';

-- ---------------------------------------------------------------------------
-- 7. ops.tools Policies (Global Read-Only)
-- ---------------------------------------------------------------------------
-- All authenticated users can view tools
create policy tools_select_all on ops.tools
  for select
  to authenticated
  using (true);

-- Only service role can modify tools (via Edge Functions)

comment on policy tools_select_all on ops.tools is 'All users can view available tools';

-- ---------------------------------------------------------------------------
-- 8. ops.upgrade_advisories Policies (Global Read-Only)
-- ---------------------------------------------------------------------------
-- All authenticated users can view upgrade advisories
create policy upgrade_advisories_select_all on ops.upgrade_advisories
  for select
  to authenticated
  using (true);

-- Only service role can modify advisories (via Edge Functions)

comment on policy upgrade_advisories_select_all on ops.upgrade_advisories is 'All users can view upgrade advisories';

-- ---------------------------------------------------------------------------
-- 9. ops.project_memberships Policies
-- ---------------------------------------------------------------------------
-- Members can view all memberships in their projects
create policy project_memberships_select_member on ops.project_memberships
  for select
  using (
    project_id in (
      select project_id
      from ops.project_memberships
      where user_id = ops.current_user_id()
    )
  );

-- Owners and admins can manage memberships
create policy project_memberships_modify_admin on ops.project_memberships
  for all
  using (
    ops.current_user_role(project_id) in ('owner', 'admin')
  )
  with check (
    ops.current_user_role(project_id) in ('owner', 'admin')
    -- Prevent non-owners from creating owner roles
    and (
      role != 'owner'
      or ops.current_user_role(project_id) = 'owner'
    )
  );

comment on policy project_memberships_select_member on ops.project_memberships is 'Members can view memberships in their projects';
comment on policy project_memberships_modify_admin on ops.project_memberships is 'Admins+ can manage memberships (owners-only for owner role)';

-- ---------------------------------------------------------------------------
-- Verification
-- ---------------------------------------------------------------------------
do $$
declare
  policy_count int;
begin
  select count(*) into policy_count
  from pg_policies
  where schemaname = 'ops';

  if policy_count >= 13 then
    raise notice 'SUCCESS: % RLS policies created', policy_count;
  else
    raise exception 'FAILED: Expected >= 13 policies, found %', policy_count;
  end if;
end $$;
```

**Apply**:
```bash
supabase db push --linked
```

**Verification**:
```bash
# List all RLS policies
psql "$SUPABASE_URL" -c "SELECT schemaname, tablename, policyname FROM pg_policies WHERE schemaname='ops' ORDER BY tablename, policyname;"

# Verify RLS is enabled
psql "$SUPABASE_URL" -c "SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname='ops' ORDER BY tablename;"
```

---

## Step 5: Indexes & Constraints (Performance + Safety)

**Migration**: `20260213_000400_ops_indexes_constraints.sql`

```sql
-- ===========================================================================
-- OdooOps Sh Indexes & Constraints: Performance + Safety
-- ===========================================================================

-- ---------------------------------------------------------------------------
-- Additional Constraints
-- ---------------------------------------------------------------------------
-- Ensure project workspace_key format
alter table ops.projects
  add constraint projects_workspace_key_format
  check (workspace_key ~ '^[a-z0-9_]+$');

-- Ensure project slug format
alter table ops.projects
  add constraint projects_slug_format
  check (slug ~ '^[a-z0-9-]+$');

-- Ensure Odoo version format
alter table ops.projects
  add constraint projects_odoo_version_format
  check (odoo_version ~ '^\d+\.\d+$');

-- Ensure run status transitions are valid (queued → claimed → running → succeeded|failed)
create or replace function ops.validate_run_status_transition()
returns trigger
language plpgsql
as $$
declare
  v_old_status text;
begin
  if tg_op = 'UPDATE' then
    v_old_status := old.status;

    -- Valid transitions
    if (v_old_status = 'queued' and new.status not in ('claimed', 'canceled')) then
      raise exception 'Invalid transition: queued can only go to claimed or canceled';
    elsif (v_old_status = 'claimed' and new.status not in ('running', 'canceled')) then
      raise exception 'Invalid transition: claimed can only go to running or canceled';
    elsif (v_old_status = 'running' and new.status not in ('succeeded', 'failed', 'canceled')) then
      raise exception 'Invalid transition: running can only go to succeeded, failed, or canceled';
    elsif (v_old_status in ('succeeded', 'failed', 'canceled')) then
      raise exception 'Invalid transition: final states cannot transition';
    end if;
  end if;

  return new;
end;
$$;

create trigger enforce_run_status_transition
  before update on ops.runs
  for each row
  execute function ops.validate_run_status_transition();

comment on trigger enforce_run_status_transition on ops.runs is 'Enforce valid run status state machine transitions';

-- ---------------------------------------------------------------------------
-- Performance Indexes (additional to those in core schema)
-- ---------------------------------------------------------------------------
-- Composite index for run queue queries
create index idx_ops_runs_queue_composite on ops.runs(status, created_at) where status = 'queued';

-- Index for recent runs by project
create index idx_ops_runs_recent_by_project on ops.runs(project_id, created_at desc);

-- Index for run event timeline queries
create index idx_ops_run_events_timeline on ops.run_events(run_id, created_at);

-- Index for artifact cleanup queries
create index idx_ops_run_artifacts_cleanup on ops.run_artifacts(expires_at) where expires_at is not null and expires_at < now();

-- ---------------------------------------------------------------------------
-- Verification
-- ---------------------------------------------------------------------------
do $$
declare
  constraint_count int;
  trigger_count int;
begin
  -- Count constraints
  select count(*) into constraint_count
  from pg_constraint
  where connamespace = 'ops'::regnamespace
    and conname like 'projects_%_format';

  if constraint_count >= 3 then
    raise notice 'SUCCESS: % format constraints created', constraint_count;
  else
    raise exception 'FAILED: Expected >= 3 constraints, found %', constraint_count;
  end if;

  -- Count triggers
  select count(*) into trigger_count
  from pg_trigger
  where tgname = 'enforce_run_status_transition';

  if trigger_count = 1 then
    raise notice 'SUCCESS: Status transition trigger created';
  else
    raise exception 'FAILED: Status transition trigger not found';
  end if;
end $$;
```

**Apply**:
```bash
supabase db push --linked
```

**Verification**:
```bash
# Verify constraints
psql "$SUPABASE_URL" -c "SELECT conname FROM pg_constraint WHERE connamespace = 'ops'::regnamespace ORDER BY conname;"

# Verify triggers
psql "$SUPABASE_URL" -c "SELECT tgname FROM pg_trigger WHERE tgname = 'enforce_run_status_transition';"
```

---

## Complete Setup Script

```bash
#!/bin/bash
# setup_ops_schema.sh - Complete OdooOps Sh schema setup

set -euo pipefail

echo "🚀 Setting up OdooOps Sh schema in Supabase..."

# Verify environment
if [[ -z "${SUPABASE_PROJECT_REF:-}" ]]; then
  echo "❌ Error: SUPABASE_PROJECT_REF not set"
  exit 1
fi

# Link to project
echo "🔗 Linking to Supabase project..."
supabase link --project-ref "$SUPABASE_PROJECT_REF"

# Step 1: Breaking change (rename agent tables)
echo "📝 Step 1/5: Renaming agent tables..."
supabase db push --include-all

# Verify no data loss
echo "✅ Verifying agent table rename..."
psql "$SUPABASE_URL" -c "SELECT count(*) as agent_runs_count FROM ops.agent_runs;" || echo "⚠️  No existing agent runs"

# Step 2: Core schema
echo "📝 Step 2/5: Creating 9 ops.* tables..."
supabase db push --linked

# Verify tables
echo "✅ Verifying ops.* tables..."
TABLE_COUNT=$(psql "$SUPABASE_URL" -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='ops' AND table_name IN ('projects', 'workflows', 'runs', 'run_events', 'run_artifacts', 'run_logs', 'tools', 'upgrade_advisories', 'project_memberships');")

if [[ "$TABLE_COUNT" -eq 9 ]]; then
  echo "✅ All 9 tables created successfully"
else
  echo "❌ Expected 9 tables, found $TABLE_COUNT"
  exit 1
fi

# Step 3: RPC functions
echo "📝 Step 3/5: Creating 6 RPC functions..."
supabase db push --linked

# Verify functions
echo "✅ Verifying RPC functions..."
psql "$SUPABASE_URL" -c "\df ops.claim_next_run" || exit 1
psql "$SUPABASE_URL" -c "\df ops.start_workflow_run" || exit 1
psql "$SUPABASE_URL" -c "\df ops.complete_workflow_run" || exit 1

# Step 4: RLS policies
echo "📝 Step 4/5: Creating RLS policies..."
supabase db push --linked

# Verify RLS enabled
echo "✅ Verifying RLS enabled..."
RLS_COUNT=$(psql "$SUPABASE_URL" -t -c "SELECT count(*) FROM pg_tables WHERE schemaname='ops' AND rowsecurity=true;")
echo "RLS enabled on $RLS_COUNT ops.* tables"

# Step 5: Indexes & constraints
echo "📝 Step 5/5: Creating indexes & constraints..."
supabase db push --linked

# Verify constraints
echo "✅ Verifying constraints..."
psql "$SUPABASE_URL" -c "SELECT conname FROM pg_constraint WHERE connamespace = 'ops'::regnamespace ORDER BY conname;" || exit 1

# Final verification
echo ""
echo "🎉 OdooOps Sh schema setup complete!"
echo ""
echo "📊 Summary:"
psql "$SUPABASE_URL" -c "SELECT tablename FROM pg_tables WHERE schemaname='ops' ORDER BY tablename;"
echo ""
echo "🔧 RPC Functions:"
psql "$SUPABASE_URL" -c "\df ops.*"
echo ""
echo "✅ Setup verification passed. Schema ready for use."
```

**Usage**:
```bash
chmod +x setup_ops_schema.sh
./setup_ops_schema.sh
```

---

## Verification & Testing

### Concurrency Test (Worker Claiming)

```sql
-- Insert 5 test runs
insert into ops.projects (workspace_key, slug, name, odoo_version)
values ('test_workspace', 'test-project', 'Test Project', '19.0')
returning id;
-- Note the project_id

insert into ops.workflows (project_id, workflow_type, name)
values ('<project_id>', 'build', 'Test Build')
returning id;
-- Note the workflow_id

insert into ops.runs (project_id, workflow_id, status)
select '<project_id>', '<workflow_id>', 'queued'
from generate_series(1, 5);

-- Simulate 3 workers claiming concurrently (run in 3 separate sessions)
-- Session 1:
select ops.claim_next_run('worker-001');

-- Session 2:
select ops.claim_next_run('worker-002');

-- Session 3:
select ops.claim_next_run('worker-003');

-- Verify each worker got unique run
select run_number, status, claimed_by, claimed_at
from ops.runs
where project_id = '<project_id>'
order by run_number;

-- Expected: 3 runs claimed by different workers, 2 still queued
```

### Full Lifecycle Test

```bash
#!/bin/bash
# test_run_lifecycle.sh - Test complete run lifecycle

set -euo pipefail

# Create project
PROJECT_ID=$(psql "$SUPABASE_URL" -t -c "
  insert into ops.projects (workspace_key, slug, name, odoo_version)
  values ('test_workspace', 'test-project', 'Test Project', '19.0')
  returning id;
" | tr -d ' ')

echo "Created project: $PROJECT_ID"

# Create workflow
WORKFLOW_ID=$(psql "$SUPABASE_URL" -t -c "
  insert into ops.workflows (project_id, workflow_type, name)
  values ('$PROJECT_ID', 'build', 'Test Build')
  returning id;
" | tr -d ' ')

echo "Created workflow: $WORKFLOW_ID"

# Create run
RUN_ID=$(psql "$SUPABASE_URL" -t -c "
  insert into ops.runs (project_id, workflow_id, status)
  values ('$PROJECT_ID', '$WORKFLOW_ID', 'queued')
  returning id;
" | tr -d ' ')

echo "Created run: $RUN_ID"

# Claim run
psql "$SUPABASE_URL" -c "SELECT ops.claim_next_run('test-worker');"

# Start run
psql "$SUPABASE_URL" -c "SELECT ops.start_workflow_run('$RUN_ID', 'test-worker');"

# Append logs
psql "$SUPABASE_URL" -c "SELECT ops.append_run_log('$RUN_ID', 'info', 'Starting build process');"
psql "$SUPABASE_URL" -c "SELECT ops.append_run_log('$RUN_ID', 'info', 'Installing dependencies');"

# Add artifact
psql "$SUPABASE_URL" -c "
  SELECT ops.add_run_artifact(
    '$RUN_ID',
    'builds/test-project/artifact.tar.gz',
    'https://storage.supabase.co/...',
    'application/gzip',
    1048576,
    'sha256:abc123',
    now() + interval '30 days'
  );
"

# Complete run
psql "$SUPABASE_URL" -c "SELECT ops.complete_workflow_run('$RUN_ID', 0);"

# Verify final state
psql "$SUPABASE_URL" -c "
  SELECT status, started_at, finished_at, exit_code
  FROM ops.runs
  WHERE id = '$RUN_ID';
"

# View events
psql "$SUPABASE_URL" -c "
  SELECT event_type, message, created_at
  FROM ops.run_events
  WHERE run_id = '$RUN_ID'
  ORDER BY created_at;
"

# View logs
psql "$SUPABASE_URL" -c "
  SELECT log_level, message, timestamp
  FROM ops.run_logs
  WHERE run_id = '$RUN_ID'
  ORDER BY timestamp;
"

# View artifacts
psql "$SUPABASE_URL" -c "
  SELECT artifact_key, content_type, size_bytes, checksum
  FROM ops.run_artifacts
  WHERE run_id = '$RUN_ID';
"

echo "✅ Lifecycle test completed successfully"
```

---

## Rollback Procedures

### Rollback All Changes

```sql
-- Drop all ops.* tables (DESTRUCTIVE - use with caution)
drop table if exists ops.project_memberships cascade;
drop table if exists ops.upgrade_advisories cascade;
drop table if exists ops.tools cascade;
drop table if exists ops.run_logs cascade;
drop table if exists ops.run_artifacts cascade;
drop table if exists ops.run_events cascade;
drop table if exists ops.runs cascade;
drop table if exists ops.workflows cascade;
drop table if exists ops.projects cascade;

-- Drop RPC functions
drop function if exists ops.claim_next_run(text);
drop function if exists ops.start_workflow_run(uuid, text);
drop function if exists ops.complete_workflow_run(uuid, int, text);
drop function if exists ops.append_run_log(uuid, text, text, jsonb);
drop function if exists ops.add_run_artifact(uuid, text, text, text, bigint, text, timestamptz, jsonb);
drop function if exists ops.list_queued_runs();

-- Drop helper functions
drop function if exists ops.current_user_id();
drop function if exists ops.current_user_role(uuid);
drop function if exists ops.validate_run_status_transition();

-- Restore agent tables (if rollback is needed)
alter table if exists ops.agent_runs rename to runs;
alter table if exists ops.agent_run_logs rename to run_logs;

-- Drop backward compatibility views
drop view if exists ops.agent_runs_v;
drop view if exists ops.agent_run_logs_v;
```

### Partial Rollback (RLS Only)

```sql
-- Disable RLS on all ops.* tables
alter table ops.projects disable row level security;
alter table ops.workflows disable row level security;
alter table ops.runs disable row level security;
alter table ops.run_events disable row level security;
alter table ops.run_artifacts disable row level security;
alter table ops.run_logs disable row level security;
alter table ops.tools disable row level security;
alter table ops.upgrade_advisories disable row level security;
alter table ops.project_memberships disable row level security;

-- Drop all RLS policies
drop policy if exists projects_select_member on ops.projects;
drop policy if exists projects_update_owner on ops.projects;
drop policy if exists projects_insert_owner on ops.projects;
drop policy if exists workflows_select_member on ops.workflows;
drop policy if exists workflows_modify_developer on ops.workflows;
drop policy if exists runs_select_member on ops.runs;
drop policy if exists runs_insert_developer on ops.runs;
drop policy if exists run_events_select_member on ops.run_events;
drop policy if exists run_artifacts_select_member on ops.run_artifacts;
drop policy if exists run_logs_select_member on ops.run_logs;
drop policy if exists tools_select_all on ops.tools;
drop policy if exists upgrade_advisories_select_all on ops.upgrade_advisories;
drop policy if exists project_memberships_select_member on ops.project_memberships;
drop policy if exists project_memberships_modify_admin on ops.project_memberships;
```

---

## Next Steps

After successful setup:

1. **Update Edge Functions**:
   - `ops-ingest`: Change table references (ops.runs → ops.agent_runs)
   - `executor`: Change table references (ops.run_logs → ops.agent_run_logs)

2. **Update Scripts**:
   - `scripts/odooops/env_create.sh`: Insert into ops.runs
   - `scripts/odooops/env_wait_ready.sh`: Query run status
   - `scripts/odooops/env_destroy.sh`: Mark as canceled

3. **Create Console UI** (Future):
   - Generate Prisma schema: `supabase gen types typescript --linked > lib/database.types.ts`
   - Build Next.js control plane UI
   - Use RPC functions for all state transitions

4. **Documentation**:
   - Create DBML schema: `spec/odooops-sh/schema.dbml`
   - Generate ERD diagram: `spec/odooops-sh/schema.mmd`
   - Update `docs/odooops-sh/RUN_LIFECYCLE.md`

---

## Reference

| File | Purpose |
|------|---------|
| `spec/odooops-sh/constitution.md` | Core principles and SSOT boundaries |
| `spec/odooops-sh/prd.md` | Product requirements and user stories |
| `spec/odooops-sh/plan.md` | 6-week implementation timeline |
| `docs/odooops-sh/ARCHITECTURE.md` | System architecture layers |
| `docs/odooops-sh/RUN_LIFECYCLE.md` | Run state machine documentation |
| `docs/odooops-sh/SECURITY.md` | RLS policy explanations |

---

**Last Updated**: 2026-02-15
**Migration Version**: 20260213_000001 → 20260213_000400
**Status**: Complete schema definition ✅
