-- =============================================================================
-- Migration: 4500 - Unity Catalog-like Asset Registry
-- Purpose: Governance plane for data + AI assets with UC-compatible patterns
-- Family: 4500 (Catalog/Governance - between AI 4000 and Analytics 5000)
--
-- Architecture:
--   - catalog.assets: Universal registry (tables, views, files, models, Odoo objects)
--   - catalog.policies: RBAC/ABAC permissions per asset
--   - catalog.lineage_edges: Data lineage graph (OpenLineage-compatible)
--   - catalog.tools: Tool definitions for ipai_ask_ai copilot
--   - catalog.tool_bindings: Map tools to Odoo actions / Edge Functions
--
-- FQDN Conventions:
--   supabase.<project>.<schema>.<object>   → Supabase tables/views
--   odoo.<db>.<model>                      → Odoo models
--   odoo.<db>.action.<xmlid>               → Odoo actions
--   scout.<layer>.<object>                 → Scout medallion objects
--   uc.<catalog>.<schema>.<table>          → External Unity Catalog (future)
--
-- RLS Strategy: company_id-based isolation with service_role bypass
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- Schema Creation
-- -----------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS catalog;

COMMENT ON SCHEMA catalog IS 'Unity Catalog-like asset registry for governance, lineage, and tool orchestration';

-- -----------------------------------------------------------------------------
-- Enum Types
-- -----------------------------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE catalog.asset_type AS ENUM (
        'table',
        'view',
        'file',
        'model',
        'function',
        'dashboard',
        'odoo_model',
        'odoo_action',
        'odoo_menu',
        'odoo_view',
        'odoo_report',
        'scout_layer',
        'ai_prompt',
        'ai_agent',
        'notebook',
        'pipeline'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE catalog.asset_system AS ENUM (
        'odoo',
        'supabase',
        'databricks',
        'scout',
        'files',
        'n8n',
        'mcp',
        'external'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE catalog.principal_type AS ENUM (
        'user',
        'role',
        'group',
        'service'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE catalog.edge_type AS ENUM (
        'derived_from',
        'writes_to',
        'reads_from',
        'publishes',
        'triggers',
        'depends_on',
        'transforms'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE catalog.tool_type AS ENUM (
        'query',
        'action',
        'rpc',
        'edge_function',
        'n8n_workflow',
        'mcp_tool'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- -----------------------------------------------------------------------------
-- Core Tables
-- -----------------------------------------------------------------------------

-- Assets: Universal registry of data + AI assets
CREATE TABLE IF NOT EXISTS catalog.assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identity
    fqdn TEXT NOT NULL UNIQUE,  -- Fully Qualified Domain Name (canonical key)
    asset_type catalog.asset_type NOT NULL,
    system catalog.asset_system NOT NULL,

    -- Metadata
    title TEXT NOT NULL,
    description TEXT,
    owner TEXT,  -- email or username
    tags TEXT[] DEFAULT '{}',

    -- Location
    uri TEXT,  -- Deep link: Odoo URL, Supabase URL, object storage URL

    -- Schema/Structure (flexible)
    metadata JSONB DEFAULT '{}',  -- columns, fields, parameters, prompts, etc.

    -- Multi-tenancy
    company_id INT,  -- NULL = global/shared asset

    -- Lifecycle
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'deprecated', 'archived', 'draft')),
    version INT DEFAULT 1,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    created_by TEXT,
    updated_by TEXT,

    -- Search
    search_vector TSVECTOR
);

CREATE INDEX IF NOT EXISTS idx_catalog_assets_fqdn ON catalog.assets (fqdn);
CREATE INDEX IF NOT EXISTS idx_catalog_assets_type ON catalog.assets (asset_type);
CREATE INDEX IF NOT EXISTS idx_catalog_assets_system ON catalog.assets (system);
CREATE INDEX IF NOT EXISTS idx_catalog_assets_company ON catalog.assets (company_id);
CREATE INDEX IF NOT EXISTS idx_catalog_assets_tags ON catalog.assets USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_catalog_assets_metadata ON catalog.assets USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_catalog_assets_search ON catalog.assets USING GIN (search_vector);

COMMENT ON TABLE catalog.assets IS 'Universal asset registry (UC-compatible). Each row = one governed asset.';
COMMENT ON COLUMN catalog.assets.fqdn IS 'Canonical identifier: supabase.ipai.scout.gold_*, odoo.odoo_core.account.move, etc.';
COMMENT ON COLUMN catalog.assets.metadata IS 'Flexible schema: columns for tables, fields for Odoo models, parameters for functions';


-- Policies: RBAC/ABAC permissions per asset
CREATE TABLE IF NOT EXISTS catalog.policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Target
    asset_id UUID NOT NULL REFERENCES catalog.assets(id) ON DELETE CASCADE,

    -- Principal
    principal_type catalog.principal_type NOT NULL,
    principal_key TEXT NOT NULL,  -- e.g., 'finance_manager', 'user@example.com', 'service_role'

    -- Permissions
    permissions JSONB NOT NULL DEFAULT '{"read": true, "write": false, "execute": false}',
    -- Schema: { read: bool, write: bool, execute: bool, admin: bool }

    -- Conditions (optional row-level / column-level filters)
    conditions JSONB DEFAULT '{}',
    -- Schema: { row_filter: "company_id = $company_id", column_mask: ["ssn", "salary"] }

    -- Priority (higher = evaluated first)
    priority INT DEFAULT 0,

    -- Lifecycle
    active BOOLEAN DEFAULT true,
    expires_at TIMESTAMPTZ,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    created_by TEXT,

    UNIQUE (asset_id, principal_type, principal_key)
);

CREATE INDEX IF NOT EXISTS idx_catalog_policies_asset ON catalog.policies (asset_id);
CREATE INDEX IF NOT EXISTS idx_catalog_policies_principal ON catalog.policies (principal_type, principal_key);

COMMENT ON TABLE catalog.policies IS 'Access control policies per asset. Evaluated by copilot before granting access.';


-- Lineage Edges: Data lineage graph (OpenLineage-compatible)
CREATE TABLE IF NOT EXISTS catalog.lineage_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source → Target
    from_asset_id UUID NOT NULL REFERENCES catalog.assets(id) ON DELETE CASCADE,
    to_asset_id UUID NOT NULL REFERENCES catalog.assets(id) ON DELETE CASCADE,

    -- Edge type
    edge_type catalog.edge_type NOT NULL,

    -- Metadata
    transformation TEXT,  -- SQL, Python code, or description
    job_name TEXT,  -- Pipeline/job that created this edge
    metadata JSONB DEFAULT '{}',

    -- Audit
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,

    UNIQUE (from_asset_id, to_asset_id, edge_type)
);

