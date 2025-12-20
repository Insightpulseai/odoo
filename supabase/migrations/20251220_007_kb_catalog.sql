-- =============================================================================
-- KNOWLEDGE HUB: CATALOG / TAXONOMY TREE + COVERAGE LEDGER
-- =============================================================================
-- Provides the "site map + completeness tracking" layer so hierarchical docs
-- (Odoo docs, SAP Help Portal, OCA repos) don't collapse into an unstructured blob.
--
-- Three tables:
-- - kb.catalog_sources: Top-level sources (odoo_docs, sap_help, oca, etc.)
-- - kb.catalog_nodes: Hierarchical tree (space/section/app/product/page)
-- - kb.harvest_state: Coverage ledger (queued/running/ok/error/stale/skipped)
--
-- A category is "covered" when all 3 are true:
-- 1. Discoverable: exists as a node in the taxonomy tree
-- 2. Ingested: has at least 1 artifact version (or crawl job queued)
-- 3. Queryable: produces chunks/embeddings with tenant-safe lineage
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS kb;

-- =============================================================================
-- CATALOG SOURCES
-- =============================================================================
-- A source = "odoo_docs", "sap_help", "oca", "github_repo", "odoo_attachments"

CREATE TABLE IF NOT EXISTS kb.catalog_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    code TEXT NOT NULL,                   -- e.g. 'odoo_docs', 'sap_help'
    name TEXT NOT NULL,
    base_url TEXT,
    description TEXT,
    priority INTEGER NOT NULL DEFAULT 0,  -- Higher = process first
    is_active BOOLEAN NOT NULL DEFAULT true,
    config JSONB NOT NULL DEFAULT '{}'::jsonb,  -- Source-specific config
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_source_code UNIQUE (tenant_id, code)
);

CREATE INDEX idx_catalog_sources_tenant ON kb.catalog_sources(tenant_id);
CREATE INDEX idx_catalog_sources_active ON kb.catalog_sources(tenant_id, is_active)
    WHERE is_active = true;

-- =============================================================================
-- CATALOG NODES
-- =============================================================================
-- A node = any entry in the tree: space/section/category/product/page
-- Odoo's doc nav and SAP's product tree are fundamentally hierarchies, not documents.
-- This keeps the hierarchy separate from content, while still letting you bind
-- nodes to kb.artifacts when you ingest.

CREATE TABLE IF NOT EXISTS kb.catalog_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    source_id UUID NOT NULL REFERENCES kb.catalog_sources(id) ON DELETE CASCADE,
    parent_id UUID REFERENCES kb.catalog_nodes(id) ON DELETE CASCADE,

    kind TEXT NOT NULL,                   -- 'space'|'section'|'app'|'product'|'page'|'portfolio'|'category'
    title TEXT NOT NULL,
    slug TEXT NOT NULL,                   -- Stable identifier in-tree
    external_url TEXT,                    -- Canonical URL for crawls
    sort_order INTEGER NOT NULL DEFAULT 0,
    depth INTEGER NOT NULL DEFAULT 0,     -- Pre-computed depth for queries

    -- Binding to existing KB artifacts (optional but powerful)
    artifact_id UUID REFERENCES kb.artifacts(id) ON DELETE SET NULL,

    -- Crawl configuration
    crawl_depth INTEGER DEFAULT 3,        -- How deep to crawl from this node
    is_leaf BOOLEAN NOT NULL DEFAULT false,  -- True if this is a crawlable page
    should_harvest BOOLEAN NOT NULL DEFAULT true,  -- False to skip harvesting

    meta JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_node_slug UNIQUE (tenant_id, source_id, slug),
    CONSTRAINT valid_kind CHECK (kind IN (
        'space', 'section', 'app', 'product', 'page',
        'portfolio', 'category', 'module', 'repo'
    ))
);

CREATE INDEX idx_catalog_nodes_tenant ON kb.catalog_nodes(tenant_id);
CREATE INDEX idx_catalog_nodes_source ON kb.catalog_nodes(source_id);
CREATE INDEX idx_catalog_nodes_parent ON kb.catalog_nodes(parent_id);
CREATE INDEX idx_catalog_nodes_kind ON kb.catalog_nodes(kind);
CREATE INDEX idx_catalog_nodes_artifact ON kb.catalog_nodes(artifact_id);
CREATE INDEX idx_catalog_nodes_depth ON kb.catalog_nodes(source_id, depth);
CREATE INDEX idx_catalog_nodes_harvest ON kb.catalog_nodes(tenant_id, should_harvest)
    WHERE should_harvest = true;

-- =============================================================================
-- HARVEST STATE (Coverage Ledger)
-- =============================================================================
-- One row per node that should be harvested. Tracks:
-- - Status: queued/running/ok/error/stale/skipped
-- - Content identity (hash) to detect changes without re-embedding
-- - Link to version for lineage

