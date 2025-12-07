-- ============================================================================
-- RLS Base Template for InsightPulseAI
-- Version: 1.0.0
-- Date: 2025-12-07
-- ============================================================================
--
-- This file contains the canonical RLS patterns for multi-tenant isolation.
-- Copy and adapt these patterns when creating new tables.
--
-- ============================================================================

-- ============================================================================
-- SECTION 1: CORE TENANT CONTEXT FUNCTION
-- ============================================================================

-- This function retrieves the current tenant ID from the session context.
-- It MUST be called in every RLS policy for tenant isolation.

CREATE OR REPLACE FUNCTION core.current_tenant_id()
RETURNS uuid
LANGUAGE sql
STABLE
SECURITY DEFINER
AS $$
    SELECT NULLIF(current_setting('app.current_tenant_id', true), '')::uuid;
$$;

COMMENT ON FUNCTION core.current_tenant_id() IS
    'Returns the current tenant_id from session context. Used in all RLS policies.';

-- Helper to set tenant context (used by Edge Functions, n8n, etc.)
CREATE OR REPLACE FUNCTION core.set_tenant_context(p_tenant_id uuid)
RETURNS void
LANGUAGE sql
AS $$
    SELECT set_config('app.current_tenant_id', p_tenant_id::text, true);
$$;

COMMENT ON FUNCTION core.set_tenant_context(uuid) IS
    'Sets the tenant context for the current session/transaction.';

-- ============================================================================
-- SECTION 2: STANDARD RLS POLICY PATTERNS
-- ============================================================================

-- Pattern 1: Basic Tenant Isolation (most common)
-- Use this for any table with a tenant_id column

/*
ALTER TABLE schema.table_name ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON schema.table_name
    FOR ALL
    USING (tenant_id = core.current_tenant_id());
*/

-- Pattern 2: Tenant Isolation with Role-Based Access
-- Use this when different roles have different access levels

/*
-- Read access for all authenticated users in tenant
CREATE POLICY tenant_read ON schema.table_name
    FOR SELECT
    USING (tenant_id = core.current_tenant_id());

-- Write access only for specific roles
CREATE POLICY tenant_write ON schema.table_name
    FOR INSERT
    WITH CHECK (
        tenant_id = core.current_tenant_id()
        AND core.has_role('engine_admin')
    );

CREATE POLICY tenant_update ON schema.table_name
    FOR UPDATE
    USING (tenant_id = core.current_tenant_id() AND core.has_role('engine_admin'))
    WITH CHECK (tenant_id = core.current_tenant_id());

CREATE POLICY tenant_delete ON schema.table_name
    FOR DELETE
    USING (tenant_id = core.current_tenant_id() AND core.has_role('engine_admin'));
*/

-- Pattern 3: Owner-Based Access (user can only see their own records)
-- Use this for personal data like expense reports

/*
CREATE POLICY owner_isolation ON schema.table_name
    FOR ALL
    USING (
        tenant_id = core.current_tenant_id()
        AND (
            employee_id = core.current_user_id()
            OR core.has_role('tenant_admin')
        )
    );
*/

-- Pattern 4: Hierarchical Access (manager can see subordinates)
-- Use this for approval workflows

/*
CREATE POLICY hierarchical_access ON schema.table_name
    FOR SELECT
    USING (
        tenant_id = core.current_tenant_id()
        AND (
            employee_id = core.current_user_id()
            OR employee_id IN (SELECT id FROM core.get_subordinates(core.current_user_id()))
            OR core.has_role('tenant_admin')
        )
    );
*/

-- ============================================================================
-- SECTION 3: HELPER FUNCTIONS FOR RLS
-- ============================================================================

-- Get current user's ID from session
CREATE OR REPLACE FUNCTION core.current_user_id()
RETURNS uuid
LANGUAGE sql
STABLE
AS $$
    SELECT NULLIF(current_setting('app.current_user_id', true), '')::uuid;
$$;

-- Check if current user has a specific role
CREATE OR REPLACE FUNCTION core.has_role(p_role_name text)
RETURNS boolean
LANGUAGE sql
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM core.user_roles ur
        JOIN core.roles r ON r.id = ur.role_id
        WHERE ur.user_id = core.current_user_id()
        AND r.name = p_role_name
        AND ur.tenant_id = core.current_tenant_id()
    );
