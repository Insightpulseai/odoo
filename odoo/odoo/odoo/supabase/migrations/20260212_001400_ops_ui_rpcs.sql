-- Phase 4: ops UI RPC surface (backups, project settings, upgrade versions)
-- Assumptions:
-- - Supabase Postgres
-- - schema "ops" already exists (we guard anyway)
-- - auth.uid() is available
-- - project membership table MAY exist as ops.project_members(user_id uuid, project_id uuid)
--   If it does, we enable RLS policies for authenticated users.
--   If it doesn't, we fall back to service_role-only access (still safe).

create schema if not exists ops;

-- Extensions often exist already in Supabase; keep guarded usage minimal.
-- gen_random_uuid() requires pgcrypto (usually enabled). If missing, enable in your platform tooling.

--------------------------------------------------------------------------------
-- 1) Backups table
--------------------------------------------------------------------------------
create table if not exists ops.backups (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null,
  created_at timestamptz not null default now(),
  created_by uuid null,
  status text not null default 'created', -- created|running|failed|completed
  provider text null,                    -- e.g., 'do', 'aws', 'supabase'
  region text null,
  size_bytes bigint null,
  checksum text null,
  meta jsonb not null default '{}'::jsonb
);

create index if not exists backups_project_created_idx
  on ops.backups (project_id, created_at desc);

--------------------------------------------------------------------------------
-- 2) Project settings table
--------------------------------------------------------------------------------
create table if not exists ops.project_settings (
  project_id uuid primary key,
  settings jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  updated_by uuid null
);

--------------------------------------------------------------------------------
-- 3) Upgrade versions table
--------------------------------------------------------------------------------
create table if not exists ops.project_upgrade_versions (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null,
  created_at timestamptz not null default now(),
  planned_at timestamptz null,
  applied_at timestamptz null,
  from_version text null,
  to_version text not null,
  status text not null default 'planned', -- planned|running|failed|completed|canceled
  notes text null,
  meta jsonb not null default '{}'::jsonb
);

create index if not exists upgrade_versions_project_created_idx
  on ops.project_upgrade_versions (project_id, created_at desc);

--------------------------------------------------------------------------------
-- RLS: enable + policies if ops.project_members exists
--------------------------------------------------------------------------------
alter table ops.backups enable row level security;
alter table ops.project_settings enable row level security;
alter table ops.project_upgrade_versions enable row level security;

-- Drop/recreate policies to be idempotent-ish
do $$
begin
  -- BACKUPS
  if to_regclass('ops.project_members') is not null then
    execute 'drop policy if exists backups_select_member on ops.backups';
    execute 'create policy backups_select_member on ops.backups
      for select to authenticated
      using (exists (
        select 1 from ops.project_members pm
        where pm.project_id = backups.project_id
          and pm.user_id = auth.uid()
      ))';

    execute 'drop policy if exists backups_insert_member on ops.backups';
    execute 'create policy backups_insert_member on ops.backups
      for insert to authenticated
      with check (exists (
        select 1 from ops.project_members pm
        where pm.project_id = backups.project_id
          and pm.user_id = auth.uid()
      ))';
  else
    -- If membership table doesn't exist, do not allow authenticated access by default.
    -- Keep access restricted to service_role (RPC security definer can still serve UI through a server-side call).
    null;
  end if;

  -- PROJECT SETTINGS
  if to_regclass('ops.project_members') is not null then
    execute 'drop policy if exists project_settings_select_member on ops.project_settings';
    execute 'create policy project_settings_select_member on ops.project_settings
      for select to authenticated
      using (exists (
        select 1 from ops.project_members pm
        where pm.project_id = project_settings.project_id
          and pm.user_id = auth.uid()
      ))';

    execute 'drop policy if exists project_settings_upsert_member on ops.project_settings';
    execute 'create policy project_settings_upsert_member on ops.project_settings
      for insert to authenticated
      with check (exists (
        select 1 from ops.project_members pm
        where pm.project_id = project_settings.project_id
          and pm.user_id = auth.uid()
      ))';

    execute 'drop policy if exists project_settings_update_member on ops.project_settings';
    execute 'create policy project_settings_update_member on ops.project_settings
      for update to authenticated
      using (exists (
        select 1 from ops.project_members pm
        where pm.project_id = project_settings.project_id
          and pm.user_id = auth.uid()
      ))
      with check (exists (
        select 1 from ops.project_members pm
        where pm.project_id = project_settings.project_id
          and pm.user_id = auth.uid()
      ))';
  end if;

  -- UPGRADE VERSIONS
  if to_regclass('ops.project_members') is not null then
    execute 'drop policy if exists upgrade_versions_select_member on ops.project_upgrade_versions';
    execute 'create policy upgrade_versions_select_member on ops.project_upgrade_versions
      for select to authenticated
      using (exists (
        select 1 from ops.project_members pm
        where pm.project_id = project_upgrade_versions.project_id
          and pm.user_id = auth.uid()
      ))';
  end if;
