-- =============================================================================
-- Migration: 20260228000001_stripe_wrapper.sql
-- Purpose:   Enable Supabase Stripe FDW (stripe_wrapper) infrastructure.
--            SAFE BY DEFAULT: extension + schema + FDW handler only.
--            CREATE SERVER + IMPORT FOREIGN SCHEMA remain commented until
--            the Vault secret is provisioned and the activation gate passes.
--
-- Activation requires ALL THREE:
--   1) Vault secret provisioned:  ssot/secrets/registry.yaml :: stripe_secret_key
--   2) Vault marker flipped:      ssot/runtime/vault_provisioning.yaml :: stripe_secret_key.provisioned = true
--   3) Manual uncomment:          CI gate script detects uncommented CREATE SERVER
--                                 and will fail unless conditions 1 + 2 are met
--
-- CI gate:   scripts/ci/check_stripe_wrapper_activation.py
-- SSOT:      ssot/runtime/prod_settings.yaml :: payments.stripe.supabase_wrapper
-- Secrets:   ssot/secrets/registry.yaml :: stripe_secret_key
-- Idempotent: yes (IF NOT EXISTS everywhere; DO block guards FDW creation)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. Enable the wrappers extension (Supabase managed — idempotent)
-- ---------------------------------------------------------------------------
create extension if not exists wrappers with schema extensions;

-- ---------------------------------------------------------------------------
-- 2. Register the Stripe FDW handler (safe to run repeatedly)
-- ---------------------------------------------------------------------------
do $$
begin
  if not exists (
    select 1 from pg_foreign_data_wrapper where fdwname = 'stripe_wrapper'
  ) then
    create foreign data wrapper stripe_wrapper
      handler stripe_fdw_handler
      validator stripe_fdw_validator;
  end if;
end $$;

-- ---------------------------------------------------------------------------
-- 3. Dedicated schema for Stripe foreign tables
-- ---------------------------------------------------------------------------
create schema if not exists stripe;

-- ---------------------------------------------------------------------------
-- 4. ACTIVATION BLOCK — KEEP COMMENTED UNTIL ALL THREE GATE CONDITIONS MET
--
-- How to provision the Vault secret (run once in Supabase SQL editor or via CLI):
--
--   select vault.create_secret(
--     'sk_live_YOURKEY',           -- value: live secret key from Stripe Dashboard
--     'stripe_secret_key',         -- name: must match ssot/secrets/registry.yaml id
--     'Stripe secret key for FDW (live mode, provisioned YYYYMMDD)'
--   );
--   -- vault.create_secret() returns the key_id (vault.secrets.key_id).
--   -- Record this value — it is what api_key_id expects below.
--
-- After provisioning, confirm the secret and capture the key_id:
--
--   select key_id, name from vault.secrets where name = 'stripe_secret_key';
--   -- key_id is the value for api_key_id below (NOT vault.secrets.id)
--   -- See: https://github.com/supabase/wrappers/issues/284
--
-- Then:
--   1. Flip ssot/runtime/vault_provisioning.yaml :: vault.stripe_secret_key.provisioned = true
--   2. Uncomment the block below, supplying EITHER api_key_id OR api_key_name (not both)
--   3. Open PR → CI gate verifies all conditions before merge
--
-- NOTE: api_key_id expects vault.secrets.key_id — NOT vault.secrets.id.
--       These are different columns. Using vault.secrets.id will fail at runtime.
--       Alternatively, use api_key_name with the secret's name string (see below).
-- ---------------------------------------------------------------------------

-- create server if not exists stripe_server
--   foreign data wrapper stripe_wrapper
--   options (
--     -- Use ONE of the following two options (not both):
--
--     -- Option A: api_key_id — use key_id returned by vault.create_secret()
--     --           (vault.secrets.key_id, NOT vault.secrets.id)
--     api_key_id   '<vault_key_id>',            -- replace with vault.secrets.key_id
--
--     -- Option B: api_key_name — use the Vault secret's name string (portable)
--     -- api_key_name 'stripe_secret_key',      -- must match name= in vault.create_secret()
--
--     api_url     'https://api.stripe.com/v1/', -- optional; shown explicitly for clarity
--     api_version '2024-06-20'                  -- optional; pin to stable; update with wrapper upgrades
--   );
--
-- grant usage on foreign server stripe_server to postgres, service_role;
--
-- import foreign schema stripe
--   from server stripe_server
--   into stripe;
-- ---------------------------------------------------------------------------
-- Stripe foreign tables available after activation (non-exhaustive):
--   stripe.customers, stripe.subscriptions, stripe.invoices,
--   stripe.payment_intents, stripe.charges, stripe.products, stripe.prices
-- ---------------------------------------------------------------------------

comment on schema stripe is
  'Stripe FDW foreign tables. Activation gated on Vault secret provisioning. '
  'See: ssot/runtime/prod_settings.yaml payments.stripe.supabase_wrapper and '
  'ssot/secrets/registry.yaml stripe_secret_key. '
  'CI gate: scripts/ci/check_stripe_wrapper_activation.py. '
  'Marker: ssot/runtime/vault_provisioning.yaml';
