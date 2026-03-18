-- =============================================================================
-- OCA Docs Brain — Kapa-like Knowledge Base for Odoo CE + OCA 18
-- =============================================================================
-- Version: 1.0.0
-- PRD Reference: OCA Docs Brain (Kapa-like Docs KB Platform)
--
-- Implements:
--   * sources schema - source registry, crawl runs, source items
--   * docs schema - documents, chunks, embeddings, citations
--   * kg schema - knowledge graph entities and edges
--   * Enhanced retrieval with hybrid search
--   * Citation tracking and evidence linking
--
-- Constraints:
--   * No custom Odoo module
--   * No writes to Odoo core DB
--   * Supabase-first with RLS everywhere
-- =============================================================================

BEGIN;

-- =============================================================================
-- SCHEMAS
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS sources;
CREATE SCHEMA IF NOT EXISTS docs;
CREATE SCHEMA IF NOT EXISTS kg;

COMMENT ON SCHEMA sources IS 'Source registry: crawlers, runs, and raw source items';
COMMENT ON SCHEMA docs IS 'Document store: parsed documents, chunks, embeddings, citations';
COMMENT ON SCHEMA kg IS 'Knowledge Graph: entities, edges, and evidence linking';

-- =============================================================================
-- 1. SOURCES.SOURCES — Source Registry
-- =============================================================================

CREATE TABLE IF NOT EXISTS sources.sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id) ON DELETE CASCADE,

    -- Source identity
    source_type TEXT NOT NULL CHECK (source_type IN (
        'web', 'git', 'notion', 'confluence', 'pdf', 'markdown',
        'odoo_docs', 'oca_repo', 'sap_help', 'file_drop'
    )),
    name TEXT NOT NULL,
    description TEXT,

    -- Location
    base_url TEXT, -- For web/git
    repo_url TEXT, -- For git
    branch TEXT DEFAULT 'main',
    path_filter TEXT, -- Glob pattern: "docs/**/*.md"

    -- Authentication (reference to secrets)
    auth_type TEXT CHECK (auth_type IN ('none', 'token', 'oauth', 'api_key', 'basic')),
    auth_ref TEXT, -- vault:sources/github/odoo-oca

    -- Crawl configuration
    crawl_policy JSONB DEFAULT '{}'::jsonb,
    -- {
    --   "schedule": "0 2 * * *",
    --   "mode": "incremental",
    --   "max_depth": 5,
    --   "rate_limit_rpm": 60,
    --   "include_patterns": ["*.md", "*.rst"],
    --   "exclude_patterns": ["**/test/**", "**/vendor/**"]
    -- }

    -- Chunking configuration
    chunk_policy JSONB DEFAULT '{}'::jsonb,
    -- {
    --   "strategy": "heading_aware",
    --   "max_tokens": 512,
    --   "overlap_tokens": 50,
    --   "preserve_code_blocks": true
    -- }

    -- Embedding
    embedding_model_key TEXT REFERENCES rag.embedding_models(key) DEFAULT 'text-embedding-3-small',

    -- Tags for filtering
    tags TEXT[] DEFAULT '{}',

    -- Status
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN (
        'active', 'paused', 'disabled', 'failed'
    )),
    is_public BOOLEAN DEFAULT false, -- Visible to all tenants?

    -- Stats
    item_count INT DEFAULT 0,
    document_count INT DEFAULT 0,
    chunk_count INT DEFAULT 0,
    last_crawl_at TIMESTAMPTZ,
    last_success_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    created_by UUID,

    UNIQUE (tenant_id, name)
);

CREATE INDEX idx_sources_tenant ON sources.sources(tenant_id);
CREATE INDEX idx_sources_type ON sources.sources(source_type);
CREATE INDEX idx_sources_status ON sources.sources(status) WHERE status = 'active';
CREATE INDEX idx_sources_tags ON sources.sources USING gin(tags);

-- Enable RLS
ALTER TABLE sources.sources ENABLE ROW LEVEL SECURITY;

CREATE POLICY sources_tenant_isolation ON sources.sources
    FOR ALL USING (tenant_id = core.current_tenant_id() OR is_public = true);

COMMENT ON TABLE sources.sources IS 'Source registry for docs, repos, and external knowledge bases';

-- =============================================================================
-- 2. SOURCES.CRAWL_RUNS — Crawl Execution History
-- =============================================================================

