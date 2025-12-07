-- 202512071100_1000_CORE_SCHEMAS_AND_TENANCY.sql
-- Family: 1000 - Core platform & tenancy
-- Purpose:
--   * Define core/saas/logs/scout* schemas.
--   * Establish canonical multi-tenant skeleton (company, tenant, app_user, roles).
-- Safety:
--   * Additive and idempotent.
--   * Safe to run multiple times.

BEGIN;

-- Ensure extension used for UUID generation exists (idempotent)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Core platform schemas -------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS saas;
CREATE SCHEMA IF NOT EXISTS logs;

-- Scout / Retail Intelligence schemas (logical home for sari/sari-coach/Scout)
CREATE SCHEMA IF NOT EXISTS scout_dim;
CREATE SCHEMA IF NOT EXISTS scout_fact;
CREATE SCHEMA IF NOT EXISTS scout_gold;
CREATE SCHEMA IF NOT EXISTS scout_meta;

-- core.company
-- Canonical legal entity / company table.
CREATE TABLE IF NOT EXISTS core.company (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  legal_name text,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE core.company IS 'Canonical company record (legal entity).';

CREATE INDEX IF NOT EXISTS idx_core_company_name ON core.company (lower(name));

-- core.tenant
-- One row per workspace / tenant. Linked to company. Tenant_id used in RLS templates.
CREATE TABLE IF NOT EXISTS core.tenant (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id uuid REFERENCES core.company(id) ON DELETE SET NULL,
  slug text UNIQUE,
  name text NOT NULL,
  plan text,
  region text,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE core.tenant IS 'Workspace / tenant - top level tenant_id used for RLS (JWT claim).';

CREATE INDEX IF NOT EXISTS idx_core_tenant_company ON core.tenant (company_id);
CREATE INDEX IF NOT EXISTS idx_core_tenant_slug ON core.tenant (lower(slug));

-- core.role
-- Simple RBAC role registry used for tenancy membership mapping.
CREATE TABLE IF NOT EXISTS core.role (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code text NOT NULL UNIQUE,
  name text NOT NULL,
  description text,
  created_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE core.role IS 'Global RBAC roles (finance_admin, scout_viewer, etc).';

-- core.app_user
-- Mapping between auth.users and internal app user records
CREATE TABLE IF NOT EXISTS core.app_user (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_user_id uuid,
  email text,
  display_name text,
  phone text,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE core.app_user IS 'Maps auth.users to app-level user entry. auth_user_id references auth.users.id.';

CREATE UNIQUE INDEX IF NOT EXISTS ux_core_app_user_auth_user_id ON core.app_user (auth_user_id);
CREATE INDEX IF NOT EXISTS idx_core_app_user_email ON core.app_user (lower(email));

-- core.tenant_membership
-- Associates app_user → tenant with a role (role_id)
CREATE TABLE IF NOT EXISTS core.tenant_membership (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL REFERENCES core.tenant(id) ON DELETE CASCADE,
  app_user_id uuid NOT NULL REFERENCES core.app_user(id) ON DELETE CASCADE,
  role_id uuid REFERENCES core.role(id) ON DELETE SET NULL,
  is_owner boolean DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE core.tenant_membership IS 'User memberships per tenant with role.';

CREATE UNIQUE INDEX IF NOT EXISTS ux_core_tenant_membership_tenant_user ON core.tenant_membership (tenant_id, app_user_id);

-- core.feature_flag + core.feature_rollout
-- Lightweight feature flagging table(s) for tenant-level toggles
CREATE TABLE IF NOT EXISTS core.feature_flag (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  key text NOT NULL UNIQUE,
  description text,
  default_enabled boolean DEFAULT false,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE core.feature_flag IS 'Feature flags catalog.';

CREATE TABLE IF NOT EXISTS core.feature_rollout (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  feature_id uuid NOT NULL REFERENCES core.feature_flag(id) ON DELETE CASCADE,
  tenant_id uuid NOT NULL REFERENCES core.tenant(id) ON DELETE CASCADE,
  enabled boolean NOT NULL DEFAULT false,
  rollout_config jsonb DEFAULT '{}'::jsonb,
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (feature_id, tenant_id)
);
COMMENT ON TABLE core.feature_rollout IS 'Per-tenant feature overrides.';

-- core.audit_log (lightweight event log for tenant-level admin activity)
CREATE TABLE IF NOT EXISTS core.audit_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid REFERENCES core.tenant(id) ON DELETE SET NULL,
  actor_app_user_id uuid REFERENCES core.app_user(id) ON DELETE SET NULL,
  action text NOT NULL,
  payload jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
COMMENT ON TABLE core.audit_log IS 'General audit log for tenant-scoped admin actions.';

CREATE INDEX IF NOT EXISTS idx_core_audit_log_tenant ON core.audit_log (tenant_id);
CREATE INDEX IF NOT EXISTS idx_core_audit_log_actor ON core.audit_log (actor_app_user_id);

-- helper: update updated_at on row modification (trigger function)
CREATE OR REPLACE FUNCTION core.set_updated_at()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

-- Attach trigger to core tables (idempotent creation)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'set_updated_at_company'
  ) THEN
    CREATE TRIGGER set_updated_at_company
      BEFORE UPDATE ON core.company
      FOR EACH ROW EXECUTE FUNCTION core.set_updated_at();
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'set_updated_at_tenant'
  ) THEN
    CREATE TRIGGER set_updated_at_tenant
      BEFORE UPDATE ON core.tenant
      FOR EACH ROW EXECUTE FUNCTION core.set_updated_at();
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM pg_trigger WHERE tgname = 'set_updated_at_app_user'
  ) THEN
    CREATE TRIGGER set_updated_at_app_user
      BEFORE UPDATE ON core.app_user
      FOR EACH ROW EXECUTE FUNCTION core.set_updated_at();
  END IF;
END;
$$;

COMMIT;
