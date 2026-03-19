-- =============================================================================
-- Migration: 4501 - Catalog Semantic Layer (Open Semantics Interface)
-- Purpose: Semantic models, dimensions, metrics for BI-friendly abstractions
-- Family: 4501 (Catalog/Governance - extends 4500)
--
-- Architecture:
--   - catalog.semantic_models: Business-friendly model definitions
--   - catalog.semantic_dimensions: Categorical attributes for grouping
--   - catalog.semantic_metrics: Aggregated measures with formulas
--   - catalog.semantic_relationships: Joins between models
--   - catalog.semantic_exports: YAML/JSON snapshots for BI tools
--
-- Follows patterns from: dbt Semantic Layer, Cube.js, MetricFlow
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- Enum Types
-- -----------------------------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE catalog.semantic_status AS ENUM (
        'draft',
        'active',
        'deprecated',
        'archived'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE catalog.metric_type AS ENUM (
        'simple',           -- Direct aggregation: SUM(amount)
        'derived',          -- Calculation from other metrics: revenue - cost
        'cumulative',       -- Running total: SUM(amount) OVER (ORDER BY date)
        'ratio',            -- Division: revenue / orders
        'conversion'        -- Funnel conversion rate
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE catalog.aggregation_type AS ENUM (
        'sum',
        'count',
        'count_distinct',
        'avg',
        'min',
        'max',
        'median',
        'percentile'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE catalog.join_type AS ENUM (
        'inner',
        'left',
        'right',
        'full',
        'cross'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE catalog.time_grain AS ENUM (
        'day',
        'week',
        'month',
        'quarter',
        'year',
        'hour',
        'minute'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- -----------------------------------------------------------------------------
-- Semantic Models
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS catalog.semantic_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Link to physical asset
    asset_id UUID NOT NULL REFERENCES catalog.assets(id) ON DELETE CASCADE,

    -- Identity
    name TEXT NOT NULL,                -- Business-friendly name (e.g., "sales")
    label TEXT,                        -- Display label
    description TEXT,

    -- Source definition
    source_type TEXT NOT NULL DEFAULT 'table' CHECK (source_type IN ('table', 'view', 'sql', 'ref')),
    source_ref TEXT,                   -- Table name or SQL query
    primary_key TEXT[],                -- Primary key columns

    -- Time dimension (for time-series analysis)
    time_dimension TEXT,               -- Column name for time
    default_time_grain catalog.time_grain DEFAULT 'day',

    -- Filters
    default_filters JSONB DEFAULT '[]',  -- Array of filter conditions

    -- Status
    status catalog.semantic_status DEFAULT 'draft',
    version INT DEFAULT 1,

    -- Multi-tenancy
    company_id INT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    created_by TEXT,

    UNIQUE (asset_id, name)
);

CREATE INDEX IF NOT EXISTS idx_semantic_models_asset ON catalog.semantic_models (asset_id);
CREATE INDEX IF NOT EXISTS idx_semantic_models_name ON catalog.semantic_models (name);
CREATE INDEX IF NOT EXISTS idx_semantic_models_status ON catalog.semantic_models (status);

COMMENT ON TABLE catalog.semantic_models IS 'Business-friendly semantic model definitions over physical assets';


-- -----------------------------------------------------------------------------
-- Semantic Dimensions
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS catalog.semantic_dimensions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Link to semantic model
    model_id UUID NOT NULL REFERENCES catalog.semantic_models(id) ON DELETE CASCADE,

    -- Identity
    name TEXT NOT NULL,                -- Technical name (e.g., "customer_segment")
    label TEXT,                        -- Display label
    description TEXT,

    -- Definition
    expr TEXT NOT NULL,                -- SQL expression or column name
    data_type TEXT DEFAULT 'string',   -- string, number, date, datetime, boolean

    -- Time dimension properties
    is_time_dimension BOOLEAN DEFAULT false,
    time_grain catalog.time_grain,

    -- Hierarchy (for drill-down)
    hierarchy_level INT,               -- 1 = top level, 2 = next, etc.
    parent_dimension_id UUID REFERENCES catalog.semantic_dimensions(id),

    -- Tags and categories
    tags TEXT[] DEFAULT '{}',
    is_hidden BOOLEAN DEFAULT false,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,

    UNIQUE (model_id, name)
);

CREATE INDEX IF NOT EXISTS idx_semantic_dimensions_model ON catalog.semantic_dimensions (model_id);
CREATE INDEX IF NOT EXISTS idx_semantic_dimensions_time ON catalog.semantic_dimensions (is_time_dimension) WHERE is_time_dimension = true;

COMMENT ON TABLE catalog.semantic_dimensions IS 'Categorical attributes for grouping and filtering in semantic models';


-- -----------------------------------------------------------------------------
-- Semantic Metrics
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS catalog.semantic_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Link to semantic model
    model_id UUID NOT NULL REFERENCES catalog.semantic_models(id) ON DELETE CASCADE,

    -- Identity
    name TEXT NOT NULL,                -- Technical name (e.g., "total_revenue")
    label TEXT,                        -- Display label
    description TEXT,

    -- Definition
    metric_type catalog.metric_type NOT NULL DEFAULT 'simple',
    aggregation catalog.aggregation_type,  -- For simple metrics
    expr TEXT NOT NULL,                -- SQL expression: column name or formula

    -- For derived metrics
    depends_on TEXT[],                 -- Other metric names this depends on
    formula TEXT,                      -- Calculation formula using other metrics

    -- Formatting
    format_string TEXT,                -- e.g., "$#,##0.00", "0.0%"
    unit TEXT,                         -- e.g., "USD", "items", "%"

    -- Constraints
    filters JSONB DEFAULT '[]',        -- Metric-level filters
    time_grains catalog.time_grain[],  -- Allowed time grains

    -- Tags
    tags TEXT[] DEFAULT '{}',
    is_hidden BOOLEAN DEFAULT false,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,

    UNIQUE (model_id, name)
);

CREATE INDEX IF NOT EXISTS idx_semantic_metrics_model ON catalog.semantic_metrics (model_id);
CREATE INDEX IF NOT EXISTS idx_semantic_metrics_type ON catalog.semantic_metrics (metric_type);

COMMENT ON TABLE catalog.semantic_metrics IS 'Aggregated measures with formulas for semantic models';


-- -----------------------------------------------------------------------------
-- Semantic Relationships (Joins)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS catalog.semantic_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Models being joined
    from_model_id UUID NOT NULL REFERENCES catalog.semantic_models(id) ON DELETE CASCADE,
    to_model_id UUID NOT NULL REFERENCES catalog.semantic_models(id) ON DELETE CASCADE,

    -- Identity
    name TEXT NOT NULL,
    description TEXT,

    -- Join definition
    join_type catalog.join_type NOT NULL DEFAULT 'left',
    on_clause TEXT NOT NULL,           -- SQL join condition

    -- Cardinality hints
    from_cardinality TEXT DEFAULT 'many' CHECK (from_cardinality IN ('one', 'many')),
    to_cardinality TEXT DEFAULT 'one' CHECK (to_cardinality IN ('one', 'many')),

    -- Status
    active BOOLEAN DEFAULT true,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,

    UNIQUE (from_model_id, to_model_id, name)
);

CREATE INDEX IF NOT EXISTS idx_semantic_relationships_from ON catalog.semantic_relationships (from_model_id);
CREATE INDEX IF NOT EXISTS idx_semantic_relationships_to ON catalog.semantic_relationships (to_model_id);

COMMENT ON TABLE catalog.semantic_relationships IS 'Join definitions between semantic models';


-- -----------------------------------------------------------------------------
-- Semantic Exports (Snapshots)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS catalog.semantic_exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Link to asset
    asset_id UUID NOT NULL REFERENCES catalog.assets(id) ON DELETE CASCADE,

    -- Export metadata
    model_name TEXT NOT NULL,
    format TEXT NOT NULL CHECK (format IN ('yaml', 'json', 'dbt', 'cube')),
    version TEXT,

    -- Content
    content TEXT NOT NULL,             -- YAML or JSON content
    checksum TEXT,                     -- SHA256 of content

    -- Export context
    exported_by TEXT,
    export_reason TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,

    UNIQUE (asset_id, model_name, format, version)
);

