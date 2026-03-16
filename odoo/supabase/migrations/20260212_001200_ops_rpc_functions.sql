-- ============================================================================
-- ops.* RPC Functions
-- ============================================================================
-- Purpose: Data access functions for odooops-console
-- Spec: /spec/odooops-platform/odooops-console-PRD.md
-- Created: 2026-02-12
-- ============================================================================

-- ============================================================================
-- Helper: Get user's org IDs
-- ============================================================================
create or replace function ops.my_org_ids()
returns setof uuid
language sql security definer
set search_path = registry, public
stable
as $$
  select org_id
  from registry.org_members
  where user_id = auth.uid()
    and status = 'active';
$$;

comment on function ops.my_org_ids is 'Returns org IDs for current user';

-- ============================================================================
-- ops.list_projects() - Get all projects for user's orgs
-- ============================================================================
create or replace function ops.list_projects()
returns table (
  id uuid,
  org_id uuid,
  name text,
  slug text,
  repo_url text,
  default_branch text,
  runtime_version text,
  status text,
  created_at timestamptz,
  updated_at timestamptz,
  branch_count bigint,
  last_build_status text,
  last_build_at timestamptz
)
language sql security definer
set search_path = ops, registry, public
stable
as $$
  select
    p.id,
    p.org_id,
    p.name,
    p.slug,
    p.repo_url,
    p.default_branch,
    p.runtime_version,
    p.status,
    p.created_at,
    p.updated_at,
    count(distinct b.id) as branch_count,
    (select bu.status from ops.builds bu where bu.project_id = p.id order by bu.created_at desc limit 1) as last_build_status,
    (select bu.created_at from ops.builds bu where bu.project_id = p.id order by bu.created_at desc limit 1) as last_build_at
  from ops.projects p
  left join ops.branches b on b.project_id = p.id
  where p.org_id in (select ops.my_org_ids())
  group by p.id
  order by p.created_at desc;
$$;

grant execute on function ops.list_projects to authenticated;
comment on function ops.list_projects is 'List all projects with stats';

-- ============================================================================
-- ops.project_branches(project_id) - Get branches for project
-- ============================================================================
create or replace function ops.project_branches(p_project_id uuid)
returns table (
  id uuid,
  project_id uuid,
  name text,
  stage text,
  is_production boolean,
  last_build_id uuid,
  git_ref text,
  status text,
  created_at timestamptz,
  updated_at timestamptz,
  build_count bigint,
  last_build_status text,
  last_build_at timestamptz
)
language sql security definer
set search_path = ops, registry, public
stable
as $$
  select
    br.id,
    br.project_id,
    br.name,
    br.stage,
    br.is_production,
    br.last_build_id,
    br.git_ref,
    br.status,
    br.created_at,
    br.updated_at,
    count(bu.id) as build_count,
    (select bu2.status from ops.builds bu2 where bu2.branch_id = br.id order by bu2.created_at desc limit 1) as last_build_status,
    (select bu2.created_at from ops.builds bu2 where bu2.branch_id = br.id order by bu2.created_at desc limit 1) as last_build_at
  from ops.branches br
  join ops.projects p on br.project_id = p.id
  left join ops.builds bu on bu.branch_id = br.id
  where br.project_id = p_project_id
    and p.org_id in (select ops.my_org_ids())
  group by br.id
  order by br.stage desc, br.name;
$$;

grant execute on function ops.project_branches to authenticated;
comment on function ops.project_branches is 'Get branches for project with stats';

-- ============================================================================
-- ops.branch_builds(branch_id) - Get builds for branch
-- ============================================================================
create or replace function ops.branch_builds(p_branch_id uuid)
returns table (
  id uuid,
  project_id uuid,
  branch_id uuid,
  build_number int,
  status text,
  trigger text,
  commit_sha text,
  commit_message text,
  started_at timestamptz,
  finished_at timestamptz,
  duration_seconds int,
  error_message text,
  created_by uuid,
  created_at timestamptz
)
language sql security definer
set search_path = ops, registry, public
stable
as $$
  select
    bu.id,
    bu.project_id,
    bu.branch_id,
    bu.build_number,
    bu.status,
    bu.trigger,
    bu.commit_sha,
    bu.commit_message,
    bu.started_at,
    bu.finished_at,
    bu.duration_seconds,
    bu.error_message,
    bu.created_by,
    bu.created_at
  from ops.builds bu
  join ops.branches br on bu.branch_id = br.id
  join ops.projects p on br.project_id = p.id
  where bu.branch_id = p_branch_id
    and p.org_id in (select ops.my_org_ids())
  order by bu.created_at desc;