CREATE TABLE IF NOT EXISTS kb.harvest_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    node_id UUID NOT NULL REFERENCES kb.catalog_nodes(id) ON DELETE CASCADE,

    status TEXT NOT NULL DEFAULT 'queued',  -- queued|running|ok|error|stale|skipped
    status_reason TEXT,                     -- Human-readable reason for status

    -- Timing
    queued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    last_run_at TIMESTAMPTZ,
    last_ok_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,                -- For scheduled refreshes

    -- Error tracking
    last_error TEXT,
    error_count INTEGER NOT NULL DEFAULT 0,
    consecutive_errors INTEGER NOT NULL DEFAULT 0,

    -- Content identity (detect changes without re-embedding)
    last_content_hash TEXT,
    last_etag TEXT,                         -- HTTP ETag for efficient polling
    last_modified TIMESTAMPTZ,              -- HTTP Last-Modified

    -- Lineage
    last_version_id UUID REFERENCES kb.versions(id) ON DELETE SET NULL,
    chunk_count INTEGER DEFAULT 0,          -- Chunks produced from this node
    embedding_count INTEGER DEFAULT 0,      -- Embeddings produced

    -- Metrics
    fetch_duration_ms INTEGER,
    process_duration_ms INTEGER,
    bytes_fetched BIGINT,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_harvest_node UNIQUE (tenant_id, node_id),
    CONSTRAINT valid_status CHECK (status IN (
        'queued', 'running', 'ok', 'error', 'stale', 'skipped'
    ))
);

CREATE INDEX idx_harvest_tenant ON kb.harvest_state(tenant_id);
CREATE INDEX idx_harvest_node ON kb.harvest_state(node_id);
CREATE INDEX idx_harvest_status ON kb.harvest_state(status);
CREATE INDEX idx_harvest_pending ON kb.harvest_state(tenant_id, status)
    WHERE status IN ('queued', 'running');
CREATE INDEX idx_harvest_problems ON kb.harvest_state(tenant_id, status)
    WHERE status IN ('error', 'stale');
CREATE INDEX idx_harvest_next_run ON kb.harvest_state(next_run_at)
    WHERE next_run_at IS NOT NULL;

-- =============================================================================
-- ROW LEVEL SECURITY
-- =============================================================================

ALTER TABLE kb.catalog_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb.catalog_nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb.harvest_state ENABLE ROW LEVEL SECURITY;

-- Catalog sources
CREATE POLICY catalog_sources_tenant_isolation ON kb.catalog_sources
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

