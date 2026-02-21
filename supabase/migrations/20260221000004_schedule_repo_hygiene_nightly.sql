-- =============================================================================
-- Migration: Schedule nightly repo hygiene cron job
-- File: 20260221000004_schedule_repo_hygiene_nightly.sql
-- Purpose: Register ops_repo_hygiene_nightly in pg_cron.
--          Runs at 17:10 UTC = 01:10 Asia/Manila daily.
-- =============================================================================
-- Idempotent: unschedule before re-schedule
-- Requires:
--   - pg_cron extension enabled
--   - pg_net extension enabled
--   - Vault secrets: ops.cron.repo_hygiene_url, ops.cron.repo_hygiene_secret
--   - ops.repo_hygiene_runs table (migration 20260221000003)
-- =============================================================================
-- BEFORE APPLYING THIS MIGRATION, set these Vault secrets via SQL:
--
--   SELECT vault.create_secret(
--     'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/repo-hygiene-runner',
--     'ops.cron.repo_hygiene_url',
--     'repo-hygiene-runner Edge Function URL for cron invocations'
--   );
--
--   SELECT vault.create_secret(
--     '<REPO_HYGIENE_SECRET_value>',
--     'ops.cron.repo_hygiene_secret',
--     'x-bridge-secret for repo-hygiene-runner cron invocations'
--   );
--
-- The actual secret VALUE for REPO_HYGIENE_SECRET must also be set as
-- an Edge Function secret via Supabase CLI:
--   supabase secrets set --project-ref spdtwktxdalcfigzeqrz \
--     REPO_HYGIENE_SECRET=<value>
-- =============================================================================

BEGIN;

-- Ensure required extensions exist (SSOT; no dashboard toggles required)
-- If the Supabase plan/project does not permit these extensions, migration
-- fails loudly here — treat as a provisioning constraint, not a manual step.
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS pg_net;

-- =============================================================================
-- Job: ops_repo_hygiene_nightly
--
-- Schedule: 10 17 * * * UTC  →  01:10 Asia/Manila daily
--
-- Calls repo-hygiene-runner?action=run_nightly on every execution.
-- URL and secret read from Vault at runtime — never hardcoded here.
-- Timeout: 25s (< Edge Function wall-clock limit for free tier).
-- =============================================================================

-- Idempotent unschedule
SELECT cron.unschedule('ops_repo_hygiene_nightly')
  WHERE EXISTS (
    SELECT 1 FROM cron.job WHERE jobname = 'ops_repo_hygiene_nightly'
  );

SELECT cron.schedule(
  'ops_repo_hygiene_nightly',   -- job name (ops_* prefix convention)
  '10 17 * * *',                -- 17:10 UTC = 01:10 Asia/Manila daily
  $$
  SELECT net.http_post(
    url := (
      SELECT decrypted_secret
      FROM vault.decrypted_secrets
      WHERE name = 'ops.cron.repo_hygiene_url'
      LIMIT 1
    ) || '?action=run_nightly',
    headers := jsonb_build_object(
      'Content-Type',    'application/json',
      'x-bridge-secret', (
        SELECT decrypted_secret
        FROM vault.decrypted_secrets
        WHERE name = 'ops.cron.repo_hygiene_secret'
        LIMIT 1
      ),
      'x-request-id',   gen_random_uuid()::text
    ),
    body := '{}'::jsonb,
    timeout_milliseconds := 25000
  ) AS request_id;
  $$
);

-- =============================================================================
-- Audit event on job creation
-- =============================================================================
INSERT INTO ops.platform_events (
  event_type, actor, target, payload, status
) VALUES (
  'cron_job_created',
  'migration:20260221000004',
  'ops_repo_hygiene_nightly',
  '{
    "schedule_utc": "10 17 * * *",
    "schedule_manila": "01:10 Asia/Manila",
    "action": "run_nightly",
    "edge_function": "repo-hygiene-runner"
  }'::jsonb,
  'ok'
);

COMMIT;

-- =============================================================================
-- Verification (run after apply):
--
-- Check job is scheduled:
--   SELECT jobname, schedule, active FROM cron.job
--     WHERE jobname = 'ops_repo_hygiene_nightly';
--
-- Check last runs (will be empty until first execution):
--   SELECT jobname, start_time, end_time, status, return_message
--     FROM cron.job_run_details
--     WHERE jobname = 'ops_repo_hygiene_nightly'
--     ORDER BY start_time DESC LIMIT 5;
--
-- Check Vault secrets are set:
--   SELECT name FROM vault.secrets
--     WHERE name IN (
--       'ops.cron.repo_hygiene_url',
--       'ops.cron.repo_hygiene_secret'
--     );
-- =============================================================================
