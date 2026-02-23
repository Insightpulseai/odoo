-- =============================================================================
-- Migration: ops.repo_hygiene schema
-- File: 20260221000003_ops_repo_hygiene.sql
-- Purpose: Tables for nightly repo hygiene job tracking.
--          Jobs defined in automations/repo_hygiene/jobs/nightly.yml.
-- =============================================================================
-- Idempotent: CREATE TABLE IF NOT EXISTS, CREATE INDEX IF NOT EXISTS
-- Requires: ops schema (created in prior migrations)
-- =============================================================================

BEGIN;

-- Ensure ops schema exists (idempotent)
CREATE SCHEMA IF NOT EXISTS ops;

-- =============================================================================
-- Table: ops.repo_hygiene_jobs
-- Registry of defined hygiene jobs (SSOT from nightly.yml, seeded here).
-- =============================================================================
CREATE TABLE IF NOT EXISTS ops.repo_hygiene_jobs (
  id            BIGSERIAL PRIMARY KEY,
  job_name      TEXT        NOT NULL UNIQUE,
  display_name  TEXT        NOT NULL,
  schedule_utc  TEXT        NOT NULL,   -- cron expression
  timezone_note TEXT,
  config_path   TEXT        NOT NULL,   -- path to SSOT yml file
  enabled       BOOLEAN     NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE ops.repo_hygiene_jobs IS
  'Registry of repo hygiene job definitions. SSOT is automations/repo_hygiene/jobs/*.yml.';

-- Seed the nightly job
INSERT INTO ops.repo_hygiene_jobs (job_name, display_name, schedule_utc, timezone_note, config_path)
VALUES (
  'nightly',
  'Nightly Repo Hygiene',
  '10 17 * * *',
  '01:10 Asia/Manila (UTC+08:00)',
  'automations/repo_hygiene/jobs/nightly.yml'
) ON CONFLICT (job_name) DO NOTHING;

-- =============================================================================
-- Table: ops.repo_hygiene_runs
-- One row per execution of a hygiene job.
-- =============================================================================
CREATE TABLE IF NOT EXISTS ops.repo_hygiene_runs (
  id             BIGSERIAL    PRIMARY KEY,
  job_name       TEXT         NOT NULL REFERENCES ops.repo_hygiene_jobs(job_name),
  run_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  completed_at   TIMESTAMPTZ,
  status         TEXT         NOT NULL CHECK (status IN ('running','passed','failed','error'))
                              DEFAULT 'running',
  p0_passed      BOOLEAN,
  p1_warnings    INT          DEFAULT 0,
  p2_infos       INT          DEFAULT 0,
  duration_ms    INT,
  git_sha        TEXT,        -- HEAD SHA of repo at time of run
  git_branch     TEXT,        -- branch name at time of run
  request_id     TEXT,        -- x-request-id from Edge Function invocation
  error_detail   TEXT
);

CREATE INDEX IF NOT EXISTS idx_repo_hygiene_runs_job_run_at
  ON ops.repo_hygiene_runs(job_name, run_at DESC);

CREATE INDEX IF NOT EXISTS idx_repo_hygiene_runs_status
  ON ops.repo_hygiene_runs(status);

COMMENT ON TABLE ops.repo_hygiene_runs IS
  'Execution history for repo hygiene jobs. One row per run.';

-- =============================================================================
-- Table: ops.repo_hygiene_findings
-- Individual check results within a run.
-- =============================================================================
CREATE TABLE IF NOT EXISTS ops.repo_hygiene_findings (
  id          BIGSERIAL    PRIMARY KEY,
  run_id      BIGINT       NOT NULL REFERENCES ops.repo_hygiene_runs(id) ON DELETE CASCADE,
  check_id    TEXT         NOT NULL,   -- e.g. "p0_root_allowlist"
  priority    TEXT         NOT NULL CHECK (priority IN ('p0','p1','p2')),
  severity    TEXT         NOT NULL CHECK (severity IN ('critical','warning','info')),
  status      TEXT         NOT NULL CHECK (status IN ('passed','failed','skipped')),
  message     TEXT,
  detail      JSONB,                   -- structured detail (paths, counts, etc.)
  created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_repo_hygiene_findings_run_id
  ON ops.repo_hygiene_findings(run_id);

CREATE INDEX IF NOT EXISTS idx_repo_hygiene_findings_priority_status
  ON ops.repo_hygiene_findings(priority, status);

COMMENT ON TABLE ops.repo_hygiene_findings IS
  'Per-check results within a hygiene run. Joined to ops.repo_hygiene_runs.';

-- =============================================================================
-- Table: ops.repo_hygiene_artifacts
-- File artifacts produced by a run (reports, logs, etc.).
-- =============================================================================
CREATE TABLE IF NOT EXISTS ops.repo_hygiene_artifacts (
  id           BIGSERIAL    PRIMARY KEY,
  run_id       BIGINT       NOT NULL REFERENCES ops.repo_hygiene_runs(id) ON DELETE CASCADE,
  artifact_key TEXT         NOT NULL,   -- e.g. "summary_report"
  storage_path TEXT,                    -- Supabase Storage path if stored
  content      TEXT,                    -- inline content if small
  mime_type    TEXT         DEFAULT 'text/plain',
  created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_repo_hygiene_artifacts_run_id
  ON ops.repo_hygiene_artifacts(run_id);

COMMENT ON TABLE ops.repo_hygiene_artifacts IS
  'File artifacts produced by hygiene runs (reports, diff summaries, etc.).';

-- =============================================================================
-- Row-Level Security — service_role only for writes; reads open to authenticated
-- =============================================================================
ALTER TABLE ops.repo_hygiene_jobs     ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.repo_hygiene_runs     ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.repo_hygiene_findings ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.repo_hygiene_artifacts ENABLE ROW LEVEL SECURITY;

-- Jobs: all authenticated users can read; only service_role can write
CREATE POLICY "hygiene_jobs_read_authenticated"
  ON ops.repo_hygiene_jobs FOR SELECT
  TO authenticated USING (true);

CREATE POLICY "hygiene_jobs_write_service_role"
  ON ops.repo_hygiene_jobs FOR ALL
  TO service_role USING (true);

-- Runs: same pattern
CREATE POLICY "hygiene_runs_read_authenticated"
  ON ops.repo_hygiene_runs FOR SELECT
  TO authenticated USING (true);

CREATE POLICY "hygiene_runs_write_service_role"
  ON ops.repo_hygiene_runs FOR ALL
  TO service_role USING (true);

-- Findings: same pattern
CREATE POLICY "hygiene_findings_read_authenticated"
  ON ops.repo_hygiene_findings FOR SELECT
  TO authenticated USING (true);

CREATE POLICY "hygiene_findings_write_service_role"
  ON ops.repo_hygiene_findings FOR ALL
  TO service_role USING (true);

-- Artifacts: same pattern
CREATE POLICY "hygiene_artifacts_read_authenticated"
  ON ops.repo_hygiene_artifacts FOR SELECT
  TO authenticated USING (true);

CREATE POLICY "hygiene_artifacts_write_service_role"
  ON ops.repo_hygiene_artifacts FOR ALL
  TO service_role USING (true);

-- =============================================================================
-- Audit event for migration application
-- =============================================================================
INSERT INTO ops.platform_events (event_type, actor, target, payload, status)
VALUES (
  'migration_applied',
  'migration:20260221000003',
  'ops.repo_hygiene_*',
  '{"tables":["repo_hygiene_jobs","repo_hygiene_runs","repo_hygiene_findings","repo_hygiene_artifacts"]}'::jsonb,
  'ok'
);

COMMIT;

-- =============================================================================
-- Verification (run after apply):
--
-- SELECT table_name FROM information_schema.tables
--   WHERE table_schema = 'ops' AND table_name LIKE 'repo_hygiene%';
--
-- SELECT * FROM ops.repo_hygiene_jobs;
-- =============================================================================