CREATE POLICY catalog_sources_insert ON kb.catalog_sources
    FOR INSERT WITH CHECK (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Catalog nodes
CREATE POLICY catalog_nodes_tenant_isolation ON kb.catalog_nodes
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

CREATE POLICY catalog_nodes_insert ON kb.catalog_nodes
    FOR INSERT WITH CHECK (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Harvest state
CREATE POLICY harvest_state_tenant_isolation ON kb.harvest_state
    USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

CREATE POLICY harvest_state_insert ON kb.harvest_state
    FOR INSERT WITH CHECK (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- =============================================================================
-- COVERAGE STATS VIEW
-- =============================================================================
-- Aggregate view for answering "are we covered?" with a single query

CREATE OR REPLACE VIEW kb.coverage_stats AS
SELECT
    cn.tenant_id,
    cs.code AS source_code,
    cs.name AS source_name,
    cn.kind,
    COUNT(*) AS total_nodes,
    COUNT(*) FILTER (WHERE hs.status = 'ok') AS ok_nodes,
    COUNT(*) FILTER (WHERE hs.status IN ('queued', 'running')) AS pending_nodes,
    COUNT(*) FILTER (WHERE hs.status = 'error') AS error_nodes,
    COUNT(*) FILTER (WHERE hs.status = 'stale') AS stale_nodes,
    COUNT(*) FILTER (WHERE hs.status = 'skipped') AS skipped_nodes,
    COUNT(*) FILTER (WHERE hs.status IS NULL) AS untracked_nodes,
    COALESCE(SUM(hs.chunk_count), 0) AS total_chunks,
    COALESCE(SUM(hs.embedding_count), 0) AS total_embeddings,
    MAX(hs.last_ok_at) AS last_ok_at,
    MIN(hs.next_run_at) FILTER (WHERE hs.status = 'queued') AS next_scheduled
FROM kb.catalog_nodes cn
JOIN kb.catalog_sources cs ON cs.id = cn.source_id
LEFT JOIN kb.harvest_state hs ON hs.node_id = cn.id AND hs.tenant_id = cn.tenant_id
WHERE cn.should_harvest = true
GROUP BY cn.tenant_id, cs.code, cs.name, cn.kind;

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Get tree for a source (with depth-first ordering)
CREATE OR REPLACE FUNCTION kb.get_catalog_tree(
    p_source_code TEXT,
    p_max_depth INTEGER DEFAULT NULL
)
RETURNS TABLE(
    id UUID,
    parent_id UUID,
    kind TEXT,
    title TEXT,
    slug TEXT,
    external_url TEXT,
    depth INTEGER,
    sort_order INTEGER,
    harvest_status TEXT,
    artifact_id UUID
) AS $$
BEGIN
    RETURN QUERY
    WITH RECURSIVE tree AS (
        -- Root nodes
        SELECT
            cn.id,
            cn.parent_id,
            cn.kind,
            cn.title,
            cn.slug,
            cn.external_url,
            cn.depth,
            cn.sort_order,
            ARRAY[cn.sort_order] AS path
        FROM kb.catalog_nodes cn
        JOIN kb.catalog_sources cs ON cs.id = cn.source_id
        WHERE cs.code = p_source_code
          AND cn.parent_id IS NULL

        UNION ALL

        -- Child nodes
        SELECT
            cn.id,
            cn.parent_id,
            cn.kind,
            cn.title,
            cn.slug,
            cn.external_url,
            cn.depth,
            cn.sort_order,
            tree.path || cn.sort_order
        FROM kb.catalog_nodes cn
        JOIN tree ON cn.parent_id = tree.id
        WHERE p_max_depth IS NULL OR cn.depth <= p_max_depth
    )
    SELECT
        t.id,
        t.parent_id,
        t.kind,
        t.title,
        t.slug,
        t.external_url,
        t.depth,
        t.sort_order,
        hs.status AS harvest_status,
        cn.artifact_id
    FROM tree t
    JOIN kb.catalog_nodes cn ON cn.id = t.id
    LEFT JOIN kb.harvest_state hs ON hs.node_id = t.id
    ORDER BY t.path;
END;
$$ LANGUAGE plpgsql STABLE;

-- Get pending harvest jobs (for crawler)
CREATE OR REPLACE FUNCTION kb.get_pending_harvest(
    p_source_code TEXT DEFAULT NULL,
    p_limit INTEGER DEFAULT 100
)
RETURNS TABLE(
    node_id UUID,
    source_code TEXT,
    kind TEXT,
    title TEXT,
    slug TEXT,
    external_url TEXT,
    crawl_depth INTEGER,
    queued_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cn.id AS node_id,
        cs.code AS source_code,
        cn.kind,
        cn.title,
        cn.slug,
        cn.external_url,
        cn.crawl_depth,
        hs.queued_at
    FROM kb.catalog_nodes cn
    JOIN kb.catalog_sources cs ON cs.id = cn.source_id
    JOIN kb.harvest_state hs ON hs.node_id = cn.id
    WHERE hs.status = 'queued'
      AND cn.should_harvest = true
      AND cs.is_active = true
      AND (p_source_code IS NULL OR cs.code = p_source_code)
    ORDER BY cs.priority DESC, hs.queued_at ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- Update harvest status
CREATE OR REPLACE FUNCTION kb.update_harvest_status(
    p_node_id UUID,
    p_status TEXT,
    p_content_hash TEXT DEFAULT NULL,
    p_version_id UUID DEFAULT NULL,
    p_chunk_count INTEGER DEFAULT NULL,
    p_error TEXT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE kb.harvest_state
    SET
        status = p_status,
        last_run_at = now(),
        last_ok_at = CASE WHEN p_status = 'ok' THEN now() ELSE last_ok_at END,
        last_content_hash = COALESCE(p_content_hash, last_content_hash),
        last_version_id = COALESCE(p_version_id, last_version_id),
        chunk_count = COALESCE(p_chunk_count, chunk_count),
        last_error = CASE WHEN p_status = 'error' THEN p_error ELSE NULL END,
        error_count = CASE WHEN p_status = 'error' THEN error_count + 1 ELSE error_count END,
        consecutive_errors = CASE
            WHEN p_status = 'error' THEN consecutive_errors + 1
            WHEN p_status = 'ok' THEN 0
            ELSE consecutive_errors
        END,
        updated_at = now()
    WHERE node_id = p_node_id;

    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Queue node for harvest (creates harvest_state if not exists)
CREATE OR REPLACE FUNCTION kb.queue_harvest(
    p_node_id UUID,
    p_tenant_id UUID DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_tenant_id UUID;
    v_harvest_id UUID;
BEGIN
    -- Get tenant from node if not provided
    IF p_tenant_id IS NULL THEN
        SELECT tenant_id INTO v_tenant_id
        FROM kb.catalog_nodes WHERE id = p_node_id;
    ELSE
        v_tenant_id := p_tenant_id;
    END IF;

    -- Upsert harvest state
    INSERT INTO kb.harvest_state (tenant_id, node_id, status, queued_at)
    VALUES (v_tenant_id, p_node_id, 'queued', now())
    ON CONFLICT (tenant_id, node_id)
    DO UPDATE SET
        status = 'queued',
        queued_at = now(),
        updated_at = now()
    RETURNING id INTO v_harvest_id;

    RETURN v_harvest_id;
END;
$$ LANGUAGE plpgsql;

-- Bulk queue all pending nodes for a source
CREATE OR REPLACE FUNCTION kb.queue_source_harvest(
    p_source_code TEXT,
    p_tenant_id UUID
)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    WITH queued AS (
        INSERT INTO kb.harvest_state (tenant_id, node_id, status, queued_at)
        SELECT cn.tenant_id, cn.id, 'queued', now()
        FROM kb.catalog_nodes cn
        JOIN kb.catalog_sources cs ON cs.id = cn.source_id
        WHERE cs.code = p_source_code
          AND cn.tenant_id = p_tenant_id
          AND cn.should_harvest = true
          AND cn.is_leaf = true
        ON CONFLICT (tenant_id, node_id)
        DO UPDATE SET
            status = 'queued',
            queued_at = now(),
            updated_at = now()
        WHERE kb.harvest_state.status NOT IN ('running')
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_count FROM queued;

    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- Get coverage summary for a source
CREATE OR REPLACE FUNCTION kb.get_source_coverage(p_source_code TEXT)
RETURNS TABLE(
    total_nodes BIGINT,
    ok_nodes BIGINT,
    pending_nodes BIGINT,
    error_nodes BIGINT,
    stale_nodes BIGINT,
    coverage_pct NUMERIC,
    total_chunks BIGINT,
    last_harvest TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT AS total_nodes,
        COUNT(*) FILTER (WHERE hs.status = 'ok')::BIGINT AS ok_nodes,
        COUNT(*) FILTER (WHERE hs.status IN ('queued', 'running'))::BIGINT AS pending_nodes,
        COUNT(*) FILTER (WHERE hs.status = 'error')::BIGINT AS error_nodes,
        COUNT(*) FILTER (WHERE hs.status = 'stale')::BIGINT AS stale_nodes,
        ROUND(
            COUNT(*) FILTER (WHERE hs.status = 'ok')::NUMERIC /
            NULLIF(COUNT(*), 0) * 100, 1
        ) AS coverage_pct,
        COALESCE(SUM(hs.chunk_count), 0)::BIGINT AS total_chunks,
        MAX(hs.last_ok_at) AS last_harvest
    FROM kb.catalog_nodes cn
    JOIN kb.catalog_sources cs ON cs.id = cn.source_id
    LEFT JOIN kb.harvest_state hs ON hs.node_id = cn.id
    WHERE cs.code = p_source_code
      AND cn.should_harvest = true
      AND cn.is_leaf = true;
END;
$$ LANGUAGE plpgsql STABLE;

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Auto-compute depth on insert/update
CREATE OR REPLACE FUNCTION kb.compute_node_depth()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.parent_id IS NULL THEN
        NEW.depth := 0;
    ELSE
        SELECT depth + 1 INTO NEW.depth
        FROM kb.catalog_nodes
        WHERE id = NEW.parent_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_compute_node_depth
    BEFORE INSERT OR UPDATE OF parent_id ON kb.catalog_nodes
    FOR EACH ROW
    EXECUTE FUNCTION kb.compute_node_depth();

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION kb.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_catalog_sources_updated
    BEFORE UPDATE ON kb.catalog_sources
    FOR EACH ROW
    EXECUTE FUNCTION kb.update_timestamp();

CREATE TRIGGER trg_catalog_nodes_updated
    BEFORE UPDATE ON kb.catalog_nodes
    FOR EACH ROW
    EXECUTE FUNCTION kb.update_timestamp();

CREATE TRIGGER trg_harvest_state_updated
    BEFORE UPDATE ON kb.harvest_state
    FOR EACH ROW
    EXECUTE FUNCTION kb.update_timestamp();

-- =============================================================================
-- LOG COMPLETION
-- =============================================================================

DO $$
BEGIN
    RAISE NOTICE 'KB Catalog schema created';
    RAISE NOTICE 'Tables: kb.catalog_sources, kb.catalog_nodes, kb.harvest_state';
    RAISE NOTICE 'View: kb.coverage_stats';
    RAISE NOTICE 'Functions: get_catalog_tree, get_pending_harvest, update_harvest_status, queue_harvest, queue_source_harvest, get_source_coverage';
END;
$$;
