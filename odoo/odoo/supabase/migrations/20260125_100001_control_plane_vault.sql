-- AI Control Plane with Supabase Vault Integration
-- Provides centralized secret management for BugBot, Vercel Bot, and DO automation
-- All secrets stored encrypted at rest via Vault extension

-- Create control_plane schema
CREATE SCHEMA IF NOT EXISTS control_plane;

-- Enable Vault extension (safe & idempotent)
CREATE EXTENSION IF NOT EXISTS supabase_vault WITH SCHEMA vault;

-- Secret index table - maps logical names to Vault IDs
CREATE TABLE IF NOT EXISTS control_plane.secret_index (
    name          text PRIMARY KEY,                           -- e.g. DIGITALOCEAN_API_TOKEN
    purpose       text NOT NULL,                              -- e.g. 'digitalocean_api', 'vercel_api'
    description   text,                                       -- Human-readable description
    vault_id      uuid NOT NULL,                              -- FK to vault.secrets.id
    created_at    timestamptz NOT NULL DEFAULT now(),
    updated_at    timestamptz NOT NULL DEFAULT now(),
    last_accessed_at timestamptz,
    access_count  integer NOT NULL DEFAULT 0
);

-- Create index for purpose-based lookups
CREATE INDEX IF NOT EXISTS idx_secret_index_purpose ON control_plane.secret_index(purpose);

-- Access log for audit trail
CREATE TABLE IF NOT EXISTS control_plane.secret_access_log (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    secret_name   text NOT NULL REFERENCES control_plane.secret_index(name) ON DELETE CASCADE,
    accessor      text NOT NULL,                              -- e.g. 'bugbot', 'vercel-bot', 'edge-function'
    access_type   text NOT NULL CHECK (access_type IN ('read', 'proxy', 'exchange')),
    ip_address    inet,
    user_agent    text,
    success       boolean NOT NULL DEFAULT true,
    error_message text,
    accessed_at   timestamptz NOT NULL DEFAULT now()
);

-- Create index for recent access queries
CREATE INDEX IF NOT EXISTS idx_secret_access_log_recent ON control_plane.secret_access_log(accessed_at DESC);
CREATE INDEX IF NOT EXISTS idx_secret_access_log_secret ON control_plane.secret_access_log(secret_name);

-- Bot registry - track registered control plane bots
CREATE TABLE IF NOT EXISTS control_plane.bot_registry (
    bot_id        text PRIMARY KEY,                           -- e.g. 'bugbot', 'vercel-bot'
    display_name  text NOT NULL,
    description   text,
    bot_type      text NOT NULL CHECK (bot_type IN ('sre', 'deployment', 'infra', 'general')),
    endpoint_url  text,                                        -- Where the bot is deployed
    allowed_secrets text[] NOT NULL DEFAULT '{}',              -- Secrets this bot can access
    is_active     boolean NOT NULL DEFAULT true,
    created_at    timestamptz NOT NULL DEFAULT now(),
    updated_at    timestamptz NOT NULL DEFAULT now(),
    last_heartbeat_at timestamptz
);

-- Bot execution log
CREATE TABLE IF NOT EXISTS control_plane.bot_execution_log (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id        text NOT NULL REFERENCES control_plane.bot_registry(bot_id) ON DELETE CASCADE,
    execution_type text NOT NULL,                              -- e.g. 'bug_analysis', 'deployment_check'
    source        text,                                        -- Where the request came from
    request_payload jsonb,
    response_payload jsonb,
    ai_model      text,                                        -- Which AI model was used
    tokens_used   integer,
    latency_ms    integer,
    status        text NOT NULL CHECK (status IN ('success', 'error', 'timeout')),
    error_message text,
    executed_at   timestamptz NOT NULL DEFAULT now()
);

