-- Migration: IPAI KB Chunks Schema
-- Purpose: Create knowledge base chunks table for RAG retrieval
-- Target: Supabase (external managed database with pgvector)
--
-- This schema is designed to be applied to Supabase for vector search.
-- The chunks table stores indexed content from various sources
-- (Odoo tasks, KB articles, external docs) for AI retrieval.
--
-- Environment: Supabase project spdtwktxdalcfigzeqrz

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS vector;

-- Create kb schema if not exists
CREATE SCHEMA IF NOT EXISTS kb;

-- Grant usage to authenticated users
GRANT USAGE ON SCHEMA kb TO authenticated;
GRANT USAGE ON SCHEMA kb TO service_role;

-- ============================================================================
-- kb.chunks - Main knowledge base chunks table
-- ============================================================================
-- Stores chunked content from various sources for RAG retrieval.
-- Each chunk represents a searchable piece of knowledge with metadata
-- and optional vector embedding for semantic search.
-- ============================================================================

CREATE TABLE IF NOT EXISTS kb.chunks (
    id BIGSERIAL PRIMARY KEY,

    -- Tenant isolation (maps to Odoo company)
    tenant_ref TEXT NOT NULL,

    -- Source identification
    source_type TEXT NOT NULL,  -- 'odoo_task', 'odoo_kb', 'github', 'docs', etc.
    source_ref TEXT NOT NULL,   -- Stable identifier like 'project.task:123'

    -- Content metadata
    title TEXT,
    url TEXT,                   -- Deep link to original source
    content TEXT NOT NULL,      -- Actual chunk content

    -- Vector embedding for semantic search (OpenAI text-embedding-3-small dimension)
    embedding vector(1536),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Unique constraint for upsert operations
CREATE UNIQUE INDEX IF NOT EXISTS kb_chunks_uq
    ON kb.chunks (tenant_ref, source_type, source_ref);

-- Index for tenant-scoped queries
CREATE INDEX IF NOT EXISTS kb_chunks_tenant_idx
    ON kb.chunks (tenant_ref);

-- Index for source type filtering
CREATE INDEX IF NOT EXISTS kb_chunks_source_type_idx
    ON kb.chunks (source_type);

-- Vector index for similarity search (IVFFlat for balance of speed/accuracy)
CREATE INDEX IF NOT EXISTS kb_chunks_embedding_idx
    ON kb.chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ============================================================================
-- RPC: kb.search_chunks - Vector similarity search
-- ============================================================================
-- Primary search function using vector embeddings.
-- Returns chunks ranked by cosine similarity to query embedding.
--
-- Parameters:
--   p_tenant_ref: Tenant identifier (e.g., 'odoo_company:1')
--   p_query_embedding: Query vector (1536 dimensions)
--   p_limit: Maximum results to return (default 8)
--
-- Returns: Table of chunks with similarity score
-- ============================================================================

CREATE OR REPLACE FUNCTION kb.search_chunks(
    p_tenant_ref TEXT,
    p_query_embedding vector(1536),
    p_limit INT DEFAULT 8
) RETURNS TABLE (
    id BIGINT,
    title TEXT,
    url TEXT,
    content TEXT,
    score FLOAT
) LANGUAGE sql STABLE AS $$
    SELECT
        c.id,
        c.title,
        c.url,
        c.content,
        1 - (c.embedding <=> p_query_embedding) AS score
    FROM kb.chunks c
    WHERE c.tenant_ref = p_tenant_ref
      AND c.embedding IS NOT NULL
    ORDER BY c.embedding <=> p_query_embedding
    LIMIT p_limit;
$$;

-- Grant execute to authenticated users
GRANT EXECUTE ON FUNCTION kb.search_chunks(TEXT, vector, INT) TO authenticated;
GRANT EXECUTE ON FUNCTION kb.search_chunks(TEXT, vector, INT) TO service_role;

-- ============================================================================
-- RPC: kb.search_chunks_text - Text-based fallback search
-- ============================================================================
-- Fallback search function using text matching.
-- Used when embeddings are not available or as a supplement to vector search.
--
-- Parameters:
--   p_tenant_ref: Tenant identifier (e.g., 'odoo_company:1')
--   p_query: Search query text
--   p_limit: Maximum results to return (default 8)
--
-- Returns: Table of chunks matching query (score always 0.0)
-- ============================================================================

CREATE OR REPLACE FUNCTION kb.search_chunks_text(
    p_tenant_ref TEXT,
    p_query TEXT,
    p_limit INT DEFAULT 8
) RETURNS TABLE (
    id BIGINT,
    title TEXT,
    url TEXT,
    content TEXT,
    score FLOAT
) LANGUAGE sql STABLE AS $$
    SELECT
        c.id,
        c.title,
        c.url,
        c.content,
        0.0::FLOAT AS score
    FROM kb.chunks c
    WHERE c.tenant_ref = p_tenant_ref
      AND (
          c.title ILIKE ('%' || p_query || '%')
          OR c.content ILIKE ('%' || p_query || '%')
      )
    ORDER BY c.updated_at DESC
    LIMIT p_limit;
$$;

-- Grant execute to authenticated users
GRANT EXECUTE ON FUNCTION kb.search_chunks_text(TEXT, TEXT, INT) TO authenticated;
GRANT EXECUTE ON FUNCTION kb.search_chunks_text(TEXT, TEXT, INT) TO service_role;

-- ============================================================================
-- RLS Policies for tenant isolation
-- ============================================================================
-- Enable row-level security to ensure tenants can only access their own data.
-- Service role bypasses RLS for admin operations.
-- ============================================================================

ALTER TABLE kb.chunks ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only read their own tenant's chunks
CREATE POLICY "Tenant isolation read" ON kb.chunks
    FOR SELECT
    USING (tenant_ref = current_setting('request.jwt.claims', true)::json->>'tenant_ref');

-- Policy: Service role can do anything (for exporter)
CREATE POLICY "Service role full access" ON kb.chunks
    FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

-- Grant table access
GRANT SELECT ON kb.chunks TO authenticated;
GRANT ALL ON kb.chunks TO service_role;
GRANT USAGE, SELECT ON SEQUENCE kb.chunks_id_seq TO service_role;

-- ============================================================================
-- Trigger: Auto-update updated_at timestamp
-- ============================================================================

CREATE OR REPLACE FUNCTION kb.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER kb_chunks_updated_at
    BEFORE UPDATE ON kb.chunks
    FOR EACH ROW
    EXECUTE FUNCTION kb.update_updated_at_column();

-- ============================================================================
-- Comments for documentation
-- ============================================================================

COMMENT ON TABLE kb.chunks IS 'Knowledge base chunks for RAG retrieval. Stores indexed content from Odoo and external sources.';
COMMENT ON COLUMN kb.chunks.tenant_ref IS 'Tenant identifier for multi-tenant isolation (e.g., odoo_company:1)';
COMMENT ON COLUMN kb.chunks.source_type IS 'Type of source: odoo_task, odoo_kb, github, docs, etc.';
COMMENT ON COLUMN kb.chunks.source_ref IS 'Stable unique identifier within source (e.g., project.task:123)';
COMMENT ON COLUMN kb.chunks.title IS 'Human-readable title for the chunk';
COMMENT ON COLUMN kb.chunks.url IS 'Deep link URL to the original source';
COMMENT ON COLUMN kb.chunks.content IS 'Actual text content of the chunk';
COMMENT ON COLUMN kb.chunks.embedding IS 'Vector embedding for semantic search (1536 dimensions for OpenAI text-embedding-3-small)';

COMMENT ON FUNCTION kb.search_chunks IS 'Vector similarity search for RAG retrieval. Returns chunks ranked by cosine similarity.';
COMMENT ON FUNCTION kb.search_chunks_text IS 'Text-based fallback search when embeddings unavailable.';
