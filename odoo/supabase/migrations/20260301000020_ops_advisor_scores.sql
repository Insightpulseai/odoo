-- =============================================================================
-- Migration: 20260301000020_ops_advisor_scores.sql
-- Schema:    ops
-- Purpose:   Per-dimension rubric scores for advisor scans (agentic coding rubric)
-- Branch:    feat/advisor-migrations
-- Date:      2026-03-01
-- Depends:   20260301000010_ops_advisor.sql (ops.advisor_scans must exist)
-- =============================================================================

-- Drop the existing check constraint on provider and re-add with extended values
ALTER TABLE ops.advisor_scans
  DROP CONSTRAINT IF EXISTS advisor_scans_provider_check;

ALTER TABLE ops.advisor_scans
  ADD CONSTRAINT advisor_scans_provider_check
  CHECK (provider IN (
    'digitalocean',
    'vercel',
    'supabase',
    'github',
    'agentic_coding',
    'devops_lifecycle'
  ));

COMMENT ON COLUMN ops.advisor_scans.provider IS
  'Scan adapter: digitalocean | vercel | supabase | github | agentic_coding | devops_lifecycle';

-- -----------------------------------------------------------------------------
-- Table: ops.advisor_scores
-- Per-dimension rubric scores for advisor scans. One row per dimension per scan.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ops.advisor_scores (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id         UUID        NOT NULL
                                REFERENCES ops.advisor_scans(id)
                                ON DELETE CASCADE,
  rubric_id       TEXT        NOT NULL,    -- e.g. 'agentic_coding'
  dimension       TEXT        NOT NULL,    -- e.g. 'planning_quality'
  score           INTEGER     NOT NULL
                                CHECK (score >= 0 AND score <= 3),
  breakdown_json  JSONB,                   -- raw evidence used to compute score
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE  ops.advisor_scores IS
  'Per-dimension rubric scores for advisor scans. One row per dimension per scan.';
COMMENT ON COLUMN ops.advisor_scores.rubric_id IS
  'References ssot/advisor/rubrics/<rubric_id>.yaml';
COMMENT ON COLUMN ops.advisor_scores.dimension IS
  'Rubric dimension: planning_quality | patch_minimality | test_coverage | pr_evidence | audit_trail';
COMMENT ON COLUMN ops.advisor_scores.score IS
  'Score 0-3 per dimension. Total = sum of all dimensions for this scan.';
COMMENT ON COLUMN ops.advisor_scores.breakdown_json IS
  'Raw evidence captured during scoring (signals, counts, timestamps).';

ALTER TABLE ops.advisor_scores DISABLE ROW LEVEL SECURITY;

CREATE INDEX idx_advisor_scores_scan_id ON ops.advisor_scores(scan_id);
CREATE INDEX idx_advisor_scores_rubric ON ops.advisor_scores(rubric_id, dimension);

-- -----------------------------------------------------------------------------
-- View: ops.advisor_scan_totals
-- Aggregates per-scan rubric scores for quick dashboard consumption.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW ops.advisor_scan_totals AS
SELECT
  s.id           AS scan_id,
  s.provider,
  s.status,
  s.started_at,
  sc.rubric_id,
  SUM(sc.score)  AS total_score,
  COUNT(sc.id)   AS dimension_count
FROM ops.advisor_scans s
LEFT JOIN ops.advisor_scores sc ON sc.scan_id = s.id
GROUP BY s.id, s.provider, s.status, s.started_at, sc.rubric_id;

COMMENT ON VIEW ops.advisor_scan_totals IS
  'Aggregates per-scan rubric scores for quick dashboard consumption.';

-- Objects created:
--   ops.advisor_scores              (table, RLS disabled)
--   ops.advisor_scan_totals         (view)
--   idx_advisor_scores_scan_id      (index)
--   idx_advisor_scores_rubric       (index)
-- advisor_scans.provider constraint extended to include agentic_coding + devops_lifecycle
