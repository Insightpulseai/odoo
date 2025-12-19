-- ============================================================================
-- Ops Advisor Schema for Supabase
-- Azure Advisor-style recommendations and scoring system
-- ============================================================================

-- Create schema
CREATE SCHEMA IF NOT EXISTS ops_advisor;

-- ============================================================================
-- Core Tables
-- ============================================================================

-- Recommendations table
CREATE TABLE IF NOT EXISTS ops_advisor.recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Classification
    source TEXT NOT NULL,                           -- k8s, odoo, supabase, github, ingress, manual, api
    category TEXT NOT NULL,                         -- cost, security, reliability, ops, performance
    severity TEXT NOT NULL DEFAULT 'medium',        -- info, low, medium, high, critical

    -- Content
    title TEXT NOT NULL,
    description TEXT,

    -- Resource identification
    resource_type TEXT,                             -- e.g., k8s.pod, odoo.model, supabase.table
    resource_id TEXT,

    -- Evidence and impact
    evidence JSONB DEFAULT '{}'::jsonb,
    impact_score INT DEFAULT 50,                    -- 0-100
    estimated_savings NUMERIC(12,2),                -- For cost category
    confidence NUMERIC(5,2) DEFAULT 80.0,           -- Confidence percentage

    -- Remediation
    remediation JSONB DEFAULT '{}'::jsonb,          -- {steps:[], links:[], commands:[]}
    playbook_id TEXT,                               -- Link to playbook
    external_link TEXT,

    -- Ownership and status
    owner_id TEXT,                                  -- User identifier
    status TEXT NOT NULL DEFAULT 'open',            -- open, acknowledged, in_progress, resolved, snoozed, dismissed
    due_date DATE,
    resolved_at TIMESTAMPTZ,
    snooze_until DATE,

    -- Idempotency key for upsert
    rec_key TEXT UNIQUE,                            -- source + category + resource_id + title_hash

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for recommendations
CREATE INDEX IF NOT EXISTS idx_rec_category_severity_ts
    ON ops_advisor.recommendations (category, severity, ts DESC);
CREATE INDEX IF NOT EXISTS idx_rec_status_ts
    ON ops_advisor.recommendations (status, ts DESC);
CREATE INDEX IF NOT EXISTS idx_rec_resource
    ON ops_advisor.recommendations (resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_rec_owner
    ON ops_advisor.recommendations (owner_id) WHERE owner_id IS NOT NULL;

-- Scores table (time-series snapshots)
CREATE TABLE IF NOT EXISTS ops_advisor.scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    category TEXT NOT NULL,
    score INT NOT NULL,                             -- 0-100
    open_count INT NOT NULL DEFAULT 0,
    high_count INT NOT NULL DEFAULT 0,
    critical_count INT NOT NULL DEFAULT 0,
    resolved_count INT DEFAULT 0,                   -- Resolved in period
    inputs_json JSONB DEFAULT '{}'::jsonb           -- Raw computation inputs
);

CREATE INDEX IF NOT EXISTS idx_scores_category_ts
    ON ops_advisor.scores (category, ts DESC);

-- Activity log
CREATE TABLE IF NOT EXISTS ops_advisor.activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor_id TEXT,                                  -- User or system identifier
    action TEXT NOT NULL,                           -- create, update, resolve, assign, etc.
    entity_type TEXT NOT NULL,                      -- recommendation, score, etc.
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_activity_ts
    ON ops_advisor.activity_log (ts DESC);
CREATE INDEX IF NOT EXISTS idx_activity_entity
    ON ops_advisor.activity_log (entity_type, entity_id);

-- ============================================================================
-- Views
-- ============================================================================

-- Open recommendations by category
CREATE OR REPLACE VIEW ops_advisor.v_open_by_category AS
SELECT
    category,
    COUNT(*) FILTER (WHERE status = 'open') AS open_count,
    COUNT(*) FILTER (WHERE status = 'open' AND severity = 'high') AS high_count,
    COUNT(*) FILTER (WHERE status = 'open' AND severity = 'critical') AS critical_count,
    COUNT(*) FILTER (WHERE status = 'resolved' AND resolved_at >= now() - interval '7 days') AS resolved_7d
