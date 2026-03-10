-- =============================================================================
-- Migration: ERP Entity Model (Company / Branch)
-- =============================================================================
-- Adds Odoo 19 company/branch semantics ON TOP OF the existing schemas:
--   - core.company / core.tenant (foundation layer, 202512071100)
--   - saas.accounts (SaaS provider model, 202601120001)
--
-- This migration does NOT duplicate those tables. Instead it:
--   1. Adds erp.companies linking to core.company (legal entity) and
--      saas.accounts (billing tenant) — the Odoo res.company mirror
--   2. Adds erp.branches as optional subdivision under a company
--   3. Adds membership tables for company/branch-level access control
--   4. Adds RLS with Odoo-aligned parent/branch narrowing
--
-- Hierarchy (unified across all three schema layers):
--   auth.users → core.app_user → core.tenant_membership (tenant access)
--                                    ↓
--                              core.tenant → saas.accounts (billing)
--                                    ↓
--                              erp.companies (legal/financial, maps to res.company)
--                                    ↓
--                              erp.branches (optional subdivision)
--
-- Rules:
--   - core.tenant = SaaS workspace (billing/identity boundary)
--   - erp.companies = Odoo res.company (legal/financial entity)
--   - erp.branches = optional subdivision (NOT for subsidiaries)
--   - subsidiaries MUST be separate erp.companies rows
--
-- Data classification:
--   - Shared master data: tenant-wide by default (contacts, products)
--   - Scoped transactional data: company-scoped (invoices, orders)
--
-- Spec: spec/odoo-erp-saas/prd.md §18
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. Schema (erp already may exist from other migrations)
-- ---------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS erp;

-- ---------------------------------------------------------------------------
-- 2. erp.companies — Odoo res.company mirror (legal/financial entity)
-- ---------------------------------------------------------------------------
-- Links to core.company (legal entity) and core.tenant (workspace).
-- One tenant may contain multiple companies (multi-company Odoo setup).
-- One company maps 1:1 to an Odoo res.company.
CREATE TABLE IF NOT EXISTS erp.companies (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Link to existing foundation layer
    tenant_id       uuid NOT NULL REFERENCES core.tenant(id) ON DELETE CASCADE,
    core_company_id uuid REFERENCES core.company(id) ON DELETE SET NULL,

    -- Odoo mapping
    odoo_company_id integer,                -- res.company.id in Odoo

    name            text NOT NULL,
    currency_code   text NOT NULL DEFAULT 'PHP',
    country_code    text NOT NULL DEFAULT 'PH',
    is_parent       boolean NOT NULL DEFAULT true,
    status          text NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active', 'suspended', 'archived')),
    metadata        jsonb DEFAULT '{}',
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_erp_companies_tenant
    ON erp.companies(tenant_id);
CREATE INDEX IF NOT EXISTS idx_erp_companies_odoo
    ON erp.companies(odoo_company_id) WHERE odoo_company_id IS NOT NULL;

COMMENT ON TABLE erp.companies IS
    'ERP company — legal/financial boundary. Maps to Odoo res.company. '
    'Links to core.tenant (workspace) and optionally core.company (legal entity). '
    'Independent subsidiaries MUST be separate rows, NOT branches.';

-- ---------------------------------------------------------------------------
-- 3. erp.branches — optional subdivision under a company
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS erp.branches (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id  uuid NOT NULL REFERENCES erp.companies(id) ON DELETE CASCADE,
    name        text NOT NULL,
    code        text,                       -- short code (e.g. 'MNL', 'CEB')
    status      text NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'suspended', 'archived')),
    metadata    jsonb DEFAULT '{}',
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_erp_branches_company
    ON erp.branches(company_id);

COMMENT ON TABLE erp.branches IS
    'Branch — operational subdivision under a company. '
    'Regional offices, warehouses, departments. NOT for subsidiaries.';

