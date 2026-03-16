-- =============================================================================
-- KNOWLEDGE HUB: BLOCKS AND CITATIONS
-- =============================================================================
-- Notebook blocks and citation tracking:
-- - kb.blocks: Notebook content blocks
-- - kb.citations: Output-to-source mappings
-- - kb.related_docs: Document relationship graph
-- =============================================================================

-- =============================================================================
-- BLOCK TYPE ENUM
-- =============================================================================

CREATE TYPE kb.block_type AS ENUM (
    'source',      -- Attached file/URL/Odoo reference
    'note',        -- Free text content
    'query',       -- SQL + result pointer
    'summary',     -- AI-generated synthesis
    'decision',    -- ADR-style record
    'task',        -- Spec-kit task
    'citation',    -- Chunk reference
    'export',      -- Render target marker
    'heading',     -- Section header
    'code',        -- Code block
    'image',       -- Inline image
    'table',       -- Data table
    'callout'      -- Alert/warning/info box
);

-- =============================================================================
-- BLOCKS (Notebook Content Atoms)
-- =============================================================================

CREATE TABLE kb.blocks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    notebook_id UUID NOT NULL REFERENCES kb.artifacts(id) ON DELETE CASCADE,
    parent_block_id UUID REFERENCES kb.blocks(id) ON DELETE CASCADE,
    block_type kb.block_type NOT NULL,
    ord INTEGER NOT NULL DEFAULT 0,
    content TEXT,
    content_json JSONB,  -- Structured content for complex blocks
    source_ref TEXT,     -- For source blocks: file URI / URL / odoo://
    source_title TEXT,   -- Display title for source
    query_sql TEXT,      -- For query blocks: the SQL
    query_result_uri TEXT,  -- S3 path to cached result
    metadata JSONB DEFAULT '{}',
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_blocks_tenant ON kb.blocks(tenant_id);
CREATE INDEX idx_blocks_notebook ON kb.blocks(notebook_id);
CREATE INDEX idx_blocks_parent ON kb.blocks(parent_block_id);
CREATE INDEX idx_blocks_type ON kb.blocks(block_type);
CREATE INDEX idx_blocks_ord ON kb.blocks(notebook_id, ord);

-- RLS for blocks
ALTER TABLE kb.blocks ENABLE ROW LEVEL SECURITY;

