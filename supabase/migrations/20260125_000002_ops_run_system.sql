-- ops.runs: Agent run auditability and determinism tracking
-- This schema provides enterprise-grade auditability at the app layer

create schema if not exists ops;

-- Main runs table: tracks each agent/workflow execution
create table if not exists ops.runs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  status text not null default 'queued' check (status in ('queued', 'running', 'completed', 'failed', 'cancelled')),
  actor text,
  repo text,
  ref text,
  pack_id text,
  input jsonb not null default '{}'::jsonb,
  output jsonb not null default '{}'::jsonb
);

-- Run events: detailed event log for each run
create table if not exists ops.run_events (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references ops.runs(id) on delete cascade,
  created_at timestamptz not null default now(),
  level text not null default 'info' check (level in ('debug', 'info', 'warn', 'error')),
  message text not null,
  data jsonb not null default '{}'::jsonb
);

-- Artifacts: files/outputs produced by runs
create table if not exists ops.artifacts (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references ops.runs(id) on delete cascade,
  created_at timestamptz not null default now(),
  kind text not null,
  uri text,
  meta jsonb not null default '{}'::jsonb
);

-- Updated_at maintenance trigger
create or replace function ops.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end $$;

drop trigger if exists trg_ops_runs_updated_at on ops.runs;
create trigger trg_ops_runs_updated_at
before update on ops.runs
for each row execute function ops.set_updated_at();

-- Helper functions for agent use
create or replace function ops.start_run(
  p_actor text,
  p_repo text default null,
  p_ref text default null,
  p_pack_id text default null,
  p_input jsonb default '{}'::jsonb
)
returns uuid
language plpgsql
security definer
as $$
declare
  v_run_id uuid;
begin
  insert into ops.runs(actor, repo, ref, pack_id, input, status)
  values (p_actor, p_repo, p_ref, p_pack_id, p_input, 'running')
  returning id into v_run_id;

  perform ops.log_event(v_run_id, 'info', 'Run started');
  return v_run_id;
end $$;

create or replace function ops.log_event(
  p_run_id uuid,
  p_level text,
  p_message text,
  p_data jsonb default '{}'::jsonb
)
returns uuid
language plpgsql
security definer
as $$
declare
  v_event_id uuid;
begin
  insert into ops.run_events(run_id, level, message, data)
  values (p_run_id, p_level, p_message, p_data)
  returning id into v_event_id;

  return v_event_id;
end $$;

create or replace function ops.complete_run(
  p_run_id uuid,
  p_output jsonb default '{}'::jsonb
)
returns void
language plpgsql
security definer
as $$
begin
  update ops.runs
  set status = 'completed', output = p_output
  where id = p_run_id;

  perform ops.log_event(p_run_id, 'info', 'Run completed');
end $$;

create or replace function ops.fail_run(
  p_run_id uuid,
  p_error text,
  p_output jsonb default '{}'::jsonb
)
returns void
language plpgsql
security definer
as $$
begin
  update ops.runs
  set status = 'failed', output = p_output || jsonb_build_object('error', p_error)
  where id = p_run_id;

  perform ops.log_event(p_run_id, 'error', p_error);
end $$;

create or replace function ops.add_artifact(
  p_run_id uuid,
  p_kind text,
  p_uri text default null,
  p_meta jsonb default '{}'::jsonb
)
returns uuid
language plpgsql
security definer
as $$
declare
  v_artifact_id uuid;
begin
  insert into ops.artifacts(run_id, kind, uri, meta)
  values (p_run_id, p_kind, p_uri, p_meta)
  returning id into v_artifact_id;

  return v_artifact_id;
end $$;

-- Indexes for common queries
create index if not exists idx_ops_runs_status on ops.runs(status);
create index if not exists idx_ops_runs_actor on ops.runs(actor);
create index if not exists idx_ops_runs_created_at on ops.runs(created_at desc);
create index if not exists idx_ops_run_events_run_id on ops.run_events(run_id);
create index if not exists idx_ops_artifacts_run_id on ops.artifacts(run_id);

-- Restrict public access
revoke all on schema ops from public;
revoke all on all tables in schema ops from public;
revoke all on all functions in schema ops from public;

comment on schema ops is 'Agent run auditability and determinism tracking - enterprise parity at app layer';
comment on table ops.runs is 'Main runs table tracking each agent/workflow execution';
comment on table ops.run_events is 'Detailed event log for each run';
comment on table ops.artifacts is 'Files and outputs produced by runs';
