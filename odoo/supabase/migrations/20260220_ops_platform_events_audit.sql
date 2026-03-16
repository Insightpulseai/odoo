-- ops.platform_events: durable audit trail for platform management actions
-- SSOT: Supabase (control plane), SOR: Odoo (accounting/legal)
-- Separate from ops.run_events (agent runs) to maintain clean schema separation

create schema if not exists ops;

create table if not exists ops.platform_events (
  id            uuid primary key default gen_random_uuid(),
  created_at    timestamptz not null default now(),

  -- actor + request context
  user_id       text,
  action        text not null,
  project_ref   text,
  path          text not null,
  method        text not null,
  status        int,

  -- freeform structured payload (bounded)
  payload       jsonb not null default '{}'::jsonb
);

create index if not exists platform_events_created_at_idx on ops.platform_events (created_at desc);
create index if not exists platform_events_project_ref_idx on ops.platform_events (project_ref);
create index if not exists platform_events_action_idx on ops.platform_events (action);

-- RLS: enabled; only service role writes by default; you can add viewer policies later
alter table ops.platform_events enable row level security;

-- No permissive policies by default (service_role bypasses RLS).
