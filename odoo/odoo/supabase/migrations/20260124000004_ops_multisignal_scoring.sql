-- ===========================================================================
-- OPS MULTI-SIGNAL SCORING
-- Health windows, persistence gate, weighted score computation
-- ===========================================================================

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- 1) Health windows: rolling history for persistence evaluation
-- ---------------------------------------------------------------------------
create table if not exists ops.health_windows (
  id uuid primary key default gen_random_uuid(),
  system text not null,
  environment text not null,
  window_minutes int not null,
  observed_at timestamptz not null default now(),
  score int not null check (score between 0 and 100),
  severity text not null check (severity in ('info','warn','critical')),
  signals jsonb not null default '{}'::jsonb,      -- raw signal values
  normalized jsonb not null default '{}'::jsonb,   -- normalized 0..1
  weights jsonb not null default '{}'::jsonb,      -- weights used
  meta jsonb not null default '{}'::jsonb          -- thresholds/bands etc
);

create index if not exists idx_ops_health_windows_lookup
  on ops.health_windows(system, environment, observed_at desc);

-- ---------------------------------------------------------------------------
-- 2) Alert state for cooldown/dedupe
-- ---------------------------------------------------------------------------
create table if not exists ops.alert_threads (
  correlation_key text primary key,
  severity text not null check (severity in ('info','warn','critical')),
  last_fired_at timestamptz not null default now(),
  open_incident_id uuid,
  context jsonb not null default '{}'::jsonb
);

-- ---------------------------------------------------------------------------
-- 3) Alert events log (audit trail)
-- ---------------------------------------------------------------------------
create table if not exists ops.alert_events (
  id uuid primary key default gen_random_uuid(),
  alert_key text not null,
  severity text not null check (severity in ('info','warn','critical')),
  message text not null,
  correlation_key text,
  incident_id uuid,
  context jsonb not null default '{}'::jsonb,
  fired_at timestamptz not null default now()
);

create index if not exists idx_ops_alert_events_key_time
  on ops.alert_events(alert_key, fired_at desc);

create index if not exists idx_ops_alert_events_corr_time
  on ops.alert_events(correlation_key, fired_at desc);

-- ---------------------------------------------------------------------------
-- 4) Get alert state (for CI router)
-- ---------------------------------------------------------------------------
create or replace function ops.get_alert_state(
  p_system text,
  p_environment text,
  p_window_minutes int default 60
) returns jsonb
language plpgsql
stable
as $$
declare
  dlq_count int;
  errors_count int;
  total_count int;
begin
  select count(*) into dlq_count from ops.ingest_dlq;

  select
    count(*) filter (where level='error'),
    count(*)
  into errors_count, total_count
  from ops.run_events
  where created_at >= now() - make_interval(mins => p_window_minutes);

  return jsonb_build_object(
    'system', p_system,
    'environment', p_environment,
    'window_minutes', p_window_minutes,
    'dlq_count', dlq_count,
    'errors_count', coalesce(errors_count,0),
    'total_events', coalesce(total_count,0),
    'error_rate', case when coalesce(total_count,0) = 0 then 0 else (errors_count::numeric / total_count::numeric) end
  );
end;
$$;

-- ---------------------------------------------------------------------------
-- 5) Record health window
-- ---------------------------------------------------------------------------
create or replace function ops.record_health_window(
  p_system text,
  p_environment text,
  p_window_minutes int,
  p_score int,
  p_severity text,
  p_signals jsonb,
  p_normalized jsonb,
  p_weights jsonb,
  p_meta jsonb
) returns uuid
language plpgsql
as $$
declare
  rid uuid;
begin
  insert into ops.health_windows(system, environment, window_minutes, score, severity, signals, normalized, weights, meta)
  values (p_system, p_environment, p_window_minutes, p_score, p_severity, coalesce(p_signals,'{}'::jsonb),
          coalesce(p_normalized,'{}'::jsonb), coalesce(p_weights,'{}'::jsonb), coalesce(p_meta,'{}'::jsonb))
  returning id into rid;
  return rid;
end;
$$;

-- ---------------------------------------------------------------------------
-- 6) Persistence gate: N-of-M windows with severity >= target
-- ---------------------------------------------------------------------------
create or replace function ops.persistence_gate(
  p_system text,
  p_environment text,
  p_target text,      -- 'warn' or 'critical'
  p_n int,
  p_m int
) returns boolean
language plpgsql
stable
as $$
declare
  cnt int;
begin
  if p_target not in ('warn','critical') then
    raise exception 'p_target must be warn or critical';
  end if;

  with lastm as (
    select severity
    from ops.health_windows
    where system=p_system and environment=p_environment
    order by observed_at desc
    limit p_m
  )
  select count(*) into cnt
  from lastm
  where (p_target='warn' and severity in ('warn','critical'))
     or (p_target='critical' and severity = 'critical');

  return cnt >= p_n;
end;
$$;

-- ---------------------------------------------------------------------------
-- 7) Cooldown gate (dedupe): returns true if allowed to fire now
-- ---------------------------------------------------------------------------
create or replace function ops.allow_fire(
  p_correlation_key text,
  p_severity text,
  p_incident_id uuid,
  p_cooldown_minutes int,
  p_context jsonb
) returns boolean
language plpgsql
as $$
declare
  last_ts timestamptz;
begin
  select last_fired_at into last_ts from ops.alert_threads where correlation_key = p_correlation_key;

  if last_ts is not null and last_ts > now() - make_interval(mins => p_cooldown_minutes) then
    return false;
  end if;

  insert into ops.alert_threads(correlation_key, severity, last_fired_at, open_incident_id, context)
  values (p_correlation_key, p_severity, now(), p_incident_id, coalesce(p_context,'{}'::jsonb))
  on conflict (correlation_key) do update set
    severity = excluded.severity,
    last_fired_at = excluded.last_fired_at,
    open_incident_id = excluded.open_incident_id,
    context = ops.alert_threads.context || excluded.context;

  return true;
end;
$$;

-- ---------------------------------------------------------------------------
-- 8) Touch thread helper
-- ---------------------------------------------------------------------------
create or replace function ops.touch_thread(
  p_correlation_key text,
  p_severity text,
  p_incident_id uuid,
  p_context jsonb
) returns ops.alert_threads
language plpgsql
as $$
declare
  t ops.alert_threads;
begin
  insert into ops.alert_threads(correlation_key, severity, open_incident_id, context)
  values (p_correlation_key, p_severity, p_incident_id, coalesce(p_context,'{}'::jsonb))
  on conflict (correlation_key) do update set
    severity = excluded.severity,
    open_incident_id = excluded.open_incident_id,
    context = ops.alert_threads.context || excluded.context,
    last_fired_at = now()
  returning * into t;

  return t;
end;
$$;
