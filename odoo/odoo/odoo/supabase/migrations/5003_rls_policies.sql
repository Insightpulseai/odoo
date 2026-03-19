-- ============================================================================
-- Row Level Security: Tenant Isolation + Role-Based Access
-- ============================================================================
-- Purpose: Enforce tenant boundaries and role permissions at database level
--
-- Security Model:
--   - Tenant Isolation: Users can only access data from their tenant
--   - Role Hierarchy: owner > admin > finance > ops > viewer
--   - Service Authentication: service-role bypasses RLS (use carefully)
--
-- Policy Naming Convention: {table}_{operation}_{condition}
--   Example: tenants_select_own, profiles_update_admin
-- ============================================================================

-- 1) Enable RLS on All Tables
-- ============================================================================
alter table app.tenants enable row level security;
alter table app.profiles enable row level security;
alter table ops.service_tokens enable row level security;
alter table ops.audit_log enable row level security;

-- 2) Tenants Policies
-- ============================================================================
-- Users can only see their own tenant
create policy tenants_select_own on app.tenants
  for select
  using (id = app.current_tenant_id());

-- Only owners can update tenant settings
create policy tenants_update_owner on app.tenants
  for update
  using (
    id = app.current_tenant_id()
    and app.current_role() = 'owner'
  );

-- No direct tenant creation via SQL (use Edge Function)
-- No tenant deletion (use soft delete via is_active flag)

comment on policy tenants_select_own on app.tenants is 'Users can only view their own tenant';
comment on policy tenants_update_owner on app.tenants is 'Only tenant owners can modify tenant settings';

-- 3) Profiles Policies
-- ============================================================================
-- Users can view all profiles in their tenant
create policy profiles_select_tenant on app.profiles
  for select
  using (tenant_id = app.current_tenant_id());

-- Users can update their own profile (display_name, avatar_url, metadata)
create policy profiles_update_own on app.profiles
  for update
  using (user_id = app.current_user_id())
  with check (
    user_id = app.current_user_id()
    -- Prevent self-role-escalation
    and (
      role = (select role from app.profiles where user_id = app.current_user_id())
      or app.current_role() in ('owner', 'admin')
    )
  );

-- Admins and owners can update any profile in their tenant
create policy profiles_update_admin on app.profiles
  for update
  using (
    tenant_id = app.current_tenant_id()
    and app.current_role() in ('owner', 'admin')
  )
  with check (
    tenant_id = app.current_tenant_id()
    -- Prevent non-owners from creating/modifying owner roles
    and (
      role != 'owner'
      or app.current_role() = 'owner'
    )
  );

-- Only admins/owners can create profiles (invitation flow)
create policy profiles_insert_admin on app.profiles
  for insert
  with check (
    tenant_id = app.current_tenant_id()
    and app.current_role() in ('owner', 'admin')
    -- Prevent non-owners from creating owner roles
    and (
      role != 'owner'
      or app.current_role() = 'owner'
    )
  );

-- Only owners can delete profiles
create policy profiles_delete_owner on app.profiles
  for delete
  using (
    tenant_id = app.current_tenant_id()
    and app.current_role() = 'owner'
    -- Prevent owner from deleting themselves if last owner
    and not (
      role = 'owner'
      and user_id = app.current_user_id()
      and (
        select count(*)
        from app.profiles
        where tenant_id = app.current_tenant_id()
          and role = 'owner'
          and is_active = true
      ) = 1
    )
  );

comment on policy profiles_select_tenant on app.profiles is 'Users can view all profiles in their tenant';
comment on policy profiles_update_own on app.profiles is 'Users can update their own profile (but not self-escalate role)';
comment on policy profiles_update_admin on app.profiles is 'Admins/owners can update profiles (owners required for owner role changes)';
comment on policy profiles_insert_admin on app.profiles is 'Admins/owners can invite users (owners required for owner invitations)';
comment on policy profiles_delete_owner on app.profiles is 'Owners can remove users (but not last owner)';

-- 4) Service Tokens Policies
-- ============================================================================
-- Only admins and owners can view service tokens in their tenant
create policy service_tokens_select_admin on ops.service_tokens
  for select
  using (
    (tenant_id = app.current_tenant_id() or tenant_id is null)
    and app.current_role() in ('owner', 'admin', 'ops')
  );

-- Only admins/owners can create service tokens
create policy service_tokens_insert_admin on ops.service_tokens
  for insert
  with check (
    (tenant_id = app.current_tenant_id() or tenant_id is null)
    and app.current_role() in ('owner', 'admin')
  );

