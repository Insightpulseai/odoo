-- ============================================================================
-- Migration: ops.capabilities — platform capability registry
-- Contract:  N/A (internal control-plane)
-- SSOT:      supabase/migrations/20260301000060_ops_capabilities.sql
-- Author:    ops-console platform
-- Date:      2026-03-01
-- ============================================================================
--
-- Tables created:
--   ops.capabilities   — Canonical list of platform capabilities with maturity
--                        and surface routing metadata
--
-- Append-only rule (Rule 5, ssot-platform.md):
--   DROP TABLE / TRUNCATE are forbidden for ops.* tables.
--   Only ADD COLUMN IF NOT EXISTS is allowed after initial creation.
-- ============================================================================

CREATE TABLE IF NOT EXISTS ops.capabilities (
  id           BIGSERIAL PRIMARY KEY,
  key          TEXT NOT NULL UNIQUE,
  name         TEXT NOT NULL,
  category     TEXT NOT NULL CHECK (category IN ('supabase','vercel','digitalocean','custom')),
  maturity     TEXT NOT NULL DEFAULT 'scaffold' CHECK (maturity IN ('scaffold','beta','prod')),
  data_source  TEXT,          -- e.g. 'ops.do_databases', 'supabase_auth_sdk'
  baseline_allowed BOOLEAN NOT NULL DEFAULT true,
  surfaces     TEXT[] NOT NULL DEFAULT '{}',
  description  TEXT,
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Seed Supabase capabilities
INSERT INTO ops.capabilities (key, name, category, maturity, data_source, baseline_allowed, surfaces, description)
VALUES
  ('supabase_database', 'Database (PostgreSQL)', 'supabase', 'prod', 'ops.do_databases', true, ARRAY['/database','/overview'], 'Managed PostgreSQL via Supabase'),
  ('supabase_auth', 'Auth & RLS', 'supabase', 'prod', 'supabase_auth_sdk', true, ARRAY['/settings'], 'Supabase Auth with Row Level Security'),
  ('supabase_edge_functions', 'Edge Functions', 'supabase', 'beta', 'ops.run_events', true, ARRAY['/control-plane'], 'Deno-based serverless functions'),
  ('supabase_realtime', 'Realtime', 'supabase', 'scaffold', null, true, ARRAY['/logs'], 'PostgreSQL change streams'),
  ('supabase_storage', 'Storage', 'supabase', 'scaffold', null, false, ARRAY[], 'S3-compatible object storage'),
  ('supabase_vault', 'Vault', 'supabase', 'scaffold', 'ops.secret_sync_runs', true, ARRAY['/database'], 'Encrypted secrets store'),
  ('supabase_branches', 'Branches', 'supabase', 'scaffold', null, false, ARRAY[], 'Database branching for preview envs'),
  ('supabase_logs', 'Logs & Metrics', 'supabase', 'beta', 'ops.platform_events', true, ARRAY['/logs','/overview'], 'Platform event stream'),
  ('digitalocean_droplets', 'Droplets (Compute)', 'digitalocean', 'beta', 'ops.do_droplets', true, ARRAY['/overview','/environments','/platform/digitalocean'], 'DigitalOcean virtual machines'),
  ('digitalocean_databases', 'Managed Databases', 'digitalocean', 'beta', 'ops.do_databases', true, ARRAY['/overview','/environments','/platform/digitalocean'], 'DigitalOcean managed PostgreSQL clusters'),
  ('vercel_functions', 'Edge Functions (Vercel)', 'vercel', 'prod', null, true, ARRAY['/control-plane'], 'Next.js API routes + Edge Functions')
ON CONFLICT (key) DO UPDATE SET name=EXCLUDED.name, maturity=EXCLUDED.maturity, updated_at=now();

-- RLS
ALTER TABLE ops.capabilities ENABLE ROW LEVEL SECURITY;
CREATE POLICY "authenticated can read capabilities" ON ops.capabilities FOR SELECT TO authenticated USING (true);
CREATE POLICY "service_role full access capabilities" ON ops.capabilities FOR ALL TO service_role USING (true);
