-- =====================================================
-- Skill Creator Certification System
-- =====================================================
-- Purpose: Agent skill registry + certification system with certification-level
-- evidence, RAG-ready knowledge base, and telemetry for skill evaluations
-- =====================================================

-- =====================================================
-- SCHEMA: skills
-- Purpose: Skill definitions, criteria, holders, evaluations
-- =====================================================
CREATE SCHEMA IF NOT EXISTS skills;

-- 1) Skill definitions (like certifications)
CREATE TABLE IF NOT EXISTS skills.skill_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE,              -- e.g. 'nextjs-frontend-pro', 'odoo-oca-admin', 'supabase-dba'
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,                 -- 'frontend', 'backend', 'ai-orchestration', 'design-system'
    level TEXT NOT NULL,                    -- 'foundation', 'associate', 'professional', 'expert'
    spec_url TEXT,                          -- link to PRD/spec/docs used as reference
    design_system_token TEXT,               -- e.g. 'ipai/copilot-theme/v1'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_level CHECK (level IN ('foundation', 'associate', 'professional', 'expert'))
);

COMMENT ON TABLE skills.skill_definitions IS 'Skill catalog - defines certifiable skills with criteria';
COMMENT ON COLUMN skills.skill_definitions.slug IS 'Unique identifier for skill (e.g. nextjs-copilot-ui-pro)';
COMMENT ON COLUMN skills.skill_definitions.category IS 'Skill domain (frontend, backend, ai-orchestration, design-system)';
COMMENT ON COLUMN skills.skill_definitions.level IS 'Certification level (foundation, associate, professional, expert)';
COMMENT ON COLUMN skills.skill_definitions.design_system_token IS 'Design system token reference for UI skills';

-- Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION skills.touch_skill_definitions_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_skills_touch_definitions ON skills.skill_definitions;

CREATE TRIGGER trg_skills_touch_definitions
BEFORE UPDATE ON skills.skill_definitions
FOR EACH ROW
EXECUTE FUNCTION skills.touch_skill_definitions_updated_at();

-- 2) Skill criteria (what must be true to be "certified")
CREATE TABLE IF NOT EXISTS skills.skill_criteria (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES skills.skill_definitions(id) ON DELETE CASCADE,
    code TEXT NOT NULL,                     -- e.g. 'UI_PARITY', 'RLS_ENFORCED', 'TEST_COVERAGE'
    description TEXT NOT NULL,
    weight NUMERIC(5,2) NOT NULL DEFAULT 1.0,   -- importance
    required BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_skill_criterion UNIQUE (skill_id, code)
);

COMMENT ON TABLE skills.skill_criteria IS 'Certification criteria - scoring rubric for skills';
COMMENT ON COLUMN skills.skill_criteria.code IS 'Criterion identifier (e.g. UI_PARITY, RLS_ENFORCED)';
COMMENT ON COLUMN skills.skill_criteria.weight IS 'Relative importance for scoring (0.5-5.0)';
COMMENT ON COLUMN skills.skill_criteria.required IS 'Whether criterion must pass for certification';

CREATE INDEX IF NOT EXISTS idx_skill_criteria_skill_id
    ON skills.skill_criteria(skill_id);

-- 3) Skill holders (agents, humans, hybrid)
CREATE TABLE IF NOT EXISTS skills.skill_holders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    holder_type TEXT NOT NULL,              -- 'agent', 'human', 'hybrid'
    holder_slug TEXT NOT NULL,              -- e.g. 'Pulser.Devstral', 'Jake.Tolentino'
    display_name TEXT NOT NULL,
    meta JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT unique_holder UNIQUE (holder_type, holder_slug),
    CONSTRAINT valid_holder_type CHECK (holder_type IN ('agent', 'human', 'hybrid'))
);

COMMENT ON TABLE skills.skill_holders IS 'Entities that can hold/earn skills (agents, humans, teams)';
COMMENT ON COLUMN skills.skill_holders.holder_type IS 'Type of holder (agent, human, hybrid team)';
COMMENT ON COLUMN skills.skill_holders.holder_slug IS 'Unique identifier within type (e.g. Pulser.Devstral)';
COMMENT ON COLUMN skills.skill_holders.meta IS 'Additional holder metadata (stack, capabilities, etc.)';