CREATE INDEX IF NOT EXISTS idx_semantic_exports_asset ON catalog.semantic_exports (asset_id);
CREATE INDEX IF NOT EXISTS idx_semantic_exports_model ON catalog.semantic_exports (model_name);

COMMENT ON TABLE catalog.semantic_exports IS 'YAML/JSON snapshots for BI tool interoperability';


-- -----------------------------------------------------------------------------
-- Updated At Triggers
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_semantic_models_updated ON catalog.semantic_models;
CREATE TRIGGER trg_semantic_models_updated
    BEFORE UPDATE ON catalog.semantic_models
    FOR EACH ROW
    EXECUTE FUNCTION catalog.set_updated_at();

DROP TRIGGER IF EXISTS trg_semantic_dimensions_updated ON catalog.semantic_dimensions;
CREATE TRIGGER trg_semantic_dimensions_updated
    BEFORE UPDATE ON catalog.semantic_dimensions
    FOR EACH ROW
    EXECUTE FUNCTION catalog.set_updated_at();

DROP TRIGGER IF EXISTS trg_semantic_metrics_updated ON catalog.semantic_metrics;
CREATE TRIGGER trg_semantic_metrics_updated
    BEFORE UPDATE ON catalog.semantic_metrics
    FOR EACH ROW
    EXECUTE FUNCTION catalog.set_updated_at();

