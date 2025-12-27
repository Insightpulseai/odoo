-- Migration: MCP Job Queue and Cron System
-- Description: Tables for async MCP operations and edge-function-based cron

-- ============================================================================
-- MCP JOB QUEUE
-- Handles async operations from MCP gateway
-- ============================================================================

CREATE TABLE IF NOT EXISTS mcp_job_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL UNIQUE,
    action TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')),
    priority TEXT NOT NULL DEFAULT 'normal' CHECK (priority IN ('high', 'normal', 'low')),
    client_id TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    result JSONB,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    next_retry_at TIMESTAMPTZ
);

CREATE INDEX idx_mcp_job_queue_status ON mcp_job_queue(status);
CREATE INDEX idx_mcp_job_queue_priority ON mcp_job_queue(priority, created_at);
CREATE INDEX idx_mcp_job_queue_client ON mcp_job_queue(client_id);
CREATE INDEX idx_mcp_job_queue_pending ON mcp_job_queue(status, priority, created_at) WHERE status = 'pending';

COMMENT ON TABLE mcp_job_queue IS 'Async job queue for MCP gateway operations';

-- ============================================================================
-- MCP REQUEST LOG
-- Audit trail for all MCP requests
-- ============================================================================

CREATE TABLE IF NOT EXISTS mcp_request_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL,
    action TEXT NOT NULL,
    client_id TEXT NOT NULL,
    duration_ms INTEGER,
    status TEXT NOT NULL CHECK (status IN ('success', 'error', 'timeout')),
    response_code INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mcp_request_log_client ON mcp_request_log(client_id, created_at DESC);
CREATE INDEX idx_mcp_request_log_action ON mcp_request_log(action, created_at DESC);
CREATE INDEX idx_mcp_request_log_status ON mcp_request_log(status, created_at DESC);

-- Partition by month for performance (optional, enable if high volume)
-- ALTER TABLE mcp_request_log SET (autovacuum_vacuum_scale_factor = 0.05);

COMMENT ON TABLE mcp_request_log IS 'Audit log for MCP gateway requests';

-- ============================================================================
-- API KEYS
-- For MCP gateway authentication
-- ============================================================================

CREATE TABLE IF NOT EXISTS api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id TEXT NOT NULL,
    key_hash TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    scopes TEXT[] NOT NULL DEFAULT ARRAY['mcp:read', 'mcp:execute'],
    active BOOLEAN NOT NULL DEFAULT TRUE,
    expires_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT
);

CREATE INDEX idx_api_keys_client ON api_keys(client_id);
CREATE INDEX idx_api_keys_hash ON api_keys(key_hash) WHERE active = TRUE;

COMMENT ON TABLE api_keys IS 'API keys for MCP gateway authentication';

-- ============================================================================
-- CRON JOBS
-- Edge-function managed cron jobs (replaces n8n scheduleTrigger)
-- ============================================================================

CREATE TABLE IF NOT EXISTS cron_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    schedule TEXT NOT NULL, -- Cron expression (e.g., "0 8 * * *")
    workflow_id TEXT NOT NULL, -- n8n webhook path
    payload JSONB NOT NULL DEFAULT '{}',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    timezone TEXT NOT NULL DEFAULT 'Asia/Manila',
    last_run TIMESTAMPTZ,
    last_status TEXT CHECK (last_status IN ('success', 'failed', 'skipped')),
    next_run TIMESTAMPTZ,
    retry_on_failure BOOLEAN NOT NULL DEFAULT TRUE,
    max_retries INTEGER NOT NULL DEFAULT 3,
    timeout_seconds INTEGER NOT NULL DEFAULT 300,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_cron_jobs_enabled ON cron_jobs(enabled);
CREATE INDEX idx_cron_jobs_next_run ON cron_jobs(next_run) WHERE enabled = TRUE;
CREATE INDEX idx_cron_jobs_tags ON cron_jobs USING GIN(tags);

COMMENT ON TABLE cron_jobs IS 'Cron job definitions for edge function scheduler';

-- ============================================================================
-- CRON EXECUTIONS
-- Execution history for cron jobs
-- ============================================================================

CREATE TABLE IF NOT EXISTS cron_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES cron_jobs(id) ON DELETE CASCADE,
    job_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('running', 'success', 'failed', 'timeout')),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    response_code INTEGER,
    error TEXT,
    output JSONB,
    attempt INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX idx_cron_executions_job ON cron_executions(job_id, started_at DESC);
CREATE INDEX idx_cron_executions_status ON cron_executions(status, started_at DESC);
CREATE INDEX idx_cron_executions_recent ON cron_executions(started_at DESC);

-- Auto-cleanup old executions (keep last 30 days)
CREATE INDEX idx_cron_executions_cleanup ON cron_executions(started_at)
    WHERE started_at < NOW() - INTERVAL '30 days';

COMMENT ON TABLE cron_executions IS 'Execution history for cron jobs';

-- ============================================================================
-- SYNC EVENTS (if not exists)
-- For realtime-sync edge function
-- ============================================================================

CREATE TABLE IF NOT EXISTS sync_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    channel TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    broadcast_targets TEXT[],
    status TEXT NOT NULL DEFAULT 'sent' CHECK (status IN ('sent', 'failed', 'pending')),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sync_events_channel ON sync_events(channel, timestamp DESC);
CREATE INDEX idx_sync_events_type ON sync_events(event_type, timestamp DESC);

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to claim pending jobs (for worker)
CREATE OR REPLACE FUNCTION claim_mcp_job(p_worker_id TEXT, p_actions TEXT[] DEFAULT NULL)
RETURNS TABLE(
    id UUID,
    request_id UUID,
    action TEXT,
    payload JSONB,
    client_id TEXT,
    attempts INTEGER
) AS $$
DECLARE
    v_job_id UUID;
