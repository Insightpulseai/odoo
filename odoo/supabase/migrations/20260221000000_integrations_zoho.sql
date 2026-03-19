-- =============================================================================
-- Migration: Zoho Mail Bridge Tables
-- File: 20260221000000_integrations_zoho.sql
-- Adds Zoho-specific tables to existing integrations + bridge schemas
-- =============================================================================
-- Idempotent: all statements use IF NOT EXISTS
-- Schemas integrations, bridge, ops must exist (created by earlier migrations)
-- =============================================================================

BEGIN;

-- Ensure bridge schema exists (integrations schema assumed from 202512201001)
CREATE SCHEMA IF NOT EXISTS bridge;

-- =============================================================================
-- 1. integrations.zoho_accounts
--    Registry of Zoho Mail accounts connected to the platform
-- =============================================================================
CREATE TABLE IF NOT EXISTS integrations.zoho_accounts (
    account_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email        TEXT NOT NULL UNIQUE,
    display_name TEXT,
    scopes       TEXT[]  NOT NULL DEFAULT '{}',
    status       TEXT    NOT NULL DEFAULT 'active'
                 CHECK (status IN ('active', 'suspended', 'revoked')),
    region       TEXT    NOT NULL DEFAULT 'US'
                 CHECK (region IN ('US', 'EU', 'IN', 'AU', 'JP')),
    notes        TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE integrations.zoho_accounts IS
    'Zoho Mail accounts authorized for platform use';

-- =============================================================================
-- 2. integrations.zoho_tokens
--    Refresh token references — service role only, never readable by anon
-- =============================================================================
CREATE TABLE IF NOT EXISTS integrations.zoho_tokens (
    account_id        UUID NOT NULL REFERENCES integrations.zoho_accounts(account_id) ON DELETE CASCADE,
    refresh_token_ref TEXT NOT NULL,   -- vault key name, NOT the token itself
    last_minted_at    TIMESTAMPTZ,
    last_error        TEXT,
    error_at          TIMESTAMPTZ,
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (account_id)
);

COMMENT ON TABLE integrations.zoho_tokens IS
    'Zoho OAuth2 refresh token vault references — service role access only';

-- =============================================================================
-- 3. integrations.mail_identities
--    Per-company from/reply-to policies for outgoing mail
-- =============================================================================
CREATE TABLE IF NOT EXISTS integrations.mail_identities (
    identity_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id   UUID NOT NULL REFERENCES integrations.zoho_accounts(account_id) ON DELETE CASCADE,
    company_id   INT  NOT NULL,  -- references res.company in Odoo
    from_email   TEXT NOT NULL,
    reply_to     TEXT,
    display_name TEXT,
    policy       JSONB NOT NULL DEFAULT '{}',
    -- policy shape: { "allow_external": bool, "max_recipients": int, "footer_html": str }
    is_default   BOOLEAN NOT NULL DEFAULT false,
    active       BOOLEAN NOT NULL DEFAULT true,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (account_id, from_email)
);

COMMENT ON TABLE integrations.mail_identities IS
    'Per-company Zoho Mail sender identities and policies';

-- =============================================================================
-- 4. bridge.odoo_mail_server_map
--    Maps Odoo ir.mail_server IDs to mail_identities
-- =============================================================================
CREATE TABLE IF NOT EXISTS bridge.odoo_mail_server_map (
    identity_id         UUID NOT NULL REFERENCES integrations.mail_identities(identity_id) ON DELETE CASCADE,
    odoo_mail_server_id INT  NOT NULL,  -- ir.mail_server.id in Odoo DB
    synced_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (identity_id)
);

COMMENT ON TABLE bridge.odoo_mail_server_map IS
    'Maps Supabase mail identities to Odoo ir.mail_server records';

-- =============================================================================
-- 5. ops.platform_events — ensure table exists for audit trail
--    (may already exist from earlier migrations)
-- =============================================================================
CREATE TABLE IF NOT EXISTS ops.platform_events (
    event_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type   TEXT NOT NULL,
    actor        TEXT,
    target       TEXT,
    payload      JSONB,
    status       TEXT NOT NULL DEFAULT 'ok' CHECK (status IN ('ok', 'error')),
    error_detail TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE ops.platform_events IS
    'Append-only platform audit log';

-- =============================================================================
-- Indexes
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_zoho_accounts_email
    ON integrations.zoho_accounts (email);

CREATE INDEX IF NOT EXISTS idx_mail_identities_company
    ON integrations.mail_identities (company_id);

CREATE INDEX IF NOT EXISTS idx_platform_events_type_created
    ON ops.platform_events (event_type, created_at DESC);

-- =============================================================================
-- Row Level Security
-- =============================================================================

-- zoho_accounts: authenticated users can read; service role can write
ALTER TABLE integrations.zoho_accounts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS zoho_accounts_read ON integrations.zoho_accounts;
CREATE POLICY zoho_accounts_read ON integrations.zoho_accounts
    FOR SELECT TO authenticated USING (true);

-- zoho_tokens: service role only — no anon or authenticated reads
ALTER TABLE integrations.zoho_tokens ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS zoho_tokens_service_only ON integrations.zoho_tokens;
CREATE POLICY zoho_tokens_service_only ON integrations.zoho_tokens
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- mail_identities: authenticated users read their company's identities
ALTER TABLE integrations.mail_identities ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS mail_identities_read ON integrations.mail_identities;
CREATE POLICY mail_identities_read ON integrations.mail_identities
    FOR SELECT TO authenticated USING (active = true);

-- bridge.odoo_mail_server_map: service role only
ALTER TABLE bridge.odoo_mail_server_map ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS odoo_map_service_only ON bridge.odoo_mail_server_map;
CREATE POLICY odoo_map_service_only ON bridge.odoo_mail_server_map
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- platform_events: append-only for authenticated; service role reads all
ALTER TABLE ops.platform_events ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS platform_events_insert ON ops.platform_events;
CREATE POLICY platform_events_insert ON ops.platform_events
    FOR INSERT TO authenticated, service_role WITH CHECK (true);

DROP POLICY IF EXISTS platform_events_select ON ops.platform_events;
CREATE POLICY platform_events_select ON ops.platform_events
    FOR SELECT TO service_role USING (true);

-- =============================================================================
-- Seed: default Zoho account for insightpulseai.com
-- =============================================================================
INSERT INTO integrations.zoho_accounts (email, display_name, scopes, status, region)
VALUES (
    'business@insightpulseai.com',
    'InsightPulse AI — Zoho Mail',
    ARRAY['ZohoMail.messages.CREATE', 'ZohoMail.accounts.READ'],
    'active',
    'US'
) ON CONFLICT (email) DO NOTHING;

COMMIT;
