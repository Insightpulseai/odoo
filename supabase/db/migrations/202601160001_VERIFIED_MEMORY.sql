-- Migration: Create Agent Verified Memory System
-- Version: 202601160001
-- Description: Repository-scoped, cross-agent memory with citation verification
-- Author: Platform Team
-- Date: 2026-01-16
--
-- Based on GitHub Copilot's verified memory approach (Jan 2026):
-- - Memories stored with citations (code locations)
-- - Just-in-time verification at use-time
-- - Self-healing through citation checks
--
-- Reference: https://github.blog/changelog/2026-01-15-copilot-memory

-- ============================================================================
-- PHASE 1: CREATE IPAI SCHEMA IF NOT EXISTS
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS ipai;

COMMENT ON SCHEMA ipai IS 'InsightPulse AI internal schema for agent systems, memory, and orchestration.';

-- ============================================================================
-- PHASE 2: CREATE AGENT_MEMORY TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS ipai.agent_memory (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Scope: repository identifier (owner/name or internal repo id)
    repo            text NOT NULL,

    -- Memory content
    subject         text NOT NULL,
    fact            text NOT NULL,
    reason          text,

    -- Citations: [{path, line_start, line_end, sha?, snippet_hash?}...]
    -- - path: file path relative to repo root
    -- - line_start/line_end: line range for the citation
    -- - sha: optional commit SHA for version pinning
    -- - snippet_hash: optional hash of surrounding snippet for fuzzy matching
    citations       jsonb NOT NULL DEFAULT '[]'::jsonb,

    -- Audit trail
    created_by      text,                               -- user/agent id that created this memory
    created_at      timestamptz NOT NULL DEFAULT now(),
    refreshed_at    timestamptz NOT NULL DEFAULT now(), -- updated when memory is verified and still valid

    -- Lifecycle management
    status          text NOT NULL DEFAULT 'active'      -- active|superseded|invalid
        CHECK (status IN ('active', 'superseded', 'invalid')),
    supersedes_id   uuid REFERENCES ipai.agent_memory(id),

    -- Verification tracking
    last_verified_at    timestamptz,
    verification_count  integer NOT NULL DEFAULT 0,
    rejection_count     integer NOT NULL DEFAULT 0
);

COMMENT ON TABLE ipai.agent_memory IS 'Repository-scoped agent memory with citation verification. Memories are hypotheses verified just-in-time.';

COMMENT ON COLUMN ipai.agent_memory.repo IS 'Repository identifier (owner/name format)';
COMMENT ON COLUMN ipai.agent_memory.subject IS 'Short topic/category for the memory';
COMMENT ON COLUMN ipai.agent_memory.fact IS 'The durable convention or invariant being stored';
COMMENT ON COLUMN ipai.agent_memory.reason IS 'Why this memory was created (context for future verification)';
COMMENT ON COLUMN ipai.agent_memory.citations IS 'JSON array of code location citations that support this memory';
COMMENT ON COLUMN ipai.agent_memory.status IS 'Lifecycle status: active (usable), superseded (replaced by newer), invalid (citations contradicted)';
COMMENT ON COLUMN ipai.agent_memory.supersedes_id IS 'Reference to the memory this one replaced (creates correction chain)';
COMMENT ON COLUMN ipai.agent_memory.refreshed_at IS 'Timestamp of last successful verification (recency reflects usefulness)';

-- ============================================================================
-- PHASE 3: CREATE INDEXES
-- ============================================================================

-- Primary retrieval: most recent memories per repo
CREATE INDEX IF NOT EXISTS idx_agent_memory_repo_refreshed
    ON ipai.agent_memory (repo, refreshed_at DESC);

-- Filter by status
CREATE INDEX IF NOT EXISTS idx_agent_memory_repo_status
    ON ipai.agent_memory (repo, status);

-- Search within citations using GIN
CREATE INDEX IF NOT EXISTS idx_agent_memory_citations_gin
    ON ipai.agent_memory USING gin (citations);

-- Subject search for deduplication
CREATE INDEX IF NOT EXISTS idx_agent_memory_subject
    ON ipai.agent_memory (repo, subject);

-- Supersession chain traversal
CREATE INDEX IF NOT EXISTS idx_agent_memory_supersedes
    ON ipai.agent_memory (supersedes_id)
    WHERE supersedes_id IS NOT NULL;

-- ============================================================================
-- PHASE 4: PREVENT EXACT DUPLICATES
-- ============================================================================

-- Prevent exact duplicate subject+fact per repo
CREATE UNIQUE INDEX IF NOT EXISTS uq_agent_memory_repo_subject_fact
    ON ipai.agent_memory (repo, subject, fact)
    WHERE status = 'active';

