-- =============================================================================
-- DOCS PLATFORM: TAXONOMY SCHEMA
-- =============================================================================
-- SAP-grade documentation platform taxonomy structure
-- Provides hierarchical browsing, document metadata, and related docs graph
-- =============================================================================

-- Enable ltree extension for hierarchical paths
CREATE EXTENSION IF NOT EXISTS ltree;

-- Create docs schema
CREATE SCHEMA IF NOT EXISTS docs;

-- =============================================================================
-- TAXONOMY NODES (Hierarchical Topic Tree)
-- =============================================================================

CREATE TABLE docs.taxonomy_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES docs.taxonomy_nodes(id) ON DELETE RESTRICT,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    icon TEXT,  -- Optional icon identifier
    path LTREE NOT NULL,
    depth INTEGER NOT NULL DEFAULT 0,
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_visible BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT slug_format CHECK (slug ~ '^[a-z0-9][a-z0-9-]*[a-z0-9]$' OR slug ~ '^[a-z0-9]$')
);

-- Index for tree traversal
CREATE INDEX idx_taxonomy_nodes_path ON docs.taxonomy_nodes USING GIST (path);
CREATE INDEX idx_taxonomy_nodes_parent ON docs.taxonomy_nodes(parent_id);
CREATE INDEX idx_taxonomy_nodes_depth ON docs.taxonomy_nodes(depth);
CREATE INDEX idx_taxonomy_nodes_visible ON docs.taxonomy_nodes(is_visible) WHERE is_visible = true;

-- Trigger to maintain depth from path
CREATE OR REPLACE FUNCTION docs.taxonomy_update_depth()
RETURNS TRIGGER AS $$
BEGIN
    NEW.depth := nlevel(NEW.path) - 1;
    NEW.updated_at := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_taxonomy_depth
    BEFORE INSERT OR UPDATE ON docs.taxonomy_nodes
    FOR EACH ROW EXECUTE FUNCTION docs.taxonomy_update_depth();

-- =============================================================================
-- DOCUMENT METADATA
-- =============================================================================

CREATE TABLE docs.doc_metadata (
    doc_id UUID PRIMARY KEY,  -- References rag.documents(id) if exists
    product TEXT NOT NULL,
    content_type TEXT NOT NULL,
    release_channel TEXT NOT NULL DEFAULT 'stable',
    version TEXT,
    is_breaking BOOLEAN NOT NULL DEFAULT false,
    is_deprecated BOOLEAN NOT NULL DEFAULT false,
    successor_id UUID REFERENCES docs.doc_metadata(doc_id),
    glossary_terms TEXT[] DEFAULT '{}',
    orphan_flag BOOLEAN NOT NULL DEFAULT false,
    featured BOOLEAN NOT NULL DEFAULT false,
    last_reviewed_at TIMESTAMPTZ,
    last_reviewed_by TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT valid_release_channel CHECK (release_channel IN ('edge', 'stable', 'lts', 'deprecated')),
    CONSTRAINT valid_content_type CHECK (content_type IN ('guide', 'reference', 'tutorial', 'api', 'faq', 'changelog', 'migration'))
);

-- Index for faceted search
CREATE INDEX idx_doc_metadata_product ON docs.doc_metadata(product);
CREATE INDEX idx_doc_metadata_type ON docs.doc_metadata(content_type);
CREATE INDEX idx_doc_metadata_channel ON docs.doc_metadata(release_channel);
CREATE INDEX idx_doc_metadata_glossary ON docs.doc_metadata USING GIN (glossary_terms);
CREATE INDEX idx_doc_metadata_current ON docs.doc_metadata(product, content_type)
    WHERE is_deprecated = false AND orphan_flag = false;

-- =============================================================================
-- DOCUMENT-TAXONOMY MAPPING (Many-to-Many)
-- =============================================================================

CREATE TABLE docs.doc_taxonomy (
    doc_id UUID NOT NULL,
    taxonomy_id UUID NOT NULL REFERENCES docs.taxonomy_nodes(id) ON DELETE CASCADE,
    is_primary BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (doc_id, taxonomy_id)
);

-- Index for browse queries
CREATE INDEX idx_doc_taxonomy_taxonomy ON docs.doc_taxonomy(taxonomy_id);
CREATE INDEX idx_doc_taxonomy_primary ON docs.doc_taxonomy(taxonomy_id) WHERE is_primary = true;