CREATE TABLE IF NOT EXISTS sources.crawl_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources.sources(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),

    -- Run metadata
    run_type TEXT NOT NULL DEFAULT 'incremental' CHECK (run_type IN (
        'full', 'incremental', 'reembed', 'reparse'
    )),
    triggered_by TEXT DEFAULT 'schedule', -- schedule, manual, webhook
    triggered_by_user UUID,

    -- Status
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'running', 'completed', 'failed', 'cancelled'
    )),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    -- Progress
    progress_pct INT DEFAULT 0,
    current_item TEXT,

    -- Stats
    items_fetched INT DEFAULT 0,
    items_created INT DEFAULT 0,
    items_updated INT DEFAULT 0,
    items_unchanged INT DEFAULT 0,
    items_deleted INT DEFAULT 0,
    chunks_created INT DEFAULT 0,
    embeddings_created INT DEFAULT 0,
    entities_extracted INT DEFAULT 0,
    edges_created INT DEFAULT 0,

    -- Errors
    error_count INT DEFAULT 0,
    errors JSONB DEFAULT '[]'::jsonb,
    fatal_error TEXT,

    -- Change summary (for UI)
    change_summary JSONB DEFAULT '{}'::jsonb,
    -- {"added": [...urls], "updated": [...urls], "deleted": [...urls]}

    -- Performance
    duration_seconds DECIMAL(10,2),
    bytes_processed BIGINT DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_crawl_runs_source ON sources.crawl_runs(source_id, created_at DESC);
CREATE INDEX idx_crawl_runs_status ON sources.crawl_runs(status) WHERE status IN ('pending', 'running');
CREATE INDEX idx_crawl_runs_tenant ON sources.crawl_runs(tenant_id, created_at DESC);

-- Enable RLS
ALTER TABLE sources.crawl_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY crawl_runs_tenant_isolation ON sources.crawl_runs
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE sources.crawl_runs IS 'Crawl execution history with progress and change tracking';

-- =============================================================================
-- 3. SOURCES.SOURCE_ITEMS — Raw Fetched Items
-- =============================================================================

CREATE TABLE IF NOT EXISTS sources.source_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES sources.sources(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),

    -- Identity
    canonical_url TEXT NOT NULL, -- Stable URL for citations
    relative_path TEXT, -- Path within source (e.g., "docs/finance/close.md")

    -- Content
    raw_content TEXT,
    content_hash TEXT NOT NULL, -- SHA256 for change detection
    content_type TEXT, -- text/markdown, text/html, application/pdf

    -- Metadata
    title TEXT,
    language TEXT DEFAULT 'en',
    metadata JSONB DEFAULT '{}'::jsonb,
    -- {
    --   "author": "...",
    --   "last_modified": "...",
    --   "version": "18.0",
    --   "module": "account"
    -- }

    -- Fetch info
    fetched_at TIMESTAMPTZ DEFAULT now(),
    http_status INT,
    http_headers JSONB,

    -- Processing status
    parse_status TEXT DEFAULT 'pending' CHECK (parse_status IN (
        'pending', 'parsed', 'failed', 'skipped'
    )),
    parsed_at TIMESTAMPTZ,
    parse_error TEXT,

    -- Previous version (for diff)
    previous_content_hash TEXT,
    changed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (source_id, canonical_url)
);

CREATE INDEX idx_source_items_source ON sources.source_items(source_id);
CREATE INDEX idx_source_items_tenant ON sources.source_items(tenant_id);
CREATE INDEX idx_source_items_hash ON sources.source_items(content_hash);
CREATE INDEX idx_source_items_url ON sources.source_items(canonical_url);
CREATE INDEX idx_source_items_changed ON sources.source_items(changed_at DESC) WHERE changed_at IS NOT NULL;

-- Enable RLS
ALTER TABLE sources.source_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY source_items_tenant_isolation ON sources.source_items
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE sources.source_items IS 'Raw fetched items with content hash for change detection';

-- =============================================================================
-- 4. DOCS.DOCUMENTS — Parsed Documents
-- =============================================================================