FROM ops_advisor.recommendations
GROUP BY category;

-- Latest scores per category
CREATE OR REPLACE VIEW ops_advisor.v_latest_scores AS
WITH latest AS (
    SELECT category, MAX(ts) AS ts
    FROM ops_advisor.scores
    GROUP BY category
)
SELECT s.*
FROM ops_advisor.scores s
JOIN latest l USING (category, ts);

-- Recommendations summary for dashboard
CREATE OR REPLACE VIEW ops_advisor.v_dashboard_summary AS
SELECT
    category,
    COALESCE(ls.score, 0) AS score,
    COALESCE(ob.open_count, 0) AS open_count,
    COALESCE(ob.high_count, 0) AS high_count,
    COALESCE(ob.critical_count, 0) AS critical_count,
    COALESCE(ob.resolved_7d, 0) AS resolved_7d
FROM (SELECT UNNEST(ARRAY['cost', 'security', 'reliability', 'ops', 'performance']) AS category) cats
LEFT JOIN ops_advisor.v_latest_scores ls USING (category)
LEFT JOIN ops_advisor.v_open_by_category ob USING (category);

-- ============================================================================
-- Functions
-- ============================================================================

-- Generate deterministic recommendation key
CREATE OR REPLACE FUNCTION ops_advisor.generate_rec_key(
    p_source TEXT,
    p_category TEXT,
    p_resource_id TEXT,
    p_title TEXT
) RETURNS TEXT AS $$
BEGIN
    RETURN encode(
        sha256(
            (COALESCE(p_source, '') || '|' ||
             COALESCE(p_category, '') || '|' ||
             COALESCE(p_resource_id, '') || '|' ||
             COALESCE(p_title, ''))::bytea
        ),
        'hex'
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Compute score for a category
CREATE OR REPLACE FUNCTION ops_advisor.compute_category_score(p_category TEXT)
RETURNS INT AS $$
DECLARE
    v_critical INT;
    v_high INT;
    v_open INT;
    v_score INT;
BEGIN
    SELECT
        COUNT(*) FILTER (WHERE severity = 'critical'),
        COUNT(*) FILTER (WHERE severity = 'high'),
        COUNT(*)
    INTO v_critical, v_high, v_open
    FROM ops_advisor.recommendations
    WHERE category = p_category AND status = 'open';

    -- Score formula: 100 - (critical * 25) - (high * 10) - (open * 2)
    v_score := 100 - (v_critical * 25) - (v_high * 10) - (v_open * 2);

    RETURN GREATEST(0, LEAST(100, v_score));
END;
$$ LANGUAGE plpgsql;

-- Recompute all scores and insert snapshots
CREATE OR REPLACE FUNCTION ops_advisor.recompute_all_scores()
RETURNS TABLE(category TEXT, score INT, open_count INT, high_count INT, critical_count INT) AS $$
DECLARE
    cat TEXT;
    v_score INT;
    v_open INT;
    v_high INT;
    v_critical INT;
BEGIN
    FOREACH cat IN ARRAY ARRAY['cost', 'security', 'reliability', 'ops', 'performance']
    LOOP
        SELECT
            COUNT(*) FILTER (WHERE status = 'open'),
            COUNT(*) FILTER (WHERE status = 'open' AND severity = 'high'),
            COUNT(*) FILTER (WHERE status = 'open' AND severity = 'critical')
        INTO v_open, v_high, v_critical
        FROM ops_advisor.recommendations
        WHERE ops_advisor.recommendations.category = cat;

        v_score := GREATEST(0, LEAST(100, 100 - (v_critical * 25) - (v_high * 10) - (v_open * 2)));

        INSERT INTO ops_advisor.scores (category, score, open_count, high_count, critical_count)
        VALUES (cat, v_score, v_open, v_high, v_critical);

        category := cat;
        score := v_score;
        open_count := v_open;
        high_count := v_high;
        critical_count := v_critical;
        RETURN NEXT;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Upsert recommendation with idempotency
CREATE OR REPLACE FUNCTION ops_advisor.upsert_recommendation(
    p_source TEXT,
    p_category TEXT,
    p_severity TEXT,
    p_title TEXT,
    p_description TEXT DEFAULT NULL,
    p_resource_type TEXT DEFAULT NULL,
    p_resource_id TEXT DEFAULT NULL,
    p_evidence JSONB DEFAULT '{}'::jsonb,
    p_impact_score INT DEFAULT 50,
    p_estimated_savings NUMERIC DEFAULT NULL,
    p_remediation JSONB DEFAULT '{}'::jsonb
) RETURNS UUID AS $$
DECLARE
    v_rec_key TEXT;
    v_id UUID;
BEGIN
    v_rec_key := ops_advisor.generate_rec_key(p_source, p_category, p_resource_id, p_title);

    INSERT INTO ops_advisor.recommendations (
        source, category, severity, title, description,
        resource_type, resource_id, evidence, impact_score,
        estimated_savings, remediation, rec_key
    ) VALUES (
        p_source, p_category, p_severity, p_title, p_description,
        p_resource_type, p_resource_id, p_evidence, p_impact_score,
        p_estimated_savings, p_remediation, v_rec_key
    )
    ON CONFLICT (rec_key) DO UPDATE SET
        severity = EXCLUDED.severity,
        description = EXCLUDED.description,
        evidence = EXCLUDED.evidence,
        impact_score = EXCLUDED.impact_score,
        estimated_savings = EXCLUDED.estimated_savings,
        remediation = EXCLUDED.remediation,
        updated_at = now()
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- RLS Policies
-- ============================================================================

ALTER TABLE ops_advisor.recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops_advisor.scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops_advisor.activity_log ENABLE ROW LEVEL SECURITY;

-- Admin role can do everything
CREATE POLICY admin_all ON ops_advisor.recommendations
    FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin')
    WITH CHECK (auth.jwt() ->> 'role' = 'admin');

-- Authenticated users can read all recommendations
CREATE POLICY read_all_recs ON ops_advisor.recommendations
    FOR SELECT TO authenticated
    USING (true);

-- Owners can update their own recommendations
CREATE POLICY owner_update ON ops_advisor.recommendations
    FOR UPDATE TO authenticated
    USING (owner_id = auth.uid()::text OR auth.jwt() ->> 'role' = 'admin');

-- Scores are read-only for regular users
CREATE POLICY read_scores ON ops_advisor.scores
    FOR SELECT TO authenticated
    USING (true);

CREATE POLICY admin_scores ON ops_advisor.scores
    FOR ALL TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin')
    WITH CHECK (auth.jwt() ->> 'role' = 'admin');

-- Activity log read-only
CREATE POLICY read_activity ON ops_advisor.activity_log
    FOR SELECT TO authenticated
    USING (true);

-- ============================================================================
-- Triggers
-- ============================================================================

-- Update updated_at on recommendations
CREATE OR REPLACE FUNCTION ops_advisor.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_rec_updated_at
    BEFORE UPDATE ON ops_advisor.recommendations
    FOR EACH ROW
    EXECUTE FUNCTION ops_advisor.update_updated_at();

-- Log recommendation status changes
CREATE OR REPLACE FUNCTION ops_advisor.log_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO ops_advisor.activity_log (
            actor_id, action, entity_type, entity_id,
            old_values, new_values
        ) VALUES (
            COALESCE(auth.uid()::text, 'system'),
            'status_change',
            'recommendation',
            NEW.id,
            jsonb_build_object('status', OLD.status),
            jsonb_build_object('status', NEW.status)
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_rec_status_log
    AFTER UPDATE ON ops_advisor.recommendations
    FOR EACH ROW
    EXECUTE FUNCTION ops_advisor.log_status_change();

-- ============================================================================
-- Seed default scores (empty)
-- ============================================================================

INSERT INTO ops_advisor.scores (category, score, open_count, high_count, critical_count)
SELECT cat, 100, 0, 0, 0
FROM UNNEST(ARRAY['cost', 'security', 'reliability', 'ops', 'performance']) AS cat
ON CONFLICT DO NOTHING;

COMMENT ON SCHEMA ops_advisor IS 'Ops Advisor - Azure Advisor-style recommendations and scoring';
