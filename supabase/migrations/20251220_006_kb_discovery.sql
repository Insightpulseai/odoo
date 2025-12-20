-- =============================================================================
-- KNOWLEDGE HUB: DISCOVERY FEATURES
-- =============================================================================
-- Discovery and learning features:
-- - kb.glossary_terms: Canonical definitions
-- - kb.journeys: Learning paths
-- - kb.journey_steps: Path steps
-- - rag.search_logs: Query analytics
-- =============================================================================

-- =============================================================================
-- GLOSSARY TERMS
-- =============================================================================

CREATE TABLE kb.glossary_terms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    term TEXT NOT NULL,
    definition TEXT NOT NULL,
    acronym_expansion TEXT,        -- If term is acronym
    product_context TEXT,          -- odoo-ce, sap, platform, etc.
    synonyms TEXT[] DEFAULT '{}',
    see_also UUID[],               -- Other glossary term IDs
    authoritative_artifact_id UUID REFERENCES kb.artifacts(id),
    anchor_id TEXT,                -- Anchor within artifact
    examples TEXT[],               -- Usage examples
    is_deprecated BOOLEAN DEFAULT false,
    successor_term_id UUID REFERENCES kb.glossary_terms(id),
    metadata JSONB DEFAULT '{}',
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_term_context UNIQUE (tenant_id, term, product_context)
);

CREATE INDEX idx_glossary_tenant ON kb.glossary_terms(tenant_id);
CREATE INDEX idx_glossary_term ON kb.glossary_terms(term);
CREATE INDEX idx_glossary_term_prefix ON kb.glossary_terms(term text_pattern_ops);
CREATE INDEX idx_glossary_product ON kb.glossary_terms(product_context);
CREATE INDEX idx_glossary_synonyms ON kb.glossary_terms USING GIN (synonyms);
CREATE INDEX idx_glossary_active ON kb.glossary_terms(tenant_id, term)
    WHERE is_deprecated = false;

-- RLS for glossary
ALTER TABLE kb.glossary_terms ENABLE ROW LEVEL SECURITY;