CREATE TABLE IF NOT EXISTS docs.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_item_id UUID NOT NULL REFERENCES sources.source_items(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources.sources(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),

    -- Identity
    canonical_url TEXT NOT NULL,
    title TEXT NOT NULL,
    slug TEXT, -- URL-friendly identifier

    -- Content
    content_markdown TEXT, -- Normalized markdown
    content_plain TEXT, -- Plain text for search

    -- Metadata
    language TEXT DEFAULT 'en',
    doc_type TEXT, -- guide, reference, tutorial, changelog, readme, manifest
    version TEXT, -- e.g., "18.0", "18.0.1.0.0"

    -- Odoo/OCA specific
    module_name TEXT, -- OCA/Odoo module name
    model_names TEXT[], -- Models mentioned
    feature_tags TEXT[], -- Feature categories

    -- Publishing
    published_at TIMESTAMPTZ,
    last_modified_at TIMESTAMPTZ,
    author TEXT,

    -- Structure
    heading_tree JSONB, -- Hierarchical heading structure
    toc JSONB, -- Table of contents
    word_count INT,
    reading_time_minutes INT,

    -- Freshness
    freshness_score DECIMAL(3,2), -- 0-1, decays over time
    stale_after TIMESTAMPTZ, -- When to consider stale

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, canonical_url)
);

CREATE INDEX idx_docs_source ON docs.documents(source_id);
CREATE INDEX idx_docs_tenant ON docs.documents(tenant_id);
CREATE INDEX idx_docs_module ON docs.documents(module_name) WHERE module_name IS NOT NULL;
CREATE INDEX idx_docs_version ON docs.documents(version);
CREATE INDEX idx_docs_type ON docs.documents(doc_type);
CREATE INDEX idx_docs_features ON docs.documents USING gin(feature_tags);
CREATE INDEX idx_docs_models ON docs.documents USING gin(model_names);
CREATE INDEX idx_docs_freshness ON docs.documents(freshness_score DESC);

-- Full-text search
ALTER TABLE docs.documents ADD COLUMN IF NOT EXISTS tsv tsvector;

CREATE INDEX idx_docs_tsv ON docs.documents USING gin(tsv);

CREATE OR REPLACE FUNCTION docs.documents_tsv_update()
RETURNS TRIGGER LANGUAGE plpgsql AS $func$
BEGIN
    NEW.tsv := setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
               setweight(to_tsvector('english', COALESCE(NEW.module_name, '')), 'A') ||
               setweight(to_tsvector('english', COALESCE(NEW.content_plain, '')), 'B');
    RETURN NEW;
END;
$func$;

DROP TRIGGER IF EXISTS trg_docs_tsv ON docs.documents;
CREATE TRIGGER trg_docs_tsv
    BEFORE INSERT OR UPDATE OF title, module_name, content_plain
    ON docs.documents
    FOR EACH ROW EXECUTE FUNCTION docs.documents_tsv_update();

-- Enable RLS
ALTER TABLE docs.documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY documents_tenant_isolation ON docs.documents
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE docs.documents IS 'Parsed documents with Odoo/OCA metadata and full-text search';

-- =============================================================================
-- 5. DOCS.CHUNKS — Document Chunks for Retrieval
-- =============================================================================

CREATE TABLE IF NOT EXISTS docs.chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES docs.documents(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources.sources(id),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),

    -- Position
    chunk_index INT NOT NULL, -- Order within document
    char_start INT, -- Character offset start
    char_end INT, -- Character offset end

    -- Content
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL, -- For deduplication

    -- Structure
    heading_path TEXT, -- "Finance > Month-End > Closing Steps"
    heading_level INT, -- 1-6
    section_title TEXT,

    -- Token info
    token_count INT,
    embedding_model_key TEXT REFERENCES rag.embedding_models(key),

    -- Embedding
    embedding vector(1536),

    -- Anchors for citations
    anchor_id TEXT, -- HTML anchor: "closing-steps"
    line_start INT,
    line_end INT,

    -- Metadata
    chunk_type TEXT DEFAULT 'text' CHECK (chunk_type IN (
        'text', 'code', 'table', 'list', 'quote', 'heading'
    )),
    language TEXT, -- For code blocks

    -- Lexical search
    tsv tsvector,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (document_id, chunk_index)
);