DROP TRIGGER IF EXISTS trg_semantic_relationships_updated ON catalog.semantic_relationships;
CREATE TRIGGER trg_semantic_relationships_updated
    BEFORE UPDATE ON catalog.semantic_relationships
    FOR EACH ROW
    EXECUTE FUNCTION catalog.set_updated_at();


-- -----------------------------------------------------------------------------
-- Row Level Security
-- -----------------------------------------------------------------------------
ALTER TABLE catalog.semantic_models ENABLE ROW LEVEL SECURITY;
ALTER TABLE catalog.semantic_dimensions ENABLE ROW LEVEL SECURITY;
ALTER TABLE catalog.semantic_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE catalog.semantic_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE catalog.semantic_exports ENABLE ROW LEVEL SECURITY;

-- Semantic Models: Inherit from parent asset
DROP POLICY IF EXISTS "semantic_models_access" ON catalog.semantic_models;
CREATE POLICY "semantic_models_access" ON catalog.semantic_models FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM catalog.assets a
            WHERE a.id = catalog.semantic_models.asset_id
            AND (
                a.company_id IS NULL
                OR a.company_id = (current_setting('app.current_company_id', true)::int)
                OR auth.jwt() ->> 'role' = 'service_role'
            )
        )
    );

-- Dimensions: Inherit from parent model
DROP POLICY IF EXISTS "semantic_dimensions_access" ON catalog.semantic_dimensions;
CREATE POLICY "semantic_dimensions_access" ON catalog.semantic_dimensions FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM catalog.semantic_models m
            JOIN catalog.assets a ON a.id = m.asset_id
            WHERE m.id = catalog.semantic_dimensions.model_id
            AND (
                a.company_id IS NULL
                OR a.company_id = (current_setting('app.current_company_id', true)::int)
                OR auth.jwt() ->> 'role' = 'service_role'
            )
        )
    );

-- Metrics: Inherit from parent model
DROP POLICY IF EXISTS "semantic_metrics_access" ON catalog.semantic_metrics;
CREATE POLICY "semantic_metrics_access" ON catalog.semantic_metrics FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM catalog.semantic_models m
            JOIN catalog.assets a ON a.id = m.asset_id
            WHERE m.id = catalog.semantic_metrics.model_id
            AND (
                a.company_id IS NULL
                OR a.company_id = (current_setting('app.current_company_id', true)::int)
                OR auth.jwt() ->> 'role' = 'service_role'
            )
        )
    );

-- Relationships: Inherit from either model
DROP POLICY IF EXISTS "semantic_relationships_access" ON catalog.semantic_relationships;
CREATE POLICY "semantic_relationships_access" ON catalog.semantic_relationships FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM catalog.semantic_models m
            JOIN catalog.assets a ON a.id = m.asset_id
            WHERE (m.id = catalog.semantic_relationships.from_model_id OR m.id = catalog.semantic_relationships.to_model_id)
            AND (
                a.company_id IS NULL
                OR a.company_id = (current_setting('app.current_company_id', true)::int)
                OR auth.jwt() ->> 'role' = 'service_role'
            )
        )
    );

