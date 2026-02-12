-- ============================================================================
-- DATAVERSE ENTERPRISE CONSOLE - POLICY EXTENSIONS
-- ============================================================================
-- Portfolio Initiative: PORT-2026-012
-- Created: 2026-02-13
-- Purpose: Extend ops.* schema with Cursor-Enterprise-style policy enforcement
-- Related: CTRL-POLICY-001, CTRL-CAPABILITY-001, CTRL-MODEL-001
-- ============================================================================

-- Create ops schema if not exists
CREATE SCHEMA IF NOT EXISTS ops;

-- ============================================================================
-- TABLE: ops.model_policy
-- Purpose: Model allowlist/blocklist per organization
-- Pattern: Cursor's model governance enforcement
-- ============================================================================

CREATE TABLE IF NOT EXISTS ops.model_policy (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL,
    model_family TEXT NOT NULL CHECK (model_family IN ('anthropic', 'openai', 'deepseek', 'google', 'meta')),
    model_name TEXT NOT NULL,
    policy_type TEXT NOT NULL CHECK (policy_type IN ('allow', 'block')),
    reason TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    created_by UUID,
    updated_at TIMESTAMPTZ DEFAULT now(),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE (org_id, model_name)
);

CREATE INDEX IF NOT EXISTS ops_model_policy_org_idx ON ops.model_policy(org_id);
CREATE INDEX IF NOT EXISTS ops_model_policy_family_idx ON ops.model_policy(model_family);
CREATE INDEX IF NOT EXISTS ops_model_policy_type_idx ON ops.model_policy(policy_type);

COMMENT ON TABLE ops.model_policy IS 'Model governance: allowlist/blocklist enforcement per org';
COMMENT ON COLUMN ops.model_policy.model_family IS 'LLM provider family (anthropic, openai, etc)';
COMMENT ON COLUMN ops.model_policy.model_name IS 'Specific model identifier (claude-sonnet-4.5, gpt-4o)';
COMMENT ON COLUMN ops.model_policy.policy_type IS 'Policy action: allow (explicit approval) or block (prohibited)';

-- ============================================================================
-- TABLE: ops.policy_decisions
-- Purpose: Real-time policy audit trail (append-only log)
-- Pattern: Cursor's policy decision logging with evidence linkage
-- ============================================================================

CREATE TABLE IF NOT EXISTS ops.policy_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ts TIMESTAMPTZ DEFAULT now(),
    bot_id TEXT,
    request_id UUID,
    policy_type TEXT NOT NULL CHECK (policy_type IN ('privacy', 'model', 'capability', 'rate_limit', 'composite')),
    decision TEXT NOT NULL CHECK (decision IN ('allow', 'block', 'warn')),
    reason TEXT NOT NULL,
    model_requested TEXT,
    tool_requested TEXT,
    privacy_mode_enabled BOOLEAN,
    evidence_id TEXT,
    evidence_path TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS ops_policy_decisions_ts_idx ON ops.policy_decisions(ts DESC);
CREATE INDEX IF NOT EXISTS ops_policy_decisions_bot_idx ON ops.policy_decisions(bot_id);
CREATE INDEX IF NOT EXISTS ops_policy_decisions_decision_idx ON ops.policy_decisions(decision) WHERE decision = 'block';
CREATE INDEX IF NOT EXISTS ops_policy_decisions_policy_type_idx ON ops.policy_decisions(policy_type);
CREATE INDEX IF NOT EXISTS ops_policy_decisions_request_idx ON ops.policy_decisions(request_id);

COMMENT ON TABLE ops.policy_decisions IS 'Append-only audit log for all policy enforcement decisions';
COMMENT ON COLUMN ops.policy_decisions.policy_type IS 'Type of policy evaluated (privacy, model, capability, rate_limit, composite)';
COMMENT ON COLUMN ops.policy_decisions.decision IS 'Enforcement outcome (allow, block, warn)';
COMMENT ON COLUMN ops.policy_decisions.evidence_id IS 'Link to evidence artifact (EVID-YYYYMMDD-XXX format)';
COMMENT ON COLUMN ops.policy_decisions.evidence_path IS 'Relative path to evidence in docs/evidence/';

