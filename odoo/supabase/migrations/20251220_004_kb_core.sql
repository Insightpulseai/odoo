-- =============================================================================
-- KNOWLEDGE HUB: CORE SCHEMA
-- =============================================================================
-- Core tables for the Knowledge Hub platform:
-- - kb.spaces: Workspace containers
-- - kb.artifacts: Canonical artifact records
-- - kb.versions: Immutable version snapshots
-- =============================================================================

-- Create kb schema
CREATE SCHEMA IF NOT EXISTS kb;

-- =============================================================================
-- ARTIFACT TYPE ENUM
-- =============================================================================

CREATE TYPE kb.artifact_type AS ENUM (
    'doc_page',
    'spec_bundle',
    'runbook',
    'notebook',
    'notebook_block',
    'dataset_contract',
    'api_spec',
    'evidence_pack',
    'agent_output',
    'journey',
    'glossary_term'
);

CREATE TYPE kb.artifact_status AS ENUM (
    'draft',
    'review',
    'published',
    'deprecated',
    'archived'
);

CREATE TYPE kb.visibility AS ENUM (
    'public',
    'workspace',
    'private'
);

-- =============================================================================
-- SPACES (Workspace Containers)
-- =============================================================================

CREATE TABLE kb.spaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    parent_id UUID REFERENCES kb.spaces(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    visibility kb.visibility NOT NULL DEFAULT 'workspace',
    settings JSONB DEFAULT '{}',
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_space_slug UNIQUE (tenant_id, parent_id, slug)
);

CREATE INDEX idx_spaces_tenant ON kb.spaces(tenant_id);
CREATE INDEX idx_spaces_parent ON kb.spaces(parent_id);

-- RLS for spaces
ALTER TABLE kb.spaces ENABLE ROW LEVEL SECURITY;

