create schema if not exists registry;
create schema if not exists audit;

-- Organizations
create table if not exists registry.orgs (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  created_at timestamptz not null default now()
);

-- Membership
create table if not exists registry.org_members (
  org_id uuid not null references registry.orgs(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  role text not null check (role in ('admin','operator','viewer')),
  created_at timestamptz not null default now(),
  primary key (org_id, user_id)
);

-- Audit log
create table if not exists audit.events (
  id uuid primary key default gen_random_uuid(),
  org_id uuid references registry.orgs(id),
  actor_user_id uuid references auth.users(id),
  action text not null,
  target jsonb not null default '{}'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- Helper: current user's org ids
create or replace function registry.my_org_ids()
returns setof uuid
language sql stable as $$
  select org_id from registry.org_members where user_id = auth.uid()
$$;

-- RLS
alter table registry.orgs enable row level security;
alter table registry.org_members enable row level security;
alter table audit.events enable row level security;

-- Policies
create policy "orgs: members can read"
on registry.orgs
for select
using (id in (select registry.my_org_ids()));

create policy "org_members: members can read"
on registry.org_members
for select
using (org_id in (select registry.my_org_ids()));

create policy "audit: members can read"
on audit.events
for select
using (org_id in (select registry.my_org_ids()));