CREATE INDEX IF NOT EXISTS idx_catalog_lineage_from ON catalog.lineage_edges (from_asset_id);
CREATE INDEX IF NOT EXISTS idx_catalog_lineage_to ON catalog.lineage_edges (to_asset_id);
CREATE INDEX IF NOT EXISTS idx_catalog_lineage_type ON catalog.lineage_edges (edge_type);

COMMENT ON TABLE catalog.lineage_edges IS 'Data lineage graph. Enables impact analysis and provenance tracking.';


-- Tools: Tool definitions for ipai_ask_ai copilot
CREATE TABLE IF NOT EXISTS catalog.tools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Identity
    tool_key TEXT NOT NULL UNIQUE,  -- e.g., 'odoo.create_invoice', 'scout.query_sales'
    tool_type catalog.tool_type NOT NULL,

    -- Metadata
    name TEXT NOT NULL,
    description TEXT NOT NULL,  -- Used for LLM tool selection

    -- Schema (OpenAPI-ish)
    parameters JSONB NOT NULL DEFAULT '{}',
    -- Schema: { type: "object", properties: { ... }, required: [...] }

    returns JSONB DEFAULT '{}',
    -- Schema: { type: "object", properties: { ... } }

    -- Access control
    requires_confirmation BOOLEAN DEFAULT true,  -- Preview → Apply pattern
    allowed_roles TEXT[] DEFAULT '{}',  -- Empty = all roles

    -- Tags for categorization
    tags TEXT[] DEFAULT '{}',

    -- Lifecycle
    active BOOLEAN DEFAULT true,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_catalog_tools_key ON catalog.tools (tool_key);
CREATE INDEX IF NOT EXISTS idx_catalog_tools_type ON catalog.tools (tool_type);
CREATE INDEX IF NOT EXISTS idx_catalog_tools_tags ON catalog.tools USING GIN (tags);

