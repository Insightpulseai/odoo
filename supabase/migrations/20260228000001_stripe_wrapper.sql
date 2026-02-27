-- =============================================================================
-- Migration: 20260228000001_stripe_wrapper.sql
-- Purpose:   Enable Supabase Stripe FDW (stripe_wrapper) infrastructure.
--            Foreign tables are imported after Vault secret is provisioned
--            out-of-band (see ssot/secrets/registry.yaml :: stripe_api_key).
-- SSOT:      ssot/runtime/prod_settings.yaml :: payments.stripe
-- Secrets:   ssot/secrets/registry.yaml :: stripe_api_key
-- Idempotent: yes (IF NOT EXISTS everywhere)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. Enable the wrappers extension (Supabase managed — idempotent)
-- ---------------------------------------------------------------------------
create extension if not exists wrappers with schema extensions;

-- ---------------------------------------------------------------------------
-- 2. Register the Stripe FDW handler
-- ---------------------------------------------------------------------------
create foreign data wrapper if not exists stripe_wrapper
  handler stripe_fdw_handler
  validator stripe_fdw_validator;

-- ---------------------------------------------------------------------------
-- 3. Dedicated schema for Stripe foreign tables
-- ---------------------------------------------------------------------------
create schema if not exists stripe;

-- ---------------------------------------------------------------------------
-- 4. FDW Server + foreign table import
--
-- IMPORTANT: The server creation below is commented out intentionally.
--   Reason:  Requires a Vault secret UUID (api_key_id) which is provisioned
--            out-of-band after this migration runs. Uncomment + fill in
--            <vault_secret_uuid> once the secret exists in Supabase Vault.
--
-- How to provision the Vault secret:
--   Option A (Supabase Dashboard): Database → Vault → New Secret
--                                   Name: stripe_api_key
--                                   Value: sk_test_... (or sk_live_... for prod)
--   Option B (SQL — after key is rotated to live):
--     select vault.create_secret(
--       'sk_live_YOURKEY',          -- value (live key only; never commit this)
--       'stripe_secret_key',        -- name  (matches ssot/secrets/registry.yaml)
--       'Stripe secret key for FDW (live mode)'  -- description
--     );
--   Then retrieve the UUID:
--     select id from vault.secrets where name = 'stripe_secret_key';
--
-- After provisioning, run the server creation + import below manually or
-- in a follow-up migration: supabase/migrations/YYYYMMDDHHMMSS_stripe_server.sql
-- ---------------------------------------------------------------------------

-- create server if not exists stripe_server
--   foreign data wrapper stripe_wrapper
--   options (
--     api_key_id  '<vault_secret_uuid>',      -- from vault.secrets.id
--     api_url     'https://api.stripe.com/v1/',
--     api_version '2024-06-20'                -- pin to a stable version
--   );

-- grant usage on foreign server stripe_server to postgres, service_role;

-- import foreign schema stripe
--   from server stripe_server
--   into stripe;
-- ---------------------------------------------------------------------------
-- Stripe foreign tables available after import (non-exhaustive):
--   stripe.customers, stripe.subscriptions, stripe.invoices,
--   stripe.payment_intents, stripe.charges, stripe.products, stripe.prices
-- ---------------------------------------------------------------------------

comment on schema stripe is
  'Stripe FDW foreign tables. Server creation deferred until Vault secret is provisioned. '
  'See: ssot/runtime/prod_settings.yaml payments.stripe and '
  'ssot/secrets/registry.yaml stripe_api_key.';