-- Ensure only one primary taxonomy per document
CREATE UNIQUE INDEX idx_doc_taxonomy_one_primary
    ON docs.doc_taxonomy(doc_id) WHERE is_primary = true;

-- =============================================================================
-- RELATED DOCUMENTS GRAPH
-- =============================================================================

CREATE TABLE docs.related_docs (
    source_id UUID NOT NULL,
    target_id UUID NOT NULL,
    relationship TEXT NOT NULL,
    weight FLOAT NOT NULL DEFAULT 1.0,
    bidirectional BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (source_id, target_id, relationship),

    CONSTRAINT valid_relationship CHECK (relationship IN (
        'prerequisite',   -- Target must be read before source
        'see_also',       -- Related topic
        'supersedes',     -- Source replaces target
        'example_of',     -- Source is example of target concept
        'contradicts',    -- Documents have conflicting info (trigger review)
        'implements',     -- Source implements target specification
        'extends'         -- Source extends target functionality
    )),
    CONSTRAINT valid_weight CHECK (weight >= 0.0 AND weight <= 1.0),
    CONSTRAINT no_self_reference CHECK (source_id != target_id)
);

-- Index for graph traversal
CREATE INDEX idx_related_docs_source ON docs.related_docs(source_id);
CREATE INDEX idx_related_docs_target ON docs.related_docs(target_id);
CREATE INDEX idx_related_docs_relationship ON docs.related_docs(relationship);

-- =============================================================================
-- TAXONOMY AUDIT LOG
-- =============================================================================

CREATE TABLE docs.taxonomy_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    taxonomy_id UUID,  -- May be null if deleted
    action TEXT NOT NULL,
    old_value JSONB,
    new_value JSONB,
    changed_by TEXT,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT valid_action CHECK (action IN ('INSERT', 'UPDATE', 'DELETE'))
);

CREATE INDEX idx_taxonomy_audit_node ON docs.taxonomy_audit(taxonomy_id);
CREATE INDEX idx_taxonomy_audit_time ON docs.taxonomy_audit(changed_at DESC);

-- Audit trigger
CREATE OR REPLACE FUNCTION docs.taxonomy_audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO docs.taxonomy_audit (taxonomy_id, action, old_value, changed_by)
        VALUES (OLD.id, 'DELETE', to_jsonb(OLD), current_user);
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO docs.taxonomy_audit (taxonomy_id, action, old_value, new_value, changed_by)
        VALUES (NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), current_user);
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO docs.taxonomy_audit (taxonomy_id, action, new_value, changed_by)
        VALUES (NEW.id, 'INSERT', to_jsonb(NEW), current_user);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_taxonomy_audit
    AFTER INSERT OR UPDATE OR DELETE ON docs.taxonomy_nodes
    FOR EACH ROW EXECUTE FUNCTION docs.taxonomy_audit_trigger();

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Get full taxonomy path as breadcrumb
CREATE OR REPLACE FUNCTION docs.get_taxonomy_breadcrumb(node_id UUID)
RETURNS TABLE(id UUID, slug TEXT, title TEXT, depth INTEGER) AS $$
BEGIN
    RETURN QUERY
    WITH node AS (
        SELECT path FROM docs.taxonomy_nodes WHERE docs.taxonomy_nodes.id = node_id
    )
    SELECT tn.id, tn.slug, tn.title, tn.depth
    FROM docs.taxonomy_nodes tn, node
    WHERE tn.path @> node.path OR tn.path = node.path
    ORDER BY tn.depth;
END;
$$ LANGUAGE plpgsql STABLE;

-- Get documents for a taxonomy node and its children
CREATE OR REPLACE FUNCTION docs.get_taxonomy_docs(
    node_id UUID,
    include_children BOOLEAN DEFAULT true
)
RETURNS TABLE(doc_id UUID, is_primary BOOLEAN) AS $$
BEGIN
    IF include_children THEN
        RETURN QUERY
        SELECT dt.doc_id, dt.is_primary
        FROM docs.doc_taxonomy dt
        JOIN docs.taxonomy_nodes tn ON tn.id = dt.taxonomy_id
        WHERE tn.path <@ (SELECT path FROM docs.taxonomy_nodes WHERE id = node_id);
    ELSE
        RETURN QUERY
        SELECT dt.doc_id, dt.is_primary
        FROM docs.doc_taxonomy dt
        WHERE dt.taxonomy_id = node_id;
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;

