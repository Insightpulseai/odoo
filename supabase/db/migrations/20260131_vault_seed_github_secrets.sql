-- Migration: Seed GitHub App Secrets in Vault
-- Purpose: Store GitHub App (pulser-hub) secrets in Supabase Vault
-- Date: 2026-01-31
--
-- IMPORTANT: Replace placeholder values before running in production
-- This migration is idempotent - safe to run multiple times
--
-- Secret values should be substituted via:
-- 1. CI/CD pipeline (sed replacement)
-- 2. Manual substitution before running
-- 3. Supabase CLI with environment variables

-- Delete existing secrets (idempotent)
DELETE FROM vault.secrets WHERE name IN (
    'GITHUB_APP_ID',
    'GITHUB_CLIENT_ID',
    'GITHUB_CLIENT_SECRET',
    'GITHUB_WEBHOOK_SECRET',
    'GITHUB_APP_PRIVATE_KEY_B64',
    'MCP_COORDINATOR_PUBLIC_URL'
);

-- Insert GitHub App secrets
-- Note: vault.create_secret() encrypts the value automatically

-- GitHub App ID (from pulser-hub settings)
SELECT vault.create_secret(
    'GITHUB_APP_ID',
    '2191216',  -- App ID: 2191216
    'GitHub App ID for pulser-hub'
);

-- GitHub OAuth Client ID
SELECT vault.create_secret(
    'GITHUB_CLIENT_ID',
    'Iv23liwGL7fnYySPPAjS',  -- Client ID from GitHub App settings
    'GitHub OAuth Client ID for pulser-hub'
);

-- GitHub OAuth Client Secret
-- PLACEHOLDER: Replace with actual secret from GitHub App settings
SELECT vault.create_secret(
    'GITHUB_CLIENT_SECRET',
    '__GITHUB_CLIENT_SECRET_PLACEHOLDER__',
    'GitHub OAuth Client Secret for pulser-hub - REPLACE BEFORE PRODUCTION'
);

-- GitHub Webhook Secret
-- PLACEHOLDER: Replace with actual secret from GitHub App webhook settings
SELECT vault.create_secret(
    'GITHUB_WEBHOOK_SECRET',
    '__GITHUB_WEBHOOK_SECRET_PLACEHOLDER__',
    'GitHub Webhook signing secret for pulser-hub - REPLACE BEFORE PRODUCTION'
);

-- GitHub App Private Key (Base64 encoded)
-- PLACEHOLDER: Replace with: base64 -w 0 pulser-hub.private-key.pem
SELECT vault.create_secret(
    'GITHUB_APP_PRIVATE_KEY_B64',
    '__GITHUB_APP_PRIVATE_KEY_B64_PLACEHOLDER__',
    'Base64 encoded GitHub App private key (PEM) - REPLACE BEFORE PRODUCTION'
);

-- MCP Coordinator Public URL (for OAuth callbacks)
SELECT vault.create_secret(
    'MCP_COORDINATOR_PUBLIC_URL',
    'http://178.128.112.214:8766',
    'Public URL for MCP Coordinator (used in OAuth callbacks)'
);

-- Verification: List all GitHub-related secrets (names only, not values)
DO $$
DECLARE
    secret_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO secret_count
    FROM vault.secrets
    WHERE name LIKE 'GITHUB_%' OR name = 'MCP_COORDINATOR_PUBLIC_URL';

    RAISE NOTICE 'Seeded % GitHub-related secrets in Vault', secret_count;

    -- Check for placeholders that need replacement
    IF EXISTS (
        SELECT 1 FROM vault.decrypted_secrets
        WHERE decrypted_secret LIKE '%PLACEHOLDER%'
    ) THEN
        RAISE WARNING 'PLACEHOLDER values detected - replace before production deployment';
    END IF;
END $$;
