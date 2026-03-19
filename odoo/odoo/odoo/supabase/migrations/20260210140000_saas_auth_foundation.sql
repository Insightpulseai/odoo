-- PHASE 1: SAAS AUTH FOUNDATION
-- Tables: profiles, organizations, organization_members, organization_invites
-- Auth trigger: auto-create org on signup

-- ============================================================================
-- PROFILES TABLE (1:1 with auth.users)
-- ============================================================================
create table if not exists public.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  email text,
  full_name text,
  avatar_url text,
  created_at timestamptz default now()
);

comment on table public.profiles is 'User profiles - extends Supabase Auth users';

-- ============================================================================
-- ORGANIZATIONS TABLE (tenant isolation)
-- ============================================================================
create table if not exists public.organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text unique not null,
  created_at timestamptz default now(),
  created_by uuid references auth.users(id)
);

comment on table public.organizations is 'Organizations - multi-tenant isolation';

-- ============================================================================
-- ORGANIZATION MEMBERS TABLE (M:N with roles)
-- ============================================================================
create table if not exists public.organization_members (
  org_id uuid references public.organizations(id) on delete cascade,
  user_id uuid references auth.users(id) on delete cascade,
  role text check (role in ('owner','admin','member','viewer')) not null,
  created_at timestamptz default now(),
  primary key (org_id, user_id)
);

comment on table public.organization_members is 'Org membership - supports owner/admin/member/viewer roles';

-- ============================================================================
-- ORGANIZATION INVITES TABLE (pending invitations)
-- ============================================================================
create table if not exists public.organization_invites (
  id uuid primary key default gen_random_uuid(),
  org_id uuid references public.organizations(id) on delete cascade,
  email text not null,
  role text check (role in ('admin','member','viewer')) not null,
  token text unique not null,
  expires_at timestamptz not null,
  created_at timestamptz default now()
);

comment on table public.organization_invites is 'Pending org invitations';

-- ============================================================================
-- AUTH BOOTSTRAP: AUTO-CREATE ORG ON SIGNUP
-- ============================================================================
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
as $$
declare
  new_org_id uuid;
  base_slug text;
  final_slug text;
begin
  -- Create profile
  insert into public.profiles (user_id, email)
  values (new.id, new.email)
  on conflict do nothing;

  -- Generate slug from email
  base_slug := lower(regexp_replace(coalesce(split_part(new.email,'@',1),'user'), '[^a-z0-9]+', '-', 'g'));
  final_slug := base_slug || '-' || substr(new.id::text, 1, 6);

  -- Create personal organization
  insert into public.organizations (name, slug, created_by)
  values (
    coalesce(new.email, 'Personal Workspace'),
    final_slug,
    new.id
  )
  returning id into new_org_id;

  -- Add user as owner
  insert into public.organization_members (org_id, user_id, role)
  values (new_org_id, new.id, 'owner');

  return new;
end;
$$;

-- ============================================================================
-- TRIGGER: ON AUTH USER CREATED
-- ============================================================================
drop trigger if exists on_auth_user_created on auth.users;

create trigger on_auth_user_created
after insert on auth.users
for each row
execute procedure public.handle_new_user();

comment on function public.handle_new_user is 'Auth trigger - creates profile + personal org on signup';