COMMENT ON TABLE catalog.tools IS 'Tool definitions for AI copilot. Schema follows OpenAPI-ish format.';


-- Tool Bindings: Map tools to execution targets
CREATE TABLE IF NOT EXISTS catalog.tool_bindings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Tool reference
    tool_id UUID NOT NULL REFERENCES catalog.tools(id) ON DELETE CASCADE,

    -- Execution target
    target_type TEXT NOT NULL CHECK (target_type IN ('odoo_action', 'odoo_rpc', 'edge_function', 'n8n_webhook', 'mcp_server')),
    target_config JSONB NOT NULL,
    -- Schema varies by target_type:
    --   odoo_action: { model: "account.move", method: "action_post", action_id: 123 }
    --   odoo_rpc: { model: "account.move", method: "create", endpoint: "/web/dataset/call_kw" }
    --   edge_function: { function_name: "three-way-match", base_url: "..." }
    --   n8n_webhook: { webhook_url: "...", workflow_id: "..." }
    --   mcp_server: { server_name: "odoo-erp-server", tool_name: "create_record" }

    -- Priority (for multiple bindings per tool)
    priority INT DEFAULT 0,

    -- Conditions (when to use this binding)
    conditions JSONB DEFAULT '{}',
    -- Schema: { company_id: [1, 2], environment: "production" }

    -- Lifecycle
    active BOOLEAN DEFAULT true,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,

    UNIQUE (tool_id, target_type, priority)
);

CREATE INDEX IF NOT EXISTS idx_catalog_bindings_tool ON catalog.tool_bindings (tool_id);
CREATE INDEX IF NOT EXISTS idx_catalog_bindings_target ON catalog.tool_bindings (target_type);

COMMENT ON TABLE catalog.tool_bindings IS 'Maps tools to execution targets (Odoo, Edge Functions, n8n, MCP).';


-- -----------------------------------------------------------------------------
-- Full-Text Search Trigger
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION catalog.update_asset_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english',
        COALESCE(NEW.fqdn, '') || ' ' ||
        COALESCE(NEW.title, '') || ' ' ||
        COALESCE(NEW.description, '') || ' ' ||
        COALESCE(NEW.owner, '') || ' ' ||
        COALESCE(array_to_string(NEW.tags, ' '), '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_catalog_assets_search ON catalog.assets;
CREATE TRIGGER trg_catalog_assets_search
    BEFORE INSERT OR UPDATE ON catalog.assets
    FOR EACH ROW
    EXECUTE FUNCTION catalog.update_asset_search_vector();


-- -----------------------------------------------------------------------------
-- Updated At Trigger
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION catalog.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_catalog_assets_updated ON catalog.assets;
CREATE TRIGGER trg_catalog_assets_updated
    BEFORE UPDATE ON catalog.assets
    FOR EACH ROW
    EXECUTE FUNCTION catalog.set_updated_at();

DROP TRIGGER IF EXISTS trg_catalog_policies_updated ON catalog.policies;
CREATE TRIGGER trg_catalog_policies_updated
    BEFORE UPDATE ON catalog.policies
    FOR EACH ROW
    EXECUTE FUNCTION catalog.set_updated_at();

DROP TRIGGER IF EXISTS trg_catalog_lineage_updated ON catalog.lineage_edges;
CREATE TRIGGER trg_catalog_lineage_updated
    BEFORE UPDATE ON catalog.lineage_edges
    FOR EACH ROW
    EXECUTE FUNCTION catalog.set_updated_at();

DROP TRIGGER IF EXISTS trg_catalog_tools_updated ON catalog.tools;
CREATE TRIGGER trg_catalog_tools_updated
    BEFORE UPDATE ON catalog.tools
    FOR EACH ROW
    EXECUTE FUNCTION catalog.set_updated_at();

DROP TRIGGER IF EXISTS trg_catalog_bindings_updated ON catalog.tool_bindings;
CREATE TRIGGER trg_catalog_bindings_updated
    BEFORE UPDATE ON catalog.tool_bindings
    FOR EACH ROW
    EXECUTE FUNCTION catalog.set_updated_at();


-- -----------------------------------------------------------------------------
-- Row Level Security
-- -----------------------------------------------------------------------------
ALTER TABLE catalog.assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE catalog.policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE catalog.lineage_edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE catalog.tools ENABLE ROW LEVEL SECURITY;
ALTER TABLE catalog.tool_bindings ENABLE ROW LEVEL SECURITY;

-- Assets: Company-scoped with global fallback
DROP POLICY IF EXISTS "catalog_assets_access" ON catalog.assets;
CREATE POLICY "catalog_assets_access" ON catalog.assets FOR ALL
    USING (
        company_id IS NULL  -- Global assets visible to all
        OR company_id = (current_setting('app.current_company_id', true)::int)
        OR auth.jwt() ->> 'role' = 'service_role'
    );

-- Policies: Inherit from parent asset
DROP POLICY IF EXISTS "catalog_policies_access" ON catalog.policies;
CREATE POLICY "catalog_policies_access" ON catalog.policies FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM catalog.assets a
            WHERE a.id = catalog.policies.asset_id
            AND (
                a.company_id IS NULL
                OR a.company_id = (current_setting('app.current_company_id', true)::int)
                OR auth.jwt() ->> 'role' = 'service_role'
            )
        )
    );