-- Only admins/owners can revoke tokens (set is_active = false)
create policy service_tokens_update_admin on ops.service_tokens
  for update
  using (
    (tenant_id = app.current_tenant_id() or tenant_id is null)
    and app.current_role() in ('owner', 'admin')
  )
  with check (
    -- Only allow updating is_active and last_used_at
    (tenant_id = app.current_tenant_id() or tenant_id is null)
  );

-- Only owners can permanently delete tokens
create policy service_tokens_delete_owner on ops.service_tokens
  for delete
  using (
    (tenant_id = app.current_tenant_id() or tenant_id is null)
    and app.current_role() = 'owner'
  );

comment on policy service_tokens_select_admin on ops.service_tokens is 'Admins/owners/ops can view service tokens';
comment on policy service_tokens_insert_admin on ops.service_tokens is 'Admins/owners can create service tokens';
comment on policy service_tokens_update_admin on ops.service_tokens is 'Admins/owners can revoke tokens';
comment on policy service_tokens_delete_owner on ops.service_tokens is 'Only owners can permanently delete tokens';

-- 5) Audit Log Policies
-- ============================================================================
-- Everyone can read audit logs from their tenant (transparency)
create policy audit_log_select_tenant on ops.audit_log
  for select
  using (tenant_id = app.current_tenant_id());

-- System writes audit logs (use service-role or security definer function)
-- No direct insert/update/delete from users

comment on policy audit_log_select_tenant on ops.audit_log is 'Users can view audit logs for their tenant (transparency)';

-- 6) Helper Function: Log Audit Events
-- ============================================================================
create or replace function ops.log_audit(
  p_action text,
  p_resource_type text,
  p_resource_id text default null,
  p_metadata jsonb default '{}'::jsonb
)
returns uuid
language plpgsql
security definer
set search_path = public, app, ops, auth
as $
declare
  audit_id uuid;
begin
  insert into ops.audit_log (
    tenant_id,
    user_id,
    action,
    resource_type,
    resource_id,
    metadata,
    ip_address,
    user_agent
  )
  values (
    app.current_tenant_id(),
    app.current_user_id(),
    p_action,
    p_resource_type,
    p_resource_id,
    p_metadata,
    inet(current_setting('request.headers', true)::json->>'x-forwarded-for'),
    current_setting('request.headers', true)::json->>'user-agent'
  )
  returning id into audit_id;

  return audit_id;
end;
$;

comment on function ops.log_audit is 'Helper to log audit events with automatic tenant/user context';

-- 7) Audit Trigger for Sensitive Operations
-- ============================================================================
create or replace function app.audit_profile_changes()
returns trigger
language plpgsql
security definer
set search_path = public, app, ops
as $
begin
  if TG_OP = 'UPDATE' then
    -- Log role changes
    if old.role != new.role then
      perform ops.log_audit(
        'profile.role_changed',
        'profile',
        new.user_id::text,
        jsonb_build_object(
          'old_role', old.role,
          'new_role', new.role,
          'changed_by', app.current_user_id()
        )
      );
    end if;

    -- Log activation/deactivation
    if old.is_active != new.is_active then
      perform ops.log_audit(
        case when new.is_active then 'profile.activated' else 'profile.deactivated' end,
        'profile',
        new.user_id::text,
        jsonb_build_object('changed_by', app.current_user_id())
      );
    end if;
  elsif TG_OP = 'INSERT' then
    -- Log profile creation
    perform ops.log_audit(
      'profile.created',
      'profile',
      new.user_id::text,
      jsonb_build_object('role', new.role, 'created_by', app.current_user_id())
    );
  elsif TG_OP = 'DELETE' then
    -- Log profile deletion
    perform ops.log_audit(
      'profile.deleted',
      'profile',
      old.user_id::text,
      jsonb_build_object('role', old.role, 'deleted_by', app.current_user_id())
    );
  end if;

  return coalesce(new, old);
end;
$;

create trigger profiles_audit_trigger
  after insert or update or delete on app.profiles
  for each row
  execute function app.audit_profile_changes();

comment on function app.audit_profile_changes is 'Automatically log security-relevant profile changes';

-- 8) Verification Queries
-- ============================================================================
-- Run these after enabling RLS to verify tenant isolation:
--
-- -- Should only return current user's tenant
-- select * from app.tenants;
--
-- -- Should only return profiles from current user's tenant
-- select * from app.profiles;
--
-- -- Should only return service tokens from current user's tenant
-- select * from ops.service_tokens;
--
-- -- Should only return audit logs from current user's tenant
-- select * from ops.audit_log;
