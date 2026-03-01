-- Slack envelope ledger for idempotent event processing
-- Contract: C-20 (docs/contracts/SLACK_PULSER_CONTRACT.md)

CREATE TABLE IF NOT EXISTS ops.slack_envelopes (
    id BIGSERIAL PRIMARY KEY,
    envelope_id TEXT NOT NULL,
    team_id TEXT NOT NULL,
    event_type TEXT,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    received_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    processed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'pending',
    last_error TEXT,
    CONSTRAINT slack_envelopes_unique UNIQUE (team_id, envelope_id)
);

CREATE INDEX IF NOT EXISTS idx_slack_envelopes_status ON ops.slack_envelopes(status);
CREATE INDEX IF NOT EXISTS idx_slack_envelopes_received ON ops.slack_envelopes(received_at DESC);

ALTER TABLE ops.slack_envelopes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only_slack_envelopes"
    ON ops.slack_envelopes
    FOR ALL
    USING (auth.role() = 'service_role');

COMMENT ON TABLE ops.slack_envelopes IS 'Slack event envelope ledger (idempotent). Contract C-20.';
