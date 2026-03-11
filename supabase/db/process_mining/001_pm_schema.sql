-- Process Mining Schema for Odoo Copilot
-- Local-first event log storage and analytics
--
-- Usage:
--   psql -h $ODOO_DB_HOST -U $ODOO_DB_USER -d $ODOO_DB_NAME -f 001_pm_schema.sql

BEGIN;

CREATE SCHEMA IF NOT EXISTS pm;

COMMENT ON SCHEMA pm IS 'Process Mining schema for Odoo Copilot - local-first event logs and analytics';

-- Track ETL runs (incremental, idempotent)
CREATE TABLE IF NOT EXISTS pm.job_state (
  job_name        text PRIMARY KEY,
  last_run_ts     timestamptz NOT NULL DEFAULT '1970-01-01',
  updated_at      timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE pm.job_state IS 'Tracks last successful run of each ETL job for incremental processing';

-- Canonical process cases (one case per business document)
CREATE TABLE IF NOT EXISTS pm.case (
  case_id         text PRIMARY KEY,           -- e.g., 'p2p:po:<id>'
  process         text NOT NULL,              -- 'p2p', 'o2c', 'r2r', etc.
  source_model    text NOT NULL,              -- 'purchase.order', 'sale.order', etc.
  source_id       bigint NOT NULL,            -- FK to source document
  company_id      bigint NULL,
  start_ts        timestamptz NULL,
  end_ts          timestamptz NULL,
  duration_s      bigint NULL,
  variant_id      text NULL,
  attrs_json      jsonb NOT NULL DEFAULT '{}'::jsonb,
  updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pm_case_process_company ON pm.case(process, company_id);
CREATE INDEX IF NOT EXISTS idx_pm_case_updated_at ON pm.case(updated_at);
CREATE INDEX IF NOT EXISTS idx_pm_case_variant ON pm.case(variant_id) WHERE variant_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_pm_case_source ON pm.case(source_model, source_id);

COMMENT ON TABLE pm.case IS 'Process cases - one per business document (PO, SO, etc.)';

-- Event log (XES-like structure)
CREATE TABLE IF NOT EXISTS pm.event (
  event_id        bigserial PRIMARY KEY,
  case_id         text NOT NULL REFERENCES pm.case(case_id) ON DELETE CASCADE,
  process         text NOT NULL,
  activity        text NOT NULL,
  ts              timestamptz NOT NULL,
  resource        text NULL,                  -- user / partner / system
  source_model    text NULL,                  -- purchase.order, stock.picking, account.move, ...
  source_id       bigint NULL,
  attrs_json      jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_pm_event_case_ts ON pm.event(case_id, ts);
CREATE INDEX IF NOT EXISTS idx_pm_event_process_activity_ts ON pm.event(process, activity, ts);
CREATE INDEX IF NOT EXISTS idx_pm_event_ts ON pm.event(ts);

COMMENT ON TABLE pm.event IS 'Event log entries - activities with timestamps per case';

-- Variant catalog (unique activity sequences)
CREATE TABLE IF NOT EXISTS pm.variant (
  variant_id      text PRIMARY KEY,           -- md5(sequence)
  process         text NOT NULL,
  sequence        text[] NOT NULL,            -- ordered activity list
  sequence_hash   text NOT NULL,
  case_count      bigint NOT NULL DEFAULT 0,
  updated_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pm_variant_process_count ON pm.variant(process, case_count DESC);

COMMENT ON TABLE pm.variant IS 'Variant catalog - unique activity sequences with frequency';

-- DFG edges with latency stats (aggregated)
CREATE TABLE IF NOT EXISTS pm.edge (
  process         text NOT NULL,
  activity_from   text NOT NULL,
  activity_to     text NOT NULL,
  edge_count      bigint NOT NULL,
  p50_s           bigint NULL,                -- median latency in seconds
  p95_s           bigint NULL,                -- 95th percentile latency
  updated_at      timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(process, activity_from, activity_to)
);

CREATE INDEX IF NOT EXISTS idx_pm_edge_bottleneck ON pm.edge(process, p95_s DESC NULLS LAST);

COMMENT ON TABLE pm.edge IS 'Directly-follows graph edges with latency percentiles';

-- Deviations (rule-based conformance)
CREATE TABLE IF NOT EXISTS pm.deviation (
  deviation_id    bigserial PRIMARY KEY,
  process         text NOT NULL,
  case_id         text NOT NULL REFERENCES pm.case(case_id) ON DELETE CASCADE,
  rule_id         text NOT NULL,
  severity        text NOT NULL CHECK (severity IN ('low','medium','high')),
  details_json    jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pm_deviation_process_rule ON pm.deviation(process, rule_id);
CREATE INDEX IF NOT EXISTS idx_pm_deviation_case ON pm.deviation(case_id);
CREATE INDEX IF NOT EXISTS idx_pm_deviation_severity ON pm.deviation(process, severity, created_at DESC);

COMMENT ON TABLE pm.deviation IS 'Conformance deviations detected by rule engine';

-- Insights (generated recommendations)
CREATE TABLE IF NOT EXISTS pm.insight (
  insight_id      bigserial PRIMARY KEY,
  process         text NOT NULL,
  insight_type    text NOT NULL,              -- 'bottleneck', 'rework', 'compliance', 'optimization'
  summary         text NOT NULL,
  evidence_json   jsonb NOT NULL DEFAULT '{}'::jsonb,
  action_json     jsonb NULL,                 -- suggested actions
  created_at      timestamptz NOT NULL DEFAULT now(),
  expires_at      timestamptz NULL,           -- for time-sensitive insights
  acknowledged    boolean NOT NULL DEFAULT false
);

CREATE INDEX IF NOT EXISTS idx_pm_insight_process_type ON pm.insight(process, insight_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pm_insight_active ON pm.insight(process, acknowledged, created_at DESC) WHERE NOT acknowledged;

COMMENT ON TABLE pm.insight IS 'Generated insights and recommendations for Copilot';

-- Redaction configuration (for PII compliance)
CREATE TABLE IF NOT EXISTS pm.redaction_config (
  config_id       serial PRIMARY KEY,
  source_model    text NOT NULL,
  field_name      text NOT NULL,
  redaction_type  text NOT NULL CHECK (redaction_type IN ('mask', 'hash', 'remove')),
  enabled         boolean NOT NULL DEFAULT true,
  UNIQUE(source_model, field_name)
);

COMMENT ON TABLE pm.redaction_config IS 'Configuration for PII field redaction in event attributes';

-- Insert default job state entries
INSERT INTO pm.job_state(job_name) VALUES ('p2p_etl'), ('o2c_etl'), ('r2r_etl')
ON CONFLICT (job_name) DO NOTHING;

COMMIT;