-- ---------------------------------------------------------------------------
-- 4. erp.company_memberships — user ↔ company access
-- ---------------------------------------------------------------------------
-- References core.app_user (not auth.users directly) to stay consistent
-- with the core tenancy model.
CREATE TABLE IF NOT EXISTS erp.company_memberships (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    app_user_id uuid NOT NULL REFERENCES core.app_user(id) ON DELETE CASCADE,
    company_id  uuid NOT NULL REFERENCES erp.companies(id) ON DELETE CASCADE,
    role        text NOT NULL DEFAULT 'user'
                CHECK (role IN ('admin', 'manager', 'user', 'viewer')),
    created_at  timestamptz NOT NULL DEFAULT now(),
    UNIQUE (app_user_id, company_id)
);

COMMENT ON TABLE erp.company_memberships IS
    'User access to a specific ERP company. Admin role inherits all branch access. '
    'Uses core.app_user (not auth.users) for consistency with core tenancy model.';

-- ---------------------------------------------------------------------------
-- 5. erp.branch_memberships — user ↔ branch access
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS erp.branch_memberships (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    app_user_id uuid NOT NULL REFERENCES core.app_user(id) ON DELETE CASCADE,
    branch_id   uuid NOT NULL REFERENCES erp.branches(id) ON DELETE CASCADE,
    role        text NOT NULL DEFAULT 'user'
                CHECK (role IN ('manager', 'user', 'viewer')),
    created_at  timestamptz NOT NULL DEFAULT now(),
    UNIQUE (app_user_id, branch_id)
);

COMMENT ON TABLE erp.branch_memberships IS
    'User access to a specific branch. Only needed if branch-level narrowing is active.';

-- ---------------------------------------------------------------------------
-- 6. RLS — Enable on all new tables
-- ---------------------------------------------------------------------------
ALTER TABLE erp.companies              ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp.branches               ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp.company_memberships    ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp.branch_memberships     ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 7. RLS Policies — Company level
-- ---------------------------------------------------------------------------

-- Users can see companies in tenants they belong to
-- (via core.tenant_membership, the existing tenancy model)
CREATE POLICY company_tenant_read ON erp.companies
    FOR SELECT USING (
        tenant_id IN (
            SELECT tm.tenant_id FROM core.tenant_membership tm
            JOIN core.app_user au ON au.id = tm.app_user_id
            WHERE au.auth_user_id = auth.uid()
        )
    );

-- Users can modify companies they have direct membership in
CREATE POLICY company_member_write ON erp.companies
    FOR UPDATE USING (
        id IN (
            SELECT cm.company_id FROM erp.company_memberships cm
            JOIN core.app_user au ON au.id = cm.app_user_id
            WHERE au.auth_user_id = auth.uid()
            AND cm.role IN ('admin', 'manager')
        )
    );

-- Users can see their own company memberships
CREATE POLICY company_membership_read ON erp.company_memberships
    FOR SELECT USING (
        app_user_id IN (
            SELECT id FROM core.app_user WHERE auth_user_id = auth.uid()
        )
    );

-- ---------------------------------------------------------------------------
-- 8. RLS Policies — Branch level (narrowing)
-- ---------------------------------------------------------------------------

-- Users can see branches of companies they belong to
CREATE POLICY branch_company_read ON erp.branches
    FOR SELECT USING (
        company_id IN (
            SELECT cm.company_id FROM erp.company_memberships cm
            JOIN core.app_user au ON au.id = cm.app_user_id
            WHERE au.auth_user_id = auth.uid()
        )
    );

-- Users can see their branch memberships
CREATE POLICY branch_membership_read ON erp.branch_memberships
    FOR SELECT USING (
        app_user_id IN (
            SELECT id FROM core.app_user WHERE auth_user_id = auth.uid()
        )
    );

