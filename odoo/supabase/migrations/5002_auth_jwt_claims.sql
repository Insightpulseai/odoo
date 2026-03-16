-- ============================================================================
-- JWT Custom Claims: Inject tenant_id + role into access tokens
-- ============================================================================
-- Purpose: Add tenant_id and app role to JWT so RLS policies can enforce
--          tenant isolation without additional DB lookups
--
-- Flow:
--   1. User authenticates via Supabase Auth
--   2. Supabase calls custom_access_token_hook()
--   3. Function looks up user profile and adds claims
--   4. JWT now contains: { sub, email, tenant_id, role, ... }
--   5. RLS policies extract claims via current_setting('request.jwt.claims')
-- ============================================================================

-- 1) Custom Access Token Hook
-- ============================================================================
-- This function is called by Supabase Auth when issuing JWTs
-- It must be named exactly "custom_access_token_hook" to work with Supabase
-- Enable in: Supabase Dashboard → Authentication → Hooks → Custom Access Token

create or replace function public.custom_access_token_hook(event jsonb)
returns jsonb
language plpgsql
stable
security definer
set search_path = public, app, auth
as $func$
declare
  claims jsonb;
  user_profile record;
begin
  -- Extract user ID from auth event
  select
    p.tenant_id,
    p.role,
    p.display_name,
    t.slug as tenant_slug,
    t.is_active as tenant_active
  into user_profile
  from app.profiles p
  join app.tenants t on t.id = p.tenant_id
  where p.user_id = (event->>'user_id')::uuid
    and p.is_active = true;

  -- If user has no profile or tenant is inactive, block access
  if not found or not user_profile.tenant_active then
    claims := jsonb_build_object(
      'tenant_id', null,
      'role', 'none',
      'access_blocked', true
    );
  else
    -- Build custom claims
    claims := jsonb_build_object(
      'tenant_id', user_profile.tenant_id,
      'role', user_profile.role,
      'tenant_slug', user_profile.tenant_slug,
      'display_name', coalesce(user_profile.display_name, '')
    );
  end if;

  -- Merge custom claims into existing JWT claims
  return jsonb_set(
    event,
    '{claims}',
    coalesce(event->'claims', '{}'::jsonb) || claims,
    true
  );
end;
$func$;

comment on function public.custom_access_token_hook is 'Supabase Auth hook to inject tenant_id and role into JWT claims';

-- 2) JWT Claim Helper Functions
-- ============================================================================
-- These functions extract claims from the JWT for use in RLS policies

create or replace function app.current_tenant_id()
returns uuid
language sql
stable
as $func$
  select nullif(
    current_setting('request.jwt.claims', true)::jsonb->>'tenant_id',
    ''
  )::uuid
$func$;

create or replace function app.current_role()
returns text
language sql
stable
as $func$
  select coalesce(
    current_setting('request.jwt.claims', true)::jsonb->>'role',
    'none'
  )
$func$;

create or replace function app.current_user_id()
returns uuid
language sql
stable
as $func$
  select coalesce(
    auth.uid(),
    nullif(current_setting('request.jwt.claims', true)::jsonb->>'sub', '')::uuid
  )
$func$;

create or replace function app.is_tenant_active()
returns boolean
language sql
stable
as $func$
  select not coalesce(
    (current_setting('request.jwt.claims', true)::jsonb->>'access_blocked')::boolean,
    false
  )
$func$;

comment on function app.current_tenant_id is 'Extract tenant_id from JWT claims for RLS policies';
comment on function app.current_role is 'Extract app role from JWT claims';
comment on function app.current_user_id is 'Get current authenticated user ID';
comment on function app.is_tenant_active is 'Check if current user belongs to active tenant';

-- 3) Auto-create Profile on First Login
-- ============================================================================
-- Trigger to create app.profiles row when new user signs up
-- In production, you'd likely do this via Edge Function for more control

create or replace function app.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public, app, auth
as $func$
declare
  default_tenant_id uuid;
  is_first_user boolean;
begin
  -- Check if this is the first user ever (make them owner of default tenant)
  select not exists (select 1 from app.profiles limit 1) into is_first_user;

  if is_first_user then
    -- First user becomes owner of bootstrap tenant
    select id into default_tenant_id from app.tenants order by created_at limit 1;

    insert into app.profiles (user_id, tenant_id, role, display_name)
    values (
      new.id,
      default_tenant_id,
      'owner',
      coalesce(new.raw_user_meta_data->>'display_name', split_part(new.email, '@', 1))
    );
  else
    -- Subsequent users need to be invited (profile created via invite flow)
    -- Do nothing here - profile will be created by invite endpoint
    null;
  end if;

  return new;
end;
$func$;

-- Only create profile for first user automatically
-- All other users must be invited via proper tenant invitation flow
create trigger on_auth_user_created
  after insert on auth.users
  for each row
  execute function app.handle_new_user();

comment on function app.handle_new_user is 'Auto-create profile for first user as tenant owner - all others require invitation';

-- 4) Verification Query
-- ============================================================================
-- Run this after login to verify JWT claims are working:
--
-- select
--   app.current_user_id() as user_id,
--   app.current_tenant_id() as tenant_id,
--   app.current_role() as role,
--   app.is_tenant_active() as tenant_active;
