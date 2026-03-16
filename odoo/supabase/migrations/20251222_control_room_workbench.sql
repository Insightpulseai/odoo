-- =============================================================================
-- Control Room Workbench Schema
-- Provides Databricks-like primitives for job orchestration, runs, artifacts,
-- and lineage tracking.
--
-- Migration: 20251222_control_room_workbench
-- Author: Claude Code Agent
-- Date: 2025-12-22
-- =============================================================================

-- Create control_room schema
create schema if not exists control_room;

-- =============================================================================
-- JOBS: Job definitions (like Databricks Jobs)
-- =============================================================================
create table if not exists control_room.jobs (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  engine text not null default 'agent',  -- agent, spark, python, shell
  entrypoint text,                        -- path to main file/function
  spec jsonb not null default '{}'::jsonb,  -- job configuration
  schedule text,                          -- cron expression (optional)
  owner text,                             -- team/user owner
  tags text[] default array[]::text[],
  enabled boolean default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  -- Constraints
  constraint jobs_name_unique unique (name)
);

-- Index for job lookups
create index if not exists idx_jobs_owner on control_room.jobs(owner);
create index if not exists idx_jobs_tags on control_room.jobs using gin(tags);
create index if not exists idx_jobs_enabled on control_room.jobs(enabled) where enabled = true;

-- =============================================================================
-- RUNS: Job execution runs (like Databricks Runs)
-- =============================================================================
create table if not exists control_room.runs (
  id uuid primary key default gen_random_uuid(),
  job_id uuid references control_room.jobs(id) on delete set null,
  job_name text,                          -- denormalized for fast lookup
  trigger_type text not null default 'manual',  -- manual, schedule, webhook, spec_change
  trigger_source text,                    -- who/what triggered it
  status text not null default 'pending',  -- pending, running, success, failed, cancelled
  started_at timestamptz default now(),
  finished_at timestamptz,
  duration_ms bigint,                     -- computed on completion
  logs_url text,                          -- link to full logs
  error_message text,                     -- if failed
  meta jsonb default '{}'::jsonb,         -- additional metadata

  -- For Continue headless runs
  spec_slug text,                         -- spec/<slug>
  pr_number integer,                      -- if PR was created
  commit_sha text,                        -- git commit

  created_at timestamptz not null default now()
);

-- Indexes for run queries
create index if not exists idx_runs_job_id on control_room.runs(job_id);
create index if not exists idx_runs_status on control_room.runs(status);
create index if not exists idx_runs_started_at on control_room.runs(started_at desc);
create index if not exists idx_runs_spec_slug on control_room.runs(spec_slug);

-- =============================================================================
-- RUN_STEPS: Individual steps within a run
-- =============================================================================
create table if not exists control_room.run_steps (
  id bigserial primary key,
  run_id uuid not null references control_room.runs(id) on delete cascade,
  step_number integer not null,
  name text not null,
  status text not null default 'pending',  -- pending, running, success, failed, skipped
  started_at timestamptz,
  finished_at timestamptz,
  output text,                             -- step output/logs
  error text,                              -- if failed
  meta jsonb default '{}'::jsonb,

  created_at timestamptz not null default now(),

  -- Ensure unique step numbers per run
  constraint run_steps_run_number unique (run_id, step_number)
);

-- Index for step queries
create index if not exists idx_run_steps_run_id on control_room.run_steps(run_id);

-- =============================================================================
-- ARTIFACTS: Run outputs (like Databricks Artifacts)
-- =============================================================================
create table if not exists control_room.artifacts (
  id bigserial primary key,
  run_id uuid references control_room.runs(id) on delete set null,
  name text not null,
  type text not null,                     -- table, file, report, model, pr, commit
  uri text not null,                      -- storage location or reference
  size_bytes bigint,
  checksum text,                          -- for deduplication
  meta jsonb default '{}'::jsonb,

  created_at timestamptz not null default now()
);

-- Indexes for artifact queries
create index if not exists idx_artifacts_run_id on control_room.artifacts(run_id);
create index if not exists idx_artifacts_type on control_room.artifacts(type);
create index if not exists idx_artifacts_uri on control_room.artifacts(uri);

-- =============================================================================
-- LINEAGE_EDGES: Data lineage graph (like Unity Catalog Lineage)
-- =============================================================================
create table if not exists control_room.lineage_edges (
  id bigserial primary key,
  run_id uuid references control_room.runs(id) on delete set null,
  src text not null,                      -- source entity (table, file, spec)
  dst text not null,                      -- destination entity
  kind text not null,                     -- read, write, transform, depends_on
  meta jsonb default '{}'::jsonb,

  created_at timestamptz not null default now(),

  -- Prevent duplicate edges for same run
  constraint lineage_edges_unique unique (run_id, src, dst, kind)
);