CREATE POLICY glossary_tenant_isolation ON kb.glossary_terms
    USING (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

CREATE POLICY glossary_insert ON kb.glossary_terms
    FOR INSERT WITH CHECK (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

-- =============================================================================
-- LEARNING JOURNEYS
-- =============================================================================

CREATE TYPE kb.difficulty_level AS ENUM (
    'beginner',
    'intermediate',
    'advanced',
    'expert'
);

CREATE TABLE kb.journeys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    product TEXT NOT NULL,
    difficulty kb.difficulty_level NOT NULL DEFAULT 'intermediate',
    estimated_hours FLOAT,
    prerequisites TEXT[],          -- Other journey slugs
    tags TEXT[] DEFAULT '{}',
    certification_slug TEXT,       -- If completion grants cert
    badge_image_uri TEXT,
    is_published BOOLEAN NOT NULL DEFAULT false,
    is_featured BOOLEAN NOT NULL DEFAULT false,
    author TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_journey_slug UNIQUE (tenant_id, slug)
);

CREATE INDEX idx_journeys_tenant ON kb.journeys(tenant_id);
CREATE INDEX idx_journeys_product ON kb.journeys(product);
CREATE INDEX idx_journeys_published ON kb.journeys(tenant_id, is_published)
    WHERE is_published = true;
CREATE INDEX idx_journeys_featured ON kb.journeys(is_featured)
    WHERE is_featured = true;
CREATE INDEX idx_journeys_tags ON kb.journeys USING GIN (tags);

-- RLS for journeys
ALTER TABLE kb.journeys ENABLE ROW LEVEL SECURITY;

CREATE POLICY journeys_tenant_isolation ON kb.journeys
    USING (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

CREATE POLICY journeys_insert ON kb.journeys
    FOR INSERT WITH CHECK (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

-- =============================================================================
-- JOURNEY STEPS
-- =============================================================================

CREATE TABLE kb.journey_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    journey_id UUID NOT NULL REFERENCES kb.journeys(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    artifact_id UUID REFERENCES kb.artifacts(id) ON DELETE SET NULL,
    external_url TEXT,             -- If pointing to external resource
    title_override TEXT,
    description TEXT,
    estimated_minutes INTEGER,
    is_optional BOOLEAN DEFAULT false,
    is_checkpoint BOOLEAN DEFAULT false,  -- Requires quiz/assessment
    quiz_id UUID,                  -- If checkpoint
    prereq_step_ids UUID[],        -- Steps that must be completed first
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_journey_step UNIQUE (journey_id, step_order),
    CONSTRAINT has_content CHECK (artifact_id IS NOT NULL OR external_url IS NOT NULL)
);

CREATE INDEX idx_steps_journey ON kb.journey_steps(journey_id);
CREATE INDEX idx_steps_artifact ON kb.journey_steps(artifact_id);
CREATE INDEX idx_steps_order ON kb.journey_steps(journey_id, step_order);

-- RLS for journey_steps
ALTER TABLE kb.journey_steps ENABLE ROW LEVEL SECURITY;

CREATE POLICY steps_tenant_isolation ON kb.journey_steps
    USING (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

CREATE POLICY steps_insert ON kb.journey_steps
    FOR INSERT WITH CHECK (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

-- =============================================================================
-- USER JOURNEY PROGRESS (Runtime Schema)
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS runtime;

CREATE TABLE IF NOT EXISTS runtime.journey_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    user_id TEXT NOT NULL,
    journey_id UUID NOT NULL REFERENCES kb.journeys(id) ON DELETE CASCADE,
    step_id UUID NOT NULL REFERENCES kb.journey_steps(id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    quiz_score FLOAT,
    time_spent_seconds INTEGER,
    notes TEXT,

    CONSTRAINT unique_user_step UNIQUE (user_id, step_id)
);

CREATE INDEX idx_progress_user ON runtime.journey_progress(user_id);
CREATE INDEX idx_progress_journey ON runtime.journey_progress(journey_id);
CREATE INDEX idx_progress_completed ON runtime.journey_progress(completed_at)
    WHERE completed_at IS NOT NULL;

-- RLS for progress
ALTER TABLE runtime.journey_progress ENABLE ROW LEVEL SECURITY;

CREATE POLICY progress_user_isolation ON runtime.journey_progress
    USING (user_id = auth.jwt()->>'sub');

-- =============================================================================
-- SEARCH LOGS (Query Analytics)
-- =============================================================================

CREATE TABLE IF NOT EXISTS rag.search_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    session_id TEXT,
    user_id TEXT,
    query TEXT NOT NULL,
    query_embedding_id UUID,       -- If vector search was used
    filters JSONB,
    result_count INTEGER NOT NULL,
    top_results UUID[],            -- Artifact IDs of top results
    clicked_artifact_id UUID,
    click_position INTEGER,
    latency_ms INTEGER,
    search_type TEXT DEFAULT 'hybrid',  -- hybrid, bm25, vector
    feedback TEXT,                 -- thumbs_up, thumbs_down, null
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_search_tenant ON rag.search_logs(tenant_id);
CREATE INDEX idx_search_time ON rag.search_logs(created_at DESC);
CREATE INDEX idx_search_query ON rag.search_logs(query);
CREATE INDEX idx_search_zero ON rag.search_logs(tenant_id, query)
    WHERE result_count = 0;
CREATE INDEX idx_search_session ON rag.search_logs(session_id);

-- RLS for search_logs
ALTER TABLE rag.search_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY search_logs_tenant_isolation ON rag.search_logs
    USING (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Glossary lookup with fuzzy matching
CREATE OR REPLACE FUNCTION kb.lookup_glossary(
    p_term TEXT,
    p_product TEXT DEFAULT NULL,
    p_fuzzy BOOLEAN DEFAULT false
)
RETURNS TABLE(
    id UUID,
    term TEXT,
    definition TEXT,
    product_context TEXT,
    synonyms TEXT[],
    similarity FLOAT
) AS $$
BEGIN
    IF p_fuzzy AND EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm') THEN
        RETURN QUERY
        SELECT
            g.id,
            g.term,
            g.definition,
            g.product_context,
            g.synonyms,
            similarity(g.term, p_term) as sim
        FROM kb.glossary_terms g
        WHERE g.is_deprecated = false
          AND (p_product IS NULL OR g.product_context = p_product)
          AND similarity(g.term, p_term) > 0.3
        ORDER BY sim DESC
        LIMIT 10;
    ELSE
        RETURN QUERY
        SELECT
            g.id,
            g.term,
            g.definition,
            g.product_context,
            g.synonyms,
            1.0::FLOAT as sim
        FROM kb.glossary_terms g
        WHERE g.is_deprecated = false
          AND (p_product IS NULL OR g.product_context = p_product)
          AND (g.term ILIKE p_term || '%' OR p_term = ANY(g.synonyms))
        ORDER BY g.term
        LIMIT 20;
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;

-- Get journey with progress for user
CREATE OR REPLACE FUNCTION kb.get_journey_progress(
    p_journey_id UUID,
    p_user_id TEXT
)
RETURNS TABLE(
    step_id UUID,
    step_order INTEGER,
    artifact_id UUID,
    title TEXT,
    is_optional BOOLEAN,
    is_completed BOOLEAN,
    completed_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id as step_id,
        s.step_order,
        s.artifact_id,
        COALESCE(s.title_override, a.title) as title,
        s.is_optional,
        p.completed_at IS NOT NULL as is_completed,
        p.completed_at
    FROM kb.journey_steps s
    LEFT JOIN kb.artifacts a ON a.id = s.artifact_id
    LEFT JOIN runtime.journey_progress p ON p.step_id = s.id AND p.user_id = p_user_id
    WHERE s.journey_id = p_journey_id
    ORDER BY s.step_order;
END;
$$ LANGUAGE plpgsql STABLE;

-- Complete a journey step
CREATE OR REPLACE FUNCTION kb.complete_journey_step(
    p_user_id TEXT,
    p_step_id UUID,
    p_quiz_score FLOAT DEFAULT NULL,
    p_time_spent INTEGER DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    v_journey_id UUID;
    v_tenant_id UUID;
BEGIN
    -- Get journey and tenant
    SELECT journey_id, tenant_id INTO v_journey_id, v_tenant_id
    FROM kb.journey_steps
    WHERE id = p_step_id;

    IF v_journey_id IS NULL THEN
        RAISE EXCEPTION 'Step not found: %', p_step_id;
    END IF;

    -- Upsert progress
    INSERT INTO runtime.journey_progress (
        tenant_id, user_id, journey_id, step_id,
        completed_at, quiz_score, time_spent_seconds
    )
    VALUES (
        v_tenant_id, p_user_id, v_journey_id, p_step_id,
        now(), p_quiz_score, p_time_spent
    )
    ON CONFLICT (user_id, step_id)
    DO UPDATE SET
        completed_at = now(),
        quiz_score = COALESCE(p_quiz_score, runtime.journey_progress.quiz_score),
        time_spent_seconds = COALESCE(p_time_spent, runtime.journey_progress.time_spent_seconds);

    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- Zero-result query analysis
CREATE OR REPLACE FUNCTION rag.get_zero_result_queries(
    p_days INTEGER DEFAULT 7,
    p_min_count INTEGER DEFAULT 3
)
RETURNS TABLE(
    query TEXT,
    count BIGINT,
    last_seen TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sl.query,
        COUNT(*) as cnt,
        MAX(sl.created_at) as last_seen
    FROM rag.search_logs sl
    WHERE sl.result_count = 0
      AND sl.created_at >= now() - (p_days || ' days')::INTERVAL
    GROUP BY sl.query
    HAVING COUNT(*) >= p_min_count
    ORDER BY cnt DESC
    LIMIT 50;
END;
$$ LANGUAGE plpgsql STABLE;

-- =============================================================================
-- SEED SAMPLE DATA
-- =============================================================================

DO $$
DECLARE
    sample_tenant UUID := '00000000-0000-0000-0000-000000000001';
BEGIN
    -- Sample glossary terms
    INSERT INTO kb.glossary_terms (tenant_id, term, definition, product_context, synonyms, created_by)
    VALUES
        (sample_tenant, 'ORM', 'Object-Relational Mapping layer providing database abstraction', 'odoo-ce',
         ARRAY['Object-Relational Mapper', 'Model layer'], 'system'),
        (sample_tenant, 'RLS', 'Row-Level Security - database policies restricting row access', 'platform',
         ARRAY['Row-Level Security'], 'system'),
        (sample_tenant, 'RAG', 'Retrieval-Augmented Generation - combining search with LLM generation', 'platform',
         ARRAY['Retrieval-Augmented Generation'], 'system'),
        (sample_tenant, 'Medallion', 'Data architecture pattern with Bronze/Silver/Gold layers', 'platform',
         ARRAY['Medallion Architecture'], 'system')
    ON CONFLICT DO NOTHING;

    -- Sample journey
    INSERT INTO kb.journeys (tenant_id, slug, title, description, product, difficulty, estimated_hours, is_published, is_featured, author)
    VALUES
        (sample_tenant, 'odoo-dev-basics', 'Odoo Developer Basics',
         'Learn the fundamentals of Odoo module development', 'odoo-ce',
         'beginner', 8, true, true, 'system')
    ON CONFLICT DO NOTHING;
END;
$$;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'KB Discovery schema created';
    RAISE NOTICE 'Tables: kb.glossary_terms, kb.journeys, kb.journey_steps, runtime.journey_progress, rag.search_logs';
END;
$$;