-- Create indexes for execution log queries
CREATE INDEX IF NOT EXISTS idx_bot_execution_log_bot ON control_plane.bot_execution_log(bot_id);
CREATE INDEX IF NOT EXISTS idx_bot_execution_log_recent ON control_plane.bot_execution_log(executed_at DESC);
CREATE INDEX IF NOT EXISTS idx_bot_execution_log_status ON control_plane.bot_execution_log(status);

-- Helper function: get secret by name (SECURITY DEFINER - runs as owner)
CREATE OR REPLACE FUNCTION control_plane.get_secret(p_name text)
RETURNS text
LANGUAGE sql
SECURITY DEFINER
SET search_path = public, vault, control_plane
AS $$
    SELECT vs.decrypted_secret
    FROM control_plane.secret_index si
    JOIN vault.decrypted_secrets vs ON vs.id = si.vault_id
    WHERE si.name = p_name
    LIMIT 1;
$$;

-- Helper function: get secret with access logging
CREATE OR REPLACE FUNCTION control_plane.get_secret_logged(
    p_name text,
    p_accessor text,
    p_access_type text DEFAULT 'read',
    p_ip inet DEFAULT NULL,
    p_user_agent text DEFAULT NULL
)
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, vault, control_plane
AS $$
DECLARE
    v_secret text;
BEGIN
    -- Get the secret
    SELECT vs.decrypted_secret INTO v_secret
    FROM control_plane.secret_index si
    JOIN vault.decrypted_secrets vs ON vs.id = si.vault_id
    WHERE si.name = p_name;

    -- Log the access
    INSERT INTO control_plane.secret_access_log (
        secret_name, accessor, access_type, ip_address, user_agent, success
    ) VALUES (
        p_name, p_accessor, p_access_type, p_ip, p_user_agent, v_secret IS NOT NULL
    );

    -- Update access stats
    IF v_secret IS NOT NULL THEN
        UPDATE control_plane.secret_index
        SET last_accessed_at = now(),
            access_count = access_count + 1
        WHERE name = p_name;
    END IF;

    RETURN v_secret;
END;
$$;

-- Helper function: check if bot can access secret
CREATE OR REPLACE FUNCTION control_plane.bot_can_access_secret(
    p_bot_id text,
    p_secret_name text
)
RETURNS boolean
LANGUAGE sql
SECURITY DEFINER
SET search_path = control_plane
AS $$
    SELECT EXISTS (
        SELECT 1 FROM control_plane.bot_registry
        WHERE bot_id = p_bot_id
          AND is_active = true
          AND p_secret_name = ANY(allowed_secrets)
    );
$$;

