-- =============================================================================
-- Migration: ops convergence findings + maintenance runs + AI models + agent_runs extensions
-- Owner: Supabase (SSOT for deployment convergence + periodic maintenance)
-- Extends: 20260301000065_ops_workitems_webhooks.sql
-- See: spec/odooops-console/plan.md § Deployment Convergence, FixBot, Maintenance
-- =============================================================================

-- =============================================================================
-- Extend ops.agent_runs for FixBot columns (idempotent)
-- =============================================================================
ALTER TABLE ops.agent_runs
  ADD COLUMN IF NOT EXISTS kind           text,       -- fix_build | fix_gate | fix_migration | fix_webhook
  ADD COLUMN IF NOT EXISTS trigger_source text,       -- vercel | github | supabase | manual
  ADD COLUMN IF NOT EXISTS trigger_ref    text,       -- deployment_id, run_id, gate_id, etc.
  ADD COLUMN IF NOT EXISTS prompt         text,       -- Agent Relay Template payload
  ADD COLUMN IF NOT EXISTS pr_url         text;       -- set when PR is opened

CREATE INDEX IF NOT EXISTS idx_agent_runs_kind ON ops.agent_runs (kind);
CREATE INDEX IF NOT EXISTS idx_agent_runs_trigger ON ops.agent_runs (trigger_source, trigger_ref);

-- =============================================================================
-- ops.convergence_findings — Deployment drift detection results
-- =============================================================================
CREATE TABLE IF NOT EXISTS ops.convergence_findings (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    env             text NOT NULL,                  -- prod | stage
    kind            text NOT NULL,                  -- deploy_failed | deploy_behind | migrations_pending | env_missing | vault_missing | dns_planned | gate_failed | webhook_unverified | awaiting_auth | canceled_superseded | function_missing
    key             text NOT NULL,                  -- specific identifier (function name, env var name, etc.)
    status          text NOT NULL DEFAULT 'open',   -- open | resolved | escalated | stale
    evidence        jsonb DEFAULT '{}',             -- links, SHA diffs, error messages
    suggested_action text,                          -- human-readable next step
    first_seen      timestamptz DEFAULT now(),
    last_seen       timestamptz DEFAULT now(),
    resolved_at     timestamptz,
    created_at      timestamptz DEFAULT now(),
    updated_at      timestamptz DEFAULT now(),

    UNIQUE (env, kind, key)                         -- one finding per env+kind+key
);

CREATE INDEX IF NOT EXISTS idx_convergence_findings_env ON ops.convergence_findings (env);
CREATE INDEX IF NOT EXISTS idx_convergence_findings_status ON ops.convergence_findings (status);
CREATE INDEX IF NOT EXISTS idx_convergence_findings_kind ON ops.convergence_findings (kind);

-- RLS
ALTER TABLE ops.convergence_findings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all" ON ops.convergence_findings
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_read" ON ops.convergence_findings
    FOR SELECT TO authenticated USING (true);

GRANT SELECT, INSERT, UPDATE ON ops.convergence_findings TO service_role;
GRANT SELECT ON ops.convergence_findings TO authenticated;

