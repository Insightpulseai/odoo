-- Integration Backbone: correlation_id, unified event view, routing table
-- Depends on: 20260122000100_integration_bus.sql, 20260125_000002_ops_run_system.sql
-- Safe: all ALTER TABLE ... ADD COLUMN IF NOT EXISTS, CREATE OR REPLACE

-- =============================================================================
-- 1. Add correlation_id to existing tables
-- =============================================================================

ALTER TABLE integration.outbox
  ADD COLUMN IF NOT EXISTS correlation_id uuid;

ALTER TABLE integration.event_log
  ADD COLUMN IF NOT EXISTS correlation_id uuid;

ALTER TABLE ops.runs
  ADD COLUMN IF NOT EXISTS correlation_id uuid;

ALTER TABLE ops.run_events
  ADD COLUMN IF NOT EXISTS correlation_id uuid;

-- Partial indexes (only non-null values) for correlation tracing
CREATE INDEX IF NOT EXISTS idx_outbox_correlation_id
  ON integration.outbox (correlation_id) WHERE correlation_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_event_log_correlation_id
  ON integration.event_log (correlation_id) WHERE correlation_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ops_runs_correlation_id
  ON ops.runs (correlation_id) WHERE correlation_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_ops_run_events_correlation_id
  ON ops.run_events (correlation_id) WHERE correlation_id IS NOT NULL;

-- =============================================================================
-- 2. Unified event view: ops.v_events
-- =============================================================================

CREATE OR REPLACE VIEW ops.v_events AS
  -- Integration bus events (Odoo business events)
  SELECT
    el.id,
    'integration'::text AS schema_source,
    el.source,
    el.event_type,
    el.aggregate_type AS entity_type,
    el.aggregate_id AS entity_ref,
    el.payload,
    el.correlation_id,
    el.created_at
  FROM integration.event_log el

  UNION ALL

  -- Ops run events (agent/workflow execution events)
  SELECT
    re.id,
    'ops'::text AS schema_source,
    COALESCE(r.actor, 'system') AS source,
    re.level || '.' || COALESCE(
      re.data->>'event_type',
      REPLACE(LEFT(re.message, 64), ' ', '_')
    ) AS event_type,
    'run'::text AS entity_type,
    re.run_id::text AS entity_ref,
    re.data AS payload,
    COALESCE(re.correlation_id, r.correlation_id) AS correlation_id,
    re.created_at
  FROM ops.run_events re
  LEFT JOIN ops.runs r ON r.id = re.run_id;

COMMENT ON VIEW ops.v_events IS 'Unified read-only view over integration.event_log + ops.run_events for correlation tracing';

-- =============================================================================
-- 3. Integration routing table
-- =============================================================================

CREATE TABLE IF NOT EXISTS ops.integration_routes (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type_pattern text NOT NULL,
  handler text NOT NULL,
  handler_url text,
  enabled boolean NOT NULL DEFAULT true,
  priority int NOT NULL DEFAULT 100,
  config jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (event_type_pattern, handler)
);

CREATE INDEX IF NOT EXISTS idx_integration_routes_enabled
  ON ops.integration_routes (enabled, priority) WHERE enabled = true;

-- RLS: service-role only
ALTER TABLE ops.integration_routes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all_integration_routes"
  ON ops.integration_routes FOR ALL TO service_role
  USING (true) WITH CHECK (true);

-- Updated_at trigger
DROP TRIGGER IF EXISTS trg_integration_routes_updated_at ON ops.integration_routes;
CREATE TRIGGER trg_integration_routes_updated_at
  BEFORE UPDATE ON ops.integration_routes
  FOR EACH ROW EXECUTE FUNCTION ops.set_updated_at();

-- Seed routing rules
INSERT INTO ops.integration_routes (event_type_pattern, handler, handler_url, priority)
VALUES
  ('expense.*',             'slack-notify',    NULL, 100),
  ('finance_task.*',        'slack-notify',    NULL, 100),
  ('*.approval_required',   'slack-approval',  NULL, 50),
  ('expense.submitted',     'slack-approval',  NULL, 50),
  ('deployment.*',          'slack-notify',    NULL, 100),
  ('deployment.failed',     'slack-notify',    NULL, 10)
ON CONFLICT (event_type_pattern, handler) DO NOTHING;

-- =============================================================================
-- 4. Route resolution function
-- =============================================================================

CREATE OR REPLACE FUNCTION ops.resolve_routes(p_event_type text)
RETURNS TABLE (
  handler text,
  handler_url text,
  priority int,
  config jsonb
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ops, pg_temp
AS $$
BEGIN
  RETURN QUERY
  SELECT
    r.handler,
    r.handler_url,
    r.priority,
    r.config
  FROM ops.integration_routes r
  WHERE r.enabled = true
    AND (
      -- Exact match
      r.event_type_pattern = p_event_type
      -- Wildcard prefix: 'expense.*' matches 'expense.submitted'
      OR (
        r.event_type_pattern LIKE '%.*'
        AND p_event_type LIKE REPLACE(r.event_type_pattern, '*', '%')
      )
      -- Wildcard suffix: '*.approval_required' matches 'expense.approval_required'
      OR (
        r.event_type_pattern LIKE '*%'
        AND p_event_type LIKE REPLACE(r.event_type_pattern, '*', '%')
      )
    )
  ORDER BY r.priority ASC, r.created_at ASC;
END;
$$;

COMMENT ON FUNCTION ops.resolve_routes IS 'Resolve routing handlers for a given event type using glob-style pattern matching';

-- =============================================================================
-- 5. Update existing RPCs to accept correlation_id
-- =============================================================================

-- Wrapper RPCs for PostgREST (insert_outbox_event with correlation_id)
CREATE OR REPLACE FUNCTION public.insert_outbox_event(
  p_source text,
  p_event_type text,
  p_aggregate_type text,
  p_aggregate_id text,
  p_payload jsonb,
  p_idempotency_key text,
  p_correlation_id uuid DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = integration, pg_temp
AS $$
DECLARE
  v_id uuid;
BEGIN
  INSERT INTO integration.outbox (
    source, event_type, aggregate_type, aggregate_id, payload, idempotency_key, correlation_id
  ) VALUES (
    p_source, p_event_type, p_aggregate_type, p_aggregate_id, p_payload, p_idempotency_key, p_correlation_id
  )
  ON CONFLICT (source, idempotency_key) DO NOTHING
  RETURNING id INTO v_id;

  RETURN v_id;
END;
$$;

-- Wrapper RPC for event log with correlation_id
CREATE OR REPLACE FUNCTION public.insert_event_log(
  p_source text,
  p_event_type text,
  p_aggregate_type text,
  p_aggregate_id text,
  p_payload jsonb,
  p_correlation_id uuid DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = integration, pg_temp
AS $$
DECLARE
  v_id uuid;
BEGIN
  INSERT INTO integration.event_log (
    source, event_type, aggregate_type, aggregate_id, payload, correlation_id
  ) VALUES (
    p_source, p_event_type, p_aggregate_type, p_aggregate_id, p_payload, p_correlation_id
  )
  RETURNING id INTO v_id;

  RETURN v_id;
END;
$$;
