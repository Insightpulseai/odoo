-- LIB Hybrid Brain - Event Pruning (365-day retention)
-- Purpose: Automated cleanup of old events via pg_cron

-- Create pg_cron extension if not exists
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Function to prune old events (365 days)
CREATE OR REPLACE FUNCTION lib_shared.prune_old_events()
RETURNS TABLE(deleted_count BIGINT) AS $$
DECLARE
    count BIGINT;
BEGIN
    DELETE FROM lib_shared.events
    WHERE created_at < NOW() - INTERVAL '365 days';

    GET DIAGNOSTICS count = ROW_COUNT;

    RETURN QUERY SELECT count;
END;
$$ LANGUAGE plpgsql;

-- Schedule weekly pruning job (Sundays at 3 AM UTC)
SELECT cron.schedule(
    'lib-events-cleanup',
    '0 3 * * 0',  -- Every Sunday at 3:00 AM
    $$SELECT lib_shared.prune_old_events();$$
);

-- Function to manually trigger pruning (for testing/admin)
CREATE OR REPLACE FUNCTION public.lib_shared_prune_events()
RETURNS TABLE(deleted_count BIGINT) AS $$
BEGIN
    RETURN QUERY SELECT * FROM lib_shared.prune_old_events();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION public.lib_shared_prune_events TO service_role;

-- View to check pruning job status
CREATE OR REPLACE VIEW lib_shared.pruning_job_status AS
SELECT
    jobid,
    schedule,
    command,
    nodename,
    nodeport,
    database,
    username,
    active
FROM cron.job
WHERE jobname = 'lib-events-cleanup';

-- Public wrapper for job status
CREATE OR REPLACE FUNCTION public.lib_shared_pruning_status()
RETURNS TABLE(
    job_id BIGINT,
    schedule TEXT,
    active BOOLEAN,
    last_run TIMESTAMPTZ,
    next_run TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        j.jobid,
        j.schedule,
        j.active,
        (SELECT MAX(end_time) FROM cron.job_run_details WHERE jobid = j.jobid) as last_run,
        cron.schedule_to_timestamp(j.schedule) as next_run
    FROM cron.job j
    WHERE j.jobname = 'lib-events-cleanup';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION public.lib_shared_pruning_status TO service_role;

-- Note: This creates a weekly job that automatically deletes events older than 365 days
-- The entities table (lib_shared.entities) is NOT affected by pruning
-- Manual pruning can be triggered via: SELECT public.lib_shared_prune_events();