CREATE INDEX IF NOT EXISTS idx_skill_holders_type_slug
    ON skills.skill_holders(holder_type, holder_slug);

-- 4) Skill evaluations (attempts, like exam runs)
CREATE TABLE IF NOT EXISTS skills.skill_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES skills.skill_definitions(id) ON DELETE CASCADE,
    holder_id UUID NOT NULL REFERENCES skills.skill_holders(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'running', 'passed', 'failed'
    score NUMERIC(5,2),
    evidence_repo_url TEXT,                 -- github repo / environment
    run_id TEXT,                            -- link to CI run / BuildOps run ID
    telemetry_run_id UUID,                  -- link to telemetry.runs
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_eval_status CHECK (status IN ('pending', 'running', 'passed', 'failed'))
);

COMMENT ON TABLE skills.skill_evaluations IS 'Skill certification attempts - exam runs with evidence';
COMMENT ON COLUMN skills.skill_evaluations.status IS 'Evaluation state (pending, running, passed, failed)';
COMMENT ON COLUMN skills.skill_evaluations.score IS 'Total weighted score from criteria';
COMMENT ON COLUMN skills.skill_evaluations.evidence_repo_url IS 'Link to evidence repository';
COMMENT ON COLUMN skills.skill_evaluations.run_id IS 'CI/BuildOps run identifier';

CREATE INDEX IF NOT EXISTS idx_skill_eval_skill_holder
    ON skills.skill_evaluations(skill_id, holder_id);

CREATE INDEX IF NOT EXISTS idx_skill_eval_status
    ON skills.skill_evaluations(status);

CREATE INDEX IF NOT EXISTS idx_skill_eval_created
    ON skills.skill_evaluations(created_at DESC);

-- Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION skills.touch_skill_evaluations_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_skills_touch_evaluations ON skills.skill_evaluations;

CREATE TRIGGER trg_skills_touch_evaluations
BEFORE UPDATE ON skills.skill_evaluations
FOR EACH ROW
EXECUTE FUNCTION skills.touch_skill_evaluations_updated_at();

-- 5) Per-criterion results (like exam questions)
CREATE TABLE IF NOT EXISTS skills.skill_eval_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    eval_id UUID NOT NULL REFERENCES skills.skill_evaluations(id) ON DELETE CASCADE,
    criterion_id UUID NOT NULL REFERENCES skills.skill_criteria(id) ON DELETE CASCADE,
    status TEXT NOT NULL,                   -- 'passed', 'failed', 'skipped'
    score NUMERIC(5,2),
    details JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_result_status CHECK (status IN ('passed', 'failed', 'skipped'))
);

COMMENT ON TABLE skills.skill_eval_results IS 'Per-criterion results - exam question scores';
COMMENT ON COLUMN skills.skill_eval_results.status IS 'Criterion result (passed, failed, skipped)';
COMMENT ON COLUMN skills.skill_eval_results.score IS 'Weighted score for this criterion';
COMMENT ON COLUMN skills.skill_eval_results.details IS 'Evidence, logs, metrics for this criterion';

CREATE INDEX IF NOT EXISTS idx_skill_eval_results_eval_id
    ON skills.skill_eval_results(eval_id);

-- =====================================================
-- SCHEMA: knowledge
-- Purpose: RAG knowledge base (Kapa-style doc brain)
-- =====================================================
CREATE SCHEMA IF NOT EXISTS knowledge;

-- 1) Knowledge sources (docs, APIs, specs, official docs)
CREATE TABLE IF NOT EXISTS knowledge.sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE,              -- 'supabase-docs', 'odoo-oca-18', 'mailgun-docs'
    kind TEXT NOT NULL,                     -- 'docs', 'api', 'spec', 'repo'
    base_url TEXT,
    meta JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_source_kind CHECK (kind IN ('docs', 'api', 'spec', 'repo', 'prd', 'internal'))
);

COMMENT ON TABLE knowledge.sources IS 'Knowledge sources - docs, APIs, specs for RAG';
COMMENT ON COLUMN knowledge.sources.slug IS 'Unique identifier (e.g. supabase-docs, odoo-oca-18)';
COMMENT ON COLUMN knowledge.sources.kind IS 'Source type (docs, api, spec, repo, prd, internal)';
COMMENT ON COLUMN knowledge.sources.base_url IS 'Base URL for source (e.g. https://supabase.com/docs)';

-- Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION knowledge.touch_sources_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_knowledge_touch_sources ON knowledge.sources;

CREATE TRIGGER trg_knowledge_touch_sources
BEFORE UPDATE ON knowledge.sources
FOR EACH ROW
EXECUTE FUNCTION knowledge.touch_sources_updated_at();

-- 2) Chunks (vector-ready, Kapa-style RAG)
-- Note: embedding column requires pgvector extension
CREATE TABLE IF NOT EXISTS knowledge.chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES knowledge.sources(id) ON DELETE CASCADE,
    external_id TEXT,                       -- e.g. doc path, heading ID, file hash
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
    embedding VECTOR(1536),                 -- OpenAI text-embedding-3-large dimension
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE knowledge.chunks IS 'Document chunks for RAG retrieval';
COMMENT ON COLUMN knowledge.chunks.external_id IS 'External reference (doc path, heading ID)';
COMMENT ON COLUMN knowledge.chunks.content IS 'Chunk text content';
COMMENT ON COLUMN knowledge.chunks.embedding IS 'Vector embedding for semantic search';

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_source
    ON knowledge.chunks(source_id);

-- Create HNSW index for fast similarity search (if pgvector is available)
-- This will be created separately if pgvector extension is enabled
-- CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_embedding
--     ON knowledge.chunks USING hnsw (embedding vector_cosine_ops);

-- 3) Question/answer logs (for analytics & gap analysis)
CREATE TABLE IF NOT EXISTS knowledge.qa_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES knowledge.sources(id) ON DELETE SET NULL,
    user_kind TEXT NOT NULL,                -- 'agent', 'human'
    user_id TEXT NOT NULL,                  -- e.g. 'Pulser.Devstral', 'Jake'
    question TEXT NOT NULL,
    answer TEXT,
    answer_quality TEXT,                    -- 'ok', 'hallucinated', 'did_not_know'
    related_chunk_ids UUID[] DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_user_kind CHECK (user_kind IN ('agent', 'human')),
    CONSTRAINT valid_answer_quality CHECK (answer_quality IS NULL OR answer_quality IN ('ok', 'hallucinated', 'did_not_know', 'partial'))
);

COMMENT ON TABLE knowledge.qa_events IS 'Q&A log for analytics and gap analysis';
COMMENT ON COLUMN knowledge.qa_events.user_kind IS 'Questioner type (agent, human)';
COMMENT ON COLUMN knowledge.qa_events.answer_quality IS 'Answer quality assessment';
COMMENT ON COLUMN knowledge.qa_events.related_chunk_ids IS 'Chunks used to generate answer';

CREATE INDEX IF NOT EXISTS idx_knowledge_qa_source
    ON knowledge.qa_events(source_id);

CREATE INDEX IF NOT EXISTS idx_knowledge_qa_user
    ON knowledge.qa_events(user_kind, user_id);

CREATE INDEX IF NOT EXISTS idx_knowledge_qa_created
    ON knowledge.qa_events(created_at DESC);

-- =====================================================
-- SCHEMA: telemetry
-- Purpose: Run telemetry for BuildOps/CI integration
-- =====================================================
CREATE SCHEMA IF NOT EXISTS telemetry;

-- Telemetry runs (link to BuildOps Control Room)
CREATE TABLE IF NOT EXISTS telemetry.runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id TEXT NOT NULL UNIQUE,            -- your BuildOps / CI run ID
    agent_slug TEXT NOT NULL,               -- 'Pulser.Devstral', 'Pulser.Dash'
    context TEXT NOT NULL,                  -- 'deploy-frontend', 'seed-odoo', 'mailgun-verify'
    status TEXT NOT NULL,                   -- 'queued', 'running', 'passed', 'failed'
    score NUMERIC(5,2),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,

    CONSTRAINT valid_run_status CHECK (status IN ('queued', 'running', 'passed', 'failed', 'cancelled'))
);