-- Exports: Inherit from parent asset
DROP POLICY IF EXISTS "semantic_exports_access" ON catalog.semantic_exports;
CREATE POLICY "semantic_exports_access" ON catalog.semantic_exports FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM catalog.assets a
            WHERE a.id = catalog.semantic_exports.asset_id
            AND (
                a.company_id IS NULL
                OR a.company_id = (current_setting('app.current_company_id', true)::int)
                OR auth.jwt() ->> 'role' = 'service_role'
            )
        )
    );


-- -----------------------------------------------------------------------------
-- Helper Functions
-- -----------------------------------------------------------------------------

-- Get semantic model with all dimensions and metrics
CREATE OR REPLACE FUNCTION catalog.get_semantic_model(p_asset_fqdn TEXT, p_model_name TEXT)
RETURNS JSONB AS $$
DECLARE
    v_result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'model', jsonb_build_object(
            'id', m.id,
            'name', m.name,
            'label', m.label,
            'description', m.description,
            'source_type', m.source_type,
            'source_ref', m.source_ref,
            'primary_key', m.primary_key,
            'time_dimension', m.time_dimension,
            'default_time_grain', m.default_time_grain,
            'status', m.status
        ),
        'dimensions', (
            SELECT COALESCE(jsonb_agg(jsonb_build_object(
                'name', d.name,
                'label', d.label,
                'description', d.description,
                'expr', d.expr,
                'data_type', d.data_type,
                'is_time_dimension', d.is_time_dimension,
                'time_grain', d.time_grain,
                'tags', d.tags
            ) ORDER BY d.is_time_dimension DESC, d.name), '[]'::jsonb)
            FROM catalog.semantic_dimensions d
            WHERE d.model_id = m.id AND NOT d.is_hidden
        ),
        'metrics', (
            SELECT COALESCE(jsonb_agg(jsonb_build_object(
                'name', mt.name,
                'label', mt.label,
                'description', mt.description,
                'metric_type', mt.metric_type,
                'aggregation', mt.aggregation,
                'expr', mt.expr,
                'formula', mt.formula,
                'format_string', mt.format_string,
                'unit', mt.unit,
                'tags', mt.tags
            ) ORDER BY mt.name), '[]'::jsonb)
            FROM catalog.semantic_metrics mt
            WHERE mt.model_id = m.id AND NOT mt.is_hidden
        ),
        'relationships', (
            SELECT COALESCE(jsonb_agg(jsonb_build_object(
                'name', r.name,
                'to_model', tm.name,
                'join_type', r.join_type,
                'on_clause', r.on_clause,
                'cardinality', r.from_cardinality || '-to-' || r.to_cardinality
            )), '[]'::jsonb)
            FROM catalog.semantic_relationships r
            JOIN catalog.semantic_models tm ON tm.id = r.to_model_id
            WHERE r.from_model_id = m.id AND r.active
        )
    ) INTO v_result
    FROM catalog.semantic_models m
    JOIN catalog.assets a ON a.id = m.asset_id
    WHERE a.fqdn = p_asset_fqdn
      AND m.name = p_model_name
      AND m.status = 'active';

    RETURN COALESCE(v_result, '{}'::jsonb);
END;
$$ LANGUAGE plpgsql STABLE;


-- Resolve a semantic query to SQL
CREATE OR REPLACE FUNCTION catalog.resolve_semantic_query(
    p_asset_fqdn TEXT,
    p_model_name TEXT,
    p_dimensions TEXT[],
    p_metrics TEXT[],
    p_filters JSONB DEFAULT '[]',
    p_time_grain catalog.time_grain DEFAULT NULL,
    p_limit INT DEFAULT 1000
)
RETURNS JSONB AS $$
DECLARE
    v_model RECORD;
    v_dims TEXT[] := '{}';
    v_mets TEXT[] := '{}';
    v_sql TEXT;
    v_select_parts TEXT[] := '{}';
    v_group_parts TEXT[] := '{}';
    v_result JSONB;
