-- ===========================================================================
-- OPS CONFIG REGISTRY SCHEMA
-- Git is SSOT; Supabase stores versioned copies + rollout + status
-- Supports: design_tokens, workflow configs, seed bundles
-- ===========================================================================

-- ---------------------------------------------------------------------------
-- 1) Config Artifacts (top-level registry)
-- ---------------------------------------------------------------------------
create table if not exists ops.config_artifacts (
  id uuid primary key default gen_random_uuid(),
  kind text not null check (kind in ('design_tokens', 'workflow', 'seed_bundle', 'odoo_config', 'feature_flag')),
  slug text not null unique,
  name text not null,
  description text,
  current_version_id uuid,                -- points to active version
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_config_artifacts_kind
  on ops.config_artifacts(kind);

comment on table ops.config_artifacts is 'Registry of configuration artifacts (design tokens, workflows, seeds)';

-- ---------------------------------------------------------------------------
-- 2) Config Versions (immutable snapshots)
-- ---------------------------------------------------------------------------
create table if not exists ops.config_versions (
  id uuid primary key default gen_random_uuid(),
  artifact_id uuid not null references ops.config_artifacts(id) on delete cascade,
  version text not null,                  -- semantic version or git tag
  git_sha text not null,                  -- commit SHA for traceability
  content_hash text not null,             -- SHA256 of canonical content
  content_json jsonb,                     -- structured content (tokens, etc.)
  content_text text,                      -- text content (YAML workflows, etc.)
  created_at timestamptz not null default now(),
  created_by uuid references auth.users(id)
);

create index if not exists idx_config_versions_artifact
  on ops.config_versions(artifact_id, created_at desc);

-- Deduplication: same content = same version (idempotent publishes)
create unique index if not exists uq_config_versions_dedupe
  on ops.config_versions(artifact_id, content_hash);

comment on table ops.config_versions is 'Immutable version snapshots of configuration artifacts';

-- Add FK for current_version_id after config_versions exists
alter table ops.config_artifacts
  drop constraint if exists fk_config_artifacts_current_version;
alter table ops.config_artifacts
  add constraint fk_config_artifacts_current_version
  foreign key (current_version_id) references ops.config_versions(id) on delete set null;

-- ---------------------------------------------------------------------------
-- 3) Config Consumers (who is using config)
-- ---------------------------------------------------------------------------
create table if not exists ops.config_consumers (
  id uuid primary key default gen_random_uuid(),
  consumer_type text not null check (consumer_type in ('odoo', 'edge_fn', 'web_app', 'n8n', 'mcp_server', 'docker')),
  consumer_key text not null,             -- e.g., "odoo-core", "control-room", "pulser-runner"
  environment text not null default 'prod',
  last_seen_at timestamptz,               -- heartbeat timestamp
  last_applied_version_id uuid references ops.config_versions(id),
  status text not null default 'unknown' check (status in ('ok', 'degraded', 'failed', 'unknown', 'stale')),
  metadata jsonb not null default '{}'::jsonb,
  unique (consumer_type, consumer_key, environment)
);

create index if not exists idx_config_consumers_status
  on ops.config_consumers(status) where status != 'ok';

comment on table ops.config_consumers is 'Systems consuming configuration artifacts with health status';

-- ---------------------------------------------------------------------------
-- 4) Config Checks (detailed health probes)
-- ---------------------------------------------------------------------------
create table if not exists ops.config_checks (
  id uuid primary key default gen_random_uuid(),
  consumer_id uuid not null references ops.config_consumers(id) on delete cascade,
  check_type text not null,               -- e.g., "theme_applied", "sync_lag", "seed_integrity", "token_match"
  status text not null check (status in ('ok', 'warn', 'fail')),
  detail jsonb not null default '{}'::jsonb,
  measured_at timestamptz not null default now()
);

create index if not exists idx_config_checks_consumer_time
  on ops.config_checks(consumer_id, measured_at desc);