COMMENT ON TABLE telemetry.runs IS 'BuildOps/CI run telemetry for skill evaluations';
COMMENT ON COLUMN telemetry.runs.run_id IS 'External run identifier (CI/BuildOps)';
COMMENT ON COLUMN telemetry.runs.agent_slug IS 'Agent that performed the run';
COMMENT ON COLUMN telemetry.runs.context IS 'Run context (deploy-frontend, seed-odoo, etc.)';
COMMENT ON COLUMN telemetry.runs.status IS 'Run state (queued, running, passed, failed)';

CREATE INDEX IF NOT EXISTS idx_telemetry_runs_agent
    ON telemetry.runs(agent_slug, status);

CREATE INDEX IF NOT EXISTS idx_telemetry_runs_run_id
    ON telemetry.runs(run_id);

CREATE INDEX IF NOT EXISTS idx_telemetry_runs_started
    ON telemetry.runs(started_at DESC);

-- Add foreign key from skill_evaluations to telemetry.runs
-- (Done after telemetry.runs is created)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_skill_eval_telemetry_run'
    ) THEN
        ALTER TABLE skills.skill_evaluations
        ADD CONSTRAINT fk_skill_eval_telemetry_run
        FOREIGN KEY (telemetry_run_id) REFERENCES telemetry.runs(id) ON DELETE SET NULL;
    END IF;
END $$;

-- =====================================================
-- RPC Functions for Skill Evaluation
-- =====================================================

-- Function: Record a skill evaluation
CREATE OR REPLACE FUNCTION skills.record_evaluation(
    p_skill_slug TEXT,
    p_holder_type TEXT,
    p_holder_slug TEXT,
    p_display_name TEXT,
    p_run_id TEXT,
    p_evidence_repo_url TEXT DEFAULT NULL,
    p_criteria_results JSONB DEFAULT '[]'::JSONB
)
RETURNS UUID AS $$
DECLARE
    v_skill_id UUID;
    v_holder_id UUID;
    v_eval_id UUID;
    v_total_score NUMERIC(5,2) := 0;
    v_all_passed BOOLEAN := TRUE;
    v_result RECORD;
    v_criterion_id UUID;
BEGIN
    -- Get skill
    SELECT id INTO v_skill_id
    FROM skills.skill_definitions
    WHERE slug = p_skill_slug;

    IF v_skill_id IS NULL THEN
        RAISE EXCEPTION 'Skill not found: %', p_skill_slug;
    END IF;

    -- Upsert holder
    INSERT INTO skills.skill_holders (holder_type, holder_slug, display_name)
    VALUES (p_holder_type, p_holder_slug, p_display_name)
    ON CONFLICT (holder_type, holder_slug) DO UPDATE
        SET display_name = EXCLUDED.display_name
    RETURNING id INTO v_holder_id;

    -- Calculate total score and check if all required passed
    FOR v_result IN SELECT * FROM jsonb_to_recordset(p_criteria_results) AS x(code TEXT, status TEXT, score NUMERIC)
    LOOP
        v_total_score := v_total_score + COALESCE(v_result.score, 0);

        -- Check if required criterion failed
        IF v_result.status = 'failed' THEN
            SELECT id INTO v_criterion_id
            FROM skills.skill_criteria
            WHERE skill_id = v_skill_id AND code = v_result.code AND required = TRUE;

            IF v_criterion_id IS NOT NULL THEN
                v_all_passed := FALSE;
            END IF;
        END IF;
    END LOOP;

    -- Create evaluation
    INSERT INTO skills.skill_evaluations (
        skill_id,
        holder_id,
        status,
        score,
        evidence_repo_url,
        run_id
    ) VALUES (
        v_skill_id,
        v_holder_id,
        CASE WHEN v_all_passed THEN 'passed' ELSE 'failed' END,
        v_total_score,
        p_evidence_repo_url,
        p_run_id
    )
    RETURNING id INTO v_eval_id;

    -- Insert per-criterion results
    FOR v_result IN SELECT * FROM jsonb_to_recordset(p_criteria_results) AS x(code TEXT, status TEXT, score NUMERIC, details JSONB)
    LOOP
        SELECT id INTO v_criterion_id
        FROM skills.skill_criteria
        WHERE skill_id = v_skill_id AND code = v_result.code;

        IF v_criterion_id IS NOT NULL THEN
            INSERT INTO skills.skill_eval_results (
                eval_id,
                criterion_id,
                status,
                score,
                details
            ) VALUES (
                v_eval_id,
                v_criterion_id,
                v_result.status,
                v_result.score,
                COALESCE(v_result.details, '{}'::JSONB)
            );
        END IF;
    END LOOP;

    RETURN v_eval_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION skills.record_evaluation IS 'Record a skill evaluation with criteria results';