-- Helper function: register secret in Vault and index it
CREATE OR REPLACE FUNCTION control_plane.register_secret(
    p_name text,
    p_value text,
    p_purpose text,
    p_description text DEFAULT NULL
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = vault, control_plane
AS $$
DECLARE
    v_vault_id uuid;
BEGIN
    -- Create secret in Vault
    SELECT vault.create_secret(p_value) INTO v_vault_id;

    -- Index it
    INSERT INTO control_plane.secret_index (name, purpose, description, vault_id)
    VALUES (p_name, p_purpose, p_description, v_vault_id)
    ON CONFLICT (name) DO UPDATE
    SET vault_id = v_vault_id,
        purpose = EXCLUDED.purpose,
        description = EXCLUDED.description,
        updated_at = now();

    RETURN v_vault_id;
END;
$$;

-- Public wrapper for get_secret (for use from supabase-js RPC)
CREATE OR REPLACE FUNCTION public.control_plane_get_secret(p_name text)
RETURNS text
LANGUAGE sql
SECURITY DEFINER
SET search_path = public, vault, control_plane
AS $$
    SELECT control_plane.get_secret(p_name);
$$;

-- Public wrapper for get_secret_logged
CREATE OR REPLACE FUNCTION public.control_plane_get_secret_logged(
    p_name text,
    p_accessor text,
    p_access_type text DEFAULT 'read',
    p_ip inet DEFAULT NULL,
    p_user_agent text DEFAULT NULL
)
RETURNS text
LANGUAGE sql
SECURITY DEFINER
SET search_path = public, vault, control_plane
AS $$
    SELECT control_plane.get_secret_logged(p_name, p_accessor, p_access_type, p_ip, p_user_agent);
$$;

-- Revoke public access
REVOKE ALL ON SCHEMA control_plane FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA control_plane FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA control_plane FROM PUBLIC;
REVOKE ALL ON FUNCTION public.control_plane_get_secret(text) FROM PUBLIC;
REVOKE ALL ON FUNCTION public.control_plane_get_secret_logged(text, text, text, inet, text) FROM PUBLIC;

-- Grant to postgres (service role)
GRANT USAGE ON SCHEMA control_plane TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA control_plane TO postgres;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA control_plane TO postgres;
GRANT EXECUTE ON FUNCTION public.control_plane_get_secret(text) TO postgres;
GRANT EXECUTE ON FUNCTION public.control_plane_get_secret_logged(text, text, text, inet, text) TO postgres;

-- Link to ops.secret_registry if it exists (for unified tracking)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'ops' AND table_name = 'secret_registry') THEN
        -- Create view joining both registries
        CREATE OR REPLACE VIEW control_plane.unified_secrets AS
        SELECT
            si.name,
            si.purpose,
            si.description,
            'vault' as storage_type,
            si.last_accessed_at,
            si.access_count,
            si.created_at,
            si.updated_at
        FROM control_plane.secret_index si
        UNION ALL
        SELECT
            sr.secret_name as name,
            'ops_registry' as purpose,
            sr.notes as description,
            'env_var' as storage_type,
            sr.last_used_at as last_accessed_at,
            0 as access_count,
            sr.last_updated_at as created_at,
            sr.last_updated_at as updated_at
        FROM ops.secret_registry sr
        WHERE NOT EXISTS (
            SELECT 1 FROM control_plane.secret_index si2
            WHERE si2.name = sr.secret_name
        );
    END IF;
END $$;

-- Seed initial bot registry entries
INSERT INTO control_plane.bot_registry (bot_id, display_name, description, bot_type, allowed_secrets)
VALUES
    ('bugbot', 'BugBot', 'AI SRE & debugging assistant', 'sre',
     ARRAY['DIGITALOCEAN_API_TOKEN', 'OPENAI_API_KEY', 'SUPABASE_SERVICE_ROLE_KEY', 'SENTRY_DSN']),
    ('vercel-bot', 'Vercel Bot', 'Deployment SRE', 'deployment',
     ARRAY['VERCEL_API_TOKEN', 'OPENAI_API_KEY', 'GITHUB_TOKEN']),
    ('do-infra-bot', 'DO Infra Bot', 'DigitalOcean infrastructure automation', 'infra',
     ARRAY['DIGITALOCEAN_API_TOKEN', 'DO_SPACES_ACCESS_KEY', 'DO_SPACES_SECRET_KEY']),
    ('n8n-orchestrator', 'n8n Orchestrator', 'Workflow automation bot', 'general',
     ARRAY['SUPABASE_SERVICE_ROLE_KEY', 'N8N_API_KEY'])
ON CONFLICT (bot_id) DO UPDATE
SET allowed_secrets = EXCLUDED.allowed_secrets,
    updated_at = now();

COMMENT ON SCHEMA control_plane IS 'AI Control Plane - centralized secret management and bot orchestration';
COMMENT ON TABLE control_plane.secret_index IS 'Maps logical secret names to Supabase Vault IDs';
COMMENT ON TABLE control_plane.secret_access_log IS 'Audit trail for secret access';
COMMENT ON TABLE control_plane.bot_registry IS 'Registry of control plane bots and their permissions';
COMMENT ON TABLE control_plane.bot_execution_log IS 'Execution history for bot operations';
