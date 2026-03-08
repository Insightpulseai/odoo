-- =============================================================================
-- Migration: ERP Entity Model (Company / Branch)
-- =============================================================================
-- Implements the unified tenant → company → branch entity hierarchy
-- aligned to Odoo 19 res.company semantics.
--
-- Hierarchy:
--   auth.users → tenant.organizations → erp.companies → erp.branches
--
-- Rules:
--   - organization = SaaS tenant (billing/identity boundary)
--   - company = legal/financial entity (maps to Odoo res.company)
--   - branch = optional subdivision (maps to Odoo child res.company)
--   - subsidiaries MUST be separate companies, NOT branches
--
-- Data classification:
--   - Shared master data: org-wide by default (contacts, products)
--   - Scoped transactional data: company-scoped (invoices, orders)
--
-- Spec: spec/odoo-erp-saas/prd.md §18
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. Schemas
-- ---------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS tenant;
CREATE SCHEMA IF NOT EXISTS erp;

-- ---------------------------------------------------------------------------
-- 2. tenant.organizations — SaaS tenant (billing/identity boundary)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tenant.organizations (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name        text NOT NULL,
    slug        text NOT NULL UNIQUE,
    plan_id     text,                       -- references plans catalog
    status      text NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'suspended', 'archived')),
    metadata    jsonb DEFAULT '{}',
    created_at  timestamptz NOT NULL DEFAULT now(),
    updated_at  timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE tenant.organizations IS
    'SaaS tenant. Billing and identity boundary. One org may contain multiple Odoo companies.';

-- ---------------------------------------------------------------------------
-- 3. tenant.memberships — user ↔ organization
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tenant.memberships (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    organization_id uuid NOT NULL REFERENCES tenant.organizations(id) ON DELETE CASCADE,
    role            text NOT NULL DEFAULT 'member'
                    CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    created_at      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (user_id, organization_id)
);

COMMENT ON TABLE tenant.memberships IS
    'User membership in a SaaS organization. Grants access to the org boundary.';

