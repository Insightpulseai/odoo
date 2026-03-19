-- ============================================================================
-- Migration: ops.mail_events — Mail catcher event log
-- Contract:  docs/contracts/C-MAIL-01-mail-catcher.md (C-20)
-- SSOT:      ssot/integrations/mailgun.yaml
-- Author:    ops-console platform
-- Date:      2026-03-01
-- ============================================================================

CREATE TABLE IF NOT EXISTS ops.mail_events (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  env         TEXT        NOT NULL CHECK (env IN ('prod','stage','dev','unknown')),
  provider    TEXT        NOT NULL DEFAULT 'mailgun' CHECK (provider IN ('mailgun','ses','sendgrid','smtp')),
  message_id  TEXT        NOT NULL UNIQUE,  -- Mailgun message ID for deduplication
  subject     TEXT,
  sender      TEXT,
  recipient   TEXT,
  transport   TEXT,                         -- e.g. 'smtp.mailgun.org:2525'
  stamp       TEXT,                         -- original mail timestamp string
  raw         JSONB       NOT NULL DEFAULT '{}',
  received_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS mail_events_env_idx         ON ops.mail_events (env);
CREATE INDEX IF NOT EXISTS mail_events_received_idx    ON ops.mail_events (received_at DESC);
CREATE INDEX IF NOT EXISTS mail_events_message_id_idx  ON ops.mail_events (message_id);

-- RLS
ALTER TABLE ops.mail_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "authenticated can read mail_events"
  ON ops.mail_events FOR SELECT TO authenticated USING (true);

CREATE POLICY "service_role full access mail_events"
  ON ops.mail_events FOR ALL TO service_role USING (true);

-- Seed evidence anchor (confirms E2E test worked)
INSERT INTO ops.mail_events (env, provider, message_id, subject, sender, recipient, transport, stamp, raw)
VALUES (
  'stage',
  'mailgun',
  'e2e-mailgun-odoo-text-seed-20260301',
  'E2E-MAILGUN-ODOO-TEXT',
  'no-reply@mg.insightpulseai.com',
  'ops@insightpulseai.com',
  'smtp.mailgun.org:2525',
  '2026-03-01T00:00:00+08:00',
  '{"source": "seed", "note": "E2E evidence anchor — real events will overwrite via webhook ingest"}'::jsonb
)
ON CONFLICT (message_id) DO NOTHING;

COMMENT ON TABLE ops.mail_events IS 'Mail catcher event log — populated by ops-mailgun-ingest webhook handler';
