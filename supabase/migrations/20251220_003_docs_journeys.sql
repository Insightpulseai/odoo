-- =============================================================================
-- DOCS PLATFORM: LEARNING JOURNEYS & GLOSSARY
-- =============================================================================
-- Provides curated learning paths and canonical term definitions
-- Supports skill-building with prerequisites and progress tracking
-- =============================================================================

-- =============================================================================
-- LEARNING JOURNEYS
-- =============================================================================

CREATE TABLE docs.learning_journeys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    product TEXT NOT NULL,
    difficulty TEXT NOT NULL DEFAULT 'intermediate',
    estimated_hours FLOAT,
    certification_slug TEXT,
    prerequisites TEXT[],  -- Journey slugs that should be completed first
    tags TEXT[] DEFAULT '{}',
    is_published BOOLEAN NOT NULL DEFAULT false,
    featured BOOLEAN NOT NULL DEFAULT false,
    author TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT valid_difficulty CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    CONSTRAINT slug_format CHECK (slug ~ '^[a-z0-9][a-z0-9-]*[a-z0-9]$')
);

CREATE INDEX idx_journeys_product ON docs.learning_journeys(product);
CREATE INDEX idx_journeys_published ON docs.learning_journeys(is_published) WHERE is_published = true;
CREATE INDEX idx_journeys_featured ON docs.learning_journeys(featured) WHERE featured = true;
CREATE INDEX idx_journeys_tags ON docs.learning_journeys USING GIN (tags);

-- =============================================================================
-- LEARNING JOURNEY STEPS
-- =============================================================================

CREATE TABLE docs.learning_journey_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journey_id UUID NOT NULL REFERENCES docs.learning_journeys(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    doc_id UUID NOT NULL,  -- References document
    title_override TEXT,   -- Optional title different from doc title
    notes TEXT,           -- Additional context for this step
    estimated_minutes INTEGER,
    is_optional BOOLEAN NOT NULL DEFAULT false,
    quiz_id UUID,         -- Optional quiz to complete before proceeding
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (journey_id, step_order),
    CONSTRAINT valid_step_order CHECK (step_order >= 0)
);

-- Note: Using (journey_id, step_order) as composite key
-- Dropping the duplicate id primary key
ALTER TABLE docs.learning_journey_steps DROP CONSTRAINT IF EXISTS learning_journey_steps_pkey;
ALTER TABLE docs.learning_journey_steps DROP COLUMN IF EXISTS id;
ALTER TABLE docs.learning_journey_steps ADD PRIMARY KEY (journey_id, step_order);

CREATE INDEX idx_journey_steps_doc ON docs.learning_journey_steps(doc_id);

-- =============================================================================
-- STEP PREREQUISITES (within a journey)
-- =============================================================================

CREATE TABLE docs.journey_step_prerequisites (
    journey_id UUID NOT NULL,
    step_order INTEGER NOT NULL,
    prereq_step_order INTEGER NOT NULL,

    PRIMARY KEY (journey_id, step_order, prereq_step_order),
    FOREIGN KEY (journey_id, step_order)
        REFERENCES docs.learning_journey_steps(journey_id, step_order) ON DELETE CASCADE,
    FOREIGN KEY (journey_id, prereq_step_order)
        REFERENCES docs.learning_journey_steps(journey_id, step_order) ON DELETE CASCADE,
    CONSTRAINT prereq_before_step CHECK (prereq_step_order < step_order)
);

-- =============================================================================
-- GLOSSARY
-- =============================================================================

CREATE TABLE docs.glossary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    term TEXT NOT NULL,
    product_context TEXT NOT NULL,
    definition TEXT NOT NULL,
    acronym_expansion TEXT,  -- Full form if term is an acronym
    doc_id UUID,             -- Authoritative document
    anchor_id TEXT,          -- Anchor within document
    related_terms TEXT[] DEFAULT '{}',
    see_also UUID[],         -- Related glossary entries
    example_usage TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_term_context UNIQUE (term, product_context)
);

CREATE INDEX idx_glossary_term ON docs.glossary(term);
CREATE INDEX idx_glossary_term_prefix ON docs.glossary(term text_pattern_ops);  -- For prefix search
CREATE INDEX idx_glossary_product ON docs.glossary(product_context);
CREATE INDEX idx_glossary_doc ON docs.glossary(doc_id);
CREATE INDEX idx_glossary_related ON docs.glossary USING GIN (related_terms);

-- =============================================================================
-- RUNTIME: USER JOURNEY PROGRESS
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS runtime;