-- =============================================================================
-- ops.maintenance_runs — Periodic chore execution tracking
-- =============================================================================
CREATE TABLE IF NOT EXISTS ops.maintenance_runs (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    chore_id        text NOT NULL,                  -- matches ssot/maintenance/schedules.yaml chore ID
    chore_name      text NOT NULL,
    status          text NOT NULL DEFAULT 'pending', -- pending | running | completed | failed
    started_at      timestamptz,
    completed_at    timestamptz,
    duration_ms     integer GENERATED ALWAYS AS (
        EXTRACT(EPOCH FROM (completed_at - started_at)) * 1000
    ) STORED,
    findings_count  integer DEFAULT 0,
    evidence        jsonb DEFAULT '{}',             -- summary, artifact links
    error_message   text,
    created_at      timestamptz DEFAULT now(),
    updated_at      timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_maintenance_runs_chore ON ops.maintenance_runs (chore_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_runs_status ON ops.maintenance_runs (status);
CREATE INDEX IF NOT EXISTS idx_maintenance_runs_created ON ops.maintenance_runs (created_at DESC);

-- RLS
ALTER TABLE ops.maintenance_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all" ON ops.maintenance_runs
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_read" ON ops.maintenance_runs
    FOR SELECT TO authenticated USING (true);

GRANT SELECT, INSERT, UPDATE ON ops.maintenance_runs TO service_role;
GRANT SELECT ON ops.maintenance_runs TO authenticated;

-- =============================================================================
-- ops.maintenance_run_events — Audit trail for maintenance chore steps
-- =============================================================================
CREATE TABLE IF NOT EXISTS ops.maintenance_run_events (
    id              bigserial PRIMARY KEY,
    run_id          uuid NOT NULL REFERENCES ops.maintenance_runs(id) ON DELETE CASCADE,
    ts              timestamptz DEFAULT now(),
    level           text NOT NULL DEFAULT 'info',   -- info | warn | error
    message         text NOT NULL,
    data            jsonb DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_maintenance_run_events_run ON ops.maintenance_run_events (run_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_run_events_ts ON ops.maintenance_run_events (ts DESC);

-- RLS
ALTER TABLE ops.maintenance_run_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all" ON ops.maintenance_run_events
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_read" ON ops.maintenance_run_events
    FOR SELECT TO authenticated USING (true);

GRANT SELECT, INSERT ON ops.maintenance_run_events TO service_role;
GRANT SELECT ON ops.maintenance_run_events TO authenticated;

-- =============================================================================
-- ops.ai_models — AI provider model inventory (Gradient ADK + others)
-- =============================================================================
CREATE TABLE IF NOT EXISTS ops.ai_models (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    provider        text NOT NULL,                  -- digitalocean | openai | anthropic | etc.
    model           text NOT NULL,                  -- model name/ID
    status          text NOT NULL DEFAULT 'available', -- available | deprecated | preview
    capabilities    text[] DEFAULT '{}',            -- chat, completions, embeddings, etc.
    metadata        jsonb DEFAULT '{}',             -- context_window, pricing, etc.
    last_seen       timestamptz DEFAULT now(),
    created_at      timestamptz DEFAULT now(),
    updated_at      timestamptz DEFAULT now(),

    UNIQUE (provider, model)
);

CREATE INDEX IF NOT EXISTS idx_ai_models_provider ON ops.ai_models (provider);
CREATE INDEX IF NOT EXISTS idx_ai_models_status ON ops.ai_models (status);

-- RLS
ALTER TABLE ops.ai_models ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_all" ON ops.ai_models
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "authenticated_read" ON ops.ai_models
    FOR SELECT TO authenticated USING (true);

GRANT SELECT, INSERT, UPDATE ON ops.ai_models TO service_role;
GRANT SELECT ON ops.ai_models TO authenticated;

-- =============================================================================
-- Seed: maintenance schedules into ops.schedules
-- =============================================================================
INSERT INTO ops.schedules (name, cron, job_type, agent, input_json, enabled)
VALUES
  ('convergence-scan',       '*/15 * * * *', 'convergence_scan',     'convergence-agent',  '{}',                    true),
  ('backup-freshness-check', '0 4 * * *',    'backup_freshness',     'convergence-agent',  '{}',                    true),
  ('secrets-registry-audit', '0 9 * * 2',    'secrets_audit',        'convergence-agent',  '{}',                    true),
  ('rls-drift-audit',        '0 8 * * 2',    'rls_drift',            'convergence-agent',  '{}',                    false),
  ('access-review',          '0 11 1 * *',   'access_review',        'convergence-agent',  '{}',                    false),
  ('cost-snapshot',          '0 12 1 * *',   'cost_snapshot',        'convergence-agent',  '{}',                    false)
ON CONFLICT (name) DO NOTHING;

-- =============================================================================
-- Helper: upsert a convergence finding (idempotent by env+kind+key)
-- =============================================================================
CREATE OR REPLACE FUNCTION ops.upsert_convergence_finding(
    p_env              text,
    p_kind             text,
    p_key              text,
    p_status           text DEFAULT 'open',
    p_evidence         jsonb DEFAULT '{}',
    p_suggested_action text DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_id uuid;
BEGIN
    INSERT INTO ops.convergence_findings (env, kind, key, status, evidence, suggested_action, last_seen)
    VALUES (p_env, p_kind, p_key, p_status, p_evidence, p_suggested_action, now())
    ON CONFLICT (env, kind, key) DO UPDATE SET
        status = EXCLUDED.status,
        evidence = EXCLUDED.evidence,
        suggested_action = EXCLUDED.suggested_action,
        last_seen = now(),
        updated_at = now()
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$;

GRANT EXECUTE ON FUNCTION ops.upsert_convergence_finding TO service_role;

-- =============================================================================
-- Helper: resolve a convergence finding
-- =============================================================================
CREATE OR REPLACE FUNCTION ops.resolve_convergence_finding(
    p_env  text,
    p_kind text,
    p_key  text
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    UPDATE ops.convergence_findings
    SET status = 'resolved',
        resolved_at = now(),
        updated_at = now()
    WHERE env = p_env AND kind = p_kind AND key = p_key
      AND status != 'resolved';
END;
$$;

GRANT EXECUTE ON FUNCTION ops.resolve_convergence_finding TO service_role;
