-- ============================================================================
-- Migration: supplemental indexes for ops.github_webhook_deliveries
--
-- The base table was created by 20260301000065_ops_workitems_webhooks.sql with:
--   delivery_id TEXT PRIMARY KEY (idempotency / dedupe)
-- This migration adds query-path indexes for the ingest function and the
-- ops console deliveries page.
--
-- Context: ops-github-webhook-ingest writes deliveries for ALL GitHub App
-- events (ipai-integrations). The ingest function issues:
--   - SELECT by delivery_id     → covered by PK
--   - UPDATE by delivery_id     → covered by PK
--   - SELECT by event_type      → new index below
--   - SELECT by received_at     → new index below
--   - Potential filter by status → new index below
--
-- Supersedes: 20260302000050_ops_webhook_events_github_cols.sql
--   That migration added columns to ops.webhook_events (the legacy table).
--   ops.github_webhook_deliveries is the canonical ledger going forward.
--   ops.webhook_events remains for historical data only.
--
-- SSOT:    ssot/integrations/github_apps.yaml §ledger.deliveries_table
-- Spec:    spec/github-integrations/prd.md §FR-2, §FR-3
-- Runbook: docs/runbooks/GITHUB_APP_PROVISIONING.md §Stored event shape
-- ============================================================================

-- Event-type lookup (ops console event filter, n8n routing queries)
CREATE INDEX IF NOT EXISTS idx_github_deliveries_event_type
  ON ops.github_webhook_deliveries (event_type);

-- Time-based pagination (ops console "last N deliveries" view)
CREATE INDEX IF NOT EXISTS idx_github_deliveries_received_at
  ON ops.github_webhook_deliveries (received_at DESC);

-- Status filter (retry queries: WHERE status = 'received' AND received_at < now() - interval '5m')
CREATE INDEX IF NOT EXISTS idx_github_deliveries_status
  ON ops.github_webhook_deliveries (status)
  WHERE status <> 'processed';   -- partial: exclude the common/terminal state

-- Composite for the most common admin query pattern
CREATE INDEX IF NOT EXISTS idx_github_deliveries_status_received
  ON ops.github_webhook_deliveries (status, received_at DESC);

COMMENT ON TABLE ops.github_webhook_deliveries IS
  'Durable ledger for GitHub App (ipai-integrations) webhook deliveries. '
  'dedupe by PK delivery_id (= X-GitHub-Delivery). '
  'Written by supabase/functions/ops-github-webhook-ingest. '
  'SSOT: ssot/integrations/github_apps.yaml §ledger.deliveries_table';
