import requests
import json

token = "sbp_9aa105cc134904b74bea64212607cca42cf2d36d"
project_ref = "spdtwktxdalcfigzeqrz"

sql = """
-- MISSION: Odoo.sh x Supabase Platform Kit (Production Schema)
-- Reset for canonical alignment
DROP TABLE IF EXISTS ops.run_events CASCADE;
DROP TABLE IF EXISTS ops.runs CASCADE;
DROP TABLE IF EXISTS ops.deployments CASCADE;
DROP TABLE IF EXISTS ops.stage_clones CASCADE;
DROP TABLE IF EXISTS ops.module_versions CASCADE;
DROP TABLE IF EXISTS ops.environments CASCADE;

CREATE SCHEMA IF NOT EXISTS ops;

-- 1. Environments (Stateful Records)
CREATE TABLE ops.environments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL, -- 'prod', 'stage', 'dev'
    type TEXT NOT NULL CHECK (type IN ('production', 'staging', 'development')),
    url TEXT,
    branch_pattern TEXT, -- pattern enforced in CI
    status TEXT DEFAULT 'online',
    config JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Runs (Deterministic Execution Backbone)
CREATE TABLE ops.runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    env_id UUID REFERENCES ops.environments(id),
    kind TEXT NOT NULL, -- 'deploy', 'clone', 'backup', 'resync', 'test'
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'success', 'failed', 'cancelled')),
    initiated_by UUID REFERENCES auth.users(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Run Events (Canonical Log Truth)
CREATE TABLE ops.run_events (
    id BIGSERIAL PRIMARY KEY,
    run_id UUID REFERENCES ops.runs(id) ON DELETE CASCADE,
    level TEXT DEFAULT 'info' CHECK (level IN ('debug', 'info', 'warning', 'error', 'critical')),
    message TEXT NOT NULL,
    payload JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 4. Deployments (Odoo.sh Pattern)
CREATE TABLE ops.deployments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES ops.runs(id),
    env TEXT NOT NULL CHECK (env IN ('production', 'staging', 'development')),
    branch TEXT NOT NULL,
    commit_sha TEXT NOT NULL,
    commit_message TEXT,
    commit_author TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','running','success','warning','failed','rolled_back')),
    modules_updated TEXT[],
    artifact_id UUID, -- reference to storage or artifact record
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 5. Staging Clones
CREATE TABLE ops.stage_clones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES ops.runs(id),
    source_db TEXT NOT NULL DEFAULT 'odoo_prod',
    target_db TEXT NOT NULL DEFAULT 'odoo_stage',
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','running','success','failed')),
    dump_size_bytes BIGINT,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 6. Module Versioning
CREATE TABLE ops.module_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    module_name TEXT NOT NULL,
    version TEXT NOT NULL,
    env TEXT NOT NULL,
    manifest_hash TEXT,
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(module_name, env)
);

-- RLS & Security
ALTER TABLE ops.environments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.run_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.deployments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.stage_clones ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.module_versions ENABLE ROW LEVEL SECURITY;

-- Read policies for all authenticated users
CREATE POLICY "Enable read for all authenticated" ON ops.environments FOR SELECT TO authenticated USING (true);
CREATE POLICY "Enable read for all authenticated" ON ops.runs FOR SELECT TO authenticated USING (true);
CREATE POLICY "Enable read for all authenticated" ON ops.run_events FOR SELECT TO authenticated USING (true);
CREATE POLICY "Enable read for all authenticated" ON ops.deployments FOR SELECT TO authenticated USING (true);
CREATE POLICY "Enable read for all authenticated" ON ops.stage_clones FOR SELECT TO authenticated USING (true);
CREATE POLICY "Enable read for all authenticated" ON ops.module_versions FOR SELECT TO authenticated USING (true);

-- Admin (Jake) + Service Role full control
CREATE POLICY "Service Role full access" ON ops.environments USING (auth.role() = 'service_role');
CREATE POLICY "Service Role full access" ON ops.runs USING (auth.role() = 'service_role');
CREATE POLICY "Service Role full access" ON ops.run_events USING (auth.role() = 'service_role');
CREATE POLICY "Service Role full access" ON ops.deployments USING (auth.role() = 'service_role');
CREATE POLICY "Service Role full access" ON ops.stage_clones USING (auth.role() = 'service_role');
CREATE POLICY "Service Role full access" ON ops.module_versions USING (auth.role() = 'service_role');

-- Seed Environments
INSERT INTO ops.environments (slug, type, url, branch_pattern) VALUES
('prod', 'production', 'https://erp.insightpulseai.com', 'main'),
('stage', 'staging', 'https://stage-erp.insightpulseai.com', 'staging/*'),
('dev', 'development', 'http://localhost:8069', 'dev/*')
ON CONFLICT (slug) DO NOTHING;
"""

url = f"https://api.supabase.com/v1/projects/{project_ref}/database/query"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
payload = {"query": sql}

print(f"Applying canonical SSOT schema to {project_ref}...")
response = requests.post(url, headers=headers, json=payload)

if response.status_code == 201 or response.status_code == 200:
    print("Success: Canonical schema applied.")
else:
    print(f"Error {response.status_code}: {response.text}")