-- ============================================================================
-- TABLE: ops.capability_attestations
-- Purpose: Capability validation registry (code evidence required)
-- Pattern: Cursor's attestation-based access control
-- ============================================================================

CREATE TABLE IF NOT EXISTS ops.capability_attestations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id TEXT NOT NULL,
    capability_key TEXT NOT NULL,
    has_capability BOOLEAN NOT NULL DEFAULT false,
    attestation_method TEXT CHECK (attestation_method IN ('code_scan', 'manual_verification', 'test_suite', 'runtime_validation')),
    attestation_evidence TEXT,
    last_validated_at TIMESTAMPTZ,
    validator_id TEXT,
    expiry_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE (bot_id, capability_key)
);

CREATE INDEX IF NOT EXISTS ops_capability_attestations_bot_idx ON ops.capability_attestations(bot_id);
CREATE INDEX IF NOT EXISTS ops_capability_attestations_key_idx ON ops.capability_attestations(capability_key);
CREATE INDEX IF NOT EXISTS ops_capability_attestations_status_idx ON ops.capability_attestations(has_capability) WHERE has_capability = true;
CREATE INDEX IF NOT EXISTS ops_capability_attestations_expiry_idx ON ops.capability_attestations(expiry_date) WHERE expiry_date IS NOT NULL;

COMMENT ON TABLE ops.capability_attestations IS 'Capability validation registry with evidence-based attestation';
COMMENT ON COLUMN ops.capability_attestations.capability_key IS 'Capability identifier from gold.capability_map';
COMMENT ON COLUMN ops.capability_attestations.attestation_method IS 'How capability was validated (code_scan, manual, test_suite, runtime)';
COMMENT ON COLUMN ops.capability_attestations.attestation_evidence IS 'Path or reference to validation evidence';
COMMENT ON COLUMN ops.capability_attestations.expiry_date IS 'Optional expiry for time-bound capabilities';

-- ============================================================================
-- TABLE: ops.privacy_mode_config
-- Purpose: Privacy mode settings per organization
-- Pattern: Cursor's x-ghost-mode with privacy-by-default
-- ============================================================================

CREATE TABLE IF NOT EXISTS ops.privacy_mode_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL UNIQUE,
    default_privacy_enabled BOOLEAN NOT NULL DEFAULT true,
    allowed_models_privacy TEXT[] DEFAULT ARRAY['claude-sonnet-4.5', 'claude-opus-4.6']::TEXT[],
    blocked_indexing_paths TEXT[] DEFAULT ARRAY['**/.env*', '**/secrets/**', '**/credentials/**']::TEXT[],
    enforcement_level TEXT NOT NULL DEFAULT 'strict' CHECK (enforcement_level IN ('strict', 'warn', 'audit')),
    privacy_replica_endpoint TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS ops_privacy_config_org_idx ON ops.privacy_mode_config(org_id);

COMMENT ON TABLE ops.privacy_mode_config IS 'Privacy mode configuration per organization (Cursor x-ghost-mode pattern)';
COMMENT ON COLUMN ops.privacy_mode_config.default_privacy_enabled IS 'Privacy-by-default: true = route to privacy replica if header missing';
COMMENT ON COLUMN ops.privacy_mode_config.allowed_models_privacy IS 'Models approved for privacy mode (no plaintext code storage)';
COMMENT ON COLUMN ops.privacy_mode_config.blocked_indexing_paths IS 'Paths to exclude from indexing (like .cursorignore)';
COMMENT ON COLUMN ops.privacy_mode_config.enforcement_level IS 'strict = block violations, warn = log only, audit = passive monitoring';

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function: Get organization privacy configuration
CREATE OR REPLACE FUNCTION ops.get_org_privacy_config(p_org_id UUID)
RETURNS ops.privacy_mode_config AS $$
    SELECT * FROM ops.privacy_mode_config WHERE org_id = p_org_id;
