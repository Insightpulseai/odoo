-- Integration bus for Odoo + n8n + MCP + CMS
-- Safe defaults: RLS ON, service-role for writers, read-only for agents.

create schema if not exists integration;

-- Durable outbox (Odoo/CMS write -> n8n/edge consume)
create table if not exists integration.outbox (
  id uuid primary key default gen_random_uuid(),
  source text not null,                    -- 'odoo' | 'cms' | 'n8n' | 'edge'
  event_type text not null,                -- 'expense.submitted', 'asset.reserved', etc.
  aggregate_type text not null,            -- 'expense', 'asset_booking', 'finance_task'
  aggregate_id text not null,              -- Odoo external ID / model key
  payload jsonb not null,
  idempotency_key text not null,           -- prevent duplicates
  status text not null default 'pending',  -- pending|processing|done|failed|dead
  attempts int not null default 0,
  available_at timestamptz not null default now(),
  locked_at timestamptz,
  locked_by text,
  last_error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (source, idempotency_key)
);

create index if not exists outbox_status_available_idx
  on integration.outbox (status, available_at);

create index if not exists outbox_aggregate_idx
  on integration.outbox (aggregate_type, aggregate_id);

-- Immutable event log (append-only audit)
create table if not exists integration.event_log (
  id uuid primary key default gen_random_uuid(),
  source text not null,
  event_type text not null,
  aggregate_type text not null,
  aggregate_id text not null,
  payload jsonb not null,
  created_at timestamptz not null default now()
);

-- Mapping Odoo <-> Supabase identifiers (and later: Planner/M365 if needed)
create table if not exists integration.id_map (
  id bigserial primary key,
  system text not null,      -- 'odoo'
  model text not null,       -- 'hr.expense', 'project.task', ...
  external_id text not null, -- Odoo record id or XMLID
  internal_id uuid,          -- Supabase-side id (optional)
  meta jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique(system, model, external_id)
);

-- Simple worker claim function (n8n can call this via RPC if desired)
create or replace function integration.claim_outbox(p_limit int default 25, p_worker text default 'worker')
returns setof integration.outbox
language plpgsql
as $$
begin
  return query
  with cte as (
    select id
    from integration.outbox
    where status = 'pending'
      and available_at <= now()
      and (locked_at is null or locked_at < now() - interval '10 minutes')
    order by created_at asc
    limit p_limit
    for update skip locked
  )
  update integration.outbox o
  set status='processing',
      locked_at=now(),
      locked_by=p_worker,
      updated_at=now()
  from cte
  where o.id = cte.id
  returning o.*;
end;
$$;

-- Ack/fail helpers for n8n workflows
create or replace function integration.ack_outbox(p_id uuid)
returns void language plpgsql as $$
begin
  update integration.outbox
  set status='done', locked_at=null, locked_by=null, updated_at=now()
  where id=p_id;
end;
$$;

create or replace function integration.fail_outbox(p_id uuid, p_error text)
returns void language plpgsql as $$
begin
  update integration.outbox
  set status=case when attempts >= 9 then 'dead' else 'pending' end,
      attempts=attempts+1,
      last_error=left(p_error, 2000),
      locked_at=null,
      locked_by=null,
      available_at=now() + (interval '30 seconds' * greatest(1, attempts+1)),
      updated_at=now()
  where id=p_id;
end;
$$;

-- RLS (default: no public access)
alter table integration.outbox enable row level security;
alter table integration.event_log enable row level security;
alter table integration.id_map enable row level security;

-- Policies:
-- 1) Service role can do everything (Edge Functions / n8n w/ service key)
create policy "service_role_all_outbox" on integration.outbox
  for all to service_role using (true) with check (true);

create policy "service_role_all_event_log" on integration.event_log
  for all to service_role using (true) with check (true);

create policy "service_role_all_id_map" on integration.id_map
  for all to service_role using (true) with check (true);

-- 2) Authenticated users: read-only on event_log (optional; tighten later)
create policy "authenticated_read_event_log" on integration.event_log
  for select to authenticated using (true);

-- Trigger to keep updated_at fresh
create or replace function integration.tg_set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists set_updated_at_outbox on integration.outbox;
create trigger set_updated_at_outbox
before update on integration.outbox
for each row execute function integration.tg_set_updated_at();