BEGIN
    -- Get model
    SELECT m.*, a.fqdn as asset_fqdn
    INTO v_model
    FROM catalog.semantic_models m
    JOIN catalog.assets a ON a.id = m.asset_id
    WHERE a.fqdn = p_asset_fqdn
      AND m.name = p_model_name
      AND m.status = 'active';

    IF v_model IS NULL THEN
        RETURN jsonb_build_object('ok', false, 'error', 'Semantic model not found');
    END IF;

    -- Resolve dimensions
    FOR i IN 1..array_length(p_dimensions, 1) LOOP
        SELECT array_append(v_select_parts, d.expr || ' AS ' || d.name),
               array_append(v_group_parts, d.expr)
        INTO v_select_parts, v_group_parts
        FROM catalog.semantic_dimensions d
        WHERE d.model_id = v_model.id AND d.name = p_dimensions[i];
    END LOOP;

    -- Resolve metrics
    FOR i IN 1..array_length(p_metrics, 1) LOOP
        SELECT array_append(v_select_parts,
            CASE mt.metric_type
                WHEN 'simple' THEN mt.aggregation || '(' || mt.expr || ')'
                WHEN 'derived' THEN mt.formula
                ELSE mt.expr
            END || ' AS ' || mt.name)
        INTO v_select_parts
        FROM catalog.semantic_metrics mt
        WHERE mt.model_id = v_model.id AND mt.name = p_metrics[i];
    END LOOP;

    -- Build SQL (for query plan, not execution)
    v_sql := format(
        'SELECT %s FROM %s %s %s LIMIT %s',
        array_to_string(v_select_parts, ', '),
        v_model.source_ref,
        CASE WHEN array_length(v_group_parts, 1) > 0
             THEN 'GROUP BY ' || array_to_string(v_group_parts, ', ')
             ELSE '' END,
        '', -- WHERE clause from filters (simplified)
        p_limit
    );

    RETURN jsonb_build_object(
        'ok', true,
        'model', v_model.name,
        'asset_fqdn', v_model.asset_fqdn,
        'dimensions', p_dimensions,
        'metrics', p_metrics,
        'sql_preview', v_sql,
        'note', 'Query execution intentionally not implemented - use BI tool connector'
    );
END;
$$ LANGUAGE plpgsql STABLE;


-- Create lineage edge from physical asset to semantic model
CREATE OR REPLACE FUNCTION catalog.create_semantic_lineage(
    p_asset_fqdn TEXT,
    p_model_name TEXT
)
RETURNS UUID AS $$
DECLARE
    v_asset_id UUID;
    v_model_asset_id UUID;
    v_edge_id UUID;
BEGIN
    -- Get physical asset ID
    SELECT id INTO v_asset_id FROM catalog.assets WHERE fqdn = p_asset_fqdn;
    IF v_asset_id IS NULL THEN
        RAISE EXCEPTION 'Asset not found: %', p_asset_fqdn;
    END IF;

    -- Create semantic model asset if not exists
    INSERT INTO catalog.assets (
        fqdn,
        asset_type,
        system,
        title,
        description,
        tags
    )
    VALUES (
        p_asset_fqdn || '.semantic.' || p_model_name,
        'model',
        'scout',
        'Semantic: ' || p_model_name,
        'Semantic model over ' || p_asset_fqdn,
        ARRAY['semantic', 'model', p_model_name]
    )
    ON CONFLICT (fqdn) DO UPDATE SET updated_at = now()
    RETURNING id INTO v_model_asset_id;

    -- Create lineage edge: physical -> semantic
    INSERT INTO catalog.lineage_edges (
        from_asset_id,
        to_asset_id,
        edge_type,
        job_name
    )
    VALUES (
        v_asset_id,
        v_model_asset_id,
        'derived_from',
        'semantic_model_definition'
    )
    ON CONFLICT (from_asset_id, to_asset_id, edge_type) DO NOTHING
    RETURNING id INTO v_edge_id;

    RETURN v_edge_id;
END;
$$ LANGUAGE plpgsql;


