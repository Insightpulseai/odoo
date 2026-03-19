-- ops.run_events retention cleanup
-- Schedule daily purge of events older than 90 days via pg_cron.
-- The table is append-only (per SSOT rules) but unbounded growth
-- requires periodic cleanup of stale rows.

-- 1. Create the cleanup function
CREATE OR REPLACE FUNCTION ops.cleanup_old_events(retention_days integer DEFAULT 90)
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ops, public
AS $$
DECLARE
  deleted_count integer;
BEGIN
  DELETE FROM ops.run_events
  WHERE created_at < now() - (retention_days || ' days')::interval;
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RAISE LOG 'ops.cleanup_old_events: deleted % rows older than % days', deleted_count, retention_days;
  RETURN deleted_count;
END;
$$;

COMMENT ON FUNCTION ops.cleanup_old_events IS
  'Purge run_events older than retention_days (default 90). Scheduled via pg_cron.';

-- 2. Schedule daily at 03:00 UTC (idempotent, resilient if pg_cron unavailable)
-- pg_cron is enabled by default on Supabase Pro plans.
-- On free tier, invoke manually: SELECT ops.cleanup_old_events(90);
DO $$
BEGIN
  -- Attempt to enable pg_cron; ignore if restricted
  BEGIN
    CREATE EXTENSION IF NOT EXISTS pg_cron;
  EXCEPTION WHEN insufficient_privilege THEN
    NULL; -- extension management restricted on this instance
  END;

  -- Schedule only if pg_cron available and job not already registered
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN
    IF NOT EXISTS (SELECT 1 FROM cron.job WHERE jobname = 'ops_run_events_retention') THEN
      PERFORM cron.schedule(
        'ops_run_events_retention',
        '0 3 * * *',
        $$SELECT ops.cleanup_old_events(90)$$
      );
      RAISE LOG 'pg_cron job ops_run_events_retention scheduled at 03:00 UTC daily';
    ELSE
      RAISE LOG 'pg_cron job ops_run_events_retention already exists — skipping';
    END IF;
  ELSE
    RAISE WARNING 'pg_cron not available — ops.cleanup_old_events must be invoked manually';
  END IF;
END;
$$;
