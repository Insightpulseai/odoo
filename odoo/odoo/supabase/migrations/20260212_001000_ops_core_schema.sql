-- ============================================================================
-- ops.* Core Schema - Odoo.sh Operational Parity
-- ============================================================================
-- Purpose: Projects, branches, builds, artifacts for odooops-console
-- Spec: /spec/odooops-platform/odooops-console-PRD.md
-- Created: 2026-02-12
-- ============================================================================

-- Create ops schema
create schema if not exists ops;

-- ============================================================================
-- ops.projects - Odoo.sh projects
-- ============================================================================
create table ops.projects (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references registry.orgs(id) on delete cascade,
  name text not null,
  slug text not null,
  repo_url text not null,
  default_branch text not null default 'main',
  runtime_version text not null default '19.0',
  status text not null default 'active' check (status in ('active', 'archived', 'suspended')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint unique_org_project_slug unique(org_id, slug)
);

create index ops_projects_org_id_idx on ops.projects(org_id);
create index ops_projects_status_idx on ops.projects(status);

comment on table ops.projects is 'Odoo.sh-style projects (deployments)';
comment on column ops.projects.slug is 'URL-safe project identifier';
comment on column ops.projects.runtime_version is 'Odoo version (e.g., 19.0, 18.0)';

-- ============================================================================
-- ops.branches - Project branches (production, staging, development)
-- ============================================================================
create table ops.branches (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references ops.projects(id) on delete cascade,
  name text not null,
  stage text not null check (stage in ('production', 'staging', 'development')),
  is_production boolean not null default false,
  last_build_id uuid,
  git_ref text,
  status text not null default 'ready' check (status in ('ready', 'building', 'error', 'archived')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint unique_project_branch_name unique(project_id, name),
  constraint unique_prod_branch unique(project_id, is_production) where is_production = true
);

create index ops_branches_project_id_idx on ops.branches(project_id);
create index ops_branches_stage_idx on ops.branches(stage);
create index ops_branches_status_idx on ops.branches(status);

comment on table ops.branches is 'Git branches with deployment stages';
comment on constraint unique_prod_branch on ops.branches is 'Only one production branch per project';

-- ============================================================================
-- ops.builds - CI/CD build runs
-- ============================================================================
create table ops.builds (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references ops.projects(id) on delete cascade,
  branch_id uuid not null references ops.branches(id) on delete cascade,
  build_number serial,
  status text not null default 'queued' check (status in ('queued', 'running', 'success', 'failed', 'cancelled')),
  trigger text not null check (trigger in ('manual', 'commit', 'schedule', 'api')),
  commit_sha text,
  commit_message text,
  started_at timestamptz,
  finished_at timestamptz,
  duration_seconds int,
  error_message text,
  created_by uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default now(),

  constraint valid_duration check (duration_seconds is null or duration_seconds >= 0)
);

create index ops_builds_project_id_idx on ops.builds(project_id);
create index ops_builds_branch_id_idx on ops.builds(branch_id);
create index ops_builds_status_idx on ops.builds(status);
create index ops_builds_created_at_idx on ops.builds(created_at desc);

comment on table ops.builds is 'CI/CD build execution records';
comment on column ops.builds.build_number is 'Auto-incrementing build number';

-- ============================================================================
-- ops.build_events - Append-only event log
-- ============================================================================
create table ops.build_events (
  id bigserial primary key,
  build_id uuid not null references ops.builds(id) on delete cascade,
  ts timestamptz not null default now(),
  phase text not null check (phase in ('checkout', 'build', 'test', 'package', 'deploy', 'promote', 'system')),
  level text not null check (level in ('debug', 'info', 'warn', 'error')),
  message text not null,
  meta jsonb not null default '{}'::jsonb
);

create index ops_build_events_build_id_ts_idx on ops.build_events(build_id, ts desc);
create index ops_build_events_level_idx on ops.build_events(level) where level in ('warn', 'error');

comment on table ops.build_events is 'Append-only log stream for builds';
comment on column ops.build_events.phase is 'Build pipeline phase';

-- ============================================================================
-- ops.artifacts - Build artifacts (logs, images, dumps)
-- ============================================================================
create table ops.artifacts (
  id uuid primary key default gen_random_uuid(),
  build_id uuid not null references ops.builds(id) on delete cascade,
  type text not null check (type in ('log', 'image', 'dump', 'report')),
  name text not null,
  storage_path text not null,
  size_bytes bigint,
  mime_type text,
  created_at timestamptz not null default now(),
  expires_at timestamptz
);

create index ops_artifacts_build_id_idx on ops.artifacts(build_id);
create index ops_artifacts_type_idx on ops.artifacts(type);

comment on table ops.artifacts is 'Build output artifacts';
comment on column ops.artifacts.storage_path is 'Supabase Storage path';

-- ============================================================================
-- Triggers for updated_at
-- ============================================================================
create or replace function ops.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger ops_projects_updated_at
  before update on ops.projects
  for each row
  execute function ops.set_updated_at();

create trigger ops_branches_updated_at
  before update on ops.branches
  for each row
  execute function ops.set_updated_at();

-- ============================================================================
-- Update build duration on finish
-- ============================================================================
create or replace function ops.update_build_duration()
returns trigger
language plpgsql
as $$
begin
  if new.finished_at is not null and old.finished_at is null then
    new.duration_seconds := extract(epoch from (new.finished_at - new.started_at))::int;
  end if;
  return new;
end;
$$;

create trigger ops_builds_duration
  before update on ops.builds
  for each row
  when (new.finished_at is not null)
  execute function ops.update_build_duration();

-- ============================================================================
-- Update branch.last_build_id on successful build
-- ============================================================================
create or replace function ops.update_branch_last_build()
returns trigger
language plpgsql
as $$
begin
  if new.status = 'success' then
    update ops.branches
    set last_build_id = new.id
    where id = new.branch_id;
  end if;
  return new;
end;
$$;

create trigger ops_builds_update_branch
  after update on ops.builds
  for each row
  when (new.status = 'success')
  execute function ops.update_branch_last_build();

-- ============================================================================
-- Grants (RLS policies in next migration)
-- ============================================================================
grant usage on schema ops to authenticated;
grant all on all tables in schema ops to authenticated;
grant all on all sequences in schema ops to authenticated;