CREATE TABLE runtime.user_journey_progress (
    user_id TEXT NOT NULL,
    journey_id UUID NOT NULL REFERENCES docs.learning_journeys(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ,
    quiz_score FLOAT,
    notes TEXT,

    PRIMARY KEY (user_id, journey_id, step_order)
);

CREATE INDEX idx_progress_user ON runtime.user_journey_progress(user_id);
CREATE INDEX idx_progress_journey ON runtime.user_journey_progress(journey_id);
CREATE INDEX idx_progress_completed ON runtime.user_journey_progress(completed_at) WHERE completed_at IS NOT NULL;

-- =============================================================================
-- RUNTIME: SEARCH TELEMETRY
-- =============================================================================

CREATE TABLE runtime.search_telemetry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    filters JSONB,
    result_count INTEGER NOT NULL,
    click_position INTEGER,  -- Which result was clicked (1-indexed)
    clicked_doc_id UUID,
    session_id TEXT,
    user_id TEXT,
    latency_ms INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_telemetry_time ON runtime.search_telemetry(created_at DESC);
CREATE INDEX idx_telemetry_session ON runtime.search_telemetry(session_id);
CREATE INDEX idx_telemetry_zero_results ON runtime.search_telemetry(query)
    WHERE result_count = 0;

-- Partition by month for efficient retention
-- Note: Actual partitioning would require table recreation,
-- this is a placeholder for production

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Get journey with computed step count and progress
CREATE OR REPLACE FUNCTION docs.get_journey_summary(p_slug TEXT, p_user_id TEXT DEFAULT NULL)
RETURNS TABLE(
    id UUID,
    slug TEXT,
    title TEXT,
    description TEXT,
    product TEXT,
    difficulty TEXT,
    estimated_hours FLOAT,
    step_count BIGINT,
    completed_steps BIGINT,
    is_complete BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        j.id,
        j.slug,
        j.title,
        j.description,
        j.product,
        j.difficulty,
        j.estimated_hours,
        COUNT(DISTINCT js.step_order) as step_count,
        COUNT(DISTINCT ujp.step_order) FILTER (WHERE ujp.completed_at IS NOT NULL) as completed_steps,
        COUNT(DISTINCT js.step_order) = COUNT(DISTINCT ujp.step_order) FILTER (WHERE ujp.completed_at IS NOT NULL) as is_complete
    FROM docs.learning_journeys j
    LEFT JOIN docs.learning_journey_steps js ON js.journey_id = j.id
    LEFT JOIN runtime.user_journey_progress ujp
        ON ujp.journey_id = j.id
        AND ujp.step_order = js.step_order
        AND ujp.user_id = p_user_id
    WHERE j.slug = p_slug
    GROUP BY j.id, j.slug, j.title, j.description, j.product, j.difficulty, j.estimated_hours;
END;
$$ LANGUAGE plpgsql STABLE;

-- Get journey steps with completion status
CREATE OR REPLACE FUNCTION docs.get_journey_steps(
    p_journey_id UUID,
    p_user_id TEXT DEFAULT NULL
)
RETURNS TABLE(
    step_order INTEGER,
    doc_id UUID,
    title_override TEXT,
    notes TEXT,
    estimated_minutes INTEGER,
    is_optional BOOLEAN,
    is_locked BOOLEAN,
    is_completed BOOLEAN,
    completed_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        js.step_order,
        js.doc_id,
        js.title_override,
        js.notes,
        js.estimated_minutes,
        js.is_optional,
        -- Step is locked if any prerequisite is not completed
        EXISTS (
            SELECT 1 FROM docs.journey_step_prerequisites jsp
            LEFT JOIN runtime.user_journey_progress ujp
                ON ujp.journey_id = p_journey_id
                AND ujp.step_order = jsp.prereq_step_order
                AND ujp.user_id = p_user_id
            WHERE jsp.journey_id = p_journey_id
              AND jsp.step_order = js.step_order
              AND (ujp.completed_at IS NULL OR ujp.user_id IS NULL)
        ) as is_locked,
        ujp.completed_at IS NOT NULL as is_completed,
        ujp.completed_at
    FROM docs.learning_journey_steps js
    LEFT JOIN runtime.user_journey_progress ujp
        ON ujp.journey_id = js.journey_id
        AND ujp.step_order = js.step_order
        AND ujp.user_id = p_user_id
    WHERE js.journey_id = p_journey_id
    ORDER BY js.step_order;
END;
$$ LANGUAGE plpgsql STABLE;

-- Mark journey step complete
CREATE OR REPLACE FUNCTION docs.complete_journey_step(
    p_user_id TEXT,
    p_journey_id UUID,
    p_step_order INTEGER,
    p_quiz_score FLOAT DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    v_locked BOOLEAN;
BEGIN
    -- Check if step is locked
    SELECT EXISTS (
        SELECT 1 FROM docs.journey_step_prerequisites jsp
        LEFT JOIN runtime.user_journey_progress ujp
            ON ujp.journey_id = p_journey_id
            AND ujp.step_order = jsp.prereq_step_order
            AND ujp.user_id = p_user_id
        WHERE jsp.journey_id = p_journey_id
          AND jsp.step_order = p_step_order
          AND ujp.completed_at IS NULL
    ) INTO v_locked;

    IF v_locked THEN
        RAISE EXCEPTION 'Step % is locked - complete prerequisites first', p_step_order;
    END IF;

    -- Upsert progress
    INSERT INTO runtime.user_journey_progress (user_id, journey_id, step_order, completed_at, quiz_score)
    VALUES (p_user_id, p_journey_id, p_step_order, now(), p_quiz_score)
    ON CONFLICT (user_id, journey_id, step_order)
    DO UPDATE SET completed_at = now(), quiz_score = COALESCE(p_quiz_score, runtime.user_journey_progress.quiz_score);

    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- Glossary term lookup with fuzzy matching
CREATE OR REPLACE FUNCTION docs.lookup_glossary(
    p_term TEXT,
    p_product TEXT DEFAULT NULL,
    p_fuzzy BOOLEAN DEFAULT false
)
RETURNS TABLE(
    id UUID,
    term TEXT,
    product_context TEXT,
    definition TEXT,
    acronym_expansion TEXT,
    doc_id UUID,
    anchor_id TEXT,
    similarity FLOAT
) AS $$
BEGIN
    IF p_fuzzy THEN
        -- Fuzzy matching using trigram similarity
        RETURN QUERY
        SELECT
            g.id,
            g.term,
            g.product_context,
            g.definition,
            g.acronym_expansion,
            g.doc_id,
            g.anchor_id,
            similarity(g.term, p_term) as sim
        FROM docs.glossary g
        WHERE (p_product IS NULL OR g.product_context = p_product)
          AND similarity(g.term, p_term) > 0.3
        ORDER BY sim DESC
        LIMIT 10;
    ELSE
        -- Exact prefix match
        RETURN QUERY
        SELECT
            g.id,
            g.term,
            g.product_context,
            g.definition,
            g.acronym_expansion,
            g.doc_id,
            g.anchor_id,
            1.0::FLOAT as sim
        FROM docs.glossary g
        WHERE (p_product IS NULL OR g.product_context = p_product)
          AND g.term ILIKE p_term || '%'
        ORDER BY g.term
        LIMIT 20;
    END IF;
END;
$$ LANGUAGE plpgsql STABLE;

-- =============================================================================
-- SEED SAMPLE JOURNEYS
-- =============================================================================

INSERT INTO docs.learning_journeys (slug, title, description, product, difficulty, estimated_hours, is_published, featured) VALUES
    ('odoo-developer-basics', 'Odoo Developer Basics', 'Learn the fundamentals of Odoo module development', 'odoo-ce', 'beginner', 8, true, true),
    ('odoo-orm-mastery', 'Odoo ORM Mastery', 'Deep dive into Odoo Object Relational Mapping', 'odoo-ce', 'intermediate', 12, true, false),
    ('oca-contribution-guide', 'OCA Contribution Guide', 'How to contribute to OCA repositories', 'oca', 'intermediate', 4, true, true),
    ('platform-integration', 'Platform Integration', 'Integrate with the platform APIs and services', 'platform', 'advanced', 16, true, false);

-- =============================================================================
-- SEED SAMPLE GLOSSARY
-- =============================================================================

INSERT INTO docs.glossary (term, product_context, definition, acronym_expansion, related_terms) VALUES
    ('ORM', 'odoo-ce', 'Object-Relational Mapping layer that provides an abstraction over the database', 'Object-Relational Mapping', ARRAY['Model', 'Field', 'Record']),
    ('RLS', 'platform', 'Row-Level Security - database policy that restricts which rows users can access', 'Row-Level Security', ARRAY['Policy', 'Security', 'Multi-tenant']),
    ('OCA', 'oca', 'Odoo Community Association - non-profit organization maintaining community addons', 'Odoo Community Association', ARRAY['Addon', 'Module', 'Contribution']),
    ('RAG', 'platform', 'Retrieval-Augmented Generation - technique combining search with LLM generation', 'Retrieval-Augmented Generation', ARRAY['Embedding', 'Vector', 'Search']),
    ('Medallion', 'platform', 'Data architecture pattern with Bronze (raw), Silver (cleaned), and Gold (aggregated) layers', NULL, ARRAY['Bronze', 'Silver', 'Gold', 'ETL']),
    ('ACID', 'platform', 'Properties of database transactions: Atomicity, Consistency, Isolation, Durability', 'Atomicity, Consistency, Isolation, Durability', ARRAY['Transaction', 'Database', 'Consistency']);

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Docs journeys and glossary schema created';
    RAISE NOTICE 'Sample journeys: %', (SELECT COUNT(*) FROM docs.learning_journeys);
    RAISE NOTICE 'Sample glossary terms: %', (SELECT COUNT(*) FROM docs.glossary);
END;
$$;
