-- Migration: Multi-Tenant Provider Model
-- Version: 202601120001
-- Description: Create multi-tenant provider schema with accounts, services, subscriptions
-- Author: Claude Code
-- Date: 2026-01-12
--
-- This migration creates the "ideal" multi-tenant model where:
-- - Tenant = organization using the platform
-- - Provider = organization offering services/agents to other tenants
-- - Same org can be BOTH tenant and provider

-- ============================================================================
-- PHASE 1: CREATE SCHEMA
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS saas;

COMMENT ON SCHEMA saas IS 'Multi-tenant SaaS model: accounts, services, subscriptions';

-- ============================================================================
-- PHASE 2: CREATE ENUM TYPES
-- ============================================================================

DO $$ BEGIN
    CREATE TYPE saas.account_role_type AS ENUM ('TENANT', 'PROVIDER', 'INTERNAL');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE saas.subscription_status AS ENUM ('DRAFT', 'ACTIVE', 'SUSPENDED', 'CANCELLED');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE saas.environment_type AS ENUM ('DEV', 'STAGING', 'PROD');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE saas.account_link_type AS ENUM ('PROVIDER_OF', 'RESELLER_OF', 'PARTNER_OF');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- ============================================================================
-- PHASE 3: CORE TABLES - ACCOUNTS & USERS
-- ============================================================================

-- Accounts table (organizations - can be tenant, provider, or both)
CREATE TABLE IF NOT EXISTS saas.accounts (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug                TEXT NOT NULL,
    name                TEXT NOT NULL,
    legal_name          TEXT,
    country             TEXT,
    timezone            TEXT,
    is_active           BOOLEAN NOT NULL DEFAULT true,

    -- Multi-tenancy hints
    default_locale      TEXT,
    billing_email       TEXT,

    -- Odoo mapping
    odoo_company_id     INTEGER,
    odoo_partner_id     INTEGER,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_slug
    ON saas.accounts(slug) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_accounts_odoo_company
    ON saas.accounts(odoo_company_id) WHERE odoo_company_id IS NOT NULL;

COMMENT ON TABLE saas.accounts IS
    'Organizations that can be tenants, providers, or both. Maps to Odoo res.company/res.partner.';
COMMENT ON COLUMN saas.accounts.slug IS 'Human-readable unique identifier (e.g., tbwa-ph)';
COMMENT ON COLUMN saas.accounts.odoo_company_id IS 'res.company.id mapping for Odoo integration';

-- Account roles (allows same account to be TENANT + PROVIDER)
CREATE TABLE IF NOT EXISTS saas.account_roles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          UUID NOT NULL REFERENCES saas.accounts(id) ON DELETE CASCADE,
    role                saas.account_role_type NOT NULL,
    is_primary          BOOLEAN NOT NULL DEFAULT false,
    granted_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    granted_by          UUID,

    CONSTRAINT uq_account_role UNIQUE (account_id, role)
);

CREATE INDEX IF NOT EXISTS idx_account_roles_account ON saas.account_roles(account_id);

COMMENT ON TABLE saas.account_roles IS
    'Accounts can have multiple roles (TENANT + PROVIDER simultaneously).';

-- Users table
CREATE TABLE IF NOT EXISTS saas.users (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          UUID NOT NULL REFERENCES saas.accounts(id) ON DELETE CASCADE,
    email               TEXT NOT NULL,
    full_name           TEXT,
    is_admin            BOOLEAN NOT NULL DEFAULT false,
    is_active           BOOLEAN NOT NULL DEFAULT true,

    -- External IDs for SSO/sync
    auth_user_id        UUID,
    odoo_user_id        INTEGER,
    keycloak_id         UUID,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at          TIMESTAMPTZ,

    CONSTRAINT uq_users_email UNIQUE (email)
);

CREATE INDEX IF NOT EXISTS idx_users_account ON saas.users(account_id);
CREATE INDEX IF NOT EXISTS idx_users_auth ON saas.users(auth_user_id) WHERE auth_user_id IS NOT NULL;

COMMENT ON TABLE saas.users IS
    'Users belong to one primary account. Maps to Odoo res.users and Supabase auth.users.';

