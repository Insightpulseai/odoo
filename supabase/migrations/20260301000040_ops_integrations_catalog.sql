-- =============================================================================
-- 20260301000040_ops_integrations_catalog.sql
-- =============================================================================
-- Catalog-driven integrations registry for ops-console /integrations page.
--
-- Two tables:
--   ops.integrations_catalog     — what *could* exist (open-ended, seeded)
--   ops.integrations_installations — what IS connected + live status
--
-- Supports:
--   • PlanGuard filtering (baseline_allowed, plan_tier, cost_band)
--   • Vercel marketplace ingest → upsert installations
--   • "active/total" counts computed from installations JOIN catalog
--   • Category grouping, surface deep-links, capability tagging
--
-- Idempotent: safe to re-apply.
-- =============================================================================

-- ─── Schema guard ─────────────────────────────────────────────────────────────
CREATE SCHEMA IF NOT EXISTS ops;

-- ─── ops.integrations_catalog ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ops.integrations_catalog (
  key              TEXT PRIMARY KEY,
  name             TEXT NOT NULL,
  -- Display category (maps to UI section headings)
  category         TEXT NOT NULL CHECK (category IN (
    'auth_data','ai_inference','agents','devtools','messaging',
    'observability','storage','security','analytics','workflow'
  )),
  -- Where the integration is sourced from
  provider         TEXT NOT NULL CHECK (provider IN (
    'vercel_marketplace','supabase_native','direct','custom_bridge'
  )),
  description      TEXT,

  -- ── PlanGuard fields ──────────────────────────────────────────────────────
  baseline_allowed BOOLEAN NOT NULL DEFAULT true,
  plan_tier        TEXT NOT NULL DEFAULT 'baseline' CHECK (plan_tier IN (
    'baseline','optional','enterprise_only'
  )),
  cost_band        TEXT NOT NULL DEFAULT 'included' CHECK (cost_band IN (
    'free','included','low','medium','high'
  )),
  vendor_lock_in   TEXT NOT NULL DEFAULT 'low' CHECK (vendor_lock_in IN (
    'low','medium','high'
  )),

  -- ── Capability metadata ───────────────────────────────────────────────────
  capabilities     TEXT[]  NOT NULL DEFAULT '{}',
  -- surfaces: JSON array of console route paths (e.g. ["/database","/advisor"])
  surfaces         JSONB   NOT NULL DEFAULT '[]',
  -- env_keys: required environment variable names
  env_keys         TEXT[]  NOT NULL DEFAULT '{}',
  docs_url         TEXT,
  notes            TEXT,

  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ─── ops.integrations_installations ──────────────────────────────────────────
-- One row per integration that has been connected to this team/project.
-- Missing rows = "not installed". Stale rows = check last_checked_at.
CREATE TABLE IF NOT EXISTS ops.integrations_installations (
  key              TEXT PRIMARY KEY
                     REFERENCES ops.integrations_catalog(key)
                     ON DELETE CASCADE,
  status           TEXT NOT NULL DEFAULT 'inactive' CHECK (status IN (
    'active','inactive','error','setup_required'
  )),
  billing          TEXT NOT NULL DEFAULT 'direct' CHECK (billing IN (
    'vercel','direct','free'
  )),
  -- Provenance: where this status came from (Vercel API payload, manual, etc.)
  evidence         JSONB NOT NULL DEFAULT '{}',
  last_checked_at  TIMESTAMPTZ,
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ─── updated_at trigger ───────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION ops.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS integrations_catalog_updated_at  ON ops.integrations_catalog;
DROP TRIGGER IF EXISTS integrations_install_updated_at  ON ops.integrations_installations;

CREATE TRIGGER integrations_catalog_updated_at
  BEFORE UPDATE ON ops.integrations_catalog
  FOR EACH ROW EXECUTE FUNCTION ops.set_updated_at();

CREATE TRIGGER integrations_install_updated_at
  BEFORE UPDATE ON ops.integrations_installations
  FOR EACH ROW EXECUTE FUNCTION ops.set_updated_at();

-- ─── RLS ──────────────────────────────────────────────────────────────────────
ALTER TABLE ops.integrations_catalog      ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.integrations_installations ENABLE ROW LEVEL SECURITY;

-- Catalog: read for any authenticated user; write restricted to service_role
DROP POLICY IF EXISTS "catalog_authenticated_read"  ON ops.integrations_catalog;
DROP POLICY IF EXISTS "catalog_service_write"        ON ops.integrations_catalog;
CREATE POLICY "catalog_authenticated_read"  ON ops.integrations_catalog
  FOR SELECT TO authenticated USING (true);
CREATE POLICY "catalog_service_write"        ON ops.integrations_catalog
  FOR ALL    TO service_role USING (true);

-- Installations: same pattern
DROP POLICY IF EXISTS "installations_authenticated_read" ON ops.integrations_installations;
DROP POLICY IF EXISTS "installations_service_write"      ON ops.integrations_installations;
CREATE POLICY "installations_authenticated_read" ON ops.integrations_installations
  FOR SELECT TO authenticated USING (true);
CREATE POLICY "installations_service_write"      ON ops.integrations_installations
  FOR ALL    TO service_role USING (true);

-- ─── Seed: catalog ────────────────────────────────────────────────────────────
-- 7 currently-connected + extended catalog for future activation.
-- Conflict: update metadata but preserve key identity.
INSERT INTO ops.integrations_catalog
  (key, name, category, provider, description,
   baseline_allowed, plan_tier, cost_band, vendor_lock_in,
   capabilities, surfaces, env_keys)
VALUES
  -- ── Currently connected (from Vercel marketplace + direct) ────────────────
  ('supabase', 'Supabase', 'auth_data', 'vercel_marketplace',
   'Authentication, database, storage, and edge functions. Primary backend for ops data.',
   true, 'baseline', 'included', 'medium',
   ARRAY['auth','db','storage','edge_functions','realtime'],
   '["/database","/platform","/settings"]'::jsonb,
   ARRAY['NEXT_PUBLIC_SUPABASE_URL','SUPABASE_SERVICE_ROLE_KEY','SUPABASE_MANAGEMENT_API_TOKEN']),

  ('groq', 'Groq', 'ai_inference', 'vercel_marketplace',
   'Ultra-fast LLM inference for real-time AI operations and scoring.',
   true, 'baseline', 'included', 'low',
   ARRAY['inference','llm'],
   '["/advisor"]'::jsonb,
   ARRAY['GROQ_API_KEY']),

  ('fal', 'fal', 'ai_inference', 'vercel_marketplace',
   'Serverless AI for media processing, image generation, and multimodal tasks.',
   true, 'baseline', 'included', 'low',
   ARRAY['media_processing','image_gen','multimodal'],
   '["/advisor"]'::jsonb,
   ARRAY['FAL_KEY']),

  ('browserbase', 'Browserbase', 'agents', 'vercel_marketplace',
   'Headless browser infrastructure for AI agents and automated testing.',
   true, 'baseline', 'included', 'low',
   ARRAY['browser_automation','testing'],
   '[]'::jsonb,
   ARRAY['BROWSERBASE_API_KEY']),

  ('autonoma', 'Autonoma AI', 'agents', 'vercel_marketplace',
   'Autonomous AI agents for platform operations and monitoring tasks.',
   true, 'baseline', 'included', 'low',
   ARRAY['autonomous_agents','monitoring'],
   '[]'::jsonb,
   ARRAY['AUTONOMA_API_KEY']),

  ('inngest', 'Inngest', 'devtools', 'vercel_marketplace',
   'Event-driven background functions, workflows, and scheduled jobs.',
   true, 'baseline', 'included', 'medium',
   ARRAY['event_driven','workflows','scheduled_jobs'],
   '["/deployments","/advisor"]'::jsonb,
   ARRAY['INNGEST_EVENT_KEY','INNGEST_SIGNING_KEY']),

  ('slack', 'Slack', 'messaging', 'direct',
   'Team notifications for deployments, alerts, and gate failures.',
   true, 'baseline', 'free', 'medium',
   ARRAY['notifications','messaging'],
   '["/settings"]'::jsonb,
   ARRAY['SLACK_WEBHOOK_URL']),

  -- ── Extended catalog (not yet installed — available to activate) ───────────
  ('stripe', 'Stripe', 'analytics', 'direct',
   'Payment processing and subscription management.',
   true, 'baseline', 'included', 'high',
   ARRAY['payments','subscriptions'],
   '["/settings"]'::jsonb,
   ARRAY['STRIPE_SECRET_KEY','NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY']),

  ('vercel_analytics', 'Vercel Analytics', 'observability', 'vercel_marketplace',
   'First-party web analytics and Core Web Vitals monitoring.',
   true, 'baseline', 'included', 'high',
   ARRAY['analytics','web_vitals'],
   '["/observability","/metrics"]'::jsonb,
   ARRAY['VERCEL_WEB_ANALYTICS_ID']),

  ('n8n', 'n8n', 'workflow', 'direct',
   'Workflow automation and integration orchestration. Self-hosted on DO droplet.',
   true, 'baseline', 'free', 'low',
   ARRAY['workflow','automation','integrations'],
   '["/platform"]'::jsonb,
   ARRAY['N8N_WEBHOOK_URL']),

  ('sentry', 'Sentry', 'observability', 'direct',
   'Error tracking, performance monitoring, and alerting for production apps.',
   false, 'optional', 'low', 'medium',
   ARRAY['error_tracking','performance','alerting'],
   '["/observability"]'::jsonb,
   ARRAY['SENTRY_DSN']),

  ('openai', 'OpenAI', 'ai_inference', 'direct',
   'GPT-4 and embedding models for AI features beyond Groq capabilities.',
   false, 'optional', 'medium', 'high',
   ARRAY['inference','embeddings','llm'],
   '["/advisor"]'::jsonb,
   ARRAY['OPENAI_API_KEY'])

ON CONFLICT (key) DO UPDATE SET
  name             = EXCLUDED.name,
  description      = EXCLUDED.description,
  baseline_allowed = EXCLUDED.baseline_allowed,
  plan_tier        = EXCLUDED.plan_tier,
  cost_band        = EXCLUDED.cost_band,
  capabilities     = EXCLUDED.capabilities,
  surfaces         = EXCLUDED.surfaces,
  env_keys         = EXCLUDED.env_keys,
  updated_at       = now();

-- ─── Seed: installations (7 active per screenshot evidence) ──────────────────
INSERT INTO ops.integrations_installations (key, status, billing, evidence, last_checked_at)
VALUES
  ('supabase',    'active', 'vercel', '{"source":"vercel_marketplace","note":"primary backend"}'::jsonb,     now()),
  ('groq',        'active', 'vercel', '{"source":"vercel_marketplace"}'::jsonb,                              now()),
  ('fal',         'active', 'vercel', '{"source":"vercel_marketplace"}'::jsonb,                              now()),
  ('browserbase', 'active', 'vercel', '{"source":"vercel_marketplace"}'::jsonb,                              now()),
  ('autonoma',    'active', 'vercel', '{"source":"vercel_marketplace"}'::jsonb,                              now()),
  ('inngest',     'active', 'vercel', '{"source":"vercel_marketplace"}'::jsonb,                              now()),
  ('slack',       'active', 'direct', '{"source":"direct","note":"webhook-based"}'::jsonb,                   now())

ON CONFLICT (key) DO UPDATE SET
  status          = EXCLUDED.status,
  billing         = EXCLUDED.billing,
  evidence        = EXCLUDED.evidence,
  last_checked_at = now(),
  updated_at      = now();

-- ─── Convenience view ─────────────────────────────────────────────────────────
-- Joins catalog + installations for UI consumption.
-- Missing installation row = status 'inactive'.
CREATE OR REPLACE VIEW ops.integrations_view AS
SELECT
  c.key,
  c.name,
  c.category,
  c.provider,
  c.description,
  c.baseline_allowed,
  c.plan_tier,
  c.cost_band,
  c.vendor_lock_in,
  c.capabilities,
  c.surfaces,
  c.env_keys,
  c.docs_url,
  COALESCE(i.status,  'inactive')  AS status,
  COALESCE(i.billing, 'direct')    AS billing,
  COALESCE(i.evidence, '{}')       AS evidence,
  i.last_checked_at
FROM ops.integrations_catalog c
LEFT JOIN ops.integrations_installations i USING (key)
ORDER BY c.baseline_allowed DESC, c.plan_tier, c.category, c.name;
