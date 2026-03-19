-- Knowledge Base Schema
-- Replaces: Odoo Knowledge (Enterprise)

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Spaces (top-level containers)
CREATE TABLE IF NOT EXISTS kb_spaces (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    slug TEXT UNIQUE NOT NULL,
    icon TEXT DEFAULT '📚',
    owner_id UUID REFERENCES auth.users(id),
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Artifacts (documents, processes, rules, etc.)
CREATE TABLE IF NOT EXISTS kb_artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    space_id UUID REFERENCES kb_spaces(id) ON DELETE CASCADE,
    kind TEXT NOT NULL CHECK (kind IN ('process', 'data_model', 'business_rule', 'glossary', 'faq', 'runbook', 'architecture')),
    title TEXT NOT NULL,
    slug TEXT NOT NULL,
    content TEXT,
    content_format TEXT DEFAULT 'markdown' CHECK (content_format IN ('markdown', 'html', 'json')),
    personas TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'published', 'archived')),
    version INT DEFAULT 1,
    created_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    published_at TIMESTAMPTZ,
    UNIQUE(space_id, slug)
);

-- Catalog (intent-based indexing for search)
CREATE TABLE IF NOT EXISTS kb_catalog (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    artifact_id UUID REFERENCES kb_artifacts(id) ON DELETE CASCADE,
    intents TEXT[] DEFAULT '{}',
    systems TEXT[] DEFAULT '{}',
    sla_hours INT,
    priority INT DEFAULT 50,
    search_vector TSVECTOR,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Lineage (relationships between artifacts)
CREATE TABLE IF NOT EXISTS kb_lineage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES kb_artifacts(id) ON DELETE CASCADE,
    target_id UUID REFERENCES kb_artifacts(id) ON DELETE CASCADE,
    relationship TEXT NOT NULL CHECK (relationship IN ('references', 'implements', 'derived_from', 'supersedes', 'related')),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(source_id, target_id, relationship)
);

-- Audit log
CREATE TABLE IF NOT EXISTS kb_audit (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT NOT NULL CHECK (entity_type IN ('space', 'artifact', 'catalog')),
    entity_id UUID NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('created', 'updated', 'deleted', 'published', 'archived')),
    changed_by UUID REFERENCES auth.users(id),
    change_summary JSONB,
    previous_state JSONB,
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_kb_artifacts_space ON kb_artifacts(space_id);
CREATE INDEX idx_kb_artifacts_kind ON kb_artifacts(kind);
CREATE INDEX idx_kb_artifacts_status ON kb_artifacts(status);
CREATE INDEX idx_kb_artifacts_personas ON kb_artifacts USING GIN(personas);
CREATE INDEX idx_kb_artifacts_tags ON kb_artifacts USING GIN(tags);
CREATE INDEX idx_kb_catalog_search ON kb_catalog USING GIN(search_vector);
CREATE INDEX idx_kb_audit_entity ON kb_audit(entity_type, entity_id);

-- Full-text search function
CREATE OR REPLACE FUNCTION kb_update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE kb_catalog
    SET search_vector = to_tsvector('english',
        COALESCE((SELECT title FROM kb_artifacts WHERE id = NEW.artifact_id), '') || ' ' ||
        COALESCE((SELECT content FROM kb_artifacts WHERE id = NEW.artifact_id), '') || ' ' ||
        COALESCE(array_to_string(NEW.intents, ' '), '')
    )
    WHERE artifact_id = NEW.artifact_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for search vector update
CREATE TRIGGER kb_catalog_search_update
AFTER INSERT OR UPDATE ON kb_catalog
FOR EACH ROW EXECUTE FUNCTION kb_update_search_vector();

-- Row Level Security
ALTER TABLE kb_spaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_catalog ENABLE ROW LEVEL SECURITY;

-- Policies (public spaces visible to all, private to owner)
CREATE POLICY "Public spaces visible to all"
    ON kb_spaces FOR SELECT
    USING (is_public = true OR owner_id = auth.uid());

CREATE POLICY "Owners can manage their spaces"
    ON kb_spaces FOR ALL
    USING (owner_id = auth.uid());

CREATE POLICY "Published artifacts in public spaces visible to all"
    ON kb_artifacts FOR SELECT
    USING (
        status = 'published' AND
        EXISTS (SELECT 1 FROM kb_spaces WHERE id = space_id AND is_public = true)
    );
