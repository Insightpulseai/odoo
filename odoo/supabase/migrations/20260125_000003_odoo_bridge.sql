-- Odoo Bridge Schema
-- Tables for Odoo integration and synchronization

create schema if not exists odoo;

-- Odoo Instances: registered Odoo installations
create table if not exists odoo.instances (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  name text not null,
  base_url text not null,
  database text not null,
  active boolean not null default true,
  config jsonb not null default '{}'::jsonb
);

-- Sync Cursors: track sync progress per entity
create table if not exists odoo.sync_cursors (
  id uuid primary key default gen_random_uuid(),
  instance_id uuid not null references odoo.instances(id) on delete cascade,
  entity text not null,
  cursor text,
  last_sync_at timestamptz,
  updated_at timestamptz not null default now(),
  unique (instance_id, entity)
);

-- Entity Mappings: ID mapping between Supabase and Odoo
create table if not exists odoo.entity_mappings (
  id uuid primary key default gen_random_uuid(),
  instance_id uuid not null references odoo.instances(id) on delete cascade,
  supabase_schema text not null,
  supabase_table text not null,
  supabase_id uuid not null,
  odoo_model text not null,
  odoo_id integer not null,
  created_at timestamptz not null default now(),
  unique (instance_id, supabase_schema, supabase_table, supabase_id),
  unique (instance_id, odoo_model, odoo_id)
);

-- Webhook Events: incoming events from Odoo
create table if not exists odoo.webhook_events (
  id uuid primary key default gen_random_uuid(),
  instance_id uuid references odoo.instances(id) on delete set null,
  received_at timestamptz not null default now(),
  processed_at timestamptz,
  event_type text not null,
  model text not null,
  record_id integer,
  payload jsonb not null default '{}'::jsonb,
  status text not null default 'pending' check (status in ('pending', 'processing', 'completed', 'failed')),
  error_message text,
  retry_count integer not null default 0
);

-- Indexes
create index if not exists idx_odoo_sync_cursors_instance on odoo.sync_cursors(instance_id);
create index if not exists idx_odoo_entity_mappings_supabase on odoo.entity_mappings(supabase_schema, supabase_table, supabase_id);
create index if not exists idx_odoo_entity_mappings_odoo on odoo.entity_mappings(odoo_model, odoo_id);
create index if not exists idx_odoo_webhook_events_status on odoo.webhook_events(status, received_at);
create index if not exists idx_odoo_webhook_events_instance on odoo.webhook_events(instance_id);

-- Updated_at trigger
create or replace function odoo.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end $$;

drop trigger if exists trg_odoo_instances_updated_at on odoo.instances;
create trigger trg_odoo_instances_updated_at
before update on odoo.instances
for each row execute function odoo.set_updated_at();

drop trigger if exists trg_odoo_sync_cursors_updated_at on odoo.sync_cursors;
create trigger trg_odoo_sync_cursors_updated_at
before update on odoo.sync_cursors
for each row execute function odoo.set_updated_at();

-- Helper functions
create or replace function odoo.get_or_create_mapping(
  p_instance_id uuid,
  p_supabase_schema text,
  p_supabase_table text,
  p_supabase_id uuid,
  p_odoo_model text,
  p_odoo_id integer
)
returns uuid
language plpgsql
as $$
declare
  v_id uuid;
begin
  -- Try to find existing mapping
  select id into v_id
  from odoo.entity_mappings
  where instance_id = p_instance_id
    and supabase_schema = p_supabase_schema
    and supabase_table = p_supabase_table
    and supabase_id = p_supabase_id;

  if v_id is not null then
    return v_id;
  end if;

  -- Create new mapping
  insert into odoo.entity_mappings(
    instance_id, supabase_schema, supabase_table, supabase_id, odoo_model, odoo_id
  ) values (
    p_instance_id, p_supabase_schema, p_supabase_table, p_supabase_id, p_odoo_model, p_odoo_id
  )
  returning id into v_id;

  return v_id;
end $$;

create or replace function odoo.update_sync_cursor(
  p_instance_id uuid,
  p_entity text,
  p_cursor text
)
returns void
language plpgsql
as $$
begin
  insert into odoo.sync_cursors(instance_id, entity, cursor, last_sync_at)
  values (p_instance_id, p_entity, p_cursor, now())
  on conflict (instance_id, entity) do update
    set cursor = excluded.cursor,
        last_sync_at = excluded.last_sync_at;
end $$;

-- Restrict public access (service role only)
revoke all on schema odoo from public;
revoke all on all tables in schema odoo from public;
revoke all on all functions in schema odoo from public;

comment on schema odoo is 'Odoo integration and synchronization tables';
comment on table odoo.instances is 'Registered Odoo installations';
comment on table odoo.sync_cursors is 'Sync progress tracking per entity';
comment on table odoo.entity_mappings is 'ID mapping between Supabase and Odoo';
comment on table odoo.webhook_events is 'Incoming webhook events from Odoo';
