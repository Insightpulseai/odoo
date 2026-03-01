-- ============================================================================
-- DeerFlow Patterns: Skills Registry + Memory Plane + Error Taxonomy + Benchmarks
-- ============================================================================
-- Created: 2026-03-02
-- Spec:    spec/deerflow-patterns-adoption/
-- SSOT:    ssot/agents/skills.yaml  (synced by skills-sync GitHub Action)
--          ssot/errors/failure_modes.yaml
--          ssot/agents/benchmark.yaml
-- ============================================================================

-- Step 1: Skills Registry -------------------------------------------------

CREATE TABLE IF NOT EXISTS ops.skills (
  id              TEXT        PRIMARY KEY,              -- matches ssot/agents/skills.yaml id
  name            TEXT        NOT NULL,
  description     TEXT,
  executor        TEXT        NOT NULL DEFAULT 'vercel_sandbox'
                              CHECK (executor IN ('vercel_sandbox', 'do_runner')),
  max_duration_s  INTEGER     NOT NULL DEFAULT 300,
  tags            TEXT[]      NOT NULL DEFAULT '{}',
  state_machine   TEXT[]      NOT NULL DEFAULT '{PLAN,PATCH,VERIFY,PR}',
  owner           TEXT,
  status          TEXT        NOT NULL DEFAULT 'active'
                              CHECK (status IN ('active', 'deprecated', 'experimental')),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  metadata        JSONB       NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS ops.skill_versions (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_id    TEXT        NOT NULL REFERENCES ops.skills(id) ON DELETE CASCADE,
  version     INTEGER     NOT NULL,
  diff        JSONB       NOT NULL DEFAULT '{}'::jsonb,  -- field-level change log
  changed_by  TEXT,
  changed_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_skills_status ON ops.skills(status);
CREATE INDEX IF NOT EXISTS idx_skill_versions_skill ON ops.skill_versions(skill_id, version DESC);

-- updated_at trigger for skills
CREATE OR REPLACE FUNCTION ops.set_skills_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_ops_skills_updated_at ON ops.skills;
CREATE TRIGGER trg_ops_skills_updated_at
BEFORE UPDATE ON ops.skills
FOR EACH ROW EXECUTE FUNCTION ops.set_skills_updated_at();


-- Step 2: Add skill_id to ops.runs -----------------------------------------

ALTER TABLE ops.runs ADD COLUMN IF NOT EXISTS
  skill_id TEXT REFERENCES ops.skills(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_runs_skill_id ON ops.runs(skill_id);


-- Step 3: Memory Plane ------------------------------------------------------

CREATE TABLE IF NOT EXISTS ops.memory_entries (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  scope       TEXT        NOT NULL CHECK (scope IN ('run', 'project', 'org')),
  key         TEXT        NOT NULL,
  value       JSONB       NOT NULL DEFAULT '{}'::jsonb,
  run_id      UUID        REFERENCES ops.runs(id) ON DELETE CASCADE,  -- only for scope='run'
  project     TEXT,                                                     -- only for scope='project'
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at  TIMESTAMPTZ                                               -- NULL = never expires
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_memory_run_key
  ON ops.memory_entries(scope, run_id, key)
  WHERE scope = 'run' AND run_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_memory_project_key
  ON ops.memory_entries(scope, project, key)
  WHERE scope = 'project' AND project IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS idx_memory_org_key
  ON ops.memory_entries(scope, key)
  WHERE scope = 'org';

CREATE INDEX IF NOT EXISTS idx_memory_scope ON ops.memory_entries(scope);
CREATE INDEX IF NOT EXISTS idx_memory_expires ON ops.memory_entries(expires_at)
  WHERE expires_at IS NOT NULL;

CREATE OR REPLACE FUNCTION ops.set_memory_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_ops_memory_updated_at ON ops.memory_entries;
CREATE TRIGGER trg_ops_memory_updated_at
BEFORE UPDATE ON ops.memory_entries
FOR EACH ROW EXECUTE FUNCTION ops.set_memory_updated_at();


-- Step 4: Agent Errors (with fingerprint dedup) ----------------------------

CREATE TABLE IF NOT EXISTS ops.agent_errors (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id          UUID        NOT NULL REFERENCES ops.runs(id) ON DELETE CASCADE,
  skill_id        TEXT        REFERENCES ops.skills(id) ON DELETE SET NULL,
  failure_mode    TEXT        NOT NULL,                -- e.g. "AGENT.VERIFY_CI_FAIL"
  fingerprint     TEXT        NOT NULL,                -- sha256 of (skill_id, failure_mode, context_hash)
  message         TEXT,
  detail          JSONB       NOT NULL DEFAULT '{}'::jsonb,
  resolved        BOOLEAN     NOT NULL DEFAULT false,
  resolved_at     TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_errors_run     ON ops.agent_errors(run_id);
CREATE INDEX IF NOT EXISTS idx_agent_errors_fp      ON ops.agent_errors(fingerprint);
CREATE INDEX IF NOT EXISTS idx_agent_errors_mode    ON ops.agent_errors(failure_mode);
CREATE INDEX IF NOT EXISTS idx_agent_errors_resolved ON ops.agent_errors(resolved);


-- Step 5: Benchmark Results -------------------------------------------------

CREATE TABLE IF NOT EXISTS ops.agent_benchmark_results (
  id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id              UUID        NOT NULL REFERENCES ops.runs(id) ON DELETE CASCADE,
  skill_id            TEXT        NOT NULL REFERENCES ops.skills(id) ON DELETE CASCADE,
  composite_score     NUMERIC(5,2) NOT NULL,
  tier                TEXT        NOT NULL CHECK (tier IN ('A', 'B', 'C', 'F')),
  evidence_compliance NUMERIC(5,4),
  diff_minimality     NUMERIC(5,4),
  ci_pass_rate        NUMERIC(5,4),
  time_to_green_s     INTEGER,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
  metadata            JSONB       NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_benchmark_skill   ON ops.agent_benchmark_results(skill_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_benchmark_tier    ON ops.agent_benchmark_results(tier);
CREATE INDEX IF NOT EXISTS idx_benchmark_score   ON ops.agent_benchmark_results(composite_score DESC);


-- Step 6: Row Level Security ------------------------------------------------

ALTER TABLE ops.skills                   ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.skill_versions           ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.memory_entries           ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.agent_errors             ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.agent_benchmark_results  ENABLE ROW LEVEL SECURITY;

-- service_role: full access
CREATE POLICY skills_service_all ON ops.skills
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY skill_versions_service_all ON ops.skill_versions
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY memory_service_all ON ops.memory_entries
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY errors_service_all ON ops.agent_errors
  FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY benchmark_service_all ON ops.agent_benchmark_results
  FOR ALL TO service_role USING (true) WITH CHECK (true);

-- authenticated: read-only (ops console users)
-- anon: NO access to any of these tables
CREATE POLICY skills_auth_read ON ops.skills
  FOR SELECT TO authenticated USING (true);

CREATE POLICY skill_versions_auth_read ON ops.skill_versions
  FOR SELECT TO authenticated USING (true);

CREATE POLICY memory_auth_own ON ops.memory_entries
  FOR SELECT TO authenticated USING (true);

CREATE POLICY errors_auth_read ON ops.agent_errors
  FOR SELECT TO authenticated USING (true);

CREATE POLICY benchmark_auth_read ON ops.agent_benchmark_results
  FOR SELECT TO authenticated USING (true);
