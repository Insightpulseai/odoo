-- 20260302000050_ops_webhook_events_github_cols.sql
-- Adds GitHub-specific columns to ops.webhook_events.
--
-- ops.webhook_events already exists (20260223000004_ops_integrations.sql) with:
--   integration, event_type, idempotency_key, signature_valid, received_at,
--   headers, payload, status, error
--
-- This migration adds:
--   delivery_id  — GitHub's X-GitHub-Delivery UUID (idempotency surface)
--   action       — event action (opened/closed/merged/…)
--   repo_full_name — "org/repo" string
--   installation_id — GitHub App installation ID
--   sender_login    — GitHub user who triggered the event
--   reason          — structured reason for unhandled/failed events
--
-- The existing (integration, idempotency_key) unique index already prevents
-- duplicate processing; delivery_id is stored as idempotency_key by the ingest
-- function. This adds a dedicated delivery_id column for direct querying.
--
-- Spec: spec/github-integrations/prd.md §FR-2, §FR-3
-- Runbook: docs/runbooks/GITHUB_APP_PROVISIONING.md

begin;

alter table ops.webhook_events
  add column if not exists delivery_id     text,
  add column if not exists action          text,
  add column if not exists repo_full_name  text,
  add column if not exists installation_id bigint,
  add column if not exists sender_login    text,
  add column if not exists reason          text;

-- Partial unique index on delivery_id for GitHub events
-- (delivery_id is only set for integration='github'; other integrations remain null)
create unique index if not exists webhook_events_github_delivery_id
  on ops.webhook_events (delivery_id)
  where delivery_id is not null;

comment on column ops.webhook_events.delivery_id      is 'GitHub X-GitHub-Delivery UUID; unique per event delivery';
comment on column ops.webhook_events.action           is 'Event sub-action (opened/closed/merged/completed/…)';
comment on column ops.webhook_events.repo_full_name   is 'Repository in "org/repo" format extracted from payload';
comment on column ops.webhook_events.installation_id  is 'GitHub App installation ID from webhook payload';
comment on column ops.webhook_events.sender_login     is 'GitHub login of the user who triggered the event';
comment on column ops.webhook_events.reason           is 'Structured reason for unhandled/failed status (unknown_event|missing_action|payload_too_large|schema_mismatch)';

commit;