-- Function: Get holder skills summary
CREATE OR REPLACE FUNCTION skills.get_holder_skills(
    p_holder_slug TEXT
)
RETURNS TABLE (
    skill_slug TEXT,
    skill_title TEXT,
    skill_level TEXT,
    latest_status TEXT,
    latest_score NUMERIC,
    evaluation_count BIGINT,
    last_evaluated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sd.slug,
        sd.title,
        sd.level,
        e.status,
        e.score,
        COUNT(*) OVER (PARTITION BY sd.id),
        e.created_at
    FROM skills.skill_definitions sd
    JOIN skills.skill_evaluations e ON e.skill_id = sd.id
    JOIN skills.skill_holders h ON h.id = e.holder_id
    WHERE h.holder_slug = p_holder_slug
    AND e.created_at = (
        SELECT MAX(e2.created_at)
        FROM skills.skill_evaluations e2
        WHERE e2.skill_id = sd.id AND e2.holder_id = h.id
    )
    ORDER BY e.created_at DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION skills.get_holder_skills IS 'Get all skills for a holder with latest evaluation status';

-- =====================================================
-- RLS Policies
-- =====================================================

-- Skills schema
ALTER TABLE skills.skill_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills.skill_criteria ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills.skill_holders ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills.skill_evaluations ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills.skill_eval_results ENABLE ROW LEVEL SECURITY;

-- Service role has full access
CREATE POLICY "Service role full access on skill_definitions"
    ON skills.skill_definitions FOR ALL TO service_role USING (true);
CREATE POLICY "Service role full access on skill_criteria"
    ON skills.skill_criteria FOR ALL TO service_role USING (true);
CREATE POLICY "Service role full access on skill_holders"
    ON skills.skill_holders FOR ALL TO service_role USING (true);
CREATE POLICY "Service role full access on skill_evaluations"
    ON skills.skill_evaluations FOR ALL TO service_role USING (true);
CREATE POLICY "Service role full access on skill_eval_results"
    ON skills.skill_eval_results FOR ALL TO service_role USING (true);

-- Authenticated users can read
CREATE POLICY "Authenticated users can read skill_definitions"
    ON skills.skill_definitions FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read skill_criteria"
    ON skills.skill_criteria FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read skill_holders"
    ON skills.skill_holders FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read skill_evaluations"
    ON skills.skill_evaluations FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read skill_eval_results"
    ON skills.skill_eval_results FOR SELECT TO authenticated USING (true);

-- Knowledge schema
ALTER TABLE knowledge.sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge.chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge.qa_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access on knowledge.sources"
    ON knowledge.sources FOR ALL TO service_role USING (true);
CREATE POLICY "Service role full access on knowledge.chunks"
    ON knowledge.chunks FOR ALL TO service_role USING (true);
CREATE POLICY "Service role full access on knowledge.qa_events"
    ON knowledge.qa_events FOR ALL TO service_role USING (true);

CREATE POLICY "Authenticated users can read knowledge.sources"
    ON knowledge.sources FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read knowledge.chunks"
    ON knowledge.chunks FOR SELECT TO authenticated USING (true);
CREATE POLICY "Authenticated users can read knowledge.qa_events"
    ON knowledge.qa_events FOR SELECT TO authenticated USING (true);

-- Telemetry schema
ALTER TABLE telemetry.runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access on telemetry.runs"
    ON telemetry.runs FOR ALL TO service_role USING (true);
CREATE POLICY "Authenticated users can read telemetry.runs"
    ON telemetry.runs FOR SELECT TO authenticated USING (true);

-- =====================================================
-- Verification Query
-- =====================================================
SELECT
    table_schema,
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns c WHERE c.table_schema = t.table_schema AND c.table_name = t.table_name) AS column_count
FROM information_schema.tables t
WHERE table_schema IN ('skills', 'knowledge', 'telemetry')
ORDER BY table_schema, table_name;
