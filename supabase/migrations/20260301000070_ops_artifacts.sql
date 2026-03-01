-- 20260301000070_ops_artifacts.sql
-- Build artifact registry for iOS simulator builds, TestFlight IPAs, and future artifact kinds.
-- Provides a queryable audit trail of CI-produced artifacts; ingested by ios-preview-builds.yml.

CREATE TABLE IF NOT EXISTS ops.artifacts (
  id           uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  kind         text        NOT NULL,
  sha          text        NOT NULL,
  branch       text,
  pr_number    integer,
  run_id       text,
  artifact_url text,
  metadata     jsonb       NOT NULL DEFAULT '{}',
  created_at   timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE  ops.artifacts IS
  'CI-produced build artifacts. kind values: ios_simulator_build, ios_ipa, web_build.';
COMMENT ON COLUMN ops.artifacts.kind IS
  'ios_simulator_build | ios_ipa | web_build | other';
COMMENT ON COLUMN ops.artifacts.sha IS
  'Full git commit SHA that produced this artifact.';
COMMENT ON COLUMN ops.artifacts.artifact_url IS
  'GitHub Actions run URL or direct download URL.';
COMMENT ON COLUMN ops.artifacts.metadata IS
  'Freeform JSON: {sim_app_found, tests_passed, destination, workflow, ...}';

-- Indexes: recent artifacts per kind, and lookup by SHA
CREATE INDEX IF NOT EXISTS ops_artifacts_kind_created
  ON ops.artifacts (kind, created_at DESC);

CREATE INDEX IF NOT EXISTS ops_artifacts_sha
  ON ops.artifacts (sha);

-- RLS
ALTER TABLE ops.artifacts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_insert"
  ON ops.artifacts
  FOR INSERT
  TO service_role
  WITH CHECK (true);

CREATE POLICY "authenticated_read"
  ON ops.artifacts
  FOR SELECT
  TO authenticated
  USING (true);
