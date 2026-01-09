-- ============================================================================
-- Auth Foundation: Tenant-scoped Identity System
-- ============================================================================
-- Purpose: Establish Supabase Auth as single identity provider with proper
--          tenant isolation, role-based access, and service authentication
--
-- Architecture:
--   - auth schema: Supabase-managed identity (auth.users)
--   - app schema: Business user profiles mapped to auth.users
--   - ops schema: Service tokens and operational metadata
--
-- Tenancy Model: Every user belongs to exactly one tenant
-- Authorization: JWT claims (tenant_id, role) + RLS policies
-- ============================================================================

-- 1) Create application schemas
-- ============================================================================
create schema if not exists app;
create schema if not exists ops;

comment on schema app is 'Application business logic and user data';
comment on schema ops is 'Operational metadata, service tokens, and system management';

-- 2) Tenants: Root entity for multi-tenancy
-- ============================================================================
create table if not exists app.tenants (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  settings jsonb not null default '{}'::jsonb,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint tenants_slug_format check (slug ~ '^[a-z0-9-]+$'),
  constraint tenants_slug_length check (length(slug) between 3 and 63)
);

create index if not exists tenants_slug_idx on app.tenants(slug) where is_active;
create index if not exists tenants_created_at_idx on app.tenants(created_at desc);

comment on table app.tenants is 'Root entity for tenant isolation - every business object belongs to a tenant';
comment on column app.tenants.slug is 'URL-safe unique identifier (e.g. "acme-corp")';
comment on column app.tenants.settings is 'Tenant-specific configuration (features, limits, branding)';

-- 3) User Profiles: Maps auth.users to app context
-- ============================================================================
create table if not exists app.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  tenant_id uuid not null references app.tenants(id) on delete restrict,
  role text not null check (role in ('owner','admin','finance','ops','viewer')),
  display_name text,
  avatar_url text,
  metadata jsonb not null default '{}'::jsonb,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint profiles_role_default check (role in ('owner','admin','finance','ops','viewer'))
);

create index if not exists profiles_tenant_id_idx on app.profiles(tenant_id) where is_active;
create index if not exists profiles_role_idx on app.profiles(role);
create unique index if not exists profiles_tenant_owner_idx on app.profiles(tenant_id)
  where role = 'owner' and is_active;

comment on table app.profiles is 'User profiles mapped to auth.users with tenant context and app role';
comment on column app.profiles.role is 'Application role: owner (full control), admin (manage users/settings), finance (financial ops), ops (operational tasks), viewer (read-only)';
comment on column app.profiles.metadata is 'User preferences, notifications, UI state';

-- 4) Service Tokens: Rotatable API keys for service-to-service auth
-- ============================================================================
create table if not exists ops.service_tokens (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  token_hash text not null unique,
  tenant_id uuid references app.tenants(id) on delete cascade,
  scopes text[] not null default '{}',
  last_used_at timestamptz,
  is_active boolean not null default true,
  expires_at timestamptz,
  created_by uuid references auth.users(id),
  created_at timestamptz not null default now(),

  constraint service_tokens_scopes_valid check (
    scopes <@ array['read:receipts', 'write:receipts', 'read:reports', 'write:reports', 'admin:all']
  )
);

create index if not exists service_tokens_tenant_id_idx on ops.service_tokens(tenant_id) where is_active;
create index if not exists service_tokens_token_hash_idx on ops.service_tokens(token_hash) where is_active;

comment on table ops.service_tokens is 'Rotatable API keys for service authentication (OCR, n8n, external integrations)';
comment on column ops.service_tokens.token_hash is 'bcrypt hash of token - never store plaintext';
comment on column ops.service_tokens.scopes is 'Permitted operations: read:receipts, write:receipts, read:reports, write:reports, admin:all';

-- 5) Audit Log: Track security-relevant events
-- ============================================================================
create table if not exists ops.audit_log (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid references app.tenants(id) on delete cascade,
  user_id uuid references auth.users(id) on delete set null,
  action text not null,
  resource_type text not null,
  resource_id text,
  metadata jsonb not null default '{}'::jsonb,
  ip_address inet,
  user_agent text,
  created_at timestamptz not null default now()
);

create index if not exists audit_log_tenant_created_idx on ops.audit_log(tenant_id, created_at desc);
create index if not exists audit_log_user_created_idx on ops.audit_log(user_id, created_at desc);
create index if not exists audit_log_action_idx on ops.audit_log(action);

comment on table ops.audit_log is 'Security audit trail for sensitive operations (login, role changes, data exports)';

-- 6) Updated_at Triggers
-- ============================================================================
create or replace function app.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger tenants_updated_at before update on app.tenants
  for each row execute function app.set_updated_at();

create trigger profiles_updated_at before update on app.profiles
  for each row execute function app.set_updated_at();

-- 7) Seed Data: Bootstrap tenant for development
-- ============================================================================
-- This should be replaced with proper tenant provisioning in production

insert into app.tenants (id, slug, name, settings)
values (
  '00000000-0000-0000-0000-000000000001',
  'insightpulse',
  'InsightPulse AI',
  jsonb_build_object(
    'features', array['ocr', 'bir_compliance', 'expense_automation'],
    'limits', jsonb_build_object('users', 50, 'storage_gb', 100)
  )
)
on conflict (id) do nothing;

comment on table app.tenants is 'Bootstrap tenant created for development - use tenant provisioning API in production';