-- Export semantic model to YAML format
CREATE OR REPLACE FUNCTION catalog.export_semantic_yaml(
    p_asset_fqdn TEXT,
    p_model_name TEXT
)
RETURNS TEXT AS $$
DECLARE
    v_model JSONB;
    v_yaml TEXT;
    v_dim JSONB;
    v_met JSONB;
BEGIN
    v_model := catalog.get_semantic_model(p_asset_fqdn, p_model_name);

    IF v_model = '{}'::jsonb THEN
        RETURN NULL;
    END IF;

    -- Build YAML manually (simplified)
    v_yaml := E'# Open Semantics Interface (OSI) Export\n';
    v_yaml := v_yaml || E'# Asset: ' || p_asset_fqdn || E'\n';
    v_yaml := v_yaml || E'# Generated: ' || now()::text || E'\n\n';

    v_yaml := v_yaml || E'model:\n';
    v_yaml := v_yaml || E'  name: ' || (v_model->'model'->>'name') || E'\n';
    v_yaml := v_yaml || E'  label: ' || COALESCE(v_model->'model'->>'label', v_model->'model'->>'name') || E'\n';
    v_yaml := v_yaml || E'  description: ' || COALESCE(v_model->'model'->>'description', '') || E'\n';
    v_yaml := v_yaml || E'  source: ' || COALESCE(v_model->'model'->>'source_ref', '') || E'\n';

    IF v_model->'model'->>'time_dimension' IS NOT NULL THEN
        v_yaml := v_yaml || E'  time_dimension: ' || (v_model->'model'->>'time_dimension') || E'\n';
    END IF;

    -- Dimensions
    v_yaml := v_yaml || E'\ndimensions:\n';
    FOR v_dim IN SELECT * FROM jsonb_array_elements(v_model->'dimensions')
    LOOP
        v_yaml := v_yaml || E'  - name: ' || (v_dim->>'name') || E'\n';
        v_yaml := v_yaml || E'    expr: ' || (v_dim->>'expr') || E'\n';
        v_yaml := v_yaml || E'    type: ' || COALESCE(v_dim->>'data_type', 'string') || E'\n';
        IF (v_dim->>'is_time_dimension')::boolean THEN
            v_yaml := v_yaml || E'    is_time_dimension: true\n';
        END IF;
    END LOOP;

    -- Metrics
    v_yaml := v_yaml || E'\nmetrics:\n';
    FOR v_met IN SELECT * FROM jsonb_array_elements(v_model->'metrics')
    LOOP
        v_yaml := v_yaml || E'  - name: ' || (v_met->>'name') || E'\n';
        v_yaml := v_yaml || E'    type: ' || (v_met->>'metric_type') || E'\n';
        IF v_met->>'aggregation' IS NOT NULL THEN
            v_yaml := v_yaml || E'    aggregation: ' || (v_met->>'aggregation') || E'\n';
        END IF;
        v_yaml := v_yaml || E'    expr: ' || (v_met->>'expr') || E'\n';
        IF v_met->>'formula' IS NOT NULL THEN
            v_yaml := v_yaml || E'    formula: ' || (v_met->>'formula') || E'\n';
        END IF;
    END LOOP;

    RETURN v_yaml;
END;
$$ LANGUAGE plpgsql STABLE;


-- -----------------------------------------------------------------------------
-- Views
-- -----------------------------------------------------------------------------

-- Semantic models summary
CREATE OR REPLACE VIEW catalog.v_semantic_models AS
SELECT
    m.id,
    m.name,
    m.label,
    m.description,
    a.fqdn as asset_fqdn,
    a.title as asset_title,
    m.source_type,
    m.source_ref,
    m.time_dimension,
    m.status,
    m.created_at,
    (SELECT COUNT(*) FROM catalog.semantic_dimensions d WHERE d.model_id = m.id) as dimension_count,
    (SELECT COUNT(*) FROM catalog.semantic_metrics mt WHERE mt.model_id = m.id) as metric_count
FROM catalog.semantic_models m
JOIN catalog.assets a ON a.id = m.asset_id;


COMMIT;

-- =============================================================================
-- End Migration: 4501 - Catalog Semantic Layer
-- =============================================================================
