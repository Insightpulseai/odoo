-- Migration: Knowledge Graph Schema
-- Purpose: Create unified organizational memory layer with graph, FTS, and vector search
-- Target: Supabase (external managed database with pgvector)
--
-- This schema implements the Knowledge Graph (KG) system for:
-- - Infra map: DigitalOcean droplets, domains, DNS records, services
-- - Code map: GitHub repos, branches, PRs, issues, workflows, Odoo modules
-- - Why map: Docs, decisions, chat threads linked to entities
--
-- Environment: Supabase project spdtwktxdalcfigzeqrz

-- ============================================================================
-- Extensions
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- Schema: kg (Knowledge Graph)
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS kg;

GRANT USAGE ON SCHEMA kg TO authenticated;
GRANT USAGE ON SCHEMA kg TO service_role;

-- ============================================================================
-- kg.nodes - Graph Nodes
-- ============================================================================
-- Core entity storage for all organizational objects.
-- Each node has a type (e.g., Repo, Droplet, OdooModule) and a stable key.
--
-- Key patterns by type:
--   Org:        org:<name>
--   Repo:       repo:<org>/<name>
--   Branch:     branch:<org>/<repo>:<name>
--   PR:         pr:<org>/<repo>#<num>
--   Issue:      issue:<org>/<repo>#<num>
--   Workflow:   workflow:<org>/<repo>:<name>
--   Run:        run:<org>/<repo>:<run_id>
--   Host:       droplet:<id>
--   Domain:     domain:<fqdn>
--   DNSRecord:  dns:<domain>:<type>:<name>
--   Service:    service:<name> or do-app:<id>
--   OdooModule: odoo:module:<technical_name>
--   OdooModel:  odoo:model:<model_name>
--   OdooView:   odoo:view:<xml_id>
--   OCARepo:    oca:repo:<name>
--   OCAModule:  oca:module:<name>
--   Doc:        doc:<source>:<ref>
--   Decision:   adr:<slug>
--   ChatThread: chat:<source>:<thread_id>
-- ============================================================================

CREATE TABLE IF NOT EXISTS kg.nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Node classification
    type TEXT NOT NULL,                 -- e.g., Repo, Host, OdooModule, Doc
    key TEXT NOT NULL,                  -- Stable unique key within type

    -- Human-readable info
    title TEXT,                         -- Display name

    -- Flexible metadata
    data JSONB NOT NULL DEFAULT '{}'::JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint: one node per (type, key)
    UNIQUE (type, key)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS kg_nodes_type_idx ON kg.nodes(type);
CREATE INDEX IF NOT EXISTS kg_nodes_key_idx ON kg.nodes(key);
CREATE INDEX IF NOT EXISTS kg_nodes_data_gin ON kg.nodes USING gin(data);

-- ============================================================================
-- kg.edges - Graph Edges (Relationships)
-- ============================================================================
-- Typed relationships between nodes with optional weight and metadata.
--
-- Edge types:
--   OWNS:       Org → Repo, Module → Model/View
--   DEPLOYS_TO: Repo → Service/Host
--   DEPENDS_ON: Module → Module
--   IMPLEMENTS: PR → Issue
--   REFERENCES: Doc → Repo/Module
--   RESOLVES:   Issue → Incident
--   CONFIGURES: DNSRecord → Service/Host
--   MENTIONS:   Doc/ChatThread → AnyNode (with confidence score in data)
-- ============================================================================

CREATE TABLE IF NOT EXISTS kg.edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source and destination nodes
    src_id UUID NOT NULL REFERENCES kg.nodes(id) ON DELETE CASCADE,
    dst_id UUID NOT NULL REFERENCES kg.nodes(id) ON DELETE CASCADE,

    -- Relationship type
    type TEXT NOT NULL,                 -- e.g., DEPENDS_ON, DEPLOYS_TO

    -- Optional weight for ranking/scoring
    weight DOUBLE PRECISION NOT NULL DEFAULT 1.0,

    -- Flexible metadata
    data JSONB NOT NULL DEFAULT '{}'::JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint: one edge per (src, dst, type)
    UNIQUE (src_id, dst_id, type)
);