-- ---------------------------------------------------------------------------
-- 9. Helper function — check company/branch access for RLS reuse
-- ---------------------------------------------------------------------------
-- Resolves auth.uid() → core.app_user → membership checks.
-- Used by transactional tables for RLS policies.
--
-- Narrowing rules (aligned to Odoo 19):
--   - Company admin: sees all branches
--   - Branch member: sees only their branch
--   - company_id is always required; branch_id is optional
CREATE OR REPLACE FUNCTION erp.check_access(
    p_tenant_id uuid,
    p_company_id uuid,
    p_branch_id uuid DEFAULT NULL
) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = erp, core, pg_temp
AS $$
    SELECT EXISTS (
        -- User must be member of the tenant (via core tenancy model)
        SELECT 1 FROM core.tenant_membership tm
        JOIN core.app_user au ON au.id = tm.app_user_id
        WHERE au.auth_user_id = auth.uid()
          AND tm.tenant_id = p_tenant_id
    )
    AND EXISTS (
        -- User must have company membership
        SELECT 1 FROM erp.company_memberships cm
        JOIN core.app_user au ON au.id = cm.app_user_id
        WHERE au.auth_user_id = auth.uid()
          AND cm.company_id = p_company_id
    )
    AND (
        -- Branch check: skip if no branch, or user is company admin, or has branch membership
        p_branch_id IS NULL
        OR EXISTS (
            SELECT 1 FROM erp.company_memberships cm
            JOIN core.app_user au ON au.id = cm.app_user_id
            WHERE au.auth_user_id = auth.uid()
              AND cm.company_id = p_company_id
              AND cm.role = 'admin'
        )
        OR EXISTS (
            SELECT 1 FROM erp.branch_memberships bm
            JOIN core.app_user au ON au.id = bm.app_user_id
            WHERE au.auth_user_id = auth.uid()
              AND bm.branch_id = p_branch_id
        )
    );
$$;

COMMENT ON FUNCTION erp.check_access IS
    'Reusable access check for transactional table RLS. '
    'Resolves auth.uid() → core.app_user → tenant/company/branch membership. '
    'Company admin inherits all branches; branch member sees only their branch. '
    'Aligned to Odoo 19 res.company parent/branch narrowing semantics.';

-- ---------------------------------------------------------------------------
-- 10. Schema Reconciliation Views
-- ---------------------------------------------------------------------------
-- Provides a unified view joining the three entity layers for queries that
-- need the full tenant → company → branch hierarchy.

CREATE OR REPLACE VIEW erp.v_entity_hierarchy AS
SELECT
    t.id        AS tenant_id,
    t.slug      AS tenant_slug,
    t.name      AS tenant_name,
    t.plan      AS tenant_plan,
    sa.id       AS saas_account_id,
    sa.slug     AS saas_account_slug,
    cc.id       AS core_company_id,
    cc.legal_name AS core_legal_name,
    ec.id       AS erp_company_id,
    ec.name     AS erp_company_name,
    ec.odoo_company_id,
    ec.currency_code,
    ec.country_code,
    ec.is_parent,
    eb.id       AS branch_id,
    eb.name     AS branch_name,
    eb.code     AS branch_code
FROM core.tenant t
LEFT JOIN saas.accounts sa ON sa.slug = t.slug
LEFT JOIN erp.companies ec ON ec.tenant_id = t.id
LEFT JOIN core.company cc ON cc.id = ec.core_company_id
LEFT JOIN erp.branches eb ON eb.company_id = ec.id
WHERE ec.status = 'active' OR ec.status IS NULL;

COMMENT ON VIEW erp.v_entity_hierarchy IS
    'Unified view joining core.tenant + saas.accounts + erp.companies + erp.branches. '
    'Use for queries that need the full tenant → company → branch hierarchy.';

-- ---------------------------------------------------------------------------
-- 11. RLS template examples (comments only — apply per transactional table)
-- ---------------------------------------------------------------------------
-- For company/branch-scoped transactional tables:
--   Columns: tenant_id (NOT NULL), company_id (NOT NULL), branch_id (nullable)
--
--   CREATE POLICY scoped_read ON erp.<table>
--       FOR SELECT USING (erp.check_access(tenant_id, company_id, branch_id));
--
--   CREATE POLICY scoped_write ON erp.<table>
--       FOR ALL USING (erp.check_access(tenant_id, company_id, branch_id));
--
-- For shared master data (tenant-wide read):
--   Columns: tenant_id (NOT NULL), company_id (nullable), branch_id (nullable)
--
--   CREATE POLICY shared_read ON <schema>.<table>
--       FOR SELECT USING (
--           tenant_id IN (
--               SELECT tm.tenant_id FROM core.tenant_membership tm
--               JOIN core.app_user au ON au.id = tm.app_user_id
--               WHERE au.auth_user_id = auth.uid()
--           )
--       );
-- ---------------------------------------------------------------------------
