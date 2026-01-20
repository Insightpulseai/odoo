-- Operations Knowledge Graph: Infrastructure Memory
-- Extends kg schema with infrastructure-specific node kinds, predicates, and discovery tracking
-- Purpose: Enable LLM agents to understand and navigate infrastructure relationships

-- =============================================================================
-- INFRASTRUCTURE NODE KINDS (Canonical)
-- =============================================================================

COMMENT ON TABLE kg.nodes IS
'Knowledge Graph entities. Infrastructure node kinds:
- droplet: DigitalOcean droplet (VM)
- managed_db: DigitalOcean managed database cluster
- supabase_project: Supabase project instance
- vercel_project: Vercel deployment project
- docker_container: Docker container instance
- docker_image: Docker image
- docker_network: Docker network
- edge_function: Supabase Edge Function
- odoo_module: Odoo module (ipai_*, OCA, CE)
- odoo_model: Odoo ORM model
- github_repo: GitHub repository
- github_workflow: GitHub Actions workflow
- schema: Database schema
- table: Database table
- api_endpoint: REST/GraphQL endpoint
- domain: DNS domain/subdomain
- secret: Vault secret reference (not the value!)
- cron_job: Scheduled job (pg_cron, GitHub Actions)
- service: Logical service grouping';

-- =============================================================================
-- INFRASTRUCTURE PREDICATES (Canonical)
-- =============================================================================