-- Indexes for lineage queries
create index if not exists idx_lineage_run_id on control_room.lineage_edges(run_id);
create index if not exists idx_lineage_src on control_room.lineage_edges(src);
create index if not exists idx_lineage_dst on control_room.lineage_edges(dst);

-- =============================================================================
-- CATALOG_ENTITIES: Data catalog (like Unity Catalog)
-- =============================================================================
create table if not exists control_room.catalog_entities (
  id uuid primary key default gen_random_uuid(),
  entity_type text not null,              -- table, file, model, spec, job
  name text not null,
  full_name text not null,                -- schema.table or path
  description text,
  owner text,
  domain text,                            -- finance-ppm, hr, etc.
  schema_def jsonb,                       -- column definitions for tables
  tags text[] default array[]::text[],
  meta jsonb default '{}'::jsonb,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint catalog_full_name_unique unique (full_name)
);

-- Indexes for catalog queries
create index if not exists idx_catalog_entity_type on control_room.catalog_entities(entity_type);
create index if not exists idx_catalog_domain on control_room.catalog_entities(domain);
create index if not exists idx_catalog_tags on control_room.catalog_entities using gin(tags);

-- =============================================================================
-- PERMISSIONS: Access control (simplified Unity Catalog style)
-- =============================================================================
create table if not exists control_room.permissions (
  id bigserial primary key,
  principal text not null,                -- user email, role, or group
  principal_type text not null default 'user',  -- user, role, group
  resource_type text not null,            -- job, catalog, run
  resource_id text not null,              -- * for all, or specific ID
  permission text not null,               -- read, write, execute, admin
  granted_by text,
  granted_at timestamptz not null default now(),

  constraint permissions_unique unique (principal, resource_type, resource_id, permission)
);

-- Index for permission lookups
create index if not exists idx_permissions_principal on control_room.permissions(principal);
create index if not exists idx_permissions_resource on control_room.permissions(resource_type, resource_id);

-- =============================================================================
-- WEBHOOKS: Callback configurations
-- =============================================================================
create table if not exists control_room.webhooks (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  url text not null,
  events text[] not null,                 -- run.started, run.completed, run.failed
  secret text,                            -- for signing
  enabled boolean default true,

  created_at timestamptz not null default now()
);

-- =============================================================================
-- VIEWS: Useful aggregations
-- =============================================================================

-- Recent runs view
create or replace view control_room.recent_runs as
select
  r.id,
  r.job_name,
  r.status,
  r.trigger_type,
  r.spec_slug,
  r.pr_number,
  r.started_at,
  r.finished_at,
  r.duration_ms,
  r.error_message,
  (select count(*) from control_room.artifacts a where a.run_id = r.id) as artifact_count,
  (select count(*) from control_room.lineage_edges l where l.run_id = r.id) as lineage_count
from control_room.runs r
order by r.started_at desc
limit 100;

-- Job stats view
create or replace view control_room.job_stats as
select
  j.id,
  j.name,
  j.engine,
  j.owner,
  (select count(*) from control_room.runs r where r.job_id = j.id) as total_runs,
  (select count(*) from control_room.runs r where r.job_id = j.id and r.status = 'success') as success_count,
  (select count(*) from control_room.runs r where r.job_id = j.id and r.status = 'failed') as failed_count,
  (select max(r.started_at) from control_room.runs r where r.job_id = j.id) as last_run_at
from control_room.jobs j;

-- Lineage graph view (for visualization)
create or replace view control_room.lineage_graph as
select
  le.src,
  le.dst,
  le.kind,
  count(*) as edge_count,
  max(le.created_at) as last_seen
from control_room.lineage_edges le
group by le.src, le.dst, le.kind;

-- =============================================================================
-- FUNCTIONS: Utility functions
-- =============================================================================

-- Function to get upstream lineage (what does this entity depend on?)
create or replace function control_room.get_upstream(
  p_entity text,
  p_depth integer default 3
)
returns table (
  entity text,
  kind text,
  depth integer
)
language sql stable
as $$
  with recursive upstream as (
    -- Base case: direct dependencies
    select le.src as entity, le.kind, 1 as depth
    from control_room.lineage_edges le
    where le.dst = p_entity

    union all

    -- Recursive case: dependencies of dependencies
    select le.src, le.kind, u.depth + 1
    from control_room.lineage_edges le
    join upstream u on le.dst = u.entity
    where u.depth < p_depth
  )
  select distinct entity, kind, min(depth) as depth
  from upstream
  group by entity, kind
  order by depth, entity;
$$;