-- Indexes for graph traversal
CREATE INDEX IF NOT EXISTS kg_edges_src_idx ON kg.edges(src_id);
CREATE INDEX IF NOT EXISTS kg_edges_dst_idx ON kg.edges(dst_id);
CREATE INDEX IF NOT EXISTS kg_edges_type_idx ON kg.edges(type);
CREATE INDEX IF NOT EXISTS kg_edges_src_type_idx ON kg.edges(src_id, type);
CREATE INDEX IF NOT EXISTS kg_edges_dst_type_idx ON kg.edges(dst_id, type);

-- ============================================================================
-- kg.docs - Documents (Chat, README, PRD, ADR, logs)
-- ============================================================================
-- Content storage for RAG retrieval. Each doc has:
-- - Source identification (github, slack, gdrive, chatgpt, odoo, do)
-- - Full-text search via tsvector
-- - Vector embedding for semantic search (1536 dims for OpenAI)
-- ============================================================================

CREATE TABLE IF NOT EXISTS kg.docs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Source identification
    source TEXT NOT NULL,               -- github, slack, gdrive, chatgpt, odoo, do
    source_ref TEXT NOT NULL,           -- URL, message ID, file ID

    -- Content
    title TEXT,
    body TEXT NOT NULL,

    -- Flexible metadata
    meta JSONB NOT NULL DEFAULT '{}'::JSONB,

    -- Full-text search vector (auto-computed via trigger)
    tsv TSVECTOR,

    -- Embedding for semantic search (OpenAI text-embedding-3-small: 1536 dims)
    embedding vector(1536),

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Unique constraint: one doc per (source, source_ref)
    UNIQUE (source, source_ref)
);

-- Full-text search index
CREATE INDEX IF NOT EXISTS kg_docs_tsv_gin ON kg.docs USING gin(tsv);

-- Vector similarity index (IVFFlat for balance of speed/accuracy)
-- lists = 100 is appropriate for < 1M vectors
CREATE INDEX IF NOT EXISTS kg_docs_embedding_ivf
    ON kg.docs USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Metadata index
CREATE INDEX IF NOT EXISTS kg_docs_meta_gin ON kg.docs USING gin(meta);
CREATE INDEX IF NOT EXISTS kg_docs_source_idx ON kg.docs(source);

-- ============================================================================
-- Trigger: Auto-update tsvector for full-text search
-- ============================================================================

CREATE OR REPLACE FUNCTION kg.docs_tsv_update()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.tsv :=
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.body, '')), 'B');
    RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_kg_docs_tsv ON kg.docs;
CREATE TRIGGER trg_kg_docs_tsv
    BEFORE INSERT OR UPDATE ON kg.docs
    FOR EACH ROW
    EXECUTE FUNCTION kg.docs_tsv_update();

-- ============================================================================
-- kg.mentions - Links between docs and nodes
-- ============================================================================
-- Connects documents to the entities they mention.
-- Used for knowledge graph enrichment and context expansion in RAG.
--
-- Kinds:
--   MENTIONS:   Generic reference
--   DEFINES:    Doc defines the entity
--   DECIDES:    Doc contains decision about entity (ADR)
--   CONFIGURES: Doc configures the entity
-- ============================================================================

CREATE TABLE IF NOT EXISTS kg.mentions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- References
    doc_id UUID NOT NULL REFERENCES kg.docs(id) ON DELETE CASCADE,
    node_id UUID NOT NULL REFERENCES kg.nodes(id) ON DELETE CASCADE,

    -- Mention classification
    kind TEXT NOT NULL DEFAULT 'MENTIONS',  -- MENTIONS, DEFINES, DECIDES, CONFIGURES

    -- Confidence score for extracted mentions (0.0 - 1.0)
    confidence DOUBLE PRECISION NOT NULL DEFAULT 0.5,

    -- Flexible metadata
    meta JSONB NOT NULL DEFAULT '{}'::JSONB,

    -- Unique constraint: one mention per (doc, node, kind)
    UNIQUE (doc_id, node_id, kind)
);