comment on table ops.config_checks is 'Detailed health check results for config consumers';

-- ---------------------------------------------------------------------------
-- 5) Config Rollouts (deployment tracking)
-- ---------------------------------------------------------------------------
create table if not exists ops.config_rollouts (
  id uuid primary key default gen_random_uuid(),
  artifact_id uuid not null references ops.config_artifacts(id) on delete cascade,
  from_version_id uuid references ops.config_versions(id),
  to_version_id uuid not null references ops.config_versions(id),
  strategy text not null default 'all' check (strategy in ('all', 'canary', 'phased', 'manual')),
  status text not null default 'running' check (status in ('pending', 'running', 'completed', 'aborted', 'failed')),
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  progress_pct int not null default 0 check (progress_pct >= 0 and progress_pct <= 100),
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists idx_config_rollouts_artifact_status
  on ops.config_rollouts(artifact_id, status, started_at desc);

comment on table ops.config_rollouts is 'Config deployment rollouts with progress tracking';

-- ---------------------------------------------------------------------------
-- 6) Config Drift Events (Git vs applied state)
-- ---------------------------------------------------------------------------
create table if not exists ops.config_drift_events (
  id uuid primary key default gen_random_uuid(),
  artifact_id uuid not null references ops.config_artifacts(id) on delete cascade,
  consumer_id uuid references ops.config_consumers(id) on delete set null,
  drift_type text not null check (drift_type in ('version_mismatch', 'content_mismatch', 'missing', 'stale')),
  expected_version_id uuid references ops.config_versions(id),
  actual_version_id uuid references ops.config_versions(id),
  detail jsonb not null default '{}'::jsonb,
  detected_at timestamptz not null default now(),
  resolved_at timestamptz
);

create index if not exists idx_config_drift_unresolved
  on ops.config_drift_events(artifact_id, detected_at desc) where resolved_at is null;

comment on table ops.config_drift_events is 'Configuration drift detection and resolution tracking';

-- ---------------------------------------------------------------------------
-- 7) RLS Policies
-- ---------------------------------------------------------------------------
alter table ops.config_artifacts enable row level security;
alter table ops.config_versions enable row level security;
alter table ops.config_consumers enable row level security;
alter table ops.config_checks enable row level security;
alter table ops.config_rollouts enable row level security;
alter table ops.config_drift_events enable row level security;

-- Baseline: no public access
revoke all on schema ops from public;
revoke all on all tables in schema ops from public;
revoke all on ops.config_artifacts from public;
revoke all on ops.config_versions from public;
revoke all on ops.config_consumers from public;
revoke all on ops.config_checks from public;
revoke all on ops.config_rollouts from public;
revoke all on ops.config_drift_events from public;

-- Create ops_admin role if not exists (idempotent)
do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'ops_admin') then
    create role ops_admin nologin;
  end if;
end
$$;

-- Read policies for authenticated users with ops_admin role
create policy "ops_admin_read_config_artifacts"
on ops.config_artifacts for select
to authenticated
using ((auth.jwt() ->> 'role') = 'ops_admin' or (auth.jwt() -> 'app_metadata' ->> 'role') = 'ops_admin');

create policy "ops_admin_read_config_versions"
on ops.config_versions for select
to authenticated
using ((auth.jwt() ->> 'role') = 'ops_admin' or (auth.jwt() -> 'app_metadata' ->> 'role') = 'ops_admin');

create policy "ops_admin_read_config_consumers"
on ops.config_consumers for select
to authenticated
using ((auth.jwt() ->> 'role') = 'ops_admin' or (auth.jwt() -> 'app_metadata' ->> 'role') = 'ops_admin');

create policy "ops_admin_read_config_checks"
on ops.config_checks for select
to authenticated
using ((auth.jwt() ->> 'role') = 'ops_admin' or (auth.jwt() -> 'app_metadata' ->> 'role') = 'ops_admin');