$$ LANGUAGE SQL STABLE SECURITY DEFINER;

COMMENT ON FUNCTION ops.get_org_privacy_config IS 'Retrieve privacy configuration for an organization';

-- Function: Check if model is allowed for organization
CREATE OR REPLACE FUNCTION ops.check_model_allowed(p_org_id UUID, p_model TEXT)
RETURNS BOOLEAN AS $$
    SELECT EXISTS (
        SELECT 1 FROM ops.model_policy
        WHERE org_id = p_org_id
        AND model_name = p_model
        AND policy_type = 'allow'
    ) AND NOT EXISTS (
        SELECT 1 FROM ops.model_policy
        WHERE org_id = p_org_id
        AND model_name = p_model
        AND policy_type = 'block'
    );
$$ LANGUAGE SQL STABLE SECURITY DEFINER;

COMMENT ON FUNCTION ops.check_model_allowed IS 'Validate if model is allowed (not explicitly blocked) for org';

-- Function: Check if bot has capability
CREATE OR REPLACE FUNCTION ops.check_bot_capability(p_bot_id TEXT, p_capability TEXT)
RETURNS BOOLEAN AS $$
    SELECT EXISTS (
        SELECT 1 FROM ops.capability_attestations
        WHERE bot_id = p_bot_id
        AND capability_key = p_capability
        AND has_capability = true
        AND (expiry_date IS NULL OR expiry_date > now())
    );
$$ LANGUAGE SQL STABLE SECURITY DEFINER;

COMMENT ON FUNCTION ops.check_bot_capability IS 'Validate if bot has attested capability (non-expired)';

-- Function: Log policy decision (convenience wrapper)
CREATE OR REPLACE FUNCTION ops.log_policy_decision(
    p_bot_id TEXT,
    p_request_id UUID,
    p_policy_type TEXT,
    p_decision TEXT,
    p_reason TEXT,
    p_model_requested TEXT DEFAULT NULL,
    p_tool_requested TEXT DEFAULT NULL,
    p_privacy_mode BOOLEAN DEFAULT NULL,
    p_evidence_id TEXT DEFAULT NULL,
    p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS UUID AS $$
DECLARE
    v_decision_id UUID;
BEGIN
    INSERT INTO ops.policy_decisions (
        bot_id, request_id, policy_type, decision, reason,
        model_requested, tool_requested, privacy_mode_enabled,
        evidence_id, metadata
    ) VALUES (
        p_bot_id, p_request_id, p_policy_type, p_decision, p_reason,
        p_model_requested, p_tool_requested, p_privacy_mode,
        p_evidence_id, p_metadata
    ) RETURNING id INTO v_decision_id;

    RETURN v_decision_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION ops.log_policy_decision IS 'Convenience function to log policy enforcement decisions';

-- ============================================================================
-- SEED DATA: Default Policies (Production-Approved Models)
-- ============================================================================

-- Default organization (use first org from registry or create placeholder)
DO $$
DECLARE
    v_org_id UUID;
BEGIN
    -- Check if registry.orgs exists
    IF EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'registry' AND tablename = 'orgs') THEN
        SELECT id INTO v_org_id FROM registry.orgs LIMIT 1;
    END IF;

    -- Only seed if we have an org_id
    IF v_org_id IS NOT NULL THEN
        -- Seed model policies (production-approved models)
        INSERT INTO ops.model_policy (org_id, model_family, model_name, policy_type, reason)
        VALUES
            (v_org_id, 'anthropic', 'claude-sonnet-4.5', 'allow', 'Production-approved model for general use'),
            (v_org_id, 'anthropic', 'claude-opus-4.6', 'allow', 'Production-approved model for complex tasks'),
            (v_org_id, 'anthropic', 'claude-haiku-4.5', 'allow', 'Production-approved model for speed'),
            (v_org_id, 'openai', 'gpt-4o', 'allow', 'Production-approved model (fallback)'),
            (v_org_id, 'openai', 'gpt-3.5-turbo', 'block', 'Deprecated model - use claude-sonnet-4.5 instead')
        ON CONFLICT (org_id, model_name) DO NOTHING;

        -- Seed privacy config (privacy-by-default)
        INSERT INTO ops.privacy_mode_config (org_id, default_privacy_enabled, enforcement_level)
        VALUES (v_org_id, true, 'strict')
        ON CONFLICT (org_id) DO NOTHING;

        RAISE NOTICE 'Seeded default policies for org_id: %', v_org_id;
    ELSE
        RAISE NOTICE 'No organization found in registry.orgs - skipping seed data';
    END IF;
