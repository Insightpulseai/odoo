-- Code Intelligence Schema
-- Stores semantic code chunks and code review events for Bugbot/Composer integration
--
-- Prerequisites:
--   - pgvector extension: CREATE EXTENSION IF NOT EXISTS vector;
--   - kb schema (from ipai_kb_chunks migration)
--   - observability schema

-- ============ Enable pgvector if not exists ============
CREATE EXTENSION IF NOT EXISTS vector;

-- ============ KB Schema (if not exists) ============
CREATE SCHEMA IF NOT EXISTS kb;

-- ============ Semantic Code Chunks ============
-- Stores code blocks with embeddings for semantic search / RAG

CREATE TABLE IF NOT EXISTS kb.code_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Location
    file_path TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,

    -- Semantic metadata
    chunk_type TEXT NOT NULL CHECK (chunk_type IN (
        'function', 'class', 'method', 'module', 'model', 'view', 'workflow', 'migration'
    )),
    chunk_name TEXT,                    -- e.g., 'create_invoice', 'ResPartner'
    language TEXT NOT NULL DEFAULT 'python',

    -- Content
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,         -- SHA256 for dedup

    -- Embedding (MiniLM L6 v2 = 384 dimensions)
    embedding VECTOR(384),

    -- Context
    metadata JSONB DEFAULT '{}',        -- imports, decorators, docstring, etc.
    dependencies JSONB DEFAULT '[]',    -- referenced modules/functions

    -- Versioning
    repo_sha TEXT NOT NULL,             -- Git commit SHA
    indexed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Soft delete
    deleted_at TIMESTAMPTZ
);

-- Indexes for search
CREATE INDEX IF NOT EXISTS code_chunks_embedding_idx
    ON kb.code_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS code_chunks_file_path_idx
    ON kb.code_chunks (file_path);

CREATE INDEX IF NOT EXISTS code_chunks_type_idx
    ON kb.code_chunks (chunk_type);

CREATE INDEX IF NOT EXISTS code_chunks_name_idx
    ON kb.code_chunks (chunk_name) WHERE chunk_name IS NOT NULL;

CREATE INDEX IF NOT EXISTS code_chunks_repo_sha_idx
    ON kb.code_chunks (repo_sha);

CREATE UNIQUE INDEX IF NOT EXISTS code_chunks_content_hash_sha_idx
    ON kb.code_chunks (content_hash, repo_sha) WHERE deleted_at IS NULL;

-- ============ Code Review Events (Bugbot) ============
-- Stores findings from AI code review tools

CREATE TABLE IF NOT EXISTS observability.code_review_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- PR context
    pr_number INTEGER NOT NULL,
    repo TEXT NOT NULL,
    pr_sha TEXT NOT NULL,

    -- Reviewer
    reviewer TEXT NOT NULL,             -- 'bugbot', 'coderabbit', 'human:<username>'
    reviewer_version TEXT,              -- Tool version if applicable

    -- Finding
    finding_type TEXT NOT NULL CHECK (finding_type IN (
        'bug', 'security', 'performance', 'style', 'logic', 'edge_case', 'other'
    )),
    severity TEXT NOT NULL CHECK (severity IN (
        'critical', 'high', 'medium', 'low', 'info'
    )),

    -- Location
    file_path TEXT NOT NULL,
    start_line INTEGER,
    end_line INTEGER,

    -- Content
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    suggestion TEXT,                    -- Proposed fix

    -- Resolution
    fixed BOOLEAN NOT NULL DEFAULT FALSE,
    fixed_at TIMESTAMPTZ,
    fixed_by TEXT,                      -- Who fixed it
    dismissed BOOLEAN NOT NULL DEFAULT FALSE,
    dismissed_reason TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for querying
CREATE INDEX IF NOT EXISTS code_review_events_pr_idx
    ON observability.code_review_events (repo, pr_number);

CREATE INDEX IF NOT EXISTS code_review_events_severity_idx
    ON observability.code_review_events (severity, finding_type);

CREATE INDEX IF NOT EXISTS code_review_events_fixed_idx
    ON observability.code_review_events (fixed, created_at DESC);

CREATE INDEX IF NOT EXISTS code_review_events_reviewer_idx
    ON observability.code_review_events (reviewer);

-- ============ RPC Functions ============