$$;

-- Check if current user has any of the specified roles
CREATE OR REPLACE FUNCTION core.has_any_role(p_role_names text[])
RETURNS boolean
LANGUAGE sql
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM core.user_roles ur
        JOIN core.roles r ON r.id = ur.role_id
        WHERE ur.user_id = core.current_user_id()
        AND r.name = ANY(p_role_names)
        AND ur.tenant_id = core.current_tenant_id()
    );
$$;

-- Get subordinate employee IDs for hierarchical access
CREATE OR REPLACE FUNCTION core.get_subordinates(p_manager_id uuid)
RETURNS TABLE(id uuid)
LANGUAGE sql
STABLE
AS $$
    WITH RECURSIVE subordinates AS (
        SELECT e.id
        FROM core.employees e
        WHERE e.manager_id = p_manager_id
        AND e.tenant_id = core.current_tenant_id()

        UNION ALL

        SELECT e.id
        FROM core.employees e
        JOIN subordinates s ON e.manager_id = s.id
        WHERE e.tenant_id = core.current_tenant_id()
    )
    SELECT id FROM subordinates;
$$;

-- ============================================================================
-- SECTION 4: ROLE AND USER MANAGEMENT TABLES
-- ============================================================================

-- Roles table (if not exists)
CREATE TABLE IF NOT EXISTS core.roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- User roles junction table
CREATE TABLE IF NOT EXISTS core.user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    user_id UUID NOT NULL,
    role_id UUID NOT NULL REFERENCES core.roles(id),
    granted_by UUID,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ,
    UNIQUE(tenant_id, user_id, role_id)
);

ALTER TABLE core.user_roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON core.user_roles
    FOR ALL
    USING (tenant_id = core.current_tenant_id());

-- ============================================================================
-- SECTION 5: STANDARD ROLE DEFINITIONS
-- ============================================================================

-- Insert standard roles (idempotent)
INSERT INTO core.roles (name, description, permissions) VALUES
    ('platform_admin', 'Full platform access, can manage tenants', '["*"]'),
    ('tenant_admin', 'Full tenant access, can manage users and roles', '["tenant:*"]'),
    ('engine_admin', 'Engine-specific admin access', '["engine:*"]'),
    ('engine_user', 'Standard engine user access', '["engine:read", "engine:write"]'),
    ('readonly', 'Read-only access to tenant data', '["tenant:read"]')
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- SECTION 6: EXAMPLE TABLE WITH FULL RLS SETUP
-- ============================================================================

/*
-- Example: Creating a new table with complete RLS setup

-- 1. Create the table
CREATE TABLE schema.example_table (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    employee_id UUID NOT NULL REFERENCES core.employees(id),
    data TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ
);

-- 2. Enable RLS
ALTER TABLE schema.example_table ENABLE ROW LEVEL SECURITY;

-- 3. Create tenant isolation policy
CREATE POLICY tenant_isolation ON schema.example_table
    FOR ALL
    USING (tenant_id = core.current_tenant_id());

-- 4. Create indexes
CREATE INDEX idx_example_table_tenant ON schema.example_table(tenant_id);
CREATE INDEX idx_example_table_employee ON schema.example_table(tenant_id, employee_id);

-- 5. Add updated_at trigger
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON schema.example_table
    FOR EACH ROW
    EXECUTE FUNCTION core.set_updated_at();

-- 6. Grant permissions to roles
GRANT SELECT ON schema.example_table TO authenticated;
GRANT INSERT, UPDATE ON schema.example_table TO authenticated;
*/

-- ============================================================================
-- SECTION 7: AUDIT TRAIL FOR RLS CHANGES
-- ============================================================================

-- Table to log RLS policy changes (for compliance)
CREATE TABLE IF NOT EXISTS logs.rls_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schema_name TEXT NOT NULL,
    table_name TEXT NOT NULL,
    policy_name TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('CREATE', 'ALTER', 'DROP')),
    policy_definition TEXT,
    performed_by TEXT NOT NULL DEFAULT current_user,
    performed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE logs.rls_audit IS
    'Audit trail for RLS policy changes. Required for compliance.';

-- ============================================================================
-- END OF TEMPLATE
-- ============================================================================