-- Indexes for expansion queries
CREATE INDEX IF NOT EXISTS kg_mentions_doc_idx ON kg.mentions(doc_id);
CREATE INDEX IF NOT EXISTS kg_mentions_node_idx ON kg.mentions(node_id);
CREATE INDEX IF NOT EXISTS kg_mentions_kind_idx ON kg.mentions(kind);

-- ============================================================================
-- RPC: kg.search_docs - Full-text search
-- ============================================================================

CREATE OR REPLACE FUNCTION kg.search_docs(
    p_query TEXT,
    p_limit INT DEFAULT 10
) RETURNS TABLE (
    id UUID,
    source TEXT,
    source_ref TEXT,
    title TEXT,
    body TEXT,
    rank REAL
) LANGUAGE sql STABLE AS $$
    SELECT
        d.id,
        d.source,
        d.source_ref,
        d.title,
        d.body,
        ts_rank(d.tsv, websearch_to_tsquery('english', p_query)) AS rank
    FROM kg.docs d
    WHERE d.tsv @@ websearch_to_tsquery('english', p_query)
    ORDER BY rank DESC
    LIMIT p_limit;
$$;

-- ============================================================================
-- RPC: kg.search_docs_vector - Vector similarity search
-- ============================================================================

CREATE OR REPLACE FUNCTION kg.search_docs_vector(
    p_embedding vector(1536),
    p_limit INT DEFAULT 10
) RETURNS TABLE (
    id UUID,
    source TEXT,
    source_ref TEXT,
    title TEXT,
    body TEXT,
    similarity FLOAT
) LANGUAGE sql STABLE AS $$
    SELECT
        d.id,
        d.source,
        d.source_ref,
        d.title,
        d.body,
        1 - (d.embedding <=> p_embedding) AS similarity
    FROM kg.docs d
    WHERE d.embedding IS NOT NULL
    ORDER BY d.embedding <=> p_embedding
    LIMIT p_limit;
$$;

-- ============================================================================
-- RPC: kg.get_neighbors - Graph traversal (1-hop)
-- ============================================================================

CREATE OR REPLACE FUNCTION kg.get_neighbors(
    p_node_id UUID,
    p_direction TEXT DEFAULT 'both',  -- 'out', 'in', 'both'
    p_edge_type TEXT DEFAULT NULL     -- Filter by edge type (optional)
) RETURNS TABLE (
    edge_id UUID,
    edge_type TEXT,
    neighbor_id UUID,
    neighbor_type TEXT,
    neighbor_key TEXT,
    neighbor_title TEXT,
    direction TEXT
) LANGUAGE sql STABLE AS $$
    -- Outgoing edges
    SELECT
        e.id AS edge_id,
        e.type AS edge_type,
        n.id AS neighbor_id,
        n.type AS neighbor_type,
        n.key AS neighbor_key,
        n.title AS neighbor_title,
        'out' AS direction
    FROM kg.edges e
    JOIN kg.nodes n ON n.id = e.dst_id
    WHERE e.src_id = p_node_id
      AND (p_direction IN ('out', 'both'))
      AND (p_edge_type IS NULL OR e.type = p_edge_type)

    UNION ALL

    -- Incoming edges
    SELECT
        e.id AS edge_id,
        e.type AS edge_type,
        n.id AS neighbor_id,
        n.type AS neighbor_type,
        n.key AS neighbor_key,
        n.title AS neighbor_title,
        'in' AS direction
    FROM kg.edges e
    JOIN kg.nodes n ON n.id = e.src_id
    WHERE e.dst_id = p_node_id
      AND (p_direction IN ('in', 'both'))
      AND (p_edge_type IS NULL OR e.type = p_edge_type);
$$;

-- ============================================================================
-- RPC: kg.get_node_docs - Get docs mentioning a node
-- ============================================================================