BEGIN
    -- Find and lock the next pending job
    SELECT mcp_job_queue.id INTO v_job_id
    FROM mcp_job_queue
    WHERE status = 'pending'
      AND (p_actions IS NULL OR action = ANY(p_actions))
      AND (next_retry_at IS NULL OR next_retry_at <= NOW())
    ORDER BY
        CASE priority
            WHEN 'high' THEN 1
            WHEN 'normal' THEN 2
            WHEN 'low' THEN 3
        END,
        created_at
    LIMIT 1
    FOR UPDATE SKIP LOCKED;

    IF v_job_id IS NULL THEN
        RETURN;
    END IF;

    -- Update job status
    UPDATE mcp_job_queue
    SET status = 'processing',
        started_at = NOW(),
        attempts = attempts + 1
    WHERE mcp_job_queue.id = v_job_id;

    -- Return the claimed job
    RETURN QUERY
    SELECT
        mcp_job_queue.id,
        mcp_job_queue.request_id,
        mcp_job_queue.action,
        mcp_job_queue.payload,
        mcp_job_queue.client_id,
        mcp_job_queue.attempts
    FROM mcp_job_queue
    WHERE mcp_job_queue.id = v_job_id;
END;
$$ LANGUAGE plpgsql;

-- Function to complete a job
CREATE OR REPLACE FUNCTION complete_mcp_job(
    p_job_id UUID,
    p_success BOOLEAN,
    p_result JSONB DEFAULT NULL,
    p_error TEXT DEFAULT NULL
) RETURNS VOID AS $$
DECLARE
    v_job RECORD;
BEGIN
    SELECT * INTO v_job FROM mcp_job_queue WHERE id = p_job_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Job not found: %', p_job_id;
    END IF;

    IF p_success THEN
        UPDATE mcp_job_queue
        SET status = 'completed',
            completed_at = NOW(),
            result = p_result
        WHERE id = p_job_id;
    ELSE
        -- Check if we should retry
        IF v_job.attempts < v_job.max_attempts THEN
            UPDATE mcp_job_queue
            SET status = 'pending',
                error = p_error,
                next_retry_at = NOW() + (POWER(2, v_job.attempts) * INTERVAL '1 minute')
            WHERE id = p_job_id;
        ELSE
            UPDATE mcp_job_queue
            SET status = 'failed',
                completed_at = NOW(),
                error = p_error
            WHERE id = p_job_id;
        END IF;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to get job queue stats
CREATE OR REPLACE FUNCTION get_mcp_queue_stats()
RETURNS TABLE(
    status TEXT,
    count BIGINT,
    oldest TIMESTAMPTZ,
    avg_duration_ms NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        mcp_job_queue.status,
        COUNT(*)::BIGINT,
        MIN(mcp_job_queue.created_at),
        AVG(EXTRACT(EPOCH FROM (mcp_job_queue.completed_at - mcp_job_queue.started_at)) * 1000)::NUMERIC
    FROM mcp_job_queue
    WHERE created_at > NOW() - INTERVAL '24 hours'
    GROUP BY mcp_job_queue.status;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SEED DEFAULT CRON JOBS
-- Migrate existing n8n cron triggers
-- ============================================================================

INSERT INTO cron_jobs (name, description, schedule, workflow_id, payload, tags) VALUES
    ('bir-deadline-alerts', 'Check for upcoming BIR filing deadlines', '0 8 * * *', 'bir-deadline-alert', '{}', ARRAY['finance', 'bir', 'alerts']),
    ('ppm-daily-reminders', 'Send daily PPM close task reminders', '0 8 * * *', 'ppm-monthly-close', '{}', ARRAY['ppm', 'monthly-close']),
    ('health-check', 'System health check', '*/15 * * * *', 'system-health', '{}', ARRAY['monitoring', 'health']),
    ('sync-cleanup', 'Clean up old sync events', '0 2 * * *', 'sync-cleanup', '{"days_to_keep": 30}', ARRAY['maintenance'])
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- PG_CRON SETUP (run on Supabase dashboard or via supabase CLI)
-- ============================================================================
-- Note: Execute these in Supabase SQL Editor with pg_cron extension enabled

-- SELECT cron.schedule(
--     'mcp-cron-processor',
--     '* * * * *',  -- Every minute
--     $$SELECT net.http_post(
--         url := current_setting('app.supabase_url') || '/functions/v1/cron-processor',
--         headers := jsonb_build_object(
--             'Authorization', 'Bearer ' || current_setting('app.service_role_key'),
--             'Content-Type', 'application/json'
--         ),
--         body := '{}'::jsonb
--     );$$
-- );

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

ALTER TABLE mcp_job_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE mcp_request_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE cron_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE cron_executions ENABLE ROW LEVEL SECURITY;

-- Service role has full access (for edge functions)
CREATE POLICY "Service role full access" ON mcp_job_queue
    FOR ALL TO service_role USING (TRUE);

CREATE POLICY "Service role full access" ON mcp_request_log
    FOR ALL TO service_role USING (TRUE);

CREATE POLICY "Service role full access" ON api_keys
    FOR ALL TO service_role USING (TRUE);

CREATE POLICY "Service role full access" ON cron_jobs
    FOR ALL TO service_role USING (TRUE);

CREATE POLICY "Service role full access" ON cron_executions
    FOR ALL TO service_role USING (TRUE);

-- Authenticated users can view their own requests
CREATE POLICY "Users can view own requests" ON mcp_request_log
    FOR SELECT TO authenticated
    USING (client_id = auth.uid()::TEXT);

CREATE POLICY "Users can view own jobs" ON mcp_job_queue
    FOR SELECT TO authenticated
    USING (client_id = auth.uid()::TEXT);
