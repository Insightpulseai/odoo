-- =============================================================================
-- Migration: ops.secret_inventory — observed state of secrets vs registry
-- Owner: platform / ops-secrets-scan Edge Function
-- SSOT: ssot/secrets/registry.yaml (v2 entries)
-- See: supabase/functions/ops-secrets-scan/index.ts
-- =============================================================================
-- Extends ops schema (must run after convergence_maintenance migration)
-- Append-only table design: status updates via UPDATE, never DROP/TRUNCATE.
-- =============================================================================

-- ops.secret_inventory — observed state of secrets vs registry desired state
CREATE TABLE IF NOT EXISTS ops.secret_inventory (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  key                 text NOT NULL UNIQUE,
  purpose             text,
  severity_if_missing text CHECK (severity_if_missing IN ('critical', 'high', 'medium', 'low')),
  desired_consumers   jsonb DEFAULT '[]'::jsonb,
  observed            jsonb DEFAULT '{}'::jsonb,
  -- status: ok | missing | stale | unknown
  status              text NOT NULL DEFAULT 'unknown'
                        CHECK (status IN ('ok', 'missing', 'stale', 'unknown')),
  probe_status_code   int,
  probe_error         text,
  last_checked_at     timestamptz,
  next_rotation_at    timestamptz,
  notes               text,
  created_at          timestamptz DEFAULT now(),
  updated_at          timestamptz DEFAULT now()
);

-- Row-level security: only service_role can read/write
ALTER TABLE ops.secret_inventory ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service role full access" ON ops.secret_inventory
  USING (auth.role() = 'service_role');

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS secret_inventory_status_idx
  ON ops.secret_inventory (status);

CREATE INDEX IF NOT EXISTS secret_inventory_key_idx
  ON ops.secret_inventory (key);

CREATE INDEX IF NOT EXISTS secret_inventory_severity_idx
  ON ops.secret_inventory (severity_if_missing);

-- Auto-update updated_at on row modification
CREATE OR REPLACE FUNCTION ops.set_secret_inventory_updated_at()
  RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS secret_inventory_updated_at ON ops.secret_inventory;
CREATE TRIGGER secret_inventory_updated_at
  BEFORE UPDATE ON ops.secret_inventory
  FOR EACH ROW EXECUTE FUNCTION ops.set_secret_inventory_updated_at();

-- Grant access
GRANT SELECT, INSERT, UPDATE ON ops.secret_inventory TO service_role;

-- =============================================================================
-- Seed: insert registry entries as 'unknown' status (initial scan populates them)
-- This ensures the table has rows even before the first scanner run.
-- =============================================================================

INSERT INTO ops.secret_inventory (key, purpose, severity_if_missing, desired_consumers, status)
VALUES
  (
    'supabase_access_token',
    'Supabase Management API PAT used by Supabase CLI and CI deploy workflows',
    'critical',
    '[{"kind":"github_secret","name":"SUPABASE_ACCESS_TOKEN"}]'::jsonb,
    'unknown'
  ),
  (
    'supabase_service_role_key',
    'Supabase project service role key — bypasses RLS for Edge Functions and ops-console API routes',
    'critical',
    '[{"kind":"github_secret","name":"SUPABASE_SERVICE_ROLE_KEY"},{"kind":"vercel_env","project":"odooops-console","name":"SUPABASE_SERVICE_ROLE_KEY"}]'::jsonb,
    'unknown'
  ),
  (
    'supabase_anon_key',
    'Supabase project anon key (public-safe) for ops-console public queries with RLS enforced',
    'high',
    '[{"kind":"vercel_env","project":"odooops-console","name":"NEXT_PUBLIC_SUPABASE_ANON_KEY"}]'::jsonb,
    'unknown'
  ),
  (
    'plane_webhook_secret',
    'Shared HMAC secret for verifying inbound Plane.so webhook payloads in ops-console',
    'high',
    '[{"kind":"supabase_vault","name":"plane_webhook_secret"},{"kind":"vercel_env","project":"odooops-console","name":"PLANE_WEBHOOK_SECRET"}]'::jsonb,
    'unknown'
  ),
  (
    'github_webhook_secret',
    'Shared HMAC-SHA256 secret for verifying inbound GitHub webhook payloads (X-Hub-Signature-256)',
    'high',
    '[{"kind":"supabase_vault","name":"github_webhook_secret"},{"kind":"vercel_env","project":"odooops-console","name":"GITHUB_WEBHOOK_SECRET"}]'::jsonb,
    'unknown'
  ),
  (
    'vercel_token',
    'Vercel API PAT used by CI workflows to trigger and manage Vercel deployments',
    'medium',
    '[{"kind":"github_secret","name":"VERCEL_TOKEN"}]'::jsonb,
    'unknown'
  ),
  (
    'cloudflare_api_token',
    'Cloudflare scoped API token for Terraform DNS apply via CI',
    'medium',
    '[{"kind":"github_secret","name":"CF_DNS_EDIT_TOKEN"}]'::jsonb,
    'unknown'
  ),
  (
    'digitalocean_access_token',
    'DigitalOcean API token for doctl, App Platform and Ops Advisor DO scan adapter',
    'high',
    '[{"kind":"github_secret","name":"DO_ACCESS_TOKEN"},{"kind":"supabase_vault","name":"digitalocean_api_token"}]'::jsonb,
    'unknown'
  ),
  (
    'mailgun_api_key',
    'Mailgun API key for webhook verification and optional management API queries',
    'low',
    '[{"kind":"supabase_vault","name":"mailgun_api_key"}]'::jsonb,
    'unknown'
  ),
  (
    'zoho_mail_smtp_password',
    'Zoho Mail SMTP app-specific password for Odoo outbound email',
    'medium',
    '[{"kind":"odoo_config","name":"ir.mail_server.smtp_pass"}]'::jsonb,
    'unknown'
  )
ON CONFLICT (key) DO NOTHING;