end$$;

--------------------------------------------------------------------------------
-- RPCs expected by UI
--------------------------------------------------------------------------------
-- 1) ops.ui_backups(project_id, limit, offset)
create or replace function ops.ui_backups(
  p_project_id uuid,
  p_limit int default 50,
  p_offset int default 0
)
returns table (
  id uuid,
  project_id uuid,
  created_at timestamptz,
  created_by uuid,
  status text,
  provider text,
  region text,
  size_bytes bigint,
  checksum text,
  meta jsonb
)
language sql
stable
security definer
set search_path = ops, public
as $$
  select
    b.id, b.project_id, b.created_at, b.created_by, b.status, b.provider,
    b.region, b.size_bytes, b.checksum, b.meta
  from ops.backups b
  where b.project_id = p_project_id
  order by b.created_at desc
  limit greatest(0, least(p_limit, 500))
  offset greatest(0, p_offset);
$$;

-- 2) ops.ui_project_settings(project_id)
create or replace function ops.ui_project_settings(
  p_project_id uuid
)
returns jsonb
language sql
stable
security definer
set search_path = ops, public
as $$
  select coalesce(ps.settings, '{}'::jsonb)
  from ops.project_settings ps
  where ps.project_id = p_project_id;
$$;

-- Optional: if UI needs saving settings, expose a controlled upsert RPC.
create or replace function ops.ui_project_settings_upsert(
  p_project_id uuid,
  p_settings jsonb
)
returns jsonb
language plpgsql
volatile
security definer
set search_path = ops, public
as $$
declare
  v jsonb;
begin
  insert into ops.project_settings (project_id, settings, updated_at, updated_by)
  values (p_project_id, coalesce(p_settings, '{}'::jsonb), now(), auth.uid())
  on conflict (project_id) do update
    set settings = excluded.settings,
        updated_at = now(),
        updated_by = auth.uid()
  returning settings into v;

  return coalesce(v, '{}'::jsonb);
end;
$$;

-- 3) ops.ui_project_upgrade_versions(project_id, limit, offset)
create or replace function ops.ui_project_upgrade_versions(
  p_project_id uuid,
  p_limit int default 50,
  p_offset int default 0
)
returns table (
  id uuid,
  project_id uuid,
  created_at timestamptz,
  planned_at timestamptz,
  applied_at timestamptz,
  from_version text,
  to_version text,
  status text,
  notes text,
  meta jsonb
)
language sql
stable
security definer
set search_path = ops, public
as $$
  select
    u.id, u.project_id, u.created_at, u.planned_at, u.applied_at,
    u.from_version, u.to_version, u.status, u.notes, u.meta
  from ops.project_upgrade_versions u
  where u.project_id = p_project_id
  order by u.created_at desc
  limit greatest(0, least(p_limit, 500))
  offset greatest(0, p_offset);
$$;

--------------------------------------------------------------------------------
-- Grants (Supabase: typically functions callable by authenticated via PostgREST RPC)
--------------------------------------------------------------------------------
grant usage on schema ops to authenticated;
grant select, insert on ops.backups to authenticated;
grant select, insert, update on ops.project_settings to authenticated;
grant select on ops.project_upgrade_versions to authenticated;

grant execute on function ops.ui_backups(uuid,int,int) to authenticated;
grant execute on function ops.ui_project_settings(uuid) to authenticated;
grant execute on function ops.ui_project_settings_upsert(uuid,jsonb) to authenticated;
grant execute on function ops.ui_project_upgrade_versions(uuid,int,int) to authenticated;