CREATE POLICY blocks_tenant_isolation ON kb.blocks
    USING (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

CREATE POLICY blocks_insert ON kb.blocks
    FOR INSERT WITH CHECK (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

-- =============================================================================
-- CITATIONS (Output-to-Source Mappings)
-- =============================================================================

CREATE TABLE kb.citations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    output_version_id UUID NOT NULL REFERENCES kb.versions(id) ON DELETE CASCADE,
    chunk_id UUID NOT NULL,  -- References rag.chunks if exists
    quote TEXT,              -- Extracted quote from chunk
    context TEXT,            -- Surrounding context
    score FLOAT,             -- Relevance score (0-1)
    citation_type TEXT DEFAULT 'supports',  -- supports, contradicts, elaborates
    position_start INTEGER,  -- Character position in output
    position_end INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT valid_score CHECK (score IS NULL OR (score >= 0 AND score <= 1))
);

CREATE INDEX idx_citations_tenant ON kb.citations(tenant_id);
CREATE INDEX idx_citations_output ON kb.citations(output_version_id);
CREATE INDEX idx_citations_chunk ON kb.citations(chunk_id);
CREATE INDEX idx_citations_type ON kb.citations(citation_type);

-- RLS for citations
ALTER TABLE kb.citations ENABLE ROW LEVEL SECURITY;

CREATE POLICY citations_tenant_isolation ON kb.citations
    USING (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

CREATE POLICY citations_insert ON kb.citations
    FOR INSERT WITH CHECK (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

-- =============================================================================
-- RELATED DOCS (Relationship Graph)
-- =============================================================================

CREATE TYPE kb.relationship_type AS ENUM (
    'prerequisite',    -- Must read before
    'see_also',        -- Related topic
    'supersedes',      -- Replaces older doc
    'example_of',      -- Example of concept
    'implements',      -- Implements spec
    'extends',         -- Extends concept
    'contradicts',     -- Conflicting info
    'derived_from',    -- Based on source
    'similar_to'       -- Semantically similar
);

CREATE TABLE kb.related_docs (
    source_artifact_id UUID NOT NULL REFERENCES kb.artifacts(id) ON DELETE CASCADE,
    target_artifact_id UUID NOT NULL REFERENCES kb.artifacts(id) ON DELETE CASCADE,
    relationship kb.relationship_type NOT NULL,
    weight FLOAT NOT NULL DEFAULT 1.0,
    is_computed BOOLEAN NOT NULL DEFAULT false,  -- true if from embedding similarity
    confidence FLOAT,  -- For computed relationships
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (source_artifact_id, target_artifact_id, relationship),
    CONSTRAINT valid_weight CHECK (weight >= 0 AND weight <= 1),
    CONSTRAINT no_self_ref CHECK (source_artifact_id != target_artifact_id)
);

CREATE INDEX idx_related_source ON kb.related_docs(source_artifact_id);
CREATE INDEX idx_related_target ON kb.related_docs(target_artifact_id);
CREATE INDEX idx_related_type ON kb.related_docs(relationship);

-- =============================================================================
-- EXPORT LOG (Track Notebook Exports)
-- =============================================================================

CREATE TABLE kb.export_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    notebook_id UUID NOT NULL REFERENCES kb.artifacts(id) ON DELETE CASCADE,
    output_artifact_id UUID NOT NULL REFERENCES kb.artifacts(id) ON DELETE CASCADE,
    export_type kb.artifact_type NOT NULL,
    block_count INTEGER NOT NULL,
    citation_count INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    exported_by TEXT NOT NULL,
    exported_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_export_tenant ON kb.export_log(tenant_id);
CREATE INDEX idx_export_notebook ON kb.export_log(notebook_id);
CREATE INDEX idx_export_output ON kb.export_log(output_artifact_id);

-- RLS for export_log
ALTER TABLE kb.export_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY export_log_tenant_isolation ON kb.export_log
    USING (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Get notebook with all blocks
CREATE OR REPLACE FUNCTION kb.get_notebook_blocks(p_notebook_id UUID)
RETURNS TABLE(
    id UUID,
    block_type kb.block_type,
    ord INTEGER,
    content TEXT,
    source_ref TEXT,
    source_title TEXT,
    metadata JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        b.id,
        b.block_type,
        b.ord,
        b.content,
        b.source_ref,
        b.source_title,
        b.metadata
    FROM kb.blocks b
    WHERE b.notebook_id = p_notebook_id
    ORDER BY b.ord;
END;
$$ LANGUAGE plpgsql STABLE;

-- Get citations for a version
CREATE OR REPLACE FUNCTION kb.get_version_citations(p_version_id UUID)
RETURNS TABLE(
    chunk_id UUID,
    quote TEXT,
    score FLOAT,
    citation_type TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.chunk_id,
        c.quote,
        c.score,
        c.citation_type
    FROM kb.citations c
    WHERE c.output_version_id = p_version_id
    ORDER BY c.position_start NULLS LAST, c.score DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- Get related documents
CREATE OR REPLACE FUNCTION kb.get_related_docs(p_artifact_id UUID)
RETURNS TABLE(
    artifact_id UUID,
    title TEXT,
    relationship kb.relationship_type,
    weight FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id as artifact_id,
        a.title,
        r.relationship,
        r.weight
    FROM kb.related_docs r
    JOIN kb.artifacts a ON a.id = r.target_artifact_id
    WHERE r.source_artifact_id = p_artifact_id
      AND a.status = 'published'
    ORDER BY r.weight DESC, a.title;
END;
$$ LANGUAGE plpgsql STABLE;

-- Reorder blocks (set ord for all blocks in notebook)
CREATE OR REPLACE FUNCTION kb.reorder_blocks(
    p_notebook_id UUID,
    p_block_ids UUID[]
)
RETURNS BOOLEAN AS $$
DECLARE
    i INTEGER := 0;
    block_id UUID;
BEGIN
    FOREACH block_id IN ARRAY p_block_ids LOOP
        UPDATE kb.blocks
        SET ord = i, updated_at = now()
        WHERE id = block_id AND notebook_id = p_notebook_id;
        i := i + 1;
    END LOOP;
    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'KB Blocks and Citations schema created';
    RAISE NOTICE 'Tables: kb.blocks, kb.citations, kb.related_docs, kb.export_log';
END;
$$;