CREATE INDEX idx_chunks_document ON docs.chunks(document_id, chunk_index);
CREATE INDEX idx_chunks_source ON docs.chunks(source_id);
CREATE INDEX idx_chunks_tenant ON docs.chunks(tenant_id);
CREATE INDEX idx_chunks_hash ON docs.chunks(content_hash);
CREATE INDEX idx_chunks_heading ON docs.chunks(heading_path);
CREATE INDEX idx_chunks_tsv ON docs.chunks USING gin(tsv);

-- Vector index (IVFFlat - adjust lists based on data size)
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON docs.chunks
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Trigger for tsvector
CREATE OR REPLACE FUNCTION docs.chunks_tsv_update()
RETURNS TRIGGER LANGUAGE plpgsql AS $func$
BEGIN
    NEW.tsv := to_tsvector('english', COALESCE(NEW.content, ''));
    RETURN NEW;
END;
$func$;

DROP TRIGGER IF EXISTS trg_chunks_tsv ON docs.chunks;
CREATE TRIGGER trg_chunks_tsv
    BEFORE INSERT OR UPDATE OF content
    ON docs.chunks
    FOR EACH ROW EXECUTE FUNCTION docs.chunks_tsv_update();

-- Enable RLS
ALTER TABLE docs.chunks ENABLE ROW LEVEL SECURITY;

CREATE POLICY chunks_tenant_isolation ON docs.chunks
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE docs.chunks IS 'Document chunks with embeddings and stable anchors for citations';

-- =============================================================================
-- 6. DOCS.CITATIONS — Answer-to-Chunk Links
-- =============================================================================

CREATE TABLE IF NOT EXISTS docs.citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),

    -- What this cites
    chunk_id UUID NOT NULL REFERENCES docs.chunks(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES docs.documents(id),

    -- Where it was cited
    answer_id UUID, -- References runtime.answers or similar
    query_id UUID, -- References runtime.queries

    -- Citation details
    relevance_score DECIMAL(5,4), -- Similarity score
    rank INT, -- Position in retrieval results

    -- Snippet
    snippet TEXT, -- Highlighted excerpt
    snippet_start INT,
    snippet_end INT,

    -- Usage
    was_used BOOLEAN DEFAULT false, -- Actually used in answer
    was_shown BOOLEAN DEFAULT false, -- Shown to user
    was_clicked BOOLEAN DEFAULT false, -- User clicked through

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_citations_chunk ON docs.citations(chunk_id);
CREATE INDEX idx_citations_answer ON docs.citations(answer_id);
CREATE INDEX idx_citations_query ON docs.citations(query_id);
CREATE INDEX idx_citations_tenant ON docs.citations(tenant_id, created_at DESC);

-- Enable RLS
ALTER TABLE docs.citations ENABLE ROW LEVEL SECURITY;

CREATE POLICY citations_tenant_isolation ON docs.citations
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE docs.citations IS 'Links between answers and source chunks for citation tracking';

-- =============================================================================
-- 7. KG.ENTITIES — Knowledge Graph Nodes
-- =============================================================================

CREATE TABLE IF NOT EXISTS kg.entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),

    -- Entity identity
    entity_type TEXT NOT NULL CHECK (entity_type IN (
        'module', 'model', 'feature', 'config_key', 'version',
        'field', 'view', 'action', 'menu', 'report', 'wizard',
        'concept', 'term', 'error_code', 'api_endpoint'
    )),
    name TEXT NOT NULL,
    normalized_key TEXT NOT NULL, -- Lowercase, no special chars

    -- Display
    display_name TEXT,
    description TEXT,

    -- Attributes (type-specific)
    attributes JSONB DEFAULT '{}'::jsonb,
    -- Module: {"technical_name": "account", "installable": true, "depends": [...]}
    -- Model: {"model": "account.move", "inherit": [...], "fields": [...]}
    -- Feature: {"category": "accounting", "enterprise_equiv": "..."}

    -- Odoo-specific
    odoo_version TEXT, -- 18.0
    module_name TEXT, -- Source module
    is_oca BOOLEAN DEFAULT false,
    is_enterprise_feature BOOLEAN DEFAULT false,

    -- Evidence
    primary_chunk_id UUID REFERENCES docs.chunks(id),
    evidence_chunk_ids UUID[],

    -- Embedding (for entity search)
    embedding vector(1536),
    embedding_model_key TEXT REFERENCES rag.embedding_models(key),

    -- Stats
    mention_count INT DEFAULT 0,
    edge_count INT DEFAULT 0,

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'deprecated', 'deleted')),
    deprecated_by UUID REFERENCES kg.entities(id),
    deprecated_reason TEXT,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, entity_type, normalized_key)
);