-- Lineage: Inherit from both source and target assets
DROP POLICY IF EXISTS "catalog_lineage_access" ON catalog.lineage_edges;
CREATE POLICY "catalog_lineage_access" ON catalog.lineage_edges FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM catalog.assets a
            WHERE a.id = catalog.lineage_edges.from_asset_id
            AND (
                a.company_id IS NULL
                OR a.company_id = (current_setting('app.current_company_id', true)::int)
                OR auth.jwt() ->> 'role' = 'service_role'
            )
        )
        AND EXISTS (
            SELECT 1 FROM catalog.assets a
            WHERE a.id = catalog.lineage_edges.to_asset_id
            AND (
                a.company_id IS NULL
                OR a.company_id = (current_setting('app.current_company_id', true)::int)
                OR auth.jwt() ->> 'role' = 'service_role'
            )
        )
    );

-- Tools: Global (no company scoping)
DROP POLICY IF EXISTS "catalog_tools_access" ON catalog.tools;
CREATE POLICY "catalog_tools_access" ON catalog.tools FOR ALL
    USING (true);

-- Tool Bindings: Global (no company scoping)
DROP POLICY IF EXISTS "catalog_bindings_access" ON catalog.tool_bindings;
CREATE POLICY "catalog_bindings_access" ON catalog.tool_bindings FOR ALL
    USING (true);


-- -----------------------------------------------------------------------------
-- Helper Functions
-- -----------------------------------------------------------------------------

-- Get asset by FQDN
CREATE OR REPLACE FUNCTION catalog.get_asset(p_fqdn TEXT)
RETURNS catalog.assets AS $$
    SELECT * FROM catalog.assets WHERE fqdn = p_fqdn LIMIT 1;
$$ LANGUAGE sql STABLE;

-- Search assets by query
CREATE OR REPLACE FUNCTION catalog.search_assets(
    p_query TEXT,
    p_asset_type catalog.asset_type DEFAULT NULL,
    p_system catalog.asset_system DEFAULT NULL,
    p_limit INT DEFAULT 20
)
RETURNS SETOF catalog.assets AS $$
    SELECT *
    FROM catalog.assets
    WHERE (p_query IS NULL OR search_vector @@ plainto_tsquery('english', p_query))
      AND (p_asset_type IS NULL OR asset_type = p_asset_type)
      AND (p_system IS NULL OR system = p_system)
      AND status = 'active'
    ORDER BY ts_rank(search_vector, plainto_tsquery('english', COALESCE(p_query, ''))) DESC
    LIMIT p_limit;
$$ LANGUAGE sql STABLE;

-- Get lineage (upstream)
CREATE OR REPLACE FUNCTION catalog.get_upstream_lineage(p_asset_id UUID, p_depth INT DEFAULT 3)
RETURNS TABLE (
    asset_id UUID,
    fqdn TEXT,
    title TEXT,
    edge_type catalog.edge_type,
    depth INT
) AS $$
    WITH RECURSIVE lineage AS (
        -- Base case: direct parents
        SELECT
            le.from_asset_id as asset_id,
            a.fqdn,
            a.title,
            le.edge_type,
            1 as depth
        FROM catalog.lineage_edges le
        JOIN catalog.assets a ON a.id = le.from_asset_id
        WHERE le.to_asset_id = p_asset_id

        UNION ALL

        -- Recursive case: ancestors
        SELECT
            le.from_asset_id,
            a.fqdn,
            a.title,
            le.edge_type,
            l.depth + 1
        FROM catalog.lineage_edges le
        JOIN catalog.assets a ON a.id = le.from_asset_id
        JOIN lineage l ON l.asset_id = le.to_asset_id
        WHERE l.depth < p_depth
    )
    SELECT DISTINCT * FROM lineage ORDER BY depth;
