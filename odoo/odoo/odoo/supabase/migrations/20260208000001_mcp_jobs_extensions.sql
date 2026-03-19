-- =============================================================================
-- MCP Jobs Schema Extensions for Ops Control Plane
-- =============================================================================
-- Purpose: Extend mcp_jobs schema with timeout handling for stuck job detection
-- Compatibility: Builds on existing 20260120_mcp_jobs_schema.sql
-- Idempotent: All statements use IF NOT EXISTS / CREATE OR REPLACE
-- Author: Claude Code
-- Date: 2026-02-08
-- Updated: 2026-02-08 - Fixed status 'running' -> 'processing' per table constraint
-- =============================================================================

-- Schema should already exist, but be safe
CREATE SCHEMA IF NOT EXISTS mcp_jobs;

-- =============================================================================
-- ADD timeout_at COLUMN (idempotent)
-- =============================================================================
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'mcp_jobs'
          AND table_name = 'jobs'
          AND column_name = 'timeout_at'
    ) THEN
        ALTER TABLE mcp_jobs.jobs
        ADD COLUMN timeout_at TIMESTAMPTZ;

        COMMENT ON COLUMN mcp_jobs.jobs.timeout_at IS
            'Deadline for job execution; exceeded = stuck, eligible for reaper';
    END IF;
END $$;

-- =============================================================================
-- INDEX for stuck-job detection (idempotent)
-- Note: Uses 'processing' status per jobs_status_check constraint
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_jobs_stuck_detection
ON mcp_jobs.jobs (status, timeout_at)
WHERE status = 'processing';

-- =============================================================================
-- SAFETY NET VIEW for monitoring stuck jobs
-- =============================================================================
CREATE OR REPLACE VIEW mcp_jobs.v_stuck_jobs AS
SELECT
    id, source, kind, status, priority, retries, max_retries,
    created_at, started_at, timeout_at,
    now() - coalesce(started_at, created_at) AS age
FROM mcp_jobs.jobs
WHERE status IN ('processing', 'queued')
  AND (
      (status = 'processing' AND timeout_at IS NOT NULL AND timeout_at < NOW())
      OR
      (status = 'queued' AND created_at < NOW() - INTERVAL '30 minutes')
  );

COMMENT ON VIEW mcp_jobs.v_stuck_jobs IS
    'Safety net view: jobs stuck in processing (past timeout) or queued too long (>30min)';

-- =============================================================================
-- STUCK JOB REAPER FUNCTION
-- =============================================================================
-- Reclaims jobs where status='processing' AND timeout_at < now()
-- Behavior: increment retries, set to 'queued' if retries left, else 'failed'