-- Count documents per taxonomy node
CREATE OR REPLACE FUNCTION docs.taxonomy_doc_counts()
RETURNS TABLE(taxonomy_id UUID, doc_count BIGINT, child_doc_count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT
        tn.id as taxonomy_id,
        COUNT(DISTINCT dt.doc_id) FILTER (WHERE dt.taxonomy_id = tn.id) as doc_count,
        COUNT(DISTINCT dt.doc_id) as child_doc_count
    FROM docs.taxonomy_nodes tn
    LEFT JOIN docs.taxonomy_nodes children ON children.path <@ tn.path
    LEFT JOIN docs.doc_taxonomy dt ON dt.taxonomy_id = children.id
    GROUP BY tn.id;
END;
$$ LANGUAGE plpgsql STABLE;

-- =============================================================================
-- SEED INITIAL TAXONOMY
-- =============================================================================

-- Root nodes
INSERT INTO docs.taxonomy_nodes (id, slug, title, description, path, sort_order) VALUES
    ('10000000-0000-0000-0000-000000000001', 'odoo-ce', 'Odoo CE', 'Core Odoo Community Edition documentation', 'odoo_ce', 1),
    ('10000000-0000-0000-0000-000000000002', 'oca', 'OCA Addons', 'Odoo Community Association modules', 'oca', 2),
    ('10000000-0000-0000-0000-000000000003', 'platform', 'Platform', 'Infrastructure and platform documentation', 'platform', 3),
    ('10000000-0000-0000-0000-000000000004', 'integrations', 'Integrations', 'Third-party integrations and connectors', 'integrations', 4);

-- Odoo CE L2 nodes
INSERT INTO docs.taxonomy_nodes (parent_id, slug, title, description, path, sort_order) VALUES
    ('10000000-0000-0000-0000-000000000001', 'odoo-modules', 'Modules', 'Core Odoo module documentation', 'odoo_ce.modules', 1),
    ('10000000-0000-0000-0000-000000000001', 'odoo-development', 'Development', 'Odoo development guides', 'odoo_ce.development', 2),
    ('10000000-0000-0000-0000-000000000001', 'odoo-deployment', 'Deployment', 'Odoo deployment and operations', 'odoo_ce.deployment', 3);

-- Odoo Modules L3 nodes
INSERT INTO docs.taxonomy_nodes (parent_id, slug, title, path, sort_order)
SELECT
    (SELECT id FROM docs.taxonomy_nodes WHERE slug = 'odoo-modules'),
    slug,
    title,
    'odoo_ce.modules.' || REPLACE(slug, '-', '_'),
    sort_order
FROM (VALUES
    ('sale', 'Sales', 1),
    ('purchase', 'Purchase', 2),
    ('inventory', 'Inventory', 3),
    ('accounting', 'Accounting', 4),
    ('hr', 'Human Resources', 5),
    ('crm', 'CRM', 6),
    ('project', 'Project', 7),
    ('manufacturing', 'Manufacturing', 8)
) AS modules(slug, title, sort_order);

-- Development L3 nodes
INSERT INTO docs.taxonomy_nodes (parent_id, slug, title, path, sort_order)
SELECT
    (SELECT id FROM docs.taxonomy_nodes WHERE slug = 'odoo-development'),
    slug,
    title,
    'odoo_ce.development.' || REPLACE(slug, '-', '_'),
    sort_order
FROM (VALUES
    ('orm', 'ORM', 1),
    ('views', 'Views & Forms', 2),
    ('actions', 'Actions', 3),
    ('security', 'Security', 4),
    ('api', 'API', 5),
    ('testing', 'Testing', 6)
) AS dev(slug, title, sort_order);

-- Platform L2 nodes
INSERT INTO docs.taxonomy_nodes (parent_id, slug, title, path, sort_order)
SELECT
    '10000000-0000-0000-0000-000000000003',
    slug,
    title,
    'platform.' || REPLACE(slug, '-', '_'),
    sort_order
FROM (VALUES
    ('architecture', 'Architecture', 1),
    ('api-reference', 'API Reference', 2),
    ('data-pipeline', 'Data Pipeline', 3),
    ('security-compliance', 'Security & Compliance', 4)
) AS plat(slug, title, sort_order);

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Docs taxonomy schema created with % nodes',
        (SELECT COUNT(*) FROM docs.taxonomy_nodes);
END;
$$;