create policy "ops_admin_read_config_rollouts"
on ops.config_rollouts for select
to authenticated
using ((auth.jwt() ->> 'role') = 'ops_admin' or (auth.jwt() -> 'app_metadata' ->> 'role') = 'ops_admin');

create policy "ops_admin_read_config_drift"
on ops.config_drift_events for select
to authenticated
using ((auth.jwt() ->> 'role') = 'ops_admin' or (auth.jwt() -> 'app_metadata' ->> 'role') = 'ops_admin');

-- Service role bypass for server-side writes
create policy "service_role_config_artifacts"
on ops.config_artifacts for all
to service_role
using (true)
with check (true);

create policy "service_role_config_versions"
on ops.config_versions for all
to service_role
using (true)
with check (true);

create policy "service_role_config_consumers"
on ops.config_consumers for all
to service_role
using (true)
with check (true);

create policy "service_role_config_checks"
on ops.config_checks for all
to service_role
using (true)
with check (true);

create policy "service_role_config_rollouts"
on ops.config_rollouts for all
to service_role
using (true)
with check (true);

create policy "service_role_config_drift"
on ops.config_drift_events for all
to service_role
using (true)
with check (true);

-- ---------------------------------------------------------------------------
-- 8) RPCs for Config Operations
-- ---------------------------------------------------------------------------

-- Enqueue/publish a new config version
create or replace function ops.publish_config_version(
  p_kind text,
  p_slug text,
  p_name text,
  p_description text,
  p_version text,
  p_git_sha text,
  p_content_json jsonb default null,
  p_content_text text default null,
  p_auto_promote boolean default true
)
returns jsonb
language plpgsql
security definer
as $$
declare
  v_artifact_id uuid;
  v_version_id uuid;
  v_content_hash text;
  v_canonical text;
  v_existing_version_id uuid;
begin
  -- Compute content hash for deduplication
  v_canonical := coalesce(p_content_json::text, p_content_text, '');
  v_content_hash := encode(digest(p_kind || ':' || p_slug || ':' || v_canonical, 'sha256'), 'hex');

  -- Upsert artifact
  insert into ops.config_artifacts (kind, slug, name, description)
  values (p_kind, p_slug, p_name, coalesce(p_description, ''))
  on conflict (slug) do update set
    name = excluded.name,
    description = coalesce(excluded.description, ops.config_artifacts.description),
    updated_at = now()
  returning id into v_artifact_id;

  -- Check for existing version with same content hash
  select id into v_existing_version_id
  from ops.config_versions
  where artifact_id = v_artifact_id and content_hash = v_content_hash;

  if v_existing_version_id is not null then
    return jsonb_build_object(
      'ok', true,
      'artifact_id', v_artifact_id,
      'version_id', v_existing_version_id,
      'deduped', true,
      'message', 'Version already exists with identical content'
    );
  end if;

  -- Insert new version
  insert into ops.config_versions (artifact_id, version, git_sha, content_hash, content_json, content_text)
  values (v_artifact_id, p_version, p_git_sha, v_content_hash, p_content_json, p_content_text)
  returning id into v_version_id;

  -- Auto-promote if requested
  if p_auto_promote then
    update ops.config_artifacts
    set current_version_id = v_version_id, updated_at = now()
    where id = v_artifact_id;
  end if;

  -- Log audit event
  insert into audit.events (topic, action, actor, payload)
  values (
    'config',
    'publish',
    'system',
    jsonb_build_object(
      'artifact_id', v_artifact_id,
      'version_id', v_version_id,
      'kind', p_kind,
      'slug', p_slug,
      'version', p_version,
      'git_sha', p_git_sha,
      'auto_promoted', p_auto_promote
    )
  );

  return jsonb_build_object(
    'ok', true,
    'artifact_id', v_artifact_id,
    'version_id', v_version_id,
    'deduped', false,
    'promoted', p_auto_promote
  );
