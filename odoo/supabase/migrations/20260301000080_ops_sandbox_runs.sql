-- ============================================================================
-- Migration: ops.sandbox_runs — Vercel Sandbox execution records
-- Provider:  ssot/providers/vercel/sandbox.yaml
-- Contract:  docs/contracts/C-VERCEL-01-sandbox.md (planned)
-- Spec:      spec/cloudera-ai-workbench-reverse/ (WorkbenchX phase 0)
-- ============================================================================
--
-- Tables created:
--   ops.sandbox_runs  — durable ledger for Vercel Sandbox (and DO runner) runs
--
-- Append-only rule (Rule 5, ssot-platform.md):
--   DROP TABLE / TRUNCATE are forbidden for ops.* tables.
--   Only ADD COLUMN IF NOT EXISTS is allowed after initial creation.
-- ============================================================================

CREATE TABLE IF NOT EXISTS ops.sandbox_runs (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id       UUID        REFERENCES ops.runs(id),  -- parent ops.runs row (nullable for standalone)
  provider     TEXT        NOT NULL DEFAULT 'vercel_sandbox'
                           CHECK (provider IN ('vercel_sandbox', 'do_runner', 'local')),
  sandbox_id   TEXT,                                  -- external sandbox ID (e.g. Vercel Sandbox ID)
  status       TEXT        NOT NULL DEFAULT 'queued'
                           CHECK (status IN ('queued', 'running', 'success', 'failed', 'timeout')),
  exit_code    INTEGER,                               -- process exit code (0 = success)
  logs_url     TEXT,                                  -- Supabase Storage artifact URL for captured logs
  preview_url  TEXT,                                  -- Vercel Preview deployment URL (when available)
  started_at   TIMESTAMPTZ,
  finished_at  TIMESTAMPTZ,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS sandbox_runs_run_id_idx  ON ops.sandbox_runs (run_id);
CREATE INDEX IF NOT EXISTS sandbox_runs_status_idx  ON ops.sandbox_runs (status);
CREATE INDEX IF NOT EXISTS sandbox_runs_created_idx ON ops.sandbox_runs (created_at DESC);

-- RLS
ALTER TABLE ops.sandbox_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated can read sandbox_runs"
  ON ops.sandbox_runs FOR SELECT TO authenticated USING (true);

CREATE POLICY "service_role full access sandbox_runs"
  ON ops.sandbox_runs FOR ALL TO service_role USING (true);

COMMENT ON TABLE ops.sandbox_runs IS
  'Durable ledger for Vercel Sandbox and DO runner execution records. '
  'Provider: ssot/providers/vercel/sandbox.yaml. '
  'Append-only per Rule 5 (ssot-platform.md).';

COMMENT ON COLUMN ops.sandbox_runs.run_id IS
  'Foreign key to ops.runs — links sandbox execution to parent job run.';
COMMENT ON COLUMN ops.sandbox_runs.sandbox_id IS
  'External sandbox identifier (e.g. Vercel Sandbox ID).';
COMMENT ON COLUMN ops.sandbox_runs.logs_url IS
  'Supabase Storage URL for captured stdout/stderr log artifact.';
COMMENT ON COLUMN ops.sandbox_runs.preview_url IS
  'Vercel Preview deployment URL produced by this sandbox run, if applicable.';
