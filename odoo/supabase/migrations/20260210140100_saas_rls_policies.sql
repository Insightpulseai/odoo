-- PHASE 1: RLS POLICIES
-- Multi-tenant security with org-scoped access

-- ============================================================================
-- RLS HELPER FUNCTION
-- ============================================================================
create or replace function public.is_org_member(org uuid)
returns boolean
language sql
stable
security definer
as $$
  select exists (
    select 1
    from public.organization_members m
    where m.org_id = org
      and m.user_id = auth.uid()
  );
$$;

comment on function public.is_org_member is 'RLS helper - checks if current user is member of org';

-- ============================================================================
-- ENABLE RLS ON ALL TABLES
-- ============================================================================
alter table public.profiles enable row level security;
alter table public.organizations enable row level security;
alter table public.organization_members enable row level security;
alter table public.organization_invites enable row level security;

-- ============================================================================
-- PROFILES POLICIES
-- ============================================================================
drop policy if exists "users_read_own_profile" on public.profiles;
create policy "users_read_own_profile"
on public.profiles for select
using (auth.uid() = user_id);

drop policy if exists "users_update_own_profile" on public.profiles;
create policy "users_update_own_profile"
on public.profiles for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

-- ============================================================================
-- ORGANIZATIONS POLICIES
-- ============================================================================
drop policy if exists "org_members_read_org" on public.organizations;
create policy "org_members_read_org"
on public.organizations for select
using (
  exists (
    select 1 from public.organization_members
    where org_id = organizations.id
      and user_id = auth.uid()
  )
);

drop policy if exists "org_owners_update_org" on public.organizations;
create policy "org_owners_update_org"
on public.organizations for update
using (
  exists (
    select 1 from public.organization_members
    where org_id = organizations.id
      and user_id = auth.uid()
      and role in ('owner', 'admin')
  )
);

-- ============================================================================
-- ORGANIZATION MEMBERS POLICIES
-- ============================================================================
drop policy if exists "org_members_read_members" on public.organization_members;
create policy "org_members_read_members"
on public.organization_members for select
using (
  exists (
    select 1 from public.organization_members m
    where m.org_id = organization_members.org_id
      and m.user_id = auth.uid()
  )
);

drop policy if exists "org_admins_manage_members" on public.organization_members;
create policy "org_admins_manage_members"
on public.organization_members for all
using (
  exists (
    select 1 from public.organization_members m
    where m.org_id = organization_members.org_id
      and m.user_id = auth.uid()
      and m.role in ('owner', 'admin')
  )
);

-- ============================================================================
-- ORGANIZATION INVITES POLICIES
-- ============================================================================
drop policy if exists "org_admins_manage_invites" on public.organization_invites;
create policy "org_admins_manage_invites"
on public.organization_invites for all
using (
  exists (
    select 1 from public.organization_members m
    where m.org_id = organization_invites.org_id
      and m.user_id = auth.uid()
      and m.role in ('owner', 'admin')
  )
);

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================
grant usage on schema public to anon, authenticated;
grant select on public.profiles to authenticated;
grant update on public.profiles to authenticated;
grant select on public.organizations to authenticated;
grant update on public.organizations to authenticated;
grant select, insert, update, delete on public.organization_members to authenticated;
grant select, insert, update, delete on public.organization_invites to authenticated;
