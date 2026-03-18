-- ===========================================================================
-- OPS ROUTING MATRIX + ESCALATION
-- Route rules, escalation policies, acknowledgements, time gating
-- ===========================================================================

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- 1) Route rules: match by system/env/component/severity and score range
-- ---------------------------------------------------------------------------
create table if not exists ops.route_rules (
  id uuid primary key default gen_random_uuid(),

  system text not null,
  environment text not null,

  component text not null default 'general', -- odoo|mirror|auth|db|etl|edge|general
  severity text not null check (severity in ('info','warn','critical')),

  score_min int not null default 0,
  score_max int not null default 100,

  -- Time gating (Asia/Manila). If null => always
  active_days text[] null,              -- e.g. {Mon,Tue,Wed,Thu,Fri}
  active_start_local time null,         -- 09:00
  active_end_local time null,           -- 18:00
  timezone text not null default 'Asia/Manila',

  -- Routing target
  mattermost_webhook_url text not null,
  route_label text not null,            -- e.g. ops-warn, ops-critical, finance, data

  cooldown_minutes int not null default 15,

  escalation_policy_id uuid null,       -- optional
  priority int not null default 3,       -- 1 highest

  is_enabled boolean not null default true,

  unique(system, environment, component, severity, score_min, score_max, route_label)
);

create index if not exists idx_ops_route_rules_match
  on ops.route_rules(system, environment, component, severity, is_enabled, priority);

-- ---------------------------------------------------------------------------
-- 2) Escalation policies: step ladder
-- ---------------------------------------------------------------------------
create table if not exists ops.escalation_policies (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  description text null,
  is_enabled boolean not null default true
);

create table if not exists ops.escalation_steps (
  id uuid primary key default gen_random_uuid(),
  policy_id uuid not null references ops.escalation_policies(id) on delete cascade,
  step_index int not null,
  after_minutes int not null,
  webhook_url text not null,
  message_prefix text not null default 'ESCALATION',
  unique(policy_id, step_index)
);

create index if not exists idx_ops_escalation_steps_policy
  on ops.escalation_steps(policy_id, step_index);

-- ---------------------------------------------------------------------------
-- 3) Acknowledgements (for incidents or correlation keys)
-- ---------------------------------------------------------------------------
create table if not exists ops.acks (
  id uuid primary key default gen_random_uuid(),
  correlation_key text not null,
  incident_id uuid null,
  acked_by text null,
  acked_at timestamptz not null default now(),
  expires_at timestamptz null,
  note text null
);

create index if not exists idx_ops_acks_corr_time
  on ops.acks(correlation_key, acked_at desc);

-- ---------------------------------------------------------------------------
-- 4) Escalation state per correlation
-- ---------------------------------------------------------------------------
create table if not exists ops.escalation_state (
  correlation_key text primary key,
  policy_id uuid not null references ops.escalation_policies(id),
  incident_id uuid null,
  started_at timestamptz not null default now(),
  last_escalated_at timestamptz null,
  current_step_index int not null default 0,
  is_active boolean not null default true,
  context jsonb not null default '{}'::jsonb
);

-- ---------------------------------------------------------------------------
-- 5) Pick route rule (priority order, time gating)
-- ---------------------------------------------------------------------------
create or replace function ops.pick_route_rule(
  p_system text,
  p_environment text,
  p_component text,
  p_severity text,
  p_score int,
  p_now timestamptz default now()
) returns ops.route_rules
language plpgsql
stable
as $$
declare
  r ops.route_rules;
  dow text;
  local_t time;
begin
  -- day-of-week token
  dow := to_char(p_now at time zone 'UTC' at time zone 'Asia/Manila', 'Dy');
  local_t := (p_now at time zone 'UTC' at time zone 'Asia/Manila')::time;

  select * into r
  from ops.route_rules
  where is_enabled
    and system=p_system
    and environment=p_environment
    and component in (p_component, 'general')
    and severity=p_severity
    and p_score between score_min and score_max
    and (
      active_days is null
      or dow = any(active_days)
    )
    and (
      active_start_local is null
      or active_end_local is null
      or (local_t between active_start_local and active_end_local)
    )
  order by priority asc, component desc
  limit 1;

  return r;
end;
$$;

-- ---------------------------------------------------------------------------
-- 6) Check if acknowledged
-- ---------------------------------------------------------------------------
create or replace function ops.is_acked(p_correlation_key text, p_now timestamptz default now())
returns boolean
language plpgsql
stable
as $$
declare
  a ops.acks;
begin
  select * into a
  from ops.acks
  where correlation_key=p_correlation_key
  order by acked_at desc
  limit 1;

  if a.id is null then
    return false;
  end if;

  if a.expires_at is null then
    return true;
  end if;

  return a.expires_at > p_now;
end;
$$;

-- ---------------------------------------------------------------------------
-- 7) Last alert time for a key
-- ---------------------------------------------------------------------------
create or replace function ops.last_alert_at(p_alert_key text)
returns timestamptz
language sql
stable
as $$
  select max(fired_at) from ops.alert_events where alert_key = p_alert_key;
$$;
