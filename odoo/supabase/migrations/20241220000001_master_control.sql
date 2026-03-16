-- Pulser Master Control — v0.1 schema
-- Core tables for work orchestration, SLA enforcement, and evidence collection
--
-- Usage:
--   supabase db reset  # Apply all migrations
--   supabase db diff   # Check drift

-- ============================================================================
-- Schema Setup
-- ============================================================================
create schema if not exists runtime;

-- ============================================================================
-- Work Items (Tickets / Tasks)
-- ============================================================================
-- The central entity for all work: GitHub PRs, Odoo events, manual requests
create table if not exists runtime.work_items (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,

  -- Source identification
  source text not null,                 -- github_pr | odoo_event | manual | bpmn
  source_ref text not null,             -- PR URL | ticket id | process instance

  -- Work item details
  title text not null,
  description text,
  status text not null default 'open',  -- open | running | blocked | done | cancelled
  lane text,                            -- DEV | HR | IT | FIN | MGR
  priority int not null default 3,      -- 1=critical, 2=high, 3=medium, 4=low

  -- Hierarchy support (for BPMN subprocess expansion)
  parent_id uuid references runtime.work_items(id) on delete set null,

  -- Assignment
  assignee_id text,                     -- User ID (from Odoo or external)
  assignee_email text,

  -- Flexible payload
  payload jsonb not null default '{}'::jsonb,
  tags text[] default array[]::text[],

  -- Timestamps
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  resolved_at timestamptz,

  -- Constraints
  constraint chk_status check (status in ('open', 'running', 'blocked', 'done', 'cancelled')),
  constraint chk_lane check (lane is null or lane in ('DEV', 'HR', 'IT', 'FIN', 'MGR')),
  constraint chk_priority check (priority between 1 and 4)
);

comment on table runtime.work_items is 'Central work item table for all intake sources';
comment on column runtime.work_items.source is 'Origin: github_pr, odoo_event, manual, bpmn';
comment on column runtime.work_items.lane is 'Routing lane: DEV, HR, IT, FIN, MGR';

-- Indexes for common queries
create index if not exists ix_work_items_tenant_status
  on runtime.work_items (tenant_id, status, updated_at desc);

create index if not exists ix_work_items_lane
  on runtime.work_items (tenant_id, lane, status) where lane is not null;

create index if not exists ix_work_items_parent
  on runtime.work_items (parent_id) where parent_id is not null;

create unique index if not exists ux_work_items_source_ref
  on runtime.work_items (tenant_id, source, source_ref);

-- ============================================================================
-- Runs (Agent Execution Sessions)
-- ============================================================================
-- Each run represents a plan→apply→verify cycle
create table if not exists runtime.runs (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  work_item_id uuid not null references runtime.work_items(id) on delete cascade,

  -- Execution state
  stage text not null default 'planned',  -- planned | applying | verifying | done | failed
  runner text,                             -- Worker identity

  -- Timing
  started_at timestamptz not null default now(),
  finished_at timestamptz,

  -- Metadata (patch plan, tool calls, etc.)
  meta jsonb not null default '{}'::jsonb,

  constraint chk_run_stage check (stage in ('planned', 'applying', 'verifying', 'done', 'failed'))
);

comment on table runtime.runs is 'Agent execution runs (plan→apply→verify cycles)';

create index if not exists ix_runs_work_item
  on runtime.runs (tenant_id, work_item_id, started_at desc);

create index if not exists ix_runs_stage
  on runtime.runs (tenant_id, stage, started_at desc);

-- ============================================================================
-- Run Logs (Execution Trace)
-- ============================================================================
create table if not exists runtime.run_logs (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  run_id uuid not null references runtime.runs(id) on delete cascade,

  -- Log entry
  level text not null default 'info',     -- debug | info | warn | error
  message text not null,
  detail jsonb not null default '{}'::jsonb,

  created_at timestamptz not null default now(),

  constraint chk_log_level check (level in ('debug', 'info', 'warn', 'error'))
);

comment on table runtime.run_logs is 'Execution logs for runs (tool calls, decisions)';

create index if not exists ix_run_logs_run
  on runtime.run_logs (tenant_id, run_id, created_at asc);

