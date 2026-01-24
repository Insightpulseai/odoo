-- ===========================================================================
-- OPS HARDENING: Idempotency, DLQ, Constraints
-- ===========================================================================

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- 1) Idempotency: store processed event ids (global dedupe)
-- ---------------------------------------------------------------------------
create table if not exists ops.ingest_dedupe (
  event_id text primary key,
  first_seen_at timestamptz not null default now(),
  topic text,
  action text,
  source text,
  payload_hash text
);

create index if not exists idx_ops_ingest_dedupe_time
  on ops.ingest_dedupe(first_seen_at desc);

-- ---------------------------------------------------------------------------
-- 2) Dead-letter queue for ingest failures
-- ---------------------------------------------------------------------------
create table if not exists ops.ingest_dlq (
  id uuid primary key default gen_random_uuid(),
  event_id text,
  reason text not null,
  payload jsonb not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_ops_ingest_dlq_time
  on ops.ingest_dlq(created_at desc);

-- ---------------------------------------------------------------------------
-- 3) Minimal constraints for safety
-- ---------------------------------------------------------------------------
do $$
begin
  if not exists (
    select 1 from pg_constraint where conname = 'deployments_system_chk'
  ) then
    alter table ops.deployments
      add constraint deployments_system_chk check (length(system) > 3);
  end if;
exception when others then null;
end $$;

do $$
begin
  if not exists (
    select 1 from pg_constraint where conname = 'incidents_system_chk'
  ) then
    alter table ops.incidents
      add constraint incidents_system_chk check (length(system) > 3);
  end if;
exception when others then null;
end $$;

-- ---------------------------------------------------------------------------
-- 4) Retention helpers: mark old run events for cleanup
-- ---------------------------------------------------------------------------
create or replace function ops.cleanup_run_events(p_days int)
returns int
language plpgsql
as $$
declare
  n int;
begin
  delete from ops.run_events where created_at < now() - make_interval(days => p_days);
  get diagnostics n = row_count;
  return n;
end;
$$;

create or replace function ops.cleanup_ingest_dedupe(p_days int)
returns int
language plpgsql
as $$
declare
  n int;
begin
  delete from ops.ingest_dedupe where first_seen_at < now() - make_interval(days => p_days);
  get diagnostics n = row_count;
  return n;
end;
$$;

-- ---------------------------------------------------------------------------
-- 5) Views for dashboarding
-- ---------------------------------------------------------------------------
create or replace view ops.ingest_health_v as
select
  date_trunc('hour', created_at) as hour,
  count(*) filter (where level='error') as errors,
  count(*) as total
from ops.run_events
group by 1
order by 1 desc;

create or replace view ops.dlq_summary_v as
select
  date_trunc('day', created_at) as day,
  count(*) as dlq_count,
  count(distinct event_id) as unique_events
from ops.ingest_dlq
group by 1
order by 1 desc;

-- ---------------------------------------------------------------------------
-- 6) Ensure incident correlation
-- ---------------------------------------------------------------------------
create or replace function ops.ensure_incident(
  p_system text,
  p_environment text,
  p_severity text,
  p_title text,
  p_correlation_key text,
  p_artifact_ref text,
  p_metadata jsonb
) returns uuid
language plpgsql
as $$
declare
  inc_id uuid;
begin
  select id into inc_id
  from ops.incidents
  where status='open'
    and system=p_system
    and environment=p_environment
    and (metadata->>'correlation_key') = p_correlation_key
  order by started_at desc
  limit 1;

  if inc_id is not null then
    return inc_id;
  end if;

  insert into ops.incidents(system, environment, severity, status, title, started_at, artifact_ref, metadata)
  values (
    p_system,
    p_environment,
    p_severity,
    'open',
    p_title,
    now(),
    p_artifact_ref,
    coalesce(p_metadata,'{}'::jsonb) || jsonb_build_object('correlation_key', p_correlation_key)
  )
  returning id into inc_id;

  return inc_id;
end;
$$;
