-- =============================================================================
-- Migration: Cron Jobs SSOT
-- File: 20260221000002_cron_token_prewarm.sql
-- Purpose: Schedule pg_cron jobs for Edge Function invocations.
--          All jobs defined here are the SSOT for cron schedules.
--          Dashboard-only cron edits are treated as drift.
-- =============================================================================
-- Idempotent: uses cron.unschedule() before re-scheduling
-- Requires:
--   - pg_cron extension enabled (Supabase project settings → Database Extensions)
--   - pg_net extension enabled (same)
--   - Vault secrets set (see instructions below — values never in this file)
-- =============================================================================
-- BEFORE APPLYING THIS MIGRATION, set these Vault secrets via SQL:
--
--   SELECT vault.create_secret(
--     'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/zoho-mail-bridge',
--     'ops.cron.zoho_bridge_url',
--     'zoho-mail-bridge Edge Function URL for cron invocations'
--   );
--
--   SELECT vault.create_secret(
--     '<BRIDGE_SHARED_SECRET_value>',
--     'ops.cron.zoho_bridge_secret',
--     'x-bridge-secret for zoho-mail-bridge cron invocations'
--   );
--
-- The actual secret VALUES are set via the dashboard or Supabase CLI:
--   supabase secrets set --project-ref spdtwktxdalcfigzeqrz \
--     BRIDGE_SHARED_SECRET=<value>
-- =============================================================================

BEGIN;

-- Ensure required extensions exist (SSOT; no dashboard toggles required)
-- If the Supabase plan/project does not permit these extensions, migration
-- fails loudly here — treat as a provisioning constraint, not a manual step.
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS pg_net;

-- =============================================================================
-- Job 1: ops_zoho_token_prewarm
--
-- Every 45 minutes, call mint_token on zoho-mail-bridge to keep the
-- in-memory OAuth2 token cache warm. The bridge caches access tokens
-- for 1 hour (with 60s expiry buffer); pre-warming prevents cold-start
-- token mint latency on time-sensitive ERP document emails.
--
-- Cost: 1 HTTPS request every 45 min (~32 req/day) — well within free tier.
-- =============================================================================

-- Remove previous version if exists (idempotent)
SELECT cron.unschedule('ops_zoho_token_prewarm')
  WHERE EXISTS (
    SELECT 1 FROM cron.job WHERE jobname = 'ops_zoho_token_prewarm'
  );

SELECT cron.schedule(
  'ops_zoho_token_prewarm',    -- job name (must be prefixed ops_* or svc_*)
  '*/45 * * * *',              -- every 45 minutes
  $$
  SELECT net.http_post(
    url := (
      SELECT decrypted_secret
      FROM vault.decrypted_secrets
      WHERE name = 'ops.cron.zoho_bridge_url'
      LIMIT 1
    ) || '?action=mint_token',
    headers := jsonb_build_object(
      'Content-Type',    'application/json',
      'x-bridge-secret', (
        SELECT decrypted_secret
        FROM vault.decrypted_secrets
        WHERE name = 'ops.cron.zoho_bridge_secret'
        LIMIT 1
      ),
      'x-request-id',   gen_random_uuid()::text
    ),
    body := '{}'::jsonb,
    timeout_milliseconds := 20000
  ) AS request_id;
  $$
);

-- =============================================================================
-- Register jobs in ops.platform_events on schedule creation (audit trail)
-- =============================================================================
INSERT INTO ops.platform_events (
  event_type, actor, target, payload, status
) VALUES (
  'cron_job_created',
  'migration:20260221000002',
  'ops_zoho_token_prewarm',
  '{"schedule": "*/45 * * * *", "action": "mint_token"}'::jsonb,
  'ok'
);

COMMIT;

-- =============================================================================
-- Verification (run after apply):
--
-- Check job exists:
--   SELECT jobname, schedule, active FROM cron.job WHERE jobname LIKE 'ops_%';
--
-- Check last run:
--   SELECT jobname, start_time, status, return_message
--   FROM cron.job_run_details
--   WHERE jobname = 'ops_zoho_token_prewarm'
--   ORDER BY start_time DESC
--   LIMIT 5;
--
-- Check Vault secrets are set (names only — values not returned):
--   SELECT name FROM vault.secrets
--   WHERE name IN ('ops.cron.zoho_bridge_url', 'ops.cron.zoho_bridge_secret');
-- =============================================================================