-- ============================================================================
-- SLA Timers
-- ============================================================================
-- Track response and resolution SLAs per work item
create table if not exists runtime.sla_timers (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  work_item_id uuid not null references runtime.work_items(id) on delete cascade,

  -- Timer configuration
  timer_type text not null default 'resolution',  -- response | resolution | custom
  due_at timestamptz not null,

  -- State
  breached boolean not null default false,
  paused_at timestamptz,                          -- For blocked items

  -- Tracking
  last_checked_at timestamptz,
  breached_at timestamptz,

  constraint chk_timer_type check (timer_type in ('response', 'resolution', 'custom'))
);

comment on table runtime.sla_timers is 'SLA timers with breach detection';

create index if not exists ix_sla_by_due
  on runtime.sla_timers (tenant_id, breached, due_at asc)
  where breached = false and paused_at is null;

create index if not exists ix_sla_work_item
  on runtime.sla_timers (work_item_id);

-- ============================================================================
-- Evidence (Artifacts / Audit Trail)
-- ============================================================================
-- Immutable evidence collection for compliance
create table if not exists runtime.evidence (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  work_item_id uuid not null references runtime.work_items(id) on delete cascade,

  -- Evidence classification
  kind text not null,                     -- log | patch | doc | report | screenshot | check | approval

  -- Content (URI or inline)
  uri text,                               -- S3/GCS URL or local path
  body text,                              -- Inline content (for small artifacts)

  -- Metadata
  meta jsonb not null default '{}'::jsonb,
  actor_id text,                          -- Who created this evidence

  created_at timestamptz not null default now(),

  constraint chk_evidence_kind check (kind in ('log', 'patch', 'doc', 'report', 'screenshot', 'check', 'approval'))
);

comment on table runtime.evidence is 'Immutable evidence artifacts for audit trail';
comment on column runtime.evidence.uri is 'External storage URL (S3/GCS)';
comment on column runtime.evidence.body is 'Inline content for small artifacts';

create index if not exists ix_evidence_work_item
  on runtime.evidence (tenant_id, work_item_id, created_at desc);

create index if not exists ix_evidence_kind
  on runtime.evidence (tenant_id, kind, created_at desc);

