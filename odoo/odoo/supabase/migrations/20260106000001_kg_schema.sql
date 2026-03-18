-- Knowledge Graph Schema for Auto-Claude Framework
-- Provides entity relationships, evidence provenance, and semantic search

-- Create KG schema
CREATE SCHEMA IF NOT EXISTS kg;

-- =============================================================================
-- ENTITIES (Nodes)
-- =============================================================================

CREATE TABLE IF NOT EXISTS kg.nodes (
  node_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL,
  kind text NOT NULL,              -- e.g. person, org, brand, sku, invoice, project, task, doc, module
  key text NOT NULL,               -- natural key within kind (e.g. "brand:alaska", "module:ipai_finance_ppm")
  label text NOT NULL,
  attrs jsonb NOT NULL DEFAULT '{}'::jsonb,
  embedding_updated_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, kind, key)
);

COMMENT ON TABLE kg.nodes IS 'Knowledge Graph entities - any trackable object in the system';
COMMENT ON COLUMN kg.nodes.kind IS 'Entity type: person, org, brand, sku, invoice, project, task, doc, module, skill, tool';
COMMENT ON COLUMN kg.nodes.key IS 'Stable identifier unique within kind, e.g. odoo:res.partner:123';
COMMENT ON COLUMN kg.nodes.attrs IS 'Flexible attributes as JSON';

-- =============================================================================
-- RELATIONSHIPS (Edges)
-- =============================================================================