CREATE OR REPLACE FUNCTION kg.get_node_docs(
    p_node_id UUID,
    p_limit INT DEFAULT 10
) RETURNS TABLE (
    doc_id UUID,
    source TEXT,
    source_ref TEXT,
    title TEXT,
    mention_kind TEXT,
    confidence FLOAT
) LANGUAGE sql STABLE AS $$
    SELECT
        d.id AS doc_id,
        d.source,
        d.source_ref,
        d.title,
        m.kind AS mention_kind,
        m.confidence
    FROM kg.mentions m
    JOIN kg.docs d ON d.id = m.doc_id
    WHERE m.node_id = p_node_id
    ORDER BY m.confidence DESC, d.created_at DESC
    LIMIT p_limit;
$$;

-- ============================================================================
-- RPC: kg.upsert_node - Idempotent node upsert
-- ============================================================================

CREATE OR REPLACE FUNCTION kg.upsert_node(
    p_type TEXT,
    p_key TEXT,
    p_title TEXT DEFAULT NULL,
    p_data JSONB DEFAULT '{}'::JSONB
) RETURNS UUID LANGUAGE plpgsql AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO kg.nodes (type, key, title, data, updated_at)
    VALUES (p_type, p_key, p_title, p_data, NOW())
    ON CONFLICT (type, key) DO UPDATE SET
        title = COALESCE(EXCLUDED.title, kg.nodes.title),
        data = kg.nodes.data || EXCLUDED.data,
        updated_at = NOW()
    RETURNING id INTO v_id;

    RETURN v_id;
END $$;

-- ============================================================================
-- RPC: kg.upsert_edge - Idempotent edge upsert
-- ============================================================================

CREATE OR REPLACE FUNCTION kg.upsert_edge(
    p_src_id UUID,
    p_dst_id UUID,
    p_type TEXT,
    p_weight DOUBLE PRECISION DEFAULT 1.0,
    p_data JSONB DEFAULT '{}'::JSONB
) RETURNS UUID LANGUAGE plpgsql AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO kg.edges (src_id, dst_id, type, weight, data)
    VALUES (p_src_id, p_dst_id, p_type, p_weight, p_data)
    ON CONFLICT (src_id, dst_id, type) DO UPDATE SET
        weight = EXCLUDED.weight,
        data = kg.edges.data || EXCLUDED.data
    RETURNING id INTO v_id;

    RETURN v_id;
END $$;

-- ============================================================================
-- RLS Policies
-- ============================================================================
-- For now, allow authenticated users full read access.
-- Service role has full access for ingestion.
-- TODO: Add org-based isolation if multi-tenant.
-- ============================================================================

ALTER TABLE kg.nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE kg.edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE kg.docs ENABLE ROW LEVEL SECURITY;
ALTER TABLE kg.mentions ENABLE ROW LEVEL SECURITY;

-- Authenticated users can read everything
CREATE POLICY "Authenticated read nodes" ON kg.nodes
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated read edges" ON kg.edges
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated read docs" ON kg.docs
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated read mentions" ON kg.mentions
    FOR SELECT TO authenticated USING (true);

-- Service role has full access (for ingestion)
CREATE POLICY "Service role full access nodes" ON kg.nodes
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access edges" ON kg.edges
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access docs" ON kg.docs
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access mentions" ON kg.mentions
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ============================================================================
-- Grants
-- ============================================================================

GRANT SELECT ON kg.nodes TO authenticated;
GRANT SELECT ON kg.edges TO authenticated;
GRANT SELECT ON kg.docs TO authenticated;
GRANT SELECT ON kg.mentions TO authenticated;

GRANT ALL ON kg.nodes TO service_role;
GRANT ALL ON kg.edges TO service_role;
GRANT ALL ON kg.docs TO service_role;
GRANT ALL ON kg.mentions TO service_role;