-- ============================================================================
-- Process Definitions (BPMN Templates)
-- ============================================================================
-- Store imported BPMN process definitions
create table if not exists runtime.process_defs (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,

  -- Process identification
  code text not null,                     -- onboarding_v1, offboarding_v1
  name text not null,
  version text not null default '1.0.0',

  -- BPMN content
  bpmn_xml text,                          -- Original BPMN 2.0 XML
  lanes jsonb not null default '[]'::jsonb,      -- Extracted lanes
  nodes jsonb not null default '[]'::jsonb,      -- Extracted tasks/events
  edges jsonb not null default '[]'::jsonb,      -- Sequence flows

  -- Metadata
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

comment on table runtime.process_defs is 'BPMN process definitions for work item generation';

create unique index if not exists ux_process_defs_code_version
  on runtime.process_defs (tenant_id, code, version);

-- ============================================================================
-- Process Instances (Running Processes)
-- ============================================================================
create table if not exists runtime.process_instances (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  process_def_id uuid not null references runtime.process_defs(id) on delete cascade,

  -- Instance state
  status text not null default 'running',  -- running | completed | cancelled
  current_node text,                       -- Current BPMN node ID

  -- Context
  context jsonb not null default '{}'::jsonb,  -- Variables for gateway evaluation

  -- Timing
  started_at timestamptz not null default now(),
  completed_at timestamptz,

  -- Link to root work item
  root_work_item_id uuid references runtime.work_items(id) on delete set null,

  constraint chk_instance_status check (status in ('running', 'completed', 'cancelled'))
);

comment on table runtime.process_instances is 'Running instances of BPMN processes';

create index if not exists ix_process_instances_def
  on runtime.process_instances (tenant_id, process_def_id, status);

-- ============================================================================
-- Escalation Rules
-- ============================================================================
create table if not exists runtime.escalation_rules (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,

  -- Matching criteria
  lane text,
  priority int,

  -- Escalation targets
  notify_channel text,                    -- slack | email | webhook
  notify_target text,                     -- Channel ID, email, or URL

  -- Timing
  escalate_after_minutes int not null default 60,
  is_active boolean not null default true,

  created_at timestamptz not null default now()
);

comment on table runtime.escalation_rules is 'SLA breach escalation configuration';

-- ============================================================================
-- Functions and Triggers
-- ============================================================================

-- Auto-update updated_at timestamp
create or replace function runtime.touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_touch_work_items on runtime.work_items;
create trigger trg_touch_work_items
  before update on runtime.work_items
  for each row execute function runtime.touch_updated_at();

drop trigger if exists trg_touch_process_defs on runtime.process_defs;
create trigger trg_touch_process_defs
  before update on runtime.process_defs
  for each row execute function runtime.touch_updated_at();

-- Auto-create SLA timer on work item insert
create or replace function runtime.create_sla_timer()
returns trigger language plpgsql as $$
declare
  sla_minutes int;
begin
  -- Default SLA based on priority (can be configured via escalation_rules)
  sla_minutes := case new.priority
    when 1 then 240   -- 4 hours for P1
    when 2 then 480   -- 8 hours for P2
    when 3 then 1440  -- 24 hours for P3
    else 4320         -- 72 hours for P4
  end;

  insert into runtime.sla_timers (tenant_id, work_item_id, timer_type, due_at)
  values (new.tenant_id, new.id, 'resolution', now() + (sla_minutes || ' minutes')::interval);

  return new;
end;
$$;

drop trigger if exists trg_create_sla_timer on runtime.work_items;
create trigger trg_create_sla_timer
  after insert on runtime.work_items
  for each row execute function runtime.create_sla_timer();

-- Set resolved_at when status changes to done
create or replace function runtime.set_resolved_at()
returns trigger language plpgsql as $$
begin
  if new.status = 'done' and old.status != 'done' then
    new.resolved_at = now();
  end if;
  return new;
end;
$$;

drop trigger if exists trg_set_resolved_at on runtime.work_items;
create trigger trg_set_resolved_at
  before update on runtime.work_items
  for each row execute function runtime.set_resolved_at();

-- ============================================================================
-- RPC: Check SLA breaches
-- ============================================================================
create or replace function runtime.check_sla_breaches()
returns table (
  work_item_id uuid,
  timer_id uuid,
  title text,
  lane text,
  priority int,
  due_at timestamptz,
  minutes_overdue int
) language sql as $$
  update runtime.sla_timers
  set breached = true,
      breached_at = now(),
      last_checked_at = now()
  where breached = false
    and paused_at is null
    and due_at < now()
  returning
    work_item_id,
    id as timer_id,
    (select w.title from runtime.work_items w where w.id = work_item_id) as title,
    (select w.lane from runtime.work_items w where w.id = work_item_id) as lane,
    (select w.priority from runtime.work_items w where w.id = work_item_id) as priority,
    due_at,
    extract(epoch from (now() - due_at))::int / 60 as minutes_overdue;
$$;

comment on function runtime.check_sla_breaches is 'Mark and return newly breached SLA timers';

-- ============================================================================
-- RPC: Get work item stats
-- ============================================================================
create or replace function runtime.get_work_item_stats(p_tenant_id uuid)
returns table (
  lane text,
  status text,
  priority int,
  count bigint
) language sql as $$
  select lane, status, priority, count(*)
  from runtime.work_items
  where tenant_id = p_tenant_id
  group by lane, status, priority
  order by lane, status, priority;
$$;

comment on function runtime.get_work_item_stats is 'Aggregate work item counts by lane/status/priority';

-- ============================================================================
-- Sample Data (for testing)
-- ============================================================================
-- Uncomment to seed test data:
/*
insert into runtime.work_items (tenant_id, source, source_ref, title, lane, priority, payload)
values
  ('00000000-0000-0000-0000-000000000001', 'github_pr', 'https://github.com/org/repo/pull/1', 'Fix CI: lint failures', 'DEV', 2, '{"pr_number": 1}'),
  ('00000000-0000-0000-0000-000000000001', 'odoo_event', 'hr.employee:42:hire', 'Onboard: John Doe', 'HR', 2, '{"employee_id": 42}'),
  ('00000000-0000-0000-0000-000000000001', 'manual', 'REQ-2024-001', 'Expense Report Review', 'FIN', 3, '{"amount": 1500.00}');
*/
