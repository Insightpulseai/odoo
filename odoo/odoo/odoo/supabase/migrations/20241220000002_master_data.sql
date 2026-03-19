-- Pulser Master Control — Master Data Tables
-- Shared reference records that operational tables point to
--
-- Master data = slowly changing, reused across workflows
-- Operational data = transactional, event-driven

-- ============================================================================
-- Master Data Schema
-- ============================================================================
create schema if not exists master;

-- ============================================================================
-- Tenants (Multi-tenancy Root)
-- ============================================================================
create table if not exists master.tenants (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,              -- ACME, TBWA, etc.
  name text not null,
  settings jsonb not null default '{}'::jsonb,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

comment on table master.tenants is 'Root tenant registry for multi-tenancy';

-- ============================================================================
-- Roles / Lanes (RBAC Foundation)
-- ============================================================================
create table if not exists master.roles (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references master.tenants(id) on delete cascade,
  code text not null,                     -- DEV, HR, IT, FIN, MGR
  name text not null,
  description text,
  permissions jsonb not null default '[]'::jsonb,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

comment on table master.roles is 'Lane/role definitions for routing and access control';

create unique index if not exists ux_roles_tenant_code
  on master.roles (tenant_id, code);

-- ============================================================================
-- Users (Identity Registry)
-- ============================================================================
create table if not exists master.users (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references master.tenants(id) on delete cascade,

  -- Identity
  email text not null,
  name text not null,
  employee_code text,                     -- Links to Odoo x_employee_code

  -- External mappings
  odoo_user_id int,
  github_login text,
  slack_user_id text,

  -- Roles (many-to-many simplified as array)
  role_codes text[] not null default array[]::text[],

  -- Status
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

comment on table master.users is 'User identity registry with external system mappings';

create unique index if not exists ux_users_tenant_email
  on master.users (tenant_id, email);

create index if not exists ix_users_employee_code
  on master.users (tenant_id, employee_code) where employee_code is not null;

-- ============================================================================
-- Repositories (GitHub/Git Registry)
-- ============================================================================
create table if not exists master.repositories (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references master.tenants(id) on delete cascade,

  -- Identification
  owner text not null,                    -- GitHub org/user
  name text not null,                     -- Repo name
  full_name text generated always as (owner || '/' || name) stored,

  -- Configuration
  default_branch text not null default 'main',
  primary_lane text default 'DEV',
  auto_remediate boolean not null default true,

  -- Metadata
  github_id bigint,
  settings jsonb not null default '{}'::jsonb,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

comment on table master.repositories is 'GitHub repository registry for Pulser Bot';

create unique index if not exists ux_repos_full_name
  on master.repositories (tenant_id, owner, name);

-- ============================================================================
-- Environments (Deployment Targets)
-- ============================================================================
create table if not exists master.environments (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references master.tenants(id) on delete cascade,
  code text not null,                     -- dev, staging, prod
  name text not null,
  url text,
  settings jsonb not null default '{}'::jsonb,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

comment on table master.environments is 'Deployment environment registry';

create unique index if not exists ux_envs_tenant_code
  on master.environments (tenant_id, code);

-- ============================================================================
-- SLA Rules (Policy Configuration)
-- ============================================================================
create table if not exists master.sla_rules (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references master.tenants(id) on delete cascade,

  -- Matching criteria
  lane text,
  priority int,
  source text,                            -- github_pr, odoo_event, etc.

  -- SLA configuration
  response_minutes int,                   -- Time to first response
  resolution_minutes int not null,        -- Time to resolution
  warning_pct int default 75,             -- Warn at this % of SLA

  -- Metadata
  name text not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

comment on table master.sla_rules is 'SLA policy rules by lane/priority/source';

create index if not exists ix_sla_rules_match
  on master.sla_rules (tenant_id, lane, priority, source) where is_active = true;

-- ============================================================================
-- Checklist Templates
-- ============================================================================
create table if not exists master.checklist_templates (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references master.tenants(id) on delete cascade,
  code text not null,                     -- onboarding_hr, offboarding_it
  name text not null,
  lane text,
  items jsonb not null default '[]'::jsonb,  -- Array of {order, name, required, evidence_type}
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

comment on table master.checklist_templates is 'Reusable checklist templates for work items';

create unique index if not exists ux_checklists_tenant_code
  on master.checklist_templates (tenant_id, code);

-- ============================================================================
-- External System Mappings
-- ============================================================================
create table if not exists master.external_mappings (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references master.tenants(id) on delete cascade,

  -- Entity reference
  entity_type text not null,              -- user, employee, account, etc.
  internal_id text not null,

  -- External system
  system_code text not null,              -- odoo, github, slack, concur
  external_id text not null,

  -- Metadata
  meta jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

comment on table master.external_mappings is 'ID mappings between internal and external systems';

create unique index if not exists ux_mappings_internal
  on master.external_mappings (tenant_id, entity_type, internal_id, system_code);

create index if not exists ix_mappings_external
  on master.external_mappings (tenant_id, system_code, external_id);

-- ============================================================================
-- Process Template Library (Predefined Processes)
-- ============================================================================
-- Note: runtime.process_defs stores instances, this stores templates
create table if not exists master.process_templates (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references master.tenants(id) on delete cascade,
  code text not null,                     -- employee_onboarding, expense_approval
  name text not null,
  category text,                          -- hr, finance, it, operations
  description text,

  -- BPMN source
  bpmn_xml text,

  -- Extracted structure (for quick access)
  lanes jsonb not null default '[]'::jsonb,
  nodes jsonb not null default '[]'::jsonb,
  edges jsonb not null default '[]'::jsonb,

  -- Linked checklists per lane
  checklist_mappings jsonb not null default '{}'::jsonb,  -- {HR: "onboarding_hr", IT: "onboarding_it"}

  -- Status
  version text not null default '1.0.0',
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

comment on table master.process_templates is 'Master BPMN process templates (source of truth)';

create unique index if not exists ux_process_templates_code
  on master.process_templates (tenant_id, code, version);

-- ============================================================================
-- Triggers
-- ============================================================================
create or replace function master.touch_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_touch_tenants on master.tenants;
create trigger trg_touch_tenants
  before update on master.tenants
  for each row execute function master.touch_updated_at();

drop trigger if exists trg_touch_users on master.users;
create trigger trg_touch_users
  before update on master.users
  for each row execute function master.touch_updated_at();

drop trigger if exists trg_touch_checklists on master.checklist_templates;
create trigger trg_touch_checklists
  before update on master.checklist_templates
  for each row execute function master.touch_updated_at();

drop trigger if exists trg_touch_process_templates on master.process_templates;
create trigger trg_touch_process_templates
  before update on master.process_templates
  for each row execute function master.touch_updated_at();

-- ============================================================================
-- Seed Data: Default Tenant and Roles
-- ============================================================================
insert into master.tenants (id, code, name) values
  ('00000000-0000-0000-0000-000000000001', 'DEFAULT', 'Default Tenant')
on conflict (code) do nothing;

insert into master.roles (tenant_id, code, name, description) values
  ('00000000-0000-0000-0000-000000000001', 'DEV', 'Development', 'Software development and CI/CD'),
  ('00000000-0000-0000-0000-000000000001', 'HR', 'Human Resources', 'People operations and onboarding'),
  ('00000000-0000-0000-0000-000000000001', 'IT', 'Information Technology', 'Infrastructure and access provisioning'),
  ('00000000-0000-0000-0000-000000000001', 'FIN', 'Finance', 'Accounting and expense management'),
  ('00000000-0000-0000-0000-000000000001', 'MGR', 'Management', 'Approvals and oversight')
on conflict do nothing;

-- Default SLA rules
insert into master.sla_rules (tenant_id, name, priority, resolution_minutes) values
  ('00000000-0000-0000-0000-000000000001', 'P1 Critical', 1, 240),
  ('00000000-0000-0000-0000-000000000001', 'P2 High', 2, 480),
  ('00000000-0000-0000-0000-000000000001', 'P3 Medium', 3, 1440),
  ('00000000-0000-0000-0000-000000000001', 'P4 Low', 4, 4320)
on conflict do nothing;

-- Default checklist templates
insert into master.checklist_templates (tenant_id, code, name, lane, items) values
  ('00000000-0000-0000-0000-000000000001', 'onboarding_hr', 'HR Onboarding Checklist', 'HR', '[
    {"order": 1, "name": "Create employee record", "required": true},
    {"order": 2, "name": "Collect ID documents", "required": true, "evidence_type": "doc"},
    {"order": 3, "name": "Setup payroll", "required": true},
    {"order": 4, "name": "Enroll in benefits", "required": false}
  ]'::jsonb),
  ('00000000-0000-0000-0000-000000000001', 'onboarding_it', 'IT Onboarding Checklist', 'IT', '[
    {"order": 1, "name": "Create email account", "required": true},
    {"order": 2, "name": "Provision laptop", "required": true},
    {"order": 3, "name": "Grant system access", "required": true},
    {"order": 4, "name": "Setup VPN", "required": false}
  ]'::jsonb),
  ('00000000-0000-0000-0000-000000000001', 'offboarding_it', 'IT Offboarding Checklist', 'IT', '[
    {"order": 1, "name": "Disable email account", "required": true},
    {"order": 2, "name": "Revoke system access", "required": true},
    {"order": 3, "name": "Collect equipment", "required": true, "evidence_type": "doc"},
    {"order": 4, "name": "Backup user data", "required": true}
  ]'::jsonb)
on conflict do nothing;
