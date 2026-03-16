-- =============================================================================
-- MCP Jobs Cron Trigger for Run Executor
-- =============================================================================
-- Purpose: Schedule pg_cron job to invoke run-executor Edge Function
-- Compatibility: Requires pg_cron and pg_net extensions
-- Author: Claude Code
-- Date: 2026-02-08
-- =============================================================================

-- Ensure required extensions are available
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS pg_net;

-- =============================================================================
-- CRON SECRET MANAGEMENT
-- =============================================================================
-- The X-CRON-SECRET must be set in Supabase Dashboard → Edge Functions → Secrets
-- OR via Supabase CLI: supabase secrets set CRON_SECRET=<your-secret>
--
-- DO NOT store the secret value in SQL. This migration only schedules the cron.
-- The Edge Function validates the header at runtime.
-- =============================================================================

-- =============================================================================
-- CRON JOB: Run Executor (every minute)
-- =============================================================================
-- Processes queued jobs and reaps stuck jobs

SELECT cron.unschedule('mcp-jobs-run-executor')
WHERE EXISTS (
    SELECT 1 FROM cron.job WHERE jobname = 'mcp-jobs-run-executor'
);

SELECT cron.schedule(
    'mcp-jobs-run-executor',
    '* * * * *',  -- Every minute
    $$
    SELECT net.http_post(
        url := (SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'SUPABASE_URL' LIMIT 1)
               || '/functions/v1/run-executor',
        headers := jsonb_build_object(
            'Content-Type', 'application/json',
            'X-CRON-SECRET', (SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'CRON_SECRET' LIMIT 1)
        ),
        body := jsonb_build_object(
            'max_jobs', 10,
            'timeout_minutes', 5
        )
    );
    $$
);

COMMENT ON EXTENSION pg_cron IS 'Schedules run-executor Edge Function every minute';

-- =============================================================================
-- CRON JOB: Stuck Job Reaper (every 5 minutes)
-- =============================================================================
-- Dedicated reaper for stuck jobs (backup to run-executor's built-in reaping)

SELECT cron.unschedule('mcp-jobs-reaper')
WHERE EXISTS (
    SELECT 1 FROM cron.job WHERE jobname = 'mcp-jobs-reaper'
);

SELECT cron.schedule(
    'mcp-jobs-reaper',
    '*/5 * * * *',  -- Every 5 minutes
    $$
    SELECT net.http_post(
        url := (SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'SUPABASE_URL' LIMIT 1)
               || '/functions/v1/run-executor/reap',
        headers := jsonb_build_object(
            'Content-Type', 'application/json',
            'X-CRON-SECRET', (SELECT decrypted_secret FROM vault.decrypted_secrets WHERE name = 'CRON_SECRET' LIMIT 1)
        ),
        body := '{}'::jsonb
    );
    $$
);

-- =============================================================================
-- ALTERNATIVE: Direct Database Reaper (no HTTP)
-- =============================================================================
-- If pg_net is not available or HTTP calls are problematic, use this instead:
--
-- SELECT cron.schedule(
--     'mcp-jobs-db-reaper',
--     '*/5 * * * *',
--     $$SELECT * FROM mcp_jobs.reap_stuck_jobs(5)$$
-- );
-- =============================================================================

-- =============================================================================
-- VERIFICATION QUERIES (run manually to confirm)
-- =============================================================================
-- Check scheduled jobs:
-- SELECT jobid, jobname, schedule, active FROM cron.job WHERE jobname LIKE 'mcp-jobs%';
--
-- Check recent cron runs:
-- SELECT * FROM cron.job_run_details WHERE jobid IN (
--     SELECT jobid FROM cron.job WHERE jobname LIKE 'mcp-jobs%'
-- ) ORDER BY start_time DESC LIMIT 10;
-- =============================================================================
