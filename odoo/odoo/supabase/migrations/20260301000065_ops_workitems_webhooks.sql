-- ============================================================================
-- Migration: ops work items webhook delivery ledgers + work queue
-- Contract:  docs/contracts/C-PLANE-02-workitems-webhooks.md (C-21)
--            docs/contracts/C-GH-02-workitems-webhooks.md (C-22)
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS ops;

-- ops.work_items — canonical work item store (populated by processors)
CREATE TABLE IF NOT EXISTS ops.work_items (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  work_item_ref TEXT        NOT NULL UNIQUE, -- e.g. plane:iss_1001, github:Insightpulseai/odoo#421
  system       TEXT        NOT NULL CHECK (system IN ('plane','github','linear','jira')),
  external_id  TEXT        NOT NULL,
  project_ref  TEXT,
  title        TEXT        NOT NULL,
  status       TEXT        NOT NULL DEFAULT 'open',
  assignee     TEXT,
  url          TEXT,
  updated_at   TIMESTAMPTZ,
  ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS work_items_system_idx ON ops.work_items (system);
CREATE INDEX IF NOT EXISTS work_items_updated_idx ON ops.work_items (updated_at DESC);

-- Plane webhook delivery ledger
CREATE TABLE IF NOT EXISTS ops.plane_webhook_deliveries (
  delivery_id  TEXT        PRIMARY KEY,   -- X-Plane-Delivery header value
  event_type   TEXT        NOT NULL,      -- e.g. issue.created
  received_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  status       TEXT        NOT NULL DEFAULT 'received' CHECK (status IN ('received','processed','failed')),
  last_error   TEXT,
  payload      JSONB       NOT NULL
);

-- GitHub webhook delivery ledger
CREATE TABLE IF NOT EXISTS ops.github_webhook_deliveries (
  delivery_id  TEXT        PRIMARY KEY,   -- X-GitHub-Delivery header value
  event_type   TEXT        NOT NULL,      -- X-GitHub-Event header value
  received_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  status       TEXT        NOT NULL DEFAULT 'received' CHECK (status IN ('received','processed','failed')),
  last_error   TEXT,
  payload      JSONB       NOT NULL
);

-- Work queue (durable async processor queue)
CREATE TABLE IF NOT EXISTS ops.work_queue (
  id           BIGSERIAL   PRIMARY KEY,
  source       TEXT        NOT NULL CHECK (source IN ('plane','github')),
  delivery_id  TEXT        NOT NULL,
  status       TEXT        NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','claimed','done','failed')),
  attempts     INT         NOT NULL DEFAULT 0,
  available_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  claimed_at   TIMESTAMPTZ,
  last_error   TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_work_queue_status_available ON ops.work_queue (status, available_at);

-- RLS
ALTER TABLE ops.work_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.plane_webhook_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.github_webhook_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.work_queue ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated can read work_items"
  ON ops.work_items FOR SELECT TO authenticated USING (true);
CREATE POLICY "service_role full access work_items"
  ON ops.work_items FOR ALL TO service_role USING (true);

CREATE POLICY "service_role full access plane_deliveries"
  ON ops.plane_webhook_deliveries FOR ALL TO service_role USING (true);
CREATE POLICY "service_role full access github_deliveries"
  ON ops.github_webhook_deliveries FOR ALL TO service_role USING (true);
CREATE POLICY "service_role full access work_queue"
  ON ops.work_queue FOR ALL TO service_role USING (true);

COMMENT ON TABLE ops.work_items IS 'Canonical work items populated by Plane + GitHub webhook processors';
COMMENT ON TABLE ops.plane_webhook_deliveries IS 'Durable ledger for Plane webhook deliveries — dedupe by PK delivery_id';
COMMENT ON TABLE ops.github_webhook_deliveries IS 'Durable ledger for GitHub webhook deliveries — dedupe by PK delivery_id';
COMMENT ON TABLE ops.work_queue IS 'Async processing queue for webhook-triggered work item ingestion';