GRANT EXECUTE ON FUNCTION kg.search_docs(TEXT, INT) TO authenticated;
GRANT EXECUTE ON FUNCTION kg.search_docs(TEXT, INT) TO service_role;

GRANT EXECUTE ON FUNCTION kg.search_docs_vector(vector, INT) TO authenticated;
GRANT EXECUTE ON FUNCTION kg.search_docs_vector(vector, INT) TO service_role;

GRANT EXECUTE ON FUNCTION kg.get_neighbors(UUID, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION kg.get_neighbors(UUID, TEXT, TEXT) TO service_role;

GRANT EXECUTE ON FUNCTION kg.get_node_docs(UUID, INT) TO authenticated;
GRANT EXECUTE ON FUNCTION kg.get_node_docs(UUID, INT) TO service_role;

GRANT EXECUTE ON FUNCTION kg.upsert_node(TEXT, TEXT, TEXT, JSONB) TO service_role;
GRANT EXECUTE ON FUNCTION kg.upsert_edge(UUID, UUID, TEXT, DOUBLE PRECISION, JSONB) TO service_role;

-- ============================================================================
-- Trigger: Auto-update updated_at on nodes
-- ============================================================================

CREATE OR REPLACE FUNCTION kg.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER kg_nodes_updated_at
    BEFORE UPDATE ON kg.nodes
    FOR EACH ROW
    EXECUTE FUNCTION kg.update_updated_at_column();

-- ============================================================================
-- Comments for documentation
-- ============================================================================

COMMENT ON SCHEMA kg IS 'Knowledge Graph: unified organizational memory layer';

COMMENT ON TABLE kg.nodes IS 'Graph nodes representing organizational entities (repos, droplets, modules, etc.)';
COMMENT ON COLUMN kg.nodes.type IS 'Node type: Org, Repo, Branch, PR, Issue, Workflow, Run, Host, Domain, DNSRecord, Service, OdooModule, OdooModel, OdooView, Doc, Decision, ChatThread';
COMMENT ON COLUMN kg.nodes.key IS 'Stable unique identifier within type (e.g., repo:org/name, droplet:123)';
COMMENT ON COLUMN kg.nodes.data IS 'Flexible JSONB metadata for type-specific fields';

COMMENT ON TABLE kg.edges IS 'Graph edges representing relationships between nodes';
COMMENT ON COLUMN kg.edges.type IS 'Edge type: OWNS, DEPLOYS_TO, DEPENDS_ON, IMPLEMENTS, REFERENCES, RESOLVES, CONFIGURES, MENTIONS';
COMMENT ON COLUMN kg.edges.weight IS 'Optional weight for ranking (default 1.0)';

COMMENT ON TABLE kg.docs IS 'Document storage with FTS and vector search for RAG retrieval';
COMMENT ON COLUMN kg.docs.source IS 'Document source: github, slack, gdrive, chatgpt, claude, odoo, do';
COMMENT ON COLUMN kg.docs.embedding IS 'Vector embedding for semantic search (1536 dims for OpenAI text-embedding-3-small)';

COMMENT ON TABLE kg.mentions IS 'Links between documents and nodes they reference';
COMMENT ON COLUMN kg.mentions.kind IS 'Mention type: MENTIONS, DEFINES, DECIDES, CONFIGURES';
COMMENT ON COLUMN kg.mentions.confidence IS 'Extraction confidence score (0.0 - 1.0)';

COMMENT ON FUNCTION kg.search_docs IS 'Full-text search across documents using websearch syntax';
COMMENT ON FUNCTION kg.search_docs_vector IS 'Vector similarity search for semantic retrieval';
COMMENT ON FUNCTION kg.get_neighbors IS 'Get neighboring nodes via edges (graph traversal)';
COMMENT ON FUNCTION kg.get_node_docs IS 'Get documents that mention a specific node';
COMMENT ON FUNCTION kg.upsert_node IS 'Idempotent node insert/update by (type, key)';
COMMENT ON FUNCTION kg.upsert_edge IS 'Idempotent edge insert/update by (src_id, dst_id, type)';