end;
$$;

-- Get current config for a consumer
create or replace function ops.get_current_config(p_slug text)
returns jsonb
language sql
stable
as $$
  select jsonb_build_object(
    'artifact_id', a.id,
    'kind', a.kind,
    'slug', a.slug,
    'name', a.name,
    'version_id', v.id,
    'version', v.version,
    'git_sha', v.git_sha,
    'content_json', v.content_json,
    'content_text', v.content_text,
    'updated_at', a.updated_at
  )
  from ops.config_artifacts a
  left join ops.config_versions v on v.id = a.current_version_id
  where a.slug = p_slug;
$$;

-- Consumer heartbeat with version check
create or replace function ops.consumer_heartbeat(
  p_consumer_type text,
  p_consumer_key text,
  p_environment text,
  p_applied_version_id uuid default null,
  p_status text default 'ok',
  p_metadata jsonb default '{}'::jsonb
)
returns jsonb
language plpgsql
security definer
as $$
declare
  v_consumer_id uuid;
begin
  insert into ops.config_consumers (consumer_type, consumer_key, environment, last_seen_at, last_applied_version_id, status, metadata)
  values (p_consumer_type, p_consumer_key, p_environment, now(), p_applied_version_id, p_status, p_metadata)
  on conflict (consumer_type, consumer_key, environment) do update set
    last_seen_at = now(),
    last_applied_version_id = coalesce(excluded.last_applied_version_id, ops.config_consumers.last_applied_version_id),
    status = excluded.status,
    metadata = ops.config_consumers.metadata || excluded.metadata
  returning id into v_consumer_id;

  return jsonb_build_object(
    'ok', true,
    'consumer_id', v_consumer_id,
    'timestamp', now()
  );
end;
$$;

-- Record a config check result
create or replace function ops.record_config_check(
  p_consumer_type text,
  p_consumer_key text,
  p_environment text,
  p_check_type text,
  p_status text,
  p_detail jsonb default '{}'::jsonb
)
returns jsonb
language plpgsql
security definer
as $$
declare
  v_consumer_id uuid;
  v_check_id uuid;
begin
  -- Find or create consumer
  select id into v_consumer_id
  from ops.config_consumers
  where consumer_type = p_consumer_type
    and consumer_key = p_consumer_key
    and environment = p_environment;

  if v_consumer_id is null then
    insert into ops.config_consumers (consumer_type, consumer_key, environment, status)
    values (p_consumer_type, p_consumer_key, p_environment, 'unknown')
    returning id into v_consumer_id;
  end if;

  -- Insert check result
  insert into ops.config_checks (consumer_id, check_type, status, detail)
  values (v_consumer_id, p_check_type, p_status, p_detail)
  returning id into v_check_id;

  -- Update consumer status based on check
  if p_status = 'fail' then
    update ops.config_consumers set status = 'degraded' where id = v_consumer_id;
  end if;

  return jsonb_build_object(
    'ok', true,
    'consumer_id', v_consumer_id,
    'check_id', v_check_id
  );
end;
$$;

-- Detect config drift
create or replace function ops.detect_config_drift()
returns table (
  artifact_id uuid,
  artifact_slug text,
  consumer_id uuid,
  consumer_key text,
  drift_type text,
  expected_version text,
  actual_version text
)
language sql
stable
as $$
  select
    a.id as artifact_id,
    a.slug as artifact_slug,
    c.id as consumer_id,
    c.consumer_key,
    case
      when c.last_applied_version_id is null then 'missing'
      when c.last_applied_version_id != a.current_version_id then 'version_mismatch'
      when c.last_seen_at < now() - interval '1 hour' then 'stale'
      else 'ok'
    end as drift_type,
    ev.version as expected_version,
    av.version as actual_version
  from ops.config_consumers c
  cross join ops.config_artifacts a
  left join ops.config_versions ev on ev.id = a.current_version_id
  left join ops.config_versions av on av.id = c.last_applied_version_id
  where c.last_applied_version_id is distinct from a.current_version_id
     or c.last_seen_at < now() - interval '1 hour';