$$ LANGUAGE sql STABLE;

-- Get lineage (downstream)
CREATE OR REPLACE FUNCTION catalog.get_downstream_lineage(p_asset_id UUID, p_depth INT DEFAULT 3)
RETURNS TABLE (
    asset_id UUID,
    fqdn TEXT,
    title TEXT,
    edge_type catalog.edge_type,
    depth INT
) AS $$
    WITH RECURSIVE lineage AS (
        -- Base case: direct children
        SELECT
            le.to_asset_id as asset_id,
            a.fqdn,
            a.title,
            le.edge_type,
            1 as depth
        FROM catalog.lineage_edges le
        JOIN catalog.assets a ON a.id = le.to_asset_id
        WHERE le.from_asset_id = p_asset_id

        UNION ALL

        -- Recursive case: descendants
        SELECT
            le.to_asset_id,
            a.fqdn,
            a.title,
            le.edge_type,
            l.depth + 1
        FROM catalog.lineage_edges le
        JOIN catalog.assets a ON a.id = le.to_asset_id
        JOIN lineage l ON l.asset_id = le.from_asset_id
        WHERE l.depth < p_depth
    )
    SELECT DISTINCT * FROM lineage ORDER BY depth;
$$ LANGUAGE sql STABLE;

-- Check permission for principal on asset
CREATE OR REPLACE FUNCTION catalog.check_permission(
    p_asset_fqdn TEXT,
    p_principal_key TEXT,
    p_permission TEXT DEFAULT 'read'
)
RETURNS BOOLEAN AS $$
DECLARE
    v_asset_id UUID;
    v_has_permission BOOLEAN := false;
BEGIN
    -- Get asset ID
    SELECT id INTO v_asset_id FROM catalog.assets WHERE fqdn = p_asset_fqdn;
    IF v_asset_id IS NULL THEN
        RETURN false;
    END IF;

    -- Check policies (highest priority wins)
    SELECT
        (permissions ->> p_permission)::boolean INTO v_has_permission
    FROM catalog.policies
    WHERE asset_id = v_asset_id
      AND active = true
      AND (expires_at IS NULL OR expires_at > now())
      AND principal_key = p_principal_key
    ORDER BY priority DESC
    LIMIT 1;

    RETURN COALESCE(v_has_permission, false);
END;
$$ LANGUAGE plpgsql STABLE;


-- -----------------------------------------------------------------------------
-- Views for convenience
-- -----------------------------------------------------------------------------

-- Asset summary view
CREATE OR REPLACE VIEW catalog.v_assets_summary AS
SELECT
    a.id,
    a.fqdn,
    a.asset_type,
    a.system,
    a.title,
    a.owner,
    a.tags,
    a.status,
    a.company_id,
    a.created_at,
    a.updated_at,
    (SELECT COUNT(*) FROM catalog.policies p WHERE p.asset_id = a.id AND p.active) as policy_count,
    (SELECT COUNT(*) FROM catalog.lineage_edges le WHERE le.from_asset_id = a.id OR le.to_asset_id = a.id) as lineage_edge_count
FROM catalog.assets a
WHERE a.status = 'active';

-- Tool summary view
CREATE OR REPLACE VIEW catalog.v_tools_summary AS
SELECT
    t.id,
    t.tool_key,
    t.tool_type,
    t.name,
    t.description,
    t.requires_confirmation,
    t.allowed_roles,
    t.tags,
    (SELECT COUNT(*) FROM catalog.tool_bindings tb WHERE tb.tool_id = t.id AND tb.active) as binding_count
FROM catalog.tools t
WHERE t.active = true;


COMMIT;

-- =============================================================================
-- End Migration: 4500 - Unity Catalog-like Asset Registry
-- =============================================================================