CREATE INDEX idx_entities_tenant ON kg.entities(tenant_id);
CREATE INDEX idx_entities_type ON kg.entities(entity_type);
CREATE INDEX idx_entities_key ON kg.entities(normalized_key);
CREATE INDEX idx_entities_module ON kg.entities(module_name);
CREATE INDEX idx_entities_version ON kg.entities(odoo_version);
CREATE INDEX idx_entities_status ON kg.entities(status) WHERE status = 'active';

-- Vector index for entity search
CREATE INDEX IF NOT EXISTS idx_entities_embedding ON kg.entities
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50)
    WHERE embedding IS NOT NULL;

-- Enable RLS
ALTER TABLE kg.entities ENABLE ROW LEVEL SECURITY;

CREATE POLICY entities_tenant_isolation ON kg.entities
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE kg.entities IS 'Knowledge graph entities: modules, models, features, concepts';

-- =============================================================================
-- 8. KG.EDGES — Knowledge Graph Relationships
-- =============================================================================

CREATE TABLE IF NOT EXISTS kg.edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),

    -- Relationship
    from_entity_id UUID NOT NULL REFERENCES kg.entities(id) ON DELETE CASCADE,
    to_entity_id UUID NOT NULL REFERENCES kg.entities(id) ON DELETE CASCADE,
    edge_type TEXT NOT NULL CHECK (edge_type IN (
        'depends_on', 'implements', 'extends', 'overrides',
        'requires', 'conflicts_with', 'replaces', 'deprecated_by',
        'contains', 'belongs_to', 'references', 'calls',
        'inherits', 'delegates_to', 'described_by', 'documented_in'
    )),

    -- Direction metadata
    is_bidirectional BOOLEAN DEFAULT false,

    -- Evidence
    evidence_chunk_id UUID REFERENCES docs.chunks(id),
    evidence_text TEXT, -- Extracted sentence/paragraph

    -- Confidence
    confidence DECIMAL(3,2) DEFAULT 1.0, -- 0-1
    extraction_method TEXT, -- manual, regex, llm, dependency_parse

    -- Attributes
    attributes JSONB DEFAULT '{}'::jsonb,
    -- depends_on: {"optional": false, "auto_install": true}
    -- implements: {"coverage": "full", "enterprise_feature": "..."}

    -- Weight (for graph algorithms)
    weight DECIMAL(5,4) DEFAULT 1.0,

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    -- Prevent duplicate edges
    UNIQUE (from_entity_id, to_entity_id, edge_type)
);

CREATE INDEX idx_edges_from ON kg.edges(from_entity_id);
CREATE INDEX idx_edges_to ON kg.edges(to_entity_id);
CREATE INDEX idx_edges_type ON kg.edges(edge_type);
CREATE INDEX idx_edges_tenant ON kg.edges(tenant_id);
CREATE INDEX idx_edges_evidence ON kg.edges(evidence_chunk_id);

-- Enable RLS
ALTER TABLE kg.edges ENABLE ROW LEVEL SECURITY;

CREATE POLICY edges_tenant_isolation ON kg.edges
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE kg.edges IS 'Knowledge graph edges with evidence linking';

-- =============================================================================
-- 9. KG.MODULE_REGISTRY — OCA/Odoo Module Index
-- =============================================================================

CREATE TABLE IF NOT EXISTS kg.module_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),

    -- Module identity
    technical_name TEXT NOT NULL,
    display_name TEXT,
    summary TEXT,
    description TEXT,

    -- Source
    source_type TEXT NOT NULL CHECK (source_type IN ('odoo_core', 'oca', 'custom', 'third_party')),
    repo_url TEXT,
    repo_path TEXT, -- e.g., "OCA/account-financial-tools"

    -- Version
    odoo_version TEXT NOT NULL, -- 18.0
    module_version TEXT, -- 18.0.1.0.0

    -- Manifest data
    manifest JSONB NOT NULL,
    -- Full __manifest__.py as JSON

    -- Dependencies
    depends TEXT[],
    external_dependencies JSONB, -- {"python": [...], "bin": [...]}

    -- Classification
    category TEXT,
    application BOOLEAN DEFAULT false,
    installable BOOLEAN DEFAULT true,
    auto_install BOOLEAN DEFAULT false,

    -- Enterprise parity
    enterprise_equivalent TEXT, -- Enterprise module this replaces
    parity_level TEXT CHECK (parity_level IN ('full', 'partial', 'alternative', 'none')),
    parity_notes TEXT,

    -- Links
    entity_id UUID REFERENCES kg.entities(id),
    primary_doc_id UUID REFERENCES docs.documents(id),

    -- Stats
    install_order INT, -- Computed from dependency graph
    dependent_count INT DEFAULT 0, -- Modules that depend on this

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'deprecated', 'unmaintained')),

    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    UNIQUE (tenant_id, technical_name, odoo_version)
);