-- Semantic search for code chunks
CREATE OR REPLACE FUNCTION kb.search_code(
    p_query_embedding VECTOR(384),
    p_limit INTEGER DEFAULT 10,
    p_chunk_types TEXT[] DEFAULT NULL,
    p_file_pattern TEXT DEFAULT NULL
) RETURNS TABLE (
    id UUID,
    file_path TEXT,
    chunk_type TEXT,
    chunk_name TEXT,
    content TEXT,
    start_line INTEGER,
    end_line INTEGER,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cc.id,
        cc.file_path,
        cc.chunk_type,
        cc.chunk_name,
        cc.content,
        cc.start_line,
        cc.end_line,
        1 - (cc.embedding <=> p_query_embedding) AS similarity
    FROM kb.code_chunks cc
    WHERE cc.deleted_at IS NULL
      AND cc.embedding IS NOT NULL
      AND (p_chunk_types IS NULL OR cc.chunk_type = ANY(p_chunk_types))
      AND (p_file_pattern IS NULL OR cc.file_path LIKE p_file_pattern)
    ORDER BY cc.embedding <=> p_query_embedding
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Get code review stats
CREATE OR REPLACE FUNCTION observability.get_code_review_stats(
    p_repo TEXT DEFAULT NULL,
    p_days INTEGER DEFAULT 30
) RETURNS TABLE (
    reviewer TEXT,
    total_findings BIGINT,
    critical_count BIGINT,
    high_count BIGINT,
    fixed_count BIGINT,
    fix_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        cre.reviewer,
        COUNT(*) AS total_findings,
        COUNT(*) FILTER (WHERE cre.severity = 'critical') AS critical_count,
        COUNT(*) FILTER (WHERE cre.severity = 'high') AS high_count,
        COUNT(*) FILTER (WHERE cre.fixed) AS fixed_count,
        ROUND(
            COUNT(*) FILTER (WHERE cre.fixed)::NUMERIC /
            NULLIF(COUNT(*), 0) * 100,
            2
        ) AS fix_rate
    FROM observability.code_review_events cre
    WHERE (p_repo IS NULL OR cre.repo = p_repo)
      AND cre.created_at > NOW() - (p_days || ' days')::INTERVAL
    GROUP BY cre.reviewer
    ORDER BY total_findings DESC;
END;
$$ LANGUAGE plpgsql;

-- Upsert code chunk (for incremental indexing)
CREATE OR REPLACE FUNCTION kb.upsert_code_chunk(
    p_file_path TEXT,
    p_start_line INTEGER,
    p_end_line INTEGER,
    p_chunk_type TEXT,
    p_chunk_name TEXT,
    p_language TEXT,
    p_content TEXT,
    p_embedding VECTOR(384),
    p_metadata JSONB,
    p_repo_sha TEXT
) RETURNS UUID AS $$
DECLARE
    v_content_hash TEXT;
    v_id UUID;
BEGIN
    -- Compute content hash
    v_content_hash := encode(sha256(p_content::bytea), 'hex');

    -- Check if unchanged
    SELECT id INTO v_id
    FROM kb.code_chunks
    WHERE content_hash = v_content_hash
      AND repo_sha = p_repo_sha
      AND deleted_at IS NULL
    LIMIT 1;

    IF v_id IS NOT NULL THEN
        -- Already indexed, return existing
        RETURN v_id;
    END IF;

    -- Soft delete old version
    UPDATE kb.code_chunks
    SET deleted_at = NOW()
    WHERE file_path = p_file_path
      AND start_line = p_start_line
      AND end_line = p_end_line
      AND deleted_at IS NULL;

    -- Insert new
    INSERT INTO kb.code_chunks (
        file_path, start_line, end_line, chunk_type, chunk_name,
        language, content, content_hash, embedding, metadata, repo_sha
    ) VALUES (
        p_file_path, p_start_line, p_end_line, p_chunk_type, p_chunk_name,
        p_language, p_content, v_content_hash, p_embedding, p_metadata, p_repo_sha
    )
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- ============ Grants ============
GRANT USAGE ON SCHEMA kb TO service_role, authenticated;
GRANT SELECT ON kb.code_chunks TO service_role, authenticated;
GRANT INSERT, UPDATE ON kb.code_chunks TO service_role;
GRANT EXECUTE ON FUNCTION kb.search_code TO service_role, authenticated;
GRANT EXECUTE ON FUNCTION kb.upsert_code_chunk TO service_role;

GRANT SELECT ON observability.code_review_events TO service_role, authenticated;
GRANT INSERT, UPDATE ON observability.code_review_events TO service_role;
GRANT EXECUTE ON FUNCTION observability.get_code_review_stats TO service_role, authenticated;

-- Comments
COMMENT ON TABLE kb.code_chunks IS 'Semantic code chunks with embeddings for RAG/search';
COMMENT ON TABLE observability.code_review_events IS 'AI code review findings (Bugbot, etc.)';
COMMENT ON FUNCTION kb.search_code IS 'Semantic search over code chunks using embeddings';
COMMENT ON FUNCTION kb.upsert_code_chunk IS 'Upsert code chunk with deduplication';
