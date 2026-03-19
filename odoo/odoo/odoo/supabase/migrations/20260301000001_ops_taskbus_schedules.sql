-- =============================================================================
-- Migration: ops.schedules + taskbus columns on ops.runs
-- Owner: Supabase (SSOT for scheduled agent runs)
-- Extends: 20260228_001_ops_llm_observability.sql
-- =============================================================================

-- Add agent + idempotency_key columns to ops.runs (idempotent)
ALTER TABLE ops.runs
  ADD COLUMN IF NOT EXISTS agent         text,
  ADD COLUMN IF NOT EXISTS input_json    jsonb DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS error_json    jsonb,
  ADD COLUMN IF NOT EXISTS idempotency_key text UNIQUE;

CREATE INDEX IF NOT EXISTS idx_runs_agent ON ops.runs (agent);
CREATE INDEX IF NOT EXISTS idx_runs_idempotency ON ops.runs (idempotency_key);

-- =============================================================================
-- ops.schedules — Cron schedule registry
-- Cron trigger reads this table every tick to determine due jobs.
-- =============================================================================
CREATE TABLE IF NOT EXISTS ops.schedules (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name            text NOT NULL UNIQUE,
    cron            text NOT NULL,           -- cron expression (informational; Vercel cron is external)
    job_type        text NOT NULL,           -- matches agents/registry job types
    agent           text NOT NULL,           -- agent name that handles this job
    input_json      jsonb DEFAULT '{}',      -- static input to pass per run
    enabled         boolean NOT NULL DEFAULT true,
    last_run_at     timestamptz,
    last_run_id     uuid REFERENCES ops.runs(id),
    created_at      timestamptz DEFAULT now(),
    updated_at      timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_schedules_enabled ON ops.schedules (enabled);
CREATE INDEX IF NOT EXISTS idx_schedules_job_type ON ops.schedules (job_type);

-- RLS
ALTER TABLE ops.schedules ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all" ON ops.schedules
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_read" ON ops.schedules
    FOR SELECT TO authenticated USING (true);

-- Grants
GRANT SELECT, UPDATE ON ops.schedules TO service_role;
GRANT SELECT ON ops.schedules TO authenticated;

-- =============================================================================
-- Helper: enqueue a run for a schedule (idempotent by bucket key)
-- Called from the cron tick endpoint.
-- =============================================================================
CREATE OR REPLACE FUNCTION ops.enqueue_scheduled_run(
    p_schedule_id  uuid,
    p_bucket_key   text,          -- e.g. schedule_id + yyyy-mm-dd-HH-mm
    p_now          timestamptz DEFAULT now()
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_sched  ops.schedules%ROWTYPE;
    v_run_id uuid;
BEGIN
    SELECT * INTO v_sched FROM ops.schedules WHERE id = p_schedule_id FOR UPDATE;

    IF NOT FOUND OR NOT v_sched.enabled THEN
        RETURN NULL;
    END IF;

    -- Idempotency: skip if this bucket was already enqueued
    SELECT id INTO v_run_id FROM ops.runs WHERE idempotency_key = p_bucket_key;
    IF v_run_id IS NOT NULL THEN
        RETURN v_run_id;
    END IF;

    INSERT INTO ops.runs (
        run_type, agent, status, source,
        input_json, idempotency_key,
        started_at, metadata
    ) VALUES (
        v_sched.job_type, v_sched.agent, 'pending', 'supabase',
        v_sched.input_json, p_bucket_key,
        p_now, jsonb_build_object('schedule_id', p_schedule_id, 'schedule_name', v_sched.name)
    )
    RETURNING id INTO v_run_id;

    -- Update last_run tracking
    UPDATE ops.schedules
    SET last_run_at = p_now, last_run_id = v_run_id, updated_at = now()
    WHERE id = p_schedule_id;

    RETURN v_run_id;
END;
$$;

GRANT EXECUTE ON FUNCTION ops.enqueue_scheduled_run TO service_role;

-- Seed: default schedules
INSERT INTO ops.schedules (name, cron, job_type, agent, input_json, enabled)
VALUES
  ('ping-health', '*/5 * * * *',  'ping',      'ping-agent',       '{}',               true),
  ('odoo-sync',   '0 * * * *',    'sync_odoo', 'sync-odoo-agent',  '{"dry_run": true}', false)
ON CONFLICT (name) DO NOTHING;