-- ---------------------------------------------------------------------------
-- 4. erp.companies — Odoo res.company mirror (legal/financial entity)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS erp.companies (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id uuid NOT NULL REFERENCES tenant.organizations(id) ON DELETE CASCADE,
    odoo_company_id integer,                -- maps to res.company.id in Odoo
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

CREATE INDEX IF NOT EXISTS idx_erp_companies_org
    ON erp.companies(organization_id);

COMMENT ON TABLE erp.companies IS
    'ERP company — legal/financial boundary. Maps to Odoo res.company. '
    'Independent subsidiaries MUST be separate rows, NOT branches.';

-- ---------------------------------------------------------------------------
-- 5. erp.branches — optional subdivision under a company
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
-- 6. erp.company_memberships — user ↔ company access
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS erp.company_memberships (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    company_id  uuid NOT NULL REFERENCES erp.companies(id) ON DELETE CASCADE,
    role        text NOT NULL DEFAULT 'user'
                CHECK (role IN ('admin', 'manager', 'user', 'viewer')),
    created_at  timestamptz NOT NULL DEFAULT now(),
    UNIQUE (user_id, company_id)
);

COMMENT ON TABLE erp.company_memberships IS
    'User access to a specific company. Admin role inherits all branch access.';

-- ---------------------------------------------------------------------------
-- 7. erp.branch_memberships — user ↔ branch access
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS erp.branch_memberships (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    branch_id   uuid NOT NULL REFERENCES erp.branches(id) ON DELETE CASCADE,
    role        text NOT NULL DEFAULT 'user'
                CHECK (role IN ('manager', 'user', 'viewer')),
    created_at  timestamptz NOT NULL DEFAULT now(),
    UNIQUE (user_id, branch_id)
);

COMMENT ON TABLE erp.branch_memberships IS
    'User access to a specific branch. Only needed if branch-level narrowing is active.';

-- ---------------------------------------------------------------------------
-- 8. RLS — Enable on all tables
-- ---------------------------------------------------------------------------
ALTER TABLE tenant.organizations       ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant.memberships         ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp.companies              ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp.branches               ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp.company_memberships    ENABLE ROW LEVEL SECURITY;
ALTER TABLE erp.branch_memberships     ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 9. RLS Policies — Organization level
-- ---------------------------------------------------------------------------

-- Users can see orgs they belong to
CREATE POLICY org_member_read ON tenant.organizations
    FOR SELECT USING (
        id IN (
            SELECT organization_id FROM tenant.memberships
            WHERE user_id = auth.uid()
        )
    );

-- Users can see their own memberships
CREATE POLICY membership_self_read ON tenant.memberships
    FOR SELECT USING (user_id = auth.uid());

-- ---------------------------------------------------------------------------
-- 10. RLS Policies — Company level
-- ---------------------------------------------------------------------------

-- Users can see companies in their org
CREATE POLICY company_org_read ON erp.companies
    FOR SELECT USING (
        organization_id IN (
            SELECT organization_id FROM tenant.memberships
            WHERE user_id = auth.uid()
        )
    );

-- Users can modify companies they have membership in
CREATE POLICY company_member_write ON erp.companies
    FOR UPDATE USING (
        id IN (
            SELECT company_id FROM erp.company_memberships
            WHERE user_id = auth.uid()
            AND role IN ('admin', 'manager')
        )
    );

-- Users can see their company memberships
CREATE POLICY company_membership_read ON erp.company_memberships
    FOR SELECT USING (user_id = auth.uid());

-- ---------------------------------------------------------------------------
-- 11. RLS Policies — Branch level (narrowing)
-- ---------------------------------------------------------------------------

-- Users can see branches of companies they belong to
CREATE POLICY branch_company_read ON erp.branches
    FOR SELECT USING (
        company_id IN (
            SELECT company_id FROM erp.company_memberships
            WHERE user_id = auth.uid()
        )
    );

-- Users can see their branch memberships
CREATE POLICY branch_membership_read ON erp.branch_memberships
    FOR SELECT USING (user_id = auth.uid());

-- ---------------------------------------------------------------------------
-- 12. Helper function — check company/branch access for RLS reuse
-- ---------------------------------------------------------------------------

-- Check if user has access to a specific org + company + branch combination.
-- Used by transactional tables for RLS policies.
--
-- Narrowing rules (aligned to Odoo):
--   - Company admin: sees all branches
--   - Branch member: sees only their branch
--   - company_id is always required; branch_id is optional
CREATE OR REPLACE FUNCTION erp.check_access(
    p_organization_id uuid,
    p_company_id uuid,
    p_branch_id uuid DEFAULT NULL
) RETURNS boolean
LANGUAGE sql STABLE SECURITY DEFINER
SET search_path = erp, pg_temp
AS $$
    SELECT EXISTS (
        -- User must be member of the organization
        SELECT 1 FROM tenant.memberships tm
        WHERE tm.user_id = auth.uid()
          AND tm.organization_id = p_organization_id
    )
    AND EXISTS (
        -- User must have company membership
        SELECT 1 FROM erp.company_memberships cm
        WHERE cm.user_id = auth.uid()
          AND cm.company_id = p_company_id
    )
    AND (
        -- Branch check: skip if no branch, or user is company admin, or has branch membership
        p_branch_id IS NULL
        OR EXISTS (
            SELECT 1 FROM erp.company_memberships cm
            WHERE cm.user_id = auth.uid()
              AND cm.company_id = p_company_id
              AND cm.role = 'admin'
        )
        OR EXISTS (
            SELECT 1 FROM erp.branch_memberships bm
            WHERE bm.user_id = auth.uid()
              AND bm.branch_id = p_branch_id
        )
    );
$$;

COMMENT ON FUNCTION erp.check_access IS
    'Reusable access check for transactional table RLS. '
    'Company admin inherits all branches; branch member sees only their branch.';

-- ---------------------------------------------------------------------------
-- 13. Example RLS template for transactional tables
-- ---------------------------------------------------------------------------
-- Apply to any table with (organization_id, company_id, branch_id) columns:
--
--   CREATE POLICY scoped_read ON erp.<table>
--       FOR SELECT USING (
--           erp.check_access(organization_id, company_id, branch_id)
--       );
--
--   CREATE POLICY scoped_write ON erp.<table>
--       FOR ALL USING (
--           erp.check_access(organization_id, company_id, branch_id)
--       );
--
-- For shared master data (org-wide read, optional company restriction):
--
--   CREATE POLICY shared_read ON <schema>.<table>
--       FOR SELECT USING (
--           organization_id IN (
--               SELECT organization_id FROM tenant.memberships
--               WHERE user_id = auth.uid()
--           )
--       );
-- ---------------------------------------------------------------------------