CREATE INDEX idx_modules_tenant ON kg.module_registry(tenant_id);
CREATE INDEX idx_modules_name ON kg.module_registry(technical_name);
CREATE INDEX idx_modules_version ON kg.module_registry(odoo_version);
CREATE INDEX idx_modules_type ON kg.module_registry(source_type);
CREATE INDEX idx_modules_category ON kg.module_registry(category);
CREATE INDEX idx_modules_depends ON kg.module_registry USING gin(depends);
CREATE INDEX idx_modules_enterprise ON kg.module_registry(enterprise_equivalent) WHERE enterprise_equivalent IS NOT NULL;

-- Enable RLS
ALTER TABLE kg.module_registry ENABLE ROW LEVEL SECURITY;

CREATE POLICY module_registry_tenant_isolation ON kg.module_registry
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE kg.module_registry IS 'OCA/Odoo module registry with dependency and parity info';

-- =============================================================================
-- 10. RUNTIME EXTENSIONS — Answers Table
-- =============================================================================

CREATE TABLE IF NOT EXISTS runtime.answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES core.tenants(id),
    query_id UUID NOT NULL REFERENCES runtime.queries(id) ON DELETE CASCADE,
    session_id UUID REFERENCES runtime.sessions(id),

    -- Answer content
    answer_text TEXT NOT NULL,
    answer_markdown TEXT,

    -- Model info
    model TEXT NOT NULL,
    provider TEXT,

    -- Citations
    citation_count INT DEFAULT 0,
    citations JSONB, -- [{chunk_id, score, snippet, url}]

    -- Quality signals
    confidence_score DECIMAL(5,4),
    has_code BOOLEAN DEFAULT false,
    has_table BOOLEAN DEFAULT false,

    -- Freshness of sources
    oldest_source_date TIMESTAMPTZ,
    newest_source_date TIMESTAMPTZ,
    avg_source_freshness DECIMAL(3,2),

    -- Tokens
    prompt_tokens INT,
    completion_tokens INT,
    total_tokens INT,

    -- Timing
    latency_ms INT,

    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_answers_query ON runtime.answers(query_id);
CREATE INDEX idx_answers_session ON runtime.answers(session_id);
CREATE INDEX idx_answers_tenant ON runtime.answers(tenant_id, created_at DESC);

-- Enable RLS
ALTER TABLE runtime.answers ENABLE ROW LEVEL SECURITY;

CREATE POLICY answers_tenant_isolation ON runtime.answers
    FOR ALL USING (tenant_id = core.current_tenant_id());

COMMENT ON TABLE runtime.answers IS 'Generated answers with citation metadata and quality signals';

-- =============================================================================
-- 11. HYBRID SEARCH FUNCTION
-- =============================================================================

