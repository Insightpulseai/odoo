-- =============================================================================
-- ops.taskbus_intents — Pulser intent queue (Slack + Odoo connector)
-- =============================================================================
-- Contract:  docs/contracts/C-PULSER-ODOO-01.md
-- Spec:      spec/odooops-console/prd.md (FR17 — Slack Interface)
--
-- Pulser slash commands and API calls enqueue intent rows here.
-- Odoo ipai_pulser_connector claims odoo.* intents via RPC.
-- Supabase Edge Functions handle non-Odoo intents.
-- =============================================================================

-- Table: durable intent queue for Pulser commands
CREATE TABLE IF NOT EXISTS ops.taskbus_intents (
  id                BIGSERIAL    PRIMARY KEY,
  run_id            UUID         NOT NULL DEFAULT gen_random_uuid() UNIQUE,
  request_id        TEXT         NOT NULL UNIQUE,  -- idempotency key (Slack trigger_id or UUID)
  intent_type       TEXT         NOT NULL,          -- e.g. 'status', 'odoo.healthcheck'
  args              JSONB        NOT NULL DEFAULT '{}'::jsonb,
  requested_by      TEXT         NOT NULL,          -- Slack user id or 'manual' or 'cron'
  channel_id        TEXT,                            -- Slack channel for reply
  response_url      TEXT,                            -- Slack response_url for deferred replies
  status            TEXT         NOT NULL DEFAULT 'queued' CHECK (status IN (
                                   'queued', 'claimed', 'running', 'done', 'failed'
                                 )),
  result            JSONB,                           -- Execution result payload (always JSON)
  error_message     TEXT,
  -- Claiming fields (atomic lease model for Odoo connector)
  claimed_by        TEXT,                            -- Instance ID of the claiming worker
  claim_token       UUID,                            -- Unique token for this claim (required to complete)
  claimed_at        TIMESTAMPTZ,
  claim_expires_at  TIMESTAMPTZ,                     -- Lease expiry; expired claims can be re-claimed
  completed_at      TIMESTAMPTZ,
  created_at        TIMESTAMPTZ  NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- Indexes for queue consumption
CREATE INDEX IF NOT EXISTS idx_taskbus_intents_status_created
  ON ops.taskbus_intents (status, created_at)
  WHERE status IN ('queued', 'claimed');

CREATE INDEX IF NOT EXISTS idx_taskbus_intents_claim_expires
  ON ops.taskbus_intents (claim_expires_at)
  WHERE claim_expires_at IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_taskbus_intents_run_id
  ON ops.taskbus_intents (run_id);

CREATE INDEX IF NOT EXISTS idx_taskbus_intents_requested_by
  ON ops.taskbus_intents (requested_by, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_taskbus_intents_intent_type
  ON ops.taskbus_intents (intent_type, status, created_at);

-- RLS: service_role full access; authenticated can read all intents
ALTER TABLE ops.taskbus_intents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role full access taskbus_intents"
  ON ops.taskbus_intents FOR ALL TO service_role USING (true);

CREATE POLICY "authenticated can read intents"
  ON ops.taskbus_intents FOR SELECT TO authenticated
  USING (true);

-- Comment
COMMENT ON TABLE ops.taskbus_intents IS
  'Durable intent queue for Pulser. Slack /pulser commands and manual inserts enqueue rows; Odoo connector and Edge Functions claim and execute.';

-- =============================================================================
-- RPC: ops.claim_taskbus_intent — atomic claim with FOR UPDATE SKIP LOCKED
-- =============================================================================
-- Odoo calls this RPC to claim exactly one queued intent per cron tick.
-- Lease model: claimed intents expire after p_lease_seconds; expired claims
-- can be re-claimed by any worker (prevents stuck intents).
-- =============================================================================

CREATE OR REPLACE FUNCTION ops.claim_taskbus_intent(
  p_intent_prefix TEXT,              -- e.g. 'odoo.' to claim only odoo.* intents
  p_claimed_by    TEXT,              -- e.g. 'odoo-prod-1' (instance identifier)
  p_lease_seconds INT DEFAULT 120   -- lease duration before expiry
)
RETURNS TABLE (
  intent_id   BIGINT,
  run_id      UUID,
  request_id  TEXT,
  intent_type TEXT,
  args        JSONB,
  response_url TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  v_now   TIMESTAMPTZ := now();
  v_lease TIMESTAMPTZ := v_now + make_interval(secs => p_lease_seconds);
  v_token UUID        := gen_random_uuid();
BEGIN
  RETURN QUERY
  WITH cte AS (
    SELECT t.id
    FROM ops.taskbus_intents t
    WHERE t.status = 'queued'
      AND t.intent_type LIKE (p_intent_prefix || '%')
      AND (t.claim_expires_at IS NULL OR t.claim_expires_at < v_now)
    ORDER BY t.created_at ASC
    LIMIT 1
    FOR UPDATE SKIP LOCKED
  )
  UPDATE ops.taskbus_intents t
  SET status           = 'running',
      claimed_by       = p_claimed_by,
      claim_token      = v_token,
      claimed_at       = v_now,
      claim_expires_at = v_lease,
      updated_at       = v_now
  FROM cte
  WHERE t.id = cte.id
  RETURNING t.id AS intent_id, t.run_id, t.request_id, t.intent_type, t.args, t.response_url;
END;
$$;

COMMENT ON FUNCTION ops.claim_taskbus_intent IS
  'Atomically claim one queued intent matching the given prefix. Uses FOR UPDATE SKIP LOCKED to prevent double-claims across concurrent workers.';
