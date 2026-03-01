-- ============================================================================
-- BREAKING CHANGE: Universal Run Model (ops.runs) Unification
-- ============================================================================
-- Created: 2026-03-01
-- Rationale: Consolidate `ops.agent_runs`, `ops.maintenance_runs` into a single
--            universal `ops.runs` envelope.
-- Impact: Recreates ops.runs. Converts ops.agent_runs to a view.
-- ============================================================================

-- Step 1: Create the universal runs table (if it doesn't already exist from an older rollback)
CREATE TABLE IF NOT EXISTS ops.runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled')),
  kind TEXT NOT NULL DEFAULT 'agent' CHECK (kind IN ('agent', 'maintenance', 'convergence_scan', 'autoheal')),
  agent_id TEXT,
  triggered_by TEXT,
  repo TEXT,
  ref TEXT,
  task_id TEXT,
  pr_url TEXT,
  evidence_path TEXT,
  input JSONB NOT NULL DEFAULT '{}'::jsonb,
  output JSONB NOT NULL DEFAULT '{}'::jsonb,
  task_description TEXT,
  score INTEGER,
  metadata JSONB DEFAULT '{}'::jsonb
);

-- Run Events (Universal)
CREATE TABLE IF NOT EXISTS ops.run_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES ops.runs(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  step TEXT,
  outcome TEXT,
  level TEXT NOT NULL DEFAULT 'info' CHECK (level IN ('debug', 'info', 'warn', 'error')),
  message TEXT,
  detail JSONB NOT NULL DEFAULT '{}'::jsonb,
  event_type TEXT,
  payload JSONB DEFAULT '{}'::jsonb,
  data JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Artifacts (Universal)
CREATE TABLE IF NOT EXISTS ops.artifacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES ops.runs(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  kind TEXT,
  name TEXT,
  path TEXT,
  uri TEXT,
  meta JSONB NOT NULL DEFAULT '{}'::jsonb,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Step 2: Migrate existing agent_runs data over to ops.runs
-- Note: We assume agent_runs has columns like agent_id, status, task_description
INSERT INTO ops.runs (id, created_at, updated_at, status, kind, agent_id, task_description, metadata)
SELECT id, created_at, updated_at, status, 'agent' as kind, agent_id, task_description, metadata
FROM ops.agent_runs
ON CONFLICT (id) DO NOTHING;

INSERT INTO ops.run_events (id, run_id, created_at, event_type, payload)
SELECT id, run_id, created_at, event_type, payload
FROM ops.agent_events
ON CONFLICT (id) DO NOTHING;

INSERT INTO ops.artifacts (id, run_id, created_at, name, path, metadata)
SELECT id, run_id, created_at, name, path, metadata
FROM ops.agent_artifacts
ON CONFLICT (id) DO NOTHING;

-- Step 3: Drop the actual tables, replace with views
DROP TABLE IF EXISTS ops.agent_events CASCADE;
DROP TABLE IF EXISTS ops.agent_artifacts CASCADE;
DROP TABLE IF EXISTS ops.agent_runs CASCADE;

-- Step 4: Create Views for backwards compatibility
CREATE VIEW ops.agent_runs AS
SELECT id, created_at, updated_at, status, agent_id, task_description, metadata
FROM ops.runs
WHERE kind = 'agent';

CREATE VIEW ops.agent_events AS
SELECT id, run_id, created_at, event_type, payload
FROM ops.run_events
WHERE run_id IN (SELECT id FROM ops.runs WHERE kind = 'agent');

CREATE VIEW ops.agent_artifacts AS
SELECT id, run_id, created_at, name, path, metadata
FROM ops.artifacts
WHERE run_id IN (SELECT id FROM ops.runs WHERE kind = 'agent');

-- Step 5: (Optional) Triggers to make views updatable or redirect functions
-- Currently we will just rely on direct inserts to ops.runs for new agents.

-- Step 6: Fix Updated At
CREATE OR REPLACE FUNCTION ops.set_runs_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_ops_runs_updated_at ON ops.runs;
CREATE TRIGGER trg_ops_runs_updated_at
BEFORE UPDATE ON ops.runs
FOR EACH ROW EXECUTE FUNCTION ops.set_runs_updated_at();