CREATE OR REPLACE FUNCTION docs.hybrid_search(
    p_tenant_id UUID,
    p_query TEXT,
    p_query_embedding vector(1536),
    p_top_k INT DEFAULT 10,
    p_source_ids UUID[] DEFAULT NULL,
    p_module_names TEXT[] DEFAULT NULL,
    p_doc_types TEXT[] DEFAULT NULL,
    p_version TEXT DEFAULT NULL,
    p_vector_weight FLOAT DEFAULT 0.7,
    p_lexical_weight FLOAT DEFAULT 0.3
)
RETURNS TABLE (
    chunk_id UUID,
    document_id UUID,
    source_id UUID,
    content TEXT,
    heading_path TEXT,
    canonical_url TEXT,
    module_name TEXT,
    score FLOAT,
    vector_score FLOAT,
    lexical_score FLOAT
)
LANGUAGE plpgsql
STABLE
AS $func$
BEGIN
    RETURN QUERY
    WITH
    -- Vector search
    vector_results AS (
        SELECT
            c.id AS chunk_id,
            c.document_id,
            c.source_id,
            c.content,
            c.heading_path,
            d.canonical_url,
            d.module_name,
            (1 - (c.embedding <=> p_query_embedding))::FLOAT AS vscore
        FROM docs.chunks c
        JOIN docs.documents d ON d.id = c.document_id
        WHERE c.tenant_id = p_tenant_id
          AND c.embedding IS NOT NULL
          AND (p_source_ids IS NULL OR c.source_id = ANY(p_source_ids))
          AND (p_module_names IS NULL OR d.module_name = ANY(p_module_names))
          AND (p_doc_types IS NULL OR d.doc_type = ANY(p_doc_types))
          AND (p_version IS NULL OR d.version = p_version)
        ORDER BY c.embedding <=> p_query_embedding
        LIMIT p_top_k * 3
    ),
    -- Lexical search
    lexical_results AS (
        SELECT
            c.id AS chunk_id,
            c.document_id,
            c.source_id,
            c.content,
            c.heading_path,
            d.canonical_url,
            d.module_name,
            ts_rank_cd(c.tsv, plainto_tsquery('english', p_query))::FLOAT AS tscore
        FROM docs.chunks c
        JOIN docs.documents d ON d.id = c.document_id
        WHERE c.tenant_id = p_tenant_id
          AND c.tsv @@ plainto_tsquery('english', p_query)
          AND (p_source_ids IS NULL OR c.source_id = ANY(p_source_ids))
          AND (p_module_names IS NULL OR d.module_name = ANY(p_module_names))
          AND (p_doc_types IS NULL OR d.doc_type = ANY(p_doc_types))
          AND (p_version IS NULL OR d.version = p_version)
        ORDER BY ts_rank_cd(c.tsv, plainto_tsquery('english', p_query)) DESC
        LIMIT p_top_k * 3
    ),
    -- Combine and score
    combined AS (
        SELECT
            COALESCE(v.chunk_id, l.chunk_id) AS chunk_id,
            COALESCE(v.document_id, l.document_id) AS document_id,
            COALESCE(v.source_id, l.source_id) AS source_id,
            COALESCE(v.content, l.content) AS content,
            COALESCE(v.heading_path, l.heading_path) AS heading_path,
            COALESCE(v.canonical_url, l.canonical_url) AS canonical_url,
            COALESCE(v.module_name, l.module_name) AS module_name,
            COALESCE(v.vscore, 0)::FLOAT AS vscore,
            COALESCE(l.tscore, 0)::FLOAT AS tscore,
            (COALESCE(v.vscore, 0) * p_vector_weight +
             COALESCE(l.tscore, 0) * p_lexical_weight)::FLOAT AS combined_score
        FROM vector_results v
        FULL OUTER JOIN lexical_results l ON v.chunk_id = l.chunk_id
    )
    SELECT
        c.chunk_id,
        c.document_id,
        c.source_id,
        c.content,
        c.heading_path,
        c.canonical_url,
        c.module_name,
        c.combined_score AS score,
        c.vscore AS vector_score,
        c.tscore AS lexical_score
    FROM combined c
    ORDER BY c.combined_score DESC
    LIMIT p_top_k;
END;
$func$;

COMMENT ON FUNCTION docs.hybrid_search IS 'Hybrid vector + lexical search with filtering';

-- =============================================================================
-- 12. MODULE DEPENDENCY GRAPH FUNCTION
-- =============================================================================