-- Function to get downstream lineage (what depends on this entity?)
create or replace function control_room.get_downstream(
  p_entity text,
  p_depth integer default 3
)
returns table (
  entity text,
  kind text,
  depth integer
)
language sql stable
as $$
  with recursive downstream as (
    -- Base case: direct dependents
    select le.dst as entity, le.kind, 1 as depth
    from control_room.lineage_edges le
    where le.src = p_entity

    union all

    -- Recursive case: dependents of dependents
    select le.dst, le.kind, d.depth + 1
    from control_room.lineage_edges le
    join downstream d on le.src = d.entity
    where d.depth < p_depth
  )
  select distinct entity, kind, min(depth) as depth
  from downstream
  group by entity, kind
  order by depth, entity;
$$;

-- Function to create a new run
create or replace function control_room.create_run(
  p_job_id uuid default null,
  p_job_name text default null,
  p_trigger_type text default 'manual',
  p_trigger_source text default null,
  p_spec_slug text default null,
  p_meta jsonb default '{}'::jsonb
)
returns uuid
language plpgsql
as $$
declare
  v_run_id uuid;
  v_job_name text;
begin
  -- Get job name if job_id provided
  if p_job_id is not null then
    select name into v_job_name from control_room.jobs where id = p_job_id;
  else
    v_job_name := p_job_name;
  end if;

  insert into control_room.runs (
    job_id, job_name, trigger_type, trigger_source, spec_slug, meta
  ) values (
    p_job_id, v_job_name, p_trigger_type, p_trigger_source, p_spec_slug, p_meta
  )
  returning id into v_run_id;

  return v_run_id;
end;
$$;

-- Function to complete a run
create or replace function control_room.complete_run(
  p_run_id uuid,
  p_status text,
  p_error_message text default null,
  p_pr_number integer default null,
  p_commit_sha text default null
)
returns void
language plpgsql
as $$
begin
  update control_room.runs
  set
    status = p_status,
    finished_at = now(),
    duration_ms = extract(epoch from (now() - started_at)) * 1000,
    error_message = p_error_message,
    pr_number = coalesce(p_pr_number, pr_number),
    commit_sha = coalesce(p_commit_sha, commit_sha)
  where id = p_run_id;
end;
$$;

-- =============================================================================
-- RLS POLICIES: Row Level Security
-- =============================================================================

-- Enable RLS on all tables
alter table control_room.jobs enable row level security;
alter table control_room.runs enable row level security;
alter table control_room.run_steps enable row level security;
alter table control_room.artifacts enable row level security;
alter table control_room.lineage_edges enable row level security;
alter table control_room.catalog_entities enable row level security;
alter table control_room.permissions enable row level security;
alter table control_room.webhooks enable row level security;

-- Service role can do everything
create policy "Service role full access on jobs"
  on control_room.jobs for all
  to service_role
  using (true);

create policy "Service role full access on runs"
  on control_room.runs for all
  to service_role
  using (true);

create policy "Service role full access on run_steps"
  on control_room.run_steps for all
  to service_role
  using (true);

create policy "Service role full access on artifacts"
  on control_room.artifacts for all
  to service_role
  using (true);

create policy "Service role full access on lineage_edges"
  on control_room.lineage_edges for all
  to service_role
  using (true);

create policy "Service role full access on catalog_entities"
  on control_room.catalog_entities for all
  to service_role
  using (true);

create policy "Service role full access on permissions"
  on control_room.permissions for all
  to service_role
  using (true);

create policy "Service role full access on webhooks"
  on control_room.webhooks for all
  to service_role
  using (true);

-- Authenticated users can read jobs and runs
create policy "Authenticated read jobs"
  on control_room.jobs for select
  to authenticated
  using (true);

create policy "Authenticated read runs"
  on control_room.runs for select
  to authenticated
  using (true);

create policy "Authenticated read artifacts"
  on control_room.artifacts for select
  to authenticated
  using (true);

create policy "Authenticated read lineage"
  on control_room.lineage_edges for select
  to authenticated
  using (true);

create policy "Authenticated read catalog"
  on control_room.catalog_entities for select
  to authenticated
  using (true);

-- =============================================================================
-- SEED DATA: Default jobs for Continue workflow
-- =============================================================================

insert into control_room.jobs (name, description, engine, spec) values
  ('continue-spec-validate', 'Validate spec bundles', 'shell', '{"script": "./scripts/validate-spec-kit.sh"}'),
  ('continue-policy-check', 'Check policy compliance', 'shell', '{"script": "./scripts/policy-check.sh"}'),
  ('continue-pr-create', 'Create PR from spec changes', 'agent', '{"command": "/ship"}')
on conflict (name) do nothing;

-- =============================================================================
-- GRANTS
-- =============================================================================

grant usage on schema control_room to anon, authenticated, service_role;
grant all on all tables in schema control_room to service_role;
grant select on all tables in schema control_room to authenticated;
grant select on all tables in schema control_room to anon;
grant usage, select on all sequences in schema control_room to service_role, authenticated;