$$;

grant execute on function ops.branch_builds to authenticated;
comment on function ops.branch_builds is 'Get builds for branch';

-- ============================================================================
-- ops.build_logs(build_id) - Get build event log
-- ============================================================================
create or replace function ops.build_logs(
  p_build_id uuid,
  p_limit int default 1000,
  p_offset int default 0
)
returns table (
  id bigint,
  build_id uuid,
  ts timestamptz,
  phase text,
  level text,
  message text,
  meta jsonb
)
language sql security definer
set search_path = ops, registry, public
stable
as $$
  select
    e.id,
    e.build_id,
    e.ts,
    e.phase,
    e.level,
    e.message,
    e.meta
  from ops.build_events e
  join ops.builds bu on e.build_id = bu.id
  join ops.projects p on bu.project_id = p.id
  where e.build_id = p_build_id
    and p.org_id in (select ops.my_org_ids())
  order by e.ts desc
  limit p_limit
  offset p_offset;
$$;

grant execute on function ops.build_logs to authenticated;
comment on function ops.build_logs is 'Get build event log with pagination';

-- ============================================================================
-- ops.project_metrics(project_id, metric, hours) - Get recent metrics
-- ============================================================================
create or replace function ops.project_metrics(
  p_project_id uuid,
  p_metric text,
  p_hours int default 24
)
returns table (
  ts timestamptz,
  value numeric,
  dims jsonb
)
language sql security definer
set search_path = ops, registry, public
stable
as $$
  select
    m.ts,
    m.value,
    m.dims
  from ops.metrics m
  join ops.projects p on m.project_id = p.id
  where m.project_id = p_project_id
    and m.metric = p_metric
    and m.ts >= now() - (p_hours || ' hours')::interval
    and p.org_id in (select ops.my_org_ids())
  order by m.ts desc;
$$;

grant execute on function ops.project_metrics to authenticated;
comment on function ops.project_metrics is 'Get recent metrics for project';

-- ============================================================================
-- ops.list_advisories(project_id) - Get advisories
-- ============================================================================
create or replace function ops.list_advisories(p_project_id uuid)
returns table (
  id uuid,
  project_id uuid,
  severity text,
  category text,
  title text,
  recommendation text,
  evidence jsonb,
  status text,
  created_at timestamptz,
  updated_at timestamptz,
  resolved_at timestamptz,
  snoozed_until timestamptz
)
language sql security definer
set search_path = ops, registry, public
stable
as $$
  select
    a.id,
    a.project_id,
    a.severity,
    a.category,
    a.title,
    a.recommendation,
    a.evidence,
    a.status,
    a.created_at,
    a.updated_at,
    a.resolved_at,
    a.snoozed_until
  from ops.advisories a
  join ops.projects p on a.project_id = p.id
  where a.project_id = p_project_id
    and p.org_id in (select ops.my_org_ids())
  order by
    case a.severity
      when 'critical' then 1
      when 'warning' then 2
      when 'info' then 3
    end,
    a.created_at desc;
$$;

grant execute on function ops.list_advisories to authenticated;
comment on function ops.list_advisories is 'Get advisories for project';

-- ============================================================================
-- ops.enqueue_build(build_id, priority) - Add build to queue
-- ============================================================================
create or replace function ops.enqueue_build(
  p_build_id uuid,
  p_priority int default 5
)
returns uuid
language plpgsql security definer
set search_path = ops, registry, public
as $$
declare
  v_queue_id uuid;
  v_org_id uuid;
begin
  -- Verify user has access to this build's project
  select p.org_id into v_org_id
  from ops.builds bu
  join ops.projects p on bu.project_id = p.id
  where bu.id = p_build_id;

  if v_org_id not in (select ops.my_org_ids()) then
    raise exception 'Access denied';
  end if;

  -- Insert into queue
  insert into ops.run_queue (build_id, priority, status)
  values (p_build_id, p_priority, 'queued')
  returning id into v_queue_id;

  return v_queue_id;
end;
$$;

grant execute on function ops.enqueue_build to authenticated;
comment on function ops.enqueue_build is 'Enqueue build for execution';

-- ============================================================================
-- ops.claim_next_run(runner_id) - Claim next queued build
-- ============================================================================
create or replace function ops.claim_next_run(p_runner_id text)
returns table (
  queue_id uuid,
  build_id uuid,
  project_id uuid,
  branch_id uuid
)
language plpgsql security definer
set search_path = ops, public
as $$
declare
  v_queue_record record;
