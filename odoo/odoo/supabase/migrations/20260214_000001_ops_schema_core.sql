-- Migration: OdooOps Control Plane Schema - Core Tables
-- Purpose: Create ops.* schema with core tables for projects, environments, runs, events, artifacts

-- Create ops schema
CREATE SCHEMA IF NOT EXISTS ops;

-- Projects table
CREATE TABLE IF NOT EXISTS ops.projects (
    project_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    repo_slug TEXT NOT NULL UNIQUE,
    odoo_version TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT project_id_format CHECK (project_id ~ '^[a-z0-9][a-z0-9-]*$')
);

COMMENT ON TABLE ops.projects IS 'Registered Odoo projects/instances';
COMMENT ON COLUMN ops.projects.repo_slug IS 'GitHub repo in format: org/repo';
COMMENT ON COLUMN ops.projects.odoo_version IS 'Odoo major version: 18.0, 19.0, etc.';

-- Environments table
CREATE TABLE IF NOT EXISTS ops.environments (
    env_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES ops.projects(project_id) ON DELETE CASCADE,
    env_type TEXT NOT NULL CHECK (env_type IN ('dev', 'staging', 'prod')),
    branch_pattern TEXT NOT NULL,
    db_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (project_id, env_type)
);

COMMENT ON TABLE ops.environments IS 'Environment configurations per project';
COMMENT ON COLUMN ops.environments.branch_pattern IS 'Git branch pattern: main, release/*, feature/*';
COMMENT ON COLUMN ops.environments.db_name IS 'Database name for this environment';

-- Runs table
CREATE TABLE IF NOT EXISTS ops.runs (
    run_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES ops.projects(project_id) ON DELETE CASCADE,
    env_id TEXT NOT NULL REFERENCES ops.environments(env_id) ON DELETE CASCADE,
    git_sha TEXT NOT NULL,
    git_ref TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('queued', 'claimed', 'running', 'success', 'failed', 'cancelled')),
    claimed_by TEXT,
    queued_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT run_id_format CHECK (run_id ~ '^run-[a-z0-9-]+$')
);

COMMENT ON TABLE ops.runs IS 'Build/deploy run executions';
COMMENT ON COLUMN ops.runs.claimed_by IS 'Worker/agent ID that claimed this run';
COMMENT ON COLUMN ops.runs.git_sha IS 'Full git commit SHA';
COMMENT ON COLUMN ops.runs.git_ref IS 'Git ref: branch, tag, or PR';

-- Run events table
CREATE TABLE IF NOT EXISTS ops.run_events (
    event_id TEXT PRIMARY KEY DEFAULT 'evt-' || gen_random_uuid()::text,
    run_id TEXT NOT NULL REFERENCES ops.runs(run_id) ON DELETE CASCADE,
    level TEXT NOT NULL CHECK (level IN ('debug', 'info', 'warn', 'error')),
    message TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE ops.run_events IS 'Structured event log for runs';
COMMENT ON COLUMN ops.run_events.level IS 'Log level: debug, info, warn, error';

CREATE INDEX idx_run_events_run_id ON ops.run_events(run_id, created_at DESC);
CREATE INDEX idx_run_events_level ON ops.run_events(level) WHERE level IN ('warn', 'error');

-- Artifacts table
CREATE TABLE IF NOT EXISTS ops.artifacts (
    artifact_id TEXT PRIMARY KEY DEFAULT 'art-' || gen_random_uuid()::text,
    run_id TEXT NOT NULL REFERENCES ops.runs(run_id) ON DELETE CASCADE,
    artifact_type TEXT NOT NULL CHECK (artifact_type IN ('image', 'sbom', 'logs', 'evidence', 'manifest')),
    storage_path TEXT NOT NULL,
    digest TEXT,
    size_bytes BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

COMMENT ON TABLE ops.artifacts IS 'Build artifacts (images, SBOMs, logs, evidence)';
COMMENT ON COLUMN ops.artifacts.digest IS 'SHA256 digest for images';
COMMENT ON COLUMN ops.artifacts.storage_path IS 'Storage location: GHCR URL, S3 path, etc.';

CREATE INDEX idx_artifacts_run_id ON ops.artifacts(run_id);
CREATE INDEX idx_artifacts_type ON ops.artifacts(artifact_type);

-- Indexes for performance
CREATE INDEX idx_projects_repo_slug ON ops.projects(repo_slug);
CREATE INDEX idx_environments_project_id ON ops.environments(project_id);
CREATE INDEX idx_runs_project_id ON ops.runs(project_id, created_at DESC);
CREATE INDEX idx_runs_status ON ops.runs(status) WHERE status IN ('queued', 'running');
CREATE INDEX idx_runs_env_id ON ops.runs(env_id, created_at DESC);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION ops.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER projects_updated_at BEFORE UPDATE ON ops.projects
    FOR EACH ROW EXECUTE FUNCTION ops.update_updated_at();

CREATE TRIGGER environments_updated_at BEFORE UPDATE ON ops.environments
    FOR EACH ROW EXECUTE FUNCTION ops.update_updated_at();

CREATE TRIGGER runs_updated_at BEFORE UPDATE ON ops.runs
    FOR EACH ROW EXECUTE FUNCTION ops.update_updated_at();