-- ============================================================================
-- PHASE 4: PROVIDER TABLES - SERVICES & PLANS
-- ============================================================================

-- Services offered by providers
CREATE TABLE IF NOT EXISTS saas.services (
    id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_account_id       UUID NOT NULL REFERENCES saas.accounts(id),
    key                       TEXT NOT NULL,
    name                      TEXT NOT NULL,
    description               TEXT,

    -- Visibility
    is_public                 BOOLEAN NOT NULL DEFAULT false,
    is_enabled                BOOLEAN NOT NULL DEFAULT true,

    -- Classification
    category                  TEXT,
    default_environment_type  saas.environment_type,

    -- Technical hints
    mcp_server_name           TEXT,
    n8n_workflow_id           TEXT,

    created_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at                TIMESTAMPTZ,

    CONSTRAINT uq_services_key UNIQUE (key)
);

CREATE INDEX IF NOT EXISTS idx_services_provider ON saas.services(provider_account_id);
CREATE INDEX IF NOT EXISTS idx_services_category ON saas.services(category) WHERE category IS NOT NULL;

COMMENT ON TABLE saas.services IS
    'Services offered by providers. E.g., Scout Dashboard, Ask Copilot, BIR Compliance Engine.';
COMMENT ON COLUMN saas.services.key IS 'Unique service key (e.g., scout-dashboard, ask-copilot)';
COMMENT ON COLUMN saas.services.mcp_server_name IS 'MCP server name if service is MCP-based';

-- Service plans (pricing tiers)
CREATE TABLE IF NOT EXISTS saas.service_plans (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id          UUID NOT NULL REFERENCES saas.services(id) ON DELETE CASCADE,
    key                 TEXT NOT NULL,
    name                TEXT NOT NULL,
    description         TEXT,

    -- Pricing
    monthly_price_cents INTEGER,
    annual_price_cents  INTEGER,
    currency            TEXT DEFAULT 'USD',

    -- Limits
    max_seats           INTEGER,
    max_requests_month  INTEGER,
    feature_flags       JSONB DEFAULT '{}',

    is_active           BOOLEAN NOT NULL DEFAULT true,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_service_plan_key UNIQUE (service_id, key)
);

CREATE INDEX IF NOT EXISTS idx_service_plans_service ON saas.service_plans(service_id);

COMMENT ON TABLE saas.service_plans IS
    'Pricing plans for services. Multiple tiers per service (free, pro, enterprise).';

-- ============================================================================
-- PHASE 5: TENANT TABLES - SUBSCRIPTIONS & RELATIONSHIPS
-- ============================================================================