begin
  -- Find next available build
  select q.id, q.build_id
  into v_queue_record
  from ops.run_queue q
  where q.status = 'queued'
    and (q.next_attempt_at is null or q.next_attempt_at <= now())
  order by q.priority, q.created_at
  limit 1
  for update skip locked;

  if not found then
    return;
  end if;

  -- Claim it
  update ops.run_queue
  set status = 'claimed',
      claimed_by = p_runner_id,
      claimed_at = now(),
      attempts = attempts + 1
  where id = v_queue_record.id;

  -- Update build status
  update ops.builds
  set status = 'running',
      started_at = now()
  where id = v_queue_record.build_id;

  -- Return details
  return query
  select
    v_queue_record.id,
    bu.id,
    bu.project_id,
    bu.branch_id
  from ops.builds bu
  where bu.id = v_queue_record.build_id;
end;
$$;

grant execute on function ops.claim_next_run to service_role;
comment on function ops.claim_next_run is 'Claim next build in queue (service_role only)';

-- ============================================================================
-- ops.append_build_event(build_id, phase, level, message, meta) - Log event
-- ============================================================================
create or replace function ops.append_build_event(
  p_build_id uuid,
  p_phase text,
  p_level text,
  p_message text,
  p_meta jsonb default '{}'::jsonb
)
returns bigint
language plpgsql security definer
set search_path = ops, public
as $$
declare
  v_event_id bigint;
begin
  insert into ops.build_events (build_id, phase, level, message, meta)
  values (p_build_id, p_phase, p_level, p_message, p_meta)
  returning id into v_event_id;

  return v_event_id;
end;
$$;

grant execute on function ops.append_build_event to service_role;
comment on function ops.append_build_event is 'Append event to build log (service_role only)';

-- ============================================================================
-- ops.set_build_status(build_id, status, error_message) - Update build
-- ============================================================================
create or replace function ops.set_build_status(
  p_build_id uuid,
  p_status text,
  p_error_message text default null
)
returns void
language plpgsql security definer
set search_path = ops, public
as $$
begin
  update ops.builds
  set status = p_status,
      finished_at = case when p_status in ('success', 'failed', 'cancelled') then now() else finished_at end,
      error_message = p_error_message
  where id = p_build_id;

  -- Update queue
  update ops.run_queue
  set status = case
    when p_status = 'success' then 'done'
    when p_status = 'failed' then 'failed'
    when p_status = 'cancelled' then 'done'
    else status
  end
  where build_id = p_build_id;
end;
$$;

grant execute on function ops.set_build_status to service_role;
comment on function ops.set_build_status is 'Update build status (service_role only)';

-- ============================================================================
-- ops.resolve_advisory(advisory_id) - Mark advisory as resolved
-- ============================================================================
create or replace function ops.resolve_advisory(p_advisory_id uuid)
returns void
language plpgsql security definer
set search_path = ops, registry, public
as $$
declare
  v_org_id uuid;
begin
  -- Verify access
  select p.org_id into v_org_id
  from ops.advisories a
  join ops.projects p on a.project_id = p.id
  where a.id = p_advisory_id;

  if v_org_id not in (select ops.my_org_ids()) then
    raise exception 'Access denied';
  end if;

  update ops.advisories
  set status = 'resolved',
      resolved_at = now(),
      resolved_by = auth.uid()
  where id = p_advisory_id;
end;
$$;

grant execute on function ops.resolve_advisory to authenticated;
comment on function ops.resolve_advisory is 'Mark advisory as resolved';

-- ============================================================================
-- ops.snooze_advisory(advisory_id, until) - Snooze advisory
-- ============================================================================
create or replace function ops.snooze_advisory(
  p_advisory_id uuid,
  p_until timestamptz
)
returns void
language plpgsql security definer
set search_path = ops, registry, public
as $$
declare
  v_org_id uuid;
begin
  -- Verify access
  select p.org_id into v_org_id
  from ops.advisories a
  join ops.projects p on a.project_id = p.id
  where a.id = p_advisory_id;

  if v_org_id not in (select ops.my_org_ids()) then
    raise exception 'Access denied';
  end if;

  update ops.advisories
  set status = 'snoozed',
      snoozed_until = p_until
  where id = p_advisory_id;
end;
$$;

grant execute on function ops.snooze_advisory to authenticated;
comment on function ops.snooze_advisory is 'Snooze advisory until timestamp';
