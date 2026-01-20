-- =====================================================
-- Infra Memory Job - Knowledge Graph Schema
-- =====================================================
-- Purpose: Store infrastructure discovery data as knowledge graph
-- Usage: psql "$POSTGRES_URL" -f packages/db/sql/infra_schema.sql
-- =====================================================

-- Create infra schema
CREATE SCHEMA IF NOT EXISTS infra;

-- =====================================================
-- Table: infra.sources
-- Purpose: Track discovery source metadata
-- =====================================================
CREATE TABLE IF NOT EXISTS infra.sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    last_discovered_at TIMESTAMPTZ,
    discovery_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE infra.sources IS 'Discovery source metadata (vercel, supabase, odoo, digitalocean, docker)';
COMMENT ON COLUMN infra.sources.id IS 'Source identifier (e.g., "vercel", "supabase")';
COMMENT ON COLUMN infra.sources.discovery_count IS 'Number of successful discovery runs';
COMMENT ON COLUMN infra.sources.metadata IS 'Source-specific config (API endpoints, filters, etc.)';

-- =====================================================
-- Table: infra.nodes
-- Purpose: Store infrastructure components (projects, databases, services)
-- =====================================================
CREATE TABLE IF NOT EXISTS infra.nodes (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    kind TEXT NOT NULL,
    key TEXT NOT NULL,
    name TEXT NOT NULL,
    props JSONB DEFAULT '{}',
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_source FOREIGN KEY (source) REFERENCES infra.sources(id) ON DELETE CASCADE
);

COMMENT ON TABLE infra.nodes IS 'Infrastructure components (projects, services, databases, etc.)';
COMMENT ON COLUMN infra.nodes.id IS 'Stable ID format: <source>:<kind>:<key>';
COMMENT ON COLUMN infra.nodes.source IS 'Discovery source (vercel, supabase, odoo, digitalocean, docker)';
COMMENT ON COLUMN infra.nodes.kind IS 'Component type (project, database, service, etc.)';
COMMENT ON COLUMN infra.nodes.key IS 'Source-specific unique key';
COMMENT ON COLUMN infra.nodes.name IS 'Human-readable name';
COMMENT ON COLUMN infra.nodes.props IS 'Component-specific properties';

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_nodes_source ON infra.nodes(source);
CREATE INDEX IF NOT EXISTS idx_nodes_kind ON infra.nodes(kind);
CREATE INDEX IF NOT EXISTS idx_nodes_discovered_at ON infra.nodes(discovered_at DESC);
CREATE INDEX IF NOT EXISTS idx_nodes_props_gin ON infra.nodes USING GIN(props);

-- =====================================================
-- Table: infra.edges
-- Purpose: Store relationships between infrastructure components
-- =====================================================
CREATE TABLE IF NOT EXISTS infra.edges (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    from_id TEXT NOT NULL,
    to_id TEXT NOT NULL,
    type TEXT NOT NULL,
    props JSONB DEFAULT '{}',
    discovered_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_edge_source FOREIGN KEY (source) REFERENCES infra.sources(id) ON DELETE CASCADE,
    CONSTRAINT fk_edge_from FOREIGN KEY (from_id) REFERENCES infra.nodes(id) ON DELETE CASCADE,
    CONSTRAINT fk_edge_to FOREIGN KEY (to_id) REFERENCES infra.nodes(id) ON DELETE CASCADE
);

COMMENT ON TABLE infra.edges IS 'Relationships between infrastructure components';
COMMENT ON COLUMN infra.edges.id IS 'Edge ID format: <from_id>→<to_id>';
COMMENT ON COLUMN infra.edges.source IS 'Discovery source that detected this relationship';
COMMENT ON COLUMN infra.edges.type IS 'Relationship type (OWNS, USES_INTEGRATION, DEPENDS_ON, etc.)';
COMMENT ON COLUMN infra.edges.props IS 'Relationship-specific properties';

-- Indexes for efficient graph traversal
CREATE INDEX IF NOT EXISTS idx_edges_from_id ON infra.edges(from_id);
CREATE INDEX IF NOT EXISTS idx_edges_to_id ON infra.edges(to_id);
CREATE INDEX IF NOT EXISTS idx_edges_type ON infra.edges(type);
CREATE INDEX IF NOT EXISTS idx_edges_source ON infra.edges(source);

