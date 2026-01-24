-- ============================================================================
-- Lakehouse Control Room - Ops Control Plane Schema
-- Migration: 20260124_1000_ops_lakehouse_control_plane.sql
-- Description: Core control plane tables for lakehouse executor orchestration
-- ============================================================================

create schema if not exists ops;

-- ============================================================================
-- CORE TYPES
-- ============================================================================

do $$
begin
  if not exists (select 1 from pg_type where typname = 'run_status' and typnamespace = (select oid from pg_namespace where nspname = 'ops')) then
    create type ops.run_status as enum ('queued', 'claimed', 'running', 'succeeded', 'failed', 'canceled');
  end if;
end $$;

-- ============================================================================
-- EXECUTORS REGISTRY
-- ============================================================================

create table if not exists ops.executors (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  capabilities jsonb not null default '[]'::jsonb,
  max_concurrent_runs int not null default 5,
  last_seen_at timestamptz,
  is_active boolean not null default true,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

comment on table ops.executors is 'Registered lakehouse executors (Spark, Trino, dbt, etc.)';

-- ============================================================================
-- RUNS (core state machine)
-- ============================================================================

create table if not exists ops.runs (
  id uuid primary key default gen_random_uuid(),
  kind text not null,                              -- 'sql', 'spark', 'dbt', 'python', 'notebook', 'pipeline'
  spec jsonb not null,                             -- machine-readable run specification
  status ops.run_status not null default 'queued',
  phase text,                                       -- 'prepare', 'resolve', 'execute', 'validate', 'publish', 'finalize'
  priority int not null default 100,               -- lower = higher priority
  artifact_base_uri text not null,                 -- s3://... or https://...
  idempotency_key text,                            -- optional dedup key
  timeout_seconds int not null default 3600,
  retry_count int not null default 0,
  max_retries int not null default 3,
  claimed_by uuid references ops.executors(id) on delete set null,
  claimed_at timestamptz,
  heartbeat_at timestamptz,
  started_at timestamptz,
  finished_at timestamptz,
  error_code text,
  error_message text,
  error_data jsonb,
  tags jsonb not null default '{}'::jsonb,
  created_by uuid,                                 -- user/service that created the run
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

comment on table ops.runs is 'Lakehouse job runs with state machine lifecycle';

create index if not exists runs_status_priority_idx on ops.runs(status, priority, created_at)
  where status in ('queued', 'claimed', 'running');
create index if not exists runs_claimed_by_idx on ops.runs(claimed_by) where claimed_by is not null;
create index if not exists runs_idempotency_key_idx on ops.runs(idempotency_key) where idempotency_key is not null;
create index if not exists runs_kind_status_idx on ops.runs(kind, status);

-- ============================================================================
-- RUN EVENTS (append-only log)
-- ============================================================================

create table if not exists ops.run_events (
  id bigserial primary key,
  run_id uuid not null references ops.runs(id) on delete cascade,
  ts timestamptz not null default now(),
  level text not null default 'info' check (level in ('debug', 'info', 'warn', 'error')),
  phase text,                                       -- current phase when event occurred
  message text not null,
  data jsonb not null default '{}'::jsonb
);

comment on table ops.run_events is 'Append-only event stream for run lifecycle';

create index if not exists run_events_run_id_ts_idx on ops.run_events(run_id, ts desc);
create index if not exists run_events_level_idx on ops.run_events(level) where level in ('warn', 'error');

-- ============================================================================
-- RUN ARTIFACTS
-- ============================================================================

create table if not exists ops.run_artifacts (
  id bigserial primary key,
  run_id uuid not null references ops.runs(id) on delete cascade,
  ts timestamptz not null default now(),
  kind text not null,                              -- 'log', 'dataset', 'report', 'manifest', 'checkpoint'
  uri text not null,                               -- full URI to artifact
  sha256 text,                                     -- checksum for integrity
  size_bytes bigint,
  meta jsonb not null default '{}'::jsonb
);

comment on table ops.run_artifacts is 'Output artifacts from runs (logs, datasets, reports)';

create index if not exists run_artifacts_run_id_ts_idx on ops.run_artifacts(run_id, ts desc);
create index if not exists run_artifacts_kind_idx on ops.run_artifacts(kind);

-- ============================================================================
-- CAPS (runtime limits)
-- ============================================================================

create table if not exists ops.caps (
  key text primary key,                            -- e.g. 'cpu_seconds_per_day', 'spark_minutes_per_day'
  limit_value numeric not null,
  window text not null default 'day' check (window in ('hour', 'day', 'week', 'month')),
  is_enabled boolean not null default true,
  description text,
  updated_at timestamptz not null default now()
);

comment on table ops.caps is 'Runtime caps/limits for cost control';

create table if not exists ops.cap_usage (
  id bigserial primary key,
  cap_key text not null references ops.caps(key) on delete cascade,
  ts timestamptz not null default now(),
  run_id uuid references ops.runs(id) on delete set null,
  amount numeric not null,
  meta jsonb not null default '{}'::jsonb
);

comment on table ops.cap_usage is 'Usage ledger for caps enforcement';

create index if not exists cap_usage_key_ts_idx on ops.cap_usage(cap_key, ts desc);
create index if not exists cap_usage_run_id_idx on ops.cap_usage(run_id) where run_id is not null;

-- ============================================================================
-- ROUTING MATRIX (escalation + alerting)
-- ============================================================================

create table if not exists ops.routing_matrix (
  id bigserial primary key,
  match jsonb not null,                            -- criteria: {"kind":"...", "phase":"...", "severity":"...", "tag":"..."}
  route jsonb not null,                            -- {"channels":[...], "owners":[...], "escalation":[...]}
  priority int not null default 100,               -- lower wins
  is_active boolean not null default true,
  description text,
  updated_at timestamptz not null default now()
);

comment on table ops.routing_matrix is 'Routing rules for alerts and escalation';

create index if not exists routing_matrix_active_priority_idx on ops.routing_matrix(priority) where is_active = true;

-- ============================================================================
-- ALERT RULES
-- ============================================================================

create table if not exists ops.alert_rules (
  id bigserial primary key,
  name text not null unique,
  rule jsonb not null,                             -- {"signal_type":"error_rate", "op":">", "value":0.05, "window_minutes":15}
  emit jsonb not null,                             -- {"severity":"high", "tag":"error_rate"}
  is_active boolean not null default true,
  description text,
  updated_at timestamptz not null default now()
);

comment on table ops.alert_rules is 'Threshold-based alert rule definitions';

-- ============================================================================
-- NOTIFICATIONS LEDGER
-- ============================================================================

create table if not exists ops.notifications (
  id bigserial primary key,
  ts timestamptz not null default now(),
  run_id uuid references ops.runs(id) on delete set null,
  alert_rule_id bigint references ops.alert_rules(id) on delete set null,
  kind text not null check (kind in ('webhook', 'email', 'slack', 'log')),
  target text,
  payload jsonb not null default '{}'::jsonb,
  status text not null default 'queued' check (status in ('queued', 'sent', 'failed', 'acked')),
  error text,
  sent_at timestamptz
);

comment on table ops.notifications is 'Notification delivery ledger';

create index if not exists notifications_status_ts_idx on ops.notifications(status, ts) where status = 'queued';

-- ============================================================================
-- MULTI-SIGNAL SCORING
-- ============================================================================

create table if not exists ops.signal_weights (
  signal_type text primary key,                    -- 'schema_drift', 'ci_fail', 'latency', 'error_rate', 'cost'
  weight numeric not null,
  direction text not null default 'positive' check (direction in ('positive', 'negative')),
  description text,
  updated_at timestamptz not null default now()
);

comment on table ops.signal_weights is 'Weights for multi-signal scoring';

create table if not exists ops.signals (
  id bigserial primary key,
  run_id uuid not null references ops.runs(id) on delete cascade,
  ts timestamptz not null default now(),
  signal_type text not null,
  value numeric,
  label text,
  data jsonb not null default '{}'::jsonb
);

comment on table ops.signals is 'Signal inputs for run scoring';

create index if not exists signals_run_id_ts_idx on ops.signals(run_id, ts desc);
create index if not exists signals_type_ts_idx on ops.signals(signal_type, ts desc);

create table if not exists ops.run_scores (
  run_id uuid primary key references ops.runs(id) on delete cascade,
  ts timestamptz not null default now(),
  score numeric not null,
  breakdown jsonb not null default '{}'::jsonb
);

comment on table ops.run_scores is 'Computed scores for runs';

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Claim next available run (atomic with SKIP LOCKED)
create or replace function ops.claim_run(p_executor uuid)
returns table(run_id uuid, kind text, spec jsonb, artifact_base_uri text)
language plpgsql as $$
declare
  v_run_id uuid;
begin
  -- Verify executor exists and is active
  if not exists (select 1 from ops.executors where id = p_executor and is_active = true) then
    raise exception 'Executor not found or inactive: %', p_executor;
  end if;

  -- Update last_seen
  update ops.executors set last_seen_at = now() where id = p_executor;

  -- Claim next queued run
  return query
  with next_run as (
    select r.id
    from ops.runs r
    where r.status = 'queued'
    order by r.priority asc, r.created_at asc
    for update skip locked
    limit 1
  )
  update ops.runs r
  set
    status = 'claimed',
    claimed_by = p_executor,
    claimed_at = now(),
    heartbeat_at = now(),
    updated_at = now()
  from next_run
  where r.id = next_run.id
  returning r.id, r.kind, r.spec, r.artifact_base_uri;
end $$;

-- Update run heartbeat
create or replace function ops.heartbeat_run(p_run_id uuid, p_phase text default null)
returns boolean
language plpgsql as $$
begin
  update ops.runs
  set
    heartbeat_at = now(),
    phase = coalesce(p_phase, phase),
    updated_at = now()
  where id = p_run_id and status in ('claimed', 'running');

  return found;
end $$;

-- Start run execution
create or replace function ops.start_run(p_run_id uuid)
returns boolean
language plpgsql as $$
begin
  update ops.runs
  set
    status = 'running',
    phase = 'prepare',
    started_at = now(),
    heartbeat_at = now(),
    updated_at = now()
  where id = p_run_id and status = 'claimed';

  if found then
    insert into ops.run_events(run_id, level, phase, message)
    values (p_run_id, 'info', 'prepare', 'Run started');
  end if;

  return found;
end $$;

-- Complete run successfully
create or replace function ops.complete_run(p_run_id uuid)
returns boolean
language plpgsql as $$
begin
  update ops.runs
  set
    status = 'succeeded',
    phase = 'finalize',
    finished_at = now(),
    updated_at = now()
  where id = p_run_id and status = 'running';

  if found then
    insert into ops.run_events(run_id, level, phase, message)
    values (p_run_id, 'info', 'finalize', 'Run completed successfully');
  end if;

  return found;
end $$;

-- Fail run
create or replace function ops.fail_run(
  p_run_id uuid,
  p_error_code text default null,
  p_error_message text default null,
  p_error_data jsonb default null
)
returns boolean
language plpgsql as $$
declare
  v_retry_count int;
  v_max_retries int;
begin
  select retry_count, max_retries into v_retry_count, v_max_retries
  from ops.runs where id = p_run_id;

  if v_retry_count < v_max_retries then
    -- Requeue for retry
    update ops.runs
    set
      status = 'queued',
      phase = null,
      retry_count = retry_count + 1,
      claimed_by = null,
      claimed_at = null,
      heartbeat_at = null,
      error_code = p_error_code,
      error_message = p_error_message,
      error_data = p_error_data,
      updated_at = now()
    where id = p_run_id;

    insert into ops.run_events(run_id, level, phase, message, data)
    values (p_run_id, 'warn', 'execute', 'Run failed, requeued for retry',
            jsonb_build_object('retry_count', v_retry_count + 1, 'error', p_error_message));
  else
    -- Final failure
    update ops.runs
    set
      status = 'failed',
      finished_at = now(),
      error_code = p_error_code,
      error_message = p_error_message,
      error_data = p_error_data,
      updated_at = now()
    where id = p_run_id;

    insert into ops.run_events(run_id, level, phase, message, data)
    values (p_run_id, 'error', 'execute', 'Run failed permanently',
            jsonb_build_object('error_code', p_error_code, 'error', p_error_message));
  end if;

  return found;
end $$;

-- Cancel run
create or replace function ops.cancel_run(p_run_id uuid)
returns boolean
language plpgsql as $$
begin
  update ops.runs
  set
    status = 'canceled',
    finished_at = now(),
    updated_at = now()
  where id = p_run_id and status in ('queued', 'claimed', 'running');

  if found then
    insert into ops.run_events(run_id, level, phase, message)
    values (p_run_id, 'info', null, 'Run canceled');
  end if;

  return found;
end $$;

-- Compute weighted score for a run
create or replace function ops.compute_run_score(p_run_id uuid)
returns table(score numeric, breakdown jsonb)
language plpgsql as $$
declare
  b jsonb := '{}'::jsonb;
  total numeric := 0;
  w record;
  v numeric;
begin
  for w in select * from ops.signal_weights loop
    select s.value into v
    from ops.signals s
    where s.run_id = p_run_id and s.signal_type = w.signal_type and s.value is not null
    order by s.ts desc
    limit 1;

    if v is not null then
      if w.direction = 'negative' then
        total := total - (v * w.weight);
        b := b || jsonb_build_object(w.signal_type, jsonb_build_object('value', v, 'weight', w.weight, 'contrib', -(v*w.weight)));
      else
        total := total + (v * w.weight);
        b := b || jsonb_build_object(w.signal_type, jsonb_build_object('value', v, 'weight', w.weight, 'contrib', (v*w.weight)));
      end if;
    end if;
  end loop;

  insert into ops.run_scores(run_id, score, breakdown)
  values (p_run_id, total, b)
  on conflict (run_id) do update
    set ts = now(), score = excluded.score, breakdown = excluded.breakdown;

  return query select total, b;
end $$;

-- Cap enforcement check
create or replace function ops.cap_allow(p_cap_key text, p_amount numeric)
returns boolean
language plpgsql as $$
declare
  v_limit numeric;
  v_window text;
  v_used numeric;
  v_window_start timestamptz;
begin
  select limit_value, window into v_limit, v_window
  from ops.caps
  where key = p_cap_key and is_enabled = true;

  if v_limit is null then
    return true; -- no cap configured
  end if;

  -- Calculate window start
  v_window_start := case v_window
    when 'hour' then date_trunc('hour', now())
    when 'day' then date_trunc('day', now())
    when 'week' then date_trunc('week', now())
    when 'month' then date_trunc('month', now())
    else date_trunc('day', now())
  end;

  select coalesce(sum(amount), 0) into v_used
  from ops.cap_usage
  where cap_key = p_cap_key and ts >= v_window_start;

  return (v_used + p_amount) <= v_limit;
end $$;

-- Requeue stale claimed runs (lease expiry)
create or replace function ops.requeue_stale_runs(p_stale_minutes int default 15)
returns int
language plpgsql as $$
declare
  v_count int;
begin
  with stale as (
    update ops.runs
    set
      status = 'queued',
      claimed_by = null,
      claimed_at = null,
      heartbeat_at = null,
      updated_at = now()
    where status in ('claimed', 'running')
      and heartbeat_at < now() - (p_stale_minutes || ' minutes')::interval
    returning id
  )
  select count(*) into v_count from stale;

  return v_count;
end $$;

-- ============================================================================
-- SEED DATA
-- ============================================================================

-- Default signal weights
insert into ops.signal_weights(signal_type, weight, direction, description) values
  ('schema_drift', 10, 'negative', 'Schema drift detected'),
  ('ci_fail', 8, 'negative', 'CI/CD failure'),
  ('error_rate', 6, 'negative', 'Error rate percentage'),
  ('latency_ms', 0.001, 'negative', 'Latency in milliseconds'),
  ('cost_usd', 1, 'negative', 'Cost in USD')
on conflict (signal_type) do update
  set weight = excluded.weight, direction = excluded.direction, description = excluded.description, updated_at = now();

-- Default caps
insert into ops.caps(key, limit_value, window, description) values
  ('spark_minutes_per_day', 1000, 'day', 'Spark compute minutes per day'),
  ('sql_queries_per_hour', 500, 'hour', 'SQL queries per hour'),
  ('storage_gb_total', 100, 'month', 'Total storage in GB per month'),
  ('runs_per_day', 1000, 'day', 'Total runs per day')
on conflict (key) do update
  set limit_value = excluded.limit_value, window = excluded.window, description = excluded.description, updated_at = now();

-- Default routing matrix
insert into ops.routing_matrix(match, route, priority, is_active, description) values
  ('{"severity":"critical"}',
   '{"channels":["webhook"],"owners":["oncall"],"escalation":[{"after_minutes":10,"owners":["engineering-lead"]},{"after_minutes":30,"owners":["exec"]}]}',
   10, true, 'Critical severity - immediate escalation'),
  ('{"tag":"schema_drift","severity":"high"}',
   '{"channels":["webhook"],"owners":["data-platform"],"escalation":[{"after_minutes":20,"owners":["oncall"]}]}',
   20, true, 'Schema drift - data platform team'),
  ('{"kind":"spark","severity":"high"}',
   '{"channels":["webhook"],"owners":["data-platform"],"escalation":[{"after_minutes":30,"owners":["oncall"]}]}',
   30, true, 'Spark job failures'),
  ('{"severity":"medium"}',
   '{"channels":["webhook"],"owners":["triage"],"escalation":[{"after_minutes":60,"owners":["oncall"]}]}',
   60, true, 'Medium severity - triage queue')
on conflict do nothing;