CREATE TABLE IF NOT EXISTS kg.edges (
  edge_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL,
  src_node_id uuid NOT NULL REFERENCES kg.nodes(node_id) ON DELETE CASCADE,
  predicate text NOT NULL,          -- e.g. "OWNS", "SOLD_AT", "MENTIONED_IN", "DEPENDS_ON", "INVOKES"
  dst_node_id uuid NOT NULL REFERENCES kg.nodes(node_id) ON DELETE CASCADE,
  weight numeric NOT NULL DEFAULT 1,
  attrs jsonb NOT NULL DEFAULT '{}'::jsonb,
  evidence_count int NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE kg.edges IS 'Knowledge Graph relationships between entities';
COMMENT ON COLUMN kg.edges.predicate IS 'Relationship type: OWNS, DEPENDS_ON, INVOKES, MENTIONED_IN, CREATED_BY, etc.';
COMMENT ON COLUMN kg.edges.weight IS 'Relationship strength/confidence (1.0 = certain)';

-- =============================================================================
-- PROVENANCE (Evidence)
-- =============================================================================

CREATE TABLE IF NOT EXISTS kg.evidence (
  evidence_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL,
  edge_id uuid NOT NULL REFERENCES kg.edges(edge_id) ON DELETE CASCADE,
  source_type text NOT NULL,        -- "odoo", "doc", "chat", "transaction", "email", "code", "run"
  source_ref text NOT NULL,         -- e.g. "odoo:account.move:123", "github:commit:abc123"
  excerpt text,                     -- relevant snippet/context
  confidence numeric NOT NULL DEFAULT 0.7,
  created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE kg.evidence IS 'Provenance records - why an edge exists';
COMMENT ON COLUMN kg.evidence.source_type IS 'Where evidence came from: odoo, doc, chat, code, run';
COMMENT ON COLUMN kg.evidence.source_ref IS 'URI-style reference to source';
COMMENT ON COLUMN kg.evidence.confidence IS 'Extraction confidence 0-1';

-- =============================================================================
-- EMBEDDINGS (for semantic search via pgvector)
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS kg.node_embeddings (
  node_id uuid PRIMARY KEY REFERENCES kg.nodes(node_id) ON DELETE CASCADE,
  tenant_id uuid NOT NULL,
  embedding vector(1536) NOT NULL,  -- OpenAI text-embedding-3-small dimension
  model text NOT NULL DEFAULT 'text-embedding-3-small',
  updated_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON TABLE kg.node_embeddings IS 'Vector embeddings for semantic search';

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Nodes
CREATE INDEX IF NOT EXISTS idx_nodes_tenant_kind ON kg.nodes(tenant_id, kind);
CREATE INDEX IF NOT EXISTS idx_nodes_tenant_kind_key ON kg.nodes(tenant_id, kind, key);
CREATE INDEX IF NOT EXISTS idx_nodes_kind ON kg.nodes(kind);
CREATE INDEX IF NOT EXISTS idx_nodes_attrs ON kg.nodes USING gin(attrs);

-- Edges
CREATE INDEX IF NOT EXISTS idx_edges_tenant_src_pred ON kg.edges(tenant_id, src_node_id, predicate);
CREATE INDEX IF NOT EXISTS idx_edges_tenant_dst_pred ON kg.edges(tenant_id, dst_node_id, predicate);
CREATE INDEX IF NOT EXISTS idx_edges_src ON kg.edges(src_node_id);
CREATE INDEX IF NOT EXISTS idx_edges_dst ON kg.edges(dst_node_id);
CREATE INDEX IF NOT EXISTS idx_edges_predicate ON kg.edges(predicate);

-- Evidence
CREATE INDEX IF NOT EXISTS idx_evidence_edge ON kg.evidence(edge_id);
CREATE INDEX IF NOT EXISTS idx_evidence_source ON kg.evidence(source_type, source_ref);

-- Embeddings (IVFFlat for approximate NN)
CREATE INDEX IF NOT EXISTS idx_node_embeddings_vec
ON kg.node_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- =============================================================================
-- FUNCTIONS
-- =============================================================================

-- Expand neighborhood (k-hop traversal)
CREATE OR REPLACE FUNCTION kg.neighborhood(
  p_tenant uuid,
  p_start uuid,
  p_max_depth int DEFAULT 2,
  p_predicates text[] DEFAULT NULL
)
RETURNS TABLE(depth int, src uuid, predicate text, dst uuid, dst_kind text, dst_label text)
LANGUAGE sql STABLE AS $$
WITH RECURSIVE walk AS (
  SELECT
    1 AS depth,
    e.src_node_id AS src,
    e.predicate,
    e.dst_node_id AS dst
  FROM kg.edges e
  WHERE e.tenant_id = p_tenant
    AND e.src_node_id = p_start
    AND (p_predicates IS NULL OR e.predicate = ANY(p_predicates))

  UNION ALL

  SELECT
    w.depth + 1,
    e.src_node_id,
    e.predicate,
    e.dst_node_id
  FROM walk w
  JOIN kg.edges e ON e.src_node_id = w.dst
  WHERE e.tenant_id = p_tenant
    AND w.depth < p_max_depth
    AND (p_predicates IS NULL OR e.predicate = ANY(p_predicates))
)
SELECT
  w.depth,
  w.src,
  w.predicate,
  w.dst,
  n.kind AS dst_kind,
  n.label AS dst_label
FROM walk w
JOIN kg.nodes n ON n.node_id = w.dst;
$$;

COMMENT ON FUNCTION kg.neighborhood IS 'Expand k-hop neighborhood from a starting node';

-- Top related nodes by edge weights
CREATE OR REPLACE FUNCTION kg.top_related(
  p_tenant uuid,
  p_start uuid,
  p_limit int DEFAULT 25
)
RETURNS TABLE(node_id uuid, kind text, label text, score numeric)
LANGUAGE sql STABLE AS $$
SELECT
  e.dst_node_id AS node_id,
  n.kind,
  n.label,
  SUM(e.weight) AS score
FROM kg.edges e
JOIN kg.nodes n ON n.node_id = e.dst_node_id
WHERE e.tenant_id = p_tenant AND e.src_node_id = p_start
GROUP BY e.dst_node_id, n.kind, n.label
ORDER BY score DESC
LIMIT p_limit;
$$;

COMMENT ON FUNCTION kg.top_related IS 'Get top related nodes by cumulative edge weight';

-- Semantic search via embeddings
CREATE OR REPLACE FUNCTION kg.semantic_search(
  p_tenant uuid,
  p_embedding vector(1536),
  p_limit int DEFAULT 10,
  p_kinds text[] DEFAULT NULL
)
RETURNS TABLE(node_id uuid, kind text, label text, attrs jsonb, similarity float)
LANGUAGE sql STABLE AS $$
SELECT
  n.node_id,
  n.kind,
  n.label,
  n.attrs,
  1 - (ne.embedding <=> p_embedding) AS similarity
FROM kg.node_embeddings ne
JOIN kg.nodes n ON n.node_id = ne.node_id
WHERE ne.tenant_id = p_tenant
  AND (p_kinds IS NULL OR n.kind = ANY(p_kinds))
ORDER BY ne.embedding <=> p_embedding
LIMIT p_limit;
$$;

COMMENT ON FUNCTION kg.semantic_search IS 'Find similar nodes via embedding cosine similarity';

-- Upsert node (idempotent)
CREATE OR REPLACE FUNCTION kg.upsert_node(
  p_tenant uuid,
  p_kind text,
  p_key text,
  p_label text,
  p_attrs jsonb DEFAULT '{}'::jsonb
)
RETURNS uuid
LANGUAGE plpgsql AS $$
DECLARE
  v_node_id uuid;
BEGIN
  INSERT INTO kg.nodes (tenant_id, kind, key, label, attrs)
  VALUES (p_tenant, p_kind, p_key, p_label, p_attrs)
  ON CONFLICT (tenant_id, kind, key)
  DO UPDATE SET
    label = EXCLUDED.label,
    attrs = kg.nodes.attrs || EXCLUDED.attrs,
    updated_at = now()
  RETURNING node_id INTO v_node_id;

  RETURN v_node_id;
END;
$$;

COMMENT ON FUNCTION kg.upsert_node IS 'Idempotent node upsert - merges attrs on conflict';

-- Upsert edge with evidence
CREATE OR REPLACE FUNCTION kg.upsert_edge(
  p_tenant uuid,
  p_src_node_id uuid,
  p_predicate text,
  p_dst_node_id uuid,
  p_weight numeric DEFAULT 1,
  p_source_type text DEFAULT NULL,
  p_source_ref text DEFAULT NULL,
  p_excerpt text DEFAULT NULL,
  p_confidence numeric DEFAULT 0.7
)
RETURNS uuid
LANGUAGE plpgsql AS $$
DECLARE
  v_edge_id uuid;
BEGIN
  -- Upsert edge
  INSERT INTO kg.edges (tenant_id, src_node_id, predicate, dst_node_id, weight)
  VALUES (p_tenant, p_src_node_id, p_predicate, p_dst_node_id, p_weight)
  ON CONFLICT ON CONSTRAINT edges_pkey DO NOTHING;

  -- Get or find existing edge
  SELECT edge_id INTO v_edge_id
  FROM kg.edges
  WHERE tenant_id = p_tenant
    AND src_node_id = p_src_node_id
    AND predicate = p_predicate
    AND dst_node_id = p_dst_node_id
  LIMIT 1;

  -- Add evidence if provided
  IF p_source_type IS NOT NULL AND p_source_ref IS NOT NULL THEN
    INSERT INTO kg.evidence (tenant_id, edge_id, source_type, source_ref, excerpt, confidence)
    VALUES (p_tenant, v_edge_id, p_source_type, p_source_ref, p_excerpt, p_confidence);

    -- Update evidence count
    UPDATE kg.edges SET
      evidence_count = evidence_count + 1,
      updated_at = now()
    WHERE edge_id = v_edge_id;
  END IF;

  RETURN v_edge_id;
END;
$$;

COMMENT ON FUNCTION kg.upsert_edge IS 'Upsert edge with optional evidence';

-- =============================================================================
-- RLS POLICIES (tenant isolation)
-- =============================================================================

ALTER TABLE kg.nodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE kg.edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE kg.evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE kg.node_embeddings ENABLE ROW LEVEL SECURITY;

-- Service role bypass (for Edge Functions)
CREATE POLICY "service_role_all" ON kg.nodes FOR ALL
TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all" ON kg.edges FOR ALL
TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all" ON kg.evidence FOR ALL
TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "service_role_all" ON kg.node_embeddings FOR ALL
TO service_role USING (true) WITH CHECK (true);

-- Authenticated users see own tenant
CREATE POLICY "tenant_isolation" ON kg.nodes FOR ALL
TO authenticated
USING (tenant_id = auth.jwt() ->> 'tenant_id'::text)
WITH CHECK (tenant_id = auth.jwt() ->> 'tenant_id'::text);

CREATE POLICY "tenant_isolation" ON kg.edges FOR ALL
TO authenticated
USING (tenant_id = auth.jwt() ->> 'tenant_id'::text)
WITH CHECK (tenant_id = auth.jwt() ->> 'tenant_id'::text);

CREATE POLICY "tenant_isolation" ON kg.evidence FOR ALL
TO authenticated
USING (tenant_id = auth.jwt() ->> 'tenant_id'::text)
WITH CHECK (tenant_id = auth.jwt() ->> 'tenant_id'::text);

CREATE POLICY "tenant_isolation" ON kg.node_embeddings FOR ALL
TO authenticated
USING (tenant_id = auth.jwt() ->> 'tenant_id'::text)
WITH CHECK (tenant_id = auth.jwt() ->> 'tenant_id'::text);

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION kg.update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER nodes_updated_at
  BEFORE UPDATE ON kg.nodes
  FOR EACH ROW EXECUTE FUNCTION kg.update_timestamp();

CREATE TRIGGER edges_updated_at
  BEFORE UPDATE ON kg.edges
  FOR EACH ROW EXECUTE FUNCTION kg.update_timestamp();

CREATE TRIGGER embeddings_updated_at
  BEFORE UPDATE ON kg.node_embeddings
  FOR EACH ROW EXECUTE FUNCTION kg.update_timestamp();