-- =====================================================
-- Table: infra.snapshots
-- Purpose: Store point-in-time snapshots of knowledge graph
-- =====================================================
CREATE TABLE IF NOT EXISTS infra.snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_at TIMESTAMPTZ DEFAULT NOW(),
    sources TEXT[] NOT NULL,
    node_count INTEGER NOT NULL,
    edge_count INTEGER NOT NULL,
    graph_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE infra.snapshots IS 'Point-in-time knowledge graph snapshots';
COMMENT ON COLUMN infra.snapshots.sources IS 'Array of source IDs included in snapshot';
COMMENT ON COLUMN infra.snapshots.graph_data IS 'Complete graph (nodes + edges + metadata)';
COMMENT ON COLUMN infra.snapshots.metadata IS 'Snapshot metadata (triggers, changes, etc.)';

-- Index for efficient snapshot retrieval
CREATE INDEX IF NOT EXISTS idx_snapshots_snapshot_at ON infra.snapshots(snapshot_at DESC);

-- =====================================================
-- Function: update_updated_at_timestamp()
-- Purpose: Auto-update updated_at column on row modification
-- =====================================================
CREATE OR REPLACE FUNCTION infra.update_updated_at_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_sources_timestamp
    BEFORE UPDATE ON infra.sources
    FOR EACH ROW
    EXECUTE FUNCTION infra.update_updated_at_timestamp();

CREATE TRIGGER update_nodes_timestamp
    BEFORE UPDATE ON infra.nodes
    FOR EACH ROW
    EXECUTE FUNCTION infra.update_updated_at_timestamp();

CREATE TRIGGER update_edges_timestamp
    BEFORE UPDATE ON infra.edges
    FOR EACH ROW
    EXECUTE FUNCTION infra.update_updated_at_timestamp();

-- =====================================================
-- RLS Policies (Security)
-- =====================================================
-- Enable RLS on all tables
ALTER TABLE infra.sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE infra.nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE infra.edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE infra.snapshots ENABLE ROW LEVEL SECURITY;

-- Service role has full access
CREATE POLICY "Service role has full access to sources"
    ON infra.sources
    FOR ALL
    TO service_role
    USING (true);

CREATE POLICY "Service role has full access to nodes"
    ON infra.nodes
    FOR ALL
    TO service_role
    USING (true);

CREATE POLICY "Service role has full access to edges"
    ON infra.edges
    FOR ALL
    TO service_role
    USING (true);

CREATE POLICY "Service role has full access to snapshots"
    ON infra.snapshots
    FOR ALL
    TO service_role
    USING (true);

-- Authenticated users have read-only access
CREATE POLICY "Authenticated users can read sources"
    ON infra.sources
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can read nodes"
    ON infra.nodes
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can read edges"
    ON infra.edges
    FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Authenticated users can read snapshots"
    ON infra.snapshots
    FOR SELECT
    TO authenticated
    USING (true);

-- =====================================================
-- Seed Initial Sources
-- =====================================================
INSERT INTO infra.sources (id, name, description, metadata) VALUES
    ('vercel', 'Vercel', 'Vercel projects and integrations', '{"api_endpoint": "https://api.vercel.com", "team": "insightpulseai"}'),
    ('supabase', 'Supabase', 'Supabase databases and functions', '{"project_ref": "spdtwktxdalcfigzeqrz"}'),
    ('odoo', 'Odoo', 'Odoo modules and models', '{"version": "18.0", "db": "production"}'),
    ('digitalocean', 'DigitalOcean', 'DigitalOcean droplets and apps', '{"project_id": "29cde7a1-8280-46ad-9fdf-dea7b21a7825"}'),
    ('docker', 'Docker', 'Docker containers and services', '{"compose_files": ["docker-compose.yml", "deploy/docker-compose.prod.yml"]}')
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    metadata = EXCLUDED.metadata,
    updated_at = NOW();

-- =====================================================
-- Verification Query
-- =====================================================
-- Verify schema creation
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'infra'
ORDER BY tablename;

-- Verify sources seeded
SELECT id, name, description FROM infra.sources ORDER BY id;