CREATE OR REPLACE FUNCTION kg.get_module_install_order(
    p_tenant_id UUID,
    p_module_names TEXT[],
    p_odoo_version TEXT DEFAULT '18.0'
)
RETURNS TABLE (
    module_name TEXT,
    install_order INT,
    depends TEXT[],
    is_requested BOOLEAN
)
LANGUAGE plpgsql
STABLE
AS $func$
BEGIN
    RETURN QUERY
    WITH RECURSIVE deps AS (
        -- Start with requested modules
        SELECT
            m.technical_name,
            m.depends,
            0 AS depth,
            true AS is_requested
        FROM kg.module_registry m
        WHERE m.tenant_id = p_tenant_id
          AND m.technical_name = ANY(p_module_names)
          AND m.odoo_version = p_odoo_version

        UNION ALL

        -- Add dependencies
        SELECT
            m.technical_name,
            m.depends,
            d.depth + 1,
            false
        FROM deps d
        CROSS JOIN LATERAL unnest(d.depends) AS dep_name
        JOIN kg.module_registry m ON m.technical_name = dep_name
        WHERE m.tenant_id = p_tenant_id
          AND m.odoo_version = p_odoo_version
          AND d.depth < 20 -- Prevent infinite recursion
    )
    SELECT DISTINCT ON (deps.technical_name)
        deps.technical_name AS module_name,
        MAX(deps.depth) OVER (PARTITION BY deps.technical_name) AS install_order,
        deps.depends,
        bool_or(deps.is_requested) OVER (PARTITION BY deps.technical_name) AS is_requested
    FROM deps
    ORDER BY deps.technical_name, deps.depth DESC;
END;
$func$;

COMMENT ON FUNCTION kg.get_module_install_order IS 'Get module install order with full dependency tree';

-- =============================================================================
-- 13. VIEWS FOR DOCS BRAIN UI
-- =============================================================================

-- Source health overview
CREATE OR REPLACE VIEW sources.source_health AS
SELECT
    s.id,
    s.tenant_id,
    s.source_type,
    s.name,
    s.status,
    s.item_count,
    s.document_count,
    s.chunk_count,
    s.last_success_at,
    EXTRACT(EPOCH FROM (now() - s.last_success_at)) / 3600 AS hours_since_crawl,
    (SELECT cr.status FROM sources.crawl_runs cr WHERE cr.source_id = s.id ORDER BY cr.created_at DESC LIMIT 1) AS last_run_status,
    CASE
        WHEN s.status = 'disabled' THEN 'disabled'
        WHEN s.status = 'failed' THEN 'critical'
        WHEN s.last_success_at < now() - interval '7 days' THEN 'stale'
        WHEN s.last_success_at < now() - interval '24 hours' THEN 'warning'
        ELSE 'healthy'
    END AS health_status
FROM sources.sources s;

-- Module explorer view
CREATE OR REPLACE VIEW kg.module_explorer AS
SELECT
    m.id,
    m.tenant_id,
    m.technical_name,
    m.display_name,
    m.summary,
    m.source_type,
    m.category,
    m.odoo_version,
    m.depends,
    array_length(m.depends, 1) AS dependency_count,
    m.dependent_count,
    m.enterprise_equivalent,
    m.parity_level,
    m.install_order,
    d.canonical_url AS primary_doc_url,
    (SELECT COUNT(*) FROM docs.documents dd WHERE dd.module_name = m.technical_name) AS doc_count,
    (SELECT COUNT(*) FROM docs.chunks c JOIN docs.documents dd ON dd.id = c.document_id WHERE dd.module_name = m.technical_name) AS chunk_count
FROM kg.module_registry m
LEFT JOIN docs.documents d ON d.id = m.primary_doc_id;

-- Recent changes view
CREATE OR REPLACE VIEW sources.recent_changes AS
SELECT
    si.id,
    si.tenant_id,
    s.name AS source_name,
    s.source_type,
    si.canonical_url,
    si.title,
    si.changed_at,
    si.previous_content_hash,
    si.content_hash,
    d.id AS document_id,
    d.module_name
FROM sources.source_items si
JOIN sources.sources s ON s.id = si.source_id
LEFT JOIN docs.documents d ON d.source_item_id = si.id
WHERE si.changed_at IS NOT NULL
  AND si.changed_at > now() - interval '30 days'
ORDER BY si.changed_at DESC;

-- =============================================================================
-- 14. SEED DEFAULT SOURCES
-- =============================================================================

-- These will be tenant-specific, but here's the structure for common sources
-- Actual insertion should happen per-tenant during setup

COMMENT ON TABLE sources.sources IS 'Add sources like:
- Odoo CE 18 docs: https://www.odoo.com/documentation/18.0/
- OCA repos: https://github.com/OCA/*/18.0
- SAP Help: https://help.sap.com/docs/SAP_CONCUR (for reference)
- Internal SOPs: Notion workspaces';

COMMIT;
