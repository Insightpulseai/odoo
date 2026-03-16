-- =============================================================================
-- Migration: 4502 - Operations Context Bindings
-- Purpose: Map platform tenant/account/project context to Odoo entities
-- Philosophy: Keep canonical spine in Supabase ops.*, store only mappings
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- Schema: ops (Operations Context Layer)
-- -----------------------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS ops;

-- -----------------------------------------------------------------------------
-- Odoo Bindings Table
-- Maps platform context (tenant/account/project) to Odoo DB + native entities
-- Avoids duplicating res.company/res.partner/project.project in custom models
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ops.odoo_bindings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Platform context (from ops.* canonical tables)
    tenant_id uuid NOT NULL,
    account_id uuid,  -- NULL means tenant-level binding
    project_id uuid,  -- NULL means account-level binding
    environment_id uuid NOT NULL,

    -- Odoo target coordinates
    odoo_db text NOT NULL,  -- e.g., 'odoo_core', 'odoo_marketing'
    odoo_company_id int,    -- res.company.id (NULL = all companies)
    odoo_partner_id int,    -- res.partner.id (customer/vendor org)
    odoo_project_id int,    -- project.project.id (delivery scope)
    odoo_analytic_account_id int,  -- account.analytic.account.id (cost spine)

    -- Sync metadata
    sync_enabled boolean NOT NULL DEFAULT true,
    last_sync_at timestamptz,
    sync_error text,

    -- Audit
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    created_by uuid,

    -- Constraints
    UNIQUE (tenant_id, account_id, project_id, environment_id)
);

COMMENT ON TABLE ops.odoo_bindings IS
'Maps platform context to Odoo entities. Avoids duplicating native Odoo models (res.company, res.partner, project.project) in custom ipai_* modules.';

COMMENT ON COLUMN ops.odoo_bindings.odoo_analytic_account_id IS
'Links to account.analytic.account - the cost spine that bridges accounting ↔ projects ↔ timesheets ↔ profitability';


-- -----------------------------------------------------------------------------
-- Tenancy Mode Configuration
-- Explicit choice: multi-DB (SaaS) vs multi-company (enterprise)
-- -----------------------------------------------------------------------------

CREATE TYPE ops.tenancy_mode AS ENUM (
    'multi_db',      -- 1 tenant = 1 Odoo DB (SaaS, cleanest isolation)
    'multi_company'  -- 1 DB, multi-company (res.company + allowed_company_ids)
);

CREATE TABLE IF NOT EXISTS ops.tenant_config (
    tenant_id uuid PRIMARY KEY,
    tenancy_mode ops.tenancy_mode NOT NULL DEFAULT 'multi_db',
    default_odoo_db text,
    default_company_id int,

    -- Feature flags
    enable_cross_company_access boolean NOT NULL DEFAULT false,
    enable_analytic_tracking boolean NOT NULL DEFAULT true,

    -- Metadata
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE ops.tenant_config IS
'Explicit tenancy mode per tenant. Default is multi_db (1 tenant = 1 Odoo DB) for cleanest isolation.';


-- -----------------------------------------------------------------------------
-- Context Resolution Function
-- Used by /context endpoint to resolve platform context → Odoo IDs
-- -----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ops.resolve_odoo_context(
    p_tenant_id uuid,
    p_account_id uuid DEFAULT NULL,
    p_project_id uuid DEFAULT NULL,
    p_environment_id uuid DEFAULT NULL
)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_binding ops.odoo_bindings%ROWTYPE;
    v_config ops.tenant_config%ROWTYPE;
BEGIN
    -- Get tenant config
    SELECT * INTO v_config FROM ops.tenant_config WHERE tenant_id = p_tenant_id;

    -- Find most specific binding (project > account > tenant)
    SELECT * INTO v_binding
    FROM ops.odoo_bindings
    WHERE tenant_id = p_tenant_id
      AND (environment_id = p_environment_id OR p_environment_id IS NULL)
      AND (
          (project_id = p_project_id AND p_project_id IS NOT NULL)
          OR (account_id = p_account_id AND project_id IS NULL AND p_project_id IS NULL)
          OR (account_id IS NULL AND project_id IS NULL)
      )
    ORDER BY
        CASE WHEN project_id IS NOT NULL THEN 1
             WHEN account_id IS NOT NULL THEN 2
             ELSE 3 END
    LIMIT 1;

    IF v_binding IS NULL THEN
        RETURN jsonb_build_object(
            'ok', false,
            'error', 'No Odoo binding found for context'
        );
    END IF;

    RETURN jsonb_build_object(
        'ok', true,
        'tenancy_mode', COALESCE(v_config.tenancy_mode::text, 'multi_db'),
        'odoo_db', v_binding.odoo_db,
        'odoo_company_id', v_binding.odoo_company_id,
        'odoo_partner_id', v_binding.odoo_partner_id,
        'odoo_project_id', v_binding.odoo_project_id,
        'odoo_analytic_account_id', v_binding.odoo_analytic_account_id,
        'sync_enabled', v_binding.sync_enabled
    );
END;
$$;

COMMENT ON FUNCTION ops.resolve_odoo_context IS
'Resolves platform context (tenant/account/project) to Odoo entity IDs. Used by /context API endpoint.';


-- -----------------------------------------------------------------------------
-- Analytic Account Sync Tracking
-- Track which analytic accounts are synced from Odoo for cost spine
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ops.analytic_account_cache (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    odoo_db text NOT NULL,
    odoo_analytic_id int NOT NULL,

    -- Cached Odoo fields
    name text NOT NULL,
    code text,
    plan_id int,
    plan_name text,
    company_id int,
    partner_id int,
    active boolean NOT NULL DEFAULT true,

    -- Financial summary (updated by sync)
    balance numeric(16,2) DEFAULT 0,
    debit numeric(16,2) DEFAULT 0,
    credit numeric(16,2) DEFAULT 0,
    line_count int DEFAULT 0,

    -- Sync metadata
    last_sync_at timestamptz NOT NULL DEFAULT now(),

    UNIQUE (tenant_id, odoo_db, odoo_analytic_id)
);

COMMENT ON TABLE ops.analytic_account_cache IS
'Cached analytic accounts from Odoo. The cost spine that bridges accounting ↔ projects ↔ timesheets ↔ profitability.';


-- -----------------------------------------------------------------------------
-- RLS Policies
-- -----------------------------------------------------------------------------

ALTER TABLE ops.odoo_bindings ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.tenant_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.analytic_account_cache ENABLE ROW LEVEL SECURITY;

-- Service role has full access
CREATE POLICY "Service role full access on odoo_bindings"
    ON ops.odoo_bindings FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on tenant_config"
    ON ops.tenant_config FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role full access on analytic_account_cache"
    ON ops.analytic_account_cache FOR ALL
    USING (auth.role() = 'service_role');


-- -----------------------------------------------------------------------------
-- Indexes
-- -----------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_odoo_bindings_tenant
    ON ops.odoo_bindings (tenant_id);

CREATE INDEX IF NOT EXISTS idx_odoo_bindings_lookup
    ON ops.odoo_bindings (tenant_id, account_id, project_id, environment_id);

CREATE INDEX IF NOT EXISTS idx_analytic_cache_tenant_db
    ON ops.analytic_account_cache (tenant_id, odoo_db);


COMMIT;

-- =============================================================================
-- End Migration: 4502 - Operations Context Bindings
-- =============================================================================
