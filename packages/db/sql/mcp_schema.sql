-- MCP Multi-Tier Architecture - Supabase Schema
-- Production-grade MCP tables with pgvector and RLS

-- Create MCP schema
CREATE SCHEMA IF NOT EXISTS mcp;

-- Enable pgvector extension for embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- Skills Registry (promoted from Git via CI)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mcp.skills_registry (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT,
    status TEXT CHECK(status IN ('stable', 'approved')) NOT NULL DEFAULT 'approved',
    metadata JSONB DEFAULT '{}'::jsonb,
    file_path TEXT,
    promoted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    promoted_by TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_skills_status ON mcp.skills_registry(status);
CREATE INDEX IF NOT EXISTS idx_skills_name ON mcp.skills_registry(name);
CREATE INDEX IF NOT EXISTS idx_skills_metadata ON mcp.skills_registry USING gin(metadata);

COMMENT ON TABLE mcp.skills_registry IS 'Production skills promoted from local dev via CI/CD';
COMMENT ON COLUMN mcp.skills_registry.status IS 'Only stable and approved skills allowed in production';

-- ============================================================================
-- RAG Embeddings (production corpora)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mcp.rag_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    corpus TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(1536), -- OpenAI ada-002 or similar
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vector similarity index (ivfflat for performance)
CREATE INDEX IF NOT EXISTS idx_rag_embeddings_vector
    ON mcp.rag_embeddings USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_rag_corpus ON mcp.rag_embeddings(corpus);
CREATE INDEX IF NOT EXISTS idx_rag_metadata ON mcp.rag_embeddings USING gin(metadata);

COMMENT ON TABLE mcp.rag_embeddings IS 'Production RAG corpora with vector embeddings';
COMMENT ON COLUMN mcp.rag_embeddings.embedding IS 'Vector embedding (1536 dimensions for OpenAI ada-002)';

-- ============================================================================
-- Usage Metrics (aggregated only, no conversation history)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mcp.usage_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation TEXT NOT NULL,
    target TEXT, -- odoo_prod, odoo_lab
    latency_ms INTEGER,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON mcp.usage_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_usage_operation ON mcp.usage_metrics(operation);
CREATE INDEX IF NOT EXISTS idx_usage_target ON mcp.usage_metrics(target);
CREATE INDEX IF NOT EXISTS idx_usage_success ON mcp.usage_metrics(success);

COMMENT ON TABLE mcp.usage_metrics IS 'Aggregated usage metrics (no conversation history)';

-- ============================================================================
-- Coordinator Routing Cache (Redis alternative)
-- ============================================================================
CREATE TABLE IF NOT EXISTS mcp.routing_cache (
    cache_key TEXT PRIMARY KEY,
    target TEXT NOT NULL,
    confidence FLOAT,
    metadata JSONB DEFAULT '{}'::jsonb,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_routing_expires ON mcp.routing_cache(expires_at);

COMMENT ON TABLE mcp.routing_cache IS 'Routing decision cache (TTL-based)';

-- ============================================================================
-- Row-Level Security Policies
-- ============================================================================

-- Skills: Read-only for MCP clients (approved/stable only)
ALTER TABLE mcp.skills_registry ENABLE ROW LEVEL SECURITY;

CREATE POLICY "mcp_clients_read_approved_skills"
    ON mcp.skills_registry FOR SELECT
    USING (status IN ('stable', 'approved'));

-- RAG: Read-only for MCP clients
ALTER TABLE mcp.rag_embeddings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "mcp_clients_read_rag"
    ON mcp.rag_embeddings FOR SELECT
    USING (true);

-- Usage Metrics: Write-only for MCP coordinator
ALTER TABLE mcp.usage_metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "mcp_coordinator_write_metrics"
    ON mcp.usage_metrics FOR INSERT
    WITH CHECK (true);

-- Routing Cache: Read/Write for coordinator only
ALTER TABLE mcp.routing_cache ENABLE ROW LEVEL SECURITY;

CREATE POLICY "mcp_coordinator_manage_cache"
    ON mcp.routing_cache
    USING (true)
    WITH CHECK (true);

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Semantic search function
CREATE OR REPLACE FUNCTION mcp.search_rag(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10,
    filter_corpus text DEFAULT NULL
)
RETURNS TABLE (
    id uuid,
    corpus text,
    chunk_text text,
    similarity float,
    metadata jsonb
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.id,
        r.corpus,
        r.chunk_text,
        1 - (r.embedding <=> query_embedding) as similarity,
        r.metadata
    FROM mcp.rag_embeddings r
    WHERE (filter_corpus IS NULL OR r.corpus = filter_corpus)
        AND 1 - (r.embedding <=> query_embedding) > match_threshold
    ORDER BY r.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

COMMENT ON FUNCTION mcp.search_rag IS 'Semantic search across RAG embeddings';

-- Cleanup expired cache entries
CREATE OR REPLACE FUNCTION mcp.cleanup_routing_cache()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM mcp.routing_cache
    WHERE expires_at < NOW();
END;
$$;

COMMENT ON FUNCTION mcp.cleanup_routing_cache IS 'Remove expired routing cache entries';

-- Trigger to auto-update updated_at
CREATE OR REPLACE FUNCTION mcp.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON mcp.skills_registry
    FOR EACH ROW EXECUTE FUNCTION mcp.update_updated_at_column();

CREATE TRIGGER update_rag_updated_at BEFORE UPDATE ON mcp.rag_embeddings
    FOR EACH ROW EXECUTE FUNCTION mcp.update_updated_at_column();

-- ============================================================================
-- Sample Data (for testing)
-- ============================================================================

-- Insert sample skill
INSERT INTO mcp.skills_registry (id, name, version, status, metadata, file_path, promoted_by)
VALUES (
    'odoo-developer-prod-001',
    'odoo-developer',
    '1.0.0',
    'approved',
    '{"description": "Odoo CE 18.0 development expert (production)", "triggers": ["odoo", "module", "xml", "python"]}'::jsonb,
    'skills/odoo-developer.yaml',
    'ci-pipeline'
)
ON CONFLICT (id) DO NOTHING;

-- Grant usage to service role
GRANT USAGE ON SCHEMA mcp TO service_role;
GRANT ALL ON ALL TABLES IN SCHEMA mcp TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA mcp TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA mcp TO service_role;

-- Grant read access to authenticated users
GRANT USAGE ON SCHEMA mcp TO authenticated;
GRANT SELECT ON mcp.skills_registry TO authenticated;
GRANT SELECT ON mcp.rag_embeddings TO authenticated;
GRANT SELECT ON mcp.usage_metrics TO authenticated;
