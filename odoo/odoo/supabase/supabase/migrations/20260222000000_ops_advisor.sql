-- Migration: ops advisor tables
-- Creates the ops schema + advisor_runs, advisor_findings, advisor_scores
-- All tables are service-role only (no anon reads).

CREATE SCHEMA IF NOT EXISTS ops;

-- ─── advisor_runs ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ops.advisor_runs (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  team_id       text NOT NULL DEFAULT 'default',
  triggered_by  text NOT NULL DEFAULT 'system',   -- 'system' | 'manual' | 'api'
  status        text NOT NULL DEFAULT 'pending',   -- 'pending' | 'running' | 'complete' | 'error'
  started_at    timestamptz NOT NULL DEFAULT now(),
  finished_at   timestamptz,
  summary       jsonb                              -- {total_findings, by_severity, by_pillar}
);

CREATE INDEX IF NOT EXISTS idx_advisor_runs_team_id_started ON ops.advisor_runs (team_id, started_at DESC);

-- ─── advisor_findings ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ops.advisor_findings (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id        uuid NOT NULL REFERENCES ops.advisor_runs(id) ON DELETE CASCADE,
  pillar        text NOT NULL,   -- 'cost'|'security'|'reliability'|'operational_excellence'|'performance'
  rule_id       text NOT NULL,   -- e.g. 'preview-protection-enabled'
  severity      text NOT NULL,   -- 'critical'|'high'|'medium'|'low'|'info'
  fingerprint   text UNIQUE NOT NULL, -- stable dedup key: sha256(rule_id + resource_ref)
  title         text NOT NULL,
  description   text,
  remediation   text,
  resource_ref  text,            -- e.g. 'vercel:project:odooops-console'
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_advisor_findings_run_id ON ops.advisor_findings (run_id);
CREATE INDEX IF NOT EXISTS idx_advisor_findings_pillar_severity ON ops.advisor_findings (pillar, severity);

-- ─── advisor_scores ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ops.advisor_scores (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id          uuid NOT NULL REFERENCES ops.advisor_runs(id) ON DELETE CASCADE,
  pillar          text NOT NULL,
  score           int NOT NULL CHECK (score >= 0 AND score <= 100),
  finding_counts  jsonb,         -- {critical: n, high: n, medium: n, low: n, info: n}
  computed_at     timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_advisor_scores_run_id ON ops.advisor_scores (run_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_advisor_scores_run_pillar ON ops.advisor_scores (run_id, pillar);

-- ─── RLS: service role only (no anon/public reads) ───────────────────────────
ALTER TABLE ops.advisor_runs      ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.advisor_findings  ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.advisor_scores    ENABLE ROW LEVEL SECURITY;

-- Service role bypasses RLS automatically; no explicit policy needed for service role.
-- Deny all other roles:
CREATE POLICY deny_all_runs      ON ops.advisor_runs      USING (false);
CREATE POLICY deny_all_findings  ON ops.advisor_findings  USING (false);
CREATE POLICY deny_all_scores    ON ops.advisor_scores    USING (false);
