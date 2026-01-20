-- =====================================================
-- MCP Jobs Schema - Central Job Orchestration & Observability
-- =====================================================
-- Purpose: Shared jobs + observability backend for all MCP-enabled apps
-- Stack: Odoo, Supabase Edge Functions, Vercel apps, n8n workflows
-- =====================================================

-- Create schema
CREATE SCHEMA IF NOT EXISTS mcp_jobs;

-- =====================================================
-- Table: mcp_jobs.jobs
-- Purpose: Job queue with state machine tracking
-- =====================================================
CREATE TABLE IF NOT EXISTS mcp_jobs.jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,                    -- Source app (odoo, supabase, vercel, n8n, etc.)
    job_type TEXT NOT NULL,                  -- Job type (discovery, sync, report, etc.)
    status TEXT NOT NULL DEFAULT 'queued',   -- queued | running | completed | failed | cancelled
    payload JSONB NOT NULL DEFAULT '{}',     -- Job-specific data
    priority INTEGER NOT NULL DEFAULT 5,     -- Priority (1=highest, 10=lowest)

    -- Scheduling
    scheduled_at TIMESTAMPTZ,                -- When to run (NULL = run immediately)
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,

    -- Retries
    max_retries INTEGER NOT NULL DEFAULT 3,
    retry_count INTEGER NOT NULL DEFAULT 0,
    retry_delay_seconds INTEGER NOT NULL DEFAULT 60,

    -- Results
    result JSONB,                            -- Job result data
    error TEXT,                              -- Error message if failed
    error_stack TEXT,                        -- Full stack trace

    -- Metadata
    worker_id TEXT,                          -- Worker that processed the job
    metadata JSONB DEFAULT '{}',             -- Additional job metadata

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled')),
    CONSTRAINT valid_priority CHECK (priority >= 1 AND priority <= 10)
);

COMMENT ON TABLE mcp_jobs.jobs IS 'Central job queue for all MCP agent operations';
COMMENT ON COLUMN mcp_jobs.jobs.source IS 'Source application (odoo, supabase, vercel, n8n)';
COMMENT ON COLUMN mcp_jobs.jobs.job_type IS 'Job type identifier (discovery, sync, report, notification)';
COMMENT ON COLUMN mcp_jobs.jobs.status IS 'Current job state (queued → running → completed/failed)';
COMMENT ON COLUMN mcp_jobs.jobs.payload IS 'Job-specific input data';
COMMENT ON COLUMN mcp_jobs.jobs.priority IS 'Priority level (1=highest, 10=lowest)';

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_jobs_status ON mcp_jobs.jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_source ON mcp_jobs.jobs(source);
CREATE INDEX IF NOT EXISTS idx_jobs_job_type ON mcp_jobs.jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_jobs_scheduled_at ON mcp_jobs.jobs(scheduled_at) WHERE scheduled_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON mcp_jobs.jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_priority_created ON mcp_jobs.jobs(priority, created_at) WHERE status = 'queued';

-- =====================================================
-- Table: mcp_jobs.job_runs
-- Purpose: Detailed execution log for each job run
-- =====================================================
CREATE TABLE IF NOT EXISTS mcp_jobs.job_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES mcp_jobs.jobs(id) ON DELETE CASCADE,
    run_number INTEGER NOT NULL,             -- Attempt number (1, 2, 3, etc.)
    status TEXT NOT NULL,                    -- running | completed | failed

    -- Timing
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    duration_ms INTEGER,                     -- Execution time in milliseconds

    -- Results
    result JSONB,                            -- Run result data
    error TEXT,                              -- Error message if failed
    error_stack TEXT,                        -- Full stack trace

    -- Worker info
    worker_id TEXT,
    worker_metadata JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE mcp_jobs.job_runs IS 'Execution history for each job run/retry';
COMMENT ON COLUMN mcp_jobs.job_runs.run_number IS 'Attempt number (1=first attempt, 2+=retries)';
COMMENT ON COLUMN mcp_jobs.job_runs.duration_ms IS 'Execution time in milliseconds';

-- Indexes
CREATE INDEX IF NOT EXISTS idx_job_runs_job_id ON mcp_jobs.job_runs(job_id);
CREATE INDEX IF NOT EXISTS idx_job_runs_started_at ON mcp_jobs.job_runs(started_at DESC);

-- =====================================================
-- Table: mcp_jobs.job_events
-- Purpose: Detailed event log for job execution
-- =====================================================
CREATE TABLE IF NOT EXISTS mcp_jobs.job_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES mcp_jobs.jobs(id) ON DELETE CASCADE,
    run_id UUID REFERENCES mcp_jobs.job_runs(id) ON DELETE CASCADE,

    event_type TEXT NOT NULL,                -- started | progress | completed | failed | cancelled
    message TEXT,                            -- Human-readable message
    data JSONB DEFAULT '{}',                 -- Event-specific data

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE mcp_jobs.job_events IS 'Event log for job execution details';
COMMENT ON COLUMN mcp_jobs.job_events.event_type IS 'Event type (started, progress, completed, failed, cancelled)';

