-- ============================================================================
-- PPM Clarity: Portfolio Initiatives + Status Rollups
-- ============================================================================
-- Created: 2026-03-02
-- Spec:    spec/ppm-clarity/
-- SSOT:    ssot/ppm/portfolio.yaml  (seeded by ops-ppm-rollup Edge Function)
-- ============================================================================

-- Portfolio initiatives (mirrors ssot/ppm/portfolio.yaml)
CREATE TABLE IF NOT EXISTS ops.ppm_initiatives (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  initiative_id    TEXT        NOT NULL UNIQUE,           -- e.g. "INIT-001"
  name             TEXT        NOT NULL,
  owner            TEXT,
  status           TEXT        NOT NULL DEFAULT 'active'
                               CHECK (status IN ('active','on-hold','completed','cancelled')),
  spec_slug        TEXT,                                   -- folder under spec/
  github_label     TEXT,                                   -- GitHub label for PR tracking
  start_date       DATE,
  target_date      DATE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  metadata         JSONB       NOT NULL DEFAULT '{}'::jsonb
);

-- Computed status rollups (written by ops-ppm-rollup Edge Function)
CREATE TABLE IF NOT EXISTS ops.ppm_status_rollups (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  initiative_id    TEXT        NOT NULL REFERENCES ops.ppm_initiatives(initiative_id) ON DELETE CASCADE,
  computed_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  blocking_findings INTEGER    NOT NULL DEFAULT 0,
  merged_prs_30d   INTEGER     NOT NULL DEFAULT 0,
  last_run_at      TIMESTAMPTZ,
  last_run_status  TEXT,
  notes            TEXT,
  metadata         JSONB       NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_ppm_initiatives_status
  ON ops.ppm_initiatives(status);

CREATE INDEX IF NOT EXISTS idx_ppm_initiatives_owner
  ON ops.ppm_initiatives(owner);

CREATE INDEX IF NOT EXISTS idx_ppm_rollups_initiative
  ON ops.ppm_status_rollups(initiative_id, computed_at DESC);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_ppm_initiatives_fts
  ON ops.ppm_initiatives
  USING GIN (to_tsvector('english', coalesce(name,'') || ' ' || coalesce(spec_slug,'') || ' ' || coalesce(owner,'')));

-- Updated-at trigger
CREATE OR REPLACE FUNCTION ops.set_ppm_initiatives_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_ppm_initiatives_updated_at ON ops.ppm_initiatives;
CREATE TRIGGER trg_ppm_initiatives_updated_at
BEFORE UPDATE ON ops.ppm_initiatives
FOR EACH ROW EXECUTE FUNCTION ops.set_ppm_initiatives_updated_at();

-- Row Level Security
ALTER TABLE ops.ppm_initiatives     ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.ppm_status_rollups  ENABLE ROW LEVEL SECURITY;

-- service_role: full access (for Edge Functions)
CREATE POLICY ppm_initiatives_service_all ON ops.ppm_initiatives
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY ppm_rollups_service_all ON ops.ppm_status_rollups
  FOR ALL TO service_role USING (true) WITH CHECK (true);

-- authenticated: read-only
CREATE POLICY ppm_initiatives_auth_select ON ops.ppm_initiatives
  FOR SELECT TO authenticated USING (true);

CREATE POLICY ppm_rollups_auth_select ON ops.ppm_status_rollups
  FOR SELECT TO authenticated USING (true);