-- Create a reference table for allowed predicates (documentation only)
CREATE TABLE IF NOT EXISTS kg.predicate_catalog (
  predicate text PRIMARY KEY,
  category text NOT NULL,
  description text NOT NULL,
  inverse_predicate text,
  created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE kg.predicate_catalog IS 'Catalog of allowed edge predicates for documentation';

-- Insert canonical infrastructure predicates
INSERT INTO kg.predicate_catalog (predicate, category, description, inverse_predicate) VALUES
  -- Deployment relationships
  ('DEPLOYS_TO', 'deployment', 'Source deploys to target infrastructure', 'DEPLOYED_FROM'),
  ('DEPLOYED_FROM', 'deployment', 'Target is deployed from source', 'DEPLOYS_TO'),
  ('RUNS_ON', 'deployment', 'Service runs on infrastructure', 'HOSTS'),
  ('HOSTS', 'deployment', 'Infrastructure hosts service', 'RUNS_ON'),

  -- Data relationships
  ('USES_DB', 'data', 'Service uses database', 'DB_USED_BY'),
  ('DB_USED_BY', 'data', 'Database is used by service', 'USES_DB'),
  ('MIRRORS_TO', 'data', 'Source mirrors data to target', 'MIRRORS_FROM'),
  ('MIRRORS_FROM', 'data', 'Target receives mirrored data from source', 'MIRRORS_TO'),
  ('STORES_DATA_FOR', 'data', 'Storage stores data for service', 'DATA_STORED_IN'),

  -- Dependency relationships
  ('DEPENDS_ON', 'dependency', 'Source depends on target', 'DEPENDENCY_OF'),
  ('DEPENDENCY_OF', 'dependency', 'Target is dependency of source', 'DEPENDS_ON'),
  ('REQUIRES', 'dependency', 'Source requires target to function', 'REQUIRED_BY'),
  ('REQUIRED_BY', 'dependency', 'Target is required by source', 'REQUIRES'),

  -- Module relationships
  ('EXTENDS', 'module', 'Module extends another module', 'EXTENDED_BY'),
  ('EXTENDED_BY', 'module', 'Module is extended by another', 'EXTENDS'),
  ('INHERITS', 'module', 'Model inherits from another', 'INHERITED_BY'),
  ('INHERITED_BY', 'module', 'Model is inherited by another', 'INHERITS'),
  ('PROVIDES', 'module', 'Module provides capability', 'PROVIDED_BY'),

  -- Network relationships
  ('CONNECTS_TO', 'network', 'Source connects to target', 'CONNECTED_FROM'),
  ('EXPOSES_API', 'network', 'Service exposes API endpoint', 'API_OF'),
  ('ROUTES_TO', 'network', 'Proxy routes to backend', 'ROUTED_FROM'),

  -- Authentication relationships
  ('AUTHENTICATES', 'auth', 'Service authenticates via provider', 'AUTHENTICATES_FOR'),
  ('AUTHORIZES', 'auth', 'Policy authorizes access', 'AUTHORIZED_BY'),

  -- Integration relationships
  ('INTEGRATES_WITH', 'integration', 'Service integrates with another', NULL),
  ('SYNCS_TO', 'integration', 'Data syncs to target', 'SYNCS_FROM'),
  ('SYNCS_FROM', 'integration', 'Data syncs from source', 'SYNCS_TO'),
  ('TRIGGERS', 'integration', 'Event triggers action', 'TRIGGERED_BY'),

  -- Containment relationships
  ('CONTAINS', 'containment', 'Parent contains child', 'CONTAINED_IN'),
  ('CONTAINED_IN', 'containment', 'Child is contained in parent', 'CONTAINS'),
  ('MEMBER_OF', 'containment', 'Entity is member of group', 'HAS_MEMBER'),

  -- Ownership relationships
  ('OWNS', 'ownership', 'Entity owns resource', 'OWNED_BY'),
  ('OWNED_BY', 'ownership', 'Resource is owned by entity', 'OWNS'),
  ('MANAGED_BY', 'ownership', 'Resource is managed by entity', 'MANAGES'),
  ('MANAGES', 'ownership', 'Entity manages resource', 'MANAGED_BY')
ON CONFLICT (predicate) DO NOTHING;

-- =============================================================================
-- INFRASTRUCTURE DISCOVERY TRACKING
-- =============================================================================

CREATE TABLE IF NOT EXISTS kg.discovery_runs (
  run_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL,
  discovery_type text NOT NULL,  -- 'vercel', 'supabase', 'digitalocean', 'docker', 'odoo', 'github'
  status text NOT NULL DEFAULT 'running', -- 'running', 'completed', 'failed'
  nodes_discovered int DEFAULT 0,
  edges_discovered int DEFAULT 0,
  error_message text,
  started_at timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz,
  metadata jsonb DEFAULT '{}'::jsonb
);

COMMENT ON TABLE kg.discovery_runs IS 'Tracks infrastructure discovery job executions';

CREATE INDEX IF NOT EXISTS idx_discovery_runs_type_status
ON kg.discovery_runs(tenant_id, discovery_type, status);

CREATE INDEX IF NOT EXISTS idx_discovery_runs_started
ON kg.discovery_runs(started_at DESC);

-- =============================================================================
-- INFRASTRUCTURE VIEWS
-- =============================================================================

-- View: All infrastructure nodes
CREATE OR REPLACE VIEW kg.v_infrastructure_nodes AS
SELECT
  n.node_id,
  n.tenant_id,
  n.kind,
  n.key,
  n.label,
  n.attrs,
  n.created_at,
  n.updated_at,
  CASE
    WHEN ne.embedding IS NOT NULL THEN true
    ELSE false
  END as has_embedding
FROM kg.nodes n
LEFT JOIN kg.node_embeddings ne ON n.node_id = ne.node_id
WHERE n.kind IN (
  'droplet', 'managed_db', 'supabase_project', 'vercel_project',
  'docker_container', 'docker_image', 'docker_network',
  'edge_function', 'odoo_module', 'odoo_model',
  'github_repo', 'github_workflow', 'schema', 'table',
  'api_endpoint', 'domain', 'cron_job', 'service'
);

COMMENT ON VIEW kg.v_infrastructure_nodes IS 'All infrastructure-related nodes in the knowledge graph';

-- View: Service dependencies
CREATE OR REPLACE VIEW kg.v_service_dependencies AS
SELECT
  src.label as service,
  src.kind as service_kind,
  e.predicate,
  dst.label as dependency,
  dst.kind as dependency_kind,
  e.weight,
  e.evidence_count
FROM kg.edges e
JOIN kg.nodes src ON e.src_node_id = src.node_id
JOIN kg.nodes dst ON e.dst_node_id = dst.node_id
WHERE e.predicate IN ('DEPENDS_ON', 'REQUIRES', 'USES_DB', 'CONNECTS_TO', 'INTEGRATES_WITH')
ORDER BY src.label, e.predicate;

COMMENT ON VIEW kg.v_service_dependencies IS 'Service dependency graph for impact analysis';

-- View: Deployment topology
CREATE OR REPLACE VIEW kg.v_deployment_topology AS
SELECT
  src.label as source,
  src.kind as source_kind,
  e.predicate,
  dst.label as target,
  dst.kind as target_kind,
  src.attrs as source_attrs,
  dst.attrs as target_attrs
FROM kg.edges e
JOIN kg.nodes src ON e.src_node_id = src.node_id
JOIN kg.nodes dst ON e.dst_node_id = dst.node_id
WHERE e.predicate IN ('DEPLOYS_TO', 'RUNS_ON', 'HOSTS', 'ROUTES_TO')
ORDER BY src.label;

COMMENT ON VIEW kg.v_deployment_topology IS 'Deployment relationships showing where services run';

-- View: Module dependency graph
CREATE OR REPLACE VIEW kg.v_module_graph AS
SELECT
  src.label as module,
  src.attrs->>'version' as version,
  e.predicate,
  dst.label as dependency,
  dst.attrs->>'version' as dep_version
FROM kg.edges e
JOIN kg.nodes src ON e.src_node_id = src.node_id
JOIN kg.nodes dst ON e.dst_node_id = dst.node_id
WHERE src.kind = 'odoo_module'
  AND dst.kind = 'odoo_module'
  AND e.predicate IN ('DEPENDS_ON', 'EXTENDS', 'REQUIRES')
ORDER BY src.label, e.predicate;

COMMENT ON VIEW kg.v_module_graph IS 'Odoo module dependency graph';

-- View: Discovery run history
CREATE OR REPLACE VIEW kg.v_discovery_history AS
SELECT
  run_id,
  discovery_type,
  status,
  nodes_discovered,
  edges_discovered,
  started_at,
  completed_at,
  EXTRACT(EPOCH FROM (COALESCE(completed_at, now()) - started_at)) as duration_seconds,
  error_message
FROM kg.discovery_runs
ORDER BY started_at DESC;

COMMENT ON VIEW kg.v_discovery_history IS 'Infrastructure discovery job history';

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Function: Get infrastructure node by key
CREATE OR REPLACE FUNCTION kg.get_infra_node(
  p_tenant uuid,
  p_kind text,
  p_key text
)
RETURNS TABLE(node_id uuid, label text, attrs jsonb, updated_at timestamptz)
LANGUAGE sql STABLE AS $$
  SELECT node_id, label, attrs, updated_at
  FROM kg.nodes
  WHERE tenant_id = p_tenant
    AND kind = p_kind
    AND key = p_key
  LIMIT 1;
$$;

COMMENT ON FUNCTION kg.get_infra_node IS 'Get infrastructure node by kind and key';

-- Function: Find all paths between two nodes (BFS, max 5 hops)
CREATE OR REPLACE FUNCTION kg.find_paths(
  p_tenant uuid,
  p_start uuid,
  p_end uuid,
  p_max_depth int DEFAULT 5
)
RETURNS TABLE(path_depth int, path_nodes uuid[], path_predicates text[])
LANGUAGE sql STABLE AS $$
WITH RECURSIVE paths AS (
  -- Base case: start node
  SELECT
    1 AS depth,
    ARRAY[e.src_node_id, e.dst_node_id] AS nodes,
    ARRAY[e.predicate] AS predicates,
    e.dst_node_id AS current_node
  FROM kg.edges e
  WHERE e.tenant_id = p_tenant
    AND e.src_node_id = p_start

  UNION ALL

  -- Recursive case: extend path
  SELECT
    p.depth + 1,
    p.nodes || e.dst_node_id,
    p.predicates || e.predicate,
    e.dst_node_id
  FROM paths p
  JOIN kg.edges e ON e.src_node_id = p.current_node
  WHERE e.tenant_id = p_tenant
    AND p.depth < p_max_depth
    AND NOT e.dst_node_id = ANY(p.nodes)  -- Avoid cycles
)
SELECT depth, nodes, predicates
FROM paths
WHERE current_node = p_end
ORDER BY depth;
$$;

COMMENT ON FUNCTION kg.find_paths IS 'Find all paths between two nodes (BFS with cycle detection)';

-- Function: Impact analysis (what breaks if node fails)
CREATE OR REPLACE FUNCTION kg.impact_analysis(
  p_tenant uuid,
  p_node_id uuid,
  p_max_depth int DEFAULT 3
)
RETURNS TABLE(
  depth int,
  impacted_node_id uuid,
  impacted_kind text,
  impacted_label text,
  via_predicate text
)
LANGUAGE sql STABLE AS $$
WITH RECURSIVE impact AS (
  -- Base case: direct dependents
  SELECT
    1 AS depth,
    e.src_node_id AS impacted,
    e.predicate
  FROM kg.edges e
  WHERE e.tenant_id = p_tenant
    AND e.dst_node_id = p_node_id
    AND e.predicate IN ('DEPENDS_ON', 'REQUIRES', 'USES_DB', 'CONNECTS_TO')

  UNION ALL

  -- Recursive case: transitive dependents
  SELECT
    i.depth + 1,
    e.src_node_id,
    e.predicate
  FROM impact i
  JOIN kg.edges e ON e.dst_node_id = i.impacted
  WHERE e.tenant_id = p_tenant
    AND i.depth < p_max_depth
    AND e.predicate IN ('DEPENDS_ON', 'REQUIRES', 'USES_DB', 'CONNECTS_TO')
)
SELECT DISTINCT
  i.depth,
  i.impacted AS impacted_node_id,
  n.kind AS impacted_kind,
  n.label AS impacted_label,
  i.predicate AS via_predicate
FROM impact i
JOIN kg.nodes n ON n.node_id = i.impacted
ORDER BY i.depth, n.label;
$$;

COMMENT ON FUNCTION kg.impact_analysis IS 'Analyze what services would be impacted if a node fails';

-- Function: Record discovery run
CREATE OR REPLACE FUNCTION kg.start_discovery_run(
  p_tenant uuid,
  p_discovery_type text,
  p_metadata jsonb DEFAULT '{}'::jsonb
)
RETURNS uuid
LANGUAGE plpgsql AS $$
DECLARE
  v_run_id uuid;
BEGIN
  INSERT INTO kg.discovery_runs (tenant_id, discovery_type, metadata)
  VALUES (p_tenant, p_discovery_type, p_metadata)
  RETURNING run_id INTO v_run_id;

  RETURN v_run_id;
END;
$$;

-- Function: Complete discovery run
CREATE OR REPLACE FUNCTION kg.complete_discovery_run(
  p_run_id uuid,
  p_nodes_discovered int,
  p_edges_discovered int,
  p_error_message text DEFAULT NULL
)
RETURNS void
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE kg.discovery_runs SET
    status = CASE WHEN p_error_message IS NULL THEN 'completed' ELSE 'failed' END,
    nodes_discovered = p_nodes_discovered,
    edges_discovered = p_edges_discovered,
    error_message = p_error_message,
    completed_at = now()
  WHERE run_id = p_run_id;
END;
$$;

-- =============================================================================
-- CRON JOB FOR PERIODIC DISCOVERY
-- =============================================================================

-- Note: The actual discovery logic runs as Edge Functions triggered by pg_cron
-- This just sets up the cron schedule entry

-- Create extension if not exists
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule infrastructure discovery every 6 hours
-- (Actual function call will be made by Edge Function polling this schedule)
DO $$
BEGIN
  -- Check if cron job exists before creating
  IF NOT EXISTS (
    SELECT 1 FROM cron.job WHERE jobname = 'infra_discovery_trigger'
  ) THEN
    PERFORM cron.schedule(
      'infra_discovery_trigger',
      '0 */6 * * *',  -- Every 6 hours
      $$SELECT pg_notify('infra_discovery', '{"type": "scheduled"}')$$
    );
  END IF;
END $$;

-- =============================================================================
-- RLS FOR NEW TABLES
-- =============================================================================

ALTER TABLE kg.discovery_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE kg.predicate_catalog ENABLE ROW LEVEL SECURITY;

-- Service role can do everything
CREATE POLICY "service_role_all" ON kg.discovery_runs FOR ALL
TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all" ON kg.predicate_catalog FOR ALL
TO service_role USING (true) WITH CHECK (true);

-- Authenticated users see own tenant discovery runs
CREATE POLICY "tenant_isolation" ON kg.discovery_runs FOR ALL
TO authenticated
USING (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid)
WITH CHECK (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);

-- Predicate catalog is readable by all
CREATE POLICY "read_all" ON kg.predicate_catalog FOR SELECT
TO authenticated USING (true);

-- =============================================================================
-- GRANTS
-- =============================================================================

GRANT USAGE ON SCHEMA kg TO authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA kg TO service_role;
GRANT SELECT ON ALL TABLES IN SCHEMA kg TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA kg TO authenticated, service_role;