CREATE POLICY spaces_tenant_isolation ON kb.spaces
    USING (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

CREATE POLICY spaces_insert ON kb.spaces
    FOR INSERT WITH CHECK (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

-- =============================================================================
-- ARTIFACTS (Canonical Records)
-- =============================================================================

CREATE TABLE kb.artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    space_id UUID REFERENCES kb.spaces(id) ON DELETE SET NULL,
    type kb.artifact_type NOT NULL,
    slug TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    tags TEXT[] DEFAULT '{}',
    status kb.artifact_status NOT NULL DEFAULT 'draft',
    visibility kb.visibility NOT NULL DEFAULT 'workspace',
    canonical_ref TEXT,  -- git://repo/path@sha, odoo://model/id, https://url
    latest_version_id UUID,  -- Updated after version insert
    metadata JSONB DEFAULT '{}',
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_artifact_slug UNIQUE (tenant_id, space_id, slug)
);

CREATE INDEX idx_artifacts_tenant ON kb.artifacts(tenant_id);
CREATE INDEX idx_artifacts_space ON kb.artifacts(space_id);
CREATE INDEX idx_artifacts_type ON kb.artifacts(type);
CREATE INDEX idx_artifacts_status ON kb.artifacts(status);
CREATE INDEX idx_artifacts_tags ON kb.artifacts USING GIN (tags);
CREATE INDEX idx_artifacts_canonical ON kb.artifacts(canonical_ref);
CREATE INDEX idx_artifacts_tenant_status ON kb.artifacts(tenant_id, status);

-- RLS for artifacts
ALTER TABLE kb.artifacts ENABLE ROW LEVEL SECURITY;

CREATE POLICY artifacts_tenant_isolation ON kb.artifacts
    USING (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

CREATE POLICY artifacts_visibility ON kb.artifacts
    USING (
        visibility = 'public'
        OR (visibility = 'workspace' AND space_id IN (
            SELECT id FROM kb.spaces WHERE tenant_id = (auth.jwt()->>'tenant_id')::uuid
        ))
        OR (visibility = 'private' AND created_by = auth.jwt()->>'sub')
    );

CREATE POLICY artifacts_insert ON kb.artifacts
    FOR INSERT WITH CHECK (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

-- =============================================================================
-- VERSIONS (Immutable Snapshots)
-- =============================================================================

CREATE TABLE kb.versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    artifact_id UUID NOT NULL REFERENCES kb.artifacts(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    content_hash TEXT NOT NULL,  -- SHA-256 of content
    content_md TEXT,  -- Markdown content (if inline)
    content_text TEXT,  -- Plain text for FTS
    content_tsvector TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', COALESCE(content_text, ''))) STORED,
    source_uri TEXT,  -- s3://..., git://..., odoo://...
    render_uri TEXT,  -- Cached rendered HTML in S3
    word_count INTEGER,
    is_breaking BOOLEAN DEFAULT false,
    is_deprecated BOOLEAN DEFAULT false,
    deprecation_reason TEXT,
    successor_version_id UUID REFERENCES kb.versions(id),
    metadata JSONB DEFAULT '{}',
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT unique_artifact_version UNIQUE (artifact_id, version)
);

CREATE INDEX idx_versions_tenant ON kb.versions(tenant_id);
CREATE INDEX idx_versions_artifact ON kb.versions(artifact_id);
CREATE INDEX idx_versions_hash ON kb.versions(content_hash);
CREATE INDEX idx_versions_fts ON kb.versions USING GIN (content_tsvector);
CREATE INDEX idx_versions_created ON kb.versions(created_at DESC);

-- RLS for versions
ALTER TABLE kb.versions ENABLE ROW LEVEL SECURITY;

CREATE POLICY versions_tenant_isolation ON kb.versions
    USING (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

CREATE POLICY versions_insert ON kb.versions
    FOR INSERT WITH CHECK (tenant_id = (auth.jwt()->>'tenant_id')::uuid);

-- Add FK for latest_version after versions table exists
ALTER TABLE kb.artifacts
    ADD CONSTRAINT fk_latest_version
    FOREIGN KEY (latest_version_id) REFERENCES kb.versions(id);

-- =============================================================================
-- TRIGGER: Auto-update latest_version_id
-- =============================================================================

CREATE OR REPLACE FUNCTION kb.update_latest_version()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE kb.artifacts
    SET latest_version_id = NEW.id, updated_at = now()
    WHERE id = NEW.artifact_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_latest_version
    AFTER INSERT ON kb.versions
    FOR EACH ROW EXECUTE FUNCTION kb.update_latest_version();

-- =============================================================================
-- TRIGGER: Auto-increment version number
-- =============================================================================

CREATE OR REPLACE FUNCTION kb.auto_version_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.version IS NULL THEN
        SELECT COALESCE(MAX(version), 0) + 1 INTO NEW.version
        FROM kb.versions
        WHERE artifact_id = NEW.artifact_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_auto_version
    BEFORE INSERT ON kb.versions
    FOR EACH ROW EXECUTE FUNCTION kb.auto_version_number();

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Get artifact with latest version
CREATE OR REPLACE FUNCTION kb.get_artifact_with_version(p_artifact_id UUID)
RETURNS TABLE(
    id UUID,
    type kb.artifact_type,
    slug TEXT,
    title TEXT,
    status kb.artifact_status,
    version INTEGER,
    content_md TEXT,
    content_hash TEXT,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id,
        a.type,
        a.slug,
        a.title,
        a.status,
        v.version,
        v.content_md,
        v.content_hash,
        v.created_at
    FROM kb.artifacts a
    JOIN kb.versions v ON v.id = a.latest_version_id
    WHERE a.id = p_artifact_id;
END;
$$ LANGUAGE plpgsql STABLE;

-- Full-text search across versions
CREATE OR REPLACE FUNCTION kb.search_content(
    p_query TEXT,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE(
    artifact_id UUID,
    title TEXT,
    slug TEXT,
    type kb.artifact_type,
    snippet TEXT,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id as artifact_id,
        a.title,
        a.slug,
        a.type,
        ts_headline('english', v.content_text, plainto_tsquery('english', p_query),
            'MaxWords=50, MinWords=20, StartSel=<mark>, StopSel=</mark>') as snippet,
        ts_rank(v.content_tsvector, plainto_tsquery('english', p_query)) as rank
    FROM kb.artifacts a
    JOIN kb.versions v ON v.id = a.latest_version_id
    WHERE v.content_tsvector @@ plainto_tsquery('english', p_query)
      AND a.status = 'published'
    ORDER BY rank DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql STABLE;

-- =============================================================================
-- SEED SAMPLE SPACES
-- =============================================================================

-- Note: In production, these would be created per-tenant
-- This is for development/testing only

DO $$
DECLARE
    sample_tenant UUID := '00000000-0000-0000-0000-000000000001';
BEGIN
    INSERT INTO kb.spaces (tenant_id, slug, title, description, visibility, created_by)
    VALUES
        (sample_tenant, 'platform', 'Platform Docs', 'Infrastructure and platform documentation', 'public', 'system'),
        (sample_tenant, 'odoo', 'Odoo Modules', 'Odoo CE and OCA module documentation', 'public', 'system'),
        (sample_tenant, 'runbooks', 'Runbooks', 'Operations playbooks and procedures', 'workspace', 'system')
    ON CONFLICT DO NOTHING;
END;
$$;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'KB Core schema created';
    RAISE NOTICE 'Tables: kb.spaces, kb.artifacts, kb.versions';
END;
$$;
