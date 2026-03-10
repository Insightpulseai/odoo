-- Superset Dashboard: Odoo 19 EE Parity Tracking
-- Create these datasets in Superset for visual parity monitoring

-- ==================================================
-- TABLE: Store parity test results over time
-- ==================================================

CREATE TABLE IF NOT EXISTS public.ee_parity_results (
    id SERIAL PRIMARY KEY,
    test_run_id UUID DEFAULT gen_random_uuid(),
    test_id VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    feature VARCHAR(200) NOT NULL,
    ee_description TEXT,
    status VARCHAR(20) NOT NULL CHECK (status IN ('full', 'partial', 'alt', 'missing', 'skip')),
    score DECIMAL(3,2) NOT NULL DEFAULT 0,
    notes TEXT,
    error TEXT,
    execution_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_parity_category ON public.ee_parity_results(category);
CREATE INDEX IF NOT EXISTS idx_parity_status ON public.ee_parity_results(status);
CREATE INDEX IF NOT EXISTS idx_parity_created ON public.ee_parity_results(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_parity_run ON public.ee_parity_results(test_run_id);

-- ==================================================
-- VIEW: Latest test run results
-- ==================================================

CREATE OR REPLACE VIEW public.v_latest_parity_results AS
WITH latest_run AS (
    SELECT test_run_id
    FROM public.ee_parity_results
    ORDER BY created_at DESC
    LIMIT 1
)
SELECT
    r.test_id,
    r.category,
    r.feature,
    r.status,
    r.score,
    r.notes,
    r.created_at
FROM public.ee_parity_results r
JOIN latest_run lr ON r.test_run_id = lr.test_run_id
ORDER BY r.category, r.test_id;

-- ==================================================
-- VIEW: Parity scorecard by category
-- ==================================================

CREATE OR REPLACE VIEW public.v_parity_scorecard AS
WITH latest_run AS (
    SELECT test_run_id
    FROM public.ee_parity_results
    ORDER BY created_at DESC
    LIMIT 1
),
category_stats AS (
    SELECT
        r.category,
        COUNT(*) as total_tests,
        COUNT(*) FILTER (WHERE r.status = 'full') as full_parity,
        COUNT(*) FILTER (WHERE r.status = 'partial') as partial_parity,
        COUNT(*) FILTER (WHERE r.status = 'alt') as alternative,
        COUNT(*) FILTER (WHERE r.status = 'missing') as missing,
        COUNT(*) FILTER (WHERE r.status = 'skip') as skipped,
        AVG(r.score) as avg_score
    FROM public.ee_parity_results r
    JOIN latest_run lr ON r.test_run_id = lr.test_run_id
    GROUP BY r.category
)
SELECT
    category,
    total_tests,
    full_parity,
    partial_parity,
    alternative,
    missing,
    skipped,
    ROUND(avg_score * 100, 1) as parity_percentage,
    CASE
        WHEN avg_score >= 0.9 THEN 'Full Parity'
        WHEN avg_score >= 0.75 THEN 'Production Ready'
        WHEN avg_score >= 0.5 THEN 'MVP Ready'
        ELSE 'Not Ready'
    END as status_label
FROM category_stats
ORDER BY parity_percentage DESC;

-- ==================================================
-- VIEW: Overall parity score
-- ==================================================

CREATE OR REPLACE VIEW public.v_overall_parity AS
WITH latest_run AS (
    SELECT test_run_id
    FROM public.ee_parity_results
    ORDER BY created_at DESC
    LIMIT 1
)
SELECT
    COUNT(*) as total_tests,
    COUNT(*) FILTER (WHERE status = 'full') as full_parity,
    COUNT(*) FILTER (WHERE status = 'partial') as partial,
    COUNT(*) FILTER (WHERE status = 'missing') as missing,
    COUNT(*) FILTER (WHERE status = 'skip') as skipped,
    ROUND(AVG(score) FILTER (WHERE status != 'skip') * 100, 1) as overall_parity_score,
    CASE
        WHEN AVG(score) FILTER (WHERE status != 'skip') >= 0.9 THEN 'Full EE Parity'
        WHEN AVG(score) FILTER (WHERE status != 'skip') >= 0.75 THEN 'Production Ready'
        WHEN AVG(score) FILTER (WHERE status != 'skip') >= 0.5 THEN 'MVP Ready'
        ELSE 'Not Ready'
    END as readiness_status
FROM public.ee_parity_results r
JOIN latest_run lr ON r.test_run_id = lr.test_run_id;

-- ==================================================
-- VIEW: Parity trend over time
-- ==================================================

CREATE OR REPLACE VIEW public.v_parity_trend AS
SELECT
    DATE_TRUNC('day', created_at) as test_date,
    test_run_id,
    COUNT(*) as total_tests,
    ROUND(AVG(score) FILTER (WHERE status != 'skip') * 100, 1) as parity_score,
    COUNT(*) FILTER (WHERE status = 'full') as full_count,
    COUNT(*) FILTER (WHERE status = 'missing') as missing_count
FROM public.ee_parity_results
GROUP BY DATE_TRUNC('day', created_at), test_run_id
ORDER BY test_date DESC;

-- ==================================================
-- VIEW: Gap analysis - what's missing
-- ==================================================

CREATE OR REPLACE VIEW public.v_parity_gaps AS
WITH latest_run AS (
    SELECT test_run_id
    FROM public.ee_parity_results
    ORDER BY created_at DESC
    LIMIT 1
)
SELECT
    r.category,
    r.feature,
    r.ee_description,
    r.status,
    r.notes,
    CASE r.category
        WHEN 'payroll' THEN 1
        WHEN 'accounting' THEN 2
        WHEN 'approvals' THEN 3
        WHEN 'helpdesk' THEN 4
        WHEN 'planning' THEN 5
        ELSE 6
    END as priority_order
FROM public.ee_parity_results r
JOIN latest_run lr ON r.test_run_id = lr.test_run_id
WHERE r.status IN ('missing', 'partial')
ORDER BY priority_order, r.score ASC;

-- ==================================================
-- FUNCTION: Insert test results from JSON
-- ==================================================

CREATE OR REPLACE FUNCTION public.insert_parity_results(results_json JSONB)
RETURNS UUID AS $$
DECLARE
    run_id UUID := gen_random_uuid();
    result_record JSONB;
BEGIN
    FOR result_record IN SELECT * FROM jsonb_array_elements(results_json->'results')
    LOOP
        INSERT INTO public.ee_parity_results (
            test_run_id,
            test_id,
            category,
            feature,
            status,
            score,
            notes,
            error
        ) VALUES (
            run_id,
            result_record->>'test_id',
            result_record->>'category',
            result_record->>'feature',
            result_record->>'status',
            (result_record->>'score')::DECIMAL,
            result_record->>'notes',
            result_record->>'error'
        );
    END LOOP;

    RETURN run_id;
END;
$$ LANGUAGE plpgsql;

-- ==================================================
-- Example: Insert test results
-- ==================================================

-- Example usage from Python:
--
-- import json
-- import requests
--
-- # After running test_ee_parity.py --report json
-- with open('parity_report.json') as f:
--     results = json.load(f)
--
-- # Insert via Supabase
-- response = supabase.rpc('insert_parity_results', {'results_json': results}).execute()
-- print(f"Test run ID: {response.data}")

-- ==================================================
-- Superset Dashboard Configuration
-- ==================================================

/*
Create these charts in Superset:

1. BIG NUMBER - Overall Parity Score
   Dataset: v_overall_parity
   Metric: overall_parity_score

2. PIE CHART - Status Distribution
   Dataset: v_latest_parity_results
   Dimension: status
   Metric: COUNT(*)

3. BAR CHART - Parity by Category
   Dataset: v_parity_scorecard
   X-Axis: category
   Y-Axis: parity_percentage
   Color: status_label

4. LINE CHART - Parity Trend
   Dataset: v_parity_trend
   X-Axis: test_date
   Y-Axis: parity_score

5. TABLE - Gap Analysis
   Dataset: v_parity_gaps
   Columns: category, feature, ee_description, status, notes

6. HEATMAP - Feature Coverage
   Dataset: v_latest_parity_results
   X: category
   Y: feature
   Value: score
*/

COMMENT ON VIEW public.v_overall_parity IS 'Superset dataset: Overall parity KPI';
COMMENT ON VIEW public.v_parity_scorecard IS 'Superset dataset: Category-level scorecard';
COMMENT ON VIEW public.v_parity_trend IS 'Superset dataset: Historical trend';
COMMENT ON VIEW public.v_parity_gaps IS 'Superset dataset: Missing features analysis';
