-- =============================================================================
-- Migration: Vault Secret Registry
-- File: 20260221000001_vault_secret_registry.sql
-- Purpose: Declare required integration secrets (names only — no values stored here).
--          Enables CI to assert "all required secrets are present" without
--          exposing actual secret values. Also provides a safe RPC for
--          runtime health checks.
-- =============================================================================
-- Idempotent: all statements use IF NOT EXISTS / OR REPLACE
-- Requires: integrations schema (created by earlier migration 202512201001)
--           pgsodium/vault extension (available on all Supabase projects)
-- =============================================================================

BEGIN;

-- =============================================================================
-- 1. integrations.secret_registry
--    Metadata table: records required secret names and ownership.
--    Does NOT store secret values — values live in vault.secrets (encrypted)
--    or in Edge Function Secrets (Deno runtime).
-- =============================================================================
CREATE TABLE IF NOT EXISTS integrations.secret_registry (
    secret_name    TEXT        PRIMARY KEY,          -- e.g. 'integrations.zoho.client_id'
    env_var_name   TEXT        NOT NULL,             -- e.g. 'ZOHO_CLIENT_ID' (Edge Secret name)
    storage_type   TEXT        NOT NULL              -- 'vault' | 'edge_secret' | 'container_env'
                   CHECK (storage_type IN ('vault', 'edge_secret', 'container_env')),
    owner_service  TEXT        NOT NULL,             -- e.g. 'zoho-mail-bridge'
    purpose        TEXT        NOT NULL,             -- human description
    rotation_days  INT         NOT NULL DEFAULT 365, -- expected rotation interval
    last_rotated   TIMESTAMPTZ,                      -- null = unknown/never rotated
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON TABLE integrations.secret_registry IS
  'Registry of required integration secrets. Stores names and metadata only — '
  'never values. Values live in vault.secrets or Edge Function Secrets.';

-- RLS: only service_role can read/write the registry
ALTER TABLE integrations.secret_registry ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_full" ON integrations.secret_registry;
CREATE POLICY "service_role_full"
    ON integrations.secret_registry
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- =============================================================================
-- 2. Seed: required secrets for the Zoho mail bridge
--    These are Edge Function Secrets (Deno.env.get()), not Vault keys.
--    The registry just declares "these must exist before the bridge works."
-- =============================================================================
INSERT INTO integrations.secret_registry
    (secret_name, env_var_name, storage_type, owner_service, purpose, rotation_days)
VALUES
    (
        'integrations.zoho.bridge_shared_secret',
        'BRIDGE_SHARED_SECRET',
        'edge_secret',
        'zoho-mail-bridge',
        'Shared secret for x-bridge-secret auth between Odoo and Edge Function',
        180
    ),
    (
        'integrations.zoho.client_id',
        'ZOHO_CLIENT_ID',
        'edge_secret',
        'zoho-mail-bridge',
        'Zoho OAuth2 client ID for token minting',
        365
    ),
    (
        'integrations.zoho.client_secret',
        'ZOHO_CLIENT_SECRET',
        'edge_secret',
        'zoho-mail-bridge',
        'Zoho OAuth2 client secret for token minting',
        180
    ),
    (
        'integrations.zoho.refresh_token',
        'ZOHO_REFRESH_TOKEN',
        'edge_secret',
        'zoho-mail-bridge',
        'Zoho OAuth2 refresh token (long-lived, manually generated)',
        365
    ),
    (
        'integrations.zoho.account_id',
        'ZOHO_ACCOUNT_ID',
        'edge_secret',
        'zoho-mail-bridge',
        'Zoho Mail account ID from /api/accounts response',
        365
    ),
    (
        'integrations.zoho.smtp_app_password',
        'ZOHO_SMTP_APP_PASSWORD',
        'edge_secret',
        'supabase-auth-smtp',
        'Zoho SMTP app password for Supabase Auth identity emails',
        180
    ),
    (
        'integrations.zoho.smtp_user',
        'ZOHO_SMTP_USER',
        'edge_secret',
        'supabase-auth-smtp',
        'Zoho SMTP sender address for Supabase Auth identity emails',
        365
    )
ON CONFLICT (secret_name) DO NOTHING;

-- =============================================================================
-- 3. integrations.check_required_secrets()
--    SECURITY DEFINER RPC that checks which required secrets are present
--    in vault.secrets (for vault-type secrets) or reports 'unverifiable'
--    for edge_secret / container_env types (we can't introspect those).
--
--    Returns: table of (secret_name, env_var_name, storage_type, status)
--    status = 'present' | 'missing' | 'unverifiable'
--    NEVER returns actual secret values.
-- =============================================================================
CREATE OR REPLACE FUNCTION integrations.check_required_secrets()
RETURNS TABLE (
    secret_name    TEXT,
    env_var_name   TEXT,
    storage_type   TEXT,
    status         TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = integrations, vault, public
AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.secret_name,
        r.env_var_name,
        r.storage_type,
        CASE
            WHEN r.storage_type = 'vault' THEN
                CASE WHEN EXISTS (
                    SELECT 1 FROM vault.secrets vs
                    WHERE vs.name = r.secret_name
                ) THEN 'present' ELSE 'missing' END
            ELSE
                -- Edge secrets and container env vars cannot be introspected
                -- from Postgres. Mark as unverifiable (use CLI to verify).
                'unverifiable'
        END AS status
    FROM integrations.secret_registry r
    ORDER BY r.storage_type, r.secret_name;
END;
$$;

COMMENT ON FUNCTION integrations.check_required_secrets() IS
  'Returns required secret names and their verification status. '
  'Never returns secret values. Edge/container secrets are unverifiable from SQL.';

-- Grant execute to service_role only
REVOKE ALL ON FUNCTION integrations.check_required_secrets() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION integrations.check_required_secrets() TO service_role;

COMMIT;