-- Subscriptions (tenant subscribing to provider service)
CREATE TABLE IF NOT EXISTS saas.subscriptions (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_account_id     UUID NOT NULL REFERENCES saas.accounts(id),
    provider_account_id   UUID NOT NULL REFERENCES saas.accounts(id),
    service_id            UUID NOT NULL REFERENCES saas.services(id),
    service_plan_id       UUID REFERENCES saas.service_plans(id),

    status                saas.subscription_status NOT NULL DEFAULT 'DRAFT',

    -- Lifecycle
    started_at            TIMESTAMPTZ,
    ended_at              TIMESTAMPTZ,
    trial_ends_at         TIMESTAMPTZ,
    next_billing_at       TIMESTAMPTZ,

    -- Billing reference
    external_ref          TEXT,
    billing_metadata      JSONB DEFAULT '{}',

    created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
    cancelled_at          TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant ON saas.subscriptions(tenant_account_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_provider ON saas.subscriptions(provider_account_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_tenant_service
    ON saas.subscriptions(tenant_account_id, service_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON saas.subscriptions(status);

COMMENT ON TABLE saas.subscriptions IS
    'Links tenants to provider services. The core billing relationship.';
COMMENT ON COLUMN saas.subscriptions.external_ref IS 'Stripe/Invoice ID for external billing';

-- Account links (explicit relationships between accounts)
CREATE TABLE IF NOT EXISTS saas.account_links (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_account_id     UUID NOT NULL REFERENCES saas.accounts(id),
    to_account_id       UUID NOT NULL REFERENCES saas.accounts(id),
    link_type           saas.account_link_type NOT NULL,

    metadata            JSONB DEFAULT '{}',
    is_active           BOOLEAN NOT NULL DEFAULT true,

    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_account_link UNIQUE (from_account_id, to_account_id, link_type),
    CONSTRAINT ck_no_self_link CHECK (from_account_id != to_account_id)
);

CREATE INDEX IF NOT EXISTS idx_account_links_from ON saas.account_links(from_account_id);
CREATE INDEX IF NOT EXISTS idx_account_links_to ON saas.account_links(to_account_id);

COMMENT ON TABLE saas.account_links IS
    'Explicit relationships between accounts. PROVIDER_OF = from is provider for to.';

-- ============================================================================
-- PHASE 6: ENVIRONMENTS (INFRASTRUCTURE BINDINGS)
-- ============================================================================

CREATE TABLE IF NOT EXISTS saas.environments (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id             UUID NOT NULL REFERENCES saas.accounts(id) ON DELETE CASCADE,
    env_type               saas.environment_type NOT NULL,

    -- Supabase binding
    supabase_project_ref   TEXT,
    supabase_service_role  TEXT,

    -- Vercel binding
    vercel_project_id      TEXT,
    vercel_team_id         TEXT,

    -- DigitalOcean binding
    digitalocean_app_id    TEXT,
    digitalocean_cluster   TEXT,

    -- Odoo binding
    odoo_db_name           TEXT,
    odoo_base_url          TEXT,

    -- Superset binding
    superset_database_key  TEXT,
    superset_dashboard_ids TEXT[],

    is_active              BOOLEAN NOT NULL DEFAULT true,
    created_at             TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at             TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_account_env UNIQUE (account_id, env_type)
);

CREATE INDEX IF NOT EXISTS idx_environments_supabase
    ON saas.environments(supabase_project_ref) WHERE supabase_project_ref IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_environments_odoo
    ON saas.environments(odoo_db_name) WHERE odoo_db_name IS NOT NULL;

COMMENT ON TABLE saas.environments IS
    'Maps accounts to infrastructure. Each account can have dev/staging/prod environments.';

-- ============================================================================
-- PHASE 7: USAGE TRACKING (FOR BILLING & LIMITS)
-- ============================================================================

CREATE TABLE IF NOT EXISTS saas.usage_records (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subscription_id      UUID NOT NULL REFERENCES saas.subscriptions(id),
    tenant_account_id    UUID NOT NULL REFERENCES saas.accounts(id),
    service_id           UUID NOT NULL REFERENCES saas.services(id),

    period_start         DATE NOT NULL,
    period_end           DATE NOT NULL,

    -- Metrics
    request_count        INTEGER NOT NULL DEFAULT 0,
    token_count          INTEGER NOT NULL DEFAULT 0,
    storage_bytes        BIGINT NOT NULL DEFAULT 0,
    compute_seconds      INTEGER NOT NULL DEFAULT 0,

    -- Status
    is_billed            BOOLEAN NOT NULL DEFAULT false,
    billed_at            TIMESTAMPTZ,

    created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_usage_period UNIQUE (subscription_id, period_start)
);

CREATE INDEX IF NOT EXISTS idx_usage_records_tenant ON saas.usage_records(tenant_account_id);
CREATE INDEX IF NOT EXISTS idx_usage_records_billing
    ON saas.usage_records(period_start, is_billed);

COMMENT ON TABLE saas.usage_records IS
    'Tracks service usage for billing and limit enforcement.';

-- ============================================================================
-- PHASE 8: AUDIT LOG FOR ACCOUNT CHANGES
-- ============================================================================

-- Ensure logs schema exists
CREATE SCHEMA IF NOT EXISTS logs;

CREATE TABLE IF NOT EXISTS logs.account_audit (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id           UUID NOT NULL REFERENCES saas.accounts(id),
    actor_user_id        UUID REFERENCES saas.users(id),
    action               TEXT NOT NULL,
    entity_type          TEXT NOT NULL,
    entity_id            UUID NOT NULL,
    changes              JSONB,
    ip_address           INET,
    user_agent           TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_account_audit_account ON logs.account_audit(account_id);
CREATE INDEX IF NOT EXISTS idx_account_audit_entity ON logs.account_audit(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_account_audit_created ON logs.account_audit(created_at);

COMMENT ON TABLE logs.account_audit IS
    'Audit trail for all account-related changes. Required for compliance.';

-- ============================================================================
-- PHASE 9: RLS CONTEXT FUNCTIONS
-- ============================================================================

-- Get current account ID from session context
CREATE OR REPLACE FUNCTION saas.current_account_id()
RETURNS UUID
LANGUAGE sql
STABLE
SECURITY DEFINER
AS $$
    SELECT NULLIF(current_setting('app.current_account_id', true), '')::uuid;
$$;

COMMENT ON FUNCTION saas.current_account_id() IS
    'Returns the current account_id from session context. Used in all RLS policies.';

-- Set account context (used by Edge Functions, n8n, etc.)
CREATE OR REPLACE FUNCTION saas.set_account_context(p_account_id UUID)
RETURNS void
LANGUAGE sql
AS $$
    SELECT set_config('app.current_account_id', p_account_id::text, true);
$$;

COMMENT ON FUNCTION saas.set_account_context(UUID) IS
    'Sets the account context for the current session/transaction.';

-- Check if current user has provider role
CREATE OR REPLACE FUNCTION saas.is_provider()
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM saas.account_roles ar
        WHERE ar.account_id = saas.current_account_id()
        AND ar.role = 'PROVIDER'
    );
$$;

-- Check if current account can access a subscription
CREATE OR REPLACE FUNCTION saas.can_access_subscription(p_subscription_id UUID)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM saas.subscriptions s
        WHERE s.id = p_subscription_id
        AND (
            s.tenant_account_id = saas.current_account_id()
            OR s.provider_account_id = saas.current_account_id()
        )
    );
$$;

-- ============================================================================
-- PHASE 10: ENABLE RLS & CREATE POLICIES
-- ============================================================================

-- Accounts: Users can only see their own account
ALTER TABLE saas.accounts ENABLE ROW LEVEL SECURITY;

CREATE POLICY accounts_isolation ON saas.accounts
    FOR ALL
    USING (id = saas.current_account_id());

-- Account roles: Users can see roles for their account
ALTER TABLE saas.account_roles ENABLE ROW LEVEL SECURITY;

CREATE POLICY account_roles_isolation ON saas.account_roles
    FOR ALL
    USING (account_id = saas.current_account_id());

-- Users: Users can see other users in their account
ALTER TABLE saas.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY users_isolation ON saas.users
    FOR ALL
    USING (account_id = saas.current_account_id());

-- Services: Public services are visible to all, others only to provider
ALTER TABLE saas.services ENABLE ROW LEVEL SECURITY;

CREATE POLICY services_read ON saas.services
    FOR SELECT
    USING (
        is_public = true
        OR provider_account_id = saas.current_account_id()
        OR EXISTS (
            SELECT 1 FROM saas.subscriptions s
            WHERE s.service_id = saas.services.id
            AND s.tenant_account_id = saas.current_account_id()
            AND s.status = 'ACTIVE'
        )
    );

CREATE POLICY services_write ON saas.services
    FOR INSERT
    WITH CHECK (provider_account_id = saas.current_account_id());

CREATE POLICY services_update ON saas.services
    FOR UPDATE
    USING (provider_account_id = saas.current_account_id());

CREATE POLICY services_delete ON saas.services
    FOR DELETE
    USING (provider_account_id = saas.current_account_id());

-- Service plans: Same visibility as services
ALTER TABLE saas.service_plans ENABLE ROW LEVEL SECURITY;

CREATE POLICY service_plans_read ON saas.service_plans
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM saas.services s
            WHERE s.id = saas.service_plans.service_id
            AND (
                s.is_public = true
                OR s.provider_account_id = saas.current_account_id()
            )
        )
    );

CREATE POLICY service_plans_write ON saas.service_plans
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM saas.services s
            WHERE s.id = saas.service_plans.service_id
            AND s.provider_account_id = saas.current_account_id()
        )
    );