CREATE OR REPLACE FUNCTION mcp_jobs.reap_stuck_jobs(
    p_default_timeout_minutes INTEGER DEFAULT 5
)
RETURNS TABLE(
    job_id UUID,
    action_taken TEXT,
    retry_count INTEGER,
    max_retries INTEGER
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = mcp_jobs, pg_temp
AS $$
DECLARE
    stuck_job RECORD;
    action TEXT;
BEGIN
    -- Find and process stuck jobs (using 'processing' status per table constraint)
    FOR stuck_job IN
        SELECT j.id, j.retries, j.max_retries, j.payload
        FROM mcp_jobs.jobs j
        WHERE j.status = 'processing'
          AND (
              j.timeout_at IS NOT NULL AND j.timeout_at < NOW()
              OR (j.timeout_at IS NULL AND j.started_at < NOW() - (p_default_timeout_minutes || ' minutes')::interval)
          )
        FOR UPDATE SKIP LOCKED
    LOOP
        IF stuck_job.retries < stuck_job.max_retries THEN
            -- Can retry: increment counter, requeue
            UPDATE mcp_jobs.jobs
            SET status = 'queued',
                retries = stuck_job.retries + 1,
                timeout_at = NULL,
                started_at = NULL,
                error = 'Reaped: job timed out while processing',
                finished_at = NULL
            WHERE id = stuck_job.id;

            action := 'requeued';
        ELSE
            -- Max retries exhausted: mark failed
            UPDATE mcp_jobs.jobs
            SET status = 'failed',
                error = 'Reaped: max retries exhausted after timeout',
                finished_at = NOW()
            WHERE id = stuck_job.id;

            action := 'failed_to_dlq';

            -- Move to dead letter queue if it exists
            INSERT INTO mcp_jobs.dead_letter_queue (
                job_id, source, kind, payload,
                final_error, total_attempts, last_run_at
            )
            SELECT id, source, kind, payload,
                   'Reaped: max retries exhausted after timeout',
                   stuck_job.max_retries,
                   NOW()
            FROM mcp_jobs.jobs
            WHERE id = stuck_job.id
            ON CONFLICT (job_id) DO NOTHING;
        END IF;

        -- Return result row
        job_id := stuck_job.id;
        action_taken := action;
        retry_count := stuck_job.retries;
        max_retries := stuck_job.max_retries;
        RETURN NEXT;
    END LOOP;

    RETURN;
END;
$$;

COMMENT ON FUNCTION mcp_jobs.reap_stuck_jobs IS
    'Reclaims jobs stuck in processing state past their timeout_at or default timeout';

-- =============================================================================
-- ENHANCED CLAIM FUNCTION (sets timeout_at)
-- =============================================================================
-- Override existing claim_next_job to also set timeout_at

CREATE OR REPLACE FUNCTION mcp_jobs.claim_next_job(
    p_worker_id TEXT,
    p_source_filter TEXT DEFAULT NULL,
    p_timeout_minutes INTEGER DEFAULT 5
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = mcp_jobs, pg_temp
AS $$
DECLARE
    claimed_job_id UUID;
    current_retry INTEGER;
BEGIN
    -- Atomically claim next available job with FOR UPDATE SKIP LOCKED
    -- Uses 'processing' status per jobs_status_check constraint
    UPDATE mcp_jobs.jobs
    SET status = 'processing',
        started_at = NOW(),
        timeout_at = NOW() + (p_timeout_minutes || ' minutes')::interval
    WHERE id = (
        SELECT id FROM mcp_jobs.jobs
        WHERE status = 'queued'
          AND (p_source_filter IS NULL OR source = p_source_filter)
        ORDER BY priority ASC, created_at ASC
        FOR UPDATE SKIP LOCKED
        LIMIT 1
    )
    RETURNING id, retries INTO claimed_job_id, current_retry;

    RETURN claimed_job_id;
END;
$$;

-- =============================================================================
-- ENHANCED COMPLETE FUNCTION (clears timeout_at)
-- =============================================================================

CREATE OR REPLACE FUNCTION mcp_jobs.complete_job(
    p_job_id UUID,
    p_result JSONB DEFAULT '{}'::jsonb
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = mcp_jobs, pg_temp
AS $$
BEGIN
    -- Mark job completed
    UPDATE mcp_jobs.jobs
    SET status = 'completed',
        result = p_result,
        finished_at = NOW(),
        timeout_at = NULL
    WHERE id = p_job_id;
END;
$$;

-- =============================================================================
-- ENHANCED FAIL FUNCTION (handles retries + DLQ)
-- =============================================================================

CREATE OR REPLACE FUNCTION mcp_jobs.fail_job(
    p_job_id UUID,
    p_error TEXT,
    p_error_stack TEXT DEFAULT NULL
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = mcp_jobs, pg_temp
AS $$
DECLARE
    job_record RECORD;
BEGIN
    -- Get job details (using correct column names)
    SELECT id, retries, max_retries, payload, source, kind
    INTO job_record
    FROM mcp_jobs.jobs
    WHERE id = p_job_id;

    IF job_record IS NULL THEN
        RAISE EXCEPTION 'Job not found: %', p_job_id;
    END IF;

    IF job_record.retries < job_record.max_retries THEN
        -- Retry: requeue
        UPDATE mcp_jobs.jobs
        SET status = 'queued',
            retries = job_record.retries + 1,
            error = p_error,
            timeout_at = NULL,
            started_at = NULL
        WHERE id = p_job_id;
    ELSE
        -- Max retries exceeded: fail permanently + DLQ
        UPDATE mcp_jobs.jobs
        SET status = 'failed',
            error = p_error,
            finished_at = NOW(),
            timeout_at = NULL
        WHERE id = p_job_id;

        -- Move to dead letter queue
        INSERT INTO mcp_jobs.dead_letter_queue (
            job_id, source, kind, payload,
            final_error, total_attempts, last_run_at
        )
        VALUES (
            p_job_id, job_record.source, job_record.kind, job_record.payload,
            p_error, job_record.max_retries, NOW()
        )
        ON CONFLICT (job_id) DO UPDATE
        SET final_error = p_error,
            last_run_at = NOW();
    END IF;
END;
$$;

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

DO $$
BEGIN
    GRANT EXECUTE ON FUNCTION mcp_jobs.reap_stuck_jobs TO service_role;
    GRANT EXECUTE ON FUNCTION mcp_jobs.claim_next_job TO service_role;
    GRANT EXECUTE ON FUNCTION mcp_jobs.complete_job TO service_role;
    GRANT EXECUTE ON FUNCTION mcp_jobs.fail_job TO service_role;
EXCEPTION
    WHEN undefined_object THEN
        -- Role may not exist in some environments
        RAISE NOTICE 'service_role not found, skipping grants';
END $$;

-- =============================================================================
-- VERIFICATION QUERIES (run manually to confirm)
-- =============================================================================
-- SELECT column_name, data_type FROM information_schema.columns
-- WHERE table_schema = 'mcp_jobs' AND table_name = 'jobs' AND column_name = 'timeout_at';
--
-- SELECT * FROM mcp_jobs.reap_stuck_jobs();
-- SELECT * FROM mcp_jobs.v_stuck_jobs;
