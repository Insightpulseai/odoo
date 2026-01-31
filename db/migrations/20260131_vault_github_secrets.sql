-- Migration: Vault GitHub Secrets RPC
-- Purpose: Secure RPC functions for retrieving GitHub App secrets from Vault
-- Date: 2026-01-31
--
-- This migration creates:
-- 1. ipai_security schema for security-related functions
-- 2. get_vault_secret() - single secret retrieval
-- 3. get_vault_secrets() - batch secret retrieval
-- 4. All functions are SECURITY DEFINER and restricted to service_role only

-- Create security schema if not exists
CREATE SCHEMA IF NOT EXISTS ipai_security;

-- Grant usage to service_role only
GRANT USAGE ON SCHEMA ipai_security TO service_role;
REVOKE USAGE ON SCHEMA ipai_security FROM anon, authenticated;

-- Function: Get single secret by name
-- Returns: decrypted secret value or NULL if not found
CREATE OR REPLACE FUNCTION ipai_security.get_vault_secret(secret_name TEXT)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = vault, pg_temp
AS $$
DECLARE
    secret_value TEXT;
BEGIN
    -- Only service_role can call this function
    IF current_setting('request.jwt.claims', TRUE)::json->>'role' != 'service_role' THEN
        RAISE EXCEPTION 'Access denied: service_role required';
    END IF;

    -- Get decrypted secret from vault
    SELECT decrypted_secret
    INTO secret_value
    FROM vault.decrypted_secrets
    WHERE name = secret_name
    LIMIT 1;

    RETURN secret_value;
END;
$$;

-- Function: Get multiple secrets by names
-- Returns: JSONB object with name -> value mapping
CREATE OR REPLACE FUNCTION ipai_security.get_vault_secrets(secret_names TEXT[])
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = vault, pg_temp
AS $$
DECLARE
    result JSONB := '{}';
    secret_record RECORD;
BEGIN
    -- Only service_role can call this function
    IF current_setting('request.jwt.claims', TRUE)::json->>'role' != 'service_role' THEN
        RAISE EXCEPTION 'Access denied: service_role required';
    END IF;

    -- Get all matching secrets
    FOR secret_record IN
        SELECT name, decrypted_secret
        FROM vault.decrypted_secrets
        WHERE name = ANY(secret_names)
    LOOP
        result := result || jsonb_build_object(secret_record.name, secret_record.decrypted_secret);
    END LOOP;

    RETURN result;
END;
$$;

-- Function: Check if secret exists (without revealing value)
CREATE OR REPLACE FUNCTION ipai_security.secret_exists(secret_name TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = vault, pg_temp
AS $$
BEGIN
    -- Only service_role can call this function
    IF current_setting('request.jwt.claims', TRUE)::json->>'role' != 'service_role' THEN
        RAISE EXCEPTION 'Access denied: service_role required';
    END IF;

    RETURN EXISTS (
        SELECT 1 FROM vault.secrets WHERE name = secret_name
    );
END;
$$;

-- Revoke all permissions from public
REVOKE ALL ON FUNCTION ipai_security.get_vault_secret(TEXT) FROM PUBLIC;
REVOKE ALL ON FUNCTION ipai_security.get_vault_secrets(TEXT[]) FROM PUBLIC;
REVOKE ALL ON FUNCTION ipai_security.secret_exists(TEXT) FROM PUBLIC;

-- Grant execute only to service_role
GRANT EXECUTE ON FUNCTION ipai_security.get_vault_secret(TEXT) TO service_role;
GRANT EXECUTE ON FUNCTION ipai_security.get_vault_secrets(TEXT[]) TO service_role;
GRANT EXECUTE ON FUNCTION ipai_security.secret_exists(TEXT) TO service_role;

-- Add comments
COMMENT ON FUNCTION ipai_security.get_vault_secret(TEXT) IS
    'Retrieve a single secret from Vault by name. Service role only.';
COMMENT ON FUNCTION ipai_security.get_vault_secrets(TEXT[]) IS
    'Retrieve multiple secrets from Vault by name array. Service role only.';
COMMENT ON FUNCTION ipai_security.secret_exists(TEXT) IS
    'Check if a secret exists in Vault without revealing value. Service role only.';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Vault GitHub Secrets RPC migration completed successfully';
END $$;
