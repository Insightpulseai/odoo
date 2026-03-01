-- 20260301000071_ops_artifacts_hardening.sql
-- Harden ops.artifacts: add status/reason/env/name columns + dedupe unique index.
-- Required before ios-preview-builds.yml can post truthful per-run records.

-- 1. Add status column (success | failed | skipped).
--    Defaults to 'success' so existing rows remain valid.
ALTER TABLE ops.artifacts
  ADD COLUMN IF NOT EXISTS status text NOT NULL DEFAULT 'success'
    CHECK (status IN ('success', 'failed', 'skipped'));

-- 2. Add reason column — human-readable code for non-success rows.
--    Examples: NO_XCODE_PROJECT, SIM_BUILD_FAILED, FASTLANE_FAILED, CANCELLED.
ALTER TABLE ops.artifacts
  ADD COLUMN IF NOT EXISTS reason text;

-- 3. Add env column — execution environment (ci | local | staging).
--    Defaults to 'ci' for all existing rows.
ALTER TABLE ops.artifacts
  ADD COLUMN IF NOT EXISTS env text NOT NULL DEFAULT 'ci';

-- 4. Add name column — unique artifact name within a run.
--    Examples: ios-preview-abc12345, OdooMobile-ipa-abc12345.
ALTER TABLE ops.artifacts
  ADD COLUMN IF NOT EXISTS name text;

-- 5. Column comments
COMMENT ON COLUMN ops.artifacts.status IS
  'success | failed | skipped — reflects actual build outcome';
COMMENT ON COLUMN ops.artifacts.reason IS
  'Machine-readable reason code when status != success (e.g. NO_XCODE_PROJECT)';
COMMENT ON COLUMN ops.artifacts.env IS
  'Execution environment: ci | local | staging';
COMMENT ON COLUMN ops.artifacts.name IS
  'Unique artifact name within a run (e.g. ios-preview-abc12345)';

-- 6. Dedupe unique index: one row per (kind, sha, env, name) tuple.
--    Uses a partial index to tolerate NULL name (historical rows without name).
CREATE UNIQUE INDEX IF NOT EXISTS ops_artifacts_kind_sha_env_name_uq
  ON ops.artifacts (kind, sha, env, name)
  WHERE name IS NOT NULL;

-- 7. Index for status-based lookups (e.g. "find all failed ios builds")
CREATE INDEX IF NOT EXISTS ops_artifacts_status
  ON ops.artifacts (status, kind, created_at DESC);