-- Indexes
CREATE INDEX IF NOT EXISTS idx_job_events_job_id ON mcp_jobs.job_events(job_id);
CREATE INDEX IF NOT EXISTS idx_job_events_run_id ON mcp_jobs.job_events(run_id);
CREATE INDEX IF NOT EXISTS idx_job_events_created_at ON mcp_jobs.job_events(created_at DESC);

-- =====================================================
-- Table: mcp_jobs.dead_letter_queue
-- Purpose: Failed jobs after max retries exhausted
-- =====================================================
CREATE TABLE IF NOT EXISTS mcp_jobs.dead_letter_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES mcp_jobs.jobs(id) ON DELETE CASCADE,

    -- Job snapshot at failure
    source TEXT NOT NULL,
    job_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    final_error TEXT,
    final_error_stack TEXT,

    -- Failure details
    total_attempts INTEGER NOT NULL,
    last_run_at TIMESTAMPTZ NOT NULL,

    -- Resolution
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    resolved_by TEXT,
    resolution_notes TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE mcp_jobs.dead_letter_queue IS 'Failed jobs after exhausting all retries';
COMMENT ON COLUMN mcp_jobs.dead_letter_queue.resolved IS 'Whether failure has been resolved';

-- Indexes
CREATE INDEX IF NOT EXISTS idx_dlq_resolved ON mcp_jobs.dead_letter_queue(resolved, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_dlq_source ON mcp_jobs.dead_letter_queue(source);

-- =====================================================
-- Table: mcp_jobs.metrics
-- Purpose: Aggregated job metrics for monitoring
-- =====================================================
CREATE TABLE IF NOT EXISTS mcp_jobs.metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Dimensions
    source TEXT NOT NULL,
    job_type TEXT NOT NULL,
    time_bucket TIMESTAMPTZ NOT NULL,        -- Hour bucket for aggregation

    -- Metrics
    total_jobs INTEGER NOT NULL DEFAULT 0,
    completed_jobs INTEGER NOT NULL DEFAULT 0,
    failed_jobs INTEGER NOT NULL DEFAULT 0,
    avg_duration_ms INTEGER,
    p95_duration_ms INTEGER,
    p99_duration_ms INTEGER,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE mcp_jobs.metrics IS 'Aggregated job metrics per hour';
COMMENT ON COLUMN mcp_jobs.metrics.time_bucket IS 'Hour bucket for metric aggregation';

-- Indexes
CREATE UNIQUE INDEX IF NOT EXISTS idx_metrics_unique ON mcp_jobs.metrics(source, job_type, time_bucket);
CREATE INDEX IF NOT EXISTS idx_metrics_time_bucket ON mcp_jobs.metrics(time_bucket DESC);

-- =====================================================
-- Function: update_updated_at_timestamp()
-- Purpose: Auto-update updated_at column
-- =====================================================
CREATE OR REPLACE FUNCTION mcp_jobs.update_updated_at_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger
CREATE TRIGGER update_jobs_timestamp
    BEFORE UPDATE ON mcp_jobs.jobs
    FOR EACH ROW
    EXECUTE FUNCTION mcp_jobs.update_updated_at_timestamp();

-- =====================================================
-- Function: enqueue_job()
-- Purpose: Add new job to queue
-- =====================================================
CREATE OR REPLACE FUNCTION mcp_jobs.enqueue_job(
    p_source TEXT,
    p_job_type TEXT,
    p_payload JSONB DEFAULT '{}',
    p_priority INTEGER DEFAULT 5,
    p_scheduled_at TIMESTAMPTZ DEFAULT NULL,
    p_max_retries INTEGER DEFAULT 3
)
RETURNS UUID AS $$
DECLARE
    v_job_id UUID;
BEGIN
    INSERT INTO mcp_jobs.jobs (
        source,
        job_type,
        payload,
        priority,
        scheduled_at,
        max_retries
    ) VALUES (
        p_source,
        p_job_type,
        p_payload,
        p_priority,
        p_scheduled_at,
        p_max_retries
    )
    RETURNING id INTO v_job_id;

    -- Log event
    INSERT INTO mcp_jobs.job_events (job_id, event_type, message)
    VALUES (v_job_id, 'queued', 'Job queued successfully');

    RETURN v_job_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION mcp_jobs.enqueue_job IS 'Add new job to queue with validation';

-- =====================================================
-- Function: claim_next_job()
-- Purpose: Worker claims next available job
-- =====================================================
CREATE OR REPLACE FUNCTION mcp_jobs.claim_next_job(
    p_worker_id TEXT,
    p_source_filter TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_job_id UUID;
BEGIN
    -- Find and claim next job atomically
    UPDATE mcp_jobs.jobs
    SET
        status = 'running',
        started_at = NOW(),
        worker_id = p_worker_id,
        retry_count = retry_count + 1
    WHERE id = (
        SELECT id
        FROM mcp_jobs.jobs
        WHERE
            status = 'queued'
            AND (scheduled_at IS NULL OR scheduled_at <= NOW())
            AND (p_source_filter IS NULL OR source = p_source_filter)
        ORDER BY priority ASC, created_at ASC
        LIMIT 1
        FOR UPDATE SKIP LOCKED
    )
    RETURNING id INTO v_job_id;

    -- Log event
    IF v_job_id IS NOT NULL THEN
        INSERT INTO mcp_jobs.job_events (job_id, event_type, message, data)
        VALUES (v_job_id, 'started', 'Job claimed by worker', jsonb_build_object('worker_id', p_worker_id));
    END IF;

    RETURN v_job_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION mcp_jobs.claim_next_job IS 'Worker claims next available job from queue';

-- =====================================================
-- Function: complete_job()
-- Purpose: Mark job as completed
-- =====================================================
CREATE OR REPLACE FUNCTION mcp_jobs.complete_job(
    p_job_id UUID,
    p_result JSONB DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    UPDATE mcp_jobs.jobs
    SET
        status = 'completed',
        finished_at = NOW(),
        result = p_result
    WHERE id = p_job_id;

    -- Log event
    INSERT INTO mcp_jobs.job_events (job_id, event_type, message)
    VALUES (p_job_id, 'completed', 'Job completed successfully');
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- Function: fail_job()
-- Purpose: Mark job as failed, move to DLQ if max retries reached
-- =====================================================
CREATE OR REPLACE FUNCTION mcp_jobs.fail_job(
    p_job_id UUID,
    p_error TEXT,
    p_error_stack TEXT DEFAULT NULL
)
RETURNS VOID AS $$
DECLARE
    v_job RECORD;
BEGIN
    -- Get job details
    SELECT * INTO v_job FROM mcp_jobs.jobs WHERE id = p_job_id;

    -- Check if max retries reached
    IF v_job.retry_count >= v_job.max_retries THEN
        -- Move to dead letter queue
        INSERT INTO mcp_jobs.dead_letter_queue (
            job_id, source, job_type, payload,
            final_error, final_error_stack,
            total_attempts, last_run_at
        ) VALUES (
            v_job.id, v_job.source, v_job.job_type, v_job.payload,
            p_error, p_error_stack,
            v_job.retry_count, NOW()
        );

        -- Mark as failed (terminal state)
        UPDATE mcp_jobs.jobs
        SET
            status = 'failed',
            finished_at = NOW(),
            error = p_error,
            error_stack = p_error_stack
        WHERE id = p_job_id;

        -- Log event
        INSERT INTO mcp_jobs.job_events (job_id, event_type, message)
        VALUES (p_job_id, 'failed', 'Job failed after max retries, moved to DLQ');
    ELSE
        -- Retry: back to queued
        UPDATE mcp_jobs.jobs
        SET
            status = 'queued',
            error = p_error,
            error_stack = p_error_stack,
            scheduled_at = NOW() + (v_job.retry_delay_seconds || ' seconds')::INTERVAL
        WHERE id = p_job_id;

        -- Log event
        INSERT INTO mcp_jobs.job_events (job_id, event_type, message, data)
        VALUES (p_job_id, 'failed', 'Job failed, will retry', jsonb_build_object(
            'retry_count', v_job.retry_count + 1,
            'max_retries', v_job.max_retries,
            'next_retry_at', NOW() + (v_job.retry_delay_seconds || ' seconds')::INTERVAL
        ));
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- RLS Policies (Security)
-- =====================================================
ALTER TABLE mcp_jobs.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE mcp_jobs.job_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE mcp_jobs.job_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE mcp_jobs.dead_letter_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE mcp_jobs.metrics ENABLE ROW LEVEL SECURITY;

-- Service role has full access
CREATE POLICY "Service role has full access to jobs"
    ON mcp_jobs.jobs FOR ALL TO service_role USING (true);

CREATE POLICY "Service role has full access to job_runs"
    ON mcp_jobs.job_runs FOR ALL TO service_role USING (true);

CREATE POLICY "Service role has full access to job_events"
    ON mcp_jobs.job_events FOR ALL TO service_role USING (true);

CREATE POLICY "Service role has full access to dead_letter_queue"
    ON mcp_jobs.dead_letter_queue FOR ALL TO service_role USING (true);

CREATE POLICY "Service role has full access to metrics"
    ON mcp_jobs.metrics FOR ALL TO service_role USING (true);

-- Authenticated users have read-only access
CREATE POLICY "Authenticated users can read jobs"
    ON mcp_jobs.jobs FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read job_runs"
    ON mcp_jobs.job_runs FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read job_events"
    ON mcp_jobs.job_events FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read dead_letter_queue"
    ON mcp_jobs.dead_letter_queue FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can read metrics"
    ON mcp_jobs.metrics FOR SELECT TO authenticated USING (true);

-- =====================================================
-- Verification Query
-- =====================================================
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'mcp_jobs'
ORDER BY tablename;
