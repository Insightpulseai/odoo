-- ============================================================================
-- BREAKING CHANGE: Rename agent tracking tables to avoid OdooOps Sh conflict
-- ============================================================================
-- Created: 2026-02-13
-- Rationale: ops.runs and ops.run_events will be used for OdooOps workflow
--            execution. Existing agent execution tracking moved to agent_* namespace.
-- Impact: 2 Edge Functions require updates (ops-ingest, executor)
-- ============================================================================

-- Step 1: Rename tables
ALTER TABLE ops.runs RENAME TO agent_runs;
ALTER TABLE ops.run_events RENAME TO agent_events;
ALTER TABLE ops.artifacts RENAME TO agent_artifacts;

-- Step 2: Update foreign key constraints
ALTER TABLE ops.agent_events
  DROP CONSTRAINT IF EXISTS run_events_run_id_fkey,
  ADD CONSTRAINT agent_events_run_id_fkey
    FOREIGN KEY (run_id) REFERENCES ops.agent_runs(id) ON DELETE CASCADE;

ALTER TABLE ops.agent_artifacts
  DROP CONSTRAINT IF EXISTS artifacts_run_id_fkey,
  ADD CONSTRAINT agent_artifacts_run_id_fkey
    FOREIGN KEY (run_id) REFERENCES ops.agent_runs(id) ON DELETE CASCADE;

-- Step 3: Rename indexes
ALTER INDEX IF EXISTS ops.runs_pkey RENAME TO agent_runs_pkey;
ALTER INDEX IF EXISTS ops.runs_agent_id_idx RENAME TO agent_runs_agent_id_idx;
ALTER INDEX IF EXISTS ops.runs_status_idx RENAME TO agent_runs_status_idx;
ALTER INDEX IF EXISTS ops.run_events_pkey RENAME TO agent_events_pkey;
ALTER INDEX IF EXISTS ops.run_events_run_id_idx RENAME TO agent_events_run_id_idx;

-- Step 4: Rename triggers
ALTER TRIGGER IF EXISTS trg_ops_runs_updated_at ON ops.agent_runs RENAME TO trg_agent_runs_updated_at;

-- Step 5: Update function signatures
CREATE OR REPLACE FUNCTION ops.start_agent_run(
  p_agent_id TEXT,
  p_task_description TEXT,
  p_metadata JSONB DEFAULT '{}'::jsonb
) RETURNS UUID AS $$
DECLARE
  v_run_id UUID;
BEGIN
  INSERT INTO ops.agent_runs (agent_id, task_description, status, metadata)
  VALUES (p_agent_id, p_task_description, 'running', p_metadata)
  RETURNING id INTO v_run_id;

  RETURN v_run_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION ops.log_agent_event(
  p_run_id UUID,
  p_event_type TEXT,
  p_payload JSONB DEFAULT '{}'::jsonb
) RETURNS UUID AS $$
DECLARE
  v_event_id UUID;
BEGIN
  INSERT INTO ops.agent_events (run_id, event_type, payload)
  VALUES (p_run_id, p_event_type, p_payload)
  RETURNING id INTO v_event_id;

  RETURN v_event_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION ops.complete_agent_run(
  p_run_id UUID,
  p_status TEXT,
  p_result_summary TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
  UPDATE ops.agent_runs
  SET status = p_status,
      completed_at = now(),
      result_summary = COALESCE(p_result_summary, result_summary)
  WHERE id = p_run_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION ops.fail_agent_run(
  p_run_id UUID,
  p_error_message TEXT
) RETURNS VOID AS $$
BEGIN
  UPDATE ops.agent_runs
  SET status = 'failed',
      completed_at = now(),
      result_summary = p_error_message
  WHERE id = p_run_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION ops.add_agent_artifact(
  p_run_id UUID,
  p_name TEXT,
  p_path TEXT,
  p_metadata JSONB DEFAULT '{}'::jsonb
) RETURNS UUID AS $$
DECLARE
  v_artifact_id UUID;
BEGIN
  INSERT INTO ops.agent_artifacts (run_id, name, path, metadata)
  VALUES (p_run_id, p_name, p_path, p_metadata)
  RETURNING id INTO v_artifact_id;

  RETURN v_artifact_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 6: Drop old functions
DROP FUNCTION IF EXISTS ops.start_run(TEXT, TEXT, JSONB);
DROP FUNCTION IF EXISTS ops.log_event(UUID, TEXT, JSONB);
DROP FUNCTION IF EXISTS ops.complete_run(UUID, TEXT, TEXT);
DROP FUNCTION IF EXISTS ops.fail_run(UUID, TEXT);
DROP FUNCTION IF EXISTS ops.add_artifact(UUID, TEXT, TEXT, JSONB);

COMMENT ON TABLE ops.agent_runs IS 'Agent execution tracking (renamed from ops.runs for OdooOps Sh compatibility)';
COMMENT ON TABLE ops.agent_events IS 'Agent event logs (renamed from ops.run_events for OdooOps Sh compatibility)';
COMMENT ON TABLE ops.agent_artifacts IS 'Agent artifacts (renamed from ops.artifacts for OdooOps Sh compatibility)';