-- Subscriptions: Visible to both tenant and provider
ALTER TABLE saas.subscriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY subscriptions_read ON saas.subscriptions
    FOR SELECT
    USING (
        tenant_account_id = saas.current_account_id()
        OR provider_account_id = saas.current_account_id()
    );

CREATE POLICY subscriptions_tenant_insert ON saas.subscriptions
    FOR INSERT
    WITH CHECK (tenant_account_id = saas.current_account_id());

CREATE POLICY subscriptions_update ON saas.subscriptions
    FOR UPDATE
    USING (
        tenant_account_id = saas.current_account_id()
        OR provider_account_id = saas.current_account_id()
    );

-- Account links: Visible to both parties
ALTER TABLE saas.account_links ENABLE ROW LEVEL SECURITY;

CREATE POLICY account_links_read ON saas.account_links
    FOR SELECT
    USING (
        from_account_id = saas.current_account_id()
        OR to_account_id = saas.current_account_id()
    );

CREATE POLICY account_links_write ON saas.account_links
    FOR INSERT
    WITH CHECK (from_account_id = saas.current_account_id());

-- Environments: Only visible to own account
ALTER TABLE saas.environments ENABLE ROW LEVEL SECURITY;

CREATE POLICY environments_isolation ON saas.environments
    FOR ALL
    USING (account_id = saas.current_account_id());