END $$;

-- ============================================================================
-- ROW-LEVEL SECURITY (RLS)
-- ============================================================================

ALTER TABLE ops.model_policy ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.policy_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.capability_attestations ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.privacy_mode_config ENABLE ROW LEVEL SECURITY;

-- Policy: Service role has full access
CREATE POLICY IF NOT EXISTS "Service role full access model_policy"
    ON ops.model_policy FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY IF NOT EXISTS "Service role full access policy_decisions"
    ON ops.policy_decisions FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY IF NOT EXISTS "Service role full access capability_attestations"
    ON ops.capability_attestations FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

CREATE POLICY IF NOT EXISTS "Service role full access privacy_config"
    ON ops.privacy_mode_config FOR ALL
    USING (auth.jwt() ->> 'role' = 'service_role');

-- Policy: Org admins can read their org's policies
CREATE POLICY IF NOT EXISTS "Org admins read model_policy"
    ON ops.model_policy FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM memberships m
            WHERE m.user_id = auth.uid()
            AND m.org_id = model_policy.org_id
            AND m.role IN ('org_owner', 'admin', 'security_admin')
        )
    );

-- Policy: Org admins can view policy decisions for their org
CREATE POLICY IF NOT EXISTS "Org admins read policy_decisions"
    ON ops.policy_decisions FOR SELECT
    USING (
        bot_id IN (
            SELECT bot_id FROM control_plane.bot_registry br
            INNER JOIN memberships m ON m.org_id = br.org_id
            WHERE m.user_id = auth.uid()
            AND m.role IN ('org_owner', 'admin', 'security_admin')
        )
    );

-- ============================================================================
-- GRANTS
-- ============================================================================

-- Grant usage on schema
GRANT USAGE ON SCHEMA ops TO service_role, authenticated, anon;

-- Grant table permissions
GRANT ALL ON ops.model_policy TO service_role;
GRANT ALL ON ops.policy_decisions TO service_role;
GRANT ALL ON ops.capability_attestations TO service_role;
GRANT ALL ON ops.privacy_mode_config TO service_role;

GRANT SELECT ON ops.model_policy TO authenticated;
GRANT SELECT ON ops.policy_decisions TO authenticated;
GRANT SELECT ON ops.capability_attestations TO authenticated;
GRANT SELECT ON ops.privacy_mode_config TO authenticated;

-- Grant function execution
GRANT EXECUTE ON FUNCTION ops.get_org_privacy_config TO service_role, authenticated;
GRANT EXECUTE ON FUNCTION ops.check_model_allowed TO service_role, authenticated;
GRANT EXECUTE ON FUNCTION ops.check_bot_capability TO service_role, authenticated;
GRANT EXECUTE ON FUNCTION ops.log_policy_decision TO service_role;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check tables exist
DO $$
BEGIN
    ASSERT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'ops' AND tablename = 'model_policy'),
        'ops.model_policy table not created';
    ASSERT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'ops' AND tablename = 'policy_decisions'),
        'ops.policy_decisions table not created';
    ASSERT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'ops' AND tablename = 'capability_attestations'),
        'ops.capability_attestations table not created';
    ASSERT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = 'ops' AND tablename = 'privacy_mode_config'),
        'ops.privacy_mode_config table not created';

    RAISE NOTICE 'All policy extension tables created successfully';
END $$;

-- ============================================================================
-- END MIGRATION
-- ============================================================================