-- ============================================================================
-- PHASE 5: CREATE MEMORY LOG TABLE (TELEMETRY)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ipai.agent_memory_log (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_id       uuid REFERENCES ipai.agent_memory(id) ON DELETE SET NULL,
    repo            text NOT NULL,
    event_type      text NOT NULL
        CHECK (event_type IN ('created', 'retrieved', 'verified', 'rejected', 'corrected', 'refreshed', 'invalidated')),
    agent_id        text,
    session_id      text,
    details         jsonb DEFAULT '{}'::jsonb,
    created_at      timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE ipai.agent_memory_log IS 'Telemetry log for memory operations. Used for monitoring and debugging.';

CREATE INDEX IF NOT EXISTS idx_agent_memory_log_repo_type
    ON ipai.agent_memory_log (repo, event_type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_agent_memory_log_memory_id
    ON ipai.agent_memory_log (memory_id)
    WHERE memory_id IS NOT NULL;

-- ============================================================================
-- PHASE 6: HELPER FUNCTIONS
-- ============================================================================

-- Function: Store a new memory (upsert on subject+fact)
CREATE OR REPLACE FUNCTION ipai.store_memory(
    p_repo text,
    p_subject text,
    p_fact text,
    p_citations jsonb DEFAULT '[]'::jsonb,
    p_reason text DEFAULT NULL,
    p_created_by text DEFAULT NULL
) RETURNS uuid AS $$
DECLARE
    v_memory_id uuid;
    v_existing_id uuid;
BEGIN
    -- Check for existing active memory with same subject+fact
    SELECT id INTO v_existing_id
    FROM ipai.agent_memory
    WHERE repo = p_repo
      AND subject = p_subject
      AND fact = p_fact
      AND status = 'active';

    IF v_existing_id IS NOT NULL THEN
        -- Refresh existing memory
        UPDATE ipai.agent_memory
        SET refreshed_at = now(),
            citations = p_citations,
            reason = COALESCE(p_reason, reason)
        WHERE id = v_existing_id
        RETURNING id INTO v_memory_id;

        -- Log refresh
        INSERT INTO ipai.agent_memory_log (memory_id, repo, event_type, agent_id, details)
        VALUES (v_memory_id, p_repo, 'refreshed', p_created_by, jsonb_build_object('citations', p_citations));
    ELSE
        -- Insert new memory
        INSERT INTO ipai.agent_memory (repo, subject, fact, citations, reason, created_by)
        VALUES (p_repo, p_subject, p_fact, p_citations, p_reason, p_created_by)
        RETURNING id INTO v_memory_id;

        -- Log creation
        INSERT INTO ipai.agent_memory_log (memory_id, repo, event_type, agent_id, details)
        VALUES (v_memory_id, p_repo, 'created', p_created_by, jsonb_build_object('citations', p_citations));
    END IF;

    RETURN v_memory_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION ipai.store_memory IS 'Store or refresh a memory. Returns memory ID.';

-- Function: Get recent memories for a repo
CREATE OR REPLACE FUNCTION ipai.get_recent_memories(
    p_repo text,
    p_limit integer DEFAULT 20
) RETURNS TABLE (
    id uuid,
    subject text,
    fact text,
    citations jsonb,
    reason text,
    refreshed_at timestamptz,
    verification_count integer
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.subject,
        m.fact,
        m.citations,
        m.reason,
        m.refreshed_at,
        m.verification_count
    FROM ipai.agent_memory m
    WHERE m.repo = p_repo
      AND m.status = 'active'
    ORDER BY m.refreshed_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION ipai.get_recent_memories IS 'Retrieve most recent active memories for a repository.';

-- Function: Mark memory as verified (bump verification count and refresh timestamp)
CREATE OR REPLACE FUNCTION ipai.verify_memory(
    p_memory_id uuid,
    p_agent_id text DEFAULT NULL
) RETURNS boolean AS $$
DECLARE
    v_repo text;
BEGIN
    UPDATE ipai.agent_memory
    SET last_verified_at = now(),
        refreshed_at = now(),
        verification_count = verification_count + 1
    WHERE id = p_memory_id
      AND status = 'active'
    RETURNING repo INTO v_repo;

    IF v_repo IS NOT NULL THEN
        -- Log verification
        INSERT INTO ipai.agent_memory_log (memory_id, repo, event_type, agent_id)
        VALUES (p_memory_id, v_repo, 'verified', p_agent_id);
        RETURN true;
    END IF;

    RETURN false;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION ipai.verify_memory IS 'Mark a memory as verified after citation check.';

-- Function: Invalidate a memory (mark as invalid, increment rejection count)
CREATE OR REPLACE FUNCTION ipai.invalidate_memory(
    p_memory_id uuid,
    p_agent_id text DEFAULT NULL,
    p_reason text DEFAULT NULL
) RETURNS boolean AS $$
DECLARE
    v_repo text;
BEGIN
    UPDATE ipai.agent_memory
    SET status = 'invalid',
        rejection_count = rejection_count + 1
    WHERE id = p_memory_id
      AND status = 'active'
    RETURNING repo INTO v_repo;

    IF v_repo IS NOT NULL THEN
        -- Log invalidation
        INSERT INTO ipai.agent_memory_log (memory_id, repo, event_type, agent_id, details)
        VALUES (p_memory_id, v_repo, 'invalidated', p_agent_id,
                jsonb_build_object('reason', COALESCE(p_reason, 'citation verification failed')));
        RETURN true;
    END IF;

    RETURN false;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION ipai.invalidate_memory IS 'Mark a memory as invalid when citations contradict.';

-- Function: Supersede a memory with a corrected version
CREATE OR REPLACE FUNCTION ipai.supersede_memory(
    p_old_memory_id uuid,
    p_repo text,
    p_subject text,
    p_fact text,
    p_citations jsonb DEFAULT '[]'::jsonb,
    p_reason text DEFAULT NULL,
    p_created_by text DEFAULT NULL
) RETURNS uuid AS $$
DECLARE
    v_new_memory_id uuid;
    v_repo text;
BEGIN
    -- Mark old memory as superseded
    UPDATE ipai.agent_memory
    SET status = 'superseded'
    WHERE id = p_old_memory_id
      AND status = 'active'
    RETURNING repo INTO v_repo;

    -- Insert new memory with supersedes reference
    INSERT INTO ipai.agent_memory (repo, subject, fact, citations, reason, created_by, supersedes_id)
    VALUES (p_repo, p_subject, p_fact, p_citations, p_reason, p_created_by, p_old_memory_id)
    RETURNING id INTO v_new_memory_id;

    -- Log correction
    INSERT INTO ipai.agent_memory_log (memory_id, repo, event_type, agent_id, details)
    VALUES (v_new_memory_id, p_repo, 'corrected', p_created_by,
            jsonb_build_object('superseded_id', p_old_memory_id, 'citations', p_citations));

    RETURN v_new_memory_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION ipai.supersede_memory IS 'Replace an incorrect memory with a corrected version.';

-- Function: Search memories by subject pattern
CREATE OR REPLACE FUNCTION ipai.search_memories(
    p_repo text,
    p_subject_pattern text DEFAULT NULL,
    p_limit integer DEFAULT 20
) RETURNS TABLE (
    id uuid,
    subject text,
    fact text,
    citations jsonb,
    reason text,
    refreshed_at timestamptz
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.subject,
        m.fact,
        m.citations,
        m.reason,
        m.refreshed_at
    FROM ipai.agent_memory m
    WHERE m.repo = p_repo
      AND m.status = 'active'
      AND (p_subject_pattern IS NULL OR m.subject ILIKE '%' || p_subject_pattern || '%')
    ORDER BY m.refreshed_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

COMMENT ON FUNCTION ipai.search_memories IS 'Search memories by subject pattern.';

-- ============================================================================
-- PHASE 7: GRANT PERMISSIONS
-- ============================================================================

-- Service role has full access
GRANT ALL ON SCHEMA ipai TO service_role;
GRANT ALL ON ALL TABLES IN SCHEMA ipai TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA ipai TO service_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ipai TO service_role;

-- Authenticated users can read memories (for dashboard/debugging)
GRANT USAGE ON SCHEMA ipai TO authenticated;
GRANT SELECT ON ipai.agent_memory TO authenticated;
GRANT SELECT ON ipai.agent_memory_log TO authenticated;

-- ============================================================================
-- PHASE 8: ROW LEVEL SECURITY (Optional - enable if multi-tenant)
-- ============================================================================

-- Uncomment to enable RLS:
-- ALTER TABLE ipai.agent_memory ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE ipai.agent_memory_log ENABLE ROW LEVEL SECURITY;

-- Example policies (customize for your auth model):
-- CREATE POLICY agent_memory_service_all ON ipai.agent_memory
--     FOR ALL TO service_role USING (true);

-- ============================================================================
-- PHASE 9: MEMORY STATS VIEW
-- ============================================================================

CREATE OR REPLACE VIEW ipai.agent_memory_stats AS
SELECT
    repo,
    status,
    COUNT(*) as memory_count,
    AVG(verification_count) as avg_verifications,
    AVG(rejection_count) as avg_rejections,
    MAX(refreshed_at) as last_activity,
    MIN(created_at) as first_memory
FROM ipai.agent_memory
GROUP BY repo, status
ORDER BY repo, status;

GRANT SELECT ON ipai.agent_memory_stats TO authenticated, service_role;

COMMENT ON VIEW ipai.agent_memory_stats IS 'Aggregated statistics for agent memory per repository.';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Verification queries (run manually):
-- SELECT * FROM ipai.agent_memory LIMIT 5;
-- SELECT * FROM ipai.agent_memory_stats;
-- SELECT ipai.store_memory('owner/repo', 'API versioning', 'Version must match in SDK and server', '[{"path":"src/sdk.ts","line_start":1}]'::jsonb, 'Prevents integration failures', 'migration');