-- Usage records: Visible to tenant and provider
ALTER TABLE saas.usage_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY usage_records_read ON saas.usage_records
    FOR SELECT
    USING (
        tenant_account_id = saas.current_account_id()
        OR EXISTS (
            SELECT 1 FROM saas.subscriptions s
            WHERE s.id = saas.usage_records.subscription_id
            AND s.provider_account_id = saas.current_account_id()
        )
    );

CREATE POLICY usage_records_write ON saas.usage_records
    FOR INSERT
    WITH CHECK (tenant_account_id = saas.current_account_id());

-- Audit logs: Only visible to own account
ALTER TABLE logs.account_audit ENABLE ROW LEVEL SECURITY;

CREATE POLICY account_audit_isolation ON logs.account_audit
    FOR SELECT
    USING (account_id = saas.current_account_id());

-- ============================================================================
-- PHASE 11: UPDATE TRIGGERS
-- ============================================================================

-- Apply updated_at triggers to all tables with updated_at column
CREATE OR REPLACE FUNCTION saas.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
    tbl RECORD;
BEGIN
    FOR tbl IN
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE schemaname = 'saas'
    LOOP
        EXECUTE format(
            'DROP TRIGGER IF EXISTS set_updated_at ON %I.%I',
            tbl.schemaname, tbl.tablename
        );
        EXECUTE format(
            'CREATE TRIGGER set_updated_at BEFORE UPDATE ON %I.%I FOR EACH ROW EXECUTE FUNCTION saas.set_updated_at()',
            tbl.schemaname, tbl.tablename
        );
    END LOOP;
END $$;

-- ============================================================================
-- PHASE 12: SEED DEFAULT DATA
-- ============================================================================

-- Insert InsightPulseAI as the platform provider (if not exists)
INSERT INTO saas.accounts (slug, name, legal_name, country, timezone, billing_email)
VALUES ('insightpulseai', 'InsightPulse AI', 'InsightPulse AI Inc.', 'US', 'America/New_York', 'billing@insightpulseai.com')
ON CONFLICT DO NOTHING;

-- Grant PROVIDER and INTERNAL roles to InsightPulseAI
INSERT INTO saas.account_roles (account_id, role, is_primary)
SELECT id, 'PROVIDER', true
FROM saas.accounts WHERE slug = 'insightpulseai'
ON CONFLICT DO NOTHING;

INSERT INTO saas.account_roles (account_id, role, is_primary)
SELECT id, 'INTERNAL', false
FROM saas.accounts WHERE slug = 'insightpulseai'
ON CONFLICT DO NOTHING;

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

COMMENT ON SCHEMA saas IS 'Multi-tenant SaaS model with accounts, services, subscriptions, and RLS policies';
