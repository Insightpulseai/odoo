-- ===========================================================================
-- OPS SSOT BASE SCHEMA
-- Decoupled Odoo-Supabase architecture: Supabase = ops SSOT, Odoo = business SoR
-- ===========================================================================

create extension if not exists pgcrypto;

create schema if not exists ops;
create schema if not exists mirror;
create schema if not exists audit;

-- ---------------------------------------------------------------------------
-- 1) Runtime identifiers (canonical in SSOT)
-- ---------------------------------------------------------------------------
create table if not exists ops.runtime_identifiers (
  id uuid primary key default gen_random_uuid(),
  environment text not null,         -- prod/dev/stage
  system text not null,              -- erp.insightpulseai.net
  identifiers jsonb not null,        -- host, containers, db, domains, etc
  source text not null default 'git',-- git|manual|probe
  artifact_ref text,                 -- repo@sha:path
  updated_at timestamptz not null default now()
);

create index if not exists idx_ops_runtime_identifiers_system_env
  on ops.runtime_identifiers(system, environment);

-- ---------------------------------------------------------------------------
-- 2) Deployments
-- ---------------------------------------------------------------------------
create table if not exists ops.deployments (
  id uuid primary key default gen_random_uuid(),
  system text not null,
  environment text not null,
  version text,                      -- e.g. git sha or image tag
  status text not null check (status in ('pending','running','succeeded','failed','rolled_back')),
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  artifact_ref text,                 -- pointer into artifacts SSOT
  evidence_ref text,                 -- pointer to evidence bundle
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists idx_ops_deployments_system_env_started
  on ops.deployments(system, environment, started_at desc);

-- ---------------------------------------------------------------------------
-- 3) Incidents
-- ---------------------------------------------------------------------------
create table if not exists ops.incidents (
  id uuid primary key default gen_random_uuid(),
  system text not null,
  environment text not null,
  severity text not null check (severity in ('sev1','sev2','sev3','sev4')),
  status text not null check (status in ('open','mitigated','closed')),
  title text not null,
  started_at timestamptz not null default now(),
  mitigated_at timestamptz,
  closed_at timestamptz,
  timeline jsonb not null default '[]'::jsonb,
  artifact_ref text,
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists idx_ops_incidents_system_env_started
  on ops.incidents(system, environment, started_at desc);

create index if not exists idx_ops_incidents_open
  on ops.incidents(status) where status = 'open';

-- ---------------------------------------------------------------------------
-- 4) Artifact registry
-- ---------------------------------------------------------------------------
create table if not exists ops.artifact_index (
  id uuid primary key default gen_random_uuid(),
  system text not null,
  environment text,
  artifact_ref text not null unique, -- repo@sha:path
  kind text not null,                -- runbook|infra|evidence|config|runtime
  title text,
  refresh_policy jsonb,
  tags text[] not null default '{}',
  created_at timestamptz not null default now()
);

create index if not exists idx_ops_artifact_index_system
  on ops.artifact_index(system, kind);

-- ---------------------------------------------------------------------------
-- 5) Run events for observability (structured logs)
-- ---------------------------------------------------------------------------
create table if not exists ops.run_events (
  id uuid primary key default gen_random_uuid(),
  event_id text,
  level text not null check (level in ('debug','info','warn','error')),
  message text not null,
  context jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_ops_run_events_event_id
  on ops.run_events(event_id, created_at desc);

create index if not exists idx_ops_run_events_level_time
  on ops.run_events(level, created_at desc);

-- ---------------------------------------------------------------------------
-- 6) Mirrored Odoo snapshots (minimal)
-- ---------------------------------------------------------------------------
create table if not exists mirror.odoo_object_snapshots (
  id uuid primary key default gen_random_uuid(),
  odoo_model text not null,
  odoo_id bigint not null,
  external_key text,
  snapshot jsonb not null,
  captured_at timestamptz not null default now(),
  unique (odoo_model, odoo_id, captured_at)
);

create index if not exists idx_mirror_odoo_snapshots_model_id
  on mirror.odoo_object_snapshots(odoo_model, odoo_id, captured_at desc);

-- ---------------------------------------------------------------------------
-- 7) Append-only audit ledger
-- ---------------------------------------------------------------------------
create table if not exists audit.events (
  id uuid primary key default gen_random_uuid(),
  topic text not null,               -- deployments/incidents/mirror/...
  action text not null,              -- create/update/close/...
  actor text,                        -- system/user/agent
  payload jsonb not null,
  occurred_at timestamptz not null default now()
);

create index if not exists idx_audit_events_topic_time
  on audit.events(topic, occurred_at desc);

-- ---------------------------------------------------------------------------
-- 8) Summary views
-- ---------------------------------------------------------------------------
create or replace view ops.latest_deployments_v as
select distinct on (system, environment)
  system, environment, id, version, status, started_at, finished_at, artifact_ref, evidence_ref, metadata
from ops.deployments
order by system, environment, started_at desc;

create or replace view ops.open_incidents_v as
select
  system, environment, id, severity, status, title, started_at, mitigated_at, artifact_ref, metadata
from ops.incidents
where status = 'open'
order by started_at desc;

-- ---------------------------------------------------------------------------
-- 9) RPCs for Odoo mirror (return jsonb for simple consumption)
-- ---------------------------------------------------------------------------
create or replace function ops.get_deployment_summary(p_system text, p_environment text)
returns jsonb
language sql
stable
as $$
  select coalesce(
    (select to_jsonb(t) from (
      select * from ops.latest_deployments_v
      where system = p_system and environment = p_environment
      limit 1
    ) t),
    '{}'::jsonb
  );
$$;

create or replace function ops.get_incident_summary(p_system text, p_environment text)
returns jsonb
language sql
stable
as $$
  select jsonb_build_object(
    'open_count', coalesce((select count(*) from ops.open_incidents_v where system=p_system and environment=p_environment),0),
    'items', coalesce((select jsonb_agg(to_jsonb(i)) from (
      select * from ops.open_incidents_v where system=p_system and environment=p_environment limit 20
    ) i), '[]'::jsonb)
  );
$$;

-- ---------------------------------------------------------------------------
-- 10) Incident timeline helpers
-- ---------------------------------------------------------------------------
create or replace function ops.append_incident_timeline(p_incident_id uuid, p_entry jsonb)
returns void
language plpgsql
as $$
begin
  update ops.incidents
  set timeline = coalesce(timeline,'[]'::jsonb) || jsonb_build_array(p_entry)
  where id = p_incident_id;
end;
$$;

create or replace function ops.mitigate_incident(p_incident_id uuid, p_note text)
returns void
language plpgsql
as $$
begin
  update ops.incidents
  set status='mitigated', mitigated_at=coalesce(mitigated_at, now())
  where id=p_incident_id and status='open';

  perform ops.append_incident_timeline(p_incident_id, jsonb_build_object(
    'ts', now(), 'type', 'mitigated', 'note', p_note
  ));
end;
$$;

create or replace function ops.close_incident(p_incident_id uuid, p_note text)
returns void
language plpgsql
as $$
begin
  update ops.incidents
  set status='closed', closed_at=coalesce(closed_at, now())
  where id=p_incident_id and status <> 'closed';

  perform ops.append_incident_timeline(p_incident_id, jsonb_build_object(
    'ts', now(), 'type', 'closed', 'note', p_note
  ));
end;
$$;