$$;

-- Rollback to previous version
create or replace function ops.rollback_config(p_slug text, p_offset int default 1)
returns jsonb
language plpgsql
security definer
as $$
declare
  v_artifact_id uuid;
  v_current_version_id uuid;
  v_target_version_id uuid;
  v_target_version text;
begin
  -- Get artifact
  select id, current_version_id into v_artifact_id, v_current_version_id
  from ops.config_artifacts
  where slug = p_slug;

  if v_artifact_id is null then
    return jsonb_build_object('ok', false, 'error', 'Artifact not found');
  end if;

  -- Find target version (offset back from current)
  select id, version into v_target_version_id, v_target_version
  from ops.config_versions
  where artifact_id = v_artifact_id
  order by created_at desc
  offset p_offset
  limit 1;

  if v_target_version_id is null then
    return jsonb_build_object('ok', false, 'error', 'No previous version available');
  end if;

  -- Update current pointer
  update ops.config_artifacts
  set current_version_id = v_target_version_id, updated_at = now()
  where id = v_artifact_id;

  -- Create rollout record
  insert into ops.config_rollouts (artifact_id, from_version_id, to_version_id, strategy, status, progress_pct, completed_at)
  values (v_artifact_id, v_current_version_id, v_target_version_id, 'manual', 'completed', 100, now());

  -- Audit
  insert into audit.events (topic, action, actor, payload)
  values (
    'config',
    'rollback',
    'system',
    jsonb_build_object(
      'artifact_id', v_artifact_id,
      'slug', p_slug,
      'from_version_id', v_current_version_id,
      'to_version_id', v_target_version_id,
      'to_version', v_target_version
    )
  );

  return jsonb_build_object(
    'ok', true,
    'artifact_id', v_artifact_id,
    'from_version_id', v_current_version_id,
    'to_version_id', v_target_version_id,
    'to_version', v_target_version
  );
end;
$$;

-- ---------------------------------------------------------------------------
-- 9) Summary Views
-- ---------------------------------------------------------------------------
create or replace view ops.config_registry_summary_v as
select
  a.id as artifact_id,
  a.kind,
  a.slug,
  a.name,
  a.updated_at,
  v.version as current_version,
  v.git_sha as current_git_sha,
  v.created_at as version_created_at,
  (select count(*) from ops.config_versions where artifact_id = a.id) as total_versions,
  (select count(*) from ops.config_consumers where last_applied_version_id = v.id) as consumers_at_current,
  (select count(*) from ops.config_consumers where last_applied_version_id != v.id or last_applied_version_id is null) as consumers_drifted
from ops.config_artifacts a
left join ops.config_versions v on v.id = a.current_version_id
order by a.updated_at desc;

create or replace view ops.config_consumers_health_v as
select
  c.id as consumer_id,
  c.consumer_type,
  c.consumer_key,
  c.environment,
  c.status,
  c.last_seen_at,
  a.slug as artifact_slug,
  v.version as applied_version,
  cv.version as current_version,
  case
    when c.last_applied_version_id = a.current_version_id then 'in_sync'
    else 'drifted'
  end as sync_status,
  extract(epoch from (now() - c.last_seen_at)) as seconds_since_seen
from ops.config_consumers c
left join ops.config_versions v on v.id = c.last_applied_version_id
left join ops.config_artifacts a on a.id = v.artifact_id
left join ops.config_versions cv on cv.id = a.current_version_id
order by c.last_seen_at desc nulls last;

comment on view ops.config_registry_summary_v is 'Summary of all config artifacts with version and consumer stats';
comment on view ops.config_consumers_health_v is 'Consumer health with drift detection';
