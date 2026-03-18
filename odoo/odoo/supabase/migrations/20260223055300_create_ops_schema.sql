-- Create operations schema
CREATE SCHEMA IF NOT EXISTS ops;

-- Enable RLS by default on the schema if possible (or per table)
-- Note: schema level RLS isn't global in Postgres but we will apply to tables.

-- Environments
CREATE TABLE IF NOT EXISTS ops.environments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL, -- e.g. 'prod', 'stage', 'dev'
    type TEXT NOT NULL DEFAULT 'development', -- 'production', 'staging', 'development'
    url TEXT,
    branch TEXT,
    status TEXT DEFAULT 'online', -- 'online', 'maintenance', 'offline'
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Deployments
CREATE TABLE IF NOT EXISTS ops.deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    environment_id UUID REFERENCES ops.environments(id),
    sha TEXT NOT NULL,
    branch TEXT,
    state TEXT DEFAULT 'queued', -- 'queued', 'building', 'success', 'failure', 'rolled_back'
    author TEXT,
    msg TEXT,
    duration INTEGER, -- in seconds
    artifacts_json JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    finished_at TIMESTAMPTZ
);

-- Failures / Incident Tracking
CREATE TABLE IF NOT EXISTS ops.failures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    environment_id UUID REFERENCES ops.environments(id),
    code TEXT NOT NULL, -- e.g. 'ERR_RPC_TIMEOUT'
    component TEXT, -- e.g. 'odoo', 'superset', 'n8n'
    severity TEXT DEFAULT 'warning', -- 'critical', 'warning', 'info'
    message TEXT NOT NULL,
    stack TEXT,
    remediation TEXT,
    resolved BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Sync Checkpoints (SOR ↔ SSOT)
CREATE TABLE IF NOT EXISTS ops.sync_checkpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model TEXT NOT NULL, -- e.g. 'account.move'
    last_sync_at TIMESTAMPTZ NOT NULL,
    record_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'synced', -- 'synced', 'stale', 'error'
    error_msg TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Structured Logs
CREATE TABLE IF NOT EXISTS ops.logs (
    id BIGSERIAL PRIMARY KEY,
    environment_id UUID REFERENCES ops.environments(id),
    level TEXT DEFAULT 'info',
    component TEXT,
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS
ALTER TABLE ops.environments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.deployments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.failures ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.sync_checkpoints ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies (Example: Authenticated users can read, service_role can do anything)
-- Read policy for all tables
CREATE POLICY "Enable read access for authenticated users" ON ops.environments FOR SELECT TO authenticated USING (true);
CREATE POLICY "Enable read access for authenticated users" ON ops.deployments FOR SELECT TO authenticated USING (true);
CREATE POLICY "Enable read access for authenticated users" ON ops.failures FOR SELECT TO authenticated USING (true);
CREATE POLICY "Enable read access for authenticated users" ON ops.sync_checkpoints FOR SELECT TO authenticated USING (true);
CREATE POLICY "Enable read access for authenticated users" ON ops.logs FOR SELECT TO authenticated USING (true);

-- Full access for service_role
CREATE POLICY "Enable all access for service_role" ON ops.environments USING (auth.role() = 'service_role');
CREATE POLICY "Enable all access for service_role" ON ops.deployments USING (auth.role() = 'service_role');
CREATE POLICY "Enable all access for service_role" ON ops.failures USING (auth.role() = 'service_role');
CREATE POLICY "Enable all access for service_role" ON ops.sync_checkpoints USING (auth.role() = 'service_role');
CREATE POLICY "Enable all access for service_role" ON ops.logs USING (auth.role() = 'service_role');

-- Seed initial environments
INSERT INTO ops.environments (slug, type, url, branch) VALUES
('prod', 'production', 'https://erp.insightpulseai.com', 'main'),
('stage', 'staging', 'https://stage-erp.insightpulseai.com', 'develop'),
('dev', 'development', 'http://localhost:8069', 'feat/ops-console')
ON CONFLICT (slug) DO NOTHING;
